# -*- coding: utf-8 -*-
"""assets/figures/heritage-sequence.png —— 百年遗产解说序列。

自北向南的序列轴（北在上，与全带图一致）：HS-1 众智园工程起点 → HS-2 原点社区生活
变迁 → HS-3 大钟寺转运与采用。每段三栏——叙事一句、绑定节点与地标、解说载体图标组
（全部标为包内既有交付物）；轴上显式画出「可停 / 可跳过 / 可重复」三操作态；底栏给
遗存材料再利用的四条类型判据 MR-1—MR-4。

全部文字与结构直读 visual/assets/sensory-design-code.json 的 heritage_interpretation
一节，不另编：三段的名称、叙事、绑定节点与地标、载体清单、四条材料判据与边界声明，
逐条对应该文件的既有字段；图面短句只对既有字段做压缩，不新增任何史实主张。
图上不出现文保等级、保护范围、控制线与线路复原，也不引用未经核验的站场史实——
历史锚点一律留在正文，图上只印其纪律。
"""
from __future__ import annotations
from pathlib import Path as _HaidianPath

import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
T = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(T, "w81-basemap"))

import suppfont                 # noqa: E402

RENDER = os.path.join(T, "wp4b/render.js")
PKG = (str(_HaidianPath(__file__).resolve().parents[3] / 'submissions/lqqk7') + "/"
       "every-sense-jingzhang")
DATA = os.path.join(PKG, "visual/assets/sensory-design-code.json")
W, H, PAD = 1200, 750, 30
DSF = os.environ.get("W90_DSF", "2.5")

C = dict(deep="#10383d", teal="#177c78", ink="#17383c", muted="#68787b",
         paper="#f2efe7", plate="#ffffff", edge="#e2ddd0", onDark="#9ecdc7",
         coral="#a8452f", purple="#5a4b86", river="#2f6f8a", gold="#8a5a00")
SEGC = {"HS-1": C["teal"], "HS-2": C["purple"], "HS-3": C["coral"]}

LAND_EN = {"common_gauge_gate": "Common Gauge Gate",
           "every_sense_origin": "Every Sense Origin",
           "hundred_sense_forum": "Hundred-Sense Forum"}
LAND_ZH = {"common_gauge_gate": "共轨门", "every_sense_origin": "万感原点",
           "hundred_sense_forum": "百感台"}
PUB = {"HS-1": "PUBLIC-003", "HS-2": "PUBLIC-006", "HS-3": "PUBLIC-008"}
AREA = {"HS-1": ("众智园（北）", "Zhongzhiyuan, north"),
        "HS-2": ("AI 原点社区（中）", "AI Origin Community, middle"),
        "HS-3": ("大钟寺（南）", "Dazhongsi, south")}


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


D = json.load(open(DATA, encoding="utf-8"))["heritage_interpretation"]
SEGS = {x["segment_id"]: x for x in D["segments"]}
MR = D["material_reuse_criteria"]["criteria"]

# 叙事一句：对各段 narrative_zh／narrative_en 首句的压缩，不新增主张。
NARR = {
    "HS-1": ("一条线路如何在坡度面前承认「上不去就要退回来」，并把退回变成前进的一部分。",
             "How a line, faced with a gradient, admitted that what cannot be climbed "
             "must be backed out of."),
    "HS-2": ("同一条线旁边的日常如何变化；只取口述层与当代使用层，不讲功绩，不虚构言论。",
             "How daily life alongside the same line changed, drawn only from the oral "
             "and contemporary-use layers."),
    "HS-3": ("同一批东西如何从轨道一侧到达另一侧，又如何被人采用——转运与采用是同一动作的两端。",
             "How the same goods reach one side of the tracks from the other and are "
             "then taken up."),
}

