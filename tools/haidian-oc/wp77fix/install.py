# -*- coding: utf-8 -*-
"""把改好的四张图版装回包内，并逐项核对影响面。

只做搬运与核对，不做生成：量化成品由 quantize.py 产出，派生件由 mkjpg.py
重建，四册由 wp4b/mkpdf.sh 重排。
"""
from __future__ import annotations
from pathlib import Path as _HaidianPath

import hashlib
import os
import shutil
import sys

T = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PKG = str(_HaidianPath(__file__).resolve().parents[3] / 'submissions/lqqk7/every-sense-jingzhang')
FIG = os.path.join(PKG, "assets/figures")

PLATES = [
    ("land-use-structure-zh.q.png", "land-use-structure.png"),
    ("land-use-structure-en.q.png", "land-use-structure.en.png"),
    ("site-overview-zh.q.png", "site-overview.png"),
    ("site-overview-en.q.png", "site-overview.en.png"),
]

BOOKS = [
    ("wp4b/out/a3/zh.pdf", "drawings/a3-booklet.pdf"),
    ("wp4b/out/a3/en.pdf", "drawings/a3-booklet.en.pdf"),
    ("wp4b/out/a0/zh.pdf", "drawings/a0-boards.pdf"),
    ("wp4b/out/a0/en.pdf", "drawings/a0-boards.en.pdf"),
]


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def install(pairs, root):
    for src, dst in pairs:
        s = os.path.join(root, src)
        d = os.path.join(PKG, dst) if "/" in dst else os.path.join(FIG, dst)
        old = os.path.getsize(d), sha(d)[:12]
        shutil.copyfile(s, d)
        print("   %-28s %8d -> %8d B   %s -> %s"
              % (os.path.basename(dst), old[0], os.path.getsize(d), old[1], sha(d)[:12]))


if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else "plates"
    if what == "plates":
        print("== 装入图版 ==")
        install([(os.path.join("w81-basemap/png", a), b) for a, b in PLATES], T)
    elif what == "books":
        print("== 装入四册 ==")
        install(BOOKS, T)
