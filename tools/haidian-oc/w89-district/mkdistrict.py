# -*- coding: utf-8 -*-
"""三区片区策略合幅三联图 district-strategy.png（语言中立单件，中英双语同图）。

全部数值、坐标、way 编号直读 visual/assets/district-strategy.json；候选街块轮廓由
FAB-03 的构面口径（可步行网络平面图 polygonize）就地复算，并以面积、周长、质心三项
逐候选校验与该文件登记值一致后才入图，不另编几何。
"""
from __future__ import annotations
from pathlib import Path as _HaidianPath

import json
import os
import subprocess
import sys

TC = str(_HaidianPath(__file__).resolve().parents[1])
sys.path.insert(0, os.path.join(TC, "w81-basemap"))
import osmbase          # noqa: E402
import suppfont         # noqa: E402

PKG = str(_HaidianPath(__file__).resolve().parents[3] / 'submissions/lqqk7/every-sense-jingzhang')
HERE = os.path.dirname(os.path.abspath(__file__))
RENDER = os.path.join(TC, "wp4b/render.js")

C = dict(deep="#10383d", teal="#177c78", coral="#d76450", purple="#6b5b95",
         gold="#d6a13b", sky="#4aa3c4", paper="#f2efe7", ink="#17383c",
         muted="#68787b", edge="#e2ddd0", onDarkEn="#9ecdc7")

W, H = 1200, 750
PAD = 30
DSF = "2.5"                      # 3000 x 1875
CARD_W, CARD_H = 370.0, 220.0
MPP = 6.2                        # 三幅共用比例尺：1 CSS px = 6.2 m
MLAT = 110540.0
import math                                                   # noqa: E402
MLON = 111320.0 * math.cos(math.radians(39.99))

ACT = {
    "through_route":  (C["teal"],  "贯通通道", "Through-route"),
    "edge_permeation": (C["gold"], "边界渗透", "Edge permeation"),
    "corner_opening": (C["coral"], "角部开放", "Corner opening"),
    "frontage_only":  (C["muted"], "阈值以下候选", "Below-threshold candidate"),
}

DS = json.load(open(os.path.join(PKG, "visual/assets/district-strategy.json"),
                    encoding="utf-8"))
RINGS = json.load(open(os.path.join(HERE, "cand_rings.json"), encoding="utf-8"))


def gj(name):
    with open(os.path.join(PKG, "geometry", name + ".geojson"), encoding="utf-8") as f:
        return json.load(f)["features"]


KEY = gj("key_areas")
ROADS = gj("roads")
NODES = gj("constraints")
CLUSTERS = DS["corridor_and_interchange"]["rail_access"]["clusters"]


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def f1(v):
    return ("%.1f" % v).rstrip("0").rstrip(".")


def th(v):
    return "{:,}".format(int(round(v)))


# ------------------------------------------------------------------ 投影
def proj(idx):
    """分幅窗口：图面旋转 90°、北向右，三幅同比例尺；窗口取「重点区 + 候选街块」的合并包络居中，
    使最大候选块不被裁掉。"""
    pts = list(KEY[idx]["geometry"]["coordinates"][0])
    for c in DS["districts"][idx]["opening_candidates"]:
        pts += RINGS[c["candidate_id"]]
    clon = (min(c[0] for c in pts) + max(c[0] for c in pts)) / 2
    clat = (min(c[1] for c in pts) + max(c[1] for c in pts)) / 2
    span_lat = CARD_W * MPP / MLAT
    span_lon = CARD_H * MPP / MLON

    def to_px(lon, lat):
        return ((lat - (clat - span_lat / 2)) / span_lat * CARD_W,
                (lon - (clon - span_lon / 2)) / span_lon * CARD_H)

    return to_px


def path_ring(ring, to_px):
    return ("M" + " L".join("%s %s" % tuple(f1(v) for v in to_px(c[0], c[1]))
                            for c in ring) + "Z")


def path_line(coords, to_px):
    return "M" + " L".join("%s %s" % tuple(f1(v) for v in to_px(c[0], c[1]))
                           for c in coords)


def inbox(x, y, m=8):
    return -m <= x <= CARD_W + m and -m <= y <= CARD_H + m


