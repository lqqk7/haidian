# -*- coding: utf-8 -*-
"""交付 ②：A3 第 11 页《十节点差集审计明细》整表按权威口径重出。

数据来源：w82/final.py 的几何复算（EPSG:4548 / R_on=300 / R_off=150 / w=40 /
圆弧每象限 12 段 / 支线长度计入行程预算，超预算时可达线形退化为被预算截断
的支线段）。roads.geojson 加密（5 条线 114 顶点真实走向）后按 chain-data
v0.4.0 / metrics.json 重导，复算已逐值命中图版 mobility-bluegreen 的四个汇总
读数与前三行：
  网络 22,858.6 m（图版印 22 859 m）
  开启并集 438,298.947 · 关闭并集 222,078.217
  差集并集 216,220.730 · 差集占比 49.3318%（49.3%）
  OP-03 47,314 / 65.2%   OP-04 44,356 / 63.4%   OP-02 35,425 / 61.6%

页面替换全部按正则定位并由 gap-audit-data.json 派生，重复执行收敛到同一结果。
"""
from __future__ import annotations
from pathlib import Path as _HaidianPath
import json, os, re, sys

T = str(_HaidianPath(__file__).resolve().parents[1])
OUT = os.path.join(T, "wp4b/out/a3")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fixfont  # noqa: E402

D = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "gap-audit-data.json")))
ROWS = D["rows"]
S = D["summary"]
MAX = max(r["gap"] for r in ROWS)

GATE_COL = {"G0": "#68787b", "G1": "#d6a13b", "G2": "#6b5b95", "G3": "#d76450"}

SCEN = {
    "zh": {"OP-01": "S01 多模态无障碍寻路", "OP-02": "S02 低刺激安静路线与安静时段",
           "OP-03": "S03 手语、字幕、语音、易读文本同屏服务",
           "OP-04": "S04 轮椅与婴儿车连续通行辅助", "OP-05": "S05 服务机器人礼让与可预测交互",
           "OP-06": "S06 认知友好办事导航", "OP-07": "S07 触觉、声音、视觉三通道遗产解说",
           "OP-08": "S08 无障碍智能零售与支付替代路径", "OP-09": "S09 大型活动感官负荷调节",
           "OP-10": "S10 AI 关闭后的等价求助与疏散"},
    "en": {"OP-01": "S01 Multimodal accessible wayfinding",
           "OP-02": "S02 Low-stimulation route and quiet periods",
           "OP-03": "S03 Sign, caption, speech and easy-read service",
           "OP-04": "S04 Continuous wheelchair and stroller movement",
           "OP-05": "S05 Predictable service-robot interaction",
           "OP-06": "S06 Cognitively accessible procedures",
           "OP-07": "S07 Tactile, auditory and visual heritage interpretation",
           "OP-08": "S08 Accessible smart retail with payment alternatives",
           "OP-09": "S09 Sensory-load management for major events",
           "OP-10": "S10 Equivalent help and evacuation with AI disabled"},
}


def rowhtml(i, r, lang):
    hot = " hot" if i < 3 else ""
    c = GATE_COL[r["gate"]]
    return ('<div class="tr%s">\n    <span class="c0">%d</span>'
            '<span class="c1">%s</span><span class="c2">%s</span>\n'
            '    <span class="c3" style="color:%s;border-color:%s">%s</span>\n'
            '    <span class="c4"><i style="width:%s%%"></i><b>%s</b></span>\n'
            '    <span class="c5">%.1f%%</span></div>'
            % (hot, i + 1, r["id"], SCEN[lang][r["id"]], c, c, r["gate"],
               ("%.1f" % (r["gap"] / MAX * 100)).rstrip("0").rstrip("."),
               format(int(round(r["gap"])), ","), r["share"]))


def tbody(lang):
    return "".join(rowhtml(i, r, lang) for i, r in enumerate(ROWS))


ON, OFF, GAP = S["on_union"], S["off_union"], S["gap_union"]
SHARE, NETLEN = S["gap_share_pct"], S["network_length_m"]

WAN = lambda v: "%.1f 万 m²" % (v / 10000.0)                       # 43.8 万 m²
APPROX = lambda v: "approx. %s m²" % format(int(round(v / 1000.0)) * 1000, ",")
FULL = lambda v: "{:,.3f}".format(v)                               # 438,298.947

TILES = {
    "zh": [(WAN(ON), "AI 开启域并集 · 全值 %s ㎡" % FULL(ON), "临时几何 · 非法定面积"),
           (WAN(OFF), "AI 关闭域并集 · 全值 %s ㎡" % FULL(OFF), "临时几何 · 非法定面积"),
           (WAN(GAP), "差集并集 · 全值 %s ㎡" % FULL(GAP), "临时几何 · 非法定面积"),
           ("%.1f%%" % SHARE, "差集占开启域 · 全值 %.4f%%" % SHARE, "临时几何 · 非绩效值")],
    "en": [(APPROX(ON), "AI-on union · full value %s sqm" % FULL(ON),
            "provisional geometry · not a statutory area"),
           (APPROX(OFF), "AI-off union · full value %s sqm" % FULL(OFF),
            "provisional geometry · not a statutory area"),
           (APPROX(GAP), "Gap union · full value %s sqm" % FULL(GAP),
            "provisional geometry · not a statutory area"),
           ("%.1f%%" % SHARE, "Gap share of AI-on · full value %.4f%%" % SHARE,
            "provisional geometry · not a performance figure")],
}


