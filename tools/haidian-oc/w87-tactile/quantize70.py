# -*- coding: utf-8 -*-
"""本波三张图版的量化配方：pngquant --quality=40-70 --speed 1 + zopflipng。

为什么不用 wp77fix/quantize.py 的 65-98
--------------------------------------
包体硬线 40 MiB。本波要交的是「site-overview 双语重渲 + 两张新图」，按 65-98
配方与包内常规倍率合计约 1.5 MiB，装不下（重渲收口后余量只有 359 KB）。

于是把配方下限压到 40-70 逐张实测：site-overview 双语由 927,027 B 降到
713,998 B（省 213,029 B），在 100% 原始像素下与 65-98 版逐处比对——图例文字、
中英混排、OSM 底图细灰线、色块边缘——无可辨差别，密集底图区的最大通道差为
(49, 18, 32)，全部落在极浅色上。质量没有实际损失，省下的空间正是两张新图的
落脚处，因此三张图版统一采用本配方，一并登记。

用法：python quantize70.py <raw.png> [<raw.png> ...]  →  同名 .q.png
"""
from __future__ import annotations

import os
import subprocess
import sys

PNGQUANT = ["pngquant", "--quality=40-70", "--speed", "1", "--force"]
ZOPFLI = ["zopflipng", "-y", "--filters=0", "-m"]


def quantize(raw, out):
    tmp = "%s.%d.pq" % (out, os.getpid())
    subprocess.run(PNGQUANT + ["--output", tmp, raw], check=True)
    subprocess.run(ZOPFLI + [tmp, out], check=True, capture_output=True)
    pq = os.path.getsize(tmp)
    os.unlink(tmp)
    return pq, os.path.getsize(out)


if __name__ == "__main__":
    for raw in sys.argv[1:]:
        out = raw.replace(".raw.png", ".q.png")
        pq, z = quantize(raw, out)
        print("%-46s pngquant %8d -> zopfli %8d B" % (os.path.basename(out), pq, z))
