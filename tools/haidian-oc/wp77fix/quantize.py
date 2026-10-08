# -*- coding: utf-8 -*-
"""图版 PNG 量化：pngquant 量化 + zopflipng 无损再压。

配方来源不是猜的：在未改文案的原始 raw.png 上反解，
`pngquant --quality=65-98 --speed 1`（保留 Floyd-Steinberg 抖动）产出的
调色板（118 色）与像素索引与 v7.6 随包成品逐字节一致；只有其后的 deflate
实现与当时不同（本次用 zopflipng -y --filters=0 -m，同一张图差 109 B，
无损，不影响任何像素）。

用法：python quantize.py <raw.png> [<raw.png> ...]
"""
from __future__ import annotations

import os
import subprocess
import sys

PNGQUANT = ["pngquant", "--quality=65-98", "--speed", "1", "--force"]
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
