# -*- coding: utf-8 -*-
"""WP-81 交付一：在五张核心图版的图面最底层铺 OSM 路网底图。

原则
----
* 只做两件事：(a) 在每个地图 SVG 的第一个子元素位置插入底图 <g>；
  (b) 在图面角注位置追加一行 ODbL 署名。除 mobility-bluegreen 的标题与
  口径行按任务书指定改写外，既有矢量内容、标注与读数一字不动。
* 底图落位由各图版自己的投影算式反配准（geom_params.py 逐字复刻生成器）。
* 快照只含 highway / railway，不含建筑与水系；署名行如实写明。
"""
from __future__ import annotations
from pathlib import Path as _HaidianPath

import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import geom_params as GP          # noqa: E402
import osmbase                    # noqa: E402
import suppfont                   # noqa: E402

# 原 scratchpad 已被回收，页源与渲染器均迁至工具链目录 T；目录结构保持不变，
# 因此各 fig_*.py 的 SRC 相对路径（wpn2b/wp4b/out 等）一字不动。
SCR = os.path.dirname(HERE)
PKG = str(_HaidianPath(__file__).resolve().parents[3] / 'submissions/lqqk7/every-sense-jingzhang')
FIGDIR = os.path.join(PKG, "assets/figures")
RENDER = os.path.join(SCR, "wp4b/render.js")
HTML_OUT = os.environ.get("W81_HTML_OUT") or os.path.join(HERE, "html")
PNG_OUT = os.environ.get("W81_PNG_OUT") or os.path.join(HERE, "png")

SNAPSHOT_TAG = "osm-fabric-snapshot-20260815"
ATTR = {
    "zh": "底图数据 © OpenStreetMap 贡献者，ODbL 1.0；快照 " + SNAPSHOT_TAG
          + "（仅含路网与轨道）",
    "en": "Basemap data © OpenStreetMap contributors, ODbL 1.0; snapshot "
          + SNAPSHOT_TAG + " (roads and rail only)",
}

# 按图面比例尺挑层：底图不得盖过主体，密度随 m/px 收敛
def layers_for(mpp):
    if mpp >= 7.0:
        return ["subway", "mid", "major", "rail"]
    if mpp >= 4.0:
        return ["minor", "subway", "mid", "major", "rail"]
    return osmbase.LAYER_ORDER


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def attr_text(lang, x, y, anchor="end", size=12.0, halo=3.0, fill="#8a8a8a"):
    return (f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-size="{size}" '
            f'fill="{fill}" stroke="#fbfaf6" stroke-width="{halo}" '
            f'paint-order="stroke" font-family="SHS">{esc(ATTR[lang])}</text>')


# --------------------------------------------------------------- SVG 定位工具
def svg_span(html, start_tag, occurrence=0):
    """返回第 occurrence 个 start_tag 对应的 (开标签结束位置, </svg> 起始位置)。"""
    pos = -1
    for _ in range(occurrence + 1):
        pos = html.index(start_tag, pos + 1)
    open_end = pos + len(start_tag)
    close = html.index("</svg>", open_end)
    assert "<svg" not in html[open_end:close], "地图 SVG 内出现嵌套 svg"
    return open_end, close


def insert_base(html, start_tag, spec, occurrence=0, after=None, tail=""):
    """在指定地图 SVG 内插入底图（最底层）与角注（最上层）。"""
    open_end, close = svg_span(html, start_tag, occurrence)
    ins = open_end
    if after:
        k = html.index(after, open_end)
        assert k < close
        ins = k + len(after)
    g = osmbase.basemap_svg(
        spec["to_px"], spec["clip"],
        px_scale=spec.get("px_scale", 1.0),
        vector_effect=spec.get("vector_effect", False),
        layers=spec["layers"], opacity=spec.get("opacity"))
    return html[:ins] + g + html[ins:close] + tail + html[close:]


def run(cmd, **kw):
    r = subprocess.run(cmd, capture_output=True, text=True, **kw)
    if r.returncode:
        raise SystemExit("FAILED %s\n%s\n%s" % (cmd, r.stdout, r.stderr))
    return r.stdout


def finish(html, name, lang, extra_text=""):
    """补字 + 落盘 + 渲染 + 打包。"""
    css, miss = suppfont.face_css(html, ATTR[lang] + extra_text)
    if css:
        assert "</style>" in html
        html = html.replace("</style>", css + "</style>", 1)
    os.makedirs(HTML_OUT, exist_ok=True)
    os.makedirs(PNG_OUT, exist_ok=True)
    hp = os.path.join(HTML_OUT, f"{name}-{lang}.html")
    with open(hp, "w", encoding="utf-8") as f:
        f.write(html)
    raw = os.path.join(PNG_OUT, f"{name}-{lang}.raw.png")
    run(["node", RENDER, "png", hp, raw, "1200", "750", "4"])
    return hp, raw, miss
