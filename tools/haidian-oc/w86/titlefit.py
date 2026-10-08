# -*- coding: utf-8 -*-
"""主标题候选串的版心实测：把候选串塞进页源渲染，量 h1 占几行、右缘到哪。

mobility-bluegreen 的页头 .hd 是固定 94 px 的深色带，h1 26 px / line-height 1.22 /
max-width 840 px。标题一旦折成两行，第二行会压到下方图例带上（本次实测已见）。
生成器散佚，改 .hd 高度等于重排整页，因此标题只能在一行内选。本脚本给出可判定的
依据，避免凭字数估。

用法：python titlefit.py            # 跑内置候选表
判据：ink_rows == 1 且 right <= 866 px（右侧「05 / REACHABILITY…」块起始处）
"""
from __future__ import annotations
from pathlib import Path as _HaidianPath

import os
import subprocess
import sys

import numpy as np
from PIL import Image

T = str(_HaidianPath(__file__).resolve().parents[1])
HERE = os.path.dirname(os.path.abspath(__file__))
RENDER = os.path.join(T, "wp4b/render.js")
OLD_H1 = {"zh": "<h1>AI 关闭后，可达域收缩近一半：差集是审计靶区，不是达标声明</h1>",
          "en": "<h1>AI off halves the reachable domain: the gap is an audit target, "
                "not a compliance claim</h1>"}
BAND = (30, 30, 880, 94)          # h1 可用区：左 30 px 起，页头底 94 px
RIGHT_LIMIT = 866                 # 右侧栏起始

CAND = {
    "zh": ["按本图自设口径，AI 关闭后可达域收缩 49.3%：差集是审计靶区，不是达标声明",
           "按本图自设口径：AI 关闭后可达域收缩 49.3%",
           "按本图口径：AI 关闭后可达域收缩 49.3%"],
    "en": ["Under this figure's self-set convention, AI off shrinks the reachable "
           "domain by 49.3%: the gap is an audit target, not a compliance claim",
           "Under this figure's self-set convention: AI off shrinks the reachable "
           "domain by 49.3%",
           "Under this figure's convention: AI off shrinks the reachable domain by 49.3%"],
}


def measure(lang, title):
    src = os.path.join(T, "wpr6/mbg/fig-%s.html" % lang)
    h = open(src, encoding="utf-8").read()
    assert h.count(OLD_H1[lang]) == 1
    h = h.replace(OLD_H1[lang], "<h1>%s</h1>" % title)
    tmp = os.path.join(HERE, "_titlefit-%s.html" % lang)
    open(tmp, "w", encoding="utf-8").write(h)
    png = os.path.join(HERE, "_titlefit-%s.png" % lang)
    subprocess.run(["node", RENDER, "png", tmp, png, "1200", "750", "1"],
                   check=True, capture_output=True)
    a = np.asarray(Image.open(png).convert("RGB")).astype(int)
    x0, y0, x1, y1 = BAND
    sub = a[y0:y1, x0:x1]
    # 深色页头上的白字：亮度高于底色即为墨
    ink = sub.mean(axis=2) > 140
    rows = ink.any(axis=1)
    segs, run = [], None
    for i, v in enumerate(rows):
        if v and run is None:
            run = i
        elif not v and run is not None:
            segs.append((run + y0, i + y0)); run = None
    if run is not None:
        segs.append((run + y0, y1))
    right = x0 + int(np.nonzero(ink.any(axis=0))[0].max()) if ink.any() else x0
    os.unlink(tmp); os.unlink(png)
    return segs, right


if __name__ == "__main__":
    for lang in ("zh", "en"):
        print("==", lang)
        for t in CAND[lang]:
            segs, right = measure(lang, t)
            ok = len(segs) == 1 and right <= RIGHT_LIMIT
            print("  %s  行段 %s  右缘 %d px  %s"
                  % ("✓" if ok else "✗", segs, right, t[:46]))
