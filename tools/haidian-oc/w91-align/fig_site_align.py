# -*- coding: utf-8 -*-
"""WP-91：site-overview 双语图版叠遗址公园廊道参考线。

在 w81-basemap/fig_site.py 的既有链条上只加三件事，取景（geom_params._site_ring
与 site_overview()）一字不动：

  1. 在 OSM 底图之上、全部设计线位之下，加一条灰色点划线——快照中「京包线」与
     「京包客专线」共 23 条 way 合成的铁路廊道中心线，裁剪至图带矩形之内；
  2. 图例增一行，写明该线是 OSM 铁路廊道代理而不是公园边界；
  3. 图幅顶部空白带加两行偏差标注，图注补一句代理声明。

全部数值取自 visual/assets/alignment-reference.json，不在本脚本内另行计算。
"""
from __future__ import annotations

import json
import os
import sys

T = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(T, "w81-basemap"))

from build_figs import (SCR, attr_text, finish, layers_for, svg_span)  # noqa: E402
import geom_params as GP                                              # noqa: E402
import osmbase                                                        # noqa: E402

SRC = os.path.join(SCR, "wpn2b/wp4b/out")
PKG = GP.PKG
TAG = '<svg viewBox="0 0 1140 264" width="1140" height="264" font-family="SHS">'
GROUND = '<rect width="1140" height="264" fill="#fbfaf6"/>'
SITE_RECT = ('<rect x="22.0" y="56.6" width="1096.0" height="150.8" '
             'fill="#ffffff" stroke="#e2ddd0" stroke-width="1.4"/>')
BAND = (22.0, 56.6, 1118.0, 207.4)

CORRIDOR_COLOUR = "#8a8a8a"
CORRIDOR_DASH = "11 3.5 2.5 3.5"

# 图例小样：CSS 无点划线原语，用重复渐变还原 SVG 的 dasharray 观感
LEGEND_SWATCH = ("height:3px;background:repeating-linear-gradient(90deg,"
                 "#8a8a8a 0 11px,transparent 11px 14.5px,#8a8a8a 14.5px 17px,"
                 "transparent 17px 20.5px)")

LEGEND_ROW = ('<div class="lrow"><span class="lm"><i style="%s"></i></span>'
              '<span class="ls">%s</span></div>')
LEGEND_TEXT = {
    "zh": "遗址公园廊道参考线 / Heritage corridor ref.",
    "en": "Heritage corridor reference (OSM rail proxy)",
}
LEGEND_ANCHOR = {
    "zh": '<span class="ls">重点区范围 / Key area</span></div>',
    "en": '<span class="ls">Key area</span></div>',
}

CAPTION_OLD = {
    "zh": "OSM 路网底图上的概念结构图 · 全部线位、框线与节点由提交 GeoJSON 现算落位",
    "en": "Concept structure on an OSM road-network basemap; every line, frame and node placed from the submitted GeoJSON",
}
CAPTION_NEW = {
    "zh": ("OSM 路网底图上的概念结构图 · 线位、框线与节点由提交 GeoJSON 现算落位 · "
           "灰点划线为 OSM 铁路廊道代理，非公园边界"),
    "en": ("Concept structure on an OSM basemap, from the submitted GeoJSON; "
           "grey dash-dot = OSM rail proxy, not a park boundary"),
}


def _read_readings():
    with open(os.path.join(PKG, "visual/assets/alignment-reference.json"),
              encoding="utf-8") as f:
        d = json.load(f)
    r = {x["id"]: x for x in d["readings"]}
    return {
        "median": r["ALN-01"]["reading"]["median_m"],
        "p90": r["ALN-01"]["reading"]["p90_m"],
        "total": r["ALN-03"]["reading"]["corridor_total_length_m"],
        "outside": r["ALN-03"]["reading"]["outside_site_length_m"],
        "ways": d["corridor_geometry"]["way_count"],
    }


def _sig3(v):
    """按包内显示位数规则取三位有效数字，千位加分隔符。"""
    n = int(round(v, -(len(str(int(v))) - 3))) if v >= 100 else int(round(v))
    return format(n, ",")


