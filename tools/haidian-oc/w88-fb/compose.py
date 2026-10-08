# -*- coding: utf-8 -*-
"""w88-fb/compose.py — rebuild visual/assets/scene-fallback{,.en}.png panels.

Recovered recipe (measured off the shipped v7.9 files; the two panels' content
extents reproduce at cols 15..860 / rows 14..503 inside each panel, identical to
the shipped file, which is what pins the width, height and origins below):
  canvas   1824 x 692 (zh) / 1824 x 682 (en), background #10383D
  content box  x 16 .. 1807
  two scene panels 888 x 516, left at x=16, right at x=920 (16 px gutter)
  panel top   y = 95 (zh, under the two white rules at y=94) / y = 90 (en)
  chrome      header rows above the panel band, footer rows below

Only the two panel rectangles are rewritten; every chrome pixel of the shipped
file is preserved byte for byte, so the header/footer typography cannot drift.
Panels come from cap.js, which drives the real chapter-16 scene in headless
Chromium with the two real clicks ("play guidance flow", then "AI OFF").

usage: python compose.py [--write]
"""
from __future__ import annotations
from pathlib import Path as _HaidianPath
import shutil, subprocess, sys, os
from PIL import Image

# A 批图版的无损重过滤基线（v9.3）：Pillow 的 optimize 只做启发式过滤器选择，
# 对调色板索引图会选中 Sub/Paeth 一类差分而制造噪声。落盘后统一补一道
# zopflipng 无损重过滤（filters=0 = None，对调色板图最优），像素零变化。
# 与 wp77fix/quantize.py 等 B 批配方的 `-m` 不同档，两档各自登记、互不覆盖。
ZOPFLI = ["zopflipng", "-y", "--iterations=5", "--filters=0"]

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = str(_HaidianPath(__file__).resolve().parents[3] / 'submissions/lqqk7/every-sense-jingzhang')
DST = os.path.join(PKG, "visual/assets")
PANEL = (888, 516)
XS = (16, 920)
TOP = {"zh": 95, "en": 90}
NAME = {"zh": "scene-fallback.png", "en": "scene-fallback.en.png"}
BG = (16, 56, 61)


def finalize(src: str, dst: str) -> str:
    """Pillow 落盘 + zopflipng 无损重过滤，产出与包内成品逐字节一致的候选件。"""
    Image.open(src).save(dst, optimize=True)
    z = dst + ".z"
    subprocess.run(ZOPFLI + [dst, z], check=True, capture_output=True)
    os.replace(z, dst)
    return dst


def build(lang: str, write: bool) -> None:
    base = Image.open(os.path.join(DST, NAME[lang])).convert("RGB")
    top = TOP[lang]
    out = base.copy()
    # clear the whole panel band first, then paste the two fresh panels
    band = Image.new("RGB", (base.width, PANEL[1]), BG)
    out.paste(band, (0, top))
    for x, state in zip(XS, ("on", "off")):
        p = Image.open(os.path.join(HERE, "out", f"panel-{lang}-{state}.png")).convert("RGB")
        # Playwright's element shot is 517 rows tall for a 516.28 px canvas and
        # its first row is the white page pixel above the element: drop row 0.
        p = p.crop((0, 1, PANEL[0], 1 + PANEL[1]))
        out.paste(p, (x, top))
    tmp = os.path.join(HERE, "out", f"fallback-{lang}.png")
    out.save(tmp, optimize=True)
    q = out.quantize(colors=256, method=Image.MEDIANCUT, dither=Image.FLOYDSTEINBERG)
    tmp8 = os.path.join(HERE, "out", f"fallback-{lang}-p8.png")
    q.save(tmp8, optimize=True)
    print("%s  base %d B  rgb %d B  pal8 %d B" % (
        lang, os.path.getsize(os.path.join(DST, NAME[lang])),
        os.path.getsize(tmp), os.path.getsize(tmp8)))
    src = tmp8 if os.path.getsize(tmp8) < os.path.getsize(tmp) else tmp
    cand = finalize(src, os.path.join(HERE, "out", "final-%s.png" % lang))
    print("   candidate %s  %d B" % (os.path.basename(cand), os.path.getsize(cand)))
    if write:
        shutil.copyfile(cand, os.path.join(DST, NAME[lang]))
        print("   -> wrote %s from %s (%d B)" % (NAME[lang], os.path.basename(src),
                                                 os.path.getsize(os.path.join(DST, NAME[lang]))))


if __name__ == "__main__":
    w = "--write" in sys.argv
    for lang in ("zh", "en"):
        build(lang, w)
