# -*- coding: utf-8 -*-
"""WP-92 总装：三张概念详图重出 → 量化 → 装包，并生成设想要素登记 JSON。

量化配方
--------
pngquant --quality=55-90 --speed 1 + zopflipng -y --filters=0 -m，理由与实测数据
见 quantize5590.py 的模块说明：65-98 装不下包体余量，40-70 会改变界面三分类与
断面四带的语义色，55-90 是同时满足两项的唯一一档。

本脚本不 commit、不 push、不改 manifest 与正文挂载 —— 收口在另一棒。
"""
from __future__ import annotations
from pathlib import Path as _HaidianPath

import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
T = os.path.dirname(HERE)
PKG = (str(_HaidianPath(__file__).resolve().parents[3] / 'submissions/lqqk7') + "/"
       "every-sense-jingzhang")
FIG = os.path.join(PKG, "assets/figures")
PY = os.path.join(T, "venv/bin/python")
OUT = os.path.join(HERE, "out")
import quantize5590 as QZ                               # noqa: E402

FIGS = [("fig1.py", "district-concept-sections"),
        ("fig2.py", "transport-system-concept"),
        ("fig3.py", "bluegreen-system-concept")]


def run(args, **kw):
    r = subprocess.run(args, capture_output=True, text=True, **kw)
    if r.returncode:
        raise SystemExit("FAILED %s\n%s\n%s" % (args, r.stdout, r.stderr))
    return r.stdout


def main():
    total = 0
    for script, name in FIGS:
        print(run([PY, os.path.join(HERE, script)], cwd=HERE).strip())
        raw = os.path.join(OUT, name + ".raw.png")
        q = os.path.join(OUT, name + ".q.png")
        pq, z = QZ.quantize(raw, q)
        dst = os.path.join(FIG, name + ".png")
        old = os.path.getsize(dst) if os.path.exists(dst) else 0
        shutil.copy2(q, dst)
        total += z
        print("   %-28s raw %8d → pngquant %8d → zopfli %8d B  (包内 %d → %d)"
              % (name + ".png", os.path.getsize(raw), pq, z, old, z))
    print(run([PY, os.path.join(HERE, "mkregister.py")]).strip())
    reg = os.path.join(PKG, "visual/assets/concept-design-register.json")
    total += os.path.getsize(reg)
    tracked = run(["git", "-C", PKG, "ls-files"]).split()
    now = sum(os.path.getsize(os.path.join(PKG, f)) for f in tracked
              if os.path.exists(os.path.join(PKG, f)))
    print("-- 本波新增 %d B（三图 + JSON）" % total)
    print("-- git 追踪字节 %d B = %.3f MiB；距 40 MiB 硬线余 %d B"
          % (now + total, (now + total) / 1048576, 40 * 1048576 - now - total))
    print("   （三图与 JSON 为新文件，尚未 git add，故未计入上面的 ls-files 统计）")


if __name__ == "__main__":
    main()
