# -*- coding: utf-8 -*-
"""重出审计图页源 wpr6/wpe2/fig-{zh,en}.html（mobility-bluegreen-audit 的来源）。

页源生成器 wpr6/wpe2/build.py 完好，数据全部来自 geom.pkl，故本脚本只做两件事：

1. 调 build.build(lang) 重出整篇文档；
2. 把文档里的 __FONTFACE__ 换回**原页源已内嵌的**三个 SHS 子集，并把 suppfont
   机制先前追加在 </style> 之前的补字 @font-face 原样接回。

第 2 步不是省事：build.fontface() 依赖旧临时目录里的 mkfont.py，该文件已散佚；
即便重建，子集轮廓会与既有页面全部字形不同（见 w81-basemap/suppfont.py 开头的
说明）。沿用原子集可保证除数字与几何外的图面像素不变；本次改动只换数字，不引入
新字符，缺字由 w82/fixfont.py 兜底。

自检：`python mkaud.py --check` 用 geom.old.pkl 复跑，产物必须与备份逐字节一致。
该自检在本次改动前跑通（两语均逐字节一致）；此后 fcopy.py 的 cal_rows 首行把网络
总长由 20 141 m 改为 22 859 m，再跑 --check 会在该串上如实报出一处差异。
"""
from __future__ import annotations
from pathlib import Path as _HaidianPath

import argparse
import hashlib
import importlib
import os
import pickle
import shutil
import sys

T = str(_HaidianPath(__file__).resolve().parents[1])
HERE = os.path.dirname(os.path.abspath(__file__))
WPE2 = os.path.join(T, "wpr6/wpe2")
sys.path.insert(0, WPE2)
sys.path.insert(0, os.path.join(T, "w82"))
import fixfont  # noqa: E402

CSS_HEAD = "\n*{box-sizing:border-box}"


def split_style(html):
    """(文档前半, 基础字体块, 文档后半模板用的补字块)。"""
    s = html.index("<style>") + len("<style>")
    e = html.index("</style>")
    st = html[s:e]
    i = st.index(CSS_HEAD)
    return st[:i], st[i:]


def face_and_tail(old_html, css_body):
    face, rest = split_style(old_html)
    assert rest.startswith(css_body), "页源 CSS 与生成器 CSS 不一致，先查 build.py"
    return face, rest[len(css_body):]


def run(check=False):
    import build  # noqa: E402  （模块级会读取 geom.pkl）
    importlib.reload(build)
    for lang in ("zh", "en"):
        old_p = os.path.join(HERE, "aud-fig-%s.old.html" % lang)
        old = open(old_p, encoding="utf-8").read()
        css_body = build.CSS + (build.EN_CSS if lang == "en" else "")
        face, tail = face_and_tail(old, css_body)
        doc = build.build(lang).replace("__FONTFACE__", face)
        doc = doc.replace("</style>", tail + "</style>", 1)
        out = os.path.join(WPE2, "fig-%s.html" % lang)
        if check:
            same = hashlib.sha256(doc.encode()).hexdigest() == \
                hashlib.sha256(old.encode()).hexdigest()
            print("check %s: %s" % (lang, "逐字节一致 ✓" if same else "不一致 ✗"))
            if not same:
                a, b = old, doc
                k = next((i for i in range(min(len(a), len(b))) if a[i] != b[i]), None)
                print("   首处差异 @%s\n   旧 %r\n   新 %r"
                      % (k, a[k - 60:k + 60], b[k - 60:k + 60]))
            continue
        open(out, "w", encoding="utf-8").write(doc)
        print("%s  %d B  补字 %s"
              % (os.path.basename(out), len(doc), "".join(fixfont.patch(out)) or "无"))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true",
                    help="用 geom.old.pkl 复跑并与备份比对，不落盘")
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
