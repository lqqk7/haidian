# -*- coding: utf-8 -*-
"""assets/figures/bluegreen-structure.png —— 蓝绿三层结构与节点雨洪类型。

关系图，不是平面图：三条水平层带（BG-L1／L2／L3）自上而下并置，层间以带向箭头挂
三条关系判据（BG-R1／R2／R3），十个独立完成点在 BG-L2 带内按三类铺装径流去向打点，
右栏给「雨天断点」三类成因各自指向哪一件设施，底栏给三类类型判据全称。

全部文字与结构直读 visual/assets/sensory-design-code.json 的 bluegreen_stormwater
一节，不另编：三层的载体与职能、三条层间判据、三类 DR 判据与十节点归类、三类断点
成因与指向，逐条对应该文件的既有字段；图面短句只对既有字段做压缩，不新增主张。
图上不出现任何容积、渗透系数、溢流标高、管径与照度数值——该文件自身即声明这五项
一律为现场核定条件。

版面纪律：输出 3000 × 1875，接收分辨率短边 768 像素的重采样比 0.4096，故 CSS 字号
下限取 12 px（等效 12.29 px），与 v8.2 片区策略图版同一口径。该下限把整幅图的可用
文本行数封在约 48 行以内，因此每条中英短句都按所在栏宽压到单行，超出即改写。
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
         coral="#a8452f", purple="#5a4b86", river="#2f6f8a")
DRC = {"DR-A": C["teal"], "DR-B": C["coral"], "DR-C": C["purple"]}


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


D = json.load(open(DATA, encoding="utf-8"))["bluegreen_stormwater"]
LAYERS = {x["layer_id"]: x for x in D["three_layers"]}
RELS = {x["relation_id"]: x for x in D["layer_relations"]}
TYPES = {x["type_id"]: x for x in D["node_drainage_types"]["types"]}
ASSIGN = D["node_drainage_types"]["assignment"]

LAYER_TEXT = {
    "BG-L1": dict(
        cz="GREEN-001 · GREEN-002 · GREEN-003（spine_greenway）→ 挂 ROAD-001",
        ce="GREEN-001 · GREEN-002 · GREEN-003 (spine_greenway), referencing ROAD-001",
        fz="连续通行面的绿化基底与非 AI 信息底线的载体；不承担景观展示职能。",
        fe="Planting base of the continuous passage and carrier of the non-AI "
           "information baseline; not a display function."),
    "BG-L2": dict(
        cz="GREEN-004 · GREEN-005 · GREEN-006（low_stimulation_buffer）→ 挂 ROAD-005；"
           "十个独立完成点所落的十处 PUBLIC 面",
        ce="GREEN-004 · 005 · 006 (low_stimulation_buffer), referencing ROAD-005; "
           "plus the ten PUBLIC features under the ten nodes",
        fz="降低声光暴露、提供安静停留与恢复；不以绿地率或覆盖率衡量，与主脊绿带各自独立成立。",
        fe="Lowers light and noise exposure and allows quiet dwelling; not a green "
           "ratio; stands independent of the spine belt."),
    "BG-L3": dict(
        cz="清河（众智园方向）· 小月河（同名场景赋能翼水系）—— 虚线为概念性联系，不表示蓝线",
        ce="Qinghe (towards Zhongzhiyuan) and Xiaoyuehe — dashed: a conceptual "
           "relation, not a blue line",
        fz="本层不承担任何工程职能；蓝线、防洪、生态与文保条件未核验前不提出工程处理。",
        fe="No engineering function; with the blue line, flood control, ecology and "
           "heritage unverified, no works are proposed."),
}

REL_TEXT = {
    "BG-R1": ("低刺激替代线的绿化缓冲不得由主脊绿带代偿；任一条在某段被压缩，该段即判不成立。",
              "The quiet route's buffer may not be substituted by the spine belt; where "
              "either is squeezed on a segment, that segment fails."),
    "BG-R2": ("雨水去向以就地滞留为先、市政衔接为后；蓝线与防洪核验前不提出任何直接排放。",
              "Retention on site first, utility connection second; no direct discharge "
              "before the blue line and flood control are verified."),
    "BG-R3": ("只登记概念性联系：不提滨水贯通线位、不标注蓝线、不推断生态廊道宽度。",
              "Conceptual relation only: no waterfront alignment, no blue line, no "
              "ecological corridor width."),
}

BREAKS = [
    ("积水", "Ponding",
     "指向该段滞留带容积与溢流标高、通行面横坡方向——三者均为现场核定条件，读数产出后按段回填。",
     "Points to that segment's retention volume and overflow level and to the "
     "cross-fall direction — all site-verification conditions."),
    ("湿滑", "Slip surface",
     "指向铺装材料判据（透水防滑、平整连续、反光受控）；断点一经登记即为该段判据未成立的现场证据。",
     "Points to the paving criterion — permeable, slip-resistant, level, continuous, "
     "glare-controlled. A registered break is site evidence."),
    ("排水口阻挡轮椅", "Grate blocking a wheelchair",
     "指向线性排水沟位置与盖板方向，以及滞留带与通行面之间的可探知边界；与触觉带读数同处合并登记。",
     "Points to the channel's position and grating orientation and to the detectable "
     "edge; joined with the tactile reading, never double counted."),
]

ZERO_ZH = "六项空间审计读数当前全部为零值。本对应关系不产出读数，只答「断点之后该看哪一件设施」。"
ZERO_EN = ("All six spatial-audit readings are currently zero. The correspondence "
           "produces no reading: it says which feature to inspect, never how many "
           "breaks there ought to be.")

MASTER_ZH = "OP-04 · 母版：本节点排水取值已逐项核定，是其余节点取用 DR-B 的来源，不是由 DR-B 推得。"
MASTER_EN = ("OP-04 holds the master card: its drainage values are settled item by item "
             "and are the source from which DR-B is taken, not a result of it.")

FOOT_ZH = ("类型判据，非工程参数；现场核定前不构成工程结论。图上不出现容积、渗透系数、溢流标高、"
           "管径与照度的任何数值；本图为关系图，层带与打点不表示位置、长度、面积或比例。")
FOOT_EN = ("Type criteria, not engineering parameters; before field verification these are "
           "not engineering conclusions. No volume, infiltration coefficient, overflow "
           "level, pipe size or illuminance value appears here, and as a relational diagram "
           "the bands and dots carry no position, length, area or scale.")


def layer_block(lid, dashed=False):
    L, t = LAYERS[lid], LAYER_TEXT[lid]
    col = {"BG-L1": C["teal"], "BG-L2": C["deep"], "BG-L3": C["river"]}[lid]
    border = ("2px dashed %s" % col) if dashed else ("1px solid " + C["edge"])
    nodes = ""
    if lid == "BG-L2":
        chips = "".join('<span class="np" style="background:%s">%s</span>'
                        % (DRC[a["drainage_type"]], esc(a["node_id"])) for a in ASSIGN)
        nodes = ('<div class="nrow">%s</div>'
                 '<div class="mst"><b>%s</b><span>%s</span></div>'
                 % (chips, esc(MASTER_ZH), esc(MASTER_EN)))
    return ('<div class="ly" style="border:%s">'
            '<div class="lh"><span class="lid" style="background:%s">%s</span>'
            '<b>%s</b><em>%s</em></div>'
            '<p class="cr">%s<span>%s</span></p>'
            '<p class="fn">%s<span>%s</span></p>%s</div>'
            % (border, col, esc(lid), esc(L["name_zh"]), esc(L["name_en"]),
               esc(t["cz"]), esc(t["ce"]), esc(t["fz"]), esc(t["fe"]), nodes))


def rel_block(rid):
    zh, en = REL_TEXT[rid]
    return ('<div class="rl"><div class="rh">'
            '<span class="rid">%s</span><span class="rp">%s</span>'
            '<span class="rz">%s</span></div><div class="re">%s</div></div>'
            % (esc(rid), esc("↕ " + RELS[rid]["pair"]), esc(zh), esc(en)))


def type_block(tid):
    T_ = TYPES[tid]
    ids = [a["node_id"] for a in ASSIGN if a["drainage_type"] == tid]
    return ('<div class="ty"><div class="th">'
            '<span class="tid" style="background:%s">%s</span>'
            '<span class="tn">%s</span></div>'
            '<div class="tno" style="color:%s">%s</div>'
            '<div class="ten">%s</div></div>'
            % (DRC[tid], esc(tid), esc(T_["name_zh"]), DRC[tid],
               esc(" · ".join(ids)), esc(T_["name_en"])))


def build():
    layers = (layer_block("BG-L1") + rel_block("BG-R1") + layer_block("BG-L2")
              + rel_block("BG-R2") + layer_block("BG-L3", dashed=True)
              + rel_block("BG-R3"))
    brk = "".join('<div class="bk"><div class="bh"><b>%s</b><em>%s</em></div>'
                  '<p>%s<span>%s</span></p></div>' % (esc(a), esc(b), esc(c), esc(d))
                  for a, b, c, d in BREAKS)
    types = "".join(type_block(t) for t in ("DR-A", "DR-B", "DR-C"))
    return f"""<!doctype html><html lang="zh"><head><meta charset="utf-8">
