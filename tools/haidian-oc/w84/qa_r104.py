# -*- coding: utf-8 -*-
"""交付 ⑤：qa-proofing-record.json 的 R1-04 条目按本轮实测口径更新。

本轮量测（w84/typescan.js，2026-08-18）
--------------------------------------
对 A0 双语展板全 12 板的页源逐元素扫描：取每个自身持有非空文本节点、且可见
（display 非 none、visibility 非 hidden、opacity 非 0、盒宽高均 > 0）的元素的
computedStyle font-size，按 px × 0.75 = pt 换算。共 484 项读数，下限 13.606 px
= 10.20 pt，页脚 15.118 px = 11.34 pt，上限 166.299 px = 124.72 pt。

与原登记值 8.51 pt 的关系（保守披露，不宣称推翻旧值）
--------------------------------------------------
原值出自 2026-08-12 的 128 项台账，该台账未随本轮重建，无法逐项复核；两轮的
元素集合与筛选口径不同，读数不可直接互换。8.51 pt = 3 mm，对应板面上重点区
插图标注的 CSS 声明（.kai-sb span）；该插图在此后的板面改版中已不再出现——12 板
中 class 以 kai 开头的元素计数均为 0，规则成为未命中的残留声明——故当前板面上
不存在该档字号。本条目只登记当前板面的实测结果，并写明旧台账未重建。

只改 R1-04 一条，文件其余内容与格式（缩进、键序）不动。
"""
from __future__ import annotations
from pathlib import Path as _HaidianPath

import json
import os
import subprocess

PKG = str(_HaidianPath(__file__).resolve().parents[3] / 'submissions/lqqk7/every-sense-jingzhang')
QA = os.path.join(PKG, "visual/assets/qa-proofing-record.json")

NEW = {
    "method_zh": "对生成 A0 板面的 DOM 逐元素扫描：取每个自身持有非空文本节点、且可见"
                 "（display 非 none、visibility 非 hidden、opacity 非 0、盒宽高均大于 0）"
                 "的元素的 computedStyle font-size，按 px × 0.75 = pt 换算，形成读数台账"
                 "并取下限。SVG 内注记与以 JPEG 嵌入的图版内部文字不计入本项，分别由 "
                 "R1-03、R1-05 登记",
    "method_en": "Element-by-element scan of the DOM that generates the A0 boards: for every "
                 "element that owns a non-empty text node and is visible (display not none, "
                 "visibility not hidden, opacity not 0, box wider and taller than 0), read "
                 "computedStyle font-size, convert with px x 0.75 = pt, compile a reading "
                 "register and take the floor. Annotations inside SVG and text inside the "
                 "JPEG-embedded plates are outside this item and are registered under "
                 "R1-03 and R1-05",
    "tool_zh": "typescan.js（Playwright + DOM computedStyle 实测，px×0.75=pt 口径），"
               "本轮台账 484 项读数",
    "tool_en": "typescan.js (Playwright + DOM computedStyle measurement, px x 0.75 = pt "
               "basis), a register of 484 readings this round",
    "date": "2026-08-18",
    "result_zh": "版面文本字号下限 10.20 pt（13.606 px），页脚 11.34 pt（15.118 px）；"
                 "484 项读数全部落在 10.20—124.72 pt，逐板下限均为 10.20 pt（封面板"
                 "第 01 板下限 34.02 pt）",
    "result_en": "Layout text floor 10.20 pt (13.606 px), footer 11.34 pt (15.118 px); all "
                 "484 readings fall between 10.20 and 124.72 pt, and every board has the "
                 "same 10.20 pt floor except board 01, whose floor is 34.02 pt",
    "provenance_zh": "2026-08-18 元素级全量扫描（12 板 / 484 项读数）。原登记值 8.51 pt "
                     "出自 2026-08-12 的 128 项台账，该台账未随本轮重建，无法逐项复核，"
                     "两轮的元素集合与筛选口径不同，读数不可直接互换，故本条目不宣称"
                     "推翻旧值，只登记当前板面的实测结果。8.51 pt = 3 mm 对应重点区插图"
                     "标注的样式声明（.kai-sb span）；该插图在此后的板面改版中已不再"
                     "出现（12 板中 class 以 kai 开头的元素计数均为 0，规则成为未命中的"
                     "残留声明），故当前板面上不存在该档字号",
    "provenance_en": "Element-level full scan on 2026-08-18 (12 boards, 484 readings). The "
                     "previously registered 8.51 pt floor came from a register of 128 "
                     "readings dated 2026-08-12; that register was not rebuilt this round "
                     "and cannot be checked item by item, and the two rounds use different "
                     "element sets and selection rules, so the readings are not "
                     "interchangeable. This entry therefore does not claim to overturn the "
                     "earlier value, only to record what the boards measure today. The "
                     "8.51 pt figure equals 3 mm, the size declared for the key-area inset "
                     "labels (.kai-sb span); that inset no longer appears on the boards "
                     "after the later revisions (zero elements whose class begins with kai "
                     "on all 12 boards, leaving the rule as an unmatched declaration), so "
                     "that size class is not present on the current boards",
    "limitations_zh": "屏幕渲染量测；A0 展板的实际可读性还取决于张贴高度与观看距离，"
                      "本次未做现场观看距离验证。本项只覆盖页面文本层，不覆盖以 JPEG "
                      "嵌入的图版内部文字",
    "limitations_en": "A screen-rendered measurement; the actual legibility of the A0 "
                      "boards also depends on mounting height and viewing distance, and no "
                      "on-site viewing-distance verification was made this round. This item "
                      "covers the page text layer only, not text inside the JPEG-embedded "
                      "plates",
}


def main():
    raw = open(QA, encoding="utf-8").read()
    d = json.loads(raw)
    hit = None
    for rec in d["records"]:
        for c in rec["checks"]:
            if c["id"] == "R1-04":
                hit = c
    assert hit is not None, "未找到 R1-04"
    before = {k: hit.get(k) for k in NEW}
    for k, v in NEW.items():
        assert k in hit, "R1-04 缺键 %s" % k
        hit[k] = v
    open(QA, "w", encoding="utf-8").write(
        json.dumps(d, ensure_ascii=False, indent=1) + "\n")
    for k in NEW:
        print("  %-16s\n     旧 %s\n     新 %s" % (k, str(before[k])[:110], str(NEW[k])[:110]))
    # 只改这一条：diff 行数核对
    n = int(subprocess.run(["git", "-C", PKG, "diff", "--numstat", "--",
                            "visual/assets/qa-proofing-record.json"],
                           capture_output=True, text=True).stdout.split()[0] or 0)
    print("  qa-proofing-record.json 改动行数 +%d" % n)


if __name__ == "__main__":
    main()
