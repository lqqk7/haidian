#!/usr/bin/env python3
"""WP-E3 交付物：report/*.html 的后渲染补丁。

`scripts/render_proposal_html.py` 生成的报告页存在三处表达卫生问题，这三处都出现在
渲染层而不是 `proposal.md` 正文里，因此在正文定稿、报告重渲染之后统一由本脚本修补：

1. **H1 去重。** 渲染器先输出 `<section class="hero">` 里的标题，随后又输出
   `proposal.md` 自带的正文 H1，同一句话连续出现两次。本脚本保留正文 H1（即
   markdown 的 `# ` 标题节点），删除 hero 内重复的那一个，并把保留下来的正文 H1
   提到 hero 首位，使「标题 → 摘要 → 语言切换」的顺序保持正常。
   两个 H1 文本不一致时不做任何改动，只报告。

2. **表格 CSS。** 多列中文表格在自动布局下会把某一列压到近乎零宽，导致中文逐字
   竖排。注入 `table-layout: fixed` + 首列宽度约束 + 断词规则修正。

3. **范围警示行前置。** 「概念建议 · 临时几何」这一类范围限定语句目前埋在正文
   段落中段。本脚本从文档自身抽取该限定句（不新增任何主张），在首屏标题正下方
   插入一条警示行；抽不到时退回本包通用的短标签。

4. **中文离线字面注入。** 渲染器输出的 font-family 栈只列系统字体名
   （`-apple-system`、`PingFang SC`、`Noto Sans CJK SC` 等），在没有安装任何 CJK
   字体的干净浏览器里中文全部退化为方框。本脚本引入包内自足的字体子集
   `visual/assets/cjk-webfont.css`（Source Han Sans SC 子集，woff2 以 data URI
   内嵌），把它接进 `<head>`，并把子集族名前置到每一条 font-family 栈的首位，
   原有系统字体栈整条保留作后备。族名与覆盖由 `wpe3/font_coverage_check.py` 断言。

用法：
    post_render_report.py <report.html> [<report2.html> ...]   # 就地修补
    post_render_report.py --dry-run <report.html>              # 只报告不写入
    post_render_report.py --out DIR <report.html>              # 输出到别处

脚本可重复执行：已修补的文件带 `<!-- post_render_report:v1 -->` 标记，再次运行
时跳过已完成的步骤。
"""

from __future__ import annotations

import argparse
import html as htmllib
import re
import sys
from pathlib import Path

MARKER = "<!-- post_render_report:v1 -->"

HERO_RE = re.compile(r'<section class="hero">(.*?)</section>', re.S)
H1_RE = re.compile(r"<h1\b[^>]*>.*?</h1>", re.S)

CSS_BLOCK = """
/* post_render_report: 多列中文表格的列宽与断词修正 */
.proposal-table table { table-layout: fixed; min-width: 680px; }
.proposal-table th, .proposal-table td { overflow-wrap: anywhere; word-break: normal; hyphens: none; }
.proposal-table th:first-child, .proposal-table td:first-child { width: 16%; }
/* post_render_report: 预格式化块横向溢出 —— 证据标记与数据引用写在 pre/code 里，
   长行会把整页撑出横向滚动条；改为在块内自滚，页面正文不再横向溢出。 */
pre { overflow-x: auto; max-width: 100%; }
pre code { white-space: pre; }
/* post_render_report: 首屏范围警示行 */
.postrender-scope {
  margin: 14px 0 0;
  padding: 10px 14px;
  border-left: 4px solid #b4442f;
  background: #fdf1ee;
  color: #8f3320;
  font-size: 15px;
  line-height: 1.6;
}
.postrender-scope strong { letter-spacing: .04em; }
"""

