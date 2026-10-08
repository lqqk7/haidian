# -*- coding: utf-8 -*-
"""交付 ③：中文 site-overview 图版左栏末行压页脚分隔线的修复。

缺陷（量测于 1200×750 版心，w83fix/probe.js）
--------------------------------------------
左栏（.body > 第一列）自然高 336.4 px，网格给它的高度只有 328 px：
  .body   y=397  h=328    → 底边 725
  col1    y=397  h=336.4  → 底边 733.4
  .ft     y=725  h=25     → 顶边 725（其 border-top 即页脚分隔线）
于是左栏末行 .sn「公告约值 · 临时框线」（盒 716.4–733.4）越过分隔线 8.4 px，
压在页脚上沿。英文侧左栏字号更小（.lg1 22 px / .lg2 17 px），无此问题。

修法
----
只回收左栏三行统计块的行距：.srow 的 margin-top 由 8 px 改 4 px，三处共回收
12 px，左栏底边回到 721.4，与分隔线净空 3.6 px（≥ 3 px 判据）。字号、颜色、
边框、列宽、图带、题注、页脚一字不动，压线消失而不压字。

语言隔离：新增 .srowZ 只由中文页发出并挂在中文页的三个 .srow 上；英文页既不
发出该规则也不挂该类，英文图版逐字节不变。

三层同步：
  wp4b/build/sitefig.js（生成器，按 lang 分支）
  wp4b/out/site-zh.html（页源）
  w81-basemap/html/site-overview-zh.html 由 fig_site.py 从页源重出
"""
from __future__ import annotations
from pathlib import Path as _HaidianPath

import os

T = str(_HaidianPath(__file__).resolve().parents[1])

CSS_OLD = ".srow{border-left:3px solid;padding:0 0 0 10px;margin-top:8px}"
CSS_NEW = (".srow{border-left:3px solid;padding:0 0 0 10px;margin-top:8px}"
           "\n.srowZ{margin-top:4px}")

EDITS = [
    # 生成器：CSS 规则只在中文分支发出；类名只在中文分支挂上
    ("wp4b/build/sitefig.js", CSS_OLD,
     ".srow{border-left:3px solid;padding:0 0 0 10px;margin-top:8px}"
     "${zh ? '\\n.srowZ{margin-top:4px}' : ''}", 1),
    ("wp4b/build/sitefig.js", '<div class="srow" style="border-left-color:',
     '<div class="srow${zh ? \' srowZ\'  : \'\'}" style="border-left-color:', 1),
    # 页源（中文）
    ("wp4b/out/site-zh.html", CSS_OLD, CSS_NEW, 1),
    ("wp4b/out/site-zh.html", '<div class="srow" style="border-left-color:',
     '<div class="srow srowZ" style="border-left-color:', 3),
]


def main():
    for rel, old, new, want in EDITS:
        p = os.path.join(T, rel)
        s = open(p, encoding="utf-8").read()
        n = s.count(old)
        assert n == want, "%s: 命中 %d 处，期望 %d\n  %s" % (rel, n, want, old[:60])
        open(p, "w", encoding="utf-8").write(s.replace(old, new))
        print("%-22s %d 处  %s" % (rel.split("/")[-1], n, old[:46]))


if __name__ == "__main__":
    main()
