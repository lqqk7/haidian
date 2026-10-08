# -*- coding: utf-8 -*-
"""为改写后的页源补齐缺字 @font-face（沿用 w81-basemap/suppfont.py 机制）。"""
from __future__ import annotations
from pathlib import Path as _HaidianPath
import os, re, sys

T = str(_HaidianPath(__file__).resolve().parents[1])
sys.path.insert(0, os.path.join(T, "w81-basemap"))
import suppfont  # noqa: E402

TAG = re.compile(r"<[^>]+>")
STYLE = re.compile(r"<style.*?</style>", re.S)
SVG = re.compile(r"<svg.*?</svg>", re.S)


def visible_text(html):
    b = html[html.index("<body"):]
    b = STYLE.sub("", b)
    b = SVG.sub("", b)
    return TAG.sub(" ", b)


def patch(path):
    html = open(path, encoding="utf-8").read()
    css, miss = suppfont.face_css(html, visible_text(html))
    if css:
        assert "</style>" in html
        html = html.replace("</style>", css + "</style>", 1)
        open(path, "w", encoding="utf-8").write(html)
    return miss


if __name__ == "__main__":
    for p in sys.argv[1:]:
        m = patch(p)
        print("%-24s 补字 %s" % (os.path.basename(p), "".join(m) or "无"))
