# -*- coding: utf-8 -*-
"""交付 ②：mobility 两图的循环引用解环。

现状（v7.7 随包图版实测）
------------------------
主图 mobility-bluegreen 印：
  「三处断点已在上方三幅图中以珊瑚色标注；完整十节点排序见审计明细附图。」
  「完整口径六行、十节点排序表与责任方：mobility-bluegreen-audit.png」
审计图 mobility-bluegreen-audit 印：
  「按节点差集面积降序取前三位；完整十节点排序表、口径明细与责任方见审计明细附图。」
审计图自己就是那张「审计明细附图」，于是这句把读者指回它自己；主图又把读者指向
审计图。两图互指成环，而十行实体只存在于 A3 图册第 11 页《十节点差集审计明细》。

改法
----
把两处「完整十节点排序表」的指引改指 A3 图册第 11 页；仍由审计图承担的部分
（口径六行、责任方）保留原指向，不做扩权表述。改动只动指引句，数值、图形、
版面常数一字不动。

三层同步（任一层重建都不回退）：
  主图  wpr6/mbg/copy2.py · wpr6/mbg/fig-{zh,en}.html
        → fig_mbg.py 重出 w81-basemap/html/mobility-bluegreen-{zh,en}.html
  审计图 wpr6/wpe2/fcopy.py · wpr6/wpe2/fig-{zh,en}.html（无中间层）
"""
from __future__ import annotations
from pathlib import Path as _HaidianPath

import os

T = str(_HaidianPath(__file__).resolve().parents[1])

# (相对路径, 旧串, 新串)；每条都断言恰好命中 1 处
EDITS = [
    # ---------------- 主图 mobility-bluegreen ----------------
    ("wpr6/mbg/copy2.py",
     "三处断点已在上方三幅图中以珊瑚色标注；完整十节点排序见审计明细附图。",
     "三处断点已在上方三幅图中以珊瑚色标注；完整十节点排序见 A3 图册第 11 页。"),
    ("wpr6/mbg/copy2.py",
     "完整口径六行、十节点排序表与责任方：",
     "完整口径六行与责任方："),
    ("wpr6/mbg/copy2.py",
     "口径与明细见审计附图 · ",
     "口径见审计附图，十节点明细见 A3 图册第 11 页 · "),
    ("wpr6/mbg/copy2.py",
     "The three breaks are marked coral above; the full ranking is in the ledger.",
     "The three breaks are marked coral above; the full ranking is on page 11 "
     "of the A3 booklet."),
    ("wpr6/mbg/copy2.py",
     "Full caliber, ranked ledger and accountable body:",
     "Full caliber and accountable body:"),
    ("wpr6/mbg/copy2.py",
     "caliber and ledger in the companion figure · ",
     "caliber in the companion figure, full ledger on page 11 of the A3 booklet · "),
    # ---------------- 审计图 mobility-bluegreen-audit ----------------
    ("wpr6/wpe2/fcopy.py",
     "按节点差集面积降序取前三位；完整十节点排序表、口径明细与责任方见审计明细附图。",
     "按节点差集面积降序取前三位；完整十节点排序表见 A3 图册第 11 页，口径与责任方见本图。"),
    ("wpr6/wpe2/fcopy.py",
     "The three largest gaps; full ranking in the companion ledger.",
     "The three largest gaps; the full ranking is on page 11 of the A3 booklet."),
]

# 页源里的同一批字面量（HTML 已转义处理：这些串不含 & < >，可直接替换）
HTML_EDITS = [
    ("wpr6/mbg/fig-zh.html", 0), ("wpr6/mbg/fig-en.html", 3),
    ("wpr6/wpe2/fig-zh.html", 6), ("wpr6/wpe2/fig-en.html", 7),
]


def apply_one(rel, old, new):
    p = os.path.join(T, rel)
    s = open(p, encoding="utf-8").read()
    n = s.count(old)
    assert n == 1, "%s: 旧串命中 %d 处\n  %s" % (rel, n, old)
    open(p, "w", encoding="utf-8").write(s.replace(old, new, 1))
    return True


def main():
    for rel, old, new in EDITS:
        apply_one(rel, old, new)
        print("%-24s ✓ %s" % (rel.split("/")[-1], old[:26]))
    # 页源：中文主图 3 条、英文主图 3 条、审计图各 1 条
    groups = {"wpr6/mbg/fig-zh.html": EDITS[0:3],
              "wpr6/mbg/fig-en.html": EDITS[3:6],
              "wpr6/wpe2/fig-zh.html": EDITS[6:7],
              "wpr6/wpe2/fig-en.html": EDITS[7:8]}
    for rel, edits in groups.items():
        for _, old, new in edits:
            apply_one(rel, old, new)
        print("%-24s ✓ %d 条" % (rel.split("/")[-1], len(edits)))


if __name__ == "__main__":
    main()