# ------------------------------------------------------------------ 记号
def badge(kind, x, y, r=7.5):
    """开放化动作类型记号：只标类型，不画任何通道线位。"""
    col = ACT[kind][0]
    g = [f'<circle cx="{f1(x)}" cy="{f1(y)}" r="{f1(r)}" fill="#fff" '
         f'stroke="{col}" stroke-width="1.8"/>']
    if kind == "through_route":
        g.append(f'<path d="M {f1(x-4.2)} {f1(y)} L {f1(x+4.2)} {f1(y)}" '
                 f'stroke="{col}" stroke-width="1.8"/>')
        for s in (-1, 1):
            g.append(f'<path d="M {f1(x+s*4.6)} {f1(y)} L {f1(x+s*1.9)} {f1(y-2.3)} '
                     f'L {f1(x+s*1.9)} {f1(y+2.3)} Z" fill="{col}"/>')
    elif kind == "edge_permeation":
        g.append(f'<path d="M {f1(x-4.4)} {f1(y-4.4)} L {f1(x-4.4)} {f1(y+4.4)}" '
                 f'stroke="{col}" stroke-width="1.8"/>')
        for dy in (-2.8, 0, 2.8):
            g.append(f'<path d="M {f1(x-3.4)} {f1(y+dy)} L {f1(x+3.6)} {f1(y+dy)}" '
                     f'stroke="{col}" stroke-width="1.3"/>')
    elif kind == "corner_opening":
        g.append(f'<path d="M {f1(x-4.4)} {f1(y+4.4)} L {f1(x-4.4)} {f1(y-4.4)} '
                 f'L {f1(x+4.4)} {f1(y-4.4)}" fill="none" stroke="{col}" '
                 f'stroke-width="1.8"/>')
        g.append(f'<path d="M {f1(x-4.4)} {f1(y+4.4)} L {f1(x+4.4)} {f1(y-4.4)}" '
                 f'stroke="{col}" stroke-width="1.3" stroke-dasharray="2 1.6"/>')
    else:
        g.append(f'<rect x="{f1(x-4.2)}" y="{f1(y-4.2)}" width="8.4" height="8.4" '
                 f'fill="none" stroke="{col}" stroke-width="1.5" '
                 f'stroke-dasharray="2.4 1.8"/>')
    return "".join(g)


def rail_mark(x, y):
    return (f'<g><circle cx="{f1(x)}" cy="{f1(y)}" r="6.4" fill="#fff" '
            f'stroke="{C["deep"]}" stroke-width="1.6"/>'
            f'<circle cx="{f1(x)}" cy="{f1(y)}" r="2.6" fill="{C["deep"]}"/></g>')


def op_mark(x, y):
    return (f'<circle cx="{f1(x)}" cy="{f1(y)}" r="4" fill="{C["purple"]}" '
            f'stroke="#fff" stroke-width="1.4"/>')


def lab(x, y, s, col=None, size=12, weight=700, anchor="middle", halo=True):
    col = col or C["ink"]
    t = (f'<text x="{f1(x)}" y="{f1(y)}" font-size="{size}" font-weight="{weight}" '
         f'text-anchor="{anchor}" fill="%s"%s>{esc(s)}</text>')
    out = ""
    if halo:
        out += t % ("#fdfcf9", ' stroke="#fdfcf9" stroke-width="3.2" '
                               'stroke-linejoin="round" paint-order="stroke"')
    out += t % (col, "")
    return out


def textw(s, size=12):
    """700 字重思源黑体下的注记宽度估算；系数按浏览器 getComputedTextLength 标定。"""
    w = 0.0
    for ch in s:
        o = ord(ch)
        if 0x2e80 <= o <= 0x9fff or 0x3000 <= o <= 0x303f or 0xff00 <= o <= 0xffef:
            w += 1.0
        elif ch.isdigit():
            w += 0.62
        elif "A" <= ch <= "Z":
            w += 0.68
        elif "a" <= ch <= "z":
            w += 0.60
        elif ch == " ":
            w += 0.30
        elif ch in "-.,·":
            w += 0.33
        else:
            w += 0.50
    return w * size * 1.04


