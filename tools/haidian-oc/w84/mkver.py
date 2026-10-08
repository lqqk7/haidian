# -*- coding: utf-8 -*-
"""交付 ①：核验图组进 A3 双语册，新增第 12—15 页。

做法沿用 w83fix/edit_src.py 的「改 out/ 页源」模式：wp4b/build 的生成器缺
tokens.js 无法 require，因此新页不从生成器出，而是以 out/a3/{lang}-11.html
为壳克隆（该页自带完整 CSS 与三个 SHS 字体子集），只替换页眉三处印字与
<body> 内容，再由 w82/fixfont.py 按 suppfont 机制补齐壳内子集没有的码位。

版面（A3 420×297 mm，版心 left/right 16 mm、top 24 mm、bottom 20 mm，
即 388 × 253 mm）：
  第 12 页  核验图 00 单张，图框宽 236 mm，图高 = 宽 × 1875/3000 = 147.5 mm
  第 13—15 页  每页两张，两栏各 170 mm，居中（总宽 346 mm < 388 mm）

单图页的图框宽不是构图偏好，是版心防线反解出来的：该页除图框外还要放导语、
图注、核验声明、署名与页尾标识条，而英文导语比中文多两行，英文侧因此是约束方。
w84/widthscan.js 在 1588×1123 视口上逐档实测（en-12）：276 mm 溢出 67 px、尾行
倒压页脚 40.2 px。可行区间不连续——图注 .src 行在 246 mm 以上排一行、245 mm
以下排两行（高度 146.3 → 164.4 px），于是 246 mm 与 ≤240 mm 各是一段可行区，
242—244 mm 反而重新溢出。取 236 mm：落在下段可行区内且离上边界 4 mm，不吃
246 mm 那一档紧贴换行悬崖的风险。溢出归零后净空稳定在 26.5 px（与第 13—15 页
同值，由 .vnote 的 margin-top:auto 决定）。中文侧宽松得多，被英文侧覆盖。

图版派生件为语言中立单套：zh 册与 en 册引用同一批 JPEG，配方写在文件名里
（与 wp77fix/mkjpg.py、w83fix/mkjpg_site.py 登记的口径一致）。
"""
from __future__ import annotations
from pathlib import Path as _HaidianPath

import os
import re
import subprocess
import sys

T = str(_HaidianPath(__file__).resolve().parents[1])
PKG = str(_HaidianPath(__file__).resolve().parents[3] / 'submissions/lqqk7/every-sense-jingzhang')
FIG = os.path.join(PKG, "assets/figures")
OUT = os.path.join(T, "wp4b/out/a3")
JPG = os.path.join(T, "wp4b/jpg")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(T, "w82"))
import verdata as V          # noqa: E402
import fixfont               # noqa: E402

# ---------------------------------------------------------------- 版面常数
SINGLE_MM = 236.0                 # 第 12 页图框宽
PAIR_MM = 170.0                   # 第 13—15 页每栏图框宽
ASPECT = 1875.0 / 3000.0

# 派生件配方：目标印刷分辨率（dpi）与 JPEG 质量，由包体预算反解，见 README 报告
DPI = int(os.environ.get("W84_DPI", "77"))
Q = int(os.environ.get("W84_Q", "60"))

CSS = """
/* ---------- WP-84: pages 12-15, geometry verification group ---------- */
/* 语言中立单套图版：两册引用同一批 JPEG。图内自带的双语图注、ODbL 署名与
   「非设计图」标识在缩印到 515 / 716 px 后已不可读，因此不能靠它们承担任何
   判断语；页面文本层重新给出图题、要素/顶点计数、核验声明与署名，使全部判断
   语落在 >= 9 pt 的文本层上（与本册 R1-03 的阅读纪律一致）。 */
.ver{position:absolute;left:16mm;right:16mm;top:24mm;bottom:20mm;display:flex;flex-direction:column;padding-top:5mm}
.ver .lead{font-size:3.5mm;color:#68787b;line-height:1.55}
.vgrid{display:grid;gap:6mm;margin-top:4.4mm;justify-content:center}
.vfig{margin:0;background:#fff;border:.25mm solid #e2ddd0;border-radius:1.4mm;overflow:hidden}
.vfig img{display:block;width:100%;height:auto}
.vcap{padding:3mm 4.4mm 3.6mm}
.vcap .n{font-size:3.2mm;letter-spacing:.12em;color:#177c78;font-weight:700;font-family:SHS}
.vcap h3{font-size:4.2mm;margin:1.8mm 0 0;font-weight:700;line-height:1.28;color:#10383d}
.vcap .alt{font-size:3.4mm;color:#68787b;margin-top:1.4mm;line-height:1.35}
.vcap .cnt{font-size:3.6mm;color:#10383d;font-weight:700;margin-top:2.6mm;font-family:SHS;font-variant-numeric:tabular-nums}
.vcap .src{font-size:3.3mm;color:#68787b;margin-top:1.8mm;line-height:1.45}
.vnote{margin-top:auto;background:#fdf1ee;border-left:1.4mm solid #d76450;color:#d76450;font-size:3.35mm;font-weight:700;line-height:1.45;padding:3mm 4mm}
.vattr{margin-top:3.2mm;font-size:3.2mm;color:#68787b;line-height:1.42}
"""


def jpgname(key):
    return "a3-verify-%s-w%d-q%d.jpg" % (key, px_for(key), Q)


def px_for(key):
    mm = SINGLE_MM if key == "00-all" else PAIR_MM
    return int(round(mm / 25.4 * DPI))


