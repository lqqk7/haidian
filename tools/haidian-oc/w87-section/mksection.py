# -*- coding: utf-8 -*-
"""assets/figures/green-section-principle.png —— 众智园段线性绿带原则性断面。

配合正文「一段真深化：众智园段线性绿带」的四行深化表（种什么 / 地形标高 /
雨水去向 / 夜间照明，proposal.md L661—668、proposal.en.md 同段）。图上四栏与
表中四行一一对应，用语取自正文，不引入正文以外的新主张。

断面不标尺寸数值：正文明确「宽度为相对关系示意，净宽、坡度与材质待专业团队
现场核定」，因此图上只画关系——基准面在哪、坡段落在哪一侧、溢流口相对于蓄水
位与通行面孰高孰低、暗区留在哪一段——每一条都能被园林、市政与照明专业直接反
驳，这正是它与效果图的区别。
"""
from __future__ import annotations

import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
T = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(T, "w81-basemap"))

import suppfont                 # noqa: E402

RENDER = os.path.join(T, "wp4b/render.js")
W, H, PAD = 1200, 750, 30
# 渲染倍率 2.0（2400x1500）不是随手取的：包体硬线 40 MiB，本波三张图版收口后
# 只剩约 180 KB 余量给后续登记文件。逐档实测（2.5 / 2.0 / 1.8 / 1.6 / 1.5）后，
# 2.0 是仍能让 10.5 px 图注在 100%% 查看下保持锐利、又能与另一张新图一并装进硬线
# 的最高一档；核验图组同样是按包体预算反解倍率（见 w81-basemap/mkverify.py）。
DSF = os.environ.get("W87_DSF", "2.0")

C = dict(deep="#10383d", teal="#177c78", coral="#d76450", purple="#6b5b95",
         sky="#4aa3c4", paper="#f2efe7", ink="#17383c", muted="#68787b",
         edge="#e2ddd0", onDarkEn="#9ecdc7", plate="#ffffff",
         greenF="#cbdcc6", greenS="#8fae8a", bldgF="#b7c2c0", bldgS="#8fa19e",
         soil="#e4dccb", soilS="#c9bfa8", gold="#d6a13b", rail="#7d8a88")

# 半透明叠加的预乘实色：底色已知（土体 / 绿带 / 白底 / 建筑体块），因此把 alpha
# 合成的结果直接写成实色，图面不变而量化调色板显著收敛，抖动噪点随之消失。
MIX = dict(green="#d6dcc8", water="#a1c6c7", rail="#b0b3a9",
           lampA="#f4e6cc", lampB="#ecd5a7", win="#dee3e2")

BW, BH = 1140.0, 315.0                 # 断面图带
# 横向分带（西 → 东）：建筑界面、安静线、绿带、轨道遗存带、绿带、主脊、建筑界面
X = dict(w_bldg=(0, 128), quiet=(128, 246), green_w=(246, 452),
         track=(452, 578), green_e=(578, 812), spine=(812, 992),
         e_bldg=(992, 1140))
# 图带分三层：上层留给关系式标注与引线，中层是断面本体，下层是分带名。
# 早期版本把标注压在断面里，六条标注与七个分带名在同一条带上互相叠印；
# 分层之后每条标注有自己的行位，引线负责指回它说明的构件。
ANNO_BOT = 140.0                       # 标注区下界
NAME_TOP = BH - 34.0                   # 分带名区上界
DATUM = 240.0                          # 轨面基准面 ±0.00
Y_QUIET = DATUM + 5.0                  # 安静线通行面（贴西侧现状）
Y_SPINE = DATUM - 17.0                 # 主脊通行面（贴东侧现状）
Y_WBASE = DATUM + 9.0                  # 西侧建筑地坪
Y_EBASE = DATUM - 21.0                 # 东侧建筑地坪
BLDG_H = 72.0
RET_BOT, RET_STORE, RET_OVER = 20.0, 13.0, 5.0   # 滞留槽底 / 设计蓄水位 / 溢流口
BOT = NAME_TOP                         # 剖面底


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def tx(x, y, s, size=11, fill=None, anchor="middle", weight=400, halo=3.0):
    return ('<text x="%.1f" y="%.1f" text-anchor="%s" font-size="%s" '
            'font-weight="%d" fill="%s" stroke="%s" stroke-width="%.1f" '
            'paint-order="stroke">%s</text>'
            % (x, y, anchor, size, weight, fill or C["ink"], C["plate"], halo, esc(s)))