class Placer:
    """图面注记的贪心避让：记号与已放注记的包围盒逐个回避，放不下时退到末位候选。"""

    def __init__(self):
        self.boxes = []

    def block(self, x, y, r):
        self.boxes.append((x - r, y - r, x + r, y + r))

    @staticmethod
    def _hit(a, b):
        return not (a[2] <= b[0] or b[2] <= a[0] or a[3] <= b[1] or b[3] <= a[1])

    def put(self, text, pts, offs, col, size=12, weight=700, ring=(), lead=0.0,
            must=False):
        """pts 为候选锚点，offs 为位移候选；ring 给出退让半径，放不下则不画。

        位移超过 lead 时补一条细引线，使注记与其记号仍然一一对应。
        """
        w, h = textw(text, size), size * 1.16
        cands = list(offs)
        for r in ring:
            for k in range(16):
                a = 2 * math.pi * k / 16
                dx, dy = r * math.cos(a), r * math.sin(a)
                anchor = "start" if dx > 4 else ("end" if dx < -4 else "middle")
                cands.append((dx + (6 if anchor == "start" else
                                    -6 if anchor == "end" else 0), dy + 4, anchor))
        for ax, ay in pts:
            for dx, dy, anchor in cands:
                x, y = ax + dx, ay + dy
                x0 = (x - w / 2 if anchor == "middle"
                      else (x if anchor == "start" else x - w))
                box = (x0 - 2.5, y - h, x0 + w + 2.5, y + 2.5)
                if (box[0] < 2 or box[2] > CARD_W - 2 or box[1] < 2
                        or box[3] > CARD_H - 14):
                    continue
                if any(self._hit(box, b) for b in self.boxes):
                    continue
                self.boxes.append(box)
                out = ""
                d = math.hypot(dx, dy)
                if lead and d > lead:
                    tx = (box[0] if dx > 4 else box[2] if dx < -4
                          else (box[0] + box[2]) / 2)
                    ty = (box[1] + box[3]) / 2
                    ux, uy = (tx - ax) / d, (ty - ay) / d
                    out = (f'<line x1="{f1(ax + ux * 9)}" y1="{f1(ay + uy * 9)}" '
                           f'x2="{f1(tx - ux * 2)}" y2="{f1(ty - uy * 2)}" '
                           f'stroke="{col}" stroke-width="0.8" opacity="0.75"/>')
                return out + lab(x, y, text, col, size, weight, anchor)
        if not must:
            return ""
        # 必标注记（候选街块）绝不静默丢弃：裁进版心就近落位，并补引线指回记号。
        ax, ay = pts[0]
        x0 = min(max(ax - w / 2, 3.0), CARD_W - 3.0 - w)
        y = min(max(ay + 22, h + 3), CARD_H - 16)
        box = (x0 - 2.5, y - h, x0 + w + 2.5, y + 2.5)
        self.boxes.append(box)
        tx, ty = (box[0] + box[2]) / 2, (box[1] + box[3]) / 2
        dd = math.hypot(tx - ax, ty - ay) or 1.0
        ux, uy = (tx - ax) / dd, (ty - ay) / dd
        out = (f'<line x1="{f1(ax + ux * 9)}" y1="{f1(ay + uy * 9)}" '
               f'x2="{f1(tx - ux * 2)}" y2="{f1(ty - uy * 2)}" '
               f'stroke="{col}" stroke-width="0.8" opacity="0.75"/>') if dd > 12 else ""
        return out + lab(x0, y, text, col, size, weight, "start")


DIRS = [(0, -1), (0, 1), (1, 0), (-1, 0), (0.71, -0.71), (-0.71, -0.71),
        (0.71, 0.71), (-0.71, 0.71), (0.38, -0.92), (-0.38, -0.92),
        (0.92, -0.38), (-0.92, -0.38), (0.92, 0.38), (-0.92, 0.38),
        (0.38, 0.92), (-0.38, 0.92)]


def _put_stack(pl, lines, ax, ay, col, size=12, weight=700):
    """候选街块的两行居中注记：整块就近落位，位移超过一档即补引线，绝不丢标。"""
    w = max(textw(l, size) for l in lines)
    lh = size * 1.16
    ht = len(lines) * lh

    def render(cx, cy, leader):
        o = leader
        for i, ln in enumerate(lines):
            o += lab(cx, cy - ht / 2 + size + i * lh, ln, col, size,
                     weight if i == 0 else 500, "middle")
        return o

    for r in (8.5 + ht / 2 + 4, 8.5 + ht / 2 + 14, 34, 46, 60, 76, 94, 116):
        for ux, uy in DIRS:
            cx, cy = ax + ux * r, ay + uy * r
            box = (cx - w / 2 - 2.5, cy - ht / 2, cx + w / 2 + 2.5, cy + ht / 2)
            if (box[0] < 2 or box[2] > CARD_W - 2 or box[1] < 2
                    or box[3] > CARD_H - 14):
                continue
            if any(pl._hit(box, b) for b in pl.boxes):
                continue
            pl.boxes.append(box)
            lead = ""
            if r > 8.5 + ht / 2 + 14:
                tx = cx - ux * (w / 2 + 2.5) if abs(ux) > 0.5 else cx
                ty = cy - uy * (ht / 2 + 1) if abs(uy) > 0.3 else cy
                lead = (f'<line x1="{f1(ax + ux * 9)}" y1="{f1(ay + uy * 9)}" '
                        f'x2="{f1(tx)}" y2="{f1(ty)}" stroke="{col}" '
                        f'stroke-width="0.8" opacity="0.75"/>')
            return render(cx, cy, lead)
    cx = min(max(ax, w / 2 + 4), CARD_W - w / 2 - 4)
    cy = min(max(ay + 8.5 + ht / 2 + 4, ht / 2 + 3), CARD_H - 14 - ht / 2)
    pl.boxes.append((cx - w / 2 - 2.5, cy - ht / 2, cx + w / 2 + 2.5, cy + ht / 2))
    return render(cx, cy, "")


