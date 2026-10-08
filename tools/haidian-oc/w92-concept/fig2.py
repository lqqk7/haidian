# -*- coding: utf-8 -*-
"""assets/figures/transport-system-concept.png —— 交通系统概念图（走廊全域分层）。

数据派生层（实线）：轨道接入点簇六处及其到最近中心线的垂足与距离（复算值与
district-strategy 登记值逐条一致）、五条中心线、主脊唯一连续共存段（自南端
150—1700 m）、快照内既有 cycleway 45 条 21.1 km。
概念设想层（虚线）：骑行走向与节点停放点、换乘步行接驳、保障车时段分离关系。

图上不出现任何车道数、断面、路权划分、停放规模与钟点值——这些一律为交通与运营
专业在官方断面与真实班次条件下的核定事项。
"""
from __future__ import annotations

import math
import os

from pyproj import Transformer

from common import (ATTR_EN, ATTR_ZH, C, CRS_ZH, DS, GREEN, KEYA, NODES, PAD,
                    PKG, PUBLIC, ROADS, W, H, MLAT, MLON, base_css, esc, f1,
                    head, label, north_right, osmbase, render, scalebar, th)

BAND_W, BAND_H = 1140.0, 212.0
SPEC = C["spec"]
FWD = Transformer.from_crs("EPSG:4326", "EPSG:4548", always_xy=True).transform

CORR = DS["corridor_and_interchange"]
CLUSTERS = CORR["rail_access"]["clusters"]
LINES = {x["road_id"]: x for x in CORR["segmentation"]["lines"]}
FREIGHT = CORR["freight_and_support"]

SHORT = {"ROAD-001": "通用可达底线", "ROAD-005": "低刺激安静替代线",
         "ROAD-002": "众智园横向接口", "ROAD-003": "原点社区横向接口",
         "ROAD-004": "大钟寺横向接口"}

ABC = [("A", "公交优先候选段", "Bus-priority candidate", C["coral"]),
       ("B", "慢行专用候选段", "Slow-mobility-exclusive", C["teal"]),
       ("C", "共存段", "Shared", C["gold"])]

SITE = [f for f in __import__("json").load(
    open(os.path.join(PKG, "geometry/site_boundary.geojson"), encoding="utf-8")
)["features"]][0]["geometry"]["coordinates"][0]
LAT0, LAT1 = min(c[1] for c in SITE), max(c[1] for c in SITE)
LON0, LON1 = min(c[0] for c in SITE), max(c[0] for c in SITE)
S = (BAND_W - 26) / ((LAT1 - LAT0) * MLAT)          # px per metre
MPP = 1 / S
YOFF = (BAND_H - (LON1 - LON0) * MLON * S) / 2


def to_px(lon, lat):
    return (13 + (lat - LAT0) * MLAT * S, YOFF + (lon - LON0) * MLON * S)


def dpath(coords, close=False):
    d = "M" + " L".join("%s %s" % tuple(f1(v) for v in to_px(c[0], c[1]))
                        for c in coords)
    return d + ("Z" if close else "")


# ------------------------------------------------------------ 数据：接入点簇
def nearest_on(road_id, lon, lat):
    """接入点簇到最近中心线的垂足与距离（EPSG:4548 复算）。"""
    cs = ROADS[road_id]["geometry"]["coordinates"]
    m = [FWD(a, b) for a, b in cs]
    p = FWD(lon, lat)
    best = (1e18, None)
    for i in range(len(m) - 1):
        ax, ay = m[i]
        bx, by = m[i + 1]
        dx, dy = bx - ax, by - ay
        L2 = dx * dx + dy * dy
        t = 0.0 if L2 == 0 else max(0.0, min(1.0, ((p[0] - ax) * dx + (p[1] - ay) * dy) / L2))
        q = (ax + t * dx, ay + t * dy)
        d = math.dist(p, q)
        if d < best[0]:
            ll = (cs[i][0] + t * (cs[i + 1][0] - cs[i][0]),
                  cs[i][1] + t * (cs[i + 1][1] - cs[i][1]))
            best = (d, ll)
    return best