def lead(x1, y1, x2, y2, col=None):
    return ('<path d="M %.1f,%.1f L %.1f,%.1f" fill="none" stroke="%s" '
            'stroke-width="1" stroke-dasharray="3 2.5"/>'
            % (x1, y1, x2, y2, col or C["muted"]))


def tree(cx, base, h, r, bare=False):
    """落叶阔叶乔木：左半画夏季冠、右半画冬季落叶枝形，一棵树说明两季。"""
    top = base - h
    g = ['<path d="M %.1f,%.1f L %.1f,%.1f" stroke="%s" stroke-width="3.4" '
         'fill="none" stroke-linecap="round"/>' % (cx, base, cx, top + r * 0.5,
                                                   "#8a7a5f")]
    if bare:
        for a, L in ((-58, 0.95), (-28, 1.0), (0, 0.85), (28, 1.0), (58, 0.95)):
            import math
            ax = cx + math.sin(math.radians(a)) * r * L
            ay = top + r * 0.55 - math.cos(math.radians(a)) * r * L * 0.72
            g.append('<path d="M %.1f,%.1f L %.1f,%.1f" stroke="%s" '
                     'stroke-width="1.6" fill="none" stroke-linecap="round"/>'
                     % (cx, top + r * 0.6, ax, ay, "#8a7a5f"))
    else:
        g.append('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="%s" '
                 'stroke="%s" stroke-width="1.4"/>'
                 % (cx, top + r * 0.62, r, r * 0.74, C["greenF"], C["greenS"]))
    return "".join(g)


def shrubs(x0, x1, y, n=7):
    g = []
    step = (x1 - x0) / (n + 1)
    for i in range(1, n + 1):
        x = x0 + step * i
        g.append('<path d="M %.1f,%.1f q 3.5,-7 7,0" fill="%s" stroke="%s" '
                 'stroke-width="1"/>' % (x - 3.5, y, C["greenF"], C["greenS"]))
    return "".join(g)


def lamp(cx, base, h, strong=False):
    """限眩光灯具：向下配光，无上射光；strong = 节点与人工求助点局部提高。"""
    top = base - h
    g = ['<path d="M %.1f,%.1f L %.1f,%.1f" stroke="%s" stroke-width="2" '
         'fill="none"/>' % (cx, base, cx, top, C["muted"]),
         '<path d="M %.1f,%.1f L %.1f,%.1f L %.1f,%.1f Z" fill="%s"/>'
         % (cx - 7, top, cx + 7, top, cx + 4, top + 5, C["muted"])]
    sp = 13 if strong else 8
    g.append('<path d="M %.1f,%.1f L %.1f,%.1f L %.1f,%.1f Z" fill="%s"/>'
             % (cx - 4, top + 5, cx - sp, base, cx + sp, base,
                MIX["lampB"] if strong else MIX["lampA"]))
    return "".join(g)


