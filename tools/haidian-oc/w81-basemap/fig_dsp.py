# -*- coding: utf-8 -*-
"""07 dual-state-plan：AI 开启 / AI 关闭两幅并置底盘，各加 OSM 路网底图。

两幅由同一个 base_svg() 生成，字符串恒等；底图同样以恒等的字符串插入两幅，
保证「同一底盘、同一比例、同一构图」这条本图自述的性质不被破坏。
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_figs import (SCR, attr_text, finish, insert_base, layers_for)  # noqa: E402
import geom_params as GP  # noqa: E402

SRC = os.path.join(SCR, "wpv70/dsp")
TAG = ('<svg class="mp" viewBox="0 0 1150 177" width="1150" height="177" '
       'shape-rendering="geometricPrecision">')

for lang in ("zh", "en"):
    html = open(os.path.join(SRC, f"dsp-{lang}.html"), encoding="utf-8").read()
    assert html.count(TAG) == 2
    p = GP.dual_state()
    spec = dict(to_px=p["to_px"], clip=p["clip"], layers=layers_for(p["mpp"]))
    # 两幅都铺底图；署名只出一次，落在下幅底部空楔形区：
    # 场地边界折线在 x 348..802 段位于 y 146..166 之间，其下方直到 SVG 底边
    # (y=177) 只有底图，既有要素与叠层构件均不进入（逐条核过要素包围盒）。
    html = insert_base(html, TAG, spec, occurrence=0)
    html = insert_base(html, TAG, spec, occurrence=1,
                       tail=attr_text(lang, 575, 174.5, anchor="middle"))
    hp, raw, miss = finish(html, "dual-state-plan", lang)
    print(lang, "mpp=%.2f" % p["mpp"], "补字", "".join(miss) or "无")
