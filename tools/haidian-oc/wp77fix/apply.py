# -*- coding: utf-8 -*-
"""v7.7 图内残字修复：把四张换底图版里的「素底 / plain-ground」表述改写为
与图上 ODbL 署名一致的「OSM 路网底图上的概念结构图」，并按既有补字机制
为新增码位追加 @font-face（unicode-range 精确限定，既有字符渲染不变）。

用法：python apply.py <输出目录>      （不传则原地改写 w81-basemap/html）
"""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
T = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(T, "w81-basemap"))
import suppfont  # noqa: E402

SRC = os.path.join(T, "w81-basemap/html")

EDITS = {
    "land-use-structure-zh.html": [
        ("图面旋转 90° · 北向右 · 素底结构图，几何取自提交 GeoJSON",
         "图面旋转 90° · 北向右 · OSM 路网底图上的概念结构图，几何取自提交 GeoJSON"),
        ("素底概念结构图 · 几何依据：",
         "OSM 路网底图上的概念结构图 · 几何依据："),
    ],
    "land-use-structure-en.html": [
        ("Sheet rotated 90° · north to the right · plain-ground structure from the submitted GeoJSON",
         "Sheet rotated 90° · north to the right · submitted GeoJSON on an OSM road-network basemap"),
        ("Plain-ground concept structure · geometry:",
         "Concept structure on an OSM road-network basemap · geometry:"),
    ],
    "site-overview-zh.html": [
        ("素底概念结构图 · 全部线位、框线与节点由提交 GeoJSON 现算落位",
         "OSM 路网底图上的概念结构图 · 全部线位、框线与节点由提交 GeoJSON 现算落位"),
        ("素底概念结构图，几何取自提交 GeoJSON（EPSG:4326）· 不用于",
         "OSM 路网底图上的概念结构图，几何取自提交 GeoJSON（EPSG:4326）· 不用于"),
    ],
    "site-overview-en.html": [
        ("Plain-ground concept structure; every line, frame and node placed from the submitted GeoJSON",
         "Concept structure on an OSM road-network basemap; every line, frame and node placed from the submitted GeoJSON"),
        ("Plain-ground concept structure from the submitted GeoJSON (EPSG:4326) · not for revising",
         "Concept structure on an OSM road-network basemap, from the submitted GeoJSON · not for revising"),
    ],
}


def main():
    out_dir = sys.argv[1] if len(sys.argv) > 1 else SRC
    os.makedirs(out_dir, exist_ok=True)
    for name, pairs in EDITS.items():
        html = open(os.path.join(SRC, name), encoding="utf-8").read()
        new_text = ""
        for old, new in pairs:
            n = html.count(old)
            assert n == 1, "%s: %d 处命中 %r" % (name, n, old[:30])
            html = html.replace(old, new)
            new_text += new
        css, miss = suppfont.face_css(html, new_text)
        if css:
            assert "</style>" in html
            html = html.replace("</style>", css + "</style>", 1)
        with open(os.path.join(out_dir, name), "w", encoding="utf-8") as f:
            f.write(html)
        print("%-30s 补字 %s" % (name, "".join(miss) or "无"))


if __name__ == "__main__":
    main()
