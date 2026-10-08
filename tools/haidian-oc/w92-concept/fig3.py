# -*- coding: utf-8 -*-
"""assets/figures/bluegreen-system-concept.png —— 蓝绿系统概念图（走廊全域分层）。

数据派生层（实线）：六块绿地（主脊绿带三段 GREEN-001/002/003、低刺激缓冲三段
GREEN-004/005/006）、十节点的 DR-A／DR-B／DR-C 归类、以硬质面为主的公共空间面、
五条中心线与三处重点区范围。
概念设想层（虚线）：汇水概念分区、遮荫连续段与间断风险位、热环境对比、夜间照明
分级，以及一处已识别的设计张力——低刺激暗区与夜间独行安全。

图上不出现滞留容积、渗透系数、溢流标高、管径与照度的任何数值；包内无高程与水文
资料，汇水分区为概念分区，不是水文计算结果。
"""
from __future__ import annotations

import json
import math
import os

from pyproj import Transformer

from common import (ATTR_EN, ATTR_ZH, C, CRS_ZH, DS, GREEN, KEYA, NODES, PAD,
                    PKG, PUBLIC, ROADS, SDC, MLAT, MLON, base_css, esc, f1,
                    head, label, north_right, osmbase, render, scalebar, th)

BAND_W, BAND_H = 1140.0, 212.0
SPEC = C["spec"]
FWD = Transformer.from_crs("EPSG:4326", "EPSG:4548", always_xy=True).transform

BG = SDC["bluegreen_stormwater"]
LAYERS3 = {x["layer_id"]: x for x in BG["three_layers"]}
RELS = {x["relation_id"]: x for x in BG["layer_relations"]}
TYPES = {x["type_id"]: x for x in BG["node_drainage_types"]["types"]}
ASSIGN = {a["node_id"]: a["drainage_type"] for a in BG["node_drainage_types"]["assignment"]}
DRC = {"DR-A": C["teal"], "DR-B": C["coral"], "DR-C": C["purple"]}

FR = {c["class_id"]: c for c in DS["frontage_rules"]["classes"]}

SITE = json.load(open(os.path.join(PKG, "geometry/site_boundary.geojson"),
                      encoding="utf-8"))["features"][0]["geometry"]["coordinates"][0]
LAT0, LAT1 = min(c[1] for c in SITE), max(c[1] for c in SITE)
LON0, LON1 = min(c[0] for c in SITE), max(c[0] for c in SITE)
S = (BAND_W - 26) / ((LAT1 - LAT0) * MLAT)
MPP = 1 / S
YOFF = (BAND_H - (LON1 - LON0) * MLON * S) / 2


def to_px(lon, lat):
    return (13 + (lat - LAT0) * MLAT * S, YOFF + (lon - LON0) * MLON * S)


def dpath(coords, close=False):
    d = "M" + " L".join("%s %s" % tuple(f1(v) for v in to_px(c[0], c[1]))
                        for c in coords)
    return d + ("Z" if close else "")


# --------------------------------------------------------- 汇水概念分区（设想）
def key_lat_range(area_id):
    ring = KEYA[area_id]["geometry"]["coordinates"][0]
    return min(c[1] for c in ring), max(c[1] for c in ring)


DZS = key_lat_range("dazhongsi_ai_industry_cluster")
AIO = key_lat_range("beijing_ai_origin_community")
ZZY = key_lat_range("zhongzhiyuan_ai_acceleration_area")
CUT1 = (DZS[1] + AIO[0]) / 2
CUT2 = (AIO[1] + ZZY[0]) / 2
ZONES = [(LAT0, CUT1, "大钟寺片区汇水概念区", "Dazhongsi", "#e6efe6"),
         (CUT1, CUT2, "原点社区片区汇水概念区", "Origin Community", "#eef1e6"),
         (CUT2, LAT1, "众智园片区汇水概念区", "Zhongzhiyuan", "#e6edf1")]

# 遮荫间断风险位（设想）：主脊与三处横向接口的交叉处，以及硬质前厅面所在段
SHADE_BREAK_ROADS = ("ROAD-002", "ROAD-003", "ROAD-004")
HARD_FACES = ("PUBLIC-002", "PUBLIC-003", "PUBLIC-005", "PUBLIC-006",
              "PUBLIC-007", "PUBLIC-008")


