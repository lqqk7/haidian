# -*- coding: utf-8 -*-
"""05 mobility-bluegreen：三幅重点区可达域图加 OSM 路网底图 + 口径改写。

任务书指定的两处文字变更：
1. 主标题改为「按本图自设口径：AI 关闭后可达域收缩 49.3%」——49.3% 即 geom.pkl
   summary 的 union_gap_share = 0.493318（roads.geojson 按真实走向加密后重算），与
   本图 02 / GAP 卡已印的 49.33 % 同源，只是把它从卡片提到标题并加上「按本图自设
   口径」的限定。
   标题不采用正文图注的长式《按本图自设口径，AI 关闭后可达域收缩 49.3%：差集是审计
   靶区，不是达标声明》：.hd 是固定 94 px 的页头带，h1 为 26 px / line-height 1.22 /
   max-width 840 px，长式两语均折成两行、第二行压到下方图例带上（w86/titlefit.py 实
   测）。放长式须抬高 .hd 并压缩 .wrap，而该页源的生成器已散佚，等于重排整页。英文
   同理取一行内可容的最长式 "Self-set convention: AI off shrinks the reachable
   domain by 49.3%"（一行上限实测约 72 个字符）。
2. 图注区加一行自设常数声明。

版面容量（对原图逐像素扫描 + DOM 盒模型量测所得，两语分别核过）：
* CSS y 657–677 是全幅唯一的整行空带（20 px），放口径声明；
* .ftw 之下 zh 有 33 px / en 有 16 px 空白，其右侧到 .ftl 末行之间无墨，
  放 ODbL 署名。
两块都用 position:absolute 挂在 body 末尾，不进入任何 flex 流，既有元素盒
位置逐一复核不变。
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_figs import ATTR, esc, finish, insert_base, layers_for, SCR  # noqa: E402
import geom_params as GP  # noqa: E402

SRC = os.path.join(SCR, "wpr6/mbg")

TITLE = {
    "zh": ("<h1>AI 关闭后，可达域收缩近一半：差集是审计靶区，不是达标声明</h1>",
           "<h1>按本图自设口径：AI 关闭后可达域收缩 49.3%</h1>"),
    "en": ("<h1>AI off halves the reachable domain: the gap is an audit target, "
           "not a compliance claim</h1>",
           "<h1>Self-set convention: AI off shrinks the reachable domain by 49.3%</h1>"),
}
CAVEAT = {
    "zh": "R_on = 300 m / R_off = 150 m / 服务带半宽 w = 40 m 为本方案自设图面口径"
          "常数，无外部依据；改变任一常数将改变全部读数。",
    "en": "R_on = 300 m / R_off = 150 m / band half-width w = 40 m are figure-level "
          "constants set by this proposal itself, with no external basis; changing "
          "any one of them changes every reading here.",
}
# ODbL 署名行的纵向落位（CSS px，两语的 .ftw 行数不同）
ATTR_TOP = {"zh": 719.0, "en": 735.0}

MP = re.compile(r'<svg class="mp" viewBox="([-\d. ]+)"[^>]*>')

for lang in ("zh", "en"):
    html = open(os.path.join(SRC, f"fig-{lang}.html"), encoding="utf-8").read()

    # --- 1. 三幅面板铺底图 -------------------------------------------------
    tags = MP.findall(html)
    assert len(tags) == 3, tags
    for i, vb in enumerate(tags):
        vx, vy, vw, vh = [float(v) for v in vb.split()]
        q = GP.mobility_panel((vx, vy, vw, vh))
        tag = MP.findall(html)[i]
        full = re.search(r'<svg class="mp" viewBox="%s"[^>]*>' % re.escape(tag),
                         html).group(0)
        html = insert_base(html, full,
                           dict(to_px=q["to_px"], clip=q["clip"], layers=layers_for(4.5),
                                px_scale=4.5, vector_effect=True),
                           occurrence=0, after="</defs>")

    # --- 2. 标题改写 -------------------------------------------------------
    old, new = TITLE[lang]
    assert html.count(old) == 1
    html = html.replace(old, new)

    # --- 3. 口径声明 + ODbL 署名（绝对定位，不进流） ------------------------
    blocks = (
        '<div style="position:absolute;left:30px;top:659px;width:1140px;'
        'font-size:12px;line-height:1.35;font-weight:700;color:#d76450">'
        + esc(CAVEAT[lang]) + '</div>'
        '<div style="position:absolute;left:30px;top:%.1fpx;width:900px;'
        'font-size:12px;line-height:1.35;color:#68787b">' % ATTR_TOP[lang]
        + esc(ATTR[lang]) + '</div>')
    html = html.replace("</body>", blocks + "</body>", 1)

    hp, raw, miss = finish(html, "mobility-bluegreen", lang,
                           extra_text=new + CAVEAT[lang])
    print(lang, "补字", "".join(miss) or "无", "->", raw)