OFF_BLOCK = [(0, -12, "middle"), (0, 22, "middle"), (13, 4, "start"),
             (-13, 4, "end"), (0, -24, "middle"), (0, 34, "middle"),
             (13, -10, "start"), (-13, -10, "end"), (13, 18, "start"),
             (-13, 18, "end")]
OFF_OP = [(0, -9, "middle"), (0, 17, "middle"), (7, 4, "start"), (-7, 4, "end"),
          (0, -21, "middle"), (0, 29, "middle"), (7, -8, "start"), (-7, -8, "end")]
OFF_ROAD = [(6, -6, "start"), (6, 15, "start"), (-6, -6, "end"), (-6, 15, "end")]
RING_B = (30, 40, 52, 66, 82, 100, 120)
RING_O = (24, 32, 42, 54, 68)


def scalebar(x, y, metres=500):
    w = metres / MPP
    return (f'<g><line x1="{f1(x)}" y1="{f1(y)}" x2="{f1(x+w)}" y2="{f1(y)}" '
            f'stroke="{C["deep"]}" stroke-width="2.2"/>'
            f'<line x1="{f1(x)}" y1="{f1(y-3.5)}" x2="{f1(x)}" y2="{f1(y+3.5)}" '
            f'stroke="{C["deep"]}" stroke-width="2"/>'
            f'<line x1="{f1(x+w)}" y1="{f1(y-3.5)}" x2="{f1(x+w)}" y2="{f1(y+3.5)}" '
            f'stroke="{C["deep"]}" stroke-width="2"/>'
            f'<text x="{f1(x+w+6)}" y="{f1(y+4)}" font-size="12" '
            f'fill="{C["deep"]}">{metres} m</text></g>')


def north_right(x, y):
    return (f'<g><text x="{f1(x-14)}" y="{f1(y+4)}" font-size="12" font-weight="700" '
            f'text-anchor="end" fill="{C["deep"]}">N</text>'
            f'<line x1="{f1(x-10)}" y1="{f1(y)}" x2="{f1(x+12)}" y2="{f1(y)}" '
            f'stroke="{C["deep"]}" stroke-width="2.2"/>'
            f'<path d="M {f1(x+20)} {f1(y)} L {f1(x+11)} {f1(y-4.5)} '
            f'L {f1(x+11)} {f1(y+4.5)} Z" fill="{C["deep"]}"/></g>')


ROAD_STYLE = {
    "ROAD-001": f'stroke="{C["teal"]}" stroke-width="2.6"',
    "ROAD-002": f'stroke="{C["sky"]}" stroke-width="2.2"',
    "ROAD-003": f'stroke="{C["sky"]}" stroke-width="2.2"',
    "ROAD-004": f'stroke="{C["sky"]}" stroke-width="2.2"',
    "ROAD-005": f'stroke="{C["purple"]}" stroke-width="2.4" stroke-dasharray="7 5"',
}

# 分幅 C 的界面分类色带：按 frontage_rules 的适用条款派生，不做逐段实测分配。
FRONT = {"active": C["coral"], "display": C["gold"], "quiet": C["purple"]}