def crossings():
    from shapely.geometry import LineString
    r1 = LineString(ROADS["ROAD-001"]["geometry"]["coordinates"])
    out = []
    for rid in SHADE_BREAK_ROADS:
        g = r1.intersection(LineString(ROADS[rid]["geometry"]["coordinates"]))
        if g.is_empty:
            continue
        pts = [g] if g.geom_type == "Point" else list(getattr(g, "geoms", []))
        for p in pts:
            if p.geom_type == "Point":
                out.append((rid, (p.x, p.y)))
    return out


CROSS = crossings()


def band():
    o = [f'<rect width="{f1(BAND_W)}" height="{f1(BAND_H)}" fill="#fdfcf9"/>']
    # 设想：汇水概念分区（沿纬度切分，图面上为竖向带；不含高程与水文计算）
    for a, b, zh, en, col in ZONES:
        x0 = to_px(LON0, max(a, LAT0))[0]
        x1 = to_px(LON0, min(b, LAT1))[0]
        o.append(f'<rect x="{f1(x0)}" y="0" width="{f1(x1-x0)}" '
                 f'height="{f1(BAND_H)}" fill="{col}" fill-opacity=".85"/>')
        o.append(f'<line x1="{f1(x1)}" y1="0" x2="{f1(x1)}" y2="{f1(BAND_H)}" '
                 f'stroke="{SPEC}" stroke-width="1.6" stroke-dasharray="6 5"/>')
        o.append(label((x0 + x1) / 2, 15, zh, SPEC, anchor="middle"))
        o.append(label((x0 + x1) / 2, 27, en, C["muted"], weight=400,
                       anchor="middle"))
    o.append(osmbase.basemap_svg(to_px, (0, 0, BAND_W, BAND_H),
                                 layers=["major", "rail"]))
    # 数据：硬质为主的公共空间面（热环境对比的硬质一侧）
    for pid in HARD_FACES:
        o.append(f'<path d="{dpath(PUBLIC[pid]["geometry"]["coordinates"][0], True)}" '
                 f'fill="{C["coral"]}22" stroke="{C["coral"]}" stroke-width="1.1" '
                 f'stroke-dasharray="3 2.2"/>')
    # 数据：六块绿地
    for gid, g in GREEN.items():
        spine = g["properties"].get("green_type") == "spine_greenway"
        fill = "#bcd4b4" if spine else "#cfe0d6"
        o.append(f'<path d="{dpath(g["geometry"]["coordinates"][0], True)}" '
                 f'fill="{fill}" fill-opacity=".9" stroke="#7f9f79" '
                 f'stroke-width="1.1"/>')
    # 设想：夜间照明分级 —— 主脊沿线照明保障带 / 替代线低刺激暗区
    o.append(f'<path d="{dpath(ROADS["ROAD-001"]["geometry"]["coordinates"])}" '
             f'fill="none" stroke="{C["gold"]}" stroke-width="11" opacity=".28" '
             f'stroke-linecap="round"/>')
    o.append(f'<path d="{dpath(ROADS["ROAD-005"]["geometry"]["coordinates"])}" '
             f'fill="none" stroke="{C["deep"]}" stroke-width="11" opacity=".22" '
             f'stroke-linecap="round"/>')
    # 数据：中心线
    for rid in ("ROAD-002", "ROAD-003", "ROAD-004", "ROAD-005", "ROAD-001"):
        st = (f'stroke="{C["teal"]}" stroke-width="2.8"' if rid == "ROAD-001" else
              f'stroke="{C["purple"]}" stroke-width="2.2" stroke-dasharray="7 5"'
              if rid == "ROAD-005" else f'stroke="{C["sky"]}" stroke-width="2"')
        o.append(f'<path d="{dpath(ROADS[rid]["geometry"]["coordinates"])}" '
                 f'fill="none" {st} stroke-linecap="round"/>')
    # 设想：遮荫间断风险位（主脊 × 横向接口交叉处）
    for rid, (lon, lat) in CROSS:
        x, y = to_px(lon, lat)
        o.append(f'<circle cx="{f1(x)}" cy="{f1(y)}" r="6.5" fill="none" '
                 f'stroke="{SPEC}" stroke-width="2" stroke-dasharray="3 2.4"/>')
        o.append(f'<line x1="{f1(x-4.6)}" y1="{f1(y-4.6)}" x2="{f1(x+4.6)}" '
                 f'y2="{f1(y+4.6)}" stroke="{SPEC}" stroke-width="1.6"/>')
    # 数据：十节点按 DR 三类着色
    for nid, f in NODES.items():
        lon, lat = f["geometry"]["coordinates"][:2]
        x, y = to_px(lon, lat)
        col = DRC[ASSIGN[nid]]
        o.append(f'<circle cx="{f1(x)}" cy="{f1(y)}" r="5" fill="{col}" '
                 f'stroke="#fff" stroke-width="1.5"/>')
        o.append(label(x, y - 9, nid, col, anchor="middle"))
    o.append(scalebar(14, BAND_H - 12, MPP, 1000, "1 km"))
    o.append(north_right(BAND_W - 30, BAND_H - 16))
    return "".join(o)