<title>bluegreen-structure</title><style>__FONT__
*{{box-sizing:border-box}}html,body{{margin:0;padding:0}}
body{{width:{W}px;height:{H}px;overflow:hidden;background:{C['paper']};
color:{C['ink']};font-family:SHS;font-size:12px;line-height:1.3;
-webkit-font-smoothing:antialiased;text-rendering:geometricPrecision}}
.hd{{height:72px;background:{C['deep']};color:#fff;padding:9px {PAD}px 0;
display:flex;justify-content:space-between;align-items:flex-start}}
.hd .k{{font-size:12px;letter-spacing:.13em;color:{C['onDark']};font-weight:700}}
.hd h1{{font-size:22px;font-weight:700;margin:4px 0 0;line-height:1.14}}
.hd h2{{font-size:13px;font-weight:400;margin:2px 0 0;color:{C['onDark']};line-height:1.14}}
.hd .r{{text-align:right}}
.hd .r .i{{font-size:12px;letter-spacing:.12em;font-weight:700}}
.pill{{display:inline-block;margin-top:7px;background:{C['coral']};color:#fff;
font-size:12px;padding:4px 11px;border-radius:11px;font-weight:700;white-space:nowrap}}
.wrap{{padding:7px {PAD}px 0;height:{H - 72}px;display:flex;flex-direction:column}}
.main{{display:flex;gap:11px;flex:none}}
.left{{width:800px;display:flex;flex-direction:column;gap:4px}}
.ly{{background:{C['plate']};border-radius:3px;padding:4px 8px 5px;flex:none}}
.lh{{display:flex;align-items:baseline;gap:7px}}
.lid{{color:#fff;font-weight:700;font-size:12px;padding:2px 7px;border-radius:3px;
letter-spacing:.03em}}
.lh b{{font-size:15px;font-weight:700;color:{C['deep']}}}
.lh em{{font-size:12px;font-style:normal;color:{C['muted']}}}
.ly p{{margin:2px 0 0;white-space:nowrap;overflow:hidden}}
.ly p span{{display:block;color:{C['muted']}}}
.cr{{color:{C['deep']};font-weight:700}}
.nrow{{display:flex;gap:5px;margin-top:5px}}
.np{{color:#fff;font-weight:700;font-size:12px;padding:3px 0;border-radius:3px;
width:71px;text-align:center}}
.mst{{margin-top:4px;border-top:1px dashed {C['edge']};padding-top:3px;
white-space:nowrap;overflow:hidden}}
.mst b{{font-weight:700;color:{C['coral']}}}
.mst span{{display:block;color:{C['muted']}}}
.rl{{padding:0 8px;flex:none}}
.rh{{display:flex;align-items:baseline;gap:7px;white-space:nowrap}}
.rid{{background:{C['coral']};color:#fff;font-weight:700;font-size:12px;padding:2px 7px;
border-radius:3px;flex:none}}
.rp{{font-weight:700;color:{C['coral']};flex:none}}
.rz{{color:{C['ink']};font-weight:700;overflow:hidden}}
.re{{color:{C['muted']};white-space:nowrap;overflow:hidden}}
.right{{flex:1;border:1px solid {C['edge']};border-radius:3px;background:{C['plate']};
padding:5px 9px 6px;display:flex;flex-direction:column}}
.right h3{{margin:0;font-size:13px;font-weight:700;color:{C['deep']};line-height:1.2}}
.right h3 em{{display:block;font-size:12px;font-style:normal;font-weight:400;
color:{C['muted']};line-height:1.2}}
.bk{{margin-top:6px;border-left:3px solid {C['river']};padding-left:7px}}
.bh b{{font-weight:700;color:{C['river']}}}
.bh em{{font-style:normal;color:{C['muted']};margin-left:5px}}
.bk p{{margin:1px 0 0}}
.bk p span{{display:block;color:{C['muted']}}}
.zero{{margin-top:auto;border-top:1px solid {C['edge']};padding-top:4px;
color:{C['coral']};font-weight:700}}
.zero span{{display:block;color:{C['muted']};font-weight:400}}
.dr{{margin-top:6px;border-top:1px solid {C['edge']};padding-top:4px;flex:none}}
.dhd{{font-size:13px;font-weight:700;color:{C['deep']};line-height:1.2}}
.dhd em{{font-style:normal;font-weight:400;color:{C['muted']};font-size:12px}}
.dcols{{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-top:3px}}
.th{{display:flex;align-items:baseline;gap:6px}}
.tid{{color:#fff;font-weight:700;font-size:12px;padding:2px 6px;border-radius:3px}}
.tn{{font-weight:700;font-size:12px;color:{C['deep']}}}
.tno{{font-weight:700;margin-top:1px;letter-spacing:.01em}}
.ten{{color:{C['muted']};margin-top:1px}}
.ft{{margin-top:auto;padding:4px 0 5px;border-top:1px solid {C['edge']};
color:{C['muted']};line-height:1.28;flex:none;display:flex;gap:14px}}
.ft .l{{flex:1}}
.ft .s{{width:250px;text-align:right;color:{C['deep']};font-weight:700}}
</style></head><body>
<div class="hd">
  <div><div class="k">EVERY SENSE JING-ZHANG · BLUE-GREEN THREE LAYERS &amp; NODE DRAINAGE TYPES</div>
  <h1>蓝绿三层结构与节点雨洪类型</h1>
  <h2>Blue-green three-layer structure and the drainage type of each of the ten nodes</h2></div>
  <div class="r"><div class="i">DIAGRAM / BG-01</div>
  <div class="pill">关系图 · 非平面图 / RELATIONAL DIAGRAM · NOT A PLAN</div></div>
</div>
<div class="wrap">
  <div class="main">
    <div class="left">{layers}</div>
    <div class="right"><h3>「雨天断点」三类成因 → 指向哪一件设施<em>The three causes of a
    wet-weather break and the feature each points to</em></h3>{brk}
    <div class="zero">{esc(ZERO_ZH)}<span>{esc(ZERO_EN)}</span></div></div>
  </div>
  <div class="dr">
    <div class="dhd">十节点铺装径流去向 · 三类类型判据全称
    <em>Paving runoff at the ten nodes — the full name of each of the three type criteria</em></div>
    <div class="dcols">{types}</div>
  </div>
  <div class="ft"><div class="l">{esc(FOOT_ZH)}<br>{esc(FOOT_EN)}</div>
  <div class="s">数据直读 visual/assets/<br>sensory-design-code.json ·
  bluegreen_stormwater</div></div>
</div>
</body></html>"""


def main():
    html = build()
    face = suppfont.full_face_css(html.replace("__FONT__", ""))
    hp = os.path.join(HERE, "bluegreen-structure.html")
    with open(hp, "w", encoding="utf-8") as f:
        f.write(html.replace("__FONT__", face))
    out = os.path.join(HERE, "bluegreen-structure.raw.png")
    r = subprocess.run(["node", RENDER, "png", hp, out, str(W), str(H), DSF],
                       capture_output=True, text=True)
    if r.returncode:
        raise SystemExit(r.stderr)
    print("ok dsf=%s %d KB raw" % (DSF, os.path.getsize(out) // 1024))


if __name__ == "__main__":
    main()
