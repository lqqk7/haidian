# -*- coding: utf-8 -*-
"""roads.geojson 五条线位按包内 OSM 快照的真实走向加密（零手绘、可复现）。

方法（对应任务书「空间最近邻 + 走向一致 → Douglas-Peucker 简化 → 端点不动」）
------------------------------------------------------------------------
1. 数据源：包内 OSM 快照 visual/assets/osm-fabric/osm-fabric-snapshot-part1.json
   与 part2.json 的全部 highway way。剔除步行不可用与机动车专用类
   （motorway / motorway_link / construction / proposed / steps / elevator）
   与带 foot=no、access=private、access=no 的 way，剩余 way 拆成线段集。

2. 站点采样：把原线位（直线）按 STEP 米等分为若干站点。每个站点作原线位的
   法线，长度 ±RMAX 米，与线段集求交，得到一组「带符号横向偏移」候选；只保留
   走向与原线位夹角 <= BEAR 度的线段（走向一致判据）。

3. 走廊选线（Viterbi 动态规划，全局最优，无人工取舍）：
     节点代价 = ALPHA x |横向偏移|                （贴合原线位声明的位置）
     转移代价 = GAMMA x |横向偏移变化| + BETA x [换街道]（线形连续、不跳街）
     无候选的站点以原线位点作兜底候选，代价加 GAP_PEN（如实登记为「无快照依托」）。
   最优路径即该走廊在快照中的真实走向。

4. 平行约束：安静替代线（ROAD-005）在主脊（ROAD-001）结果求出后再解，候选点
   落在主脊 SEP 米内者加 PARA 惩罚，避免两条线位塌陷成同一条路。

5. 首尾替换为原端点坐标（端点不动，constraints 节点挂接不连锁），Douglas-Peucker
   简化，容差二分搜索使顶点数落在 [15, 25] 且尽量接近 20。

坐标平面：EPSG:4548（与 metrics.json / gapcalc 复算口径一致）。
"""
from __future__ import annotations
from pathlib import Path as _HaidianPath

import json
import math
import os

from pyproj import Transformer
from shapely.geometry import LineString, Point
from shapely.strtree import STRtree

PKG = str(_HaidianPath(__file__).resolve().parents[3] / 'submissions/lqqk7/every-sense-jingzhang')
HERE = os.path.dirname(os.path.abspath(__file__))
TF = Transformer.from_crs("EPSG:4326", "EPSG:4548", always_xy=True).transform
INV = Transformer.from_crs("EPSG:4548", "EPSG:4326", always_xy=True).transform

EXCLUDE = {"motorway", "motorway_link", "construction", "proposed",
           "elevator", "steps"}
BLOCK_TAGS = {("foot", "no"), ("access", "private"), ("access", "no")}

STEP = 40.0        # 站点间距 m
RMAX = 260.0       # 法线搜索半径 m
BEAR = 45.0        # 走向一致容差 度
ALPHA = 0.35       # 贴合原线位权重
BETA = 100.0       # 换街道惩罚 m
GAP_PEN = 90.0     # 无候选兜底惩罚 m
SEP = 130.0        # 平行约束触发距离 m
GAMMA = 3.0        # 横向位移平滑权重
PARA = 150.0       # 平行约束惩罚 m
TARGET, VMIN, VMAX = 24, 15, 25


def load_ways():
    ws = []
    for p in ("part1", "part2"):
        f = os.path.join(PKG, "visual/assets/osm-fabric",
                         "osm-fabric-snapshot-%s.json" % p)
        ws += json.load(open(f, encoding="utf-8"))["ways"]
    out = []
    for w in ws:
        if not w[1] or w[1] in EXCLUDE:
            continue
        t = w[4] or {}
        if any((k, t.get(k)) in BLOCK_TAGS for k in ("foot", "access")):
            continue
        out.append(w)
    return out


WAYS = load_ways()

