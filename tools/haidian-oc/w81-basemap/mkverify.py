# -*- coding: utf-8 -*-
"""WP-81 交付二：核验图组 verification-overlay-00..06。

体裁抄 QGIS 核验出图：把 geometry/*.geojson 原样叠在 OSM 真实底图上直出。
作用有两个，都不是美化：
  1. 证明「文本里说的」与「包里交的」是同一份几何；
  2. 让读者一眼看见本包几何有多粗——要素数与顶点数逐图印在图上，
     四个用地仍是四条贴边矩形，图面不做任何掩饰。五条线位已按真实走向加密
     （各 20—24 顶点、合计 114 个），白圈随之逐点画出，顶点数不再是「两点直线」。

语言中立单套：一张图上中英双语图注上下并排，不出两套文件。
"""
from __future__ import annotations
from pathlib import Path as _HaidianPath

import json
import math
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import osmbase          # noqa: E402
import suppfont         # noqa: E402

PKG = str(_HaidianPath(__file__).resolve().parents[3] / 'submissions/lqqk7/every-sense-jingzhang')
# 页源与渲染器已随工具链迁出旧临时目录（见 build_figs.py 开头的说明）；此处原先仍
# 指向旧路径，旧目录一旦被回收本模块即不可运行，改为指向工具链内的同一份渲染器。
RENDER = os.path.join(os.path.dirname(HERE), "wp4b/render.js")
OUT_HTML = os.path.join(HERE, "html")
OUT_PNG = os.path.join(HERE, "png")

C = dict(deep="#10383d", teal="#177c78", coral="#d76450", purple="#6b5b95",
         gold="#d6a13b", sky="#4aa3c4", paper="#f2efe7", ink="#17383c",
         line="#cbd3cf", muted="#68787b", edge="#e2ddd0", onDarkEn="#9ecdc7")
FN = ["#59b0a7", "#94c49f", "#eac87d", "#a28ebd"]
GREEN_F, GREEN_S = "#cbdcc6", "#8fae8a"
BLDG_F, BLDG_S = "#b7c2c0", "#8fa19e"

MLAT = 110540.0
MLON = 111320.0 * math.cos(math.radians(39.98))


def gj(name):
    with open(os.path.join(PKG, "geometry", name + ".geojson"), encoding="utf-8") as f:
        return json.load(f)["features"]


def verts(g):
    t, c = g["type"], g["coordinates"]
    if t == "Point":
        return 1
    if t == "LineString":
        return len(c)
    if t == "Polygon":
        return sum(len(r) for r in c)
    if t == "MultiPolygon":
        return sum(len(r) for p in c for r in p)
    return 0


LAYERS = {n: gj(n) for n in ("site_boundary", "land_use", "roads", "buildings",
                             "green_space", "public_space", "key_areas",
                             "constraints")}
COUNT = {n: (len(f), sum(verts(x["geometry"]) for x in f)) for n, f in LAYERS.items()}

SITE_RING = LAYERS["site_boundary"][0]["geometry"]["coordinates"][0]
LAT0 = min(c[1] for c in SITE_RING)
LAT1 = max(c[1] for c in SITE_RING)
LON0 = min(c[0] for c in SITE_RING)
LON1 = max(c[0] for c in SITE_RING)


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def f1(v):
    return ("%.1f" % v).rstrip("0").rstrip(".")


# --------------------------------------------------------------- 版面常数
W, H = 1200, 750
PAD = 30
BAND_W, BAND_H = 1140.0, 196.0
CARD_W, CARD_H = 370.0, 190.0
DSF = "2.5"   # 3000x1875；与 1.8 MiB 包体预算反解所得
CARD_MPP = 5.8                     # 详图窗口比例尺：1 CSS px = 2.6 m


def band_proj():
    """走廊图带：图面旋转 90°，北向右（与包内既有图版同一取向）。"""
    s = (BAND_W - 24) / ((LAT1 - LAT0) * MLAT)
    y0 = (BAND_H - (LON1 - LON0) * MLON * s) / 2

    def to_px(lon, lat):
        return (12 + (lat - LAT0) * MLAT * s, y0 + (lon - LON0) * MLON * s)

    return to_px, 1 / s


