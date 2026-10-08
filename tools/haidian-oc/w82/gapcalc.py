# -*- coding: utf-8 -*-
"""十节点可达域差集复算（B 路管线口径）。

口径（取自 mobility-bluegreen 图版 01 / CALIBER 节与图注）：
  * 平面坐标 EPSG:4548
  * 网络 = roads.geojson 五条线位在交点处打断后的连通图
  * 节点以最短直线支线接入网络，支线长度计入行程预算
  * AI 开启域 R_on = 300 m 网络距离；AI 关闭域 R_off = 150 m 网络距离
  * 服务带半宽 w = 40 m 缓冲成面（圆弧每象限 12 段）
  * gap = 开启并集 − 关闭并集
"""
from __future__ import annotations
from pathlib import Path as _HaidianPath

import heapq
import json
import math
import os
import sys

from pyproj import Transformer
from shapely.geometry import LineString, MultiLineString, Point, shape
from shapely.ops import linemerge, unary_union, substring, transform

PKG = str(_HaidianPath(__file__).resolve().parents[3] / 'submissions/lqqk7/every-sense-jingzhang')
TF = Transformer.from_crs("EPSG:4326", "EPSG:4548", always_xy=True).transform
QS = 12          # 圆弧每象限段数
W = 40.0         # 服务带半宽
R_ON, R_OFF = 300.0, 150.0


def gj(name):
    with open(os.path.join(PKG, "geometry", name + ".geojson"), encoding="utf-8") as f:
        return json.load(f)["features"]


def to4548(geom):
    return transform(lambda x, y, z=None: TF(x, y), geom)


roads = [to4548(shape(f["geometry"])) for f in gj("roads")]
nodes = [(f["properties"]["id"], f["properties"]["scenario_id"],
          f["properties"]["gate_id"], to4548(shape(f["geometry"])))
         for f in gj("constraints")
         if f["properties"].get("layer") == "SCENARIO_NODE"]
nodes.sort(key=lambda t: t[0])

print("roads raw total %.1f m" % sum(r.length for r in roads))

# ---------------------------------------------------------------- 打断成图
def build_graph(lines, snap=1e-6):
    """在所有交点处打断，返回 (顶点表, 边表[(i,j,LineString)])。"""
    merged = unary_union(lines)          # shapely 的 unary_union 会在交点处 node 化
    merged = linemerge(merged) if merged.geom_type != "LineString" else merged
    segs = list(merged.geoms) if merged.geom_type == "MultiLineString" else [merged]
    # linemerge 会把交点处再接起来，故用 unary_union 的 noded 结果重新拆
    noded = unary_union(lines)
    segs = list(noded.geoms) if noded.geom_type == "MultiLineString" else [noded]
    verts, index, edges = [], {}, []

    def vid(pt):
        k = (round(pt[0], 6), round(pt[1], 6))
        if k not in index:
            index[k] = len(verts)
            verts.append(k)
        return index[k]

    for s in segs:
        cs = list(s.coords)
        a, b = vid(cs[0]), vid(cs[-1])
        edges.append((a, b, s))
    return verts, edges


verts, edges = build_graph(roads)
print("graph: %d verts %d edges  total %.1f m"
      % (len(verts), len(edges), sum(e[2].length for e in edges)))

# ------------------------------------------------------------ 网络距离可达集
adj = {}
for k, (a, b, s) in enumerate(edges):
    adj.setdefault(a, []).append((b, k, s.length))
    adj.setdefault(b, []).append((a, k, s.length))


def reach_lines(pt, budget, with_spur=True):
    """从 pt 起，最短直线支线接入网络后，网络距离 <= budget 的可达线形。"""
    # 接入点：网络上最近点
    best = None
    for k, (a, b, s) in enumerate(edges):
        d = s.distance(pt)
        if best is None or d < best[0]:
            best = (d, k, s.project(pt))
    spur_len, ek, t = best
    a, b, s = edges[ek]
    rem = budget - spur_len
    out = []
    if rem <= 0:
        return out
    if with_spur and spur_len > 1e-9:
        out.append(LineString([(pt.x, pt.y), s.interpolate(t).coords[0]]))
    # 起始边上双向展开
    lo = max(0.0, t - rem)
    hi = min(s.length, t + rem)
    if hi > lo:
        out.append(substring(s, lo, hi))
    dist = {}
    pq = []
    if rem - t > 0:
        heapq.heappush(pq, (rem - t, a))          # 剩余预算写成"到达顶点后余额"
    if rem - (s.length - t) > 0:
        heapq.heappush(pq, (rem - (s.length - t), b))
    while pq:
        left, v = heapq.heappop(pq)
        if dist.get(v, -1) >= left:
            continue
        dist[v] = left
        for (u, k, L) in adj[v]:
            if k == ek and v in (a, b):
                pass
            e = edges[k][2]
            if L <= left:
                out.append(e)
                nl = left - L
                if nl > dist.get(u, -1):
                    heapq.heappush(pq, (nl, u))
            else:
                # 部分覆盖
                if edges[k][0] == v:
                    out.append(substring(e, 0, left))
                else:
                    out.append(substring(e, e.length - left, e.length))
    return out


def domain(pt, budget, with_spur=True):
    ls = reach_lines(pt, budget, with_spur)
    if not ls:
        return None
    return unary_union([l.buffer(W, quad_segs=QS) for l in ls])


for with_spur in (True, False):
    on_u, off_u, rows = [], [], []
    for nid, sid, gate, p in nodes:
        don = domain(p, R_ON, with_spur)
        doff = domain(p, R_OFF, with_spur)
        on_u.append(don)
        if doff is not None:
            off_u.append(doff)
        g = don.difference(doff) if doff is not None else don
        rows.append((nid, sid, gate, don.area, doff.area if doff else 0.0, g.area))
    ON = unary_union(on_u)
    OFF = unary_union(off_u)
    GAP = ON.difference(OFF)
    print("\n== with_spur=%s ==" % with_spur)
    print("ON  %,.0f  OFF %,.0f  GAP %,.0f  share %.4f%%"
          .replace(",", "") % (ON.area, OFF.area, GAP.area, GAP.area / ON.area * 100))
    for r in sorted(rows, key=lambda r: -r[5]):
        print("  %s %s %s  on=%9.1f off=%9.1f gap=%9.1f  %.1f%%"
              % (r[0], r[1], r[2], r[3], r[4], r[5], r[5] / r[3] * 100))
