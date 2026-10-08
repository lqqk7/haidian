# -*- coding: utf-8 -*-
"""交付 ① 第一步：A3 双语册 12 页 → 16 页的页码印字改写。

本册页码只在三处印出，且形态唯一（尾页 12 → 16 后逐页复核）：
  封面   <span>01 / 12</span>                （.cfoot 右栏）
  页眉   <div class="p">NN / 12</div>        （.hdr .r .p）
  页脚   <span class="pg">NN / 12</span>     （.foot .pg）
因此改写只认 `>NN / 12<` 这一形态；页内其它以「NN /」开头的印字（01 / CALIBER、
10 / 10 节点、05A / GAP AUDIT LEDGER 等）分母都不是 12，不会被误伤。改写后逐文件
打印 before → after 的每一处命中，供页码 diff 复核。

顺序：本脚本先跑（把原尾页 12 挪成 16 并把全册分母改成 16），mkver.py 后跑
（新建 12—15，其页码直接以 16 为分母生成）。脚本可重复执行：分母已是 16 时
只做零命中的空转。
"""
from __future__ import annotations
from pathlib import Path as _HaidianPath

import os
import re
import sys

T = str(_HaidianPath(__file__).resolve().parents[1])
OUT = os.path.join(T, "wp4b/out/a3")
OLD_N, NEW_N = 12, 16

PAT = re.compile(r">(\d\d) / (%d)<" % OLD_N)


def shift_tail():
    """原尾页 12 → 16。"""
    for lang in ("zh", "en"):
        src = os.path.join(OUT, "%s-%02d.html" % (lang, OLD_N))
        dst = os.path.join(OUT, "%s-%02d.html" % (lang, NEW_N))
        if os.path.exists(dst):
            print("   %s 已存在，跳过挪页" % os.path.basename(dst))
            continue
        assert os.path.exists(src), src
        os.rename(src, dst)
        print("   %s → %s" % (os.path.basename(src), os.path.basename(dst)))


def renumber():
    ok = True
    for lang in ("zh", "en"):
        for p in sorted(os.listdir(OUT)):
            m = re.fullmatch(r"%s-(\d\d)\.html" % lang, p)
            if not m:
                continue
            idx = int(m.group(1))
            path = os.path.join(OUT, p)
            s = open(path, encoding="utf-8").read()
            hits = PAT.findall(s)
            if not hits:
                print("   %-14s 命中 0 处（分母已是 %d）" % (p, NEW_N))
                continue
            # 封面只印 1 处，其余每页 2 处（页眉 + 页脚）
            want = 1 if idx == 1 else 2
            if len(hits) != want:
                print("   %-14s ✗ 命中 %d 处，期望 %d 处" % (p, len(hits), want))
                ok = False
            # 未挪动的页：印字页序必须等于文件序；挪动的尾页：印字仍是原序 OLD_N
            expect = OLD_N if idx == NEW_N else idx
            bad = [h for h in hits if int(h[0]) != expect]
            if bad:
                print("   %-14s ✗ 页码与文件序不符：%s" % (p, bad))
                ok = False
            new, n = PAT.subn(lambda m: ">%02d / %d<" % (idx, NEW_N), s)
            open(path, "w", encoding="utf-8").write(new)
            print("   %-14s %d 处： %s → %s"
                  % (p, n, " ".join("%s / %d" % (h[0], OLD_N) for h in hits),
                     " ".join("%s / %d" % (h[0], NEW_N) for h in hits)))
    return ok


def audit():
    """终态复核：逐页把每一处页码印字打印出来。"""
    print("== 页码终态逐页复核 ==")
    bad = 0
    for lang in ("zh", "en"):
        files = sorted(f for f in os.listdir(OUT)
                       if re.fullmatch(r"%s-\d\d\.html" % lang, f))
        for p in files:
            idx = int(p[3:5])
            s = open(os.path.join(OUT, p), encoding="utf-8").read()
            hits = re.findall(r">(\d\d) / (\d\d)<", s)
            want = 1 if idx == 1 else 2
            state = "OK "
            if len(hits) != want or any(int(a) != idx or int(b) != NEW_N
                                        for a, b in hits):
                state = "✗  "
                bad += 1
            print("   %s%-14s %s" % (state, p, ["%s / %s" % h for h in hits]))
    print("   总页数 zh %d · en %d ; 异常 %d 页"
          % (sum(1 for f in os.listdir(OUT) if re.fullmatch(r"zh-\d\d\.html", f)),
             sum(1 for f in os.listdir(OUT) if re.fullmatch(r"en-\d\d\.html", f)),
             bad))
    return bad == 0


if __name__ == "__main__":
    if "--audit" in sys.argv:
        sys.exit(0 if audit() else 1)
    print("== 挪尾页 ==")
    shift_tail()
    print("== 改写分母 %d → %d ==" % (OLD_N, NEW_N))
    sys.exit(0 if renumber() else 1)
