# -*- coding: utf-8 -*-
"""核验图组进 A3 双语册所需的全部文案与版面常数。

文案纪律：本模块不产生任何新判断。图注的中英文字串取自核验图版自身
（w81-basemap/mkverify.py 的 SHEETS / LAYER_LABEL / NOTE_ZH / NOTE_EN /
ATTR_ZH / ATTR_EN / CRS_ZH / SUB_ZH / SUB_EN），要素数与顶点数取自该模块
对 geometry/*.geojson 的现算结果，与图面印字逐字一致。

一处例外，且是有意的：图版原件（3000 × 1875 px）上顶点白圈直径约 13 px，
「逐个可数」在原件尺寸上成立；但册页把同一张图缩到 515 px（配对页）与
740 px（单图页），白圈只剩 2.3 px 与 3.3 px，在 A3 上数不出来——包体
39.5 MiB 的上限不允许把配对图放到能兑现该承诺的 1000 px 以上。因此
SUB_ZH / SUB_EN 与第 13—15 页导语在册页上不重述「逐个可数」，改为标明
册页是缩印本、逐个清点以 assets/figures/ 下的 PNG 原件为准。册页仍然
承担可核对的部分：图题、要素数与顶点数、图版路径、核验声明。
"""
from __future__ import annotations

# key, zh 图题, en 图题, 要素数, 顶点数（与图面右上「本图要素 N 个 / 顶点 N 个」同源）
SHEETS = [
    # v8.0：roads.geojson 按真实走向加密（五条线位各 20—24 顶点、合计 114），
    # 02-roads 与 00-all 两行的顶点数随之更新，与核验图版印字同源。
    ("00-all", "全部图层叠加", "All layers overlaid", 42, 263),
    ("01-landuse", "用地结构 land_use", "Land use", 4, 24),
    ("02-roads", "线位 roads", "Roads (centrelines)", 5, 114),
    ("03-buildings", "概念体量 buildings", "Buildings (concept masses)", 4, 20),
    ("04-green", "绿地 green_space", "Green space", 6, 30),
    ("05-publicspace", "公共空间 public_space", "Public space", 10, 50),
    ("06-keyareas", "重点区 key_areas + 独立完成节点 constraints",
     "Key areas + completion nodes", 13, 25),
]

# 图面自带的说明句（逐字）
NOTE_ZH = ("本图为核验图：将本包提交的正式几何原样叠加于 OSM 底图。本包几何为关系示意级"
           "（要素数与顶点数如实可见），不表示测绘精度。")
NOTE_EN = ("This is a verification sheet: the geometry filed in this package is "
           "overlaid on an OpenStreetMap basemap exactly as submitted. The geometry "
           "is relationship-diagram grade — its feature and vertex counts are shown "
           "as they are — and does not represent survey accuracy.")
SUB_ZH = "白圈为几何顶点；册页为缩印，逐个清点用该 PNG 原件"
SUB_EN = ("white ring = geometry vertex; these pages are reduced reproductions — "
          "count them on the PNG itself")
CRS_ZH = "坐标 EPSG:4326 · 量测复算 EPSG:4548 · 非法定规划图，不表示权属边界"
CRS_EN = "Coordinates EPSG:4326, recomputed in EPSG:4548 · not a statutory plan"
ATTR_ZH = ("底图数据 © OpenStreetMap 贡献者，ODbL 1.0；快照 osm-fabric-snapshot-20260815"
           "（该快照仅含 highway / railway 要素，故底图只有路网与轨道，无建筑与水系）")
ATTR_EN = ("Basemap data © OpenStreetMap contributors, ODbL 1.0; snapshot "
           "osm-fabric-snapshot-20260815 (highway / railway elements only: the "
           "basemap carries roads and rail, no buildings or water)")

# 每页页眉：h2 标题 与 右上 idx
PAGES = {
    12: dict(keys=["00-all"],
             zh_h2="几何核验图 · 全部图层叠加", en_h2="Geometry Verification · All Layers",
             zh_s="附页 C · V00 / GEOMETRY VERIFICATION",
             en_s="APPENDIX C · V00 / GEOMETRY VERIFICATION"),
    13: dict(keys=["01-landuse", "02-roads"],
             zh_h2="几何核验图 · 用地与线位", en_h2="Geometry Verification · Land Use and Roads",
             zh_s="附页 C · V01—V02 / GEOMETRY VERIFICATION",
             en_s="APPENDIX C · V01—V02 / GEOMETRY VERIFICATION"),
    14: dict(keys=["03-buildings", "04-green"],
             zh_h2="几何核验图 · 概念体量与绿地",
             en_h2="Geometry Verification · Masses and Green Space",
             zh_s="附页 C · V03—V04 / GEOMETRY VERIFICATION",
             en_s="APPENDIX C · V03—V04 / GEOMETRY VERIFICATION"),
    15: dict(keys=["05-publicspace", "06-keyareas"],
             zh_h2="几何核验图 · 公共空间与重点区",
             en_h2="Geometry Verification · Public Space and Key Areas",
             zh_s="附页 C · V05—V06 / GEOMETRY VERIFICATION",
             en_s="APPENDIX C · V05—V06 / GEOMETRY VERIFICATION"),
}

LEAD = {
    "zh": {
        12: ("本册第 12—15 页为几何核验图组：把 geometry 目录下提交的正式几何原样叠加在 OSM "
             "底图上直出，用来核对正文所述与包内所交是同一份几何。图组为语言中立单套，两册"
             "共用同一批图版。本页七个图层同时叠加。"),
        13: "两图各只画一个图层：用地结构与慢行线位。图面白圈为几何顶点。",
        14: "两图各只画一个图层：概念体量与绿地。图面白圈为几何顶点。",
        15: "两图分别画公共空间，以及重点区粗略范围与十个独立完成节点。图面白圈为几何顶点。",
    },
    "en": {
        12: ("Pages 12-15 are the geometry verification group: the geometry filed in the "
             "geometry directory is overlaid on an OpenStreetMap basemap exactly as "
             "submitted, so a reader can check that the text and the files describe one "
             "and the same geometry. The sheets are a single language-neutral set, shared "
             "by both booklets. This page overlays all seven layers at once."),
        13: ("Each sheet draws one layer only: land use and slow-mobility centrelines. "
             "The white rings mark geometry vertices."),
        14: ("Each sheet draws one layer only: concept masses and green space. "
             "The white rings mark geometry vertices."),
        15: ("The two sheets draw public space, and the approximate key-area extents "
             "together with the ten completion nodes. The white rings mark geometry "
             "vertices."),
    },
}

PTR = {"zh": "对应图版目录：assets/figures/", "en": "Plate directory: assets/figures/"}