def card_proj(idx):
    """三处重点区详图窗口：与图带同取向（图面旋转 90°，北向右），统一比例尺。

    取向与比例尺的选法不是构图偏好：重点区在纬度方向最长 2045 m、在经度方向
    939 m，北向上的横幅窗口装不下最长的一处；改为北向右并取能整幅装下最大一处
    的统一比例尺 5.8 m/px，三张卡才都是「整块重点区 + 街区上下文」，也才不会
    出现某一图层在某张卡里恰好落在窗口外、卡片一片空白的假象。
    """
    ring = LAYERS["key_areas"][idx]["geometry"]["coordinates"][0]
    clon = (min(c[0] for c in ring) + max(c[0] for c in ring)) / 2
    clat = (min(c[1] for c in ring) + max(c[1] for c in ring)) / 2
    span_lat = CARD_W * CARD_MPP / MLAT          # 纬度方向落在图面横轴
    span_lon = CARD_H * CARD_MPP / MLON          # 经度方向落在图面纵轴

    def to_px(lon, lat):
        return ((lat - (clat - span_lat / 2)) / span_lat * CARD_W,
                (lon - (clon - span_lon / 2)) / span_lon * CARD_H)

    return to_px


# ------------------------------------------------------------- 要素绘制
def _poly(feat, to_px, style):
    g = feat["geometry"]
    rings = ([g["coordinates"][0]] if g["type"] == "Polygon"
             else [p[0] for p in g["coordinates"]])
    d = "".join("M" + " L".join("%s %s" % tuple(f1(v) for v in to_px(c[0], c[1]))
                                for c in r) + "Z" for r in rings)
    return f'<path d="{d}" {style}/>'


def _line(feat, to_px, style):
    d = "M" + " L".join("%s %s" % tuple(f1(v) for v in to_px(c[0], c[1]))
                        for c in feat["geometry"]["coordinates"])
    return f'<path d="{d}" fill="none" {style}/>'


def draw_layer(name, to_px, scale=1.0, vertex_dots=True, a=1.0):
    """按图层画出提交几何；vertex_dots 把每个顶点打成小圈，顶点数肉眼可数。"""
    o = []
    fs = LAYERS[name]
    if name == "site_boundary":
        for f in fs:
            o.append(_poly(f, to_px, f'fill="none" stroke="{C["deep"]}" '
                                     f'stroke-width="1.2" stroke-dasharray="5 3.5" '
                                     f'opacity=".75"'))
    elif name == "land_use":
        for i, f in enumerate(fs):
            o.append(_poly(f, to_px, f'fill="{FN[i]}" fill-opacity="{0.33*a:.2f}" stroke="{FN[i]}" '
                                     f'stroke-width="1.4"'))
    elif name == "roads":
        for f in fs:
            rid = f["properties"]["id"]
            st = (f'stroke="{C["teal"]}" stroke-width="3"' if rid == "ROAD-001" else
                  f'stroke="{C["purple"]}" stroke-width="2.6" stroke-dasharray="7 5"'
                  if rid == "ROAD-005" else f'stroke="{C["sky"]}" stroke-width="2.4"')
            o.append(_line(f, to_px, st + ' stroke-linecap="round"'))
    elif name == "buildings":
        for f in fs:
            o.append(_poly(f, to_px, f'fill="{BLDG_F}" fill-opacity="{0.88*a:.2f}" '
                                     f'stroke="{BLDG_S}" stroke-width="1.1"'))
    elif name == "green_space":
        for f in fs:
            o.append(_poly(f, to_px, f'fill="{GREEN_F}" fill-opacity="{0.78*a:.2f}" '
                                     f'stroke="{GREEN_S}" stroke-width="1.1"'))
    elif name == "public_space":
        for f in fs:
            o.append(_poly(f, to_px, f'fill="{C["sky"]}" fill-opacity="{0.2*a:.2f}" '
                                     f'stroke="{C["sky"]}" stroke-width="1.1" '
                                     f'stroke-dasharray="3.5 2.4"'))
    elif name == "key_areas":
        for f in fs:
            o.append(_poly(f, to_px, f'fill="{C["coral"]}0d" stroke="{C["coral"]}" '
                                     f'stroke-width="1.6" stroke-dasharray="7 4"'))
    elif name == "constraints":
        for f in fs:
            x, y = to_px(*f["geometry"]["coordinates"][:2])
            o.append(f'<circle cx="{f1(x)}" cy="{f1(y)}" r="{f1(3.6*scale)}" '
                     f'fill="{C["purple"]}" stroke="#fff" stroke-width="{f1(1.2*scale)}"/>')
    if vertex_dots and name not in ("constraints",):
        for f in fs:
            g = f["geometry"]
            cs = []
            if g["type"] == "Polygon":
                cs = g["coordinates"][0]
            elif g["type"] == "MultiPolygon":
                cs = [c for p in g["coordinates"] for c in p[0]]
            elif g["type"] == "LineString":
                cs = g["coordinates"]
            for c in cs:
                x, y = to_px(c[0], c[1])
                o.append(f'<circle cx="{f1(x)}" cy="{f1(y)}" r="{f1(1.9*scale)}" '
                         f'fill="#fff" stroke="{C["deep"]}" stroke-width="{f1(0.9*scale)}"/>')
    return "".join(o)


