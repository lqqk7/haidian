# -*- coding: utf-8 -*-
"""assets/figures/district-concept-sections.png —— 三片区概念详图（三联）。

每联取一个真实典型段，把包内既有的制度性判据落成一次空间组合：
  联 A 众智园 ZZY-BK-01 贯通通道段 + OP-01
  联 B 原点社区 ROAD-003 接口段 + OP-02（三候选块距接口均 0 m）
  联 C 大钟寺 OP-04 段 + 万感服务桌（SD-1→SD-4 位序）

街块轮廓、中心线、节点、公共空间面与轨道接入点簇为包内既有数据，实线绘制；
通道线位、建筑体量、界面分段、入口与服务点位为概念设想，虚线绘制，逐要素在
图面标注其既有判据来源。三联同取向（北向右）、同比例尺。
"""
from __future__ import annotations

import math
import os

from shapely.geometry import LineString, Point, Polygon
from shapely.ops import substring

from common import (ATTR_EN, ATTR_ZH, C, CRS_ZH, DS, DSF, GREEN, H, KEYA, NODES,
                    PAD, PKG, PUBLIC, RINGS,
                    ROADS, SDC, W, MLAT, MLON, base_css, esc, f1, head, label,
                    north_right, osmbase, render, scalebar, th)

MAP_W, MAP_H = 370.0, 258.0
MPP = 3.3                          # 三联共用比例尺：1 CSS px = 3.3 m
# 取 3.1 的理由：联 B 三块候选沿经度方向展开 805 m，落在图面纵轴；纵轴 264 px 要
# 整幅装下即 MPP ≥ 3.12；取 3.3 留出两侧各约 23 m 余量。三联同比例尺是本图的
# 可比性前提，故三联一并取该值。
GAP = 15.0

FR = {c["class_id"]: c for c in DS["frontage_rules"]["classes"]}
FRC = {"active_frontage": C["coral"], "display_frontage": C["gold"],
       "quiet_frontage": C["purple"]}
SPEC = C["spec"]

# 各区街块中位规模的等效方形边长（既有参考标尺，见 frontage_rules.reference_scale）
SPACING = {"zzy": 50.5, "aio": 41.0, "dzs": 31.1}
BANDS = [("多模态导路带", "Wayfinding", 2.50, C["teal"]),
         ("触觉引导带", "Tactile", 0.30, C["deep"]),
         ("设施带", "Equipment", 1.20, C["gold"]),
         ("安静缓冲绿带", "Quiet buffer", 1.50, "#8fae8a")]


class Frame:
    """单联的局部平面米框架 + 北向右投影。"""

    def __init__(self, clon, clat):
        self.clon, self.clat = clon, clat

    def m(self, lon, lat):
        return ((lon - self.clon) * MLON, (lat - self.clat) * MLAT)

    def ll(self, x, y):
        return (self.clon + x / MLON, self.clat + y / MLAT)

    def px(self, x, y):
        return (MAP_W / 2 + y / MPP, MAP_H / 2 + x / MPP)

    def pxll(self, lon, lat):
        return self.px(*self.m(lon, lat))

    def poly(self, ring):
        return Polygon([self.m(*c) for c in ring])

    def line(self, coords):
        return LineString([self.m(*c) for c in coords])

    def d(self, geom, close=False):
        cs = (list(geom.exterior.coords) if isinstance(geom, Polygon)
              else list(geom.coords))
        p = "M" + " L".join("%s %s" % tuple(f1(v) for v in self.px(*c)) for c in cs)
        return p + ("Z" if close or isinstance(geom, Polygon) else "")


def rect_along(line, s, half_len, offset, width):
    """沿 line 在链距 s 处、法向偏移 offset 处放一块矩形概念体量。"""
    a = line.interpolate(max(0.0, s - half_len))
    b = line.interpolate(min(line.length, s + half_len))
    dx, dy = b.x - a.x, b.y - a.y
    L = math.hypot(dx, dy) or 1.0
    ux, uy = dx / L, dy / L
    nx, ny = -uy, ux
    cx, cy = (a.x + b.x) / 2 + nx * offset, (a.y + b.y) / 2 + ny * offset
    hl, hw = L / 2, width / 2
    return Polygon([(cx + ux * hl + nx * hw, cy + uy * hl + ny * hw),
                    (cx + ux * hl - nx * hw, cy + uy * hl - ny * hw),
                    (cx - ux * hl - nx * hw, cy - uy * hl - ny * hw),
                    (cx - ux * hl + nx * hw, cy - uy * hl + ny * hw)])


