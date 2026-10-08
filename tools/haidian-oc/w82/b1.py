# -*- coding: utf-8 -*-
"""交付 ①（A0 板 01）：用包内既有定义填满下部留白。

板 01 原设计（WP-N2b）刻意只放「一个论点 + 一张图」，下部约 30% 是空的。
本次在图注与角注之间加入三条索引带，全部字号 ≥ 12 mm（沿用本板「评审缩放下
每个字符 ≥ 13 mm」的既定判据），内容一律抄自包内既有定义，不新造：

  四色语义   proposal.md / proposal.en.md「配色体系」六色板中的四个信息色，
             及「颜色不得单独承载信息」的冗余规则（写进本带说明）。
  证据行动门 A3 第 10 页「阶段零：九十天证据门」G0—G3 逐字。
  十个运行节点 geometry/constraints.geojson SCENARIO_NODE 的 id 与 gate_id。

版心：把 .b1foot 的下留白由 38 mm 收到 20 mm（纯空白参数），三条索引带用
margin-top:auto 顶到角注之上，两语渲染后逐一量测未越界。
"""
from __future__ import annotations
from pathlib import Path as _HaidianPath
import os, sys

T = str(_HaidianPath(__file__).resolve().parents[1])
OUT = os.path.join(T, "wp4b/out/a0")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fixfont  # noqa: E402

CSS = """
/* WP-82 板 01 下部索引带：三条，全部 >= 12 mm */
.b1idx{margin-top:auto}
.b1idx .ix{display:grid;grid-template-columns:268mm 1fr;gap:14mm;align-items:baseline;padding:6mm 0;border-top:.6mm solid #cbd3cf}
.b1idx .ix .k{font-size:12mm;letter-spacing:.08em;color:#177c78;font-weight:700;line-height:1.3}
.b1idx .ix .v{font-size:13.3mm;line-height:1.34;color:#10383d}
.b1idx .ix .v i{display:inline-block;width:9mm;height:9mm;border-radius:50%;margin:0 4mm 0 8mm;vertical-align:0}
.b1idx .ix .v i:first-child{margin-left:0}
.b1idx .note{font-size:12mm;line-height:1.34;color:#68787b;padding:6mm 0 0;border-top:.6mm solid #cbd3cf}
"""

GATES = {"OP-01": "G2", "OP-02": "G1", "OP-03": "G2", "OP-04": "G0", "OP-05": "G2",
         "OP-06": "G1", "OP-07": "G1", "OP-08": "G3", "OP-09": "G3", "OP-10": "G3"}
NODES = " · ".join("%s %s" % (k, v) for k, v in sorted(GATES.items()))

SW = [("#177c78", "水鸭青 #177c78 通用可达底线", "teal #177c78 access baseline"),
      ("#d76450", "珊瑚 #d76450 人工接管与求助", "coral #d76450 human handover"),
      ("#6b5b95", "紫 #6b5b95 共同设计证据", "purple #6b5b95 co-design"),
      ("#d6a13b", "金 #d6a13b 文化与遗产层", "gold #d6a13b heritage layer")]

TXT = {
    "zh": dict(k1="四色语义 / COLOUR SEMANTICS", k2="证据行动门 / EVIDENCE GATES",
               k3="十个运行节点 / TEN OPERATING NODES",
               g="G0 对齐资料、许可与任务脚本 · G1 形成可逆原型 · G2 完成封闭成对测试 · G3 取得独立复核",
               note="颜色不单独承载信息：以颜色区分的状态同时具备形状、文字或触觉冗余。"
                    "节点编号与闸门取自 geometry/constraints.geojson，闸门定义见 A3 第 10 页。"),
    "en": dict(k1="COLOUR SEMANTICS", k2="EVIDENCE GATES", k3="TEN OPERATING NODES",
               g="G0 verifies material, permissions and task scripts · G1 reversible prototype · "
                 "G2 closed paired testing · G3 independent review",
               note="Colour never carries information alone: every colour-coded state also "
                    "carries a shape, a word or a tactile cue. Node ids and gates: "
                    "geometry/constraints.geojson; gate definitions on A3 page 10."),
}


def block(lang):
    i = 2 if lang == "en" else 1
    chips = "".join('<i style="background:%s"></i>%s' % (c[0], c[i]) for c in SW)
    t = TXT[lang]
    row = ('<div class="ix"><span class="k">%s</span><span class="v">%s</span></div>')
    return ('<div class="b1idx">'
            + row % (t["k1"], chips)
            + row % (t["k2"], t["g"])
            + row % (t["k3"], NODES)
            + '<div class="note">%s</div></div>\n  ' % t["note"])


for lang in ("zh", "en"):
    p = os.path.join(OUT, "%s-01.html" % lang)
    h = open(p, encoding="utf-8").read()
    n0 = len(h)
    assert h.count(".b1foot{margin-top:auto;padding-bottom:38mm;") == 1
    h = h.replace(".b1foot{margin-top:auto;padding-bottom:38mm;",
                  ".b1foot{margin-top:10mm;padding-bottom:20mm;", 1)
    for o, n in ((".b1cap{display:grid;grid-template-columns:1fr 1fr;gap:36mm;margin-top:38mm}",
                  ".b1cap{display:grid;grid-template-columns:1fr 1fr;gap:36mm;margin-top:24mm}"),
                 (".b1fig{width:1125mm;margin-top:26mm;", ".b1fig{width:1125mm;margin-top:20mm;")):
        assert h.count(o) == 1, o
        h = h.replace(o, n, 1)
    assert "</style>" in h
    h = h.replace("</style>", CSS + "</style>", 1)
    assert h.count('<div class="b1foot">') == 1
    h = h.replace('<div class="b1foot">', block(lang) + '<div class="b1foot">', 1)
    open(p, "w", encoding="utf-8").write(h)
    print("%s-01.html %d -> %d B  补字 %s" % (lang, n0, os.path.getsize(p), "".join(fixfont.patch(p)) or "无"))
