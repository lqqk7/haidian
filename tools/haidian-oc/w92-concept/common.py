# -*- coding: utf-8 -*-
"""WP-92 概念详图三图共用件：数据装载、投影、记号与版面常数。

体裁定位
--------
本波三张图是**概念推演图**，与包内既有的核验图组、片区策略图版属不同体裁：
既有图版一律只画已登记几何与判据，明确承诺「只标类型，不画通道线位」；本波
在最显著位置声明概念性质之后，把同一批既有判据落成一次空间组合，因此图上出
现通道线位、建筑体量与界面分段。二者不矛盾的条件只有一个——每一个设想要素
都必须能指回包内既有判据，且图面必须把「数据派生」与「概念设想」区分到肉眼
可辨：实线＝数据派生，虚线＝概念设想。

版面纪律沿用 v8.2 起的既有口径：输出 3000 × 1875（CSS 1200 × 750，DSF 2.5），
接收分辨率短边 768 像素的重采样比 0.4096，故 CSS 字号下限取 12 px。
"""
from __future__ import annotations
from pathlib import Path as _HaidianPath

import json
import math
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
T = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(T, "w81-basemap"))

import osmbase           # noqa: E402
import suppfont          # noqa: E402

PKG = (str(_HaidianPath(__file__).resolve().parents[3] / 'submissions/lqqk7') + "/"
       "every-sense-jingzhang")
RENDER = os.path.join(T, "wp4b/render.js")
RINGS_PATH = os.path.join(T, "w89-district/cand_rings.json")

W, H = 1200, 750
PAD = 30
DSF = os.environ.get("W92_DSF", "2.5")

MLAT = 110540.0
MLON = 111320.0 * math.cos(math.radians(39.99))

C = dict(deep="#10383d", teal="#177c78", coral="#d76450", purple="#6b5b95",
         gold="#d6a13b", sky="#4aa3c4", paper="#f2efe7", ink="#17383c",
         muted="#68787b", edge="#e2ddd0", onDarkEn="#9ecdc7",
         spec="#a8452f", river="#2f6f8a", plate="#ffffff", green="#6f9464")

# 概念声明：三图共用同一句，逐字不变，位置在图头之下、任何图版之上。
DECL_ZH = ("概念推演图：建筑体量、通道线位与界面划分均为设计设想，"
           "不基于权属、红线或测绘资料，不代表现状或规划真实情况。")
DECL_EN = ("Concept speculation drawing: the building masses, passage alignments "
           "and frontage divisions are design speculation. They rest on no tenure, "
           "red-line or survey data and represent neither existing conditions nor "
           "any actual plan.")
PILL = "CONCEPT SPECULATION · 非法定规划图"

DIST_ZH = ("实线为数据派生，虚线为概念设想；每一设想要素的既有判据来源逐项标注，"
           "并在 visual/assets/concept-design-register.json 内登记。")
DIST_EN = ("Solid marks are data-derived, dashed marks are speculation; the existing "
           "criterion behind each speculative element is labelled here and registered "
           "in visual/assets/concept-design-register.json.")

INVERT_ZH = ("本图属「深度倒挂」声明的中间层概念补层：不改变「无官方资料不给权属级结论」"
             "的立场，也不把设想升格为主张。")
INVERT_EN = ("This sheet is the concept layer added to the middle tier of the declared "
             "depth inversion: it neither changes the position that no tenure-grade "
             "conclusion is drawn without official data, nor promotes speculation "
             "into a claim.")

ATTR_ZH = ("底图数据 © OpenStreetMap 贡献者，ODbL 1.0；快照 osm-fabric-snapshot-20260815"
           "（该快照仅含 highway / railway 要素，故底图只有路网与轨道，无建筑与水系）")
ATTR_EN = ("Basemap data © OpenStreetMap contributors, ODbL 1.0; snapshot "
           "osm-fabric-snapshot-20260815 (highway / railway elements only: the "
           "basemap carries roads and rail, no buildings or water)")
CRS_ZH = "坐标 EPSG:4326 · 量测复算 EPSG:4548 · 非法定规划图，不表示权属边界"


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def f1(v):
    return ("%.1f" % v).rstrip("0").rstrip(".")


