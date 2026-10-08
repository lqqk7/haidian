# -*- coding: utf-8 -*-
"""02 land-use-structure：主图带 + 三张接口插图，各自加 OSM 路网底图。"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_figs import (SCR, attr_text, finish, insert_base, layers_for)  # noqa: E402
import geom_params as GP  # noqa: E402

SRC = os.path.join(SCR, "wpn2b/wp4b/out")
MAIN_TAG = '<svg viewBox="0 0 1140 202.5" width="1140" height="202.5" font-family="SHS">'
MAIN_GROUND = '<rect width="1140" height="202.5" fill="#fbfaf6"/>'
INSET_TAG = '<svg viewBox="0 0 370 134" width="370" height="134" font-family="SHS">'
INSET_GROUND = '<rect width="370" height="134" fill="#fbfaf6"/>'

for lang in ("zh", "en"):
    html = open(os.path.join(SRC, f"lu-{lang}.html"), encoding="utf-8").read()
    assert html.count(INSET_TAG) == 3

    p = GP.landuse_main()
    html = insert_base(html, MAIN_TAG,
                       dict(to_px=p["to_px"], clip=p["clip"],
                            layers=layers_for(p["mpp"])),
                       after=MAIN_GROUND,
                       tail=attr_text(lang, 1134, 197))

    for i in range(3):
        q = GP.landuse_inset(i)
        html = insert_base(html, INSET_TAG,
                           dict(to_px=q["to_px"], clip=q["clip"],
                                layers=layers_for(q["mpp"])),
                           occurrence=i, after=INSET_GROUND)

    # 图注改写引入的「上、的」不在原内嵌子集里，一并交给补字机制
    hp, raw, miss = finish(html, "land-use-structure", lang, extra_text=("上的" if lang == "zh" else ""))
    print(lang, "main mpp=%.2f inset mpp=%.2f" % (p["mpp"], GP.landuse_inset(0)["mpp"]),
          "补字", "".join(miss) or "无")
