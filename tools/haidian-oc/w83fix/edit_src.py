# -*- coding: utf-8 -*-
"""v7.8 site-overview 英文图版压字修复：收回图带题注左半段的冗余同义重复。

缺陷（量测于 1200x750 版心，dsf 4）
--------------------------------
英文图版 .mapcap 是 flex 单行：左项 .a（题注）单行自然宽 618.4 px，右项 .b
（口径行）657.4 px，加 20 px 间距共 1295.8 px，超出 1140 px 版心 155.8 px，
两项各自折行 → 题注行由 17 px 涨到 34 px → 下方 .body 网格顶边被压低 17 px
（zh 396 → en 413），可用高从 330 px 降到 313 px；而左栏内容固定需要 326.4 px，
于是溢出 13.4 px，最后一行 .sn「Announced approximate value · provisional
boxes」（盒 722.4–739.4）压进页脚 .ft（726–750），与页脚说明行压字。
中文侧 .a 415.6 + .b 440.6 + 20 = 876.2 px，单行，无此问题。

修法
----
只改英文 mapCap 一处：删去「/ Jing-Zhang corridor structure」。该片段是中文版
「CORRIDOR OVERVIEW / 京张走廊总体结构」双语对照的英文重复，在英文版里与前半段
CORRIDOR OVERVIEW 同义；图版 h1 与页眉 idx 已载明京张与图号，无信息损失。
改后 .a 403.1 px，与未改动的 .b 657.4 px 合计 1080.5 px < 1120 px，题注回到单行，
网格顶边回到 396，左栏 326.4 px 落在 330 px 内，余量 +3.6 px。

口径行 mapSrc、页脚 foot、左栏文案、行距字号与中文侧一字不动；新串字符集是
原串的子集，不引入新码位，字体子集无需变更。

改两层，保证任一层重建都不回退：
  wp4b/build/sitefig.js  →  wp4b/out/site-en.html
第三层 w81-basemap/html/site-overview-en.html 由 fig_site.py 从第二层重出。
"""
from __future__ import annotations
from pathlib import Path as _HaidianPath

import os

T = str(_HaidianPath(__file__).resolve().parents[1])

OLD = "CORRIDOR OVERVIEW / Jing-Zhang corridor structure (sheet rotated 90°, north to the right)"
NEW = "CORRIDOR OVERVIEW (sheet rotated 90°, north to the right)"

TARGETS = ["wp4b/build/sitefig.js", "wp4b/out/site-en.html"]

for rel in TARGETS:
    p = os.path.join(T, rel)
    s = open(p, encoding="utf-8").read()
    n = s.count(OLD)
    assert n == 1, "%s: %d 处命中" % (rel, n)
    assert set(NEW) <= set(OLD), "新串引入了新码位"
    open(p, "w", encoding="utf-8").write(s.replace(OLD, NEW))
    print("%-30s 1 处" % rel)