# 载体图标组：取各段 carriers／carriers_en 的中心名词，图标键与名词一一对应。
CARRIERS = {
    "HS-1": [("band", "触觉文化带", "Tactile culture band"),
             ("plaque", "铸刻导视", "Cast signage"),
             ("wave", "三通道解说", "Three-channel interpretation"),
             ("hand", "实体模型", "Physical models")],
    "HS-2": [("plaque", "万感原点记录墙", "Origin public record wall"),
             ("wave", "声音档案", "Sound archive"),
             ("wave", "手语与字幕", "Sign language and captions"),
             ("hand", "易读文本与纸质流程", "Easy-read text, paper steps")],
    "HS-3": [("plaque", "百感台记录面", "Forum record face"),
             ("plaque", "铸刻导视与可更换牌面", "Cast signage, replaceable panels"),
             ("wave", "音频导览与字幕", "Audio guidance with captions"),
             ("hand", "服务桌四位序人工解说", "In-person at the service desk")],
}

MR_SHORT = [
    ("结构安全核定前只做展示性再利用：不承重、不作通行面、不作可登临构件。",
     "Display only before structural verification: no load-bearing or climbable "
     "use."),
    ("不得标注保护范围、等级或控制线；再利用构件上的文字亦不得出现该类表述。",
     "No protection extent, grade or control line marked, on any component."),
    ("三条可核对下限：不减通行净宽、不产生新的高差断点、不带尖锐边缘与积水凹陷。",
     "No loss of clear width, no new level break, no sharp edge or standing "
     "water."),
    ("轨槽口须填平或改向；道砟不得可推入通行面，也不替代触觉铺装；站台构件须留可探知边界。",
     "Flangeways filled or turned aside; ballast kept off passages; edges "
     "detectable."),
]

ICON = {
    "band": ('<svg viewBox="0 0 20 20"><rect x="1.5" y="5" width="17" height="10" rx="2" '
             'fill="none" stroke="%s" stroke-width="1.6"/>'
             + "".join('<circle cx="%.1f" cy="%.1f" r="1.15" fill="%%s"/>' % (x, y)
                       for y in (8.2, 11.8) for x in (5, 8.4, 11.8, 15.2)) + '</svg>'),
    "plaque": ('<svg viewBox="0 0 20 20"><rect x="2.5" y="3.5" width="15" height="13" rx="1.5" '
               'fill="none" stroke="%s" stroke-width="1.6"/>'
               '<path d="M5.5 8h9M5.5 11h9M5.5 14h5.5" stroke="%s" stroke-width="1.5" '
               'fill="none" stroke-linecap="round"/></svg>'),
    "wave": ('<svg viewBox="0 0 20 20"><path d="M3 10h2.2M7 5.5v9M10.6 3v14M14.2 6.5v7M17.6 9v2" '
             'stroke="%s" stroke-width="1.8" fill="none" stroke-linecap="round"/></svg>'),
    "hand": ('<svg viewBox="0 0 20 20"><path d="M4.5 3.5h8.5l3 3v10h-11.5z" fill="none" '
             'stroke="%s" stroke-width="1.6" stroke-linejoin="round"/>'
             '<path d="M7.5 8.5h5M7.5 11.5h5M7.5 14h3" stroke="%s" stroke-width="1.5" '
             'fill="none" stroke-linecap="round"/></svg>'),
}


def icon(key, col):
    tpl = ICON[key]
    return tpl.replace("%s", col)


AXIS_ZH = "序列轴 · 自北向南（北在上，与全带图一致）；三段各认领一段叙事，互不重复。"
AXIS_EN = ("Sequence axis, north to south with north at the top as on the corridor "
           "plan; each strand takes one part of the narrative and none repeats another.")
OPS = [("可停", "Can stop"), ("可跳过", "Can skip"), ("可重复", "Can repeat")]
OPS_ZH = "轴上三操作态是既有主张，序列不改变它；任一段亦可单独进入。"
OPS_EN = ("The three states on the axis are the existing tactile-culture-band "
          "statement, unaltered; a strand may also be entered on its own.")

HS3_MARK_ZH = "转运只取空间含义，不引用未经核验的站场史实。"
HS3_MARK_EN = "Transfer takes its plain spatial sense; no station history is cited."