def spine_shared_segment():
    """主脊唯一连续共存段：自南端链距 150—1700 m（既有读数，逐点复算落位）。"""
    cs = ROADS["ROAD-001"]["geometry"]["coordinates"]
    m = [FWD(a, b) for a, b in cs]
    ch = [0.0]
    for i in range(len(m) - 1):
        ch.append(ch[-1] + math.dist(m[i], m[i + 1]))

    def at(d):
        for i in range(len(ch) - 1):
            if ch[i] <= d <= ch[i + 1]:
                t = (d - ch[i]) / (ch[i + 1] - ch[i] or 1)
                return (cs[i][0] + t * (cs[i + 1][0] - cs[i][0]),
                        cs[i][1] + t * (cs[i + 1][1] - cs[i][1]))
        return cs[-1]

    out, d = [at(150.0)], 150.0
    while d < 1700.0:
        d = min(1700.0, d + 60.0)
        out.append(at(d))
    return out, ch[-1]


def cycleways():
    _meta, ways, _n = osmbase.load_snapshot()
    out, tot = [], 0.0
    for w in ways:
        if w[1] != "cycleway":
            continue
        out.append(w[5])
        m = [FWD(a, b) for a, b in w[5]]
        tot += sum(math.dist(m[i], m[i + 1]) for i in range(len(m) - 1))
    return out, tot


CW, CW_LEN = cycleways()
SHARED, SPINE_LEN = spine_shared_segment()


# ------------------------------------------------------------------ 图带
def offset_line(coords, metres):
    """沿线法向整体平移后回投经纬度：骑行走向设想的可辨表达，非线位主张。"""
    from shapely.geometry import LineString
    m = LineString([((c[0] - LON0) * MLON, (c[1] - LAT0) * MLAT)
                    for c in coords]).simplify(25)
    g = m.offset_curve(metres)
    if g.geom_type == "MultiLineString":
        g = max(g.geoms, key=lambda x: x.length)
    return [(LON0 + x / MLON, LAT0 + y / MLAT) for x, y in g.coords]


