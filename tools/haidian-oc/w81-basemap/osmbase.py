# -*- coding: utf-8 -*-
"""OSM 底图引擎（WP-81）。

职责
----
1. 把随包分发的两片 OSM 快照按其自述的 schema 字段级合并还原（只在
   scratchpad 内进行，包内文件不动）。
2. 提供两套坐标：WGS84 经纬度（EPSG:4326）与复算投影平面米（EPSG:4548）。
3. 按 highway / railway 标签把 way 分为五个绘制层级，供图版最底层铺设。

约束
----
* 快照只包含 highway 与 railway 两类 way 以及三类穿越 node（见 meta.provenance
  的逐字查询语句），**不含建筑物、水系、土地利用**。本引擎因此只能输出路网与
  轨道底图；建筑浅填充与水系淡蓝在本包数据条件下无法提供，图注须如实说明。
* 快照的完整覆盖范围仅限查询 bbox（场地 bbox 四向外扩 300 m）。bbox 之外只有
  "与 bbox 相交的 way 的完整几何"，属不完整覆盖，需在超出范围时如实标注。
"""
from __future__ import annotations
from pathlib import Path as _HaidianPath

import json
import os

PKG = str(_HaidianPath(__file__).resolve().parents[3] / 'submissions/lqqk7/every-sense-jingzhang')
SNAP_DIR = os.path.join(PKG, "visual/assets/osm-fabric")

# ------------------------------------------------------------------ 合并还原
_CACHE = {}


def load_snapshot():
    """按 meta.schema 的 ways_row / nodes_row 定义合并两片快照。"""
    if "snap" in _CACHE:
        return _CACHE["snap"]
    ways, nodes, meta = [], [], None
    for part in ("osm-fabric-snapshot-part1.json", "osm-fabric-snapshot-part2.json"):
        with open(os.path.join(SNAP_DIR, part), encoding="utf-8") as f:
            d = json.load(f)
        if d.get("part", "").startswith("1"):
            meta = d["meta"]
        ways += d["ways"]
        nodes += d["nodes"]
    assert meta is not None
    c = meta["counts"]
    assert len(ways) == c["ways"], (len(ways), c["ways"])
    assert len(nodes) == c["nodes"], (len(nodes), c["nodes"])
    assert sum(len(w[5]) for w in ways) == c["way_vertices"]
    _CACHE["snap"] = (meta, ways, nodes)
    return _CACHE["snap"]


def query_bbox():
    """快照完整覆盖范围 (minlon, minlat, maxlon, maxlat)。"""
    meta, _, _ = load_snapshot()
    s, w, n, e = meta["extent"]["query_bbox_wgs84_s_w_n_e"]
    return (w, s, e, n)


# ------------------------------------------------------------------ 图层分级
# (层名, highway 值集合, railway 值集合, 颜色, CSS px 线宽, dasharray)
LAYERS = [
    ("path",    {"footway", "path", "steps", "cycleway", "pedestrian", "track",
                 "platform", "elevator", "construction"}, set(),
     "#e7e7e7", 0.35, None),
    ("minor",   {"service", "residential", "unclassified", "living_street"}, set(),
     "#e0e0e0", 0.55, None),
    ("subway",  set(), {"subway"}, "#e2e2e2", 0.7, "3 3"),
    ("mid",     {"tertiary", "tertiary_link", "secondary", "secondary_link"}, set(),
     "#d8d8d8", 0.9, None),
    ("major",   {"motorway", "motorway_link", "trunk", "trunk_link",
                 "primary", "primary_link"}, set(),
     "#cfcfcf", 1.25, None),
    ("rail",    set(), {"rail", "disused", "razed"}, "#c4c4c4", 1.0, "6 3"),
]
LAYER_ORDER = [l[0] for l in LAYERS]        # 绘制次序：细 -> 粗


def classify(row):
    """一条 way -> 层名；不属于任何层返回 None。"""
    hw, rw = row[1], row[2]
    for name, hs, rs, _c, _w, _d in LAYERS:
        if (hw is not None and hw in hs) or (rw is not None and rw in rs):
            return name
    return None