def section_svg():
    g = ['<svg viewBox="0 0 %.0f %.0f" width="%.0f" height="%.0f">' % (BW, BH, BW, BH),
         '<rect width="%.0f" height="%.0f" fill="%s"/>' % (BW, BH, C["plate"])]

    # ---- 土体剖面：一条连续地面线，东西高差全部由绿带内部长缓坡消化
    wb0, wb1 = X["w_bldg"]
    q0, q1 = X["quiet"]
    gw0, gw1 = X["green_w"]
    t0, t1 = X["track"]
    ge0, ge1 = X["green_e"]
    s0, s1 = X["spine"]
    eb0, eb1 = X["e_bldg"]
    RET_W = (gw0 + 22, gw0 + 92)          # 西绿带内的生物滞留带
    RET_E = (ge0 + 40, ge0 + 118)         # 东绿带内的生物滞留带

    ground = [
        (wb0, Y_WBASE), (wb1, Y_WBASE), (q0, Y_QUIET), (q1, Y_QUIET),
        (RET_W[0] - 10, Y_QUIET), (RET_W[0], Y_QUIET + RET_BOT),
        (RET_W[1], Y_QUIET + RET_BOT), (RET_W[1] + 14, Y_QUIET - 2),
        (gw1 - 6, DATUM), (t0, DATUM), (t1, DATUM),
        (RET_E[0] - 12, DATUM), (RET_E[0], DATUM + RET_BOT),
        (RET_E[1], DATUM + RET_BOT), (RET_E[1] + 16, DATUM - 3),
        (ge1 - 4, Y_SPINE), (s0, Y_SPINE), (s1, Y_SPINE),
        (eb0, Y_EBASE), (eb1, Y_EBASE),
    ]
    d = "M " + " L ".join("%.1f,%.1f" % p for p in ground)
    g.append('<path d="%s L %.1f,%.1f L %.1f,%.1f Z" fill="%s" stroke="none"/>'
             % (d, BW, BOT, 0, BOT, C["soil"]))
    g.append('<path d="%s" fill="none" stroke="%s" stroke-width="1.6"/>'
             % (d, C["soilS"]))

    # ---- 绿带填色（两段）
    for a, b in ((gw0, gw1), (ge0, ge1)):
        g.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s"/>'
                 % (a, DATUM - 6, b - a, BOT - DATUM + 6, MIX["green"]))

    # ---- 生物滞留带：槽体、设计蓄水位、溢流口与市政接口
    for (ra, rb), gy in ((RET_W, Y_QUIET), (RET_E, DATUM)):
        g.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s"/>'
                 % (ra, gy + RET_STORE, rb - ra, RET_BOT - RET_STORE,
                    MIX["water"]))
        g.append('<path d="M %.1f,%.1f L %.1f,%.1f" stroke="%s" stroke-width="1.4" '
                 'stroke-dasharray="5 3" fill="none"/>'
                 % (ra, gy + RET_STORE, rb, gy + RET_STORE, C["sky"]))
        g.append('<circle cx="%.1f" cy="%.1f" r="3.4" fill="%s"/>'
                 % (rb - 6, gy + RET_OVER, C["sky"]))
        g.append('<path d="M %.1f,%.1f L %.1f,%.1f L %.1f,%.1f" fill="none" '
                 'stroke="%s" stroke-width="2" stroke-dasharray="4 3" '
                 'marker-end="url(#aw)"/>'
                 % (rb - 6, gy + RET_OVER + 4, rb - 6, gy + RET_BOT + 10,
                    rb + 44, gy + RET_BOT + 10, C["sky"]))

    # ---- 轨道遗存带：保留轨面，与相邻通行面平接或可拆卸盖板
    g.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s"/>'
             % (t0, DATUM, t1 - t0, 15, MIX["rail"]))
    for rx in (t0 + 30, t1 - 30):
        g.append('<rect x="%.1f" y="%.1f" width="6" height="7" fill="%s"/>'
                 % (rx - 3, DATUM - 7, C["deep"]))
    g.append('<path d="M %.1f,%.1f L %.1f,%.1f" stroke="%s" stroke-width="2.4" '
             'stroke-dasharray="9 5" fill="none"/>'
             % (t0, DATUM, t1, DATUM, C["deep"]))
    # 基准面线，贯通全幅
    g.append('<path d="M 0,%.1f L %.1f,%.1f" stroke="%s" stroke-width="1" '
             'stroke-dasharray="2 4" fill="none"/>'
             % (DATUM, BW, DATUM, C["coral"]))
    g.append(tx(BW - 3, DATUM - 5, "±0.00 轨面基准面 / rail-top datum", 10.5,
                C["coral"], anchor="end", weight=700))

    # ---- 通行面：安静线（低刺激）与主脊（通用可达底线 + 触觉带）
    g.append('<rect x="%.1f" y="%.1f" width="%.1f" height="5.5" fill="%s"/>'
             % (q0, Y_QUIET - 5.5, q1 - q0, C["purple"]))
    g.append('<rect x="%.1f" y="%.1f" width="%.1f" height="5.5" fill="%s"/>'
             % (s0, Y_SPINE - 5.5, s1 - s0, C["teal"]))
    for i in range(9):                     # 主脊触觉带
        g.append('<rect x="%.1f" y="%.1f" width="4" height="3" fill="%s"/>'
                 % (s0 + 16 + i * 15, Y_SPINE - 9.6, C["deep"]))
    # 路面径流：两条通行面各自流向相邻滞留带
    for xa, xb, ya in ((q1 - 12, RET_W[0] + 16, Y_QUIET - 9),
                       (s0 + 6, RET_E[1] + 12, Y_SPINE - 13)):
        g.append('<path d="M %.1f,%.1f L %.1f,%.1f" fill="none" stroke="%s" '
                 'stroke-width="2" marker-end="url(#aw)"/>' % (xa, ya, xb, ya + 10,
                                                               C["sky"]))

    # ---- 长缓坡：坡段落在绿带内部，不落在两条通行面上
    for a, b, ya, yb in ((RET_W[1] + 14, gw1 - 6, Y_QUIET - 2, DATUM),
                         (RET_E[1] + 16, ge1 - 4, DATUM - 3, Y_SPINE)):
        g.append('<path d="M %.1f,%.1f L %.1f,%.1f" fill="none" stroke="%s" '
                 'stroke-width="3" stroke-linecap="round"/>'
                 % (a, ya, b, yb, C["coral"]))

    # ---- 建筑界面
    for a, b, base in ((wb0, wb1, Y_WBASE), (eb0, eb1, Y_EBASE)):
        g.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s" '
                 'stroke="%s" stroke-width="1.4"/>'
                 % (a, base - BLDG_H, b - a, BLDG_H, C["bldgF"], C["bldgS"]))
        for r in range(2):
            for c in range(3):
                g.append('<rect x="%.1f" y="%.1f" width="15" height="11" '
                         'fill="%s"/>'
                         % (a + 18 + c * 30, base - BLDG_H + 14 + r * 28,
                            MIX["win"]))

    # ---- 种植：乔木（夏冠 / 冬枝各一）与耐践踏地被
    g.append(tree(gw0 + 154, DATUM - 2, 96, 30))
    g.append(tree(ge0 + 172, DATUM - 4, 98, 31, bare=True))
    g.append(shrubs(RET_W[0], RET_W[1], Y_QUIET + RET_BOT - 1, 6))
    g.append(shrubs(RET_E[0], RET_E[1], DATUM + RET_BOT - 1, 6))
    g.append(shrubs(ge0 + 4, ge0 + 34, DATUM - 1, 3))

    # ---- 照明：通行面最低必要、节点局部提高、绿带内部暗区
    g.append(lamp(q0 + 30, Y_QUIET - 6, 62))
    g.append(lamp(s0 + 38, Y_SPINE - 6, 62))
    g.append(lamp(s1 - 30, Y_SPINE - 6, 74, strong=True))
    for cx in (gw0 + 56,):
        g.append('<path d="M %.1f,%.1f l 8,8 M %.1f,%.1f l -8,8" stroke="%s" '
                 'stroke-width="1.6" fill="none"/>'
                 % (cx - 4, DATUM - 40, cx + 4, DATUM - 40, C["deep"]))
        g.append(tx(cx, DATUM - 20, "暗区 / dark zone", 9.5, C["muted"], halo=2.5))

    # ---- 分带名称（贴图带底缘）
    NAMES = [
        (X["w_bldg"], "西侧建筑界面", "West building edge"),
        (X["quiet"], "安静替代线步行带", "Quiet-line walking surface"),
        (X["green_w"], "绿带 · 生物滞留带", "Green band · bioretention"),
        (X["track"], "轨道遗存带", "Preserved track band"),
        (X["green_e"], "绿带 · 生物滞留带 · 长缓坡", "Green band · bioretention · long gentle slope"),
        (X["spine"], "主脊通行带 · 触觉带", "Spine walking surface · tactile band"),
        (X["e_bldg"], "东侧建筑界面", "East building edge"),
    ]
    g.append('<path d="M 0,%.1f L %.1f,%.1f" stroke="%s" stroke-width="1"/>'
             % (NAME_TOP, BW, NAME_TOP, C["edge"]))
    for (a, b), zh, en in NAMES:
        cx = (a + b) / 2
        if a > 0:
            g.append('<path d="M %.1f,%.1f L %.1f,%.1f" stroke="%s" '
                     'stroke-width="1"/>' % (a, NAME_TOP, a, BH, C["edge"]))
        g.append(tx(cx, NAME_TOP + 14, zh, 11, C["ink"], weight=700, halo=0))
        g.append(tx(cx, NAME_TOP + 27, en, 9.5, C["muted"], halo=0))

    # ---- 关系式标注：全部落在标注区内，用引线指回所说明的构件。
    # 图上不出现任何尺寸数值——正文已声明宽度为相对关系示意，净宽、坡度与材质
    # 待现场核定；这里给的是「谁比谁高」「坡段落在哪一侧」这类可被专业反驳的关系。
    ANN = [
        (q0 + 58, 20, "通行面最低必要照度 · 限眩光与上射光",
         "walking surface: the minimum necessary, glare and uplight limited",
         C["gold"], (q0 + 30, Y_QUIET - 68)),
        (s0 + 118, 20, "节点与人工求助点局部提高",
         "raised locally at nodes and staffed help points",
         C["gold"], (s1 - 30, Y_SPINE - 84)),
        (gw0 + 78, 52, "溢流口高于设计蓄水位、低于相邻通行面",
         "overflow above the storage level, below the walking surface",
         C["sky"], (RET_W[1] - 6, Y_QUIET + RET_OVER)),
        (ge0 + 120, 52, "溢流后衔接市政雨水系统，不向轨道遗存带排放",
         "then on to the municipal system, never onto the track band",
         C["sky"], (RET_E[1] + 40, DATUM + RET_BOT + 10)),
        ((t0 + t1) / 2, 84, "轨面不覆土 · 平接或可拆卸盖板",
         "rail top not buried · flush or a removable cover plate",
         C["deep"], ((t0 + t1) / 2, DATUM - 8)),
        (ge0 + 250, 84, "长缓坡落在绿带内部，不用台阶与挡墙",
         "long gentle slope inside the green band, no steps or retaining walls",
         C["coral"], (RET_E[1] + 48, DATUM - 10)),
        (q0 + 48, 116, "安静线：无动态变色、呼吸灯与追光",
         "quiet line: no colour-changing or follow lighting",
         C["purple"], (q0 + 48, Y_QUIET - 8)),
        (gw0 + 154, 116, "落叶阔叶 · 夏季遮荫", "deciduous broadleaf, summer shade",
         C["greenS"], None),
        (ge0 + 172, 116, "冬季落叶不遮低角度阳光", "bare in winter, low sun kept",
         C["greenS"], None),
        (s0 + 92, 116, "主脊触觉带", "tactile band on the spine",
         C["teal"], (s0 + 92, Y_SPINE - 12)),
    ]
    for x, y, zh, en, col, tgt in ANN:
        if tgt:
            g.append(lead(x, y + 15.0, tgt[0], tgt[1], col))
        g.append(tx(x, y, zh, 10.5, col, weight=700, halo=2.5))
        g.append(tx(x, y + 11.0, en, 9.5, C["muted"], halo=2.5))
    g.append('<defs><marker id="aw" markerWidth="7" markerHeight="7" refX="5.4" '
             'refY="2.6" orient="auto"><path d="M 0,0 L 5.6,2.6 L 0,5.2 Z" '
             'fill="%s"/></marker></defs>' % C["sky"])
    g.append("</svg>")
    return "".join(g)


