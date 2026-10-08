# -*- coding: utf-8 -*-
"""补字字体：只覆盖图版原有子集里没有的码位。

原图版内嵌的三个 SHS 子集（400/500/700）是由 OTF 转 glyf 后再切的，转换参数已
随 mkfont.py 一同散佚，重建会改动**全部**既有字形的轮廓。因此本模块不重建原子
集，而是另外生成一份只含缺字的 Source Han Sans SC 子集，用 CSS unicode-range
把它精确限定在缺字码位上追加到 @font-face 列表末尾——既有字符的匹配结果不可能
被改变，图面既有文字逐像素不变。
"""
from __future__ import annotations
from pathlib import Path as _HaidianPath

import base64
import io
import os
import re
import subprocess
import tempfile

FONT_DIR = "/Users/tutu/Library/Fonts"
SRC = {"400": "SourceHanSansSC-Regular.otf",
       "500": "SourceHanSansSC-Medium.otf",
       "700": "SourceHanSansSC-Bold.otf"}
PYFTSUBSET = str(_HaidianPath(__file__).resolve().parents[1] / 'venv/bin/pyftsubset')
CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fontcache")
FACE_RE = re.compile(r"base64,([A-Za-z0-9+/=]+)\)")


def existing_codepoints(html):
    """图版已内嵌子集覆盖的码位集合。"""
    from fontTools.ttLib import TTFont
    cps = set()
    for m in FACE_RE.finditer(html):
        f = TTFont(io.BytesIO(base64.b64decode(m.group(1))))
        cps |= set(f.getBestCmap())
    return cps


def _subset(weight, chars):
    os.makedirs(CACHE, exist_ok=True)
    key = "%s-%s" % (weight, "".join(sorted(chars)).encode("utf-8").hex()[:40])
    out = os.path.join(CACHE, key + ".otf")
    if not os.path.exists(out):
        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False,
                                         encoding="utf-8") as t:
            t.write("".join(sorted(chars)))
            tp = t.name
        subprocess.run([PYFTSUBSET, os.path.join(FONT_DIR, SRC[weight]),
                        "--text-file=" + tp, "--output-file=" + out,
                        "--layout-features=", "--no-hinting", "--desubroutinize",
                        "--drop-tables+=BASE,vhea,vmtx"],
                       check=True, capture_output=True)
        os.unlink(tp)
    return out


def face_css(html, extra_text):
    """返回追加用的 @font-face CSS；不缺字则返回空串。"""
    have = existing_codepoints(html)
    miss = sorted({c for c in extra_text if ord(c) > 32 and ord(c) not in have})
    if not miss:
        return "", []
    ur = ",".join("U+%04X" % ord(c) for c in miss)
    css = []
    for w in ("400", "500", "700"):
        b = base64.b64encode(open(_subset(w, miss), "rb").read()).decode()
        css.append(f"@font-face{{font-family:SHS;font-weight:{w};font-style:normal;"
                   f"src:url(data:font/otf;base64,{b}) format('opentype');"
                   f"unicode-range:{ur}}}")
    return "".join(css), miss


def full_face_css(text):
    """核验图组是新出的图版，没有既有渲染要保，直接切一份完整子集内嵌。"""
    chars = {c for c in text if ord(c) > 31}
    css = []
    for w in ("400", "500", "700"):
        b = base64.b64encode(open(_subset(w, chars), "rb").read()).decode()
        css.append(f"@font-face{{font-family:SHS;font-weight:{w};font-style:normal;"
                   f"src:url(data:font/otf;base64,{b}) format('opentype')}}")
    return "".join(css)