def build_jpgs():
    os.makedirs(JPG, exist_ok=True)
    tot = 0
    for key, *_ in V.SHEETS:
        src = os.path.join(FIG, "verification-overlay-%s.png" % key)
        out = os.path.join(JPG, jpgname(key))
        subprocess.run(["magick", src, "-resize", "%dx" % px_for(key),
                        "-quality", str(Q), "-sampling-factor", "4:2:0", "-strip",
                        "-colorspace", "sRGB", out], check=True)
        n = os.path.getsize(out)
        tot += n
        print("   %-40s %7d B" % (os.path.basename(out), n))
    print("   派生件合计 %d B（单册嵌入量）" % tot)
    return tot


def figblock(key, zh_t, en_t, nf, nv, lang, width_mm):
    n = key.split("-")[0]
    src = "file://" + os.path.join(JPG, jpgname(key))
    if lang == "zh":
        title, alt = zh_t, en_t
        cnt = "要素 %d 个 / 顶点 %d 个 · features %d / vertices %d" % (nf, nv, nf, nv)
        srcline = "图版 assets/figures/verification-overlay-%s.png · %s" % (key, V.SUB_ZH)
    else:
        title, alt = en_t, zh_t
        cnt = "features %d / vertices %d · 要素 %d 个 / 顶点 %d 个" % (nf, nv, nf, nv)
        srcline = "Plate assets/figures/verification-overlay-%s.png · %s" % (key, V.SUB_EN)
    return ('<figure class="vfig" style="width:%.1fmm">'
            '<img src="%s">'
            '<figcaption class="vcap"><div class="n">V%s / VERIFICATION</div>'
            '<h3>%s</h3><div class="alt">%s</div>'
            '<div class="cnt">%s</div><div class="src">%s</div>'
            '</figcaption></figure>' % (width_mm, src, n, title, alt, cnt, srcline))


def body(page, lang):
    spec = V.PAGES[page]
    keys = spec["keys"]
    sheets = {k: s for s in V.SHEETS for k in [s[0]]}
    single = len(keys) == 1
    w = SINGLE_MM if single else PAIR_MM
    cols = "%.1fmm" % SINGLE_MM if single else "%.1fmm %.1fmm" % (PAIR_MM, PAIR_MM)
    figs = "".join(figblock(k, *sheets[k][1:], lang, w) for k in keys)
    note = V.NOTE_ZH if lang == "zh" else V.NOTE_EN
    attr = ((V.ATTR_ZH + "<br>" + V.CRS_ZH) if lang == "zh"
            else (V.ATTR_EN + "<br>" + V.CRS_EN))
    if lang == "zh":
        disc = "概念建议 / 非法定规划 / 非工程线位"
        pills = ('<span style="background:#7c8b8c">公开背景 · PUBLIC</span>'
                 '<span style="background:#d76450">临时约束 · PROVISIONAL</span>'
                 '<span style="background:#177c78">概念建议 · CONCEPT</span>')
    else:
        disc = "CONCEPT PROPOSAL / NOT A STATUTORY PLAN / NOT AN ENGINEERING ALIGNMENT"
        pills = ('<span style="background:#7c8b8c">PUBLIC BACKGROUND</span>'
                 '<span style="background:#d76450">PROVISIONAL</span>'
                 '<span style="background:#177c78">CONCEPT PROPOSAL</span>')
    return ('\n<div class="ver">\n  <div class="lead">%s</div>\n'
            '  <div class="vgrid" style="grid-template-columns:%s">%s</div>\n'
            '  <div class="vnote">%s</div>\n'
            '  <div class="vattr">%s</div>\n'
            '  <div class="tailrow"><div class="disc">%s</div>'
            '<div class="pills">%s</div></div>\n</div>'
            % (V.LEAD[lang][page], cols, figs, note, attr, disc, pills))


H2 = re.compile(r"<h2>.*?</h2>", re.S)
PNUM = re.compile(r'<div class="p">\d\d / \d\d</div>')
SIDX = re.compile(r'<div class="s">.*?</div>')
PGFOOT = re.compile(r">\d\d / \d\d<")


def run(lang):
    shell = open(os.path.join(OUT, "%s-11.html" % lang), encoding="utf-8").read()
    i0 = shell.index("<body>") + len("<body>")
    i1 = shell.index('\n<div class="aud')
    i2 = shell.index('<div class="foot">')
    head, hdr, foot = shell[:i0], shell[i0:i1], shell[i2:]
    assert "</style>" in head
    head = head.replace("</style>", CSS + "</style>", 1)

    for page, spec in sorted(V.PAGES.items()):
        h = hdr
        assert len(H2.findall(h)) == 1 and len(PNUM.findall(h)) == 1
        assert len(SIDX.findall(h)) == 1
        h = H2.sub("<h2>%s</h2>" % spec["%s_h2" % lang], h, count=1)
        h = PNUM.sub('<div class="p">%02d / 16</div>' % page, h, count=1)
        h = SIDX.sub('<div class="s">%s</div>' % spec["%s_s" % lang], h, count=1)
        f, k = PGFOOT.subn('>%02d / 16<' % page, foot)
        assert k == 1, "页脚页码命中 %d 处" % k
        html = head + h + body(page, lang) + f
        p = os.path.join(OUT, "%s-%02d.html" % (lang, page))
        open(p, "w", encoding="utf-8").write(html)
        print("%s-%02d.html  %d B  补字 %s"
              % (lang, page, len(html), "".join(fixfont.patch(p)) or "无"))


if __name__ == "__main__":
    print("== 派生件（dpi=%d q=%d）==" % (DPI, Q))
    build_jpgs()
    print("== 页源 ==")
    for l in ("zh", "en"):
        run(l)