# ----------------------------------------------------------------- 图组定义
SHEETS = [
    ("00-all",
     ["land_use", "green_space", "public_space", "buildings", "key_areas",
      "roads", "constraints"],
     "全部图层叠加", "All layers overlaid", True),
    ("01-landuse", ["land_use"], "用地结构 land_use", "Land use", True),
    ("02-roads", ["roads"], "线位 roads", "Roads (centrelines)", True),
    ("03-buildings", ["buildings"], "概念体量 buildings", "Buildings (concept masses)", True),
    ("04-green", ["green_space"], "绿地 green_space", "Green space", True),
    ("05-publicspace", ["public_space"], "公共空间 public_space", "Public space", True),
    ("06-keyareas", ["key_areas", "constraints"],
     "重点区 key_areas + 独立完成节点 constraints",
     "Key areas + completion nodes", True),
]

LAYER_LABEL = {
    "land_use": ("用地结构", "Land use"),
    "roads": ("线位（中心线）", "Roads (centrelines)"),
    "buildings": ("概念体量", "Buildings"),
    "green_space": ("绿地", "Green space"),
    "public_space": ("公共空间", "Public space"),
    "key_areas": ("重点区粗略范围", "Key areas (approximate)"),
    "constraints": ("独立完成节点", "Completion nodes"),
    "site_boundary": ("临时总体设计范围", "Provisional design scope"),
}
SWATCH = {
    "land_use": f'background:{FN[2]}55;border:1.4px solid {FN[2]}',
    "roads": f'background:{C["teal"]};height:3px;margin:6px 0',
    "buildings": f'background:{BLDG_F};border:1.1px solid {BLDG_S}',
    "green_space": f'background:{GREEN_F};border:1.1px solid {GREEN_S}',
    "public_space": f'background:{C["sky"]}33;border:1.1px dashed {C["sky"]}',
    "key_areas": f'background:{C["coral"]}14;border:1.6px dashed {C["coral"]}',
    "constraints": f'background:{C["purple"]};border-radius:50%;'
                   f'box-shadow:0 0 0 1.2px #fff inset',
    "site_boundary": f'background:transparent;border:1.2px dashed {C["deep"]}',
}

NOTE_ZH = ("本图为核验图：将本包提交的正式几何原样叠加于 OSM 底图。本包几何为关系示意级"
           "（要素数与顶点数如实可见），不表示测绘精度。")
NOTE_EN = ("This is a verification sheet: the geometry filed in this package is "
           "overlaid on an OpenStreetMap basemap exactly as submitted. The geometry "
           "is relationship-diagram grade — its feature and vertex counts are shown "
           "as they are — and does not represent survey accuracy.")
SUB_ZH = "白圈为几何顶点，逐个可数"
SUB_EN = "white ring = geometry vertex"
CRS_ZH = "坐标 EPSG:4326 · 量测复算 EPSG:4548 · 非法定规划图，不表示权属边界"
CRS_EN = ("Coordinates EPSG:4326, recomputed in EPSG:4548 · not a statutory plan "
          "· verification-overlay-{key}.png")