CARRIER_NOTE_ZH = "三段十二件解说载体全部为包内既有交付物，序列不新造载体。"
CARRIER_NOTE_EN = ("All twelve carriers already exist in the package; the sequence "
                   "invents none.")

MARK_ZH = ("结构安全核定前只做展示性再利用 · 不标注保护范围、等级或控制线 · "
           "材料来源、权属与许可须逐项清权后才可使用")
MARK_EN = ("Display reuse only before structural safety is verified · no protection "
           "extent, grade or control line marked · source and ownership cleared item "
           "by item before use")

FOOT_ZH = ("本图为解说组织建议，不是文物保护规划，也不构成史实结论；历史锚点只取正文已登记的"
           "公有领域通识史实，图上不新增史实主张、不做线路复原。")
FOOT_EN = ("This figure proposes how interpretation is organised: neither a conservation "
           "plan nor a conclusion about history. Its anchors are the public-domain facts "
           "already registered in the main text; it adds no historical claim here and "
           "reconstructs no alignment.")


def seg_block(sid, last=False):
    S = SEGS[sid]
    col = SEGC[sid]
    nz, ne = NARR[sid]
    az, ae = AREA[sid]
    chips = "".join(
        '<div class="cc"><span class="ci">%s</span>'
        '<span class="ct"><b>%s</b><em>%s</em></span></div>'
        % (icon(k, col), esc(z), esc(e)) for k, z, e in CARRIERS[sid])
    mark = ""
    if sid == "HS-3":
        mark = ('<div class="mk">%s<span>%s</span></div>'
                % (esc(HS3_MARK_ZH), esc(HS3_MARK_EN)))
    return ('<div class="sg">'
            '<div class="gut"><span class="sid" style="background:%s">%s</span>'
            '<span class="dot" style="background:%s"></span>'
            '<span class="gar"%s>↓</span></div>'
            '<div class="sbody">'
            '<div class="shd"><b>%s</b><em>%s</em>'
            '<span class="area">%s / %s</span></div>'
            '<div class="cols">'
            '<div class="c1"><div class="cl">叙事一句 / One sentence</div>'
            '<p>%s<span>%s</span></p>%s</div>'
            '<div class="c2"><div class="cl">绑定节点与地标 / Node</div>'
            '<div class="nd" style="background:%s">%s</div>'
            '<p><b>%s</b> <span class="lm">%s</span><span>%s</span></p></div>'
            '<div class="c3"><div class="cl">解说载体图标组 / Interpretation carriers</div><div class="chips">%s</div></div>'
            '</div></div></div>'
            % (col, esc(sid), col, ' style="visibility:hidden"' if last else '',
               esc(S["name_zh"]), esc(S["name_en"]), esc(az), esc(ae),
               esc(nz), esc(ne), mark,
               col, esc(S["bound_node"]),
               esc(LAND_ZH[S["bound_landmark"]]), esc(LAND_EN[S["bound_landmark"]]),
               esc(PUB[sid]), chips))


