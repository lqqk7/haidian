# -*- coding: utf-8 -*-
"""检查各图版内嵌字体子集是否覆盖新增文案所需字符。"""
from pathlib import Path as _HaidianPath
import base64
import io
import re
import sys

from fontTools.ttLib import TTFont

HTML = {
    "site-zh": str(_HaidianPath(__file__).resolve().parents[1] / 'wpn2b/wp4b/out/site-zh.html'),
    "site-en": str(_HaidianPath(__file__).resolve().parents[1] / 'wpn2b/wp4b/out/site-en.html'),
    "lu-zh": str(_HaidianPath(__file__).resolve().parents[1] / 'wpn2b/wp4b/out/lu-zh.html'),
    "lu-en": str(_HaidianPath(__file__).resolve().parents[1] / 'wpn2b/wp4b/out/lu-en.html'),
    "mbg-zh": str(_HaidianPath(__file__).resolve().parents[1] / 'wpr6/mbg/fig-zh.html'),
    "mbg-en": str(_HaidianPath(__file__).resolve().parents[1] / 'wpr6/mbg/fig-en.html'),
    "dsp-zh": str(_HaidianPath(__file__).resolve().parents[1] / 'wpv70/dsp/dsp-zh.html'),
    "dsp-en": str(_HaidianPath(__file__).resolve().parents[1] / 'wpv70/dsp/dsp-en.html'),
}

ATTR_ZH = "底图数据 © OpenStreetMap 贡献者，ODbL 1.0；快照 osm-fabric-snapshot-20260815"
ATTR_EN = ("Basemap data © OpenStreetMap contributors, ODbL 1.0; "
           "snapshot osm-fabric-snapshot-20260815")
MBG_TITLE_ZH = "按本图口径：AI 关闭后可达域收缩 46.7%"
MBG_TITLE_EN = "Under this figure's convention: AI-off reachability shrinks 46.7%"
MBG_CAL_ZH = ("R_on=300 m / R_off=150 m / 服务带半宽 w=40 m 为本方案自设图面口径常数，"
              "无外部依据；改变任一常数将改变全部读数")
MBG_CAL_EN = ("R_on = 300 m / R_off = 150 m / service-band half-width w = 40 m are "
              "figure-level constants set by this proposal itself, with no external "
              "basis; changing any one of them changes every reading here.")

FACE = re.compile(r"base64,([A-Za-z0-9+/=]+)\)")


def cmap_of(path):
    src = open(path, encoding="utf-8").read()
    cps = set()
    for m in FACE.finditer(src):
        f = TTFont(io.BytesIO(base64.b64decode(m.group(1))))
        cps |= set(f.getBestCmap())
    return cps, len(FACE.findall(src))


for k, p in HTML.items():
    cps, nfaces = cmap_of(p)
    need = ATTR_ZH if k.endswith("zh") else ATTR_EN
    if k.startswith("mbg"):
        need += MBG_TITLE_ZH + MBG_CAL_ZH if k.endswith("zh") else MBG_TITLE_EN + MBG_CAL_EN
    miss = sorted({c for c in need if ord(c) > 32 and ord(c) not in cps})
    print(f"{k:8s} faces={nfaces} cmap={len(cps):4d} missing={len(miss):3d} "
          f"{''.join(miss)}")