ATTR_ZH = ("底图数据 © OpenStreetMap 贡献者，ODbL 1.0；快照 osm-fabric-snapshot-20260815"
           "（该快照仅含 highway / railway 要素，故底图只有路网与轨道，无建筑与水系）")
ATTR_EN = ("Basemap data © OpenStreetMap contributors, ODbL 1.0; snapshot "
           "osm-fabric-snapshot-20260815 (highway / railway elements only: the "
           "basemap carries roads and rail, no buildings or water)")

KEY_NAME = [("01 众智园 AI 自主创新加速区", "Zhongzhiyuan AI Accelerator"),
            ("02 北京 AI 原点社区", "Beijing AI Origin Community"),
            ("03 大钟寺 AI 产业集聚区", "Dazhongsi AI Industry Cluster")]


def scalebar(px_per_unit, metres, x, y, label, col=None):
    col = col or C["deep"]
    w = metres / px_per_unit
    return (f'<g><line x1="{f1(x)}" y1="{f1(y)}" x2="{f1(x+w)}" y2="{f1(y)}" '
            f'stroke="{col}" stroke-width="2.2"/>'
            f'<line x1="{f1(x)}" y1="{f1(y-3.5)}" x2="{f1(x)}" y2="{f1(y+3.5)}" '
            f'stroke="{col}" stroke-width="2"/>'
            f'<line x1="{f1(x+w)}" y1="{f1(y-3.5)}" x2="{f1(x+w)}" y2="{f1(y+3.5)}" '
            f'stroke="{col}" stroke-width="2"/>'
            f'<text x="{f1(x+w+6)}" y="{f1(y+4)}" font-size="12" fill="{col}">'
            f'{esc(label)}</text></g>')


def north_right(x, y):
    return (f'<g><text x="{f1(x-14)}" y="{f1(y+4)}" font-size="12" font-weight="700" '
            f'text-anchor="end" fill="{C["deep"]}">N</text>'
            f'<line x1="{f1(x-10)}" y1="{f1(y)}" x2="{f1(x+12)}" y2="{f1(y)}" '
            f'stroke="{C["deep"]}" stroke-width="2.2"/>'
            f'<path d="M {f1(x+20)} {f1(y)} L {f1(x+11)} {f1(y-4.5)} '
            f'L {f1(x+11)} {f1(y+4.5)} Z" fill="{C["deep"]}"/></g>')


def north_up(x, y):
    return (f'<g><line x1="{f1(x)}" y1="{f1(y+18)}" x2="{f1(x)}" y2="{f1(y+4)}" '
            f'stroke="{C["deep"]}" stroke-width="2.2"/>'
            f'<path d="M {f1(x)} {f1(y-4)} L {f1(x-4.5)} {f1(y+5)} '
            f'L {f1(x+4.5)} {f1(y+5)} Z" fill="{C["deep"]}"/>'
            f'<text x="{f1(x+8)}" y="{f1(y+9)}" font-size="12" font-weight="700" '
            f'fill="{C["deep"]}">N</text></g>')


def band_svg(layers, dots):
    to_px, mpp = band_proj()
    base = osmbase.basemap_svg(to_px, (0, 0, BAND_W, BAND_H),
                               layers=["subway", "mid", "major", "rail"])
    o = [f'<svg viewBox="0 0 {f1(BAND_W)} {f1(BAND_H)}" width="{f1(BAND_W)}" '
         f'height="{f1(BAND_H)}" font-family="SHS">',
         f'<rect width="{f1(BAND_W)}" height="{f1(BAND_H)}" fill="#fdfcf9"/>', base,
         draw_layer("site_boundary", to_px, vertex_dots=False)]
    for n in layers:
        o.append(draw_layer(n, to_px, vertex_dots=dots))
    o.append(scalebar(mpp, 1000, 16, BAND_H - 12, "1 km"))
    o.append(north_right(BAND_W - 30, 18))
    o.append("</svg>")
    return "".join(o)