def build():
    ids = ("HS-1", "HS-2", "HS-3")
    segs = "".join(seg_block(s, s == ids[-1]) for s in ids)
    ops = "".join('<span class="op"><b>%s</b><em>%s</em></span>' % (esc(a), esc(b))
                  for a, b in OPS)
    mrs = "".join(
        '<div class="mr"><span class="mid">%s</span><p>%s<span>%s</span></p></div>'
        % (esc(m["criterion_id"]), esc(z), esc(e))
        for m, (z, e) in zip(MR, MR_SHORT))
    return f"""<!doctype html><html lang="zh"><head><meta charset="utf-8">
<title>heritage-sequence</title><style>__FONT__
*{{box-sizing:border-box}}html,body{{margin:0;padding:0}}
body{{width:{W}px;height:{H}px;overflow:hidden;background:{C['paper']};
color:{C['ink']};font-family:SHS;font-size:12px;line-height:1.3;
-webkit-font-smoothing:antialiased;text-rendering:geometricPrecision}}
svg{{width:15px;height:15px;display:block}}
.hd{{height:72px;background:{C['deep']};color:#fff;padding:9px {PAD}px 0;
display:flex;justify-content:space-between;align-items:flex-start}}
.hd .k{{font-size:12px;letter-spacing:.13em;color:{C['onDark']};font-weight:700}}
.hd h1{{font-size:22px;font-weight:700;margin:4px 0 0;line-height:1.14}}
.hd h2{{font-size:13px;font-weight:400;margin:2px 0 0;color:{C['onDark']};line-height:1.14}}
.hd .r{{text-align:right}}
.hd .r .i{{font-size:12px;letter-spacing:.12em;font-weight:700}}
.pill{{display:inline-block;margin-top:7px;background:{C['coral']};color:#fff;
font-size:12px;padding:4px 11px;border-radius:11px;font-weight:700;white-space:nowrap}}
.wrap{{padding:6px {PAD}px 0;height:{H - 72}px;display:flex;flex-direction:column}}
.ax{{display:flex;align-items:flex-start;gap:14px;background:{C['plate']};
border:1px solid {C['edge']};border-radius:3px;padding:4px 9px 5px;flex:none}}
.ax .n{{font-weight:700;color:{C['deep']};flex:none;text-align:center;line-height:1.1}}
.ax .n b{{display:block;font-size:15px}}
.ax .t{{width:822px;flex:none}}
.ax .t span{{display:block;color:{C['muted']}}}
.opw{{flex:1;text-align:right;padding-top:1px}}
.op{{display:inline-block;border:1px solid {C['teal']};border-radius:3px;
padding:1px 7px;margin-left:5px;text-align:center}}
.op b{{display:block;font-weight:700;color:{C['teal']}}}
.op em{{display:block;font-style:normal;color:{C['muted']}}}
.opn{{margin-top:2px;color:{C['muted']};text-align:right}}
.sg{{display:flex;gap:10px;background:{C['plate']};border:1px solid {C['edge']};
border-radius:3px;padding:2px 9px 3px;margin-top:3px;flex:none}}
.gut{{width:60px;flex:none;text-align:center}}
.sid{{display:block;color:#fff;font-weight:700;font-size:12px;padding:2px 0;
border-radius:3px;letter-spacing:.04em}}
.dot{{display:block;width:9px;height:9px;border-radius:50%;margin:4px auto 0}}
.gar{{display:block;color:{C['deep']};font-weight:700;line-height:1.1;margin-top:2px}}
.sbody{{flex:1}}
.shd{{display:flex;align-items:baseline;gap:7px}}
.shd b{{font-size:15px;font-weight:700;color:{C['deep']}}}
.shd em{{font-size:12px;font-style:normal;color:{C['muted']}}}
.area{{margin-left:auto;font-weight:700;color:{C['gold']}}}
.cols{{display:flex;gap:12px;margin-top:3px}}
.c1{{width:412px;flex:none}}
.c2{{width:186px;flex:none}}
.c3{{flex:1}}
.cl{{font-weight:700;color:{C['deep']};border-bottom:1px solid {C['edge']};
padding-bottom:1px;margin-bottom:2px}}
.c1 p{{margin:0;color:{C['ink']}}}
.c1 p span{{display:block;color:{C['muted']}}}
.mk{{margin-top:3px;border-left:3px solid {C['coral']};padding-left:6px;
color:{C['coral']};font-weight:700}}
.mk span{{display:block;color:{C['muted']};font-weight:400}}
.nd{{display:inline-block;color:#fff;font-weight:700;padding:1px 8px;border-radius:3px}}
.c2 p{{margin:2px 0 0}}
.c2 p b{{font-weight:700;color:{C['deep']}}}
.lm{{color:{C['muted']}}}
.c2 p span{{display:block;color:{C['muted']}}}
.chips{{display:grid;grid-template-columns:1fr;gap:0}}
.cc{{display:flex;align-items:flex-start;gap:5px}}
.ci{{flex:none;margin-top:2px}}
.ct b{{font-weight:700;color:{C['ink']}}}
.ct em{{font-style:normal;color:{C['muted']};margin-left:5px}}
.cn{{margin-top:4px;background:{C['plate']};border-left:3px solid {C['teal']};
padding:3px 8px;color:{C['deep']};font-weight:700;flex:none}}
.cn span{{color:{C['muted']};font-weight:400;margin-left:4px}}
.mrb{{margin-top:4px;border-top:1px solid {C['edge']};padding-top:3px;flex:none}}
.mhd{{font-size:13px;font-weight:700;color:{C['deep']};line-height:1.2}}
.mhd em{{font-style:normal;font-weight:400;color:{C['muted']};font-size:12px}}
.mcols{{display:grid;grid-template-columns:repeat(4,1fr);gap:9px;margin-top:2px}}
.mr{{border-left:3px solid {C['gold']};padding-left:7px}}
.mid{{font-weight:700;color:{C['gold']}}}
.mr p{{margin:0;color:{C['ink']}}}
.mr p span{{display:block;color:{C['muted']}}}
.mark{{margin-top:5px;background:{C['plate']};border-left:3px solid {C['coral']};
padding:2px 8px;color:{C['coral']};font-weight:700;flex:none}}
.mark span{{display:block;color:{C['muted']};font-weight:400}}
.ft{{margin-top:auto;padding:4px 0 5px;border-top:1px solid {C['edge']};
color:{C['muted']};line-height:1.28;flex:none;display:flex;gap:14px}}
.ft .l{{flex:1}}
.ft .s{{width:240px;text-align:right;color:{C['deep']};font-weight:700}}
</style></head><body>
<div class="hd">
  <div><div class="k">EVERY SENSE JING-ZHANG · CENTURY HERITAGE INTERPRETATION SEQUENCE</div>
  <h1>百年遗产解说序列</h1>
  <h2>The century heritage interpretation sequence — three strands along the spine, north to south</h2></div>
  <div class="r"><div class="i">DIAGRAM / HS-01</div>
  <div class="pill">解说组织建议 · 非文物保护规划 / INTERPRETATION ONLY · NOT A CONSERVATION PLAN</div></div>
</div>
<div class="wrap">
  <div class="ax">
    <div class="n"><b>北 ↑</b>NORTH</div>
    <div class="t">{esc(AXIS_ZH)} {esc(OPS_ZH)}<span>{esc(AXIS_EN)} {esc(OPS_EN)}</span></div>
    <div class="opw">{ops}</div>
  </div>
  {segs}
  <div class="cn">{esc(CARRIER_NOTE_ZH)} <span>{esc(CARRIER_NOTE_EN)}</span></div>
  <div class="mrb">
    <div class="mhd">遗存材料再利用的类型判据 · 轨道 / 道砟 / 站台构件
    <em>Type criteria for reusing remnant material — rails, ballast, platform components</em></div>
    <div class="mcols">{mrs}</div>
  </div>
  <div class="mark">{esc(MARK_ZH)}<span>{esc(MARK_EN)}</span></div>
  <div class="ft"><div class="l">{esc(FOOT_ZH)}<br>{esc(FOOT_EN)}</div>
  <div class="s">数据直读 visual/assets/<br>sensory-design-code.json ·
  heritage_interpretation</div></div>
</div>
</body></html>"""


def main():
    html = build()
    face = suppfont.full_face_css(html.replace("__FONT__", ""))
    hp = os.path.join(HERE, "heritage-sequence.html")
    with open(hp, "w", encoding="utf-8") as f:
        f.write(html.replace("__FONT__", face))
    out = os.path.join(HERE, "heritage-sequence.raw.png")
    r = subprocess.run(["node", RENDER, "png", hp, out, str(W), str(H), DSF],
                       capture_output=True, text=True)
    if r.returncode:
        raise SystemExit(r.stderr)
    print("ok dsf=%s %d KB raw" % (DSF, os.path.getsize(out) // 1024))


if __name__ == "__main__":
    main()