SEGS, SEGMETA = [], []
for w in WAYS:
    ident = w[3] or ("way%d" % w[0])
    cs = [TF(*c) for c in w[5]]
    for a, b in zip(cs, cs[1:]):
        if a == b:
            continue
        SEGS.append(LineString([a, b]))
        SEGMETA.append((ident, w[0], w[1], w[3]))
TREE = STRtree(SEGS)


def bearing(p, q):
    return math.degrees(math.atan2(q[1] - p[1], q[0] - p[0])) % 180.0


def angdiff(a, b):
    d = abs(a - b) % 180.0
    return min(d, 180.0 - d)


def candidates(px, py, nx, ny, theta, avoid):
    """站点法线上的候选：返回 [(offset, ident, wayid, hw, name)]。"""
    probe = LineString([(px - nx * RMAX, py - ny * RMAX),
                        (px + nx * RMAX, py + ny * RMAX)])
    out, seen = [], {}
    for i in TREE.query(probe):
        seg = SEGS[i]
        cs = list(seg.coords)
        if angdiff(bearing(cs[0], cs[1]), theta) > BEAR:
            continue
        it = seg.intersection(probe)
        if it.is_empty:
            continue
        pts = [it] if it.geom_type == "Point" else list(getattr(it, "geoms", []))
        for pt in pts:
            if pt.geom_type != "Point":
                continue
            off = (pt.x - px) * nx + (pt.y - py) * ny
            ident, wid, hw, nm = SEGMETA[i]
            pen = 0.0
            if avoid is not None and avoid.distance(pt) <= SEP:
                pen = PARA
            k = ident
            if k not in seen or abs(off) < abs(seen[k][0]):
                seen[k] = (off, ident, wid, hw, nm, pen)
    out = sorted(seen.values(), key=lambda t: abs(t[0]))[:6]
    return out


def solve(line_wgs, avoid=None):
    a, b = TF(*line_wgs[0]), TF(*line_wgs[-1])
    L = math.hypot(b[0] - a[0], b[1] - a[1])
    ux, uy = (b[0] - a[0]) / L, (b[1] - a[1]) / L
    nx, ny = -uy, ux
    theta = bearing(a, b)
    n = max(2, int(round(L / STEP)))
    stations, gaps = [], 0
    for i in range(n + 1):
        t = L * i / n
        px, py = a[0] + ux * t, a[1] + uy * t
        cs = candidates(px, py, nx, ny, theta, avoid)
        if not cs:
            cs = [(0.0, "__gap__", None, None, None, GAP_PEN)]
            gaps += 1
        stations.append(((px, py), cs))

    # Viterbi
    INF = float("inf")
    prevcost = [ALPHA * abs(c[0]) + c[5] for c in stations[0][1]]
    back = []
    for i in range(1, len(stations)):
        cur = stations[i][1]
        cost, bk = [], []
        for c in cur:
            best, bj = INF, 0
            for j, p in enumerate(stations[i - 1][1]):
                v = (prevcost[j] + GAMMA * abs(c[0] - p[0])
                     + (0.0 if c[1] == p[1] else BETA))
                if v < best:
                    best, bj = v, j
            cost.append(best + ALPHA * abs(c[0]) + c[5])
            bk.append(bj)
        prevcost, _ = cost, None
        back.append(bk)
    j = min(range(len(prevcost)), key=lambda k: prevcost[k])
    idx = [j]
    for i in range(len(back) - 1, -1, -1):
        j = back[i][j]
        idx.append(j)
    idx.reverse()

    pts, used, gapstations = [], set(), 0
    for i, ((px, py), cs) in enumerate(stations):
        off, ident, wid, hw, nm, pen = cs[idx[i]]
        if ident == "__gap__":
            gapstations += 1
        else:
            used.add((wid, nm, hw))
        pts.append((px + nx * off, py + ny * off))
    return pts, used, gapstations, len(stations)