# 从文档自身抽取范围限定句；抽不到时退回本包既有的通用短标签。
SCOPE_SENTENCE_RE = {
    "zh": re.compile(r"图中边界不是官方红线[^。]*。"),
    "en": re.compile(r"Boundaries in the figures are therefore not official redlines[^.]*\."),
}
SCOPE_TAG = {
    "zh": "概念建议 · 临时几何 · 非法定规划 · 非工程线位",
    "en": "CONCEPT PROPOSAL · PROVISIONAL GEOMETRY · NOT A STATUTORY PLAN · NOT AN ENGINEERING ALIGNMENT",
}
SCOPE_FALLBACK = {
    "zh": "图中边界不是官方红线，面积不是法定或精确面积。",
    "en": "Boundaries in the figures are not official redlines and areas are not statutory or precise figures.",
}


# 中文离线字面：包内自足的 Source Han Sans SC 子集，woff2 以 data URI 内嵌于 CSS。
# report/*.html 位于 report/ 下，因此以相对路径跨目录引用 visual/assets/。
CJK_FONT_FAMILY = "ESJZ Sans Subset"
CJK_FONT_HREF = "../visual/assets/cjk-webfont.css"
CJK_FONT_LINK = f'<link rel="stylesheet" href="{CJK_FONT_HREF}">'
FONT_FAMILY_DECL_RE = re.compile(r"font-family\s*:\s*(?!\s*inherit\b)([^;{}]+)")


def inject_cjk_font(text: str, log: list[str]) -> str:
    """接入包内字体子集，并把子集族名前置到每一条 font-family 栈首位。"""
    quoted = f'"{CJK_FONT_FAMILY}"'
    if CJK_FONT_LINK not in text:
        index = text.find("<style>")
        if index < 0:
            log.append("字体: 未找到 <style>，跳过 link 注入")
        else:
            text = text[:index] + CJK_FONT_LINK + "\n" + text[index:]
            log.append(f"字体: 已接入 {CJK_FONT_HREF}")
    else:
        log.append("字体: link 已存在，跳过")

    count = 0

    def prepend(match: re.Match) -> str:
        nonlocal count
        stack = match.group(1)
        if stack.lstrip().startswith(quoted):
            return match.group(0)
        count += 1
        return f"font-family: {quoted}, {stack.lstrip()}"

    text = FONT_FAMILY_DECL_RE.sub(prepend, text)
    log.append(f"字体: font-family 栈前置 {count} 处（原栈整条保留作后备）")
    return text


def detect_language(text: str) -> str:
    match = re.search(r'<html[^>]*\blang="([^"]+)"', text)
    return "en" if match and match.group(1).lower().startswith("en") else "zh"


def plain_text(fragment: str) -> str:
    return re.sub(r"\s+", " ", htmllib.unescape(re.sub(r"<[^>]+>", " ", fragment))).strip()


def dedupe_h1(text: str, log: list[str]) -> str:
    hero = HERO_RE.search(text)
    if not hero:
        log.append("H1: 未找到 hero 区块，跳过")
        return text
    hero_h1 = H1_RE.search(hero.group(1))
    if not hero_h1:
        log.append("H1: hero 内无 H1，跳过（可能已修补）")
        return text
    tail_start = hero.end()
    body_h1 = H1_RE.search(text, tail_start)
    if not body_h1:
        log.append("H1: 正文无第二个 H1，无需去重")
        return text
    if plain_text(hero_h1.group(0)) != plain_text(body_h1.group(0)):
        log.append("H1: 两个 H1 文本不一致，未改动（请人工确认）")
        return text

    body_markup = body_h1.group(0)
    # 先删正文 H1（连同其后紧跟的一个换行），再用它替换 hero 内的重复 H1。
    after = text[body_h1.end():]
    if after.startswith("\n"):
        after = after[1:]
    text = text[: body_h1.start()] + after
    hero = HERO_RE.search(text)
    hero_h1 = H1_RE.search(hero.group(1))
    absolute = hero.start(1) + hero_h1.start()
    text = text[:absolute] + body_markup + text[absolute + len(hero_h1.group(0)):]
    log.append("H1: 已去重，保留正文 H1 并置于 hero 首位")
    return text


