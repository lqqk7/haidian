# -*- coding: utf-8 -*-
"""重建 wpr6/wpe2/geom.pkl：几何来源改为包内现行 geometry/*.geojson。

背景
----
mobility-bluegreen 主图与其审计附图的全部图面几何与读数都来自 wpr6/wpe2/geom.pkl。
该 pkl 原由旧临时目录里的准备脚本产出，脚本已散佚，只剩 pkl 本身。roads.geojson
按真实走向加密后（五条线位由各 2 顶点变为 20—24 顶点），pkl 里的可达域、支线、
面板取景框与十行台账全部过期，必须重算。

口径与算法
----------
逐条复刻 w82/final.py（该文件的算法已逐值命中旧 pkl 的 rows 与 summary）：
  * 平面坐标 EPSG:4548
  * 网络 = roads.geojson 五条线位在交点处 node 化后的连通图
  * 节点以最短直线支线接入网络，支线长度计入行程预算；预算不足时可达线形退化
    为被预算截断的支线段
  * R_on = 300 m / R_off = 150 m（网络距离）
  * 服务带半宽 w = 40 m 缓冲成面，圆弧每象限 12 段
  * gap = 开启域 − 关闭域

不重算的部分
------------
rows 的文字字段（name_zh / scenario / gate / key_area / ai_off_path /
human_handoff）与 panels 的 area_id / key_id / name_zh / members 是文案与编排常
数，一律从旧 pkl 按 id 原样搬运，本脚本不产生任何新文案。

panels.content_bounds 的算式由旧 pkl 反解并逐值命中：
    bounds(union(该面板成员的 AI 开启域, 该面板对应重点区面))

自检
----
`python mkgeom.py --check <baseline.geojson>` 用旧线位跑同一条管线，与旧 pkl 逐
字段比对；差值应全部落在 1e-6 量级（浮点重算噪声）。这一步是本脚本可信的唯一
依据，改动算法后必须重跑。
"""
from __future__ import annotations
from pathlib import Path as _HaidianPath

import argparse
import heapq
import json
import os
import pickle
import sys

from pyproj import Transformer
from shapely.geometry import LineString, shape
from shapely.ops import substring, transform, unary_union

PKG = str(_HaidianPath(__file__).resolve().parents[3] / 'submissions/lqqk7/every-sense-jingzhang')
T = str(_HaidianPath(__file__).resolve().parents[1])
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(T, "wpr6/wpe2/geom.pkl")
OLD = os.path.join(HERE, "geom.old.pkl")

TF = Transformer.from_crs("EPSG:4326", "EPSG:4548", always_xy=True).transform
QS = 12
W = 40.0
R_ON, R_OFF = 300.0, 150.0

LAYER_KEY = [("roads", "roads"), ("green", "green_space"), ("public", "public_space"),
             ("cons", "constraints"), ("keyareas", "key_areas"),
             ("site", "site_boundary"), ("blds", "buildings")]


def gj(name):
    with open(os.path.join(PKG, "geometry", name + ".geojson"), encoding="utf-8") as f:
        return json.load(f)["features"]


def to4548(g):
    return transform(lambda x, y, z=None: TF(x, y), g)


# ---------------------------------------------------------------- 网络与可达域
def build_graph(lines):
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
        edges.append((vid(cs[0]), vid(cs[-1]), s))
    return verts, edges


class Net:
    def __init__(self, lines):
        self.verts, self.edges = build_graph(lines)
        self.adj = {}
        for k, (a, b, s) in enumerate(self.edges):
            self.adj.setdefault(a, []).append((b, k, s.length))
            self.adj.setdefault(b, []).append((a, k, s.length))

    def access(self, pt):
        return min((s.distance(pt), k, s.project(pt))
                   for k, (a, b, s) in enumerate(self.edges))

    def net_lines(self, ek, t, rem):
        a, b, s = self.edges[ek]
        out = []
        lo, hi = max(0.0, t - rem), min(s.length, t + rem)
        if hi > lo:
            out.append(substring(s, lo, hi))
        dist, pq = {}, []
        if rem - t > 0:
            heapq.heappush(pq, (rem - t, a))
        if rem - (s.length - t) > 0:
            heapq.heappush(pq, (rem - (s.length - t), b))
        while pq:
            left, v = heapq.heappop(pq)
            if dist.get(v, -1) >= left:
                continue
            dist[v] = left
            for (u, k, L) in self.adj[v]:
                e = self.edges[k][2]
                if L <= left:
                    out.append(e)
                    nl = left - L
                    if nl > dist.get(u, -1):
                        heapq.heappush(pq, (nl, u))
                else:
                    out.append(substring(e, 0, left) if self.edges[k][0] == v
                               else substring(e, e.length - left, e.length))
        return out

    def domain(self, pt, budget):
        """返回 (面域, 可达线形并集, 支线长, 支线线形)。"""
        sl, ek, t = self.access(pt)
        tip = self.edges[ek][2].interpolate(t).coords[0]
        spur = LineString([(pt.x, pt.y), tip])
        rem = budget - sl
        if rem > 0:
            L = ([spur] if sl > 1e-9 else []) + self.net_lines(ek, t, rem)
        else:
            L = [substring(spur, 0, budget)]
        return (unary_union([x.buffer(W, quad_segs=QS) for x in L]),
                unary_union(L), sl, spur)


