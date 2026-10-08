# -*- coding: utf-8 -*-
"""WP-91 总装：site-overview 双语重出 → A3 派生件重出 → A3 双语册重排 → 装包。

顺序即依赖顺序。A0 双语展板不引用 site-overview（其六张图源为 brand / keyareas /
landuse / metrics / mobility / scene），本波因此不重排 A0，也不动 A0 的两个 PDF。

量化配方沿用该图版自 v8.4 起的登记配方 pngquant --quality=40-70 --speed 1 +
zopflipng -y --filters=0 -m（w87-tactile/quantize70.py），不改配方，以免仅因配方
变更就使图版字节数与包体余量发生与本轮内容无关的漂移。
"""
from __future__ import annotations
from pathlib import Path as _HaidianPath

import hashlib
import json
import os
import shutil
import subprocess
import sys

T = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PKG = str(_HaidianPath(__file__).resolve().parents[3] / 'submissions/lqqk7/every-sense-jingzhang')
FIG = os.path.join(PKG, "assets/figures")
JPG = os.path.join(T, "wp4b/jpg")
OUTA3 = os.path.join(T, "wp4b/out/a3")
PY = os.path.join(T, "venv/bin/python")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(T, "w87-tactile"))
import quantize70 as QZ                              # noqa: E402

DERIV = [
    ("a3-siteBand-%s-c4560x1056_120_408-w3400-q80.jpg", "4560x1056+120+408", 3400, 80),
    ("a3-coverPlan-%s-c4800x2624_0_376-w2800-q78.jpg", "4800x2624+0+376", 2800, 78),
]


def sha(p):
    with open(p, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


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


def step_figs():
    print("-- site-overview 双语重出（叠廊道参考线）--")
    env = dict(os.environ, W81_HTML_OUT=os.path.join(HERE, "html"),
               W81_PNG_OUT=os.path.join(HERE, "png"))
    r = subprocess.run([PY, os.path.join(HERE, "fig_site_align.py")],
                       capture_output=True, text=True, env=env)
    print(r.stdout.strip() or r.stderr.strip())
    if r.returncode:
        raise SystemExit("fig_site_align.py failed")
    for lang, dst in (("zh", "site-overview.png"), ("en", "site-overview.en.png")):
        raw = os.path.join(HERE, "png", "site-overview-%s.raw.png" % lang)
        q = raw.replace(".raw.png", ".q.png")
        pq, z = QZ.quantize(raw, q)
        old = os.path.getsize(os.path.join(FIG, dst))
        shutil.copy2(q, os.path.join(FIG, dst))
        print("   %-22s raw %8d → pngquant %8d → zopfli %8d B  (包内 %d → %d, %+d)"
              % (dst, os.path.getsize(raw), pq, z, old, z, z - old))


def step_deriv():
    print("-- A3 派生件重出 --")
    for tpl, crop, w, q in DERIV:
        for lang in ("zh", "en"):
            name = tpl % lang
            out = os.path.join(JPG, name)
            old = os.path.getsize(out) if os.path.exists(out) else 0
            src = os.path.join(FIG, "site-overview" + (".png" if lang == "zh" else ".en.png"))
            magick(src, out, crop, w, q)
            print("   %-52s %8d → %8d B  (%+d)"
                  % (name, old, os.path.getsize(out), os.path.getsize(out) - old))
            page = "01" if "coverPlan" in name else "02"
            html = os.path.join(OUTA3, "%s-%s.html" % (lang, page))
            n = open(html, encoding="utf-8").read().count(name)
            assert n == 1, "%s-%s.html 引用 %s 命中 %d 处" % (lang, page, name, n)


def step_pdf():
    from pypdf import PdfReader, PdfWriter
    for lang in ("zh", "en"):
        files = sorted(f for f in os.listdir(OUTA3)
                       if f.startswith(lang + "-") and f.endswith(".html"))
        out = os.path.join(OUTA3, lang + ".pdf")
        run(["node", os.path.join(T, "wp4b/render.js"), "pdf", out]
            + [os.path.join(OUTA3, f) for f in files], cwd=os.path.join(T, "wp4b"))
        parts = json.load(open(out + ".parts.json"))
        w = PdfWriter()
        for p in parts:
            w.append(p)
        w.write(out)
        w.close()
        merged = out.replace(".pdf", ".merged.pdf")
        run([PY, os.path.join(T, "wp4b/merge_fonts.py"), out, merged],
            cwd=os.path.join(T, "wp4b"))
        os.replace(merged, out)
        r = PdfReader(out)
        b = r.pages[0].mediabox
        print("   a3-%s: %d 页  %s B  %.2f × %.2f mm"
              % (lang, len(r.pages), format(os.path.getsize(out), ","),
                 float(b.width) / 72 * 25.4, float(b.height) / 72 * 25.4))


INSTALL = [("wp4b/out/a3/zh.pdf", "drawings/a3-booklet.pdf"),
           ("wp4b/out/a3/en.pdf", "drawings/a3-booklet.en.pdf")]


def step_install():
    for s, d in INSTALL:
        sp, dp = os.path.join(T, s), os.path.join(PKG, d)
        o = os.path.getsize(dp)
        shutil.copy2(sp, dp)
        print("   %-28s %9d → %9d B  (%+d)"
              % (d, o, os.path.getsize(dp), os.path.getsize(dp) - o))
    du = int(run(["du", "-sk", PKG]).split()[0])
    tracked = run(["git", "-C", PKG, "ls-files"]).split()
    tot = sum(os.path.getsize(os.path.join(PKG, f)) for f in tracked
              if os.path.exists(os.path.join(PKG, f)))
    print("   包体 du %.3f MiB · git 追踪字节 %.3f MiB（%d 个文件）"
          % (du / 1024, tot / 1048576, len(tracked)))


STEPS = {"figs": step_figs, "deriv": step_deriv, "pdf": step_pdf,
         "install": step_install}

if __name__ == "__main__":
    for name in (sys.argv[1:] or list(STEPS)):
        print("=" * 8, name)
        STEPS[name]()