def inject_css(text: str, log: list[str]) -> str:
    if "post_render_report: 多列中文表格" in text:
        log.append("CSS: 已存在，跳过")
        return text
    index = text.find("</style>")
    if index < 0:
        log.append("CSS: 未找到 </style>，跳过")
        return text
    log.append("CSS: 已注入表格与警示行样式")
    return text[:index] + CSS_BLOCK + text[index:]


def insert_scope_warning(text: str, lang: str, log: list[str]) -> str:
    if 'data-postrender="scope-warning"' in text:
        log.append("警示行: 已存在，跳过")
        return text
    body = plain_text(text)
    match = SCOPE_SENTENCE_RE[lang].search(body)
    if match:
        sentence = match.group(0)
        source = "抽取自正文"
    else:
        sentence = SCOPE_FALLBACK[lang]
        source = "正文未匹配，使用本包通用短句"
    banner = (
        f'\n<p class="postrender-scope" data-postrender="scope-warning">'
        f"<strong>{htmllib.escape(SCOPE_TAG[lang])}</strong> — {htmllib.escape(sentence)}</p>"
    )
    hero = HERO_RE.search(text)
    if not hero:
        log.append("警示行: 未找到 hero 区块，跳过")
        return text
    hero_h1 = H1_RE.search(hero.group(1))
    if not hero_h1:
        log.append("警示行: hero 内无 H1，跳过")
        return text
    position = hero.start(1) + hero_h1.end()
    log.append(f"警示行: 已插入标题正下方（{source}）")
    return text[:position] + banner + text[position:]


def patch(path: Path, out_path: Path, dry_run: bool) -> int:
    text = path.read_text(encoding="utf-8")
    lang = detect_language(text)
    log: list[str] = []
    patched = dedupe_h1(text, log)
    patched = insert_scope_warning(patched, lang, log)
    patched = inject_css(patched, log)
    patched = inject_cjk_font(patched, log)
    patched = render_extra_refs(patched, lang, log)
    if MARKER not in patched:
        patched = patched.replace("</body>", f"{MARKER}\n</body>", 1)
    changed = patched != text
    print(f"== {path}  (lang={lang}, changed={changed})")
    for line in log:
        print(f"   - {line}")
    if changed and not dry_run:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(patched, encoding="utf-8")
        print(f"   -> 已写入 {out_path}")
    return 0 if changed or dry_run else 1



EXTRA_REF_RE = __import__('re').compile(r"\[(assumption|self_check):([^\]\s]+)\]")
EXTRA_LABELS = {
    "zh": {"assumption": "前提与边界", "self_check": "方案自检"},
    "en": {"assumption": "Assumption", "self_check": "Self check"},
}

def render_extra_refs(text: str, lang: str, log: list) -> str:
    """官方 render_proposal_html 只认五类证据标记；站端 proposal-view 认七类。
    这里把 assumption / self_check 两类补渲染成与官方完全同款的 <sup> 标签，
    使报告页与站端主视图对这两类证据呈现一致。"""
    import html as _h
    n = 0
    def rep(m):
        nonlocal n
        kind, value = m.group(1), m.group(2)
        label = EXTRA_LABELS["en" if lang == "en" else "zh"][kind]
        sep = ": " if lang == "en" else "："
        ev = _h.escape(value)
        n += 1
        return (f'<sup class="evidence evidence-{kind}" data-evidence-kind="{kind}" '
                f'data-evidence-value="{ev}" title="{label}{sep}{ev}">{label}</sup>')
    out = EXTRA_REF_RE.sub(rep, text)
    if n:
        log.append(f"   - 证据标记: 补渲染 assumption/self_check 共 {n} 处")
    return out

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("files", nargs="+")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--out", default=None, help="输出目录；缺省为就地修补")
    args = parser.parse_args()
    status = 0
    for name in args.files:
        path = Path(name)
        out_path = Path(args.out) / path.name if args.out else path
        status |= patch(path, out_path, args.dry_run)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