def th(v):
    return "{:,}".format(int(round(v)))


# ------------------------------------------------------------------ 数据
def gj(name):
    with open(os.path.join(PKG, "geometry", name + ".geojson"), encoding="utf-8") as f:
        return {x["properties"]["id"]: x for x in json.load(f)["features"]}


def load(name):
    with open(os.path.join(PKG, "visual/assets", name), encoding="utf-8") as f:
        return json.load(f)


DS = load("district-strategy.json")
SDC = load("sensory-design-code.json")
RINGS = json.load(open(RINGS_PATH, encoding="utf-8"))
ROADS = gj("roads")
NODES = gj("constraints")
PUBLIC = gj("public_space")
GREEN = gj("green_space")
KEYA = {f["properties"]["area_id"]: f for f in
        json.load(open(os.path.join(PKG, "geometry/key_areas.geojson"),
                       encoding="utf-8"))["features"]}


def to_m(lon, lat, lon0, lat0):
    return ((lon - lon0) * MLON, (lat - lat0) * MLAT)


# ------------------------------------------------------------------ 投影
def make_proj(clon, clat, w_px, h_px, mpp):
    """图面旋转 90°、北向右（沿用包内既有图版取向）：纬度落横轴，经度落纵轴。"""
    span_lat = w_px * mpp / MLAT
    span_lon = h_px * mpp / MLON
    lat0, lon0 = clat - span_lat / 2, clon - span_lon / 2

    def to_px(lon, lat):
        return ((lat - lat0) / span_lat * w_px, (lon - lon0) / span_lon * h_px)

    return to_px


def bbox_center(points):
    return ((min(p[0] for p in points) + max(p[0] for p in points)) / 2,
            (min(p[1] for p in points) + max(p[1] for p in points)) / 2)


def path_of(coords, to_px, close=False):
    d = "M" + " L".join("%s %s" % tuple(f1(v) for v in to_px(c[0], c[1]))
                        for c in coords)
    return d + ("Z" if close else "")


# ------------------------------------------------------------------ 记号
def scalebar(x, y, mpp, metres, label, col=None):
    col = col or C["deep"]
    w = metres / mpp
    return (f'<g><line x1="{f1(x)}" y1="{f1(y)}" x2="{f1(x+w)}" y2="{f1(y)}" '
            f'stroke="{col}" stroke-width="2.2"/>'
            f'<line x1="{f1(x)}" y1="{f1(y-3.5)}" x2="{f1(x)}" y2="{f1(y+3.5)}" '
            f'stroke="{col}" stroke-width="2"/>'
            f'<line x1="{f1(x+w)}" y1="{f1(y-3.5)}" x2="{f1(x+w)}" y2="{f1(y+3.5)}" '
            f'stroke="{col}" stroke-width="2"/>'
            f'<text x="{f1(x+w+6)}" y="{f1(y+4)}" font-size="12" fill="{col}">'
            f'{esc(label)}</text></g>')


def north_right(x, y, col=None):
    col = col or C["deep"]
    return (f'<g><text x="{f1(x-14)}" y="{f1(y+4)}" font-size="12" font-weight="700" '
            f'text-anchor="end" fill="{col}">N</text>'
            f'<line x1="{f1(x-10)}" y1="{f1(y)}" x2="{f1(x+12)}" y2="{f1(y)}" '
            f'stroke="{col}" stroke-width="2.2"/>'
            f'<path d="M {f1(x+20)} {f1(y)} L {f1(x+11)} {f1(y-4.5)} '
            f'L {f1(x+11)} {f1(y+4.5)} Z" fill="{col}"/></g>')


def label(x, y, text, col=None, size=12, weight=700, anchor="start", halo=True):
    col = col or C["ink"]
    t = esc(text)
    o = ""
    if halo:
        o += (f'<text x="{f1(x)}" y="{f1(y)}" font-size="{size}" '
              f'font-weight="{weight}" text-anchor="{anchor}" fill="none" '
              f'stroke="#fdfcf9" stroke-width="3" stroke-linejoin="round" '
              f'paint-order="stroke">{t}</text>')
    o += (f'<text x="{f1(x)}" y="{f1(y)}" font-size="{size}" font-weight="{weight}" '
          f'text-anchor="{anchor}" fill="{col}">{t}</text>')
    return o


