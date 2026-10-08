# -*- coding: utf-8 -*-
"""w84 总装：图版重出 → 派生件重出 → 四册重排 → 装包。

顺序即依赖顺序，每步都带可失败的核对：
  1 补字      改写过的四个图版页源按 suppfont 机制补齐缺字
  2 主图      fig_mbg.py 重出 mobility-bluegreen（含 OSM 底图链）
  3 审计图    wpr6/wpe2/fig-*.html 直出 mobility-bluegreen-audit
  4 site      fig_site.py 重出 site-overview；英文侧必须逐字节不变
  5 派生件    受影响的 jpg 重出；未受影响的必须逐字节不变（即证明改动未越界）
  6 封面派生件 a3-coverPlan 降配方并改写 a3/*-01.html 引用；本波分两次下调：
              先 w3400q84 → w3000q80，装包实测仍超 39.5 MiB 上限 0.082 MiB，
              再 w3000q80 → w2800q78。封面图在版面上呈现宽 381 mm，2800 px
              合 187 dpi，仍在印刷可用区间，故优先压这里而不压核验图组——
              核验图组的存在价值是「白圈顶点逐个可数」，再降分辨率会使该页失效
  7 重排      A3 双语册（16 页）与 A0 双语展板
  8 装包      拷入 submissions 并报包体
"""
from __future__ import annotations
from pathlib import Path as _HaidianPath

import hashlib
import json
import os
import shutil
import subprocess
import sys

T = str(_HaidianPath(__file__).resolve().parents[1])
PKG = str(_HaidianPath(__file__).resolve().parents[3] / 'submissions/lqqk7/every-sense-jingzhang')
FIG = os.path.join(PKG, "assets/figures")
JPG = os.path.join(T, "wp4b/jpg")
OUTA3 = os.path.join(T, "wp4b/out/a3")
PY = os.path.join(T, "venv/bin/python")
sys.path.insert(0, os.path.join(T, "w82"))
sys.path.insert(0, os.path.join(T, "wp77fix"))
import fixfont                                     # noqa: E402
import quantize as QZ                              # noqa: E402

COVER_OLD = "a3-coverPlan-%s-c4800x2624_0_376-w3000-q80.jpg"
COVER_NEW = "a3-coverPlan-%s-c4800x2624_0_376-w2800-q78.jpg"
COVER_W, COVER_Q = 2800, 78


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def run(cmd, **kw):
    r = subprocess.run(cmd, capture_output=True, text=True, **kw)
    if r.returncode:
        raise SystemExit("FAILED %s\n%s\n%s" % (cmd, r.stdout, r.stderr))
    return r.stdout


def magick(src, out, crop=None, w=None, q=80):
    a = ["magick", src]
    if crop:
        a += ["-crop", crop, "+repage"]
    if w:
        a += ["-resize", "%dx" % w]
    a += ["-quality", str(q), "-sampling-factor", "4:2:0", "-strip",
          "-colorspace", "sRGB", out]
    run(a)


# ------------------------------------------------------------------ 1 补字
def step_font():
    for rel in ("wpr6/mbg/fig-zh.html", "wpr6/mbg/fig-en.html",
                "wpr6/wpe2/fig-zh.html", "wpr6/wpe2/fig-en.html"):
        p = os.path.join(T, rel)
        print("   %-24s 补字 %s" % (rel.split("/")[-1], "".join(fixfont.patch(p)) or "无"))


# --------------------------------------------------------- 2/3/4 图版重出
def step_figs():
    print("-- 主图 mobility-bluegreen --")
    print(run([PY, os.path.join(T, "w81-basemap/fig_mbg.py")]).strip())
    for lang, dst in (("zh", "mobility-bluegreen.png"), ("en", "mobility-bluegreen.en.png")):
        raw = os.path.join(T, "w81-basemap/png/mobility-bluegreen-%s.raw.png" % lang)
        q = raw.replace(".raw.png", ".q.png")
        print("   ", QZ.quantize(raw, q), os.path.basename(q))
        shutil.copy2(q, os.path.join(FIG, dst))

    print("-- 审计图 mobility-bluegreen-audit --")
    for lang, dst in (("zh", "mobility-bluegreen-audit.png"),
                      ("en", "mobility-bluegreen-audit.en.png")):
        src = os.path.join(T, "wpr6/wpe2/fig-%s.html" % lang)
        raw = os.path.join(T, "wpr6/wpe2/aud-plate-%s.raw.png" % lang)
        run(["node", os.path.join(T, "wp4b/render.js"), "png", src, raw,
             "1200", "750", "4"])
        q = raw.replace(".raw.png", ".q.png")
        print("   ", QZ.quantize(raw, q), os.path.basename(q))
        shutil.copy2(q, os.path.join(FIG, dst))

    print("-- site-overview（只中文变）--")
    en_before = sha(os.path.join(T, "w81-basemap/png/site-overview-en.raw.png"))
    print(run([PY, os.path.join(T, "w81-basemap/fig_site.py")]).strip())
    en_after = sha(os.path.join(T, "w81-basemap/png/site-overview-en.raw.png"))
    assert en_before == en_after, "英文 site-overview 被改动"
    print("   英文 raw png 逐字节不变 ✓")
    raw = os.path.join(T, "w81-basemap/png/site-overview-zh.raw.png")
    q = raw.replace(".raw.png", ".q.png")
    print("   ", QZ.quantize(raw, q))
    shutil.copy2(q, os.path.join(FIG, "site-overview.png"))


