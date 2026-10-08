# -*- coding: utf-8 -*-
"""交付 ③ metrics-evidence 大数字 + ④ 陈旧交集值全包归一。

③ 「01 / MEASURED」概念建筑基底合计 372,891 m² → 三位有效数字人读位
   （zh 约 37.3 万 ㎡ / en approx. 373,000 sqm；A0 字体子集无 ≈，故用 approx.）。
④ 绿地∩公共空间交集 452,986.656 ㎡ 是 v6.4 几何归位前的陈旧值。以当前
   geometry 复算（EPSG:4548）得 448,404.185 ㎡，与 metrics.json 登记值精确
   一致；占全域比例 3.9691% → 3.9289%。同一读数在四册里共 7 处，逐处归一，
   否则同一块展板上会新出现自相矛盾。
"""
from __future__ import annotations
from pathlib import Path as _HaidianPath
import os, sys

T = str(_HaidianPath(__file__).resolve().parents[1])
OUT = os.path.join(T, "wp4b/out")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fixfont  # noqa: E402

OLD_A, NEW_A = "452,986.656", "448,404.185"
OLD_P, NEW_P = "3.9691%", "3.9289%"

# ---- ③ metrics-evidence 页源 ------------------------------------------------
FIG = {
    "fig-zh.html": [
        ('<div class="mval num">372,891<span class="mu">m²</span></div>\n'
         '      <div class="mlab">概念建筑基底合计</div>',
         '<div class="mval num">37.3 万<span class="mu">㎡</span></div>\n'
         '      <div class="mlab">概念建筑基底合计（约）</div>')],
    "fig-en.html": [
        ('<div class="mval num">372,891<span class="mu">m²</span></div>\n'
         '      <div class="mlab">Conceptual building footprint</div>',
         '<div class="mval num">373,000<span class="mu">m²</span></div>\n'
         '      <div class="mlab">Building footprint (approx.)</div>')],
}

# ---- ④ 陈旧交集值 -----------------------------------------------------------
TILE = {
    "a0/zh-02.html": [('<div class="v">452,986.656 ㎡</div><div class="l">两类包络故意重叠</div>',
                       '<div class="v">44.8 万 ㎡</div><div class="l">两类包络故意重叠（约值）</div>')],
    "a0/en-02.html": [('<div class="v">452,986.656 sqm</div><div class="l">Deliberate envelope overlap</div>',
                       '<div class="v">448,000 sqm</div><div class="l">Deliberate envelope overlap (approx.)</div>')],
}
PLAIN = ["a0/zh-02.html", "a0/en-02.html", "a0/zh-06.html", "a0/en-06.html",
         "a3/zh-06.html", "a3/en-06.html", "a3/zh-10.html", "a3/en-10.html"]


def edit(rel, pairs, allow_many=()):
    p = os.path.join(OUT, rel)
    h = open(p, encoding="utf-8").read()
    n0 = len(h)
    for old, new in pairs:
        c = h.count(old)
        assert c >= 1, (rel, old[:40])
        h = h.replace(old, new)
    open(p, "w", encoding="utf-8").write(h)
    miss = fixfont.patch(p)
    print("%-16s %8d -> %8d B   补字 %s" % (rel, n0, os.path.getsize(p), "".join(miss) or "无"))


for rel, pairs in FIG.items():
    edit(rel, pairs)
for rel in PLAIN:
    pairs = list(TILE.get(rel, []))
    p = os.path.join(OUT, rel)
    h = open(p, encoding="utf-8").read()
    for old, new in pairs:
        assert h.count(old) == 1, (rel, "tile")
        h = h.replace(old, new)
    na, np_ = h.count(OLD_A), h.count(OLD_P)
    h = h.replace(OLD_A, NEW_A).replace(OLD_P, NEW_P)
    open(p, "w", encoding="utf-8").write(h)
    miss = fixfont.patch(p)
    print("%-16s 面积 %d 处 · 比例 %d 处 · 瓦片 %d 处   补字 %s"
          % (rel, na, np_, len(pairs), "".join(miss) or "无"))