def card_svg(idx):
    to_px = proj(idx)
    dist = DS["districts"][idx]
    o = [f'<svg viewBox="0 0 {f1(CARD_W)} {f1(CARD_H)}" width="{f1(CARD_W)}" '
         f'height="{f1(CARD_H)}" font-family="SHS">',
         f'<rect width="{f1(CARD_W)}" height="{f1(CARD_H)}" fill="#fdfcf9"/>',
         osmbase.basemap_svg(to_px, (0, 0, CARD_W, CARD_H),
                             layers=["path", "minor", "subway", "mid", "major", "rail"])]
    # 重点区临时多边形（只描边不填色，避免与候选街块的面色混读）
    o.append(f'<path d="{path_ring(KEY[idx]["geometry"]["coordinates"][0], to_px)}" '
             f'fill="none" stroke="{C["coral"]}" '
             f'stroke-width="1.6" stroke-dasharray="7 4"/>')
    # 分幅 C：界面分类色带（先铺于中心线之下）
    if idx == 2:
        for f in ROADS:
            rid = f["properties"]["id"]
            if rid not in ("ROAD-004", "ROAD-005"):
                continue
            col = FRONT["active"] if rid == "ROAD-004" else FRONT["quiet"]
            o.append(f'<path d="{path_line(f["geometry"]["coordinates"], to_px)}" '
                     f'fill="none" stroke="{col}" stroke-width="9" stroke-opacity="0.3" '
                     f'stroke-linecap="round"/>')
    # 提交中心线
    for f in ROADS:
        rid = f["properties"]["id"]
        o.append(f'<path d="{path_line(f["geometry"]["coordinates"], to_px)}" '
                 f'fill="none" {ROAD_STYLE[rid]} stroke-linecap="round"/>')
    # 候选街块
    sub = idx == 2
    cands = []
    for c in dist["opening_candidates"]:
        cid = c["candidate_id"]
        kind = c["opening_action_type"] if not sub else "frontage_only"
        col = ACT[kind][0]
        o.append(f'<path d="{path_ring(RINGS[cid], to_px)}" fill="{col}" '
                 f'fill-opacity="{0.16 if sub else 0.2}" stroke="{col}" '
                 f'stroke-width="{2.0 if sub else 2.2}"'
                 + (' stroke-dasharray="5 3"' if sub else "") + '/>')
        x, y = to_px(*c["centroid_wgs84"])
        cands.append((x, y, [cid.split("-", 1)[1], th(c["block_area_m2"]) + " m²"],
                      kind))
    pl = Placer()
    marks = []
    # 轨道接入点簇（本区相关者）
    for cl in CLUSTERS:
        if cl["key_area"] != dist["area_id"]:
            continue
        x, y = to_px(*cl["centroid_wgs84"])
        if inbox(x, y):
            marks.append(rail_mark(x, y))
            pl.block(x, y, 7)
    # 独立完成节点
    ops = []
    for f in NODES:
        x, y = to_px(*f["geometry"]["coordinates"])
        if not inbox(x, y, 2):
            continue
        marks.append(op_mark(x, y))
        pl.block(x, y, 4.5)
        ops.append((x, y, f["properties"]["id"]))
    for x, y, _t, _k in cands:
        pl.block(x, y, 10.0)
    o += marks
    # 候选记号与标注（最上层）
    texts = []
    for x, y, t, kind in cands:
        o.append(badge(kind, x, y))
        texts.append(_put_stack(pl, t, x, y, C["ink"]))
    for x, y, t in ops:
        texts.append(pl.put(t, [(x, y)], OFF_OP, C["purple"], 12, 700,
                            RING_O, 20))
    # 中心线名号：沿窗口内可见段自左向右取多个候选锚点
    for f in ROADS:
        rid = f["properties"]["id"]
        pts = [to_px(c[0], c[1]) for c in f["geometry"]["coordinates"]]
        dense = []
        for a, b in zip(pts, pts[1:]):
            seg = math.hypot(b[0] - a[0], b[1] - a[1])
            n = max(1, int(seg // 18))
            for k in range(n):
                t0 = k / n
                dense.append((a[0] + (b[0] - a[0]) * t0, a[1] + (b[1] - a[1]) * t0))
        dense.append(pts[-1])
        vis = sorted((p for p in dense if inbox(p[0], p[1], -10)), key=lambda q: q[0])
        if len(vis) < 2:
            continue
        col = C["teal"] if rid == "ROAD-001" else (C["purple"] if rid == "ROAD-005"
                                                   else C["sky"])
        texts.append(pl.put(rid, vis, OFF_ROAD, col, 12, 700))
    o += texts
    o.append(scalebar(12, CARD_H - 10))
    o.append(north_right(CARD_W - 32, 15))
    o.append("</svg>")
    return "".join(o)


# ------------------------------------------------------------------ 图注文本
CAP = [
    # 分幅 A 众智园
    ("132 街块 · 中位 2,547.8 m² · 超大块 9 个占 60.05%",
     "132 blocks · median 2,547.8 m² · 9 oversized = 60.05%",
     "四个候选分属三种动作类型；只标类型，不画通道线位。",
     "Four candidates, three action types; no alignment drawn.",
     "OP-01 距 BK-01 24.4 m；两处接入簇均在区内",
     "OP-01 24.4 m from BK-01; both rail clusters inside"),
    # 分幅 B 原点社区
    ("151 街块 · 中位 1,677.7 m² · 超大块 7 个占 42.52%",
     "151 blocks · median 1,677.7 m² · 7 oversized = 42.52%",
     "三块到 ROAD-003 均为 0 m：接口能否成段由这三块决定。",
     "All three lie 0 m from ROAD-003: they decide its continuity.",
     "OP-02 距 BK-03 1.9 m；最近接入簇距本区 685.2 m",
     "OP-02 1.9 m from BK-03; nearest rail cluster 685.2 m off"),
    # 分幅 C 大钟寺
    ("84 街块 · 中位 969.0 m² · 超过 40,000 m² 的街块为零",
     "84 blocks · median 969.0 m² · zero blocks above 40,000 m²",
     "没有超大街块，开放化不适用；画面转为界面分类。",
     "No oversized block; opening does not apply; frontage instead.",
     "ROAD-004 活性判据（间距参考 31.1 m）· ROAD-005 静界面",
     "ROAD-004 active frontage (spacing 31.1 m); ROAD-005 quiet"),
]

CARD_TITLE = [("A 众智园 AI 加速区", "A — Zhongzhiyuan · Interface Lab"),
              ("B 北京 AI 原点社区", "B — Origin Community · Co-design Lab"),
              ("C 大钟寺 AI 集聚区", "C — Dazhongsi · Adoption Market")]

GRAIN = [("众智园 Zhongzhiyuan", 50.5), ("原点社区 Origin Community", 41.0),
         ("大钟寺 Dazhongsi", 31.1)]
GRAIN_PPM = 1.0 / 1.35          # 图例小方块比例尺：1 CSS px ≈ 1.35 m

NOTE1_ZH = "快照口径派生，参考值非法定值。"
NOTE1_EN = ("Derived at snapshot caliber; a reference value is not a statutory value.")
NOTE2_ZH = "街块轮廓为 OSM 拓扑闭合面，不代表产权边界或围墙。"
NOTE2_EN = ("Block outlines are closed faces in OpenStreetMap topology; they do not "
            "represent tenure boundaries or walls.")
NOTE3_ZH = ("重点区范围为临时多边形（official_boundary=false）；界面分类按 frontage_rules "
            "的适用条款派生，不是逐段实测分配。")
NOTE3_EN = ("Key-area extents are provisional polygons (official_boundary=false); "
            "frontage classes are derived from the applicability clauses of "
            "frontage_rules, not assigned by measurement.")

ATTR_ZH = ("底图数据 © OpenStreetMap 贡献者，ODbL 1.0；快照 osm-fabric-snapshot-20260815"
           "（该快照仅含 highway / railway 要素，故底图只有路网与轨道，无建筑与水系）")
ATTR_EN = ("Basemap data © OpenStreetMap contributors, ODbL 1.0; snapshot "
           "osm-fabric-snapshot-20260815 (highway / railway elements only: the basemap "
           "carries roads and rail, no buildings or water)")
CRS_ZH = "坐标 EPSG:4326 · 复算 EPSG:4548 · 三幅同比例尺、同取向（北向右）· 非法定规划图"
CRS_EN = ("Coordinates EPSG:4326, recomputed in EPSG:4548 · one shared scale and "
          "orientation · not a statutory plan")


def legend_html():
    rows = ['<span class="lgh">开放化动作（分幅 A/B）<em>Opening action, panels A/B</em></span>']
    for kind in ("through_route", "edge_permeation", "corner_opening"):
        col, zh, en = ACT[kind]
        rows.append(f'<span class="lg"><svg width="19" height="19" viewBox="0 0 19 19">'
                    f'{badge(kind, 9.5, 9.5, 7.4)}</svg>'
                    f'<b>{esc(zh)}</b><em>{esc(en)}</em></span>')
    col = ACT["frontage_only"][0]
    rows.append(f'<span class="lg"><i style="background:{col}1a;border:1.5px dashed '
                f'{col};width:20px;height:13px"></i><b>阈值以下候选</b>'
                f'<em>Below-threshold candidate</em></span>')
    rows.append(f'<span class="lg"><i style="background:{C["coral"]}0d;border:1.6px '
                f'dashed {C["coral"]};width:20px;height:13px"></i><b>重点区粗略范围</b>'
                f'<em>Key area (approximate)</em></span>')
    rows.append(f'<span class="lg"><i style="background:{C["purple"]};border-radius:50%;'
                f'width:11px;height:11px;box-shadow:0 0 0 1.2px #fff inset"></i>'
                f'<b>独立完成节点</b><em>Completion node</em></span>')
    rows.append(f'<span class="lg"><svg width="15" height="15" viewBox="0 0 15 15">'
                f'{rail_mark(7.5, 7.5)}</svg><b>轨道接入点簇</b>'
                f'<em>Rail access cluster</em></span>')
    return "".join(rows)


def road_legend_html():
    rows = [f'<span class="lg"><i style="background:{C["teal"]};height:3px;width:22px">'
            f'</i><b>ROAD-001 主脊</b><em>spine</em></span>',
            f'<span class="lg"><i style="background:{C["sky"]};height:3px;width:22px">'
            f'</i><b>ROAD-002/003/004 横向接口</b><em>lateral interfaces</em></span>',
            f'<span class="lg"><i style="background:repeating-linear-gradient(90deg,'
            f'{C["purple"]} 0 7px,transparent 7px 12px);height:3px;width:22px"></i>'
            f'<b>ROAD-005 安静替代线</b><em>quiet alternative</em></span>']
    rows.append('<span class="lgh">界面分类（分幅 C）<em>Frontage classes, panel C</em>'
                '</span>')
    for key, zh, en in (("active", "活性界面", "Active"), ("display", "展示界面", "Display"),
                        ("quiet", "静界面", "Quiet")):
        rows.append(f'<span class="lg"><i style="background:{FRONT[key]};opacity:.42;'
                    f'height:9px;width:20px;border-radius:4px"></i><b>{esc(zh)}</b>'
                    f'<em>{esc(en)}</em></span>')
    return "".join(rows)


def grain_html():
    cells = []
    for name, m in GRAIN:
        s = m * GRAIN_PPM
        cells.append(f'<span class="gr"><i style="width:{f1(s)}px;height:{f1(s)}px"></i>'
                     f'<span><u>{m} m</u> <em>{esc(name)}</em></span></span>')
    return "".join(cells)


def sheet_html():
    cards = "".join(
        f'<div class="cd"><div class="ch"><b>{esc(CARD_TITLE[i][0])}</b>'
        f'<em>{esc(CARD_TITLE[i][1])}</em></div>{card_svg(i)}'
        f'<div class="cc"><p class="zh">{esc(CAP[i][0])}</p>'
        f'<p class="en">{esc(CAP[i][1])}</p>'
        f'<p class="zh k">{esc(CAP[i][2])}</p><p class="en">{esc(CAP[i][3])}</p>'
        f'<p class="zh">{esc(CAP[i][4])}</p><p class="en">{esc(CAP[i][5])}</p></div></div>'
        for i in range(3))
    return f"""<!doctype html><html lang="zh"><head><meta charset="utf-8">
<title>district-strategy</title><style>__FONT__
*{{box-sizing:border-box}}html,body{{margin:0;padding:0}}
body{{width:{W}px;height:{H}px;overflow:hidden;background:{C['paper']};
color:{C['ink']};font-family:SHS;-webkit-font-smoothing:antialiased;
text-rendering:geometricPrecision}}
.hd{{height:84px;background:{C['deep']};color:#fff;padding:11px {PAD}px 0;
display:flex;justify-content:space-between;align-items:flex-start}}
.hd .k{{font-size:12px;letter-spacing:.16em;color:{C['onDarkEn']};font-weight:700}}
.hd h1{{font-size:23px;font-weight:700;margin:6px 0 0;line-height:1.2}}
.hd h2{{font-size:13px;font-weight:400;margin:3px 0 0;color:{C['onDarkEn']};
line-height:1.2}}
.hd .r{{text-align:right}}
.hd .r .i{{font-size:12px;letter-spacing:.14em;font-weight:700}}
.pill{{display:inline-block;margin-top:8px;background:{C['coral']};color:#fff;
font-size:12px;padding:4px 11px;border-radius:11px;font-weight:700}}
.wrap{{padding:8px {PAD}px 0;height:{H-84}px;display:flex;flex-direction:column}}
.cards{{display:flex;gap:15px;flex:none}}
.cd{{width:{f1(CARD_W)}px;border:1px solid {C['edge']};border-radius:3px;
overflow:hidden;background:#fff}}
.ch{{height:21px;background:{C['deep']};color:#fff;display:flex;align-items:center;
gap:7px;padding:0 8px;font-size:12px;white-space:nowrap}}
.ch b{{flex:none}}.ch em{{color:{C['onDarkEn']};font-style:normal;overflow:hidden;
text-overflow:ellipsis}}
.cc{{padding:5px 8px 7px;border-top:1px solid {C['edge']}}}
.cc p{{margin:0;font-size:12px;line-height:1.33}}
.cc .zh{{color:{C['ink']};font-weight:700}}
.cc .en{{color:{C['muted']};margin-bottom:3px}}
.cc .k{{color:{C['coral']}}}
.bar{{margin-top:8px;border-top:1px solid {C['edge']};padding-top:6px;flex:none}}
.lgr{{display:flex;flex-wrap:wrap;gap:5px 15px;align-items:center}}
.lgr+.lgr{{margin-top:5px}}
.lg{{display:flex;align-items:center;gap:6px;font-size:12px;line-height:1}}
.lg i,.lg svg{{display:block;flex:none}}
.lg b{{color:{C['ink']};font-weight:700}}
.lg em{{color:{C['muted']};font-style:normal}}
.lgh{{font-size:12px;line-height:1;font-weight:700;color:{C['deep']};
border-left:3px solid {C['deep']};padding-left:6px}}
.lgh em{{color:{C['muted']};font-style:normal;font-weight:400;margin-left:5px}}
.grw{{display:flex;align-items:flex-end;gap:18px;margin-top:7px}}
.grt{{font-size:12px;line-height:1.33;max-width:400px}}
.grt b{{color:{C['ink']}}}.grt em{{color:{C['muted']};font-style:normal;display:block}}
.gr{{display:flex;flex-direction:column;align-items:center;gap:3px;font-size:12px;
line-height:1.33;white-space:nowrap}}
.gr i{{display:block;background:{C['teal']}1f;border:1.4px solid {C['teal']}}}
.gr u{{text-decoration:none;font-weight:700;color:{C['teal']}}}
.gr em{{font-style:normal;color:{C['muted']}}}
.note{{margin-top:7px;border-top:1px solid {C['edge']};padding-top:5px;flex:none}}
.note p{{margin:0;font-size:12px;line-height:1.33}}
.note .zh{{color:{C['ink']};font-weight:700}}
.note .en{{color:{C['muted']};margin-bottom:2px}}
.ft{{margin-top:auto;padding:5px 0 6px;border-top:1px solid {C['edge']};
font-size:12px;color:{C['muted']};line-height:1.3;flex:none}}
.ft .r{{color:{C['deep']};font-weight:700}}
</style></head><body>
<div class="hd">
  <div><div class="k">EVERY SENSE JING-ZHANG · DISTRICT STRATEGY PLATE</div>
  <h1>片区策略：三区街块诊断与开放化候选（快照口径）</h1>
  <h2>District strategy — block diagnosis and opening candidates across the three key
  areas, at snapshot caliber · one bilingual sheet</h2></div>
  <div class="r"><div class="i">D-01 / DISTRICT STRATEGY</div>
  <div class="pill">参考图 · NOT A STATUTORY PLAN</div></div>
</div>
<div class="wrap">
  <div class="cards">{cards}</div>
  <div class="bar">
    <div class="lgr">{legend_html()}</div>
    <div class="lgr">{road_legend_html()}</div>
    <div class="grw">
      <div class="grt"><b>入口间距参考标尺（同比例）：各区街块中位规模的等效方形边长</b>
      <em>Entrance-spacing reference scale, drawn at one shared scale: the equivalent
      square side of each area's median block size</em></div>
      {grain_html()}
    </div>
  </div>
  <div class="note">
    <p class="zh">{esc(NOTE1_ZH)} {esc(NOTE2_ZH)}</p>
    <p class="en">{esc(NOTE1_EN)} {esc(NOTE2_EN)}</p>
    <p class="zh">{esc(NOTE3_ZH)}</p>
    <p class="en">{esc(NOTE3_EN)}</p>
  </div>
  <div class="ft">{esc(ATTR_ZH)}<br>{esc(ATTR_EN)}<br>
  <span class="r">{esc(CRS_ZH)}</span> · {esc(CRS_EN)}</div>
</div>
</body></html>"""


def main():
    html = sheet_html()
    face = suppfont.full_face_css(html.replace("__FONT__", ""))
    p = os.path.join(HERE, "district-strategy.html")
    with open(p, "w", encoding="utf-8") as f:
        f.write(html.replace("__FONT__", face))
    out = os.path.join(HERE, "district-strategy.raw.png")
    r = subprocess.run(["node", RENDER, "png", p, out, str(W), str(H), DSF],
                       capture_output=True, text=True)
    if r.returncode:
        raise SystemExit(r.stderr)
    print("ok", os.path.getsize(out) // 1024, "KB raw")


if __name__ == "__main__":
    main()