def band_svg():
    return (f'<svg viewBox="0 0 {f1(BAND_W)} {f1(BAND_H)}" width="{f1(BAND_W)}" '
            f'height="{f1(BAND_H)}" font-family="SHS">{band()}</svg>')


# ------------------------------------------------------------------ 下栏三列
LAYER_ROLE = {
    "BG-L1": ("主脊绿带", "GREEN-001/002/003 · ROAD-001"),
    "BG-L2": ("低刺激缓冲与停留面", "GREEN-004/005/006 · ROAD-005"),
    "BG-L3": ("清河与小月河", "概念性联系，不表示蓝线"),
}
REL_TEXT = {
    "BG-R1": "低刺激替代线的缓冲不得由主脊绿带代偿，任一段被压缩该段即判不成立。",
    "BG-R2": "雨水去向以就地滞留为先、市政衔接为后；蓝线与防洪核验前不提出直接排放。",
    "BG-R3": "只登记概念性联系：不提滨水贯通线位、不标蓝线、不推断廊道宽度。",
}


def col_layers():
    o = []
    for lid in ("BG-L1", "BG-L2", "BG-L3"):
        zh, sub = LAYER_ROLE[lid]
        o.append(f'<div class="lyr"><span class="id">{esc(lid)}</span>'
                 f'<b>{esc(zh)}</b><em>{esc(sub)}</em></div>')
    for rid in ("BG-R1", "BG-R2", "BG-R3"):
        o.append(f'<div class="rel"><span class="rid">{esc(rid)}</span>'
                 f'{esc(REL_TEXT[rid])}</div>')
    return "".join(o)


def col_dr():
    o = []
    SHORTNAME = {"DR-A": "透水自渗 + 相邻滞留带承接",
                 "DR-B": "线性排水 + 市政衔接",
                 "DR-C": "生物滞留与市政并置，缓坡面不受纳"}
    for tid in ("DR-A", "DR-B", "DR-C"):
        ids = [n for n, t in ASSIGN.items() if t == tid]
        o.append(f'<div class="dr"><span class="id" style="background:{DRC[tid]}">'
                 f'{esc(tid)}</span><b>{esc(SHORTNAME[tid])}</b></div>'
                 f'<div class="ns" style="color:{DRC[tid]}">'
                 f'{esc(" · ".join(ids))}</div>')
    return "".join(o)


LIGHT = [("照明保障区", "Lit-assured", C["gold"], "主脊与十节点沿线"),
         ("过渡段", "Transition", C["muted"], "交接段，读数分段登记"),
         ("低刺激暗区", "Low-stimulus dark", C["deep"], "静界面段，不设动态发光")]

TENSION_ZH = ("已识别设计张力：静界面「不设动态发光」与夜间断点读数「照明不足即计断点」"
              "在同一段上互相拉扯——暗区越纯粹，夜间独行者的断点风险越高。")
TENSION_EN = ("Identified tension: the quiet-frontage clause forbidding dynamic "
              "illumination and the night-break reading that counts insufficient "
              "lighting as a break pull against each other on the same stretch.")

BN_ZH = ("处置判据（均为既有条款，本图不新设）：夜间断点读数在静界面段单独取样、不与主脊"
         "样本合并；静界面仍须有人工可及入口，该款即自然监视的既有表述——张力由现场读数"
         "判定，不由本图判定。图上不出现滞留容积、渗透系数、溢流标高、管径与照度数值；"
         "包内无高程与水文资料，汇水分区为概念分区，遮荫连续性与热环境对比为设想。")