def densify(feat, avoid=None):
    line = feat["geometry"]["coordinates"]
    pts, used, gapst, nst = solve(line, avoid)
    coords = [list(line[0])] + [[round(v, 6) for v in INV(x, y)]
                                for x, y in pts[1:-1]] + [list(line[-1])]
    raw = LineString(coords)
    lo, hi, best = 0.0, 0.02, None
    for _ in range(90):
        mid = (lo + hi) / 2
        s = raw.simplify(mid, preserve_topology=False)
        k = len(s.coords)
        if best is None or abs(k - TARGET) < abs(best[1] - TARGET):
            best = (mid, k, s)
        if k > TARGET:
            lo = mid
        else:
            hi = mid
    tol, k, s = best
    if not (VMIN <= k <= VMAX):
        cands = []
        for i in range(1, 8000):
            t = i * 2e-6
            ss = raw.simplify(t, preserve_topology=False)
            m = len(ss.coords)
            if VMIN <= m <= VMAX:
                cands.append((abs(m - TARGET), t, m, ss))
            if m < VMIN:
                break
        if cands:
            cands.sort()
            _, tol, k, s = cands[0]
    out = [[round(x, 6), round(y, 6)] for x, y in s.coords]
    out[0] = list(line[0])
    out[-1] = list(line[-1])
    dev = LineString([TF(*c) for c in out]).hausdorff_distance(
        LineString([TF(*c) for c in coords]))
    return dict(coords=out, nvert=len(out), tol=tol, dp_dev_m=dev, stations=nst,
                gap_stations=gapst, raw_vert=len(coords),
                ways=sorted({u[0] for u in used}),
                way_names=sorted({u[1] for u in used if u[1]}),
                way_classes=sorted({u[2] for u in used if u[2]}))


