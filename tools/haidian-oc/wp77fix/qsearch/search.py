# -*- coding: utf-8 -*-
"""反解 v7.6 图版的 PNG 量化配方。

目标是包内 land-use-structure.png：8 位调色板、PLTE 118 色、全 0 滤波、
无附属块、单 IDAT。在未改文案的原始 raw.png 上穷举 pngquant × zopflipng
参数，先按调色板色数与体积筛选，再逐字节比对。
"""
from __future__ import annotations

import hashlib
import os
import struct
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "../ctrl-png/land-use-structure-zh.raw.png")
TGT = os.path.join(HERE, "../../w81-basemap/png/land-use-structure-zh.q.png")


def plte(p):
    d = open(p, "rb").read()
    i, n = 8, None
    while i < len(d):
        ln = struct.unpack(">I", d[i:i + 4])[0]
        typ = d[i + 4:i + 8]
        if typ == b"PLTE":
            n = ln // 3
            break
        i += 12 + ln
    return n


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


tgt_size, tgt_plte, tgt_sha = os.path.getsize(TGT), plte(TGT), sha(TGT)
print("target %d B  PLTE=%d  sha=%s" % (tgt_size, tgt_plte, tgt_sha[:16]))

rows = []
i = 0
for q in ["65-90", "62-92", "60-95", "70-95", "55-90", "70-90", "65-95", "80-95"]:
    for nofs in (False, True):
        for sp in (1, 3, 4):
            i += 1
            pq = os.path.join(HERE, "p%d.png" % i)
            args = ["pngquant", "--quality=" + q, "--speed", str(sp), "--force",
                    "--output", pq, RAW]
            if nofs:
                args.insert(1, "--nofs")
            r = subprocess.run(args, capture_output=True)
            if r.returncode or not os.path.exists(pq):
                print("q=%-6s nofs=%-5s sp=%d  pngquant rc=%d" % (q, nofs, sp, r.returncode))
                continue
            rows.append((q, nofs, sp, pq, plte(pq), os.path.getsize(pq)))
            print("q=%-6s nofs=%-5s sp=%d  PLTE=%-4d %8d B" % (q, nofs, sp, plte(pq), os.path.getsize(pq)))

print("\n-- 调色板色数命中 %d 的候选，进入 zopflipng --" % tgt_plte)
cands = [r for r in rows if r[4] == tgt_plte]
if not cands:
    print("无色数命中；按体积最接近取前 4")
    cands = sorted(rows, key=lambda r: abs(r[5] - tgt_size))[:4]
for q, nofs, sp, pq, pl, ps in cands:
    for zf in (["--filters=0"], ["--filters=0", "-m"], []):
        out = pq.replace("p", "z", 1) + "".join(zf).replace("-", "") + ".png"
        subprocess.run(["zopflipng", "-y"] + zf + [pq, out], capture_output=True)
        if not os.path.exists(out):
            continue
        s, h = os.path.getsize(out), sha(out)
        print("q=%-6s nofs=%-5s sp=%d zopfli%-14s %8d B  %s%s"
              % (q, nofs, sp, " ".join(zf) or "(default)", s, h[:16],
                 "   <<<<<< BYTE MATCH" if h == tgt_sha else ""))
        sys.stdout.flush()
