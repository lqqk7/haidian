#!/usr/bin/env python3
"""生成 visual/assets/cjk-webfont.css：把 woff2 子集以 data URI 内嵌为 @font-face。"""
import base64, sys, os, hashlib

WOFF2 = sys.argv[1]
OUT = sys.argv[2]
FAMILY = "ESJZ Sans Subset"
# 排除 U+00B7 · / U+2013 – / U+2014 — / U+2018-2019 ‘’ / U+201C-201D “” / U+2026 …
# 这六类西文排印标点由页面既有西文字体栈承担，避免中文字面把英文页的破折号与引号改宽。
URANGE = "U+A0-B6,U+B8-2012,U+2015-2017,U+201A-201B,U+201E-2025,U+2027-10FFFF"

raw = open(WOFF2, 'rb').read()
assert raw[:4] == b'wOF2', 'not a woff2 file'
b64 = base64.b64encode(raw).decode('ascii')
css = (
 "/* 万感京张 · 中文离线字体子集（随包自足，不依赖任何系统字体或远程资源）\n"
 "   来源：Source Han Sans SC 2.005R Regular（Adobe，SIL Open Font License 1.1）\n"
 "   子集与更名依据、上游 URL 与哈希：visual/assets/cjk-webfont-provenance.json\n"
 "   许可正本（逐字节可重建）：visual/assets/font-license-ofl.json\n"
 "   按 OFL 1.1「Reserved Font Name」条款，本子集属 Modified Version，\n"
 "   已改名为 \"" + FAMILY + "\"，不使用保留名 \"Source\"。 */\n"
 "@font-face{\n"
 "  font-family:\"" + FAMILY + "\";\n"
 "  font-style:normal;\n"
 "  font-weight:400;\n"
 "  font-display:swap;\n"
 "  src:url(data:font/woff2;base64," + b64 + ") format(\"woff2\");\n"
 "  unicode-range:" + URANGE + ";\n"
 "}\n"
 "/* 浏览器 UA 样式表给 code/pre/kbd/samp 指定 monospace，该声明会绕过页面自身的\n"
 "   字体栈：这些元素里的汉字因此仍会退回系统字体。此处把子集前置到同一族链的首位，\n"
 "   其后保留完整的等宽字体栈；子集不含任何 ASCII 字形，西文与代码的等宽外观不受影响。 */\n"
 "code,pre,kbd,samp{\n"
 "  font-family:\"" + FAMILY + "\",ui-monospace,SFMono-Regular,Menlo,Consolas,\"Liberation Mono\",monospace;\n"
 "}\n"
)
open(OUT, 'w', encoding='utf-8').write(css)
print(f"{OUT}: {os.path.getsize(OUT)} bytes (woff2 {len(raw)} -> base64 {len(b64)})")
print("woff2 sha256", hashlib.sha256(raw).hexdigest())
