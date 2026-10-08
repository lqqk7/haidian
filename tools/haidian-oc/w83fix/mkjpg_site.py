# -*- coding: utf-8 -*-
"""重出英文 site-overview 图版的两张 A3 派生件（配方即文件名，与 wp77fix/mkjpg.py
和 w82/cover.py 登记的一致）：

  a3-coverPlan-en-c4800x2624_0_376-w3400-q84.jpg   A3 第 01 页封面整幅
  a3-siteBand-en-c4560x1056_120_408-w3400-q80.jpg  A3 第 02 页图带

改动前用同一配方从随包旧图版复现，两张均与 wp4b/jpg 现件逐字节一致，配方已验证。
图带裁切窗（CSS y 102–366）不含题注行（CSS y 371–405），改后若仍逐字节一致，
即证明本次改动未越出题注行。
"""
from __future__ import annotations
from pathlib import Path as _HaidianPath

import hashlib
import os
import subprocess

T = str(_HaidianPath(__file__).resolve().parents[1])
PKG = str(_HaidianPath(__file__).resolve().parents[3] / 'submissions/lqqk7/every-sense-jingzhang')
SRC = os.path.join(PKG, "assets/figures/site-overview.en.png")
JPG = os.path.join(T, "wp4b/jpg")

SPEC = [
    ("a3-coverPlan-en-c4800x2624_0_376-w3400-q84.jpg", "4800x2624+0+376", 3400, 84),
    ("a3-siteBand-en-c4560x1056_120_408-w3400-q80.jpg", "4560x1056+120+408", 3400, 80),
]


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


for name, crop, w, q in SPEC:
    out = os.path.join(JPG, name)
    old = (os.path.getsize(out), sha(out)) if os.path.exists(out) else (0, "-")
    subprocess.run(["magick", SRC, "-crop", crop, "+repage", "-resize", "%dx" % w,
                    "-quality", str(q), "-sampling-factor", "4:2:0", "-strip",
                    "-colorspace", "sRGB", out], check=True)
    new = (os.path.getsize(out), sha(out))
    print("%-50s %8d -> %8d B  %s  %s -> %s"
          % (name, old[0], new[0], "同" if old[1] == new[1] else "变",
             old[1][:12], new[1][:12]))