def card_svg(idx, layers, dots):
    to_px = card_proj(idx)
    base = osmbase.basemap_svg(to_px, (0, 0, CARD_W, CARD_H),
                               layers=["minor", "subway", "mid", "major", "rail"])
    o = [f'<svg viewBox="0 0 {f1(CARD_W)} {f1(CARD_H)}" width="{f1(CARD_W)}" '
         f'height="{f1(CARD_H)}" font-family="SHS">',
         f'<rect width="{f1(CARD_W)}" height="{f1(CARD_H)}" fill="#fdfcf9"/>', base,
         draw_layer("site_boundary", to_px, vertex_dots=False)]
    for n in layers:
        o.append(draw_layer(n, to_px, scale=1.6, vertex_dots=dots, a=0.55))
    o.append(scalebar(CARD_MPP, 500, 12, CARD_H - 12, "500 m"))
    o.append(north_right(CARD_W - 32, 16))
    o.append("</svg>")
    return "".join(o)


def legend_html(layers, dots):
    rows = []
    for n in ["site_boundary"] + layers:
        zh, en = LAYER_LABEL[n]
        cnt = COUNT[n]
        sw = SWATCH[n]
        extra = "width:13px;height:13px" if n == "constraints" else "width:22px;height:13px"
        rows.append(f'<span class="lg"><i style="{sw};{extra}"></i>'
                    f'<b>{esc(zh)}</b><em>{esc(en)}</em>'
                    f'<u>{cnt[0]} / {cnt[1]}</u></span>')
    if dots:
        rows.append(f'<span class="lg"><i style="background:#fff;border:1.2px solid '
                    f'{C["deep"]};border-radius:50%;width:13px;height:13px"></i>'
                    f'<b>{esc(SUB_ZH)}</b><em>{esc(SUB_EN)}</em></span>')
    return "".join(rows)


