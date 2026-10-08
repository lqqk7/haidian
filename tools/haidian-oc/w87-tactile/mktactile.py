# -*- coding: utf-8 -*-
"""assets/figures/tactile-corridor-map.png —— 全带触觉走廊图（触觉印刷原稿）。

体裁与包内既有触觉件（assets/tactile/op04-papercraft.svg、
visual/assets/op04-tactile-map.json）同一纪律：给出可制版的几何与设计目标值，
如实登记「未经视障使用者测试、未经盲文专业者校对」，不以制版成功替代触觉可用
性结论。

语言中立单套：图面本身不含语言（凸起线、点、形状），墨印图注中英双语上下并
排——墨印一层是给明眼协助者读的，触觉一层是给使用者摸的，两层同版。

与其他图版的关系：线位取自同一份 geometry/roads.geojson，投影算式与
site-overview 逐字相同（w81-basemap/geom_params.site_overview），因此本图与
01 图版、A3 第 02 页图带、核验图 02 是同一走向。差别只在触觉泛化三步——简化、
平滑、位移——每一步的量都印在图上，见 tgeom.py 的说明。
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
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(T, "w81-basemap"))

import geom_params as GP        # noqa: E402
import suppfont                 # noqa: E402
import tgeom as TG              # noqa: E402

PKG = str(_HaidianPath(__file__).resolve().parents[3] / 'submissions/lqqk7/every-sense-jingzhang')
RENDER = os.path.join(T, "wp4b/render.js")
# 渲染倍率 2.0（2400x1500）不是随手取的：包体硬线 40 MiB，本波三张图版收口后
# 只剩约 180 KB 余量给后续登记文件。逐档实测（2.5 / 2.0 / 1.8 / 1.6 / 1.5）后，
# 2.0 是仍能让 10.5 px 图注在 100%% 查看下保持锐利、又能与另一张新图一并装进硬线
# 的最高一档；核验图组同样是按包体预算反解倍率（见 w81-basemap/mkverify.py）。
W, H, PAD, DSF = 1200, 750, 30, "2.0"

C = dict(deep="#10383d", teal="#177c78", coral="#d76450", purple="#6b5b95",
         sky="#4aa3c4", paper="#f2efe7", ink="#17383c", muted="#68787b",
         edge="#e2ddd0", onDarkEn="#9ecdc7", relief="#2b4f52", plate="#ffffff")

# ---------------------------------------------------------------- 制版尺度
SHEET_MM = 594.0                       # 建议印制幅面：A2 横向 594 x 420 mm
MMPP = SHEET_MM / W                    # 1 CSS px = 0.495 mm
MM = lambda mm: mm / MMPP              # noqa: E731  毫米 -> CSS px

W_SPINE_MM, W_QUIET_MM = 3.0, 2.0      # 凸线宽度设计目标值
GAP_MM = 6.0                           # 平行凸线净间距设计目标值
DOT_MM, HALO_MM = 3.5, 1.5             # 完成点凸点直径 / 四周留空环宽
SHAPE_MM, SHAPE_W_MM = 14.0, 2.0       # 重点区触觉图形外径 / 线宽
BAR_W_MM = 1.5                         # 重点区区段条凸线宽
DP_TOL_MM = 2.5                        # 简化容差（图面）

BR_DOT_MM, BR_DX_MM, BR_DY_MM, BR_CELL_MM = 1.5, 2.5, 2.5, 6.0   # 盲文点位

# --------------------------------------------------------------- 几何与泛化
proj = GP.site_overview()
to_px, MPP = proj["to_px"], proj["mpp"]


def gj(name):
    with open(os.path.join(PKG, "geometry", name + ".geojson"), encoding="utf-8") as f:
        return json.load(f)["features"]


def px(coords):
    return [to_px(c[0], c[1]) for c in coords]


roads = {f["properties"]["id"]: f for f in gj("roads")}
S0 = px(roads["ROAD-001"]["geometry"]["coordinates"])
Q0 = px(roads["ROAD-005"]["geometry"]["coordinates"])

TOL = MM(DP_TOL_MM)
S1 = TG.chaikin(TG.dp(S0, TOL), 1)
Q1 = TG.chaikin(TG.dp(Q0, TOL), 1)
TARGET = MM(GAP_MM + W_SPINE_MM / 2 + W_QUIET_MM / 2)
Q2 = TG.displace(Q1, S1, TARGET)

GEN = dict(
    dp_keep=(len(TG.dp(S0, TOL)), len(TG.dp(Q0, TOL))),
    dp_drop_m=max(TG.poly_dist(p, TG.dp(S0, TOL))[0] for p in S0) * MPP,
    smooth_m=TG.max_dev(S0, S1) * MPP,
    push_max_m=max(TG.dist(a, b) for a, b in zip(Q1, Q2)) * MPP,
    dev_q_m=TG.max_dev(Q0, Q2) * MPP,
    gap_mm=min(TG.poly_dist(q, S1)[0] for q in Q2) * MMPP - (W_SPINE_MM + W_QUIET_MM) / 2,
    len_s=(TG.length(S0) * MPP, TG.length(S1) * MPP),
    len_q=(TG.length(Q0) * MPP, TG.length(Q2) * MPP),
)

NODES = sorted(((f["properties"]["id"], to_px(*f["geometry"]["coordinates"]))
                for f in gj("constraints")), key=lambda t: t[0])
NODE_MIN_MM = min(TG.dist(a[1], b[1]) for i, a in enumerate(NODES)
                  for b in NODES[i + 1:]) * MMPP - MM(DOT_MM + 2 * HALO_MM) * MMPP

AREAS = {}
for f in gj("key_areas"):
    pts = px(f["geometry"]["coordinates"][0])
    xs = [p[0] for p in pts]
    AREAS[f["properties"]["id"]] = (min(xs), max(xs))

# ------------------------------------------------------------------- 版面
BAND_W, BAND_H = 1140.0, 188.0           # 图带局部坐标系，与页面通过 CSS 定位
SHAPE_CY = 25.0                          # 三个触觉图形的中心行
BAR_Y = 52.0                             # 重点区区段条
CONTENT_TOP = min([y for _, y in S1] + [y for _, y in Q2]
                  + [p[1] for _, p in NODES]) - MM(DOT_MM / 2 + HALO_MM)
SHIFT = 76.0 - CONTENT_TOP               # 走廊内容整体平移，仅裁切不缩放


def yy(y):
    return y + SHIFT


def pathd(pts):
    return "M " + " L ".join("%.2f,%.2f" % (x, yy(y)) for x, y in pts)


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# ------------------------------------------------------------ 触觉符号绘制
def relief_line(pts, w_mm, dash=None):
    d = ' stroke-dasharray="%.2f %.2f"' % (MM(8.0), MM(4.0)) if dash else ""
    return ('<path d="%s" fill="none" stroke="%s" stroke-width="%.2f" '
            'stroke-linecap="round" stroke-linejoin="round"%s/>'
            % (pathd(pts), C["relief"], MM(w_mm), d))


def relief_dot(x, y, shifted=True):
    cy = yy(y) if shifted else y
    return ('<circle cx="%.2f" cy="%.2f" r="%.2f" fill="none" stroke="%s" '
            'stroke-width="%.2f"/><circle cx="%.2f" cy="%.2f" r="%.2f" fill="%s"/>'
            % (x, cy, MM(DOT_MM / 2 + HALO_MM / 2), C["plate"], MM(HALO_MM),
               x, cy, MM(DOT_MM / 2), C["relief"]))


def shape_svg(kind, cx, cy):
    r = MM(SHAPE_MM / 2)
    sw = MM(SHAPE_W_MM)
    at = 'fill="none" stroke="%s" stroke-width="%.2f" stroke-linejoin="round"' % (
        C["relief"], sw)
    if kind == "circle":
        return '<circle cx="%.2f" cy="%.2f" r="%.2f" %s/>' % (cx, cy, r - sw / 2, at)
    if kind == "square":
        s = (r - sw / 2) * 1.72
        return ('<rect x="%.2f" y="%.2f" width="%.2f" height="%.2f" rx="%.2f" %s/>'
                % (cx - s / 2, cy - s / 2, s, s, sw * 0.5, at))
    h = (r - sw / 2) * 1.95
    w2 = h * 0.577 * 2
    return ('<path d="M %.2f,%.2f L %.2f,%.2f L %.2f,%.2f Z" %s/>'
            % (cx, cy - h * 0.62, cx + w2 / 2, cy + h * 0.38,
               cx - w2 / 2, cy + h * 0.38, at))


# --------------------------------------------------------------- 盲文点阵
UEB = {"a": "1", "b": "12", "c": "14", "d": "145", "e": "15", "f": "124",
       "g": "1245", "h": "125", "i": "24", "j": "245", "k": "13", "l": "123",
       "m": "134", "n": "1345", "o": "135", "p": "1234", "q": "12345",
       "r": "1235", "s": "234", "t": "2345", "u": "136", "v": "1236",
       "w": "2456", "x": "1346", "y": "13456", "z": "1356", ".": "256",
       " ": "", "CAP": "6"}
DOTPOS = {1: (0, 0), 2: (0, 1), 3: (0, 2), 4: (1, 0), 5: (1, 1), 6: (1, 2)}


def braille_cells(text):
    """文本 -> 方序列（大写字母前置大写指示符 ⠠，与包内 UEB 体例一致）。"""
    cells = []
    for ch in text:
        if ch.isupper():
            cells.append(UEB["CAP"])
            cells.append(UEB[ch.lower()])
        else:
            cells.append(UEB[ch])
    return cells


def braille_svg(text, x0, y0):
    out = []
    x = x0
    for cell in braille_cells(text):
        for d in cell:
            cx, cy = DOTPOS[int(d)]
            out.append('<circle cx="%.2f" cy="%.2f" r="%.2f" fill="%s"/>'
                       % (x + cx * MM(BR_DX_MM), y0 + cy * MM(BR_DY_MM),
                          MM(BR_DOT_MM / 2), C["relief"]))
        x += MM(BR_CELL_MM)
    return "".join(out), x - x0


BRAILLE_TEXT = "Tactile corridor map"
BRAILLE_UNICODE = "".join(
    chr(0x2800 + sum(1 << (int(d) - 1) for d in c)) if c else "⠀"
    for c in braille_cells(BRAILLE_TEXT))

# ------------------------------------------------------------------ 图面
SHAPE_AT = [("PROV-KEY-001", "circle"), ("PROV-KEY-002", "square"),
            ("PROV-KEY-003", "triangle")]


def band_svg():
    g = ['<svg viewBox="0 0 %.0f %.0f" width="%.0f" height="%.0f">'
         % (BAND_W, BAND_H, BAND_W, BAND_H),
         '<rect width="%.0f" height="%.0f" fill="%s"/>' % (BAND_W, BAND_H, C["plate"])]
    # 重点区：区段条 + 触觉图形
    for aid, kind in SHAPE_AT:
        x0, x1 = AREAS[aid]
        g.append('<path d="M %.2f,%.2f L %.2f,%.2f" fill="none" stroke="%s" '
                 'stroke-width="%.2f" stroke-linecap="round"/>'
                 % (x0, BAR_Y, x1, BAR_Y, C["relief"], MM(BAR_W_MM)))
        g.append(shape_svg(kind, (x0 + x1) / 2, SHAPE_CY))
    # 两条线位
    g.append(relief_line(Q2, W_QUIET_MM, dash=True))
    g.append(relief_line(S1, W_SPINE_MM))
    # 十个完成点
    for nid, (x, y) in NODES:
        g.append(relief_dot(x, y))
    # 墨印编号（不凸起，供明眼协助者对照）。方向逐点指定：默认置于凸点上方，
    # 落在凸线上或与邻点相撞的四个编号改置下方或侧方，使编号既不压线也不互压。
    DIR = {"OP-03": "left", "OP-04": "left", "OP-05": "below", "OP-07": "below"}
    r = MM(DOT_MM / 2 + HALO_MM)
    for nid, (x, y) in NODES:
        d = DIR.get(nid, "above")
        if d == "above":
            tx, ty, anchor = x, yy(y) - r - 4.0, "middle"
        elif d == "below":
            tx, ty, anchor = x, yy(y) + r + 11.0, "middle"
        else:
            tx, ty, anchor = x - r - 3.0, yy(y) + 4.0, "end"
        g.append('<text x="%.2f" y="%.2f" text-anchor="%s" font-size="11" '
                 'font-weight="700" fill="%s" stroke="%s" stroke-width="3" '
                 'paint-order="stroke">%s</text>'
                 % (tx, ty, anchor, C["muted"], C["plate"], nid[3:]))
    g.append("</svg>")
    return "".join(g)


def legend_svg(kind, w=54.0, h=22.0):
    m = h / 2
    if kind == "spine":
        s = '<path d="M 3,%.1f L %.1f,%.1f" fill="none" stroke="%s" stroke-width="%.2f" stroke-linecap="round"/>' % (m, w - 3, m, C["relief"], MM(W_SPINE_MM))
    elif kind == "quiet":
        s = '<path d="M 3,%.1f L %.1f,%.1f" fill="none" stroke="%s" stroke-width="%.2f" stroke-linecap="round" stroke-dasharray="%.2f %.2f"/>' % (m, w - 3, m, C["relief"], MM(W_QUIET_MM), MM(8.0), MM(4.0))
    elif kind == "bar":
        s = '<path d="M 3,%.1f L %.1f,%.1f" fill="none" stroke="%s" stroke-width="%.2f" stroke-linecap="round"/>' % (m, w - 3, m, C["relief"], MM(BAR_W_MM))
    elif kind == "dot":
        s = ('<path d="M 3,%.1f L %.1f,%.1f" fill="none" stroke="%s" stroke-width="%.2f" stroke-linecap="round"/>' % (m, w - 3, m, C["relief"], MM(W_SPINE_MM))) + relief_dot(w / 2, m, shifted=False)
    else:
        s = shape_svg(kind, w / 2, m)
    return ('<svg viewBox="0 0 %.0f %.0f" width="%.0f" height="%.0f">'
            '<rect width="%.0f" height="%.0f" fill="%s"/>%s</svg>'
            % (w, h, w, h, w, h, C["plate"], s))


LEGEND = [
    ("spine", "通用可达底线（最宽凸线）", "Universal access baseline"),
    ("quiet", "低刺激安静替代线（虚凸线）", "Quiet alternative, dashed"),
    ("dot", "十个独立完成点（四周留空）", "Completion point, clear ring"),
    ("bar", "重点区沿走廊的区段范围", "Key-area extent along corridor"),
    ("circle", "重点区 · 验证（众智园）", "Key area — verify"),
    ("square", "重点区 · 共创（AI 原点社区）", "Key area — co-design"),
    ("triangle", "重点区 · 采用（大钟寺）", "Key area — adopt"),
]

SIMPLIFY_ZH = (
    "触觉泛化三步（与 01 图版同一份 geometry/roads.geojson、同一投影算式，差别只在"
    "下列泛化，量值如实登记）：① 简化 Douglas-Peucker，图面容差 %.1f mm（实地约 %.0f m），"
    "主脊 %d→%d 顶点、安静线 %d→%d，被删顶点最大偏离 %.0f m；② 平滑 Chaikin 一轮，"
    "转角圆化，最大偏离 %.0f m；③ 位移 安静线沿主脊法向外推最大 %.0f m，推后两线净间距 "
    "%.1f mm，相对提交线位最大偏移 %.0f m。线长 主脊 %.1f→%.1f km、安静线 %.1f→%.1f km。"
    "位移只作用于安静线，主脊线位不动。"
) % (DP_TOL_MM, DP_TOL_MM / MMPP * MPP, len(S0), GEN["dp_keep"][0], len(Q0),
     GEN["dp_keep"][1], GEN["dp_drop_m"], GEN["smooth_m"], GEN["push_max_m"],
     GEN["gap_mm"], GEN["dev_q_m"], GEN["len_s"][0] / 1000, GEN["len_s"][1] / 1000,
     GEN["len_q"][0] / 1000, GEN["len_q"][1] / 1000)

SIMPLIFY_EN = (
    "Three generalisation steps for touch (same GeoJSON and projection as plate 01; only "
    "these differ, all logged): 1. Douglas-Peucker at %.1f mm on the sheet, about %.0f m "
    "on the ground — spine %d→%d vertices, quiet line %d→%d, largest dropped-vertex "
    "deviation %.0f m; 2. one Chaikin pass, corners rounded, largest deviation %.0f m; "
    "3. the quiet line pushed along the spine normal by up to %.0f m to clear it by "
    "%.1f mm, a %.0f m maximum shift from the submitted alignment. Lengths: spine "
    "%.1f→%.1f km, quiet %.1f→%.1f km. Only the quiet line moves."
) % (DP_TOL_MM, DP_TOL_MM / MMPP * MPP, len(S0), GEN["dp_keep"][0], len(Q0),
     GEN["dp_keep"][1], GEN["dp_drop_m"], GEN["smooth_m"], GEN["push_max_m"],
     GEN["gap_mm"], GEN["dev_q_m"], GEN["len_s"][0] / 1000, GEN["len_s"][1] / 1000,
     GEN["len_q"][0] / 1000, GEN["len_q"][1] / 1000)

SPEC_ZH = (
    "印制规格（设计目标值，非实测结果）：建议幅面 A2 横向 %.0f×420 mm，1 CSS px = %.3f mm，"
    "比例尺 1 CSS px ≈ %.1f m；凸线宽 主脊 %.1f / 安静线 %.1f / 区段条 %.1f mm，平行凸线"
    "净间距 ≥%.1f mm；凸点直径 %.1f mm、留空环 %.1f mm；触觉图形外径 %.0f mm、线宽 %.1f mm；"
    "凸起高度 0.8—1.2 mm（沿用 op04-tactile-map）。全图同类符号最小净间距 "
    "%.1f mm（OP-04 与 OP-08 之间），接近指尖可辨下限。盲文点位尺寸依 GB/T 15720"
    "《中国盲文》核定，不复制标准数值。本 PNG 只是版式与几何示意，制版须按上列毫米值"
    "重出矢量原稿；以上未经视障使用者测试，制版成功不等于触觉可用。"
) % (SHEET_MM, MMPP, MPP, W_SPINE_MM, W_QUIET_MM, BAR_W_MM, GAP_MM, DOT_MM, HALO_MM,
     SHAPE_MM, SHAPE_W_MM, NODE_MIN_MM)

SPEC_EN = (
    "Print specification — design targets, not measurements. Sheet A2 landscape "
    "%.0f×420 mm, 1 CSS px = %.3f mm, scale 1 CSS px ≈ %.1f m. Raised lines %.1f / %.1f / "
    "%.1f mm (spine / quiet / extent bar), parallel clearance ≥%.1f mm. Raised dots %.1f mm "
    "with a %.1f mm clear ring; shapes %.0f mm at %.1f mm; relief height 0.8–1.2 mm "
    "(op04-tactile-map). Smallest same-kind clearance %.1f mm (OP-04/OP-08), "
    "near the fingertip limit. Braille cell sizes from GB/T 15720, not reproduced here. "
    "This PNG is a layout reference — plates must be re-output as vector art at the sizes "
    "above; untested with blind users."
) % (SHEET_MM, MMPP, MPP, W_SPINE_MM, W_QUIET_MM, BAR_W_MM, GAP_MM, DOT_MM, HALO_MM,
     SHAPE_MM, SHAPE_W_MM, NODE_MIN_MM)

BR_ZH = ("盲文标题（英文 UEB 一级、逐字母）读作 “%s”。转写规则与映射表沿用包内 "
         "visual/assets/braille-core-statement.json 的既有体例：确定性字母映射，"
         "大写前置大写指示符，可逐字符核对。诚实边界：本转写未经盲文使用者或持证"
         "校对员校对；中文现行盲文的机器转写错误风险高，本图不以机器转写充数，"
         "中文盲文版与核心声明同属待专业协作项。" % BRAILLE_TEXT)
BR_EN = ("The braille title (English UEB Grade 1, letter by letter) reads “%s”. Rule and "
         "mapping table follow visual/assets/braille-core-statement.json: a deterministic "
         "letter map with a capital indicator, checkable character by character. Honest "
         "boundary — not proofread by a braille user or certified transcriber; no machine "
         "transcription of Chinese braille is offered." % BRAILLE_TEXT)

# 线位是从包内 OSM 快照法线取样加密而来（见 roads.geojson 的 densification 字段），
# 属 ODbL 衍生数据；本图虽不铺底图，署名仍须随线位走。
ODBL = ("线位取样自包内 OpenStreetMap 快照 osm-fabric-snapshot-20260815（见 roads.geojson "
        "的 densification 字段），底层数据 © OpenStreetMap 贡献者，ODbL 1.0 · Alignments "
        "sampled from the in-package OpenStreetMap snapshot; data © OpenStreetMap "
        "contributors, ODbL 1.0")

FOOT_ZH = ("概念示意 · 非法定规划 · 非工程线位 · 三处重点区为公告约值临时框线。"
           "横向接口与底图路网在触觉版中一律略去——触觉可读性优先于信息完整性，"
           "完整线位见 assets/figures/site-overview.png 与核验图 02。")
FOOT_EN = ("Concept only · not a statutory plan · not an engineering alignment · the three "
           "key areas are provisional boxes. Cross interfaces and the basemap road network "
           "are omitted here: legibility by touch outranks completeness; the full set is on "
           "assets/figures/site-overview.png and verification sheet 02.")


def build():
    br_svg, br_w = braille_svg(BRAILLE_TEXT, 0.0, MM(BR_DOT_MM))
    legend = "".join(
        '<div class="lg"><span class="lm">%s</span><span class="lt">'
        '<b>%s</b><em>%s</em></span></div>' % (legend_svg(k), esc(zh), esc(en))
        for k, zh, en in LEGEND)
    return f"""<!doctype html><html lang="zh"><head><meta charset="utf-8">