def spaced(line, step, inset=0.0):
    n = int((line.length - 2 * inset) // step)
    return [line.interpolate(inset + i * step) for i in range(n + 1)]


def ticks(line, step, length, side=1.0):
    out = []
    for i, p in enumerate(spaced(line, step)):
        s = min(line.length, max(0.0, line.project(p)))
        a = line.interpolate(max(0.0, s - 2)), line.interpolate(min(line.length, s + 2))
        dx, dy = a[1].x - a[0].x, a[1].y - a[0].y
        L = math.hypot(dx, dy) or 1.0
        nx, ny = -dy / L * side, dx / L * side
        out.append(LineString([(p.x, p.y), (p.x + nx * length, p.y + ny * length)]))
    return out


# --------------------------------------------------------------- 底图与数据层
def basemap(fr):
    def to_px(lon, lat):
        return fr.pxll(lon, lat)
    # 不铺 path 与 minor 两层：本图比例尺下步行小径与支路会织成一层灰噪，既压掉概念
    # 要素的可辨性，也把量化后的字节数抬高；底图只保留主次干道与轨道，图注如实说明。
    return osmbase.basemap_svg(to_px, (0, 0, MAP_W, MAP_H), px_scale=1.0,
                               layers=["subway", "mid", "major", "rail"])


def data_layer(fr, road_ids, node_ids, public_ids, key_id=None, green_ids=()):
    o = []
    if key_id:
        f = KEYA[key_id]
        o.append(f'<path d="{fr.d(fr.poly(f["geometry"]["coordinates"][0]))}" '
                 f'fill="{C["coral"]}0a" stroke="{C["coral"]}" stroke-width="1.4" '
                 f'stroke-dasharray="7 4"/>')
    for gid in green_ids:
        g = GREEN[gid]
        o.append(f'<path d="{fr.d(fr.poly(g["geometry"]["coordinates"][0]))}" '
                 f'fill="#cbdcc6" fill-opacity=".55" stroke="#8fae8a" '
                 f'stroke-width="1"/>')
    for pid in public_ids:
        p = PUBLIC[pid]
        o.append(f'<path d="{fr.d(fr.poly(p["geometry"]["coordinates"][0]))}" '
                 f'fill="{C["sky"]}22" stroke="{C["sky"]}" stroke-width="1.2" '
                 f'stroke-dasharray="3.5 2.4"/>')
    for rid in road_ids:
        r = ROADS[rid]
        st = (f'stroke="{C["teal"]}" stroke-width="2.8"' if rid == "ROAD-001" else
              f'stroke="{C["purple"]}" stroke-width="2.4" stroke-dasharray="7 5"'
              if rid == "ROAD-005" else f'stroke="{C["sky"]}" stroke-width="2.4"')
        o.append(f'<path d="{fr.d(fr.line(r["geometry"]["coordinates"]))}" '
                 f'fill="none" {st} stroke-linecap="round"/>')
    npx = [fr.pxll(*NODES[n]["geometry"]["coordinates"][:2]) for n in node_ids]
    for pid in public_ids:
        p = PUBLIC[pid]
        ring = p["geometry"]["coordinates"][0]
        cx = sum(c[0] for c in ring[:-1]) / (len(ring) - 1)
        cy = sum(c[1] for c in ring[:-1]) / (len(ring) - 1)
        x, y = fr.pxll(cx, cy)
        near = any(abs(x - a) < 46 and abs(y - b) < 20 for a, b in npx)
        if not near and 24 < x < MAP_W - 24 and 10 < y < MAP_H - 34:
            o.append(label(x, y, pid, C["sky"], anchor="middle"))
    for nid in node_ids:
        x, y = fr.pxll(*NODES[nid]["geometry"]["coordinates"][:2])
        o.append(f'<circle cx="{f1(x)}" cy="{f1(y)}" r="4.6" fill="{C["purple"]}" '
                 f'stroke="#fff" stroke-width="1.5"/>')
    return "".join(o)


def node_labels(fr, node_ids):
    """节点编号最后落笔：压在设想层之上，避免被入口点位与体量块盖住。"""
    o = []
    for nid in node_ids:
        x, y = fr.pxll(*NODES[nid]["geometry"]["coordinates"][:2])
        if 14 < x < MAP_W - 14 and 18 < y < MAP_H - 32:
            o.append(label(x, y - 9, nid, C["purple"], anchor="middle"))
    return "".join(o)


def spec_path(d, col=SPEC, w=2.2, dash="7 4", extra=""):
    return (f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{w}" '
            f'stroke-dasharray="{dash}" stroke-linecap="round" '
            f'stroke-linejoin="round" {extra}/>')


def spec_poly(d, col=SPEC, fill=None, w=1.6, dash="5 3.5"):
    fill = fill or (col + "1f")
    return (f'<path d="{d}" fill="{fill}" stroke="{col}" stroke-width="{w}" '
            f'stroke-dasharray="{dash}" stroke-linejoin="round"/>')


def dot(x, y, col=SPEC, r=3.0):
    return (f'<circle cx="{f1(x)}" cy="{f1(y)}" r="{f1(r)}" fill="#fff" '
            f'stroke="{col}" stroke-width="1.7"/>')


def plate(zh, en):
    """图面底部说明条：与图上要素分层，避免压到街块与线位。"""
    h = 30.0
    return (f'<g><rect x="0" y="{f1(MAP_H-h)}" width="{f1(MAP_W)}" height="{f1(h)}" '
            f'fill="#fdfcf9" fill-opacity=".92"/>'
            f'<line x1="0" y1="{f1(MAP_H-h)}" x2="{f1(MAP_W)}" y2="{f1(MAP_H-h)}" '
            f'stroke="{C["edge"]}" stroke-width="1"/>'
            + label(8, MAP_H - h + 12, zh, C["deep"], halo=False)
            + label(8, MAP_H - h + 25, en, SPEC, weight=400, halo=False) + "</g>")


def chrome():
    """右上角图面器具：指北针与比例尺，垫白底避免与底图重叠。"""
    return (f'<g><rect x="{f1(MAP_W-112)}" y="2" width="110" height="34" '
            f'fill="#fdfcf9" fill-opacity=".92" stroke="{C["edge"]}" '
            f'stroke-width="1" rx="2"/>'
            + north_right(MAP_W - 24, 13)
            + scalebar(MAP_W - 104, 29, MPP, 200, "200 m") + "</g>")


# ------------------------------------------------------------------- 联 A
def panel_a():
    ring = RINGS["ZZY-BK-01"]
    clon, clat = ((min(c[0] for c in ring) + max(c[0] for c in ring)) / 2,
                  (min(c[1] for c in ring) + max(c[1] for c in ring)) / 2)
    fr = Frame(clon, clat)
    blk = fr.poly(ring)
    op1 = Point(*fr.m(*NODES["OP-01"]["geometry"]["coordinates"][:2]))

    ext = blk.exterior
    e_pt = ext.interpolate(ext.project(op1))                     # 东侧接主脊一端
    cand = [c for c in ext.coords if abs(c[1] - e_pt.y) < 260]
    w_pt = Point(min(cand, key=lambda c: c[0]))                  # 西侧接学清路一端
    ctr = blk.representative_point()
    route = LineString([(e_pt.x, e_pt.y), (ctr.x, ctr.y), (w_pt.x, w_pt.y)])

    vols = []
    for s in [d for d in range(70, int(route.length) - 60, 118)]:
        for off in (58, -58):
            r = rect_along(route, s, 44, off, 62)
            if blk.contains(r):
                vols.append(r)
    ents = [p for p in spaced(route, SPACING["zzy"], 12) if blk.contains(p)]
    quiet = route.offset_curve(-132).intersection(blk)
    if quiet.geom_type == "MultiLineString":
        quiet = max(quiet.geoms, key=lambda g: g.length)

    o = [basemap(fr),
         data_layer(fr, ["ROAD-001", "ROAD-002"], ["OP-01"], ["PUBLIC-004"],
                    key_id="zhongzhiyuan_ai_acceleration_area",
                    green_ids=("GREEN-002", "GREEN-001"))]
    o.append(f'<path d="{fr.d(blk)}" fill="{C["teal"]}12" stroke="{C["teal"]}" '
             f'stroke-width="1.8"/>')
    for v in vols:
        o.append(spec_poly(fr.d(v), fill=SPEC + "26"))
    if not quiet.is_empty:
        o.append(spec_path(fr.d(quiet), col=C["purple"], w=2.0, dash="2 4"))
    o.append(spec_path(fr.d(route), w=3.0, dash="9 5"))
    for p in ents:
        o.append(dot(*fr.px(p.x, p.y)))
    # 展示界面设想：受控测试庭一侧「可看见、不可自由进入」的边段
    if vols:
        v = vols[0]
        vc = list(v.exterior.coords)
        o.append(spec_path("M" + " L".join("%s %s" % tuple(f1(t) for t in fr.px(*c))
                                           for c in vc[:2]),
                           col=FRC["display_frontage"], w=4.0, dash="10 4"))
    ex, ey = fr.px(e_pt.x, e_pt.y)
    wx, wy = fr.px(w_pt.x, w_pt.y)
    o.append(label(ex + 7, ey + 15, "接 ROAD-001", SPEC))
    o.append(label(wx + 3, wy - 8, "接学清路 primary", SPEC))
    o.append(node_labels(fr, ["OP-01"]))
    o.append(label(8, 16, "ZZY-BK-01 · 264,409 m² · 贯通通道", C["teal"]))
    o.append(chrome())
    o.append(plate("设想入口间距 50.5 m · 街块中位等效边长（参考值）",
                   "Speculative spacing 50.5 m, median block side"))
    return "".join(o)


# ------------------------------------------------------------------- 联 B
def panel_b():
    ids = ["AIO-BK-01", "AIO-BK-02", "AIO-BK-03"]
    pts = [c for i in ids for c in RINGS[i]]
    clon, clat = ((min(c[0] for c in pts) + max(c[0] for c in pts)) / 2,
                  (min(c[1] for c in pts) + max(c[1] for c in pts)) / 2)
    fr = Frame(clon, clat)
    blocks = {i: fr.poly(RINGS[i]) for i in ids}
    r3 = fr.line(ROADS["ROAD-003"]["geometry"]["coordinates"])

    o = [basemap(fr),
         data_layer(fr, ["ROAD-003", "ROAD-005"], ["OP-02", "OP-06"],
                    ["PUBLIC-005", "PUBLIC-006"],
                    key_id="beijing_ai_origin_community",
                    green_ids=("GREEN-001", "GREEN-004", "GREEN-006"))]
    act = {"AIO-BK-01": ("through_route", C["teal"]),
           "AIO-BK-02": ("edge_permeation", C["gold"]),
           "AIO-BK-03": ("corner_opening", C["coral"])}
    for i in ids:
        col = act[i][1]
        o.append(f'<path d="{fr.d(blocks[i])}" fill="{col}12" stroke="{col}" '
                 f'stroke-width="1.6"/>')

    # BK-01 贯通通道设想：自最贴接口的一点穿越至对侧
    b1 = blocks["AIO-BK-01"]
    near = b1.exterior.interpolate(b1.exterior.project(r3.interpolate(r3.project(
        b1.representative_point()))))
    far = max(b1.exterior.coords, key=lambda c: (c[0] - near.x) ** 2 + (c[1] - near.y) ** 2)
    thr = LineString([(near.x, near.y), (far[0], far[1])]).intersection(b1)
    if thr.geom_type == "MultiLineString":
        thr = max(thr.geoms, key=lambda g: g.length)
    if not thr.is_empty:
        o.append(spec_path(fr.d(thr), w=2.8, dash="9 5"))
        for p in spaced(thr, SPACING["aio"], 10):
            o.append(dot(*fr.px(p.x, p.y), r=2.4))

    # BK-02 边界渗透设想：贴接口一侧边界上按 41.0 m 打出入口位
    b2 = blocks["AIO-BK-02"]
    edge = b2.exterior
    seg = [c for c in edge.coords if r3.distance(Point(c)) < 190]
    if len(seg) >= 2:
        el = LineString(seg)
        for t in ticks(el, SPACING["aio"], 26, side=1.0):
            o.append(spec_path(fr.d(t), col=C["gold"], w=2.0, dash="4 3"))
        for p in spaced(el, SPACING["aio"]):
            o.append(dot(*fr.px(p.x, p.y), col=C["gold"], r=2.6))

    # BK-03 角部开放设想：最贴接口的角部一个可退出停留点
    b3 = blocks["AIO-BK-03"]
    corner = min(b3.exterior.coords, key=lambda c: r3.distance(Point(c)))
    cr = Point(corner).buffer(52).intersection(b3)
    o.append(spec_poly(fr.d(cr), col=C["coral"], fill=C["coral"] + "2a"))

    # 共创院一街两院概念组合（挂 PUBLIC-005 与既有 design_role「独立生活共创院」）
    s0 = r3.project(Point(*fr.m(116.34745, 39.98955)))
    for off in (78, -78):
        y = rect_along(r3, s0, 58, off, 74)
        o.append(spec_poly(fr.d(y), fill=SPEC + "22"))
    cyx, cyy = fr.px(*list(rect_along(r3, s0, 58, 78, 74).centroid.coords)[0])
    o.append(label(cyx, cyy + 4, "共创院 · 一街两院", SPEC, anchor="middle"))

    # 服务点位设想：沿接口按 41.0 m
    for p in spaced(r3, SPACING["aio"], 20):
        x, y = fr.px(p.x, p.y)
        if 6 < x < MAP_W - 6 and 6 < y < MAP_H - 34:
            o.append(f'<rect x="{f1(x-2.6)}" y="{f1(y-2.6)}" width="5.2" '
                     f'height="5.2" fill="#fff" stroke="{SPEC}" stroke-width="1.5"/>')
    o.append(node_labels(fr, ["OP-02", "OP-06"]))
    o.append(label(8, 16, "ROAD-003 接口段 · 三块距接口均 0 m", C["sky"]))
    o.append(chrome())
    o.append(plate("设想服务点位间距 41.0 m · 街块中位等效边长（参考值）",
                   "Speculative spacing 41.0 m, median block side"))
    return "".join(o)


# ------------------------------------------------------------------- 联 C
def panel_c():
    pts = (PUBLIC["PUBLIC-007"]["geometry"]["coordinates"][0]
           + PUBLIC["PUBLIC-008"]["geometry"]["coordinates"][0]
           + RINGS["DZS-BK-01"])
    clon, clat = ((min(c[0] for c in pts) + max(c[0] for c in pts)) / 2,
                  (min(c[1] for c in pts) + max(c[1] for c in pts)) / 2)
    fr = Frame(clon, clat)
    o = [basemap(fr),
         data_layer(fr, ["ROAD-001", "ROAD-004", "ROAD-005"],
                    ["OP-04", "OP-08", "OP-09"], ["PUBLIC-007", "PUBLIC-008"],
                    key_id="dazhongsi_ai_industry_cluster",
                    green_ids=("GREEN-001", "GREEN-003", "GREEN-006"))]
    blk = fr.poly(RINGS["DZS-BK-01"])
    o.append(f'<path d="{fr.d(blk)}" fill="{C["gold"]}12" stroke="{C["gold"]}" '
             f'stroke-width="1.5"/>')

    p7 = fr.poly(PUBLIC["PUBLIC-007"]["geometry"]["coordinates"][0])
    r4 = fr.line(ROADS["ROAD-004"]["geometry"]["coordinates"])
    r5 = fr.line(ROADS["ROAD-005"]["geometry"]["coordinates"])
    r1 = fr.line(ROADS["ROAD-001"]["geometry"]["coordinates"])
    op4 = Point(*fr.m(*NODES["OP-04"]["geometry"]["coordinates"][:2]))

    # 触觉文化带设想：沿主脊连续通过本段，并分出一支接入百感台记录面
    tb = r1.intersection(p7.buffer(900).envelope)
    if tb.geom_type == "MultiLineString":
        tb = max(tb.geoms, key=lambda g: g.length)
    if not tb.is_empty:
        o.append(spec_path(fr.d(tb), col=C["deep"], w=2.6, dash="2 5"))
    p8c = fr.poly(PUBLIC["PUBLIC-008"]["geometry"]["coordinates"][0]).centroid
    o.append(spec_path(fr.d(LineString([(op4.x, op4.y), (p8c.x, p8c.y)])),
                       col=C["deep"], w=2.2, dash="2 5"))

    # 活性界面设想：市场沿 ROAD-004 的一段街面 + 31.1 m 入口位
    act = r4.intersection(p7.buffer(40))
    if act.geom_type == "MultiLineString":
        act = max(act.geoms, key=lambda g: g.length)
    if act.is_empty or act.length < 60:
        s4 = r4.project(op4)
        act = substring(r4, max(0, s4 - 170), min(r4.length, s4 + 170))
    o.append(spec_path(fr.d(act), col=FRC["active_frontage"], w=5.0, dash="12 5"))
    for p in spaced(act, SPACING["dzs"], 6):
        o.append(dot(*fr.px(p.x, p.y), col=FRC["active_frontage"], r=2.2))

    # 静界面设想：低刺激替代线一段
    qs = r5.intersection(Point(0, 0).buffer(900).envelope)
    if qs.geom_type == "MultiLineString":
        qs = max(qs.geoms, key=lambda g: g.length)
    if not qs.is_empty:
        o.append(spec_path(fr.d(qs), col=FRC["quiet_frontage"], w=5.0, dash="12 5"))

    # 服务桌四位序 SD-1 → SD-4，位序不可调换（位序为数据，落位为设想）
    sx, sy = op4.x + 78, op4.y - 78
    for i in range(4):
        cx, cy = sx, sy + i * 46
        x, y = fr.px(cx, cy)
        fillc = C["sky"] if i == 2 else SPEC
        o.append(f'<rect x="{f1(x-6.5)}" y="{f1(y-6.5)}" width="13" height="13" '
                 f'rx="2" fill="{fillc}" stroke="#fff" stroke-width="1.4"/>')
        o.append(label(x, y + 4.4, str(i + 1), "#fff", anchor="middle", halo=False))
        if i:
            x0, _ = fr.px(sx, sy + (i - 1) * 46)
            o.append(f'<path d="M {f1(x0+8)} {f1(y)} L {f1(x-9)} {f1(y)}" '
                     f'stroke="{SPEC}" stroke-width="1.4" fill="none" '
                     f'marker-end="url(#ah)"/>')
    lx, ly = fr.px(sx, sy + 69)
    o.append(label(lx, ly - 14, "服务桌 SD-1→SD-4 · 位序不可调换", SPEC,
                   anchor="middle"))

    # 「不消费也能停留」停留空间设想
    stay = Polygon([(sx + 34, sy - 26), (sx + 34, sy + 164),
                    (sx + 132, sy + 164), (sx + 132, sy - 26)])
    o.append(spec_poly(fr.d(stay), fill=SPEC + "1a"))
    stx, sty = fr.px(*list(stay.centroid.coords)[0])
    o.append(label(stx, sty + 4, "不消费也能停留", SPEC, anchor="middle"))

    o.append(node_labels(fr, ["OP-04", "OP-08", "OP-09"]))
    o.append(label(8, 16, "OP-04 段 · PUBLIC-007 多通道商业前厅", C["sky"]))
    o.append(chrome())
    o.append(plate("设想入口间距 31.1 m · 街块中位等效边长（参考值）",
                   "Speculative spacing 31.1 m, median block side"))
    return "".join(o)


DEFS = ('<defs><marker id="ah" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="5" '
        f'markerHeight="5" orient="auto"><path d="M0 0 L8 4 L0 8 Z" fill="{SPEC}"/>'
        '</marker></defs>')


def wrap_svg(inner):
    return (f'<svg viewBox="0 0 {f1(MAP_W)} {f1(MAP_H)}" width="{f1(MAP_W)}" '
            f'height="{f1(MAP_H)}" font-family="SHS">{DEFS}'
            f'<rect width="{f1(MAP_W)}" height="{f1(MAP_H)}" fill="#fdfcf9"/>'
            f'{inner}</svg>')


# ------------------------------------------------------------------ 图注文本
PANELS = [
    ("A", "众智园 · 通用接口实验院", "Zhongzhiyuan · Interface Lab", panel_a,
     "ZZY-BK-01 贯通通道段 + OP-01", "Through-route section at ZZY-BK-01",
     [("贯通通道线位", "Through-route alignment",
       "district-strategy #ZZY-BK-01 opening_action_type"),
      ("通道两侧概念体量", "Masses flanking the route",
       "buildings.geojson + 活性界面间距判据"),
      ("活性界面入口落位 50.5 m", "Active-frontage entrances",
       "frontage_rules active_frontage · 50.5 m"),
      ("安静支线绕行", "Quiet spur bypass",
       "frontage_rules quiet_frontage · BG-R1")]),
    ("B", "原点社区 · 独立生活共创院", "Origin Community", panel_b,
     "ROAD-003 接口段 + OP-02（三块距接口 0 m）",
     "Interface section with OP-02; three blocks 0 m away",
     [("三块开放化动作落位", "Where the three actions land",
       "district-strategy #AIO-BK-01/02/03 类型"),
      ("接口连续界面", "Continuous interface frontage",
       "AIO 候选 ranking_basis「接口成段」"),
      ("共创院一街两院", "Courtyards astride the street",
       "design_role 独立生活共创院 + PUBLIC-005"),
      ("服务点位落位 41.0 m", "Service points at 41.0 m",
       "frontage_rules active_frontage · 41.0 m")]),
    ("C", "大钟寺 · 包容采用市场", "Dazhongsi · Adoption Market", panel_c,
     "OP-04 段 + 万感服务桌 SD-1→SD-4",
     "OP-04 section with the service desk, SD-1 to SD-4",
     [("服务桌落位与四位序", "Desk position and station order",
       "seb-spec canonical_station_sequence"),
      ("「不消费也能停留」停留空间", "No-purchase dwelling area",
       "service-desk-gonogo · 不消费也能停留"),
      ("界面分类落位（活性／静）", "Frontage classes on the street",
       "frontage_rules classes applies 条款"),
      ("触觉文化带穿越市场", "Tactile band across the market",
       "heritage_interpretation HS-3 carriers")]),
]

SECTION_ZH = "取值引 OP-04 母版卡，非本图新给；本条比例与平面比例尺无关。"
SECTION_EN = "Quoted from the OP-04 master card; this bar carries its own scale."
RELATION_ZH = ("与既有图版的关系：片区策略图版承诺「只标类型，不画通道线位」；本图在概念"
               "声明下把同一批判据落成一次空间组合，两种口径并存、互不改写。")
RELATION_EN = ("The district-strategy sheet marks action types and draws no alignment; "
               "under the concept declaration this sheet lands the same criteria in "
               "space once.")


def section_bar():
    total = sum(b[2] for b in BANDS)
    px_per_m = 22.0
    o = [f'<svg viewBox="0 0 {f1(total*px_per_m+2)} 30" '
         f'width="{f1(total*px_per_m+2)}" height="30" font-family="SHS">']
    x = 1.0
    for zh, en, m, col in BANDS:
        w = m * px_per_m
        o.append(f'<rect x="{f1(x)}" y="10" width="{f1(w)}" height="12" fill="{col}" '
                 f'fill-opacity=".85" stroke="#fff" stroke-width="1"/>')
        o.append(f'<text x="{f1(x+w/2)}" y="8" font-size="12" font-weight="700" '
                 f'text-anchor="middle" fill="{col}">{m:.2f}</text>')
        x += w
    o.append("</svg>")
    return "".join(o)


LEGEND = [
    ("实线 · 数据派生", "data",
     f'background:{C["teal"]};height:3px;margin:4px 0'),
    ("虚线 · 概念设想", "speculation",
     f'background:repeating-linear-gradient(90deg,{SPEC} 0 6px,transparent 6px 10px);'
     f'height:3px;margin:4px 0'),
    ("主脊绿带", "GREEN-001..003",
     'background:#cbdcc6;border:1.1px solid #8fae8a'),
    ("街块 OSM 拓扑面", "block face",
     f'background:{C["teal"]}12;border:1.6px solid {C["teal"]}'),
    ("重点区范围", "key area",
     f'background:{C["coral"]}0d;border:1.4px dashed {C["coral"]}'),
    ("公共空间面", "public space",
     f'background:{C["sky"]}22;border:1.2px dashed {C["sky"]}'),
    ("完成节点", "node",
     f'background:{C["purple"]};border-radius:50%;width:11px'),
    ("设想建筑体量", "speculative mass",
     f'background:{SPEC}26;border:1.6px dashed {SPEC}'),
    ("设想入口／服务点位", "entrance / service",
     f'background:#fff;border:1.7px solid {SPEC};border-radius:50%;width:11px'),
    ("活性界面", "active",
     f'background:{FRC["active_frontage"]};height:5px;margin:3px 0'),
    ("展示界面", "display",
     f'background:{FRC["display_frontage"]};height:5px;margin:3px 0'),
    ("静界面", "quiet",
     f'background:{FRC["quiet_frontage"]};height:5px;margin:3px 0'),
    ("触觉文化带", "tactile band",
     f'background:repeating-linear-gradient(90deg,{C["deep"]} 0 2px,transparent 2px 7px);'
     f'height:3px;margin:4px 0'),
]


def build():
    cards = []
    for tag, zh, en, fn, sub_zh, sub_en, items in PANELS:
        rows = "".join(
            f'<div class="it"><span class="tg">设想</span>'
            f'<b>{esc(nz)}</b><em>{esc(ne)}</em>'
            f'<span class="src">判据 {esc(src)}</span></div>'
            for nz, ne, src in items)
        cards.append(
            f'<div class="cd"><div class="ch"><b>{tag} {esc(zh)}</b>'
            f'<em>{esc(en)}</em></div>{wrap_svg(fn())}'
            f'<div class="sub"><b>{esc(sub_zh)}</b><em>{esc(sub_en)}</em></div>'
            f'<div class="items">{rows}</div></div>')
    legend = "".join(f'<span class="lg"><i style="{sw}"></i><b>{esc(z)}</b>'
                     f'<em>{esc(e)}</em></span>' for z, e, sw in LEGEND)
    return f"""<!doctype html><html lang="zh"><head><meta charset="utf-8">
<title>district-concept-sections</title><style>__FONT__
{base_css()}
.cards{{display:flex;gap:{f1(GAP)}px;flex:none}}
.cd{{width:{f1(MAP_W)}px;display:flex;flex-direction:column}}
.ch{{height:19px;background:{C['deep']};color:#fff;display:flex;align-items:center;
gap:6px;padding:0 7px;font-size:12px;border-radius:2px 2px 0 0;white-space:nowrap;
overflow:hidden}}
.ch em{{color:{C['onDarkEn']};font-style:normal;font-weight:400}}
.cd svg{{display:block;border:1px solid {C['edge']};border-top:none}}
.sub{{margin-top:3px;font-size:12px;line-height:1.26;white-space:nowrap;overflow:hidden}}
.sub b{{color:{C['deep']};font-weight:700}}
.sub em{{display:block;color:{C['muted']};font-style:normal}}
.items{{margin-top:3px;border-top:1px solid {C['edge']};padding-top:3px}}
.it{{margin-bottom:1px;line-height:1.16;white-space:nowrap;overflow:hidden}}
.it .tg{{display:inline-block;background:{SPEC};color:#fff;font-size:12px;
font-weight:700;padding:0 5px;border-radius:2px;margin-right:5px}}
.it b{{font-weight:700;color:{C['ink']}}}
.it em{{color:{C['muted']};font-style:normal;margin-left:5px}}
.it .src{{display:block;color:{SPEC};margin-left:31px}}
.sec{{display:flex;align-items:center;gap:12px;margin-top:4px;flex:none;
border-top:1px solid {C['edge']};padding-top:4px}}
.sec .t{{font-size:12px;line-height:1.2;width:392px;flex:none}}
.sec .t b{{color:{C['deep']}}}
.sec .t em{{display:block;color:{C['muted']};font-style:normal}}
.sec .rel{{font-size:12px;line-height:1.2;flex:1;border-left:3px solid {SPEC};
padding-left:9px}}
.sec .rel b{{color:{SPEC};font-weight:700}}
.sec .rel em{{display:block;color:{C['muted']};font-style:normal}}
</style></head><body>
{head('DISTRICT CONCEPT DETAIL · THREE PANELS',
      '三片区概念详图：建筑—街道—公共空间—运营关系的一次空间组合',
      'District concept detail — one spatial composition of the building, street, '
      'public-space and operation relations across the three key areas',
      'CD-01 / CONCEPT')}
<div class="wrap">
  <div class="cards">{"".join(cards)}</div>
  <div class="lgr">{legend}</div>
  <div class="sec">{section_bar()}
    <div class="t"><b>通道断面四带 m：导路 2.50 · 触觉 0.30 · 设施 1.20 · 缓冲 1.50<br>
    {esc(SECTION_ZH)}</b>
    <em>Four passage bands. {esc(SECTION_EN)}</em></div>
    <div class="rel"><b>{esc(RELATION_ZH)}</b><em>{esc(RELATION_EN)}</em></div>
  </div>
  <div class="cap"><span><b>三联同取向</b> 北向右 · 三联共用比例尺 1 CSS px = {f1(MPP)} m
   · 窗口 {th(MAP_W*MPP)} × {th(MAP_H*MPP)} m · 街块轮廓为 OSM 拓扑闭合面，不代表产权边界</span>
   <span>one shared scale and orientation, {f1(MPP)} m per CSS px</span></div>
  <div class="ft">{esc(ATTR_ZH)}<br>{esc(ATTR_EN)}<br>
  <span class="r">{esc(CRS_ZH)}</span> · not a statutory plan ·
  底图只铺干道与轨道 basemap: arterials and rail only ·
  district-concept-sections.png</div>
</div>
</body></html>"""


if __name__ == "__main__":
    render(build(), "district-concept-sections",
           os.environ.get("W92_OUT", os.path.join(os.path.dirname(
               os.path.abspath(__file__)), "out")))
