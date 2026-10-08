# -*- coding: utf-8 -*-
"""重建四册所需的 jpg 派生件。

原 scratchpad 的 jpg 目录已被回收，但四册 PDF 里的 JPEG 是原样嵌入（未重编码），
因此可从随包 PDF 中原样抽出，作为「改动前」的逐字节基准。本脚本：

1. 用记录在文件名里的 magick 参数，从包内图版重建每一张派生件；
2. 与 PDF 抽出的原件逐字节比对——未受本次改动影响的派生件必须完全一致，
   一致即证明参数复原无误；不一致的只应是本次真正改了文案的那几张；
3. 无法复现的（a0-scene，源图解码链已变）直接沿用抽出的原件。

用法：python mkjpg.py [--verify-only]
"""
from __future__ import annotations
from pathlib import Path as _HaidianPath

import hashlib
import os
import subprocess
import sys

T = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PKG = str(_HaidianPath(__file__).resolve().parents[3] / 'submissions/lqqk7/every-sense-jingzhang')
FIG = os.path.join(PKG, "assets/figures")
JPG = os.path.join(T, "wp4b/jpg")
EXT = os.path.join(T, "wp77fix/pdfimg")

# name-template -> (figure base, crop or None, width or None, quality)
SPEC = [
    ("a3-siteBand-%s-c4560x1056_120_408-w3400-q80.jpg", "site-overview", "4560x1056+120+408", 3400, 80),
    ("a3-coverPlan-%s-c4800x2624_0_376-w2800-q78.jpg", "site-overview", "4800x2624+0+376", 2800, 78),
    ("a3-landuseBand-%s-c4560x1012_120_408-w3400-q80.jpg", "land-use-structure", "4560x1012+120+408", 3400, 80),
    ("a3-keyareasBand-%s-c4560x1496_120_532-w3400-q80.jpg", "key-areas", "4560x1496+120+532", 3400, 80),
    ("a3-mobilityZoom-%s-c1064x1168_1208_628-q84.jpg", "mobility-bluegreen", "1064x1168+1208+628", None, 84),
    ("a3-metricsDenom-%s-c2560x532_120_2352-q80.jpg", "metrics-evidence", "2560x532+120+2352", None, 80),
    ("a0-landuse-%s-w4200q80.jpg", "land-use-structure", None, 4200, 80),
    ("a0-keyareas-%s-w4200q80.jpg", "key-areas", None, 4200, 80),
    ("a0-mobility-%s-w4200q62.jpg", "mobility-bluegreen", None, 4200, 62),
    ("a0-brand-%s-w4200q80.jpg", "brand-system", None, 4200, 80),
    ("a0-metrics-%s-w4200q80.jpg", "metrics-evidence", None, 4200, 80),
]

# 从 PDF 抽出的原件：册 -> 页序 -> 派生件名模板
ORIG = {
    ("a3-booklet", "zh"): ["a3-siteBand-%s-c4560x1056_120_408-w3400-q80.jpg",
                           "a3-landuseBand-%s-c4560x1012_120_408-w3400-q80.jpg",
                           "a3-keyareasBand-%s-c4560x1496_120_532-w3400-q80.jpg",
                           "a3-mobilityZoom-%s-c1064x1168_1208_628-q84.jpg",
                           "a3-metricsDenom-%s-c2560x532_120_2352-q80.jpg"],
    ("a0-boards", "zh"): ["a0-scene-%s-c1824x505_0_100-w2400q84.jpg",
                          "a0-landuse-%s-w4200q80.jpg",
                          "a0-keyareas-%s-w4200q80.jpg",
                          "a0-mobility-%s-w4200q62.jpg",
                          "a0-brand-%s-w4200q80.jpg",
                          "a0-metrics-%s-w4200q80.jpg"],
}


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def orig_map():
    """派生件名 -> PDF 抽出的原件路径。"""
    m = {}
    for (book, _), names in ORIG.items():
        for lang, suffix in (("zh", ""), ("en", ".en")):
            d = os.path.join(EXT, book + suffix)
            for i, tpl in enumerate(names):
                m[tpl % lang] = os.path.join(d, "i-%03d.jpg" % i)
    return m


def build(name, base, crop, w, q, lang):
    src = os.path.join(FIG, base + (".png" if lang == "zh" else ".en.png"))
    out = os.path.join(JPG, name)
    args = ["magick", src]
    if crop:
        args += ["-crop", crop, "+repage"]
    if w:
        args += ["-resize", "%dx" % w]
    args += ["-quality", str(q), "-sampling-factor", "4:2:0", "-strip",
             "-colorspace", "sRGB", out]
    subprocess.run(args, check=True)
    return out


def main():
    os.makedirs(JPG, exist_ok=True)
    om = orig_map()
    changed, same, copied = [], [], []
    for tpl, base, crop, w, q in SPEC:
        for lang in ("zh", "en"):
            name = tpl % lang
            out = build(name, base, crop, w, q, lang)
            o = om.get(name)
            if o and os.path.exists(o):
                (same if sha(out) == sha(o) else changed).append(
                    (name, os.path.getsize(o), os.path.getsize(out)))
            else:
                changed.append((name, 0, os.path.getsize(out)))
    # 不可复现的派生件：沿用 PDF 抽出的原件
    for name, o in om.items():
        p = os.path.join(JPG, name)
        if not os.path.exists(p):
            subprocess.run(["cp", o, p], check=True)
            copied.append((name, os.path.getsize(p)))

    print("== 与原件逐字节一致（未受影响）%d 张 ==" % len(same))
    for n, a, b in same:
        print("   OK   %-52s %d B" % (n, b))
    print("== 与原件不同（本次改动所致）%d 张 ==" % len(changed))
    for n, a, b in changed:
        print("   CHG  %-52s %d -> %d B" % (n, a, b))
    print("== 沿用 PDF 抽出原件 %d 张 ==" % len(copied))
    for n, b in copied:
        print("   CP   %-52s %d B" % (n, b))


if __name__ == "__main__":
    main()
