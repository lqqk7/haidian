# -*- coding: utf-8 -*-
"""WP-92 三张概念详图的量化配方：pngquant --quality=55-90 --speed 1 + zopflipng。

为什么不是既有的两条配方
------------------------
本波逐条实测（三张 3000 × 1875 图版，pngquant 后再 zopflipng -y --filters=0 -m）：

    65-98：1,336,030 B → 约 1,229 KB，超出包体余量 1,229,021 B，装不下；
    40-70：1,108,991 B 装得下，但**改变了图面语义色**——金色 #d6a13b 被映射为
           (207,150,114) 的浅赭、绿色被映射为 (118,137,137) 的青灰，界面三分类
           （活性／展示／静）与断面四带的辨色因此失效，不可接受；
    55-90：1,105,390 B（估）装得下，且全部品牌色的单通道最大偏差 ≤ 8/255，
           仅三个孤立像素上的主色偏差为 17/255，浅绿填充偏差 ≤ 12/255。

因此本波取 55-90。同时把三张图的底图层压到 major + rail（图注如实说明），并把
图版内唯一一处孤立绿（断面第四带）改用与绿带填充同族的 #8fae8a——两项都是为了
让小面积语义色不被调色板挤掉，而不是为了省字节。
"""
from __future__ import annotations

import os
import subprocess
import sys

PNGQUANT = ["pngquant", "--quality=55-90", "--speed", "1", "--force"]
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