<title>tactile-corridor-map</title><style>__FONT__
*{{box-sizing:border-box}}html,body{{margin:0;padding:0}}
body{{width:{W}px;height:{H}px;overflow:hidden;background:{C['paper']};
color:{C['ink']};font-family:SHS;-webkit-font-smoothing:antialiased;
text-rendering:geometricPrecision}}
.hd{{height:84px;background:{C['deep']};color:#fff;padding:12px {PAD}px 0;
display:flex;justify-content:space-between;align-items:flex-start}}
.hd .k{{font-size:12px;letter-spacing:.16em;color:{C['onDarkEn']};font-weight:700}}
.hd h1{{font-size:24px;font-weight:700;margin:7px 0 0;line-height:1.2}}
.hd h2{{font-size:13.5px;font-weight:400;margin:3px 0 0;color:{C['onDarkEn']};
line-height:1.2}}
.hd .r{{text-align:right}}
.hd .r .i{{font-size:12px;letter-spacing:.14em;font-weight:700}}
.pill{{display:inline-block;margin-top:9px;background:{C['coral']};color:#fff;
font-size:12px;padding:5px 12px;border-radius:11px;font-weight:700}}
.wrap{{padding:8px {PAD}px 0;height:{H - 84}px;display:flex;flex-direction:column}}
.band{{width:{BAND_W:.0f}px;height:{BAND_H:.0f}px;border:1px solid {C['edge']};
border-radius:3px;overflow:hidden;flex:none;background:{C['plate']}}}
.cap{{display:flex;justify-content:space-between;gap:16px;font-size:12px;
color:{C['muted']};margin-top:4px;flex:none}}
.cap b{{color:{C['teal']};font-weight:700;letter-spacing:.06em}}
.box{{border:1px solid {C['edge']};border-radius:3px;background:{C['plate']};
padding:7px 11px 8px;margin-top:5px;flex:none}}
.bk{{font-size:12px;letter-spacing:.12em;color:{C['teal']};font-weight:700}}
.lgs{{display:grid;grid-template-columns:repeat(4,1fr);gap:4px 14px;margin-top:5px}}
.lg{{display:flex;align-items:center;gap:8px}}
.lm{{flex:none;display:flex;align-items:center;line-height:0}}
.lt b{{display:block;font-size:11.5px;font-weight:700;color:{C['ink']};line-height:1.2}}
.lt em{{display:block;font-size:10.5px;font-style:normal;color:{C['muted']};
line-height:1.2}}
.brs{{display:grid;grid-template-columns:262px 1fr 1fr;gap:14px;align-items:start;
margin-top:5px}}
.br{{line-height:0;padding-top:2px}}
.brt{{font-size:10.5px;color:{C['muted']};line-height:1.32}}
.brt.zh{{color:{C['ink']}}}
.notes{{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-top:5px;
border-top:1px solid {C['edge']};padding-top:6px;flex:none}}
.note p{{margin:0;font-size:10px;line-height:1.3}}
.note .zh{{color:{C['ink']}}}
.note .en{{color:{C['muted']};margin-top:3px}}
.ft{{margin-top:auto;padding:4px 0 4px;border-top:1px solid {C['edge']};
font-size:10px;color:{C['muted']};line-height:1.28;flex:none}}
.ft .r{{color:{C['deep']};font-weight:700}}
</style></head><body>
<div class="hd">
  <div><div class="k">EVERY SENSE JING-ZHANG · TACTILE PRINT MASTER</div>
  <h1>全带触觉走廊图 · 主脊、安静线与十个完成点</h1>
  <h2>Tactile corridor map — the spine, the quiet alternative and ten completion
  points, for embossing or swell paper</h2></div>
  <div class="r"><div class="i">TACTILE / T-01</div>
  <div class="pill">触觉印刷原稿 · 概念示意 / TACTILE MASTER · CONCEPT</div></div>
