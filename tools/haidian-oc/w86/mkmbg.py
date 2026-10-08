# -*- coding: utf-8 -*-
"""重出主图页源 wpr6/mbg/fig-{zh,en}.html（mobility-bluegreen 的来源）。

前提：该页源的生成器（WP-R6 版式）在旧临时目录被回收时散佚，工具链与旧目录里都
只剩页源本身与文案表 copy2.py。因此本脚本不重建生成器，而是就地改写页源里**确实
随几何变化的两类内容**，其余字节一律不碰：

  A. 三幅面板的地图 SVG —— 整块重画。
     重画不是另写一套画法：这三块与审计图版出自同一个 wpr6/wpe2/build.py 的
     map_svg()，只是 scale 取 4.5 m/px。自检 `--check` 用 geom.old.pkl 复现三块
     旧 SVG，与备份逐字节比对通过后才允许写新几何。
  B. 四张读数卡与前三行断点表里的数字 —— 按 geom.pkl 的 summary / rows 现算。

取景框（面板 viewBox）保持原值不改，理由有二：
  * 原值可由 window(旧 content_bounds, wpx, hpx, 4.5) 逐位复现，说明算式已确认；
    代入新 content_bounds 后 K1 位移 0.23 px、K2 位移 0、K3 位移 1.9 px，K3 的
    位移还不是路网加密造成的，而是 key_areas.geojson 的 PROV-KEY-003 早已与旧
    pkl 不一致（见 mkgeom.py 报告）；
  * 取景框一动，覆盖层里的节点圆点、引线、标签盒与 300/150 m 标注全部要重排，
    而这套排版的生成器正是散佚的那一份。
新的 AI 开启域并集在三幅取景框内均有余量（最紧的一侧 K1 上边 18.3 m），不会被裁。

标题不在此处改：fig_mbg.py 负责把标题改写为带口径的版本。
"""
from __future__ import annotations
from pathlib import Path as _HaidianPath

import argparse
import os
import re
import shutil
import sys

T = str(_HaidianPath(__file__).resolve().parents[1])
HERE = os.path.dirname(os.path.abspath(__file__))
MBG = os.path.join(T, "wpr6/mbg")
WPE2 = os.path.join(T, "wpr6/wpe2")
sys.path.insert(0, WPE2)
sys.path.insert(0, os.path.join(T, "w82"))
import fixfont  # noqa: E402

ORX, ORY = 444000.0, 4428000.0
PANELS = [("K1", ["OP-01", "OP-05", "OP-07", "OP-10"]),
          ("K2", ["OP-02", "OP-03", "OP-06"]),
          ("K3", ["OP-04", "OP-08", "OP-09"])]
GATE = {"G0": "#68787b", "G1": "#d6a13b", "G2": "#6b5b95", "G3": "#d76450"}

MP = re.compile(r'<svg class="mp" viewBox="([-\d. ]+)" width="(\d+)" height="(\d+)" '
                r'data-ox="[^"]*" data-oy="[^"]*" data-mpp="([\d.]+)"[^>]*>(.*?)</svg>',
                re.S)
TR = re.compile(r'<div class="tr">.*?</span></div>', re.S)

ROW_T = ('<div class="tr"><span class="c0">%d</span><span class="c1">%s</span>'
         '<span class="c2" style="color:%s;border-color:%s">%s</span>'
         '<span class="c3"><i style="width:%.1f%%"></i><b>%s</b></span>'
         '<span class="c4">%.1f%%</span></div>')


def panels_svg(build, html):
    """整块替换三幅面板 SVG；取景框沿用页源里印着的 viewBox。"""
    blocks = MP.findall(html)
    assert len(blocks) == 3, "面板 SVG 命中 %d 块" % len(blocks)
    out, pos = [], 0
    for m, (tag, mem) in zip(MP.finditer(html), PANELS):
        vx, vy, vw, vh = [float(v) for v in m.group(1).split()]
        win = (vx + ORX, ORY - vy - vh, vx + ORX + vw, ORY - vy)
        svg, _ = build.map_svg(win, int(m.group(2)), int(m.group(3)),
                               float(m.group(4)), sorted(mem), tag)
        out.append(html[pos:m.start()])
        out.append(svg)
        pos = m.end()
    out.append(html[pos:])
    return "".join(out)


def numbers(build, html, old_html):
    """四张读数卡 + 前三行断点表。旧串逐一断言命中一次，避免误伤。"""
    S, R = build.SUM, build.ROWS
    nf = build.nf
    subs = [("<b>482,267</b>", "<b>%s</b>" % nf(S["union_on_sqm"])),
            ("<b>257,208</b>", "<b>%s</b>" % nf(S["union_off_sqm"])),
            ("<b>225,058</b>", "<b>%s</b>" % nf(S["union_gap_sqm"])),
            ("<b>46.67</b>", "<b>%.2f</b>" % (S["union_gap_share"] * 100)),
            ("4.23%", "%.2f%%" % (S["union_on_share_of_site"] * 100))]
    for o, n in subs:
        assert html.count(o) == 1, ("锚点命中 %d 次" % html.count(o), o)
        html = html.replace(o, n)

    mx = max(r["area_gap_sqm"] for r in R)
    rows = "".join(
        ROW_T % (r["rank"], r["id"], GATE[r["gate"]], GATE[r["gate"]], r["gate"],
                 r["area_gap_sqm"] / mx * 100, nf(r["area_gap_sqm"]),
                 r["gap_share"] * 100)
        for r in R[:3])
    ms = list(TR.finditer(html))
    assert len(ms) == 3, "断点行命中 %d 处（应为前三行）" % len(ms)
    html = html[:ms[0].start()] + rows + html[ms[2].end():]
    for anchor in ("04 / KEPT UNKNOWN", "03 / FIRST BREAKS", 'class="ftw"'):
        assert anchor in html, "改写吃掉了 %s" % anchor

    # 面板里的 hot 标记 = 前三名节点；集合若变了，覆盖层要重排，此处必须停下。
    hot = {r["id"] for r in R[:3]}
    was = set(re.findall(r'class="nl hot"[^>]*>.*?(OP-\d\d)', old_html))
    assert hot == was, "前三名节点由 %s 变为 %s：覆盖层 hot 标记需重排" % (was, hot)
    return html


def run(check=False):
    import build  # noqa: E402
    for lang in ("zh", "en"):
        old_p = os.path.join(HERE, "mbg-fig-%s.old.html" % lang)
        old = open(old_p, encoding="utf-8").read()
        if check:
            got = panels_svg(build, old)
            print("check %s: 面板 SVG %s"
                  % (lang, "逐字节一致 ✓" if got == old else "不一致 ✗"))
            continue
        h = numbers(build, panels_svg(build, old), old)
        out = os.path.join(MBG, "fig-%s.html" % lang)
        open(out, "w", encoding="utf-8").write(h)
        print("%s  %d -> %d B  补字 %s"
              % (os.path.basename(out), len(old), len(h),
                 "".join(fixfont.patch(out)) or "无"))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true",
                    help="用 geom.old.pkl 复现三幅旧面板 SVG，不落盘")
    a = ap.parse_args()
    if a.check:
        live = os.path.join(WPE2, "geom.pkl")
        bak = live + ".livebak"
        shutil.copy2(live, bak)
        shutil.copy2(os.path.join(HERE, "geom.old.pkl"), live)
        try:
            run(check=True)
        finally:
            shutil.move(bak, live)
    else:
        run()