def annotation_lines(lang, R):
    med, p90 = _sig3(R["median"]), _sig3(R["p90"])
    tot, out = _sig3(R["total"]), _sig3(R["outside"])
    if lang == "zh":
        return ["遗址公园廊道参考线（OSM 铁路廊道代理，非公园边界）",
                "主脊中位偏差 %s m · P90 %s m · 廊道 %s m 中 %s m 在总体范围外"
                % (med, p90, tot, out)]
    return ["Heritage corridor reference line (OSM rail proxy, not a park boundary)",
            "Spine median offset %s m · P90 %s m · %s m of %s m outside the overall extent"
            % (med, p90, out, tot)]


def corridor_svg(to_px):
    """廊道参考线 <g>：只用快照几何，裁剪至图带矩形。"""
    meta, ways, _nodes = osmbase.load_snapshot()
    rows = sorted([w for w in ways if w[3] in ("京包线", "京包客专线")],
                  key=lambda w: (w[3], w[0]))
    x0, y0, x1, y1 = BAND
    out = ['<clipPath id="jzband"><rect x="22.0" y="56.6" width="1096.0" '
           'height="150.8"/></clipPath>',
           '<g clip-path="url(#jzband)" fill="none" stroke="%s" stroke-width="2.4" '
           'stroke-dasharray="%s" stroke-linecap="round" stroke-linejoin="round">'
           % (CORRIDOR_COLOUR, CORRIDOR_DASH)]
    drawn = 0
    for row in rows:
        pts = [to_px(c[0], c[1]) for c in row[5]]
        keep, run = [], []
        for i, p in enumerate(pts):
            inside = x0 - 6 <= p[0] <= x1 + 6 and y0 - 6 <= p[1] <= y1 + 6
            if inside:
                if not run and i:
                    run.append(pts[i - 1])
                run.append(p)
            else:
                if run:
                    run.append(p)
                    keep.append(run)
                    run = []
        if run:
            keep.append(run)
        for r in keep:
            if len(r) < 2:
                continue
            out.append('<polyline points="%s"/>'
                       % " ".join("%.1f,%.1f" % (x, y) for x, y in r))
            drawn += 1
    out.append("</g>")
    return "".join(out), len(rows), drawn


def annotation_svg(lang, R):
    a, b = annotation_lines(lang, R)
    t = []
    for y, s in ((25.0, a), (41.0, b)):
        t.append('<text x="1110" y="%.1f" text-anchor="end" font-size="12" '
                 'fill="#68787b" stroke="#fbfaf6" stroke-width="3" '
                 'paint-order="stroke" font-family="SHS">%s</text>' % (y, s))
    return "".join(t)


def build(lang, R):
    html = open(os.path.join(SRC, "site-%s.html" % lang), encoding="utf-8").read()
    p = GP.site_overview()
    assert GROUND in html and SITE_RECT in html

    open_end, close = svg_span(html, TAG, 0)
    k = html.index(SITE_RECT, open_end)
    assert k < close
    ins = k + len(SITE_RECT)
    base = osmbase.basemap_svg(p["to_px"], p["clip"], layers=layers_for(p["mpp"]))
    corr, n_ways, n_parts = corridor_svg(p["to_px"])
    tail = attr_text(lang, 6, 257, anchor="start") + annotation_svg(lang, R)
    html = html[:ins] + base + corr + html[ins:close] + tail + html[close:]

    # 图例增一行
    anchor = LEGEND_ANCHOR[lang]
    assert html.count(anchor) == 1
    html = html.replace(anchor, anchor + (LEGEND_ROW % (LEGEND_SWATCH,
                                                        LEGEND_TEXT[lang])))
    # 图注补代理声明
    assert html.count(CAPTION_OLD[lang]) == 1
    html = html.replace(CAPTION_OLD[lang], CAPTION_NEW[lang])

    extra = "".join(annotation_lines(lang, R)) + LEGEND_TEXT[lang] + CAPTION_NEW[lang]
    if lang == "zh":
        extra += "上的"
    hp, raw, miss = finish(html, "site-overview", lang, extra_text=extra)
    print("%s mpp=%.2f 廊道 %d way / %d 段可见 · 补字 %s -> %s"
          % (lang, p["mpp"], n_ways, n_parts, "".join(miss) or "无", raw))
    return raw


if __name__ == "__main__":
    R = _read_readings()
    print("读数：中位 %.3f · P90 %.3f · 全长 %.3f · 范围外 %.3f"
          % (R["median"], R["p90"], R["total"], R["outside"]))
    for lang in ("zh", "en"):
        build(lang, R)
