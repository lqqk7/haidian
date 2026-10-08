# -*- coding: utf-8 -*-
"""逐图核验：新旧对比，列出差异区域，确认改动只落在预期矩形内。"""
from pathlib import Path as _HaidianPath
import sys

import numpy as np
from PIL import Image

Image.MAX_IMAGE_PIXELS = None
SCR = str(_HaidianPath(__file__).resolve().parents[1])
W = SCR + "/w81-basemap"

# name -> (旧 raw, 新 raw, [允许改动的矩形 (x0,y0,x1,y1) in 4800x3000])
CASES = {
    "site-overview-zh": (SCR + "/wpn2b/wp4b/site-full-zh.png",
                         W + "/png/site-overview-zh.raw.png",
                         [(120, 408, 4680, 1464)]),
    "site-overview-en": (SCR + "/wpn2b/wp4b/site-full-en.png",
                         W + "/png/site-overview-en.raw.png",
                         [(120, 408, 4680, 1464)]),
    "land-use-structure-zh": (SCR + "/wpn2b/wp4b/lu-full-zh.png",
                              W + "/png/land-use-structure-zh.raw.png", None),
    "land-use-structure-en": (SCR + "/wpn2b/wp4b/lu-full-en.png",
                              W + "/png/land-use-structure-en.raw.png", None),
    "mobility-bluegreen-zh": (SCR + "/wpr6/mbg/full-zh.png",
                              W + "/png/mobility-bluegreen-zh.raw.png", None),
    "mobility-bluegreen-en": (SCR + "/wpr6/mbg/full-en.png",
                              W + "/png/mobility-bluegreen-en.raw.png", None),
    "dual-state-plan-zh": (SCR + "/wpv70/dsp/base-zh.png",
                           W + "/png/dual-state-plan-zh.raw.png", None),
    "dual-state-plan-en": (SCR + "/wpv70/dsp/base-en.png",
                           W + "/png/dual-state-plan-en.raw.png", None),
}


def boxes(mask, min_px=40):
    """把差异掩膜切成若干行段，报告每段的包围盒。"""
    rows = mask.any(axis=1)
    out, run = [], None
    for y, v in enumerate(rows):
        if v and run is None:
            run = y
        elif not v and run is not None:
            out.append((run, y))
            run = None
    if run is not None:
        out.append((run, len(rows)))
    res = []
    for y0, y1 in out:
        sub = mask[y0:y1]
        if sub.sum() < min_px:
            continue
        xs = np.nonzero(sub.any(axis=0))[0]
        res.append((int(xs.min()), y0, int(xs.max()), y1, int(sub.sum())))
    return res


for name, (old, new, allow) in CASES.items():
    a = np.asarray(Image.open(old).convert("RGB")).astype(int)
    b = np.asarray(Image.open(new).convert("RGB")).astype(int)
    d = np.abs(a - b).max(axis=2) > 8
    print(f"=== {name}  差异像素 {int(d.sum()):,}")
    for x0, y0, x1, y1, n in boxes(d):
        flag = ""
        if allow:
            ok = any(x0 >= r[0] and y0 >= r[1] and x1 <= r[2] and y1 <= r[3]
                     for r in allow)
            flag = "" if ok else "  <-- 越界"
        print(f"    x[{x0:4d},{x1:4d}] y[{y0:4d},{y1:4d}] {n:8d} px"
              f"  CSS x[{x0/4:.0f},{x1/4:.0f}] y[{y0/4:.0f},{y1/4:.0f}]{flag}")
