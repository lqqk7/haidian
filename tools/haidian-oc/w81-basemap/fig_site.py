# -*- coding: utf-8 -*-
"""01 site-overview：走廊图带加 OSM 路网底图。"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_figs import (SCR, attr_text, finish, insert_base, layers_for)  # noqa: E402
import geom_params as GP  # noqa: E402

SRC = os.path.join(SCR, "wpn2b/wp4b/out")
TAG = '<svg viewBox="0 0 1140 264" width="1140" height="264" font-family="SHS">'
GROUND = '<rect width="1140" height="264" fill="#fbfaf6"/>'
# 场地边界白底矩形是图带的第一个绘制元素，底图插在它之后才能在场地内可见；
# 相对于路网、重点区框、节点与全部标注，底图仍是最底层。
SITE_RECT = ('<rect x="22.0" y="56.6" width="1096.0" height="150.8" '
             'fill="#ffffff" stroke="#e2ddd0" stroke-width="1.4"/>')

for lang in ("zh", "en"):
    html = open(os.path.join(SRC, f"site-{lang}.html"), encoding="utf-8").read()
    p = GP.site_overview()
    spec = dict(to_px=p["to_px"], clip=p["clip"], layers=layers_for(p["mpp"]))
    assert GROUND in html and SITE_RECT in html
    html = insert_base(html, TAG, spec, after=SITE_RECT,
                       tail=attr_text(lang, 6, 257, anchor="start"))
    # 图注改写引入的「上、的」不在原内嵌子集里，一并交给补字机制
    hp, raw, miss = finish(html, "site-overview", lang, extra_text=("上的" if lang == "zh" else ""))
    print(lang, "mpp=%.2f" % p["mpp"], "补字", "".join(miss) or "无", "->", raw)
