#!/usr/bin/env python3
"""WP-E8 交付物：中文 HTML 的离线字体覆盖断言。

评审阻断（v9.7 request-changes）：`report/proposal.html` 与 `visual/index.html`
的中文在没有安装任何 CJK 字体的干净浏览器里大面积显示为方框（tofu）。根因是两份
HTML 的 font-family 栈只列了系统字体名，包内不携带任何可用的中文字面。

本脚本断言修复成立，任何一项不成立即退出码 1：

  A. 承载资产存在且合法：`visual/assets/cjk-webfont.css` 中的 `@font-face`
     data URI 能被 base64 解码，解码结果以 `wOF2` 魔数开头，且可被 fontTools
     作为完整字体打开。
  B. 覆盖为零缺字：四份 HTML 与 `visual/assets/*.js`（会向 DOM 注入文案）中出现的
     每一个非 ASCII 字符，都在该子集的 cmap 内。
  C. 字面排在字体栈首位：四份 HTML 的每一条 `font-family` 声明，第一个族名都是
     该子集族名。
  D. 引用可解析：每份 HTML 都以相对路径引用该 CSS，且该相对路径在磁盘上存在。
  E. unicode-range 例外如实登记：落在 unicode-range 之外的字符必须全部属于脚本内
     显式登记的西文排印标点白名单（这些字符由页面既有西文字体栈承担，任何带拉丁
     覆盖的字体都有它们）。出现白名单以外的例外即失败。

用法：
    font_coverage_check.py <包目录>
"""

from __future__ import annotations

import base64
import glob
import os
import re
import sys

from fontTools.ttLib import TTFont

FAMILY = "ESJZ Sans Subset"
CSS_REL = "visual/assets/cjk-webfont.css"

HTML_FILES = [
    "report/proposal.html",
    "report/proposal.en.html",
    "visual/index.html",
    "visual/index.en.html",
]
# 这两份样式表也给承载中文的场景元素设了显式 font-family，显式声明会盖掉 body 的
# 继承，因此同样要把子集族名前置，否则交互场景里的中文仍然退化为方框。
EXTRA_CSS_FILES = [
    "visual/assets/scene.css",
    "visual/assets/spine3d.css",
]

# 刻意排除在 unicode-range 之外的西文排印标点：· – — ‘ ’ “ ” …
# 排除理由：这八个码位在任何带拉丁覆盖的字体里都存在，交给页面既有西文字体栈渲染，
# 可避免中文字面把英文页的破折号与引号改成全角宽度。它们仍然被打进子集（B 项因此
# 仍为零缺字），只是 unicode-range 不认领。
PUNCT_EXEMPT = {0x00B7, 0x2013, 0x2014, 0x2018, 0x2019, 0x201C, 0x201D, 0x2026}

FONT_FACE_SRC_RE = re.compile(r"url\(data:font/woff2;base64,([A-Za-z0-9+/=]+)\)")
URANGE_RE = re.compile(r"unicode-range:\s*([^;}]+)")
FONT_FAMILY_RE = re.compile(r"font-family\s*:\s*([^;}]+)")
LINK_RE = re.compile(r'<link\b[^>]*\bhref\s*=\s*"([^"]+\.css)"', re.I)


def parse_unicode_range(text: str) -> list[tuple[int, int]]:
    spans: list[tuple[int, int]] = []
    for token in text.split(","):
        token = token.strip()
        if not token.upper().startswith("U+"):
            continue
        body = token[2:]
        if "-" in body:
            lo, hi = body.split("-", 1)
            spans.append((int(lo, 16), int(hi, 16)))
        else:
            spans.append((int(body, 16), int(body, 16)))
    return spans


def in_spans(code: int, spans: list[tuple[int, int]]) -> bool:
    return any(lo <= code <= hi for lo, hi in spans)