BN_EN = ("Disposal criteria, both already registered: night-break readings are sampled "
         "separately on quiet frontage, never pooled with the spine, and quiet frontage "
         "still carries human-reachable entrances, the existing wording of natural "
         "surveillance; the field readings settle the tension, not this sheet. No "
         "retention volume, infiltration coefficient, overflow level, pipe size or "
         "illuminance appears here, and with no terrain or hydrological data in the "
         "package the catchment division is conceptual.")

LEGEND_DATA = [
    ("主脊绿带", "GREEN-001/002/003",
     'background:#bcd4b4;border:1.1px solid #7f9f79'),
    ("低刺激缓冲", "GREEN-004/005/006",
     'background:#cfe0d6;border:1.1px solid #7f9f79'),
    ("硬质公共空间面", "hard-surfaced face",
     f'background:{C["coral"]}22;border:1.1px dashed {C["coral"]}'),
    ("节点按 DR 三类着色", "drainage type",
     f'background:linear-gradient(90deg,{DRC["DR-A"]} 33%,{DRC["DR-B"]} 33% 66%,'
     f'{DRC["DR-C"]} 66%);border-radius:6px'),
]
LEGEND_SPEC = [
    ("汇水概念分区界", "catchment division",
     f'background:repeating-linear-gradient(90deg,{SPEC} 0 6px,transparent 6px 11px);'
     f'height:3px;margin:4px 0'),
    ("遮荫间断风险位", "shading-break risk",
     f'background:transparent;border:1.8px dashed {SPEC};border-radius:50%;width:11px'),
    ("照明保障带", "lit-assured",
     f'background:{C["gold"]};opacity:.45;height:8px;margin:1px 0'),
    ("低刺激暗区带", "dark band",
     f'background:{C["deep"]};opacity:.35;height:8px;margin:1px 0'),
]

FOOT_ZH = ("图上不出现滞留容积、渗透系数、溢流标高、管径与照度的任何数值；包内无高程与"
           "水文资料，汇水分区按「就地滞留为先」（BG-R2）以三区各自成区划分，是概念分区，"
           "不是水文计算结果。遮荫连续性与热环境对比为设想，未经实测。")
FOOT_EN = ("No retention volume, infiltration coefficient, overflow level, pipe size or "
           "illuminance value appears here. The package holds no terrain or hydrological "
           "data: the catchment division follows the registered retention-first rule "
           "(BG-R2), one zone per key area, and is conceptual rather than computed. "
           "Shading continuity and the thermal contrast are speculation, unmeasured.")