def layered_ways():
    """{层名: [坐标串(lon,lat), ...]}，按 LAYER_ORDER 绘制。"""
    if "layers" in _CACHE:
        return _CACHE["layers"]
    _meta, ways, _nodes = load_snapshot()
    out = {n: [] for n in LAYER_ORDER}
    for row in ways:
        k = classify(row)
        if k:
            out[k].append(row[5])
    _CACHE["layers"] = out
    return out


LAYER_STYLE = {n: (c, w, d) for n, _h, _r, c, w, d in LAYERS}


# ------------------------------------------------------------------ 投影
def to_4548():
    """经纬度 -> EPSG:4548（CGCS2000 3-degree Gauss-Kruger CM 117E）转换函数。"""
    from pyproj import Transformer
    return Transformer.from_crs("EPSG:4326", "EPSG:4548", always_xy=True).transform


# ------------------------------------------------------------------ SVG 输出
def _fmt(v):
    s = f"{v:.2f}"
    return s.rstrip("0").rstrip(".") if "." in s else s


def basemap_svg(to_px, clip_box, px_scale=1.0, vector_effect=False,
                min_len_px=1.6, layers=None, opacity=None):
    """生成底图 <g> 字符串。

    to_px      : (lon, lat) -> (x, y) 目标 SVG 用户单位
    clip_box   : (x0, y0, x1, y1) 目标坐标系的可见窗口；超出即丢弃
    px_scale   : 用户单位/CSS px（线宽换算用；用户单位就是 px 时填 1）
    vector_effect: 用户单位不是 px 时置 True，走 non-scaling-stroke
    min_len_px : 短于此长度（CSS px）的线段整体丢弃，避免噪点
    """
    x0, y0, x1, y1 = clip_box
    pad = 4.0 * px_scale
    x0, y0, x1, y1 = x0 - pad, y0 - pad, x1 + pad, y1 + pad
    L = layered_ways()
    ve = ' vector-effect="non-scaling-stroke"' if vector_effect else ""
    out = ['<g class="osmbase" fill="none" stroke-linecap="round" '
           'stroke-linejoin="round"'
           + (f' opacity="{opacity}"' if opacity else "") + '>']
    for name in (layers or LAYER_ORDER):
        col, wid, dash = LAYER_STYLE[name]
        ds = []
        for coords in L[name]:
            pts = [to_px(c[0], c[1]) for c in coords]
            # 逐段裁剪：保留至少有一端在窗口内、或跨窗口的整段折线
            keep, run = [], []
            for i, p in enumerate(pts):
                inside = x0 <= p[0] <= x1 and y0 <= p[1] <= y1
                if inside:
                    if not run and i:
                        run.append(pts[i - 1])
                    run.append(p)
                else:
                    if run:
                        run.append(p)
                        keep.append(run)
                        run = []
            if run:
                keep.append(run)
            for r in keep:
                if len(r) < 2:
                    continue
                span = max(abs(r[-1][0] - r[0][0]), abs(r[-1][1] - r[0][1]))
                if span < min_len_px * px_scale and len(r) < 4:
                    continue
                ds.append("M" + " L".join(f"{_fmt(a)} {_fmt(b)}" for a, b in r))
        if not ds:
            continue
        sw = wid if vector_effect else wid * px_scale
        d = f' stroke-dasharray="{dash}"' if dash else ""
        out.append(f'<path d="{"".join(ds)}" stroke="{col}" '
                   f'stroke-width="{_fmt(sw)}"{d}{ve}/>')
    out.append("</g>")
    return "".join(out)


if __name__ == "__main__":
    meta, ways, nodes = load_snapshot()
    L = layered_ways()
    print("合并还原：ways=%d nodes=%d vertices=%d"
          % (len(ways), len(nodes), sum(len(w[5]) for w in ways)))
    print("完整覆盖 bbox (lon/lat):", query_bbox())
    for n in LAYER_ORDER:
        print(f"  {n:7s} {len(L[n]):5d} 条")
    unclassified = sum(1 for w in ways if classify(w) is None)
    print("未归层 way:", unclassified)