def main() -> int:
    if len(sys.argv) != 2:
        print("用法: font_coverage_check.py <包目录>")
        return 2
    base = os.path.abspath(sys.argv[1])
    failures: list[str] = []

    def chk(name: str, ok: bool, detail: str) -> None:
        print(("  OK   " if ok else "  FAIL ") + name + " — " + detail)
        if not ok:
            failures.append(name)

    # ---- A 承载资产 ----
    css_path = os.path.join(base, CSS_REL)
    if not os.path.isfile(css_path):
        chk("A1 CSS 存在", False, css_path + " 缺失")
        return 1
    css = open(css_path, encoding="utf-8").read()
    match = FONT_FACE_SRC_RE.search(css)
    chk("A1 CSS 存在且含 woff2 data URI", match is not None,
        f"{CSS_REL} {os.path.getsize(css_path)} 字节")
    if not match:
        return 1
    raw = base64.b64decode(match.group(1), validate=True)
    chk("A2 base64 可解码且为 woff2", raw[:4] == b"wOF2", f"解码 {len(raw)} 字节, 魔数 {raw[:4]!r}")
    tmp = os.path.join(os.path.dirname(css_path) or ".", ".fontcheck.tmp.woff2")
    with open(tmp, "wb") as handle:
        handle.write(raw)
    try:
        font = TTFont(tmp, lazy=True)
        cmap = font.getBestCmap()
        family = font["name"].getDebugName(1)
        num_glyphs = font["maxp"].numGlyphs
        font.close()
    finally:
        os.unlink(tmp)
    chk("A3 fontTools 可打开子集", True, f"family={family!r} glyphs={num_glyphs} cmap={len(cmap)}")
    chk("A4 子集族名已改名（OFL 保留名条款）",
        family == FAMILY and "Source" not in family,
        f"name ID 1 = {family!r}")

    urange = URANGE_RE.search(css)
    spans = parse_unicode_range(urange.group(1)) if urange else []
    chk("A5 unicode-range 已声明", bool(spans), f"{len(spans)} 段: {urange.group(1).strip() if urange else '无'}")

    # ---- B 覆盖 ----
    sources = list(HTML_FILES) + sorted(
        os.path.relpath(p, base) for p in glob.glob(os.path.join(base, "visual/assets/*.js"))
    )
    chars: dict[str, list[str]] = {}
    for rel in sources:
        path = os.path.join(base, rel)
        if not os.path.isfile(path):
            continue
        for char in set(open(path, encoding="utf-8").read()):
            if ord(char) > 0x7F:
                chars.setdefault(char, []).append(rel)
    missing = sorted(c for c in chars if ord(c) not in cmap)
    chk("B1 全部非 ASCII 字符在子集 cmap 内",
        not missing,
        f"检查 {len(sources)} 个来源 / {len(chars)} 个唯一字符, 缺字 {len(missing)} 个"
        + (" -> " + "".join(missing) if missing else ""))

    html_only = set()
    for rel in HTML_FILES:
        path = os.path.join(base, rel)
        if os.path.isfile(path):
            html_only |= {c for c in open(path, encoding="utf-8").read() if ord(c) > 0x7F}
    miss_html = sorted(c for c in html_only if ord(c) not in cmap)
    chk("B2 四份 HTML 逐字符零缺字", not miss_html,
        f"HTML 唯一非 ASCII {len(html_only)} 个, 缺字 {len(miss_html)} 个")

    # ---- C 字体栈首位 ----
    for rel in HTML_FILES + EXTRA_CSS_FILES:
        path = os.path.join(base, rel)
        if not os.path.isfile(path):
            continue
        text = open(path, encoding="utf-8").read()
        stacks = [m.group(1).strip() for m in FONT_FAMILY_RE.finditer(text)]
        stacks = [s for s in stacks if s and s != "inherit"]
        bad = [s for s in stacks if not s.lstrip().startswith(f'"{FAMILY}"')]
        chk(f"C {rel} font-family 首位", not bad,
            f"{len(stacks)} 条声明, 不合格 {len(bad)} 条"
            + (" -> " + " | ".join(sorted(set(bad))[:3]) if bad else ""))

    # ---- D 引用可解析 ----
    for rel in HTML_FILES:
        path = os.path.join(base, rel)
        if not os.path.isfile(path):
            continue
        text = open(path, encoding="utf-8").read()
        hrefs = [h for h in LINK_RE.findall(text) if h.endswith("cjk-webfont.css")]
        resolved = [
            h for h in hrefs
            if os.path.isfile(os.path.normpath(os.path.join(os.path.dirname(path), h)))
        ]
        chk(f"D {rel} 引用字体 CSS 且相对路径可解析",
            len(hrefs) == 1 and len(resolved) == 1,
            f"命中 {len(hrefs)} 条, 可解析 {len(resolved)} 条 -> {hrefs}")

    # ---- E' UA 样式表等宽族修正 ----
    # 浏览器 UA 样式表给 code/pre/kbd/samp 指定 monospace，该声明绕过页面自身的字体栈。
    # v9.8 的浏览器实测扫查证实：不加这条修正，报告页 <code> 里的 300 余个汉字仍退回
    # 系统字体。此处断言该修正在位且子集排在等宽族链首位。
    mono = re.search(r"code\s*,\s*pre\s*,\s*kbd\s*,\s*samp\s*\{[^}]*font-family\s*:\s*([^;}]+)", css)
    chk("E1 UA 等宽族已被子集接管",
        bool(mono) and mono.group(1).lstrip().startswith(f'"{FAMILY}"') and "monospace" in mono.group(1),
        (mono.group(1).strip()[:96] if mono else "未找到 code,pre,kbd,samp 规则"))

    # ---- E unicode-range 例外 ----
    outside = sorted(c for c in html_only if not in_spans(ord(c), spans))
    unexpected = [c for c in outside if ord(c) not in PUNCT_EXEMPT]
    chk("E unicode-range 之外的字符全部属于登记白名单",
        not unexpected,
        f"range 外 {len(outside)} 个 [{''.join(outside)}], 白名单外 {len(unexpected)} 个"
        + (" -> " + "".join(unexpected) if unexpected else ""))

    print()
    print(f"合计 失败 {len(failures)} 项")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
