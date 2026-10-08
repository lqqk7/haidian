# -*- coding: utf-8 -*-
"""生成器字面量同步（沿用 wp77fix/edit_src.py 的三层不回退纪律）。

页源已按 ③④ 改写；若日后重跑生成器，字面量必须同步，否则回退。
本脚本只改 T 下的生成器，不碰包内任何文件。
"""
from __future__ import annotations
from pathlib import Path as _HaidianPath
import os

B = str(_HaidianPath(__file__).resolve().parents[1] / 'wp4b/build')

GLOBAL = [("452,986.656", "448,404.185"), ("3.9691%", "3.9289%")]

FILE = {
    "metricsfig.js": [
        ("{ v: '372,891', u: 'm²', lab: '概念建筑基底合计',",
         "{ v: '37.3 万', u: '㎡', lab: '概念建筑基底合计（约）',"),
        ("{ v: '372,891', u: 'm²', lab: 'Conceptual building footprint',",
         "{ v: '373,000', u: 'm²', lab: 'Building footprint (approx.)',"),
    ],
    "metricsfig2.js": [
        ("['372,891', 'm²', '概念建筑基底合计', 'building_footprint']",
         "['37.3 万', '㎡', '概念建筑基底合计（约）', 'building_footprint']"),
        ("['372,891', 'm²', 'Conceptual building footprint', 'building_footprint']",
         "['373,000', 'm²', 'Building footprint (approx.)', 'building_footprint']"),
    ],
    "content.js": [
        ("['372,891 m²', '概念建筑基底', 'gold']", "['约 37.3 万 ㎡', '概念建筑基底', 'gold']"),
        ("['372,891 m²', 'Conceptual building footprint', 'gold']",
         "['approx. 373,000 sqm', 'Conceptual building footprint', 'gold']"),
        ("['448,404.185 ㎡', '两类包络故意重叠', 'coral']",
         "['44.8 万 ㎡', '两类包络故意重叠（约值）', 'coral']"),
        ("['448,404.185 sqm', 'Deliberate envelope overlap', 'coral']",
         "['448,000 sqm', 'Deliberate envelope overlap (approx.)', 'coral']"),
    ],
}

for name in ("content.js", "metricsfig.js", "metricsfig2.js"):
    p = os.path.join(B, name)
    s = open(p, encoding="utf-8").read()
    n = 0
    for o, w in GLOBAL:
        n += s.count(o)
        s = s.replace(o, w)
    for o, w in FILE.get(name, []):
        c = s.count(o)
        assert c >= 1, (name, o[:40])
        n += c
        s = s.replace(o, w)
    open(p, "w", encoding="utf-8").write(s)
    print("%-16s %d 处" % (name, n))