def sheet_html(key, layers, zh_t, en_t, dots):
    idx = key.split("-")[0]
    cards = "".join(
        f'<div class="cd"><div class="ch"><b>{esc(KEY_NAME[i][0])}</b>'
        f'<em>{esc(KEY_NAME[i][1])}</em></div>{card_svg(i, layers, dots)}</div>'
        for i in range(3))
    tot_f = sum(COUNT[n][0] for n in layers)
    tot_v = sum(COUNT[n][1] for n in layers)
    return f"""<!doctype html><html lang="zh"><head><meta charset="utf-8">
<title>verification-overlay-{key}</title><style>__FONT__
*{{box-sizing:border-box}}html,body{{margin:0;padding:0}}
body{{width:{W}px;height:{H}px;overflow:hidden;background:{C['paper']};
color:{C['ink']};font-family:SHS;-webkit-font-smoothing:antialiased;
text-rendering:geometricPrecision}}
.hd{{height:84px;background:{C['deep']};color:#fff;padding:12px {PAD}px 0;
display:flex;justify-content:space-between;align-items:flex-start}}
.hd .k{{font-size:12px;letter-spacing:.16em;color:{C['onDarkEn']};font-weight:700}}
.hd h1{{font-size:24px;font-weight:700;margin:7px 0 0;line-height:1.2}}
.hd h2{{font-size:14px;font-weight:400;margin:3px 0 0;color:{C['onDarkEn']};
line-height:1.2}}
.hd .r{{text-align:right}}
.hd .r .i{{font-size:12px;letter-spacing:.14em;font-weight:700}}
.pill{{display:inline-block;margin-top:9px;background:{C['coral']};color:#fff;
font-size:12px;padding:5px 12px;border-radius:11px;font-weight:700}}
.wrap{{padding:8px {PAD}px 0;height:{H-84}px;display:flex;flex-direction:column}}
.band{{width:{f1(BAND_W)}px;height:{f1(BAND_H)}px;border:1px solid {C['edge']};
border-radius:3px;overflow:hidden;flex:none}}
.cap{{display:flex;justify-content:space-between;gap:16px;font-size:12px;
color:{C['muted']};margin-top:4px;flex:none}}
.cap b{{color:{C['teal']};font-weight:700;letter-spacing:.06em}}
.lgr{{display:flex;flex-wrap:wrap;gap:6px 16px;margin-top:6px;flex:none}}
.lg{{display:flex;align-items:center;gap:6px;font-size:12px;line-height:1}}
.lg i{{display:block;flex:none}}
.lg b{{color:{C['ink']};font-weight:700}}
.lg em{{color:{C['muted']};font-style:normal}}
.lg u{{color:{C['coral']};text-decoration:none;font-weight:700}}
.cards{{display:flex;gap:15px;margin-top:7px;flex:none}}
.cd{{width:{f1(CARD_W)}px;border:1px solid {C['edge']};border-radius:3px;
overflow:hidden;background:#fff}}
.ch{{height:20px;background:{C['deep']};color:#fff;display:flex;align-items:center;
gap:7px;padding:0 8px;font-size:12px}}
.ch em{{color:{C['onDarkEn']};font-style:normal}}
.note{{margin-top:8px;border-top:1px solid {C['edge']};padding-top:6px;flex:none}}
.note p{{margin:0;font-size:12px;line-height:1.38}}
.note .zh{{color:{C['ink']};font-weight:700}}
.note .en{{color:{C['muted']};margin-top:2px}}
.note .s{{color:{C['muted']};margin-top:3px}}
.ft{{margin-top:auto;padding:5px 0 6px;border-top:1px solid {C['edge']};
font-size:12px;color:{C['muted']};line-height:1.32;flex:none}}
.ft .r{{color:{C['deep']};font-weight:700}}
</style></head><body>
<div class="hd">
  <div><div class="k">EVERY SENSE JING-ZHANG · GEOMETRY VERIFICATION SHEET</div>
  <h1>核验图 {idx}：{esc(zh_t)}</h1>
  <h2>Verification sheet {idx} — {esc(en_t)} · submitted geometry on an OSM basemap</h2></div>
  <div class="r"><div class="i">V{idx} / VERIFICATION</div>
  <div class="pill">核验图 · NOT A DESIGN SHEET</div></div>
</div>
<div class="wrap">
  <div class="band">{band_svg(layers, dots)}</div>
  <div class="cap"><span><b>CORRIDOR BAND</b> 走廊全域 · 图面旋转 90°，北向右 ·
    1 CSS px ≈ {f1(band_proj()[1])} m</span>
    <span>本图要素 {tot_f} 个 / 顶点 {tot_v} 个 · features {tot_f} / vertices {tot_v}</span></div>
  <div class="lgr">{legend_html(layers, dots)}</div>
  <div class="cards">{cards}</div>
  <div class="cap"><span><b>DETAIL WINDOWS</b> 三处重点区详图窗口 · 与图带同取向，北向右 ·
    1 CSS px = {f1(CARD_MPP)} m（窗口 {f1(CARD_W*CARD_MPP)} × {f1(CARD_H*CARD_MPP)} m，整幅覆盖各重点区）</span>
    <span>detail windows, north to the right, {f1(CARD_MPP)} m per CSS px</span></div>
  <div class="note">
    <p class="zh">{esc(NOTE_ZH)}</p>
    <p class="en">{esc(NOTE_EN)}</p>
  </div>
  <div class="ft">{esc(ATTR_ZH)}<br>{esc(ATTR_EN)}<br>
  <span class="r">{esc(CRS_ZH)}</span> · {esc(CRS_EN.format(key=key))}</div>
</div>
</body></html>"""


def main():
    os.makedirs(OUT_HTML, exist_ok=True)
    os.makedirs(OUT_PNG, exist_ok=True)
    docs = {}
    for key, layers, zh_t, en_t, dots in SHEETS:
        docs[key] = sheet_html(key, layers, zh_t, en_t, dots)
    chars = "".join(d.replace("__FONT__", "") for d in docs.values())
    face = suppfont.full_face_css(chars)
    for key, html in docs.items():
        p = os.path.join(OUT_HTML, f"verification-overlay-{key}.html")
        with open(p, "w", encoding="utf-8") as f:
            f.write(html.replace("__FONT__", face))
        out = os.path.join(OUT_PNG, f"verification-overlay-{key}.raw.png")
        r = subprocess.run(["node", RENDER, "png", p, out, str(W), str(H), DSF],
                           capture_output=True, text=True)
        if r.returncode:
            raise SystemExit(r.stderr)
        print("ok", key, os.path.getsize(out) // 1024, "KB raw")


if __name__ == "__main__":
    main()