def build():
    lg = "".join(f'<span class="lg"><i style="{sw}"></i><b>{esc(z)}</b>'
                 f'<em>{esc(e)}</em></span>' for z, e, sw in LEGEND_DATA)
    lgs = "".join(f'<span class="lg"><i style="{sw}"></i><b>{esc(z)}</b>'
                  f'<em>{esc(e)}</em></span>' for z, e, sw in LEGEND_SPEC)
    lights = "".join(
        f'<div class="li"><i style="background:{col}"></i><b>{esc(zh)}</b>'
        f'<em>{esc(en)}</em><span>{esc(note)}</span></div>'
        for zh, en, col, note in LIGHT)
    return f"""<!doctype html><html lang="zh"><head><meta charset="utf-8">
<title>bluegreen-system-concept</title><style>__FONT__
{base_css()}
.band{{width:{f1(BAND_W)}px;height:{f1(BAND_H)}px;border:1px solid {C['edge']};
border-radius:3px;overflow:hidden;flex:none}}
.lgr .tt{{font-size:12px;font-weight:700;color:{C['deep']};letter-spacing:.06em}}
.lgr .tt.s{{color:{SPEC}}}
.cols{{display:flex;gap:12px;margin-top:6px;flex:none}}
.cx{{border:1px solid {C['edge']};border-radius:3px;background:{C['plate']};
padding:4px 8px 5px}}
.cx h3{{margin:0 0 3px;font-size:13px;font-weight:700;color:{C['deep']};
line-height:1.2;white-space:nowrap;overflow:hidden}}
.cx h3 em{{font-style:normal;font-weight:400;color:{C['muted']};font-size:12px;
margin-left:5px}}
.lyr{{display:flex;align-items:baseline;gap:6px;margin-bottom:1px;white-space:nowrap;
overflow:hidden}}
.lyr .id,.dr .id{{color:#fff;background:{C['deep']};font-weight:700;font-size:12px;
padding:1px 6px;border-radius:2px;flex:none}}
.lyr b{{color:{C['ink']};font-weight:700}}
.lyr em{{color:{C['muted']};font-style:normal}}
.rel{{line-height:1.2;margin-top:2px;color:{C['ink']};padding-left:2px}}
.rel .rid{{color:{SPEC};font-weight:700;margin-right:5px}}
.dr{{display:flex;align-items:baseline;gap:6px;margin-bottom:2px;white-space:nowrap;
overflow:hidden}}
.dr b{{font-weight:700;color:{C['ink']}}}
.ns{{font-weight:700;margin:0 0 2px 34px;line-height:1.2}}
.li{{display:flex;align-items:baseline;gap:6px;line-height:1.22;white-space:nowrap;
overflow:hidden;margin-bottom:1px}}
.li i{{display:block;width:16px;height:9px;flex:none;opacity:.75}}
.li b{{color:{C['ink']};font-weight:700;flex:none}}
.li em{{color:{C['muted']};font-style:normal;flex:none}}
.li span{{color:{C['muted']}}}
.ten{{margin-top:3px;border-left:3px solid {SPEC};padding-left:8px;line-height:1.2}}
.ten b{{color:{SPEC};font-weight:700}}
.ten em{{display:block;color:{C['muted']};font-style:normal;margin-top:1px}}
.bn{{margin-top:4px;font-size:12px;line-height:1.24;color:{C['ink']};
font-weight:700;flex:none}}
.bn span{{display:block;color:{C['muted']};font-weight:400}}
</style></head><body>
{head('BLUE-GREEN SYSTEM · CONCEPT SHEET',
      '蓝绿系统概念图：汇水概念分区、排水类型、遮荫与夜间照明分级',
      'Blue-green system concept — conceptual catchments, drainage types, shading '
      'and the night-lighting grades',
      'CB-03 / CONCEPT')}
<div class="wrap">
  <div class="band">{band_svg()}</div>
  <div class="cap"><span><b>CORRIDOR BAND</b> 走廊全域 · 图面旋转 90°，北向右 ·
   1 CSS px ≈ {f1(MPP)} m · 汇水分区界取三处重点区之间的中点 · 硬质面与绿荫面并置即热环境概念对比，未经实测</span>
   <span>north to the right, {f1(MPP)} m per CSS px</span></div>
  <div class="lgr"><span class="tt">数据 DATA</span>{lg}
   <span class="tt s">设想 SPEC</span>{lgs}</div>
  <div class="cols">
    <div class="cx" style="width:392px">
      <h3>蓝绿三层结构与三条层间判据<em>three layers and their relations</em></h3>
      {col_layers()}
    </div>
    <div class="cx" style="width:330px">
      <h3>十节点铺装径流去向<em>drainage type per node</em></h3>
      {col_dr()}
      <div class="ten"><b>OP-04 为母版：其排水取值已逐项核定，是其余节点取用 DR-B
      的来源，不是由 DR-B 推得。</b><em>OP-04 holds the master card; DR-B is taken
      from it, not derived from it.</em></div>
    </div>
    <div class="cx" style="width:380px">
      <h3>夜间照明分级与设计张力<em>night lighting and one tension</em></h3>
      {lights}
      <div class="ten"><b>{esc(TENSION_ZH)}</b><em>{esc(TENSION_EN)}</em></div>
    </div>
  </div>
  <div class="bn">{esc(BN_ZH)}<br><span>{esc(BN_EN)}</span></div>
  <div class="ft">{esc(ATTR_ZH)}<br>{esc(ATTR_EN)}<br>
  <span class="r">{esc(CRS_ZH)}</span> · 底图只铺干道与轨道 basemap: arterials and rail only · bluegreen-system-concept.png</div>
</div>
</body></html>"""


if __name__ == "__main__":
    render(build(), "bluegreen-system-concept",
           os.environ.get("W92_OUT", os.path.join(os.path.dirname(
               os.path.abspath(__file__)), "out")))
