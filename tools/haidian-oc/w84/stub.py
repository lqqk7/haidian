# -*- coding: utf-8 -*-
"""交付 ④：A3 第 11 页启用 OP-07 / OP-09 接入支线警示。

w82/p11.py 在上一波已埋好文案与 W82_STUB 开关，但当时 p11 版心无余量，故未启用；
p11.py 的其余改写此后已落盘，重跑会因锚点已变而断言失败，因此本脚本只做那一处
STUB 替换（锚点串与 p11.py 的 STUB 字面量逐字一致）。

披露内容：十节点接入网络的支线长度计入行程预算，OP-07 与 OP-09 的支线分别为
170.8 m 与 188.8 m，已超 R_off = 150 m——AI 关闭时这两个节点接不到任何一条提交
中心线，其「关闭域」全部是被预算截断的支线段。这是全表最口径敏感的两行，之前只
在 mobility-bluegreen-audit 图版的 aud_note 里披露，A3 明细页没有。
"""
from __future__ import annotations
from pathlib import Path as _HaidianPath

import os
import sys

T = str(_HaidianPath(__file__).resolve().parents[1])
OUT = os.path.join(T, "wp4b/out/a3")
sys.path.insert(0, os.path.join(T, "w82"))
import fixfont  # noqa: E402

STUB = {
    "zh": ("节点以最短直线支线接入网络，支线长度计入行程预算",
           "节点以最短直线支线接入网络，支线长度计入行程预算；OP-07、OP-09 支线已超 R_off"),
    "en": ("Each node joins by its shortest straight stub; stub length counts against the budget",
           "Each node joins by its shortest straight stub; stub length counts against the budget; "
           "the OP-07 / OP-09 stubs already exceed R_off"),
}


def main():
    for lang in ("zh", "en"):
        p = os.path.join(OUT, "%s-11.html" % lang)
        s = open(p, encoding="utf-8").read()
        old, new = STUB[lang]
        assert s.count(new) == 0, "%s 已启用" % lang
        n = s.count(old)
        assert n == 1, "%s: 锚点命中 %d 处" % (lang, n)
        open(p, "w", encoding="utf-8").write(s.replace(old, new, 1))
        print("%s-11.html 已启用支线警示  补字 %s"
              % (lang, "".join(fixfont.patch(p)) or "无"))


if __name__ == "__main__":
    main()
