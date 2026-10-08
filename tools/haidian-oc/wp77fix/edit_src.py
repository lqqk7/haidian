# -*- coding: utf-8 -*-
"""v7.7 图内残字修复：改写页源与生成器里的「素底 / plain-ground」表述。

四张图版已在 WP-81 换成 OSM 路网底图并在图面加了 ODbL 署名，图注却仍写
「素底 / plain-ground」，与同图署名自相矛盾。此处按事实改为「OSM 路网底图上
的概念结构图」，口径与署名行「仅含路网与轨道」一致。

改三层，保证任一层重建都不回退：
  wp4b/build/{landusefig,sitefig}.js  →  wp4b/out/{lu,site}-{zh,en}.html
  →  w81-basemap/{fig_lu,fig_site}.py  →  w81-basemap/html/*.html
"""
from __future__ import annotations
from pathlib import Path as _HaidianPath

import os

T = str(_HaidianPath(__file__).resolve().parents[1])

ZH_NEW = "OSM 路网底图上的概念结构图"

PAIRS = {
    "wp4b/out/lu-zh.html": [
        ("图面旋转 90° · 北向右 · 素底结构图，几何取自提交 GeoJSON",
         "图面旋转 90° · 北向右 · OSM 路网底图上的概念结构图，几何取自提交 GeoJSON"),
        ("素底概念结构图 · 几何依据：", ZH_NEW + " · 几何依据："),
    ],
    "wp4b/out/lu-en.html": [
        ("Sheet rotated 90° · north to the right · plain-ground structure from the submitted GeoJSON",
         "Sheet rotated 90° · north to the right · submitted GeoJSON on an OSM road-network basemap"),
        ("Plain-ground concept structure · geometry:",
         "Concept structure on an OSM road-network basemap · geometry:"),
    ],
    "wp4b/out/site-zh.html": [
        ("素底概念结构图 · 全部线位、框线与节点由提交 GeoJSON 现算落位",
         ZH_NEW + " · 全部线位、框线与节点由提交 GeoJSON 现算落位"),
        ("素底概念结构图，几何取自提交 GeoJSON（EPSG:4326）· 不用于",
         ZH_NEW + "，几何取自提交 GeoJSON（EPSG:4326）· 不用于"),
    ],
    "wp4b/out/site-en.html": [
        ("Plain-ground concept structure; every line, frame and node placed from the submitted GeoJSON",
         "Concept structure on an OSM road-network basemap; every line, frame and node placed from the submitted GeoJSON"),
        ("Plain-ground concept structure from the submitted GeoJSON (EPSG:4326) · not for revising",
         "Concept structure on an OSM road-network basemap, from the submitted GeoJSON · not for revising"),
    ],
    # 生成器字面量：与上面逐字对应，避免重跑 landusefig/sitefig 时回退
    "wp4b/build/landusefig.js": [
        ("图面旋转 90° · 北向右 · 素底结构图，几何取自提交 GeoJSON",
         "图面旋转 90° · 北向右 · OSM 路网底图上的概念结构图，几何取自提交 GeoJSON"),
        ("素底概念结构图 · 几何依据：", ZH_NEW + " · 几何依据："),
        ("Sheet rotated 90° · north to the right · plain-ground structure from the submitted GeoJSON",
         "Sheet rotated 90° · north to the right · submitted GeoJSON on an OSM road-network basemap"),
        ("Plain-ground concept structure · geometry:",
         "Concept structure on an OSM road-network basemap · geometry:"),
    ],
    "wp4b/build/sitefig.js": [
        ("素底概念结构图 · 全部线位、框线与节点由提交 GeoJSON 现算落位",
         ZH_NEW + " · 全部线位、框线与节点由提交 GeoJSON 现算落位"),
        ("素底概念结构图，几何取自提交 GeoJSON（EPSG:4326）· 不用于",
         ZH_NEW + "，几何取自提交 GeoJSON（EPSG:4326）· 不用于"),
        ("Plain-ground concept structure; every line, frame and node placed from the submitted GeoJSON",
         "Concept structure on an OSM road-network basemap; every line, frame and node placed from the submitted GeoJSON"),
        ("Plain-ground concept structure from the submitted GeoJSON (EPSG:4326) · not for revising",
         "Concept structure on an OSM road-network basemap, from the submitted GeoJSON · not for revising"),
    ],
}

for rel, pairs in PAIRS.items():
    p = os.path.join(T, rel)
    s = open(p, encoding="utf-8").read()
    for old, new in pairs:
        n = s.count(old)
        assert n == 1, "%s: %d 处命中 %r" % (rel, n, old[:40])
        s = s.replace(old, new)
    open(p, "w", encoding="utf-8").write(s)
    print("%-34s %d 处" % (rel, len(pairs)))