def tiles(lang):
    return "".join('<div class="sq"><b>%s</b><span>%s</span><em class="pv">%s</em></div>'
                   % t for t in TILES[lang])


PCT = "%.1f%%" % SHARE

LEAD = {
    "zh": "本表为《按本图自设口径：AI 关闭后可达域收缩 {p}》"
          "的审计明细附图｜与随包附图 mobility-bluegreen 同口径同源复算，四个汇总读数与前"
          "三行逐字一致，第 4—10 行为完整排序。".format(p=PCT),
    "en": ("Companion ledger to “Self-set convention: AI off shrinks the "
           "reachable domain by {p}”"
           "｜Recomputed under the same caliber and from the same source as the companion "
           "mobility-bluegreen figure: the four summary readings and the top three rows match "
           "it verbatim; rows 4–10 are the rest of that same ranking, which the figure "
           "has no room to print.").format(p=PCT),
}

# 支线警示：OP-07 / OP-09 接入支线超 R_off，警示行印出两者实际支线长度。
SPUR = {r["id"]: r["spur"] for r in ROWS}
STUB = {
    "zh": (re.compile(r'；?OP-07[^、]*、OP-09[^支]*支线已超 R_off'),
           "；OP-07（%.2f m）、OP-09（%.2f m）支线已超 R_off" % (SPUR["OP-07"], SPUR["OP-09"])),
    "en": (re.compile(r'(; )?the OP-07 (\([\d.]+ m\) )?/ OP-09 (\([\d.]+ m\) )?'
                      r'stubs already exceed R_off'),
           "; the OP-07 (%.2f m) / OP-09 (%.2f m) stubs already exceed R_off"
           % (SPUR["OP-07"], SPUR["OP-09"])),
}

NET = {"zh": (re.compile(r'总长 [\d ,]+ m'),
              "总长 %s m" % format(int(round(NETLEN)), ",").replace(",", " ")),
       "en": (re.compile(r'[\d,]+ m total'), "%s m total" % format(int(round(NETLEN)), ","))}
TU = {"zh": (re.compile(r'(<div class="tu"><span>十节点并集</span><b>)[^<]+(</b>)'),
             WAN(GAP)),
      "en": (re.compile(r'(<span>Union of ten nodes</span><b>)[^<]+(</b>)'),
             "%s m²" % format(int(round(GAP)), ","))}

# 「首批审计断点」= 差集面积排序前三名，随表体一同重排。
FAB = (re.compile(r'(<div class="fab"><b>[^<]*</b><span>)OP-\d\d · OP-\d\d · OP-\d\d(</span>)'),
       " · ".join(r["id"] for r in ROWS[:3]))

TR_BLOCK = re.compile(r'<div class="tr hot">(?:.*?</div>){10}', re.S)
SQW = re.compile(r'<div class="sqw">.*?</div></div>', re.S)
LEAD_RE = re.compile(r'(<div class="lead">).*?(</div>)', re.S)


def sub1(h, rx, repl, tag, lang):
    """全页唯一命中的正则替换；repl 中的反斜杠与 \\g 已由 lambda 规避。"""
    n = len(rx.findall(h)); assert n == 1, (lang, tag, n)
    return rx.sub(lambda m: repl(m) if callable(repl) else repl, h, count=1)


def run(lang):
    p = os.path.join(OUT, "%s-11.html" % lang)
    h = open(p, encoding="utf-8").read()
    old = h

    h = sub1(h, TR_BLOCK, lambda m: tbody(lang), "tr", lang)
    h = sub1(h, SQW, lambda m: '<div class="sqw">%s</div>' % tiles(lang), "sqw", lang)
    h = sub1(h, LEAD_RE, lambda m: m.group(1) + LEAD[lang] + m.group(2), "lead", lang)

    rx, v = NET[lang]; h = sub1(h, rx, v, "net", lang)
    rx, v = TU[lang]
    h = sub1(h, rx, lambda m: m.group(1) + v + m.group(2), "tu", lang)
    rx, v = STUB[lang]; h = sub1(h, rx, v, "stub", lang)
    rx, v = FAB
    h = sub1(h, rx, lambda m: m.group(1) + v + m.group(2), "fab", lang)

    open(p, "w", encoding="utf-8").write(h)
    print("%s-11.html  %d -> %d B" % (lang, len(old), len(h)))
    print("   补字", "".join(fixfont.patch(p)) or "无")


for l in ("zh", "en"):
    run(l)