</div>
<div class="wrap">
  <div class="band">{band_svg()}</div>
  <div class="cap"><span><b>CORRIDOR · TOUCH EDITION</b> 走廊全域 · 图面旋转 90°，
    北向右 · 1 CSS px ≈ {MPP:.1f} m · 纵向仅平移裁切，未作缩放</span>
    <span>rotated 90°, north to the right · cropped vertically, never rescaled</span></div>
  <div class="box"><div class="bk">TACTILE LEGEND / 触觉图例 ·
    与图面同尺寸同线宽，可直接摸读</div>
    <div class="lgs">{legend}</div></div>
  <div class="box"><div class="bk">BRAILLE TITLE / 盲文标注区</div>
    <div class="brs">
      <div class="br"><svg
        viewBox="0 0 {br_w + 4:.1f} {MM(BR_DOT_MM) * 2 + MM(BR_DY_MM) * 2:.1f}"
        width="{br_w + 4:.1f}" height="{MM(BR_DOT_MM) * 2 + MM(BR_DY_MM) * 2:.1f}"
        >{br_svg}</svg></div>
      <div class="brt zh">{esc(BR_ZH)}</div>
      <div class="brt">{esc(BR_EN)}</div>
    </div>
  </div>
  <div class="notes">
    <div class="note">
      <p class="zh">{esc(SIMPLIFY_ZH)}</p>
      <p class="en">{esc(SIMPLIFY_EN)}</p>
    </div>
    <div class="note">
      <p class="zh">{esc(SPEC_ZH)}</p>
      <p class="en">{esc(SPEC_EN)}</p>
    </div>
  </div>
  <div class="ft">{esc(FOOT_ZH)} <span class="r">WGS84 / EPSG:4326 ·
  geometry/roads.geojson · geometry/constraints.geojson · geometry/key_areas.geojson</span>
  <br>{esc(FOOT_EN)}<br>{esc(ODBL)}</div>
</div>
</body></html>"""


def main():
    html = build()
    face = suppfont.full_face_css(html.replace("__FONT__", ""))
    hp = os.path.join(HERE, "tactile-corridor-map.html")
    with open(hp, "w", encoding="utf-8") as f:
        f.write(html.replace("__FONT__", face))
    out = os.path.join(HERE, "tactile-corridor-map.raw.png")
    r = subprocess.run(["node", RENDER, "png", hp, out, str(W), str(H), DSF],
                       capture_output=True, text=True)
    if r.returncode:
        raise SystemExit(r.stderr)
    print("ok", os.path.getsize(out) // 1024, "KB raw")
    for k, v in GEN.items():
        print("  ", k, v)
    print("   节点最小净间距 %.2f mm" % NODE_MIN_MM)
    print("   盲文", BRAILLE_UNICODE)


if __name__ == "__main__":
    main()