# ------------------------------------------------------------------ 版面
def head(kind, title_zh, title_en, code):
    return f"""<div class="hd">
  <div><div class="k">EVERY SENSE JING-ZHANG · {kind}</div>
  <h1>{esc(title_zh)}</h1>
  <h2>{esc(title_en)}</h2></div>
  <div class="r"><div class="i">{esc(code)}</div>
  <div class="pill">{esc(PILL)}</div></div>
</div>
<div class="decl"><p class="z">{esc(DECL_ZH)}</p><p class="e">{esc(DECL_EN)}</p></div>"""


def base_css():
    return f"""*{{box-sizing:border-box}}html,body{{margin:0;padding:0}}
body{{width:{W}px;height:{H}px;overflow:hidden;background:{C['paper']};
color:{C['ink']};font-family:SHS;font-size:12px;line-height:1.3;
display:flex;flex-direction:column;
-webkit-font-smoothing:antialiased;text-rendering:geometricPrecision}}
.hd{{height:74px;background:{C['deep']};color:#fff;padding:9px {PAD}px 0;
display:flex;justify-content:space-between;align-items:flex-start}}
.hd .k{{font-size:12px;letter-spacing:.15em;color:{C['onDarkEn']};font-weight:700}}
.hd h1{{font-size:22px;font-weight:700;margin:5px 0 0;line-height:1.16}}
.hd h2{{font-size:13px;font-weight:400;margin:2px 0 0;color:{C['onDarkEn']};
line-height:1.16}}
.hd .r{{text-align:right}}
.hd .r .i{{font-size:12px;letter-spacing:.14em;font-weight:700}}
.pill{{display:inline-block;margin-top:7px;background:{C['coral']};color:#fff;
font-size:12px;padding:4px 11px;border-radius:11px;font-weight:700;white-space:nowrap}}
.hd,.decl{{flex:none}}
.decl{{background:{C['spec']};color:#fff;padding:5px {PAD}px 6px}}
.decl .z{{margin:0;font-size:14px;font-weight:700;line-height:1.24}}
.decl .e{{margin:1px 0 0;font-size:12px;color:#f6ded7;line-height:1.24}}
.wrap{{padding:6px {PAD}px 0;flex:1;min-height:0;display:flex;flex-direction:column}}
.cap{{display:flex;justify-content:space-between;gap:14px;font-size:12px;
color:{C['muted']};margin-top:3px;flex:none}}
.cap b{{color:{C['teal']};font-weight:700;letter-spacing:.05em}}
.lgr{{display:flex;flex-wrap:wrap;gap:4px 14px;margin-top:5px;flex:none}}
.lg{{display:flex;align-items:center;gap:5px;font-size:12px;line-height:1}}
.lg i{{display:block;flex:none;width:20px;height:11px}}
.lg b{{color:{C['ink']};font-weight:700}}
.lg em{{color:{C['muted']};font-style:normal}}
.ft{{margin-top:auto;padding:4px 0 5px;border-top:1px solid {C['edge']};
font-size:12px;color:{C['muted']};line-height:1.3;flex:none}}
.ft .r{{color:{C['deep']};font-weight:700}}"""


def render(html, name, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    face = suppfont.full_face_css(html.replace("__FONT__", ""))
    hp = os.path.join(out_dir, name + ".html")
    with open(hp, "w", encoding="utf-8") as f:
        f.write(html.replace("__FONT__", face))
    out = os.path.join(out_dir, name + ".raw.png")
    r = subprocess.run(["node", RENDER, "png", hp, out, str(W), str(H), DSF],
                       capture_output=True, text=True)
    if r.returncode:
        raise SystemExit(r.stderr)
    print("ok %-34s %8d B raw" % (name, os.path.getsize(out)))
    return hp, out
