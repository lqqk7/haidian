# -*- coding: utf-8 -*-
"""交付 ⑥：A0 板 01 场景带派生件的来源与配方登记。

结论修正：该派生件的源并非不可考。它不是 assets/figures/scene-corridor-aerial.webp
（那是单幅走廊鸟瞰，与板 01 的 AI 开启 | AI 关闭双栏语义和 .b1fig 中缝分隔线不符），
而是 visual/assets/scene-fallback{,.en}.png（1824×692 / 1824×682，双栏并置的
AI 开启 / AI 关闭站点轴测）。文件名里记录的参数即是配方，逐项复现：

    magick <src> -crop 1824x505+0+100 +repage -resize 2400x \
           -quality 84 -sampling-factor 4:2:0 -strip -colorspace sRGB <out>

复现件与随包现件像素内容一致（zh RMSE 1.19%、en RMSE 1.31%，AE 0.36%），差异
全部来自 JPEG 熵编码实现不同，构图、裁切、尺寸逐项相同。因此**不重出、不替换**：
现件体积更大（129.9K / 140.2K vs 复现 95.4K / 104.0K），画质不低于复现件，替换
只会降质。本脚本只登记配方并提供校验。

用法：python mkscene.py [--rebuild]
"""
from __future__ import annotations
from pathlib import Path as _HaidianPath
import os, subprocess, sys

T = str(_HaidianPath(__file__).resolve().parents[1])
PKG = str(_HaidianPath(__file__).resolve().parents[3] / 'submissions/lqqk7/every-sense-jingzhang')
JPG = os.path.join(T, "wp4b/jpg")
NAME = "a0-scene-%s-c1824x505_0_100-w2400q84.jpg"
SRC = {"zh": "visual/assets/scene-fallback.png", "en": "visual/assets/scene-fallback.en.png"}
ARGS = ["-crop", "1824x505+0+100", "+repage", "-resize", "2400x",
        "-quality", "84", "-sampling-factor", "4:2:0", "-strip", "-colorspace", "sRGB"]


def build(lang, out):
    # force the output coder: the temp name ends in ".repro", which ImageMagick
    # cannot map to JPEG, and it would silently fall back to the input format.
    subprocess.run(["magick", os.path.join(PKG, SRC[lang])] + ARGS + ["jpeg:" + out], check=True)


if __name__ == "__main__":
    rebuild = "--rebuild" in sys.argv
    for lang in ("zh", "en"):
        cur = os.path.join(JPG, NAME % lang)
        tmp = cur + ".repro"
        build(lang, tmp)
        r = subprocess.run(["magick", "compare", "-metric", "RMSE", tmp, cur, "null:"],
                           capture_output=True, text=True)
        print("%s  现件 %d B  复现 %d B  RMSE %s"
              % (lang, os.path.getsize(cur), os.path.getsize(tmp), r.stderr.strip()))
        if rebuild:
            os.replace(tmp, cur)
        else:
            os.unlink(tmp)