# ------------------------------------------------------------ 5/6 派生件
DERIV = [
    # (文件名模板, 图版基名, crop, width, quality, 期望是否变化)
    ("a0-mobility-%s-w4200q66.jpg", "mobility-bluegreen", None, 4200, 66, True),
    ("a3-mobilityZoom-%s-c1064x1168_1208_628-q84.jpg", "mobility-bluegreen",
     "1064x1168+1208+628", None, 84, False),
    ("a3-siteBand-%s-c4560x1056_120_408-w3400-q80.jpg", "site-overview",
     "4560x1056+120+408", 3400, 80, False),
]


def step_deriv():
    for tpl, base, crop, w, q, expect_change in DERIV:
        for lang in ("zh", "en"):
            name = tpl % lang
            out = os.path.join(JPG, name)
            old = sha(out) if os.path.exists(out) else "-"
            src = os.path.join(FIG, base + (".png" if lang == "zh" else ".en.png"))
            magick(src, out, crop, w, q)
            changed = sha(out) != old
            flag = "变" if changed else "同"
            bad = ""
            if not expect_change and changed and not (base == "site-overview" and lang == "zh"):
                bad = "  ✗ 期望逐字节不变"
            print("   %-52s %8d B  %s%s" % (name, os.path.getsize(out), flag, bad))

    print("-- 封面派生件换配方 %s → w%dq%d --"
          % (COVER_OLD.split("-")[-2] + COVER_OLD.split("-")[-1][:3], COVER_W, COVER_Q))
    for lang in ("zh", "en"):
        src = os.path.join(FIG, "site-overview" + (".png" if lang == "zh" else ".en.png"))
        out = os.path.join(JPG, COVER_NEW % lang)
        magick(src, out, "4800x2624+0+376", COVER_W, COVER_Q)
        oldp = os.path.join(JPG, COVER_OLD % lang)
        o = os.path.getsize(oldp) if os.path.exists(oldp) else 0
        print("   %-52s %8d → %8d B" % (COVER_NEW % lang, o, os.path.getsize(out)))
        page = os.path.join(OUTA3, "%s-01.html" % lang)
        s = open(page, encoding="utf-8").read()
        n = s.count(COVER_OLD % lang)
        assert n == 1, "%s-01.html 封面图引用命中 %d 处" % (lang, n)
        open(page, "w", encoding="utf-8").write(s.replace(COVER_OLD % lang,
                                                          COVER_NEW % lang))
        print("      %s-01.html 图引用已改写" % lang)


# ---------------------------------------------------------------- 7 重排
def step_pdf():
    for k in ("a3", "a0"):
        for l in ("zh", "en"):
            d = os.path.join(T, "wp4b/out", k)
            files = sorted(f for f in os.listdir(d)
                           if f.startswith(l + "-") and f.endswith(".html"))
            run(["node", os.path.join(T, "wp4b/render.js"), "pdf",
                 os.path.join(d, l + ".pdf")] + [os.path.join(d, f) for f in files],
                cwd=os.path.join(T, "wp4b"))
            from pypdf import PdfWriter, PdfReader
            parts = json.load(open(os.path.join(d, l + ".pdf.parts.json")))
            w = PdfWriter()
            for p in parts:
                w.append(p)
            out = os.path.join(d, l + ".pdf")
            w.write(out)
            w.close()
            r = PdfReader(out)
            b = r.pages[0].mediabox
            print("   %s-%s: %d 页  %s B  %.2f × %.2f mm"
                  % (k, l, len(r.pages), format(os.path.getsize(out), ","),
                     float(b.width) / 72 * 25.4, float(b.height) / 72 * 25.4))


# ---------------------------------------------------------------- 8 装包
INSTALL = [("wp4b/out/a3/zh.pdf", "drawings/a3-booklet.pdf"),
           ("wp4b/out/a3/en.pdf", "drawings/a3-booklet.en.pdf"),
           ("wp4b/out/a0/zh.pdf", "drawings/a0-boards.pdf"),
           ("wp4b/out/a0/en.pdf", "drawings/a0-boards.en.pdf")]


def step_install():
    for s, d in INSTALL:
        sp, dp = os.path.join(T, s), os.path.join(PKG, d)
        o = os.path.getsize(dp)
        shutil.copy2(sp, dp)
        print("   %-28s %9d → %9d B  (%+d)" % (d, o, os.path.getsize(dp),
                                               os.path.getsize(dp) - o))
    du = int(run(["du", "-sk", PKG]).split()[0])
    tracked = run(["git", "-C", PKG, "ls-files"]).split()
    tot = sum(os.path.getsize(os.path.join(PKG, f)) for f in tracked)
    print("   包体 du %.3f MiB · git 追踪字节 %.3f MiB（%d 个文件）"
          % (du / 1024, tot / 1048576, len(tracked)))


STEPS = {"font": step_font, "figs": step_figs, "deriv": step_deriv,
         "pdf": step_pdf, "install": step_install}

if __name__ == "__main__":
    want = sys.argv[1:] or list(STEPS)
    for name in want:
        print("== %s ==" % name)
        STEPS[name]()