# --------------------------------------------------------------- 四栏深化表
COLS = [
    ("种什么", "What is planted", C["greenS"], [
        ("地被取耐践踏、耐旱、可按段更换的乡土草本与低矮灌木；乔木取落叶阔叶，"
         "夏季遮荫、冬季不遮低角度阳光",
         "Ground cover: native, trample- and drought-tolerant, replaceable in "
         "sections. Trees: deciduous, summer shade, bare in winter"),
        ("不用带尖刺、强致敏花粉或大量落果的类型——三类都直接压缩轮椅、推车与"
         "视障使用者的可用通行宽度",
         "No thorns, allergenic pollen or heavy fruit drop — all three narrow the "
         "usable clear width"),
    ], "树种、密度与土层厚度待调查后由园林专业确定",
        "Species, density and soil depth await soil, buried-services and "
        "existing-tree surveys"),
    ("地形标高", "Ground level", C["coral"], [
        ("以既有轨面为基准面，两侧不作整体抬填；过渡高差用长缓坡，坡段落在绿带"
         "内部而不落在通行面上",
         "The rail top is the datum, no wholesale raising or filling; level "
         "differences bridged by long gentle slopes inside the green band"),
        ("轨面不覆土，与相邻通行面平接或可拆卸盖板，绿化不产生新的高差断点",
         "The rail top is not buried; it meets the walking surface flush or "
         "through a removable cover plate"),
    ], "标高与高差待现场核定；框架见 GB 55019-2021",
        "Framed by GB 55019-2021 and the Barrier-Free Environment Law; datum and "
        "level difference field-verified"),
    ("雨水去向", "Where the water goes", C["sky"], [
        ("绿带内按段设生物滞留带承接两条通行面的径流；溢流口高于设计蓄水位、"
         "低于相邻通行面，溢流后接市政雨水系统",
         "Bioretention strips take run-off from both walking surfaces; each "
         "overflow sits above the storage level and below the surface"),
        ("不向轨道遗存带排放；滞留带边界以高差、材质与触觉提示三者并置，"
         "是可探知的边界而不是隐蔽的坑",
         "Never onto the track band; the edge combines level change, material "
         "change and a tactile cue, so it reads as detectable"),
    ], "滞留容积、溢流标高与接口位置待排水专业核验",
        "Retention volume, infiltration, overflow level and municipal connection "
        "await drainage review"),
    ("夜间照明", "Night lighting", C["gold"], [
        ("照度分三级：通行面取最低必要照度，节点与人工求助点局部提高，"
         "绿带内部保留暗区且不作景观投光",
         "Three grades: minimum on the walking surface, raised locally at nodes and "
         "help points, dark zones kept inside the green band"),
        ("灯具限制眩光与上射光；安静替代线全段不设动态变色、呼吸灯与随人触发的追光",
         "Luminaires limit glare and uplight; the quiet line carries no "
         "colour-changing, breathing or follow lighting"),
    ], "照度值、灯高、配光与色温待基线实测后确定",
        "Illuminance, mounting height, distribution and colour temperature await "
        "baseline measurement"),
]