# ------------------------------------------------------------------ 输出
def emit(rep):
    """把加密结果写成新的 roads.geojson（含 densification 登记块）。"""
    gj = json.load(open(os.path.join(HERE, "roads.baseline.geojson"),
                        encoding="utf-8"))
    NOTE = {
        "ROAD-001": ("主脊沿学院路—学清路—西土城路—交通大学路一线的既有走向取样；"
                     "该线是场地内唯一贯通南北的连续公共步行走廊。",
                     "The spine samples the existing alignment of the Xueyuan Road / "
                     "Xueqing Road / Xitucheng Road / Jiaotong University Road line, "
                     "the only continuous north-south public pedestrian corridor on site."),
        "ROAD-002": ("沿域清街—月泉路—银泉路一线取样；该横向接口在快照中有连续"
                     "依托，走向随既有街道错位。",
                     "Sampled along the Yuqing Street / Yuequan Road / Yinquan Road line; "
                     "this crossing has continuous support in the snapshot and its "
                     "alignment follows the offsets of the existing streets."),
        "ROAD-003": ("沿摇篮路一线取样；该横向接口在快照中由单一街道连续依托。",
                     "Sampled along the Yaolan Road line; this crossing is continuously "
                     "supported by a single street in the snapshot."),
        "ROAD-004": ("沿北三环西路—师大北路一线取样；该横向接口跨越大钟寺站域，"
                     "走向随既有街道与铁路走廊错位。",
                     "Sampled along the West North 3rd Ring Road / Shida North Road line; "
                     "this crossing spans the Dazhongsi station area and its alignment "
                     "follows the offsets of the existing streets and the rail corridor."),
        "ROAD-005": ("沿小月河西侧道—石清路—西土城路—西直门北大街一线取样，并对"
                     "距主脊 130 m 以内的候选加惩罚，使安静替代线保持为独立线位；"
                     "两条线位最小间距 %s m。",
                     "Sampled along the Xiaoyue River west-bank path / Shiqing Road / "
                     "Xitucheng Road / Xizhimen North Street line, with a penalty on "
                     "candidates within 130 m of the spine so that the quiet alternative "
                     "remains a distinct alignment; the minimum separation between the "
                     "two lines is %s m."),
    }
    for f in gj["features"]:
        rid = f["properties"]["id"]
        d = rep[rid]
        zh, en = NOTE[rid]
        if rid == "ROAD-005":
            zh = zh % ("%.0f" % d["sep_to_spine"])
            en = en % ("%.0f" % d["sep_to_spine"])
        f["properties"]["densification"] = {
            "method_zh": "包内 OSM 快照法线取样（空间最近邻 + 走向一致）后按 "
                         "Douglas-Peucker 简化；端点坐标不变。",
            "method_en": "Normal-section sampling of the in-package OpenStreetMap "
                         "snapshot (nearest neighbour with bearing agreement), then "
                         "Douglas-Peucker simplification; endpoint coordinates unchanged.",
            "source_files": [
                "visual/assets/osm-fabric/osm-fabric-snapshot-part1.json",
                "visual/assets/osm-fabric/osm-fabric-snapshot-part2.json"],
            "source_way_ids": d["ways"],
            "source_way_names": d["way_names"],
            "source_way_classes": d["way_classes"],
            "station_spacing_m": STEP,
            "normal_search_radius_m": RMAX,
            "bearing_tolerance_deg": BEAR,
            "station_count": d["stations"],
            "stations_without_snapshot_support": d["gap_stations"],
            "simplify_tolerance_deg": round(d["tol"], 7),
            "simplify_max_deviation_m": round(d["dp_dev_m"], 3),
            "vertex_count_before": 2,
            "vertex_count_after": d["nvert"],
            "endpoints_unchanged": True,
            "length_before_m": round(d["old_len"], 3),
            "length_after_m": round(d["new_len"], 3),
            "sinuosity": round(d["new_len"] / d["old_len"], 4),
            "note_zh": zh,
            "note_en": en,
            "toolchain": "w85-densify/densify.py",
            "projection": "EPSG:4548",
        }
        f["geometry"]["coordinates"] = d["coords"]
    out = os.path.join(HERE, "roads.densified.geojson")
    json.dump(gj, open(out, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    print("wrote", out)


if __name__ == "__main__":
    gj = json.load(open(os.path.join(HERE, "roads.baseline.geojson"),
                        encoding="utf-8"))
    feats = {f["properties"]["id"]: f for f in gj["features"]}
    rep, spine = {}, None
    for rid in ("ROAD-001", "ROAD-002", "ROAD-003", "ROAD-004", "ROAD-005"):
        f = feats[rid]
        d = densify(f, avoid=spine if rid == "ROAD-005" else None)
        old = LineString([TF(*c) for c in f["geometry"]["coordinates"]])
        new = LineString([TF(*c) for c in d["coords"]])
        d["old_len"], d["new_len"] = old.length, new.length
        d["hausdorff"] = old.hausdorff_distance(new)
        if rid == "ROAD-001":
            spine = new
        d["sep_to_spine"] = None if rid == "ROAD-001" else spine.distance(new)
        rep[rid] = d
        print("%s n=%2d tol=%.7f gap=%3d/%3d len %8.1f -> %8.1f (x%.3f) "
              "hd=%5.1f ways=%3d names=%d"
              % (rid, d["nvert"], d["tol"], d["gap_stations"], d["stations"],
                 d["old_len"], d["new_len"], d["new_len"] / d["old_len"],
                 d["hausdorff"], len(d["ways"]), len(d["way_names"])))
    tot = sum(v["new_len"] for v in rep.values())
    off = rep["ROAD-001"]["new_len"] + rep["ROAD-005"]["new_len"]
    print("TOTAL %.3f (old 20140.587)  AI-off %.3f (old 17322.014)" % (tot, off))
    emit(rep)
    json.dump(rep, open(os.path.join(HERE, "densify-report.json"), "w"),
              indent=1, ensure_ascii=False)