# ------------------------------------------------------------------- 主流程
def build(roads_features):
    lay = {}
    for key, name in LAYER_KEY:
        feats = roads_features if key == "roads" else gj(name)
        lay[key] = [(f["properties"], to4548(shape(f["geometry"]))) for f in feats]

    net = Net([g for _, g in lay["roads"]])
    nodes = [(p, g) for p, g in lay["cons"] if p.get("layer") == "SCENARIO_NODE"]
    nodes.sort(key=lambda t: t[0]["id"])

    old = pickle.load(open(OLD, "rb"))
    oldrow = {r["id"]: r for r in old["rows"]}

    on, off, gap, stubs, rows = {}, {}, {}, {}, []
    for p, pt in nodes:
        nid = p["id"]
        don, lon, sl, spur = net.domain(pt, R_ON)
        doff, loff, _, _ = net.domain(pt, R_OFF)
        g = don.difference(doff)
        on[nid], off[nid], gap[nid], stubs[nid] = don, doff, g, spur
        o = oldrow[nid]
        rows.append(dict(
            id=nid, scenario=o["scenario"], gate=o["gate"], key_area=o["key_area"],
            name_zh=o["name_zh"], x=pt.x, y=pt.y, stub_m=sl,
            reach_len_on_m=lon.length, reach_len_off_m=loff.length,
            area_on_sqm=don.area, area_off_sqm=doff.area, area_gap_sqm=g.area,
            gap_share=g.area / don.area, off_share=doff.area / don.area,
            ai_off_path=o["ai_off_path"], human_handoff=o["human_handoff"]))
    rows.sort(key=lambda r: -r["area_gap_sqm"])
    for i, r in enumerate(rows):
        r["rank"] = i + 1

    ON = unary_union(list(on.values()))
    OFF = unary_union(list(off.values()))
    GAP = ON.difference(OFF)
    site = lay["site"][0][1]
    summary = dict(
        crs="EPSG:4548", R_on_m=R_ON, R_off_m=R_OFF, band_half_width_m=W,
        graph_edge_count=len(net.edges),
        graph_total_length_m=sum(e[2].length for e in net.edges),
        site_area_sqm=site.area,
        sum_gap_sqm=sum(r["area_gap_sqm"] for r in rows),
        union_on_sqm=ON.area, union_off_sqm=OFF.area, union_gap_sqm=GAP.area,
        union_gap_share=GAP.area / ON.area,
        union_on_share_of_site=ON.area / site.area)

    ka = {p["id"]: g for p, g in lay["keyareas"]}
    panels = {}
    for pid, op in old["panels"].items():
        mem = op["members"]
        b = unary_union([on[m] for m in mem] + [ka[op["key_id"]]]).bounds
        panels[pid] = dict(op, content_bounds=list(b))

    G = dict(lay)
    G.update(on=on, off=off, gap=gap, stubs=stubs, panels=panels,
             rows=rows, summary=summary)
    return G


def report(G):
    s = G["summary"]
    print("network %.3f m · edges %d" % (s["graph_total_length_m"], s["graph_edge_count"]))
    print("ON %.3f  OFF %.3f  GAP %.3f  share %.6f%%"
          % (s["union_on_sqm"], s["union_off_sqm"], s["union_gap_sqm"],
             s["union_gap_share"] * 100))
    print("on_share_of_site %.6f%%" % (s["union_on_share_of_site"] * 100))
    for r in G["rows"]:
        print("  %2d %-6s %-3s spur %8.2f  gap %10.1f  %5.1f%%"
              % (r["rank"], r["id"], r["gate"], r["stub_m"], r["area_gap_sqm"],
                 r["gap_share"] * 100))


def check(G, tol=1e-5):
    """与旧 pkl 逐字段比对（仅当输入是旧线位时才应全绿）。"""
    old = pickle.load(open(OLD, "rb"))
    bad = 0
    for k, v in old["summary"].items():
        n = G["summary"][k]
        if isinstance(v, float):
            d = abs(n - v)
            if d > tol * max(1.0, abs(v)):
                print("summary %-24s %r -> %r  Δ%.3g" % (k, v, n, d)); bad += 1
        elif n != v:
            print("summary %-24s %r -> %r" % (k, v, n)); bad += 1
    newrow = {r["id"]: r for r in G["rows"]}
    for o in old["rows"]:
        n = newrow[o["id"]]
        for k, v in o.items():
            if isinstance(v, float):
                d = abs(n[k] - v)
                if d > tol * max(1.0, abs(v)):
                    print("%s %-16s %r -> %r  Δ%.3g" % (o["id"], k, v, n[k], d)); bad += 1
            elif n[k] != v:
                print("%s %-16s %r -> %r" % (o["id"], k, v, n[k])); bad += 1
    for pid, op in old["panels"].items():
        for a, b in zip(op["content_bounds"], G["panels"][pid]["content_bounds"]):
            if abs(a - b) > 1e-4:
                print("panel %s bounds %r -> %r" % (pid, a, b)); bad += 1
    print("check: %d 处不一致" % bad)
    return bad


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", metavar="GEOJSON",
                    help="用给定的旧 roads.geojson 复跑并与 geom.old.pkl 比对，不落盘")
    a = ap.parse_args()
    if a.check:
        feats = json.load(open(a.check, encoding="utf-8"))["features"]
        G = build(feats)
        report(G)
        sys.exit(1 if check(G) else 0)
    G = build(gj("roads"))
    report(G)
    with open(OUT, "wb") as f:
        pickle.dump(G, f)
    print("wrote", OUT, os.path.getsize(OUT), "B")