NOTE_ZH = ("四项合起来只回答一个问题：这段绿带在 AI 关闭、天黑、下雨且有人坐在轮椅上的"
           "条件下是否仍然可用。四项都不是种植施工图，也不替代园林、市政与照明专业的"
           "正式设计；本图给出的是可被专业团队直接反驳的原则，而不是可被直接施工的图纸。"
           "断面不标尺寸数值——正文已声明宽度为相对关系示意，净宽、坡度与材质待现场核定。")
NOTE_EN = ("The four items together answer one question: is this stretch still usable with "
           "AI off, after dark, in the rain, by someone in a wheelchair. None of them is a "
           "planting drawing, and none replaces the formal work of landscape, utilities and "
           "lighting professionals — these are principles a team can reject point by point.")

FOOT_ZH = ("概念示意 · 非法定规划 · 非工程断面 · 尺寸待现场核定。图中四栏对应正文"
           "「一段真深化：众智园段线性绿带」的四行深化表，用语取自正文。")
FOOT_EN = ("Concept only · not a statutory plan · not an engineering section · dimensions "
           "subject to field verification. The four columns are the four rows of the "
           "worked-through table for the Zhongzhiyuan green band.")


def build():
    cols = "".join(
        '<div class="cd"><div class="ct" style="border-color:%s"><b>%s</b>'
        '<em>%s</em></div>%s<div class="cc">%s<br><span>%s</span></div></div>'
        % (col, esc(zh), esc(en),
           "".join('<p><b>%s</b><span>%s</span></p>' % (esc(a), esc(b))
                   for a, b in rows),
           esc(cz), esc(ce))
        for zh, en, col, rows, cz, ce in COLS)
    return f"""<!doctype html><html lang="zh"><head><meta charset="utf-8">
<title>green-section-principle</title><style>__FONT__
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
font-size:12px;padding:5px 12px;border-radius:11px;font-weight:700;
white-space:nowrap}}
.wrap{{padding:8px {PAD}px 0;height:{H - 84}px;display:flex;flex-direction:column}}
.band{{width:{BW:.0f}px;height:{BH:.0f}px;border:1px solid {C['edge']};
border-radius:3px;overflow:hidden;flex:none;background:{C['plate']}}}
.cap{{display:flex;justify-content:space-between;gap:16px;font-size:11.5px;
color:{C['muted']};margin-top:4px;flex:none}}
.cap b{{color:{C['teal']};font-weight:700;letter-spacing:.06em}}
.cols{{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-top:5px;
flex:none}}
.cd{{border:1px solid {C['edge']};border-radius:3px;background:{C['plate']};
padding:5px 9px 6px}}
.ct{{border-left:3px solid;padding-left:7px}}
.ct b{{display:block;font-size:13px;font-weight:700;color:{C['deep']};line-height:1.2}}
.ct em{{display:block;font-size:10px;font-style:normal;color:{C['muted']};
line-height:1.2}}
.cd p{{margin:4px 0 0}}
.cd p b{{display:block;font-size:10.5px;font-weight:700;color:{C['ink']};
line-height:1.25}}
.cd p span{{display:block;font-size:9.5px;color:{C['muted']};line-height:1.24}}
.cc{{margin-top:5px;padding-top:4px;border-top:1px dashed {C['edge']};
font-size:9.5px;color:{C['coral']};line-height:1.24;font-weight:700}}
.cc span{{color:{C['muted']};font-weight:400}}
.note{{margin-top:5px;border-top:1px solid {C['edge']};padding-top:4px;flex:none;
display:grid;grid-template-columns:1fr 1fr;gap:16px}}
.note p{{margin:0;font-size:10px;line-height:1.32}}
.note .en{{color:{C['muted']}}}
.ft{{margin-top:auto;padding:4px 0 6px;border-top:1px solid {C['edge']};
font-size:10px;color:{C['muted']};line-height:1.3;flex:none}}
.ft .r{{color:{C['deep']};font-weight:700}}
</style></head><body>
<div class="hd">
  <div><div class="k">EVERY SENSE JING-ZHANG · BLUE-GREEN PRINCIPLE SECTION</div>
  <h1>众智园段线性绿带 · 原则性断面</h1>
  <h2>Zhongzhiyuan linear green band — a principle section through the preserved
  track band and both walking surfaces</h2></div>
  <div class="r"><div class="i">SECTION / S-01</div>
  <div class="pill">概念示意 · 尺寸待现场核定 / CONCEPT · FIELD-VERIFIED</div></div>
</div>
<div class="wrap">
  <div class="band">{section_svg()}</div>
  <div class="cap"><span><b>SECTION · WEST TO EAST</b> 西→东 ·
    东西两侧现状高差在主脊各段中最大，高差全部由绿带内部长缓坡消化 ·
    图中无尺寸数值，宽度为相对关系示意</span>
    <span>west to east · no dimensions shown · widths are relative</span></div>
  <div class="cols">{cols}</div>
  <div class="note">
    <p class="zh">{esc(NOTE_ZH)}</p>
    <p class="en">{esc(NOTE_EN)}</p>
  </div>
  <div class="ft">{esc(FOOT_ZH)} <span class="r">proposal.md 蓝绿空间章 ·
  [depth:blue_green_public_space]</span><br>{esc(FOOT_EN)}</div>
</div>
</body></html>"""


def main():
    html = build()
    face = suppfont.full_face_css(html.replace("__FONT__", ""))
    hp = os.path.join(HERE, "green-section-principle.html")
    with open(hp, "w", encoding="utf-8") as f:
        f.write(html.replace("__FONT__", face))
    out = os.path.join(HERE, "green-section-principle.raw.png")
    r = subprocess.run(["node", RENDER, "png", hp, out, str(W), str(H), DSF],
                       capture_output=True, text=True)
    if r.returncode:
        raise SystemExit(r.stderr)
    print("ok dsf=%s %d KB raw" % (DSF, os.path.getsize(out) // 1024))


if __name__ == "__main__":
    main()