def band():
    o = [f'<rect width="{f1(BAND_W)}" height="{f1(BAND_H)}" fill="#fdfcf9"/>',
         osmbase.basemap_svg(to_px, (0, 0, BAND_W, BAND_H),
                             layers=["major", "rail"])]
    # 数据：快照内既有骑行专用要素
    for cs in CW:
        o.append(f'<path d="{dpath(cs)}" fill="none" stroke="{C["sky"]}" '
                 f'stroke-width="1.6" opacity=".85" stroke-linecap="round"/>')
    o.append(f'<path d="{dpath(SITE, True)}" fill="none" stroke="{C["deep"]}" '
             f'stroke-width="1.1" stroke-dasharray="5 3.5" opacity=".7"/>')
    for f in KEYA.values():
        o.append(f'<path d="{dpath(f["geometry"]["coordinates"][0], True)}" '
                 f'fill="{C["coral"]}0d" stroke="{C["coral"]}" stroke-width="1.4" '
                 f'stroke-dasharray="7 4"/>')
    # 概念设想：骑行走向（主脊侧向偏移一条，三处横向接口各一条）
    for rid, off in (("ROAD-001", 62), ("ROAD-002", 46), ("ROAD-003", 46),
                     ("ROAD-004", 46)):
        cs = offset_line(ROADS[rid]["geometry"]["coordinates"], off)
        o.append(f'<path d="{dpath(cs)}" fill="none" stroke="{SPEC}" '
                 f'stroke-width="2.2" stroke-dasharray="8 5" '
                 f'stroke-linecap="round"/>')
    # 数据：五条中心线
    for rid in ("ROAD-002", "ROAD-003", "ROAD-004", "ROAD-005", "ROAD-001"):
        st = (f'stroke="{C["teal"]}" stroke-width="3"' if rid == "ROAD-001" else
              f'stroke="{C["purple"]}" stroke-width="2.4" stroke-dasharray="7 5"'
              if rid == "ROAD-005" else f'stroke="{C["sky"]}" stroke-width="2.4"')
        o.append(f'<path d="{dpath(ROADS[rid]["geometry"]["coordinates"])}" '
                 f'fill="none" {st} stroke-linecap="round"/>')
    # 数据：主脊唯一连续共存段
    o.append(f'<path d="{dpath(SHARED)}" fill="none" stroke="{C["gold"]}" '
             f'stroke-width="7" opacity=".9" stroke-linecap="round"/>')
    sx, sy = to_px(*SHARED[len(SHARED) // 2])
    o.append(label(sx, sy - 24, "主脊唯一连续共存段 150—1700 m（自南端）", C["gold"],
                   anchor="middle"))
    o.append(label(sx, sy - 11, "the spine's only continuous shared stretch",
                   C["muted"], weight=400, anchor="middle"))
    # 概念设想：换乘步行接驳（接入点簇 → 最近的独立完成节点）
    for cl in CLUSTERS:
        lon, lat = cl["centroid_wgs84"]
        p = FWD(lon, lat)
        nid, best = None, 1e18
        for k, f in NODES.items():
            q = FWD(*f["geometry"]["coordinates"][:2])
            d = math.dist(p, q)
            if d < best:
                nid, best = k, d
        if best > 1200:
            continue
        x, y = to_px(lon, lat)
        nx, ny = to_px(*NODES[nid]["geometry"]["coordinates"][:2])
        o.append(f'<path d="M {f1(x)} {f1(y)} L {f1(nx)} {f1(ny)}" fill="none" '
                 f'stroke="{SPEC}" stroke-width="1.6" stroke-dasharray="3 3"/>')
    # 数据：接入点簇 + 垂足连线 + 复算距离
    for i, cl in enumerate(CLUSTERS):
        lon, lat = cl["centroid_wgs84"]
        rid = cl["nearest_centreline"]["road_id"]
        reg = cl["nearest_centreline"]["distance_m"]
        d, foot = nearest_on(rid, lon, lat)
        x, y = to_px(lon, lat)
        fx, fy = to_px(*foot)
        o.append(f'<path d="M {f1(x)} {f1(y)} L {f1(fx)} {f1(fy)}" fill="none" '
                 f'stroke="{C["deep"]}" stroke-width="1.3"/>')
        o.append(f'<circle cx="{f1(x)}" cy="{f1(y)}" r="5.4" fill="#fff" '
                 f'stroke="{C["deep"]}" stroke-width="2"/>'
                 f'<circle cx="{f1(x)}" cy="{f1(y)}" r="2.1" fill="{C["deep"]}"/>')
        up = -11 if i % 2 == 0 else 18
        anc = "start" if x < 110 else ("end" if x > BAND_W - 110 else "middle")
        ox = 8 if anc == "start" else (-8 if anc == "end" else 0)
        o.append(label(x + ox, y + up, "%s %s m" % (rid, f1(reg)), C["deep"],
                       anchor=anc))
    # 数据：十节点；设想：节点停放点
    for nid, f in NODES.items():
        lon, lat = f["geometry"]["coordinates"][:2]
        x, y = to_px(lon, lat)
        o.append(f'<rect x="{f1(x+5)}" y="{f1(y-4)}" width="8" height="8" rx="1.5" '
                 f'fill="none" stroke="{SPEC}" stroke-width="1.6" '
                 f'stroke-dasharray="3 2"/>')
        o.append(f'<circle cx="{f1(x)}" cy="{f1(y)}" r="4.2" fill="{C["purple"]}" '
                 f'stroke="#fff" stroke-width="1.4"/>')
    o.append(scalebar(14, BAND_H - 12, MPP, 1000, "1 km"))
    o.append(north_right(BAND_W - 30, 16))
    return ("".join(o))


def band_svg():
    return (f'<svg viewBox="0 0 {f1(BAND_W)} {f1(BAND_H)}" width="{f1(BAND_W)}" '
            f'height="{f1(BAND_H)}" font-family="SHS">{band()}</svg>')


# ------------------------------------------------------------------ 下栏三列
def abc_bar(rid, width=176.0):
    L = LINES[rid]
    o = [f'<svg viewBox="0 0 {f1(width)} 13" width="{f1(width)}" height="13" '
         f'font-family="SHS">']
    x = 0.0
    for k, _zh, _en, col in ABC:
        pct = L["%s_pct" % k]
        w = width * pct / 100.0
        if w > 0:
            o.append(f'<rect x="{f1(x)}" y="1" width="{f1(w)}" height="11" '
                     f'fill="{col}" fill-opacity=".9"/>')
            if w > 22:
                o.append(f'<text x="{f1(x+w/2)}" y="10" font-size="12" '
                         f'font-weight="700" text-anchor="middle" fill="#fff">'
                         f'{pct}</text>')
        x += w
    o.append("</svg>")
    return "".join(o)


def col_lines():
    rows = []
    for rid in ("ROAD-001", "ROAD-005", "ROAD-002", "ROAD-003", "ROAD-004"):
        L = LINES[rid]
        rows.append(f'<div class="lr"><span class="rid">{esc(rid)}</span>'
                    f'<span class="rn">{esc(SHORT[rid])}</span>'
                    f'<span class="rl">{th(L["length_m"])} m</span>'
                    f'{abc_bar(rid)}</div>')
    return "".join(rows)


def col_rail():
    rows = []
    for cl in CLUSTERS:
        kinds = "／".join({"station": "站体", "platform": "站台"}[k]
                          for k in cl["kinds"])
        nm = cl.get("name_zh", "未具名") if cl["named_in_snapshot"] else "未具名"
        rows.append(f'<div class="rr"><b>{esc(nm)}</b>'
                    f'<span class="k">{esc(kinds)}</span>'
                    f'<span class="d">距重点区 {f1(cl["distance_to_key_area_m"])} m</span>'
                    f'<span class="c">{esc(cl["nearest_centreline"]["road_id"])} '
                    f'{f1(cl["nearest_centreline"]["distance_m"])} m</span></div>')
    return "".join(rows)


TIME = [("常态行人时段", "Normal pedestrian hours", C["teal"]),
        ("补给时段（取 C 类共存段）", "Resupply, on class-C stretches", C["gold"]),
        ("夜间断点读数取样时段", "Night-break reading window", C["deep"])]


def time_bar():
    o = ['<svg viewBox="0 0 330 34" width="330" height="34" font-family="SHS">']
    xs = [(0, 150), (152, 96), (250, 80)]
    for (x, w), (zh, en, col) in zip(xs, TIME):
        o.append(f'<rect x="{x}" y="2" width="{w}" height="12" fill="{col}" '
                 f'fill-opacity=".88" rx="2"/>')
    o.append(f'<text x="0" y="27" font-size="12" font-weight="700" '
             f'fill="{C["muted"]}">时段互斥关系为判据；钟点值未登记，本图不给时刻</text>')
    o.append("</svg>")
    return "".join(o)


LEGEND_DATA = [
    ("五条提交中心线", "five submitted centrelines",
     f'background:{C["teal"]};height:3px;margin:4px 0'),
    ("低刺激安静替代线", "quiet alternative",
     f'background:repeating-linear-gradient(90deg,{C["purple"]} 0 7px,'
     f'transparent 7px 12px);height:3px;margin:4px 0'),
    ("主脊唯一连续共存段", "only continuous shared stretch",
     f'background:{C["gold"]};height:6px;margin:2px 0'),
    ("轨道接入点簇 + 垂足", "rail access cluster + foot",
     f'background:#fff;border:2px solid {C["deep"]};border-radius:50%;width:11px'),
    ("快照既有骑行要素", "existing cycleway in snapshot",
     f'background:{C["sky"]};height:2px;margin:4px 0'),
    ("独立完成节点", "completion node",
     f'background:{C["purple"]};border-radius:50%;width:11px'),
]
LEGEND_SPEC = [
    ("换乘步行接驳设想", "speculative walking link",
     f'background:repeating-linear-gradient(90deg,{SPEC} 0 3px,transparent 3px 6px);'
     f'height:3px;margin:4px 0'),
    ("骑行走向设想", "speculative cycling alignment",
     f'background:repeating-linear-gradient(90deg,{SPEC} 0 8px,transparent 8px 13px);'
     f'height:3px;margin:4px 0'),
    ("节点停放点设想", "speculative parking at nodes",
     f'background:transparent;border:1.6px dashed {SPEC};width:11px'),
]

FOOT_ZH = ("本图不提出车道数、断面、路权划分、停放规模、班次与任何钟点值；接入点簇按坐标"
           "与距离登记，快照中仅西直门一处带名称标签，其余十处不指认站名。")
FOOT_EN = ("No lane count, cross-section, right-of-way split, parking capacity or "
           "clock value is proposed here; clusters are registered by coordinate and "
           "distance, and only Xizhimen carries a name in the snapshot.")


def build():
    lg = "".join(f'<span class="lg"><i style="{sw}"></i><b>{esc(z)}</b>'
                 f'<em>{esc(e)}</em></span>' for z, e, sw in LEGEND_DATA)
    lgs = "".join(f'<span class="lg"><i style="{sw}"></i><b>{esc(z)}</b>'
                  f'<em>{esc(e)}</em></span>' for z, e, sw in LEGEND_SPEC)
    crit = "".join(f'<div class="cr">{esc(x)}</div>'
                   for x in FREIGHT["route_criteria_zh"])
    return f"""<!doctype html><html lang="zh"><head><meta charset="utf-8">
<title>transport-system-concept</title><style>__FONT__
{base_css()}
.band{{width:{f1(BAND_W)}px;height:{f1(BAND_H)}px;border:1px solid {C['edge']};
border-radius:3px;overflow:hidden;flex:none}}
.lgr .tt{{font-size:12px;font-weight:700;color:{C['deep']};letter-spacing:.06em}}
.lgr .tt.s{{color:{SPEC}}}
.cols{{display:flex;gap:14px;margin-top:6px;flex:none}}
.cx{{border:1px solid {C['edge']};border-radius:3px;background:{C['plate']};
padding:4px 8px 5px}}
.cx h3{{margin:0 0 3px;font-size:13px;font-weight:700;color:{C['deep']};
line-height:1.2;white-space:nowrap;overflow:hidden}}
.cx h3 em{{font-style:normal;font-weight:400;color:{C['muted']};font-size:12px;
margin-left:5px}}
.lr{{display:flex;align-items:center;gap:6px;margin-bottom:2px;white-space:nowrap}}
.rid{{font-weight:700;color:{C['deep']};width:64px;flex:none}}
.rn{{color:{C['muted']};width:112px;flex:none;overflow:hidden}}
.rl{{color:{C['ink']};font-weight:700;width:56px;flex:none;text-align:right}}
.rr{{display:flex;gap:6px;margin-bottom:1px;white-space:nowrap;line-height:1.28}}
.rr b{{width:44px;flex:none;color:{C['deep']}}}
.rr .k{{width:54px;flex:none;color:{C['muted']}}}
.rr .d{{width:104px;flex:none;color:{C['ink']}}}
.rr .c{{color:{C['teal']};font-weight:700}}
.cr{{color:{C['ink']};line-height:1.22;margin-bottom:2px;padding-left:9px;
position:relative}}
.cr:before{{content:"·";position:absolute;left:2px;color:{SPEC};font-weight:700}}
.note{{margin-top:3px;border-top:1px dashed {C['edge']};padding-top:3px;
color:{C['muted']};line-height:1.22}}
.bn{{margin-top:4px;font-size:12px;line-height:1.24;color:{C['ink']};
font-weight:700;flex:none}}
.bn span{{display:block;color:{C['muted']};font-weight:400}}
</style></head><body>
{head('TRANSPORT SYSTEM · CONCEPT SHEET',
      '交通系统概念图：轨道接入、走廊分段、骑行与保障车时段分离',
      'Transport system concept — rail access, corridor segmentation, cycling and '
      'the time separation of support vehicles',
      'CT-02 / CONCEPT')}
<div class="wrap">
  <div class="band">{band_svg()}</div>
  <div class="cap"><span><b>CORRIDOR BAND</b> 走廊全域 · 图面旋转 90°，北向右 ·
   1 CSS px ≈ {f1(MPP)} m · 主脊全长 {th(SPINE_LEN)} m（登记值 9,426 m）</span>
   <span>north to the right, {f1(MPP)} m per CSS px</span></div>
  <div class="lgr"><span class="tt">数据 DATA</span>{lg}
   <span class="tt s">设想 SPEC</span>{lgs}</div>
  <div class="cols">
    <div class="cx" style="width:398px">
      <h3>五线三类判据分段占比<em>A / B / C shares on the five lines</em></h3>
      {col_lines()}
      <div class="note">阈值 60 m／30 m／120 m 为本包方法选择，非规范值；改阈值即改全部占比。<br>
      Thresholds are a method choice, not code values.</div>
    </div>
    <div class="cx" style="width:352px">
      <h3>轨道接入点簇（11 簇中已登记 6 处）<em>rail access clusters</em></h3>
      {col_rail()}
      <div class="note">距离为 EPSG:4548 复算值，与 district-strategy 登记值逐条一致。<br>
      Distances recomputed in EPSG:4548 and identical to the registered values.</div>
    </div>
    <div class="cx" style="width:352px">
      <h3>货运与保障车：时段分离<em>freight by time separation</em></h3>
      {time_bar()}
      {crit}
      <div class="note">保障车不设专用路权；响应关系直接挂既有维护 SLA 四级阶梯，不新设时限。</div>
    </div>
  </div>
  <div class="bn">{esc(FOOT_ZH)}<br><span>{esc(FOOT_EN)}</span></div>
  <div class="ft">{esc(ATTR_ZH)}<br>{esc(ATTR_EN)}<br>
  <span class="r">{esc(CRS_ZH)}</span> · 底图只铺干道与轨道 basemap: arterials and rail only · transport-system-concept.png</div>
</div>
</body></html>"""


if __name__ == "__main__":
    render(build(), "transport-system-concept",
           os.environ.get("W92_OUT", os.path.join(os.path.dirname(
               os.path.abspath(__file__)), "out")))
