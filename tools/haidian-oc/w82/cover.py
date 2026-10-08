# -*- coding: utf-8 -*-
"""交付 ①（A3 第 01 页）：封面由纯标题页改为「带 OSM 底图的总平面 + 判据 + 读数」。

原封面（WP-N2b）只有标题、副题与三条承诺，下半幅全空；而官方评审的 18 张视觉
输入里 PDF 只取第 1 页，这一页因此是全案最贵的一张。

改法：把包内既有图版 site-overview 的图面部分（去掉图版自带的深色页眉，crop
4800x2624+0+376）整幅置于封面。该图版本身已带 OSM 路网底图、完整图例、十节点
编号、三处重点区范围与「概念结构图」口径行，不新增任何主张；封面另加一行主判据
（原承诺 02 逐字）与三个关键读数（11.41 km² 取自 metrics.json；49.3% 取自
mobility-bluegreen 图版；10 取自 SCENARIO_NODE 计数），以及原图版页眉上的
「CONCEPT ONLY · 非法定规划图」角标。
"""
from __future__ import annotations
from pathlib import Path as _HaidianPath
import os, sys

T = str(_HaidianPath(__file__).resolve().parents[1])
OUT = os.path.join(T, "wp4b/out/a3")
JPG = os.path.join(T, "wp4b/jpg")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fixfont  # noqa: E402

CSS = """
/* WP-82 封面重做：标题带 + 总平面 + 判据 + 三读数，替换 v5.4 的纯标题版式 */
.cover{position:absolute;inset:0;background:#10383d;color:#fff;display:flex;flex-direction:column;padding:8mm 16mm 5mm}
.cover .ctop{flex:none}
.cover .crow{display:flex;justify-content:space-between;align-items:center;gap:12mm}
.cover .k{font-size:4.2mm;letter-spacing:.15em;color:#9ecdc7;display:flex;align-items:center;gap:5mm;font-family:SHS;font-weight:700;margin-bottom:0}
.cover h1{font-size:11.6mm;font-weight:700;line-height:1.14;margin:4.2mm 0 0}
.cover .sub{font-size:5.2mm;color:#9ecdc7;margin-top:3.2mm;letter-spacing:.02em;line-height:1.35}
.cover .cbadge{flex:none;font-size:4.2mm;font-weight:700;color:#fff;background:#d76450;border-radius:4mm;padding:2.2mm 5.6mm;letter-spacing:.04em;white-space:nowrap}
.cover .cplan{margin-top:4mm;border:.4mm solid #3f6165;background:#f2efe7;overflow:hidden;flex:none;line-height:0}
.cover .cplan img{display:block;width:381mm}
.cover .cplan{width:381mm}
.cover .cbot{margin-top:4mm;display:flex;gap:9mm;align-items:flex-start;flex:none}
.cover .cclaim{font-size:4.6mm;line-height:1.46;width:150mm;flex:none}
.cover .creads{display:flex;gap:8mm;flex:1}
.cover .crd{flex:1;border-left:.8mm solid #5fb3ab;padding-left:4mm}
.cover .crd b{display:block;font-size:8mm;font-weight:700;line-height:1.04;font-family:SHS;font-variant-numeric:tabular-nums}
.cover .crd span{display:block;font-size:3.8mm;color:#9ecdc7;margin-top:2mm;line-height:1.32}
.cover .cfoot{position:static;margin-top:auto;padding-top:4mm;display:flex;justify-content:space-between;gap:10mm;font-size:4.2mm;color:#9ecdc7;line-height:1.32}
"""

BAR = ('<span class="bar" style="height:0.64em">'
       '<i style="width:6.2em;background:#5fb3ab;height:0.64em"></i>'
       '<i style="width:3em;background:#4aa3c4;height:0.64em"></i>'
       '<i style="width:2em;background:#d6a13b;height:0.64em"></i>'
       '<i style="width:2.6em;background:#d76450;height:0.64em"></i></span>')

T_ = {
    "zh": dict(
        kick="万感京张 / EVERY SENSE JING-ZHANG · URBAN DESIGN ATLAS",
        h1="每一种身体都能独立使用的 AI 城市",
        sub="一条公共底线 · 两条等价路径 · 三处重点区域",
        badge="CONCEPT ONLY · 非法定规划图",
        claim="十个节点在 AI 开启与关闭两种状态下都必须能完成任务；做不到就停在门内，不进入下一阶段。",
        reads=[("11.41 km²", "临时总体设计范围 site_area_sqm"),
               ("49.3%", "AI 关闭后可达域收缩（图版口径）"),
               ("10", "运行节点，均声明 AI 关闭等价路径")],
        foot="概念建议 · 设计判据 · 非实测结果 · 临时边界 · 非法定规划 · 非工程线位"),
    "en": dict(
        kick="EVERY SENSE JING-ZHANG · URBAN DESIGN ATLAS",
        h1="An AI city every kind of body can use independently",
        sub="One public baseline · two equivalent paths · three key areas",
        badge="CONCEPT ONLY · NOT A STATUTORY PLAN",
        claim="All ten nodes must let a task be completed with AI on and with AI off; where they "
              "cannot, work stops at the gate and does not advance.",
        reads=[("11.41 km²", "Provisional design scope"),
               ("49.3%", "AI-off reachability shrinkage"),
               ("10", "Nodes with declared AI-off routes")],
        foot="CONCEPT PROPOSAL · DESIGN CRITERIA · NOT MEASURED RESULTS · PROVISIONAL · "
             "NOT STATUTORY · NOT AN ENGINEERING ALIGNMENT"),
}

IMG = "a3-coverPlan-%s-c4800x2624_0_376-w3400-q84.jpg"


def body(lang):
    t = T_[lang]
    reads = "".join('<div class="crd"><b>%s</b><span>%s</span></div>' % r for r in t["reads"])
    return ('<body><div class="cover">\n'
            '  <div class="ctop">\n'
            '    <div class="crow"><div class="k">%s<span>%s</span></div>'
            '<div class="cbadge">%s</div></div>\n'
            '    <h1>%s</h1>\n'
            '    <div class="sub">%s</div></div>\n'
            '  <div class="cplan"><img src="file://%s"></div>\n'
            '  <div class="cbot"><div class="cclaim">%s</div><div class="creads">%s</div></div>\n'
            '  <div class="cfoot"><span>%s</span><span>01 / 12</span></div>\n'
            '</div></body></html>'
            % (BAR, t["kick"], t["badge"], t["h1"], t["sub"],
               os.path.join(JPG, IMG % lang), t["claim"], reads, t["foot"]))


for lang in ("zh", "en"):
    p = os.path.join(OUT, "%s-01.html" % lang)
    h = open(p, encoding="utf-8").read()
    n0 = len(h)
    assert "</style>" in h
    h = h.replace("</style>", CSS + "</style>", 1)
    i = h.index("<body")
    h = h[:i] + body(lang)
    open(p, "w", encoding="utf-8").write(h)
    print("%s-01.html %d -> %d B  补字 %s" % (lang, n0, os.path.getsize(p), "".join(fixfont.patch(p)) or "无"))
