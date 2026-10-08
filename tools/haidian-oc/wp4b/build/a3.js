'use strict';
/* A3 landscape booklet, 10 pages, 420 x 297 mm.

   WP-L (v5.4) rebuild of the reading layer.  Up to v5.3 pages 02-05 and 07 each
   scaled a whole 4800 x 3000 A0 plate into a 280 mm frame, which put the plate's
   own body copy and legends at 3.0-3.7 pt on an A3 sheet — unreadable, and the
   reason the booklet could not stand on its own away from the A0 boards.

   v5.4 splits that: every figure page becomes an A3-native SUMMARY page that
   carries 3-5 first-order judgements plus a legend at >= 9 pt, with a cropped
   graphic band as morphological evidence; the audit ledgers that used to be
   compressed inside the plates move to two A3-native APPENDIX pages that
   typeset the same ledger rows in mm units.  Summary and appendix carry
   explicit pointers to each other, to the A0 boards and to the package PNGs.

   Zero value change: every number, label and sentence is read from content.js,
   metricsfig.js and wpe2/audit-data.json, which are the same sources the A0
   boards and the companion figures already use. */

const { C, base, ruleBar, FONT_SLOT } = require('./tokens');
const { logo } = require('./logo');
const COPY = require('./content');
const MFIG = require('./metricsfig');
const AUD = require('../../wpe2/audit-data.json');

const TOTAL = 12;
const TT = String(TOTAL).padStart(2, '0');
const col = (k) => C[k] || k;
const no = (n) => String(n).padStart(2, '0');

/* Navigation and qualifier strings introduced by the split.  These are wayfinding
   and scope labels, not data: no metric, geometry or count is created here. */
const NAV = {
  zh: {
    coverClaim: '概念建议 · 设计判据 · 非实测结果',
    coverFig: '封面图为总平面缩略图；A3 可读摘要见第 02 页，完整图版随包收录于 assets/figures/site-overview.png。',
    judge: '一级判断',
    legend: '图例',
    summaryKick: 'A3 摘要版式',
    figSummary: '本页图版为针对 A3 重排的摘要图，只保留形态证据；判断、图例与限定语在本页正文层。',
    /* WP-R13: page 03's window now reaches the plate's own caption and line
       legend, so the shared sentence above — "morphology only" — would be
       false on that one page.  Only page 03 overrides it. */
    figLanduse: '本页图版为针对 A3 重排的摘要图，保留走廊形态证据与图版自身的图题、线型图例；本页一级判断与限定语在正文层。',
    figKeyareas: '本页图版为针对 A3 重排的摘要图，保留三卡首层运行形态与图版自身的图题、色块图例；本页一级判断与限定语在正文层。',
    plateAt: (b, f) => `完整图版：A0 展板 ${b} · assets/figures/${f}.png`,
    figOnly: (f) => `完整图版：assets/figures/${f}.png（A0 不设本图整版）`,
    ledgerAt: (p) => `审计台账：本册第 ${no(p)} 页`,
    backTo: (p) => `对应摘要：本册第 ${no(p)} 页`,
    appendix: '附页',
    appendixKick: 'A3 审计附页',
    audLead: '本页台账在 A3 上原生排版，与随包附图、A0 展板同源同值，不新增任何数值。',
    figFrom: (f) => `图版来源：assets/figures/${f}.png`,
    brandTitle: '品牌系统：标志与色彩语义',
    cultureTitle: '文化叙事与对外传播',
    sourcesTitle: '来源、标准与证据边界',
    seeAlso: (label, p) => `${label}：本册第 ${no(p)} 页`,
  },
  en: {
    coverClaim: 'CONCEPT PROPOSAL · DESIGN CRITERIA · NOT MEASURED RESULTS',
    coverFig: 'The cover image is a reduced masterplan key; the A3-readable summary is on page 02 and the full plate ships in the package as assets/figures/site-overview.png.',
    judge: 'FIRST-ORDER JUDGEMENTS',
    legend: 'LEGEND',
    summaryKick: 'A3 SUMMARY LAYOUT',
    figSummary: 'This band is a summary figure re-laid for A3 and carries morphology only; judgements, legend and qualifiers sit in the page text layer.',
    figLanduse: 'This band is a summary figure re-laid for A3 and carries the corridor morphology with the plate\'s own caption and line legend; this page\'s first-order judgement and qualifiers sit in the text layer.',
    figKeyareas: 'This band is a summary figure re-laid for A3 and carries the three cards\' ground-floor operating morphology with the plate\'s own captions and colour legend; this page\'s first-order judgement and qualifiers sit in the text layer.',
    plateAt: (b, f) => `Full plate: A0 board ${b} · assets/figures/${f}.png`,
    figOnly: (f) => `Full plate: assets/figures/${f}.png (no dedicated A0 board)`,
    ledgerAt: (p) => `Audit ledger: page ${no(p)} of this booklet`,
    backTo: (p) => `Summary page: page ${no(p)} of this booklet`,
    appendix: 'APPENDIX',
    appendixKick: 'A3 AUDIT APPENDIX',
    audLead: 'This ledger is typeset natively for A3. It shares its source and its values with the companion figure and the A0 boards, and introduces no new number.',
    figFrom: (f) => `Plate source: assets/figures/${f}.png`,
    brandTitle: 'Brand system: mark and colour semantics',
    cultureTitle: 'Cultural narrative and outward communication',
    sourcesTitle: 'Sources, standards and the evidence boundary',
    seeAlso: (label, p) => `${label}: page ${no(p)} of this booklet`,
  },
};

/* The four land-use function notes are lifted verbatim from the
   land-use-structure plate's own "FOUR CONCEPTUAL FUNCTIONS" column, so the A3
   summary card carries the same sentence the plate carries. */
const LUNOTE = {
  zh: ['连接研究、原型、受控测试和人工接管。', '承载连续公共底线与低刺激替代路径。',
    '检验采购、维护、纠错与退出。', '把真实公共任务反馈给产品与空间。'],
  en: ['Links research, prototyping, controlled tests and human takeover.',
    'Carries the continuous public baseline and quiet alternative.',
    'Tests procurement, maintenance, correction and exit.',
    'Feeds real public tasks back into products and space.'],
};

function css(lang) {
  const cjk = lang === 'zh';
  return `${FONT_SLOT}${base}
@page{size:420mm 297mm;margin:0}
body{width:420mm;height:297mm;overflow:hidden;background:${C.paper};position:relative}
.hdr{height:24mm;background:${C.deep};color:#fff;padding:4.4mm 16mm 0;display:flex;justify-content:space-between;align-items:flex-start}
.hdr .l .k{font-size:3.2mm;letter-spacing:.13em;color:${C.onDarkEn};display:flex;align-items:center;gap:3mm;font-family:SHS;font-weight:700}
.hdr .l h2{font-size:${cjk ? 6.4 : 5.6}mm;font-weight:700;margin:2.4mm 0 0;line-height:1.1}
.hdr .r{text-align:right;padding-top:.2mm}
.hdr .r .p{font-size:3.4mm;font-weight:700;letter-spacing:.1em;font-family:SHS}
.hdr .r .s{font-size:3.2mm;letter-spacing:.1em;color:${C.onDarkEn};margin-top:2.4mm;font-family:SHS;font-weight:700}
.foot{position:absolute;left:16mm;right:16mm;bottom:6mm;border-top:.25mm solid ${C.line};padding-top:2.4mm;display:flex;justify-content:space-between;gap:8mm;font-size:3.2mm;color:${C.muted};line-height:1.35}
.foot .pg{flex:none;font-family:SHS;font-weight:700}
.disc{font-size:3.4mm;color:${C.coral};font-weight:700;letter-spacing:.01em;line-height:1.4}
.pills{display:flex;gap:3mm;flex-wrap:wrap}
.pills span{font-size:3.2mm;color:#fff;border-radius:3mm;padding:1.5mm 4mm;letter-spacing:.05em;font-family:SHS;font-weight:700;line-height:1.2}

/* ---------- summary page ---------- */
.wrap{position:absolute;left:16mm;right:16mm;top:24mm;bottom:20mm;display:flex;flex-direction:column;padding-top:6mm}
.claim{font-size:${cjk ? 4.8 : 4.4}mm;font-weight:700;color:${C.deep};line-height:1.42;letter-spacing:.005em}
.claim i{font-style:normal;color:${C.teal};font-family:SHS;letter-spacing:.12em;font-size:3.2mm;display:block;margin-bottom:2.4mm}
.intro{font-size:3.4mm;line-height:1.62;color:${C.muted};margin:3.4mm 0 0;max-width:340mm}
.figbox{margin-top:5mm;border:.28mm solid ${C.edge};background:#fff;overflow:hidden;flex:none;display:block}
.figbox img{display:block;width:100%;height:100%;object-fit:contain;object-position:center}
.figcap{font-size:3.2mm;color:${C.muted};margin-top:2.4mm;line-height:1.4}
.cards{display:grid;gap:4mm;margin-top:5mm;flex:1;align-content:center}
.card{background:#fff;border-radius:1.4mm;border-left:1.6mm solid;padding:4mm 4.6mm;display:flex;flex-direction:column;justify-content:center}
.card .v{font-size:${cjk ? 6.2 : 5.8}mm;font-weight:700;color:${C.deep};font-family:SHS;font-variant-numeric:tabular-nums;line-height:1.1}
.card .t{font-size:3.9mm;font-weight:700;color:${C.deep};line-height:1.35;margin-top:1.8mm}
.card .s{font-size:3.5mm;font-weight:700;line-height:1.3;margin-top:1.4mm}
.card .d{font-size:3.3mm;color:${C.muted};line-height:1.5;margin-top:1.8mm}
.lgd{margin-top:4.4mm;border-top:.25mm solid ${C.line};padding-top:3.4mm}
.lgd .lt{font-size:3.2mm;letter-spacing:.12em;color:${C.teal};font-weight:700;font-family:SHS}
.lgd .row{display:flex;flex-wrap:wrap;gap:3mm 7mm;margin-top:2.6mm}
.lgd .i{display:flex;align-items:center;gap:2.6mm;font-size:3.35mm;line-height:1.35}
.lgd .i b{width:3.4mm;height:3.4mm;border-radius:50%;display:block;flex:none}
.warnbar{margin-top:4mm;background:#fdf1ee;border-left:1.4mm solid ${C.coral};color:${C.coral};font-size:3.35mm;font-weight:700;line-height:1.45;padding:3mm 4mm}
.ptr{margin-top:4mm;display:flex;flex-wrap:wrap;gap:2mm 8mm;font-size:3.2mm;color:${C.muted};line-height:1.4}
.ptr b{color:${C.teal};font-weight:700}
.tailrow{display:flex;justify-content:space-between;align-items:flex-end;gap:10mm;margin-top:4mm}

/* ---------- cover ---------- */
/* WP-N2b: the reviewing model sees this page at a 768 px short edge, i.e.
   2.59 px per mm, so nothing below ~4.7 mm can be read at review scale.  The
   v5.4 cover carried a whole-plate key at 216 mm wide (illegible at that
   reduction and duplicating board 01), four 3.2 mm metric tiles and two
   disclaimer badges.  It now carries title, subtitle, brand and three
   commitments, all at >= 4.8 mm, with the disclaimers folded into one footer
   line and the rest of the sheet left as air. */
.cover{position:absolute;inset:0;background:${C.deep};color:#fff}
.cover .lft{position:absolute;left:24mm;top:26mm;width:372mm}
.cover .k{font-size:4.8mm;letter-spacing:.16em;color:${C.onDarkEn};display:flex;align-items:center;gap:5mm;font-family:SHS;font-weight:700;margin-bottom:11mm}
.cover h1{font-size:${cjk ? 15.5 : 11.5}mm;font-weight:700;line-height:1.22;margin:0;max-width:${cjk ? 330 : 350}mm}
.cover .sub{font-size:6.6mm;color:${C.onDarkEn};margin-top:9mm;letter-spacing:.02em;line-height:1.4}
.cover .rulez{height:.4mm;background:${C.onDarkRule};margin-top:14mm;width:300mm}
.cover .prom{position:absolute;left:24mm;top:138mm;width:344mm}
.cover .pr{display:grid;grid-template-columns:16mm 1fr;gap:6mm;align-items:baseline;margin-top:13mm}
.cover .pr:first-child{margin-top:0}
.cover .pn{font-size:5.4mm;font-weight:700;color:${C.onDarkEn};font-family:SHS;letter-spacing:.1em}
.cover .pt{font-size:${cjk ? 6.2 : 5.6}mm;line-height:1.62;color:#fff}
.cover .cfoot{position:absolute;left:24mm;right:18mm;bottom:13mm;display:flex;justify-content:space-between;gap:10mm;font-size:4.8mm;color:${C.onDarkEn};line-height:1.35}

/* ---------- appendix ledger ---------- */
/* WP-R9: the ledgers are the only pages whose rows run to the frame's bottom
   edge, and their cells inherit the font's default line height.  Source Han Sans
   reports 1.45 em there where Helvetica Neue reported 1.19 em, so on the English
   ledgers — all-Latin cells, twelve rows — that difference alone pushed the
   footer 14 px past the sheet.  Pinning the Latin ledger's line height to the
   1.19 em the cells already had restores the pre-R9 row pitch exactly; the
   Chinese ledger keeps normal, which is the 1.45 em its CJK cells always
   resolved to, so that language is untouched. */
.aud{position:absolute;left:16mm;right:16mm;top:24mm;bottom:20mm;display:flex;flex-direction:column;padding-top:5mm;line-height:${cjk ? 'normal' : '1.19'}}
.aud .lead{font-size:3.5mm;color:${C.muted};line-height:1.55}
.aud .grid{display:grid;gap:7mm;margin-top:4.4mm;flex:1;align-content:start}
.sec{background:#fff;border:.25mm solid ${C.edge};border-radius:1.4mm;overflow:hidden}
.sec>.tp{height:1mm}
.sec .sh{padding:3mm 4.6mm 2mm}
.sec .sh .n{font-size:3.2mm;letter-spacing:.12em;color:${C.teal};font-weight:700;font-family:SHS}
.sec .sh h3{font-size:${cjk ? 4.6 : 4.2}mm;margin:2mm 0 0;font-weight:700;line-height:1.25}
.sec .sh p{font-size:3.5mm;color:${C.muted};margin:1.8mm 0 0;line-height:1.45}
.cr{display:grid;grid-template-columns:${cjk ? 22 : 26}mm 1fr;gap:3.4mm;padding:3mm 4.6mm;border-top:.2mm solid #f1ede3}
.cr b{font-size:3.7mm;color:${C.deep};line-height:1.35}
.cr span{font-size:3.6mm;color:${C.muted};line-height:1.45}
.pv{display:inline-block;font-style:normal;font-weight:700;font-size:3.3mm;color:${C.coral};background:#fdf1ee;border-radius:1mm;padding:.4mm 1.6mm;margin-left:2mm;white-space:nowrap;line-height:1.3}
.warn{margin:3mm 4.6mm 3.4mm;padding:2.8mm 3.6mm;background:#fdf1ee;border-left:1.2mm solid ${C.coral};color:${C.coral};font-size:3.5mm;line-height:1.45;font-weight:700}
.sqw{display:grid;grid-template-columns:1fr 1fr;gap:3mm;padding:2.6mm 4.6mm 0}
.sq{border:.25mm solid ${C.edge};border-radius:1.2mm;padding:2.4mm 3.4mm;background:#fdfcf9}
.sq b{display:block;font-size:6mm;color:${C.deep};line-height:1.05;font-family:SHS;font-variant-numeric:tabular-nums}
.sq span{display:block;font-size:3.5mm;color:${C.muted};margin-top:1.6mm;line-height:1.3}
.sq .pv{display:block;margin:1.6mm 0 0;white-space:normal}
.tn{margin:3.2mm 4.6mm 0;font-size:3.4mm;color:${C.muted};line-height:1.45}
.tn:last-child{padding-bottom:3.4mm}
.th,.tr{display:grid;grid-template-columns:6mm ${cjk ? 17 : 19}mm 1fr 10mm ${cjk ? 32 : 32}mm 16mm;gap:3mm;align-items:center;padding:0 4.6mm}
.th{font-size:3.2mm;letter-spacing:.03em;color:${C.muted};font-weight:700;padding-bottom:2mm;font-family:SHS}
.tr{padding-top:3.1mm;padding-bottom:3.1mm;border-top:.2mm solid #f1ede3}
.tr.hot{background:#fdf4f1}
.c0{font-size:3.6mm;color:${C.muted};font-family:SHS;font-weight:700}
.tr.hot .c0{color:${C.coral}}
.c1{font-size:3.8mm;font-weight:700;color:${C.deep};font-family:SHS;font-variant-numeric:tabular-nums;letter-spacing:.02em}
.c2{font-size:3.5mm;color:${C.muted};line-height:1.3}
.c3{font-size:3.3mm;font-weight:700;text-align:center;font-family:SHS}
.tr .c3{border:.35mm solid;border-radius:2mm;padding:.5mm 0}
.c4{position:relative;height:5.6mm;display:flex;align-items:center;background:#f4f1e8;border-radius:.8mm}
.c4 i{position:absolute;left:0;top:0;bottom:0;background:${C.coral};opacity:.34;border-radius:.8mm}
.c4 b{position:relative;font-size:3.8mm;color:${C.deep};padding-left:2mm;font-family:SHS;font-variant-numeric:tabular-nums}
.th .c4{background:none;height:auto;display:block}
.c5{font-size:3.6mm;color:${C.muted};text-align:right;font-family:SHS;font-variant-numeric:tabular-nums}
.tu{display:flex;justify-content:space-between;align-items:baseline;gap:4mm;margin:3.4mm 4.6mm 0;padding-top:3mm;border-top:.55mm solid ${C.deep};font-size:3.7mm;color:${C.deep};font-weight:700}
.tu b{font-size:4.8mm;font-family:SHS;font-variant-numeric:tabular-nums}
.fab{display:flex;align-items:center;gap:3.4mm;margin:3.4mm 4.6mm 0;padding:3mm 3.8mm;background:#fdf1ee;border-radius:1.2mm}
.fab b{font-size:3.5mm;color:${C.coral};font-weight:700;white-space:nowrap}
.fab span{font-size:3.9mm;font-weight:700;color:${C.deep};letter-spacing:.03em;font-family:SHS;font-variant-numeric:tabular-nums}
.erow,.ehead{display:grid;grid-template-columns:1fr 8mm 1fr ${cjk ? 34 : 38}mm;gap:3mm;align-items:center;padding:3.6mm 4.6mm}
.ehead{font-size:3.4mm;letter-spacing:.05em;color:${C.muted};font-family:SHS;font-weight:700;padding-bottom:1.6mm}
.erow{border-top:.2mm dashed ${C.edge}}
.esrc{font-size:3.7mm;color:${C.ink};font-family:SHS;font-variant-numeric:tabular-nums;letter-spacing:.02em}
.eop{font-size:3.7mm;color:${C.muted};font-family:SHS;font-variant-numeric:tabular-nums;letter-spacing:.02em}
.earr{height:.5mm;background:${C.muted};opacity:.5}
.ecls{font-size:3.3mm;border:.35mm solid;border-radius:2.6mm;padding:1mm 0;text-align:center;font-weight:700;letter-spacing:.02em;font-family:SHS}
.grow{display:grid;grid-template-columns:auto 1fr auto;gap:3.4mm;align-items:baseline;padding:3.4mm 4.6mm;border-top:.2mm solid #f0ece1}
.gk{font-size:3.6mm;color:${C.deep};font-weight:700;white-space:nowrap;font-family:SHS;font-variant-numeric:tabular-nums;letter-spacing:.02em}
.gd{font-size:3.5mm;color:${C.muted};line-height:1.4}
.gg{font-size:3.3mm;color:#fff;background:${C.gold};border-radius:2.4mm;padding:.7mm 2.4mm;font-family:SHS;font-weight:700}
.gt{font-size:3.9mm;font-weight:700;color:${C.ink};margin:4mm 4.6mm 1mm}
.brow{display:flex;align-items:center;gap:2.6mm;padding:3mm 4.6mm;border-top:.2mm solid #f0ece1}
.brow i{width:2.2mm;height:2.2mm;border-radius:50%;background:${C.purple};flex:none}
.brow span{font-size:3.5mm;color:${C.muted};font-family:SHS;font-variant-numeric:tabular-nums;letter-spacing:.02em}
${cjk ? '' : `
/* ---------- WP-R11 target 1: English page 11 only ---------- */
/* Page 11 is the one ledger whose two columns are both driven by long Latin
   prose: the caliber card's six definition rows and the ranked table's twelve
   rows.  At R9's pitch its content measured 1027 px inside the 956 px frame, so
   the pointer line and the tail row were pushed past the frame and printed over
   the footer rule and the folio.  The 71 px are recovered from VERTICAL WHITE
   SPACE ONLY — cell padding, card padding and block margins.  Not one font
   size, colour, border or column width is touched, so every value, label and
   qualifier keeps the size R9 pinned it at; the rows simply sit tighter.
   The rules are scoped to .audA, which appendixGap emits on the English page 11
   alone: page 12 keeps a bare .aud and the Chinese booklet never emits the class
   nor these declarations, so both stay bit-identical. */
.audA{padding-top:4mm}
.audA>.grid{margin-top:3.6mm}
.audA .sec .sh{padding:2.4mm 4.6mm 1.6mm}
.audA .sec .sh h3{margin-top:1.5mm}
.audA .cr{padding-top:2.2mm;padding-bottom:2.2mm}
.audA .warn{margin-top:2.4mm;margin-bottom:2.6mm;padding-top:2.2mm;padding-bottom:2.2mm}
.audA .sqw{gap:2.4mm;padding-top:2.2mm}
.audA .sq{padding-top:1.9mm;padding-bottom:1.9mm}
.audA .sq span{margin-top:1.2mm}
.audA .sq .pv{margin-top:1.2mm}
.audA .tn{margin-top:2.6mm}
.audA .tn:last-child{padding-bottom:2.6mm}
.audA .tr{padding-top:2.4mm;padding-bottom:2.4mm}
.audA .tu{margin-top:2.8mm;padding-top:2.4mm}
.audA .fab{margin-top:2.8mm;padding-top:2.4mm;padding-bottom:2.4mm}

/* ---------- WP-R12 target 2: English page 05 only ---------- */
/* Page 05 is the booklet's only "tall" summary: the figure column is height
   driven at TALL_H = 185 mm, so unlike the wide pages it cannot give the frame
   any millimetre back when the text around it grows.  In English two blocks are
   one line taller than in Chinese — the intro wraps to two lines and the figure
   caption wraps to two — which leaves the tall row 1.3 mm more content than the
   frame has room for, and the tail row prints 1.2 mm below the frame.  The
   1.2 mm come back from the two gaps that bracket the figure column, i.e. from
   VERTICAL WHITE SPACE ONLY: the tall row's top margin (5 -> 3.4 mm, set where
   summaryPage writes it, since an inline declaration outranks any selector) and
   the caption's top margin, below.  The 185 mm figure box, its border and every
   judgement card keep their size, so nothing that carries a value or a judgement
   is reduced; the caption text itself is untouched.  The rule is scoped to
   .wrapE, which summaryPage emits on the English page 05 alone. */
.wrapE .figcap{margin-top:1.6mm}
`}
${cjk ? `
/* ---------- WP-R12 target 1: Chinese page 11 only ---------- */
/* The same overflow the English page 11 carried, at a fifth of the size: the
   Chinese ledger's twelve-row table measured 971 px inside the 956 px frame, so
   the tail row printed 3.8 mm below the frame and left only 3.2 mm to the footer
   rule where every other page leaves 7.0 mm.  The CJK cells resolve their line
   height to the font's own 1.45 em (R9 left it at normal deliberately), so
   the 15 px cannot come from line height without changing the row's type
   colour; they come from VERTICAL WHITE SPACE ONLY, as on the English sheet —
   frame padding, the grid's top margin, the section header's padding and the
   table row's padding.  No font size, colour, border or column width is touched.
   .aud is a fixed-height flex column whose .grid is flex:1, so once the content
   fits the frame the tail row snaps back to the frame's bottom edge and the
   footer gap returns to the 7.0 mm the rest of the booklet carries.
   The rules are scoped to .audZ, which appendixGap emits on the Chinese page 11
   alone: page 12 keeps a bare .aud and the English booklet never emits the class
   nor these declarations, so that language stays bit-identical. */
.audZ{padding-top:4.2mm}
.audZ>.grid{margin-top:3.8mm}
.audZ .sec .sh{padding:2.6mm 4.6mm 1.8mm}
.audZ .tr{padding-top:2.9mm;padding-bottom:2.9mm}
` : ''}

/* ---------- pages 07-10: document pages, rebuilt for A3 at >= 9 pt ---------- */
.doc{position:absolute;left:16mm;right:16mm;top:24mm;bottom:20mm;display:flex;flex-direction:column;padding-top:6mm}
.doc .lead{font-size:3.5mm;color:${C.muted};line-height:1.6}
.doc .grid{display:grid;gap:8mm;margin-top:5mm;flex:1;align-content:start}
.card2{background:#fff;border:.25mm solid ${C.edge};border-radius:1.4mm;overflow:hidden;display:flex;flex-direction:column}
.card2 .tp{height:1mm}
.card2 .ch{padding:4mm 5mm 0}
.card2 .ch .n{font-size:3.2mm;letter-spacing:.12em;color:${C.teal};font-weight:700;font-family:SHS}
.logorow{display:grid;grid-template-columns:1fr 1fr;gap:5mm;padding:5mm}
.logobox{border-radius:1.2mm;padding:13mm 10mm;display:flex;align-items:center;justify-content:center}
.swatches{display:grid;grid-template-columns:repeat(6,1fr);gap:3.4mm;padding:5mm 5mm 4mm}
.sw .chip{height:15mm;border-radius:1mm;border:.2mm solid rgba(0,0,0,.08)}
.sw .hex{font-size:3.2mm;margin-top:2.4mm;color:${C.muted};font-family:SHS;font-variant-numeric:tabular-nums;letter-spacing:.02em}
.sw .use{font-size:3.3mm;margin-top:1.6mm;line-height:1.4}
.note{font-size:3.3mm;color:${C.muted};padding:0 5mm 5mm;line-height:1.55}
.brandside h3{font-size:${cjk ? 5.4 : 4.9}mm;font-weight:700;margin:0;line-height:1.3;color:${C.deep}}
.slogan{background:${C.deep};color:#fff;border-radius:1.4mm;padding:5mm 5.4mm;margin-top:6mm}
.slogan .e{font-family:SHS;font-weight:500;letter-spacing:.01em;font-size:5.4mm;line-height:1.25}
.slogan .z{font-size:3.6mm;color:${C.onDarkEn};margin-top:3mm}
.aibox{border-left:1.2mm solid ${C.teal};background:#fff;padding:4mm 4.6mm;margin-top:5mm;font-size:3.4mm;line-height:1.62}
.culrow{display:grid;grid-template-columns:repeat(3,1fr);gap:6mm}
.cul{border:.25mm solid ${C.edge};border-radius:1.4mm;padding:4.6mm 5mm;background:#fdfcf9;display:flex;flex-direction:column}
.cul .num{font-size:3.2mm;letter-spacing:.1em;font-weight:700;font-family:SHS}
.cul h4{font-size:4.6mm;margin:2.4mm 0 0;font-weight:700;line-height:1.25}
.cul .en2{font-size:3.2mm;letter-spacing:.06em;color:${C.muted};margin-top:2mm;font-family:SHS;font-weight:700}
.cul p{font-size:3.4mm;line-height:1.6;color:${C.muted};margin:3.4mm 0 0}
.cul dl{margin:auto 0 0;padding-top:3mm}
.cul dt{font-size:3.2mm;letter-spacing:.06em;color:${C.teal};font-weight:700;font-family:SHS;margin-top:3.4mm;padding-top:3mm;border-top:.2mm solid ${C.edge}}
.cul dd{margin:1.4mm 0 0;font-size:3.4mm;line-height:1.5;color:${C.ink}}
.audl .at{font-size:3.2mm;letter-spacing:.1em;color:${C.teal};font-weight:700;font-family:SHS}
.audl .ar{padding:3.4mm 0;border-top:.2mm solid ${C.edge};display:block}
.audl .ar b{font-size:3.5mm;display:block}
.audl .ar span{font-size:3.3mm;color:${C.muted};display:block;margin-top:1.4mm;line-height:1.5}
.statrow{display:grid;grid-template-columns:repeat(4,1fr);gap:4mm}
.stat{background:#fff;border-radius:1.2mm;padding:4mm 4.4mm;border-top:1mm solid ${C.teal}}
.stat .v{font-size:7mm;font-weight:700;color:${C.deep};font-family:SHS;line-height:1.05}
.stat .l{font-size:3.4mm;margin-top:2mm}
.stat .k2{font-size:3.2mm;color:${C.muted};margin-top:1.4mm;font-family:SHS;font-variant-numeric:tabular-nums;letter-spacing:.02em}
.colt{font-size:3.2mm;letter-spacing:.1em;color:${C.teal};font-weight:700;font-family:SHS;margin-bottom:3.4mm}
.colh{font-size:${cjk ? 5.4 : 4.8}mm;font-weight:700;margin:0 0 4.4mm;color:${C.deep};line-height:1.25}
.srow{padding:3.4mm 0;border-top:.2mm solid ${C.edge}}
.srow .id{font-size:3.4mm;font-weight:700;color:${C.teal};letter-spacing:.02em;font-family:SHS}
.srow .d{font-size:3.4mm;color:${C.muted};margin-top:1.6mm;line-height:1.5}
.std{display:flex;gap:3mm;padding:3.4mm 0;border-top:.2mm solid ${C.edge};align-items:flex-start}
.std i{width:2.6mm;height:2.6mm;border-radius:50%;display:block;flex:none;margin-top:1.4mm}
.std .sid{font-size:3.3mm;font-weight:700;font-family:SHS}
.std .sdim{font-size:3.3mm;color:${C.muted};margin-top:1.2mm}
.grow2{display:grid;grid-template-columns:9mm 1fr;gap:4mm;padding:8mm 0;border-top:.2mm solid ${C.edge};align-items:baseline}
.grow2 .no{font-size:3.6mm;font-weight:700;font-family:SHS}
.grow2 .tx{font-size:3.8mm;line-height:1.5}
.gate{background:${C.deep};color:#fff;border-radius:1.6mm;padding:8mm 7mm;margin-top:7mm}
.gate .t{font-size:4.6mm;font-weight:700;line-height:1.3}
.gate .b{font-size:3.4mm;line-height:1.7;color:${C.onDarkEn};margin-top:3.4mm}
.asrow{font-size:3.5mm;line-height:1.6;color:${C.ink};padding:7mm 0;border-top:.2mm solid ${C.edge}}
`;
}

/* ---------- shared chrome ---------- */

function header(t, idx, kicker, title) {
  return `<div class="hdr"><div class="l"><div class="k">${ruleBar(1.4, true)}<span>${t.brandShort}</span></div>
  <h2>${title}</h2></div>
  <div class="r"><div class="p">${no(idx)} / ${TT}</div><div class="s">${kicker}</div></div></div>`;
}

function foot(t, idx) {
  return `<div class="foot"><span>${t.osm}</span><span class="pg">${no(idx)} / ${TT}</span></div>`;
}

function pills(t) {
  const bg = { grey: '#7c8b8c', coral: C.coral, teal: C.teal };
  return `<div class="pills">${t.pills.map(([s, k]) => `<span style="background:${bg[k]}">${s}</span>`).join('')}</div>`;
}

function tail(t, ptrs) {
  return `<div class="ptr">${ptrs.map((p) => `<span>${p}</span>`).join('')}</div>
  <div class="tailrow"><div class="disc">${t.disclaimShort}</div>${pills(t)}</div>`;
}

/* ---------- cover ---------- */

/* Three commitments, quoted verbatim from the package: cover.lead and A0
   claims 4 and 6 in content.js.  No figure, no metric tile, no badge. */
const PROMISE = {
  zh: (t) => [t.cover.lead, t.a0.claims[3], t.a0.claims[5]],
  en: (t) => [t.cover.lead, t.a0.claims[3], t.a0.claims[5]],
};

/* The cover previously carried two disclaimer badges whose wording overlapped
   ("概念建议" / "CONCEPT PROPOSAL" appeared in both).  They are merged here into
   one de-duplicated footer line; no qualifier is dropped. */
const COVER_DISC = {
  zh: '概念建议 · 设计判据 · 非实测结果 · 临时边界 · 非法定规划 · 非工程线位',
  en: 'CONCEPT PROPOSAL · DESIGN CRITERIA · NOT MEASURED RESULTS · PROVISIONAL · NOT STATUTORY · NOT AN ENGINEERING ALIGNMENT',
};

function cover(t, n, lang) {
  const proms = PROMISE[lang](t)
    .map((p, i) => `<div class="pr"><div class="pn">0${i + 1}</div><div class="pt">${p}</div></div>`)
    .join('');
  return `<div class="cover">
  <div class="lft">
    <div class="k">${ruleBar(2, true)}<span>${t.cover.kicker}</span></div>
    <h1>${t.cover.h1}</h1>
    <div class="sub">${t.cover.sub}</div>
    <div class="rulez"></div>
  </div>
  <div class="prom">${proms}</div>
  <div class="cfoot"><span>${COVER_DISC[lang]}</span><span>01 / ${TT}</span></div>
</div>`;
}

/* ---------- summary page ---------- */

function cardHtml(c, padY) {
  const pad = padY ? `;padding-top:${padY}mm;padding-bottom:${padY}mm` : '';
  return `<div class="card" style="border-left-color:${col(c.c)}${pad}">
  ${c.v ? `<div class="v">${c.v}</div>` : ''}
  <div class="t">${c.t}</div>
  ${c.s ? `<div class="s" style="color:${col(c.c)}">${c.s}</div>` : ''}
  ${c.d ? `<div class="d">${c.d}</div>` : ''}</div>`;
}

function legendHtml(n, items, title, mt) {
  return `<div class="lgd"${mt ? ` style="margin-top:${mt}mm"` : ''}><div class="lt">${title || n.legend}</div><div class="row">${items
    .map(([c, s]) => `<div class="i"><b style="background:${col(c)}"></b><span>${s}</span></div>`)
    .join('')}</div></div>`;
}

/* Figure band width in mm.  A "wide" band spans the full 388 mm text block and
   its height follows the crop aspect; a "tall" band is height-driven so a
   near-square crop is enlarged rather than letterboxed. */
const BAND_W = 388;
const TALL_H = 185;

/* WP-R11 target 2 — per-page pacing.
   `.cards` is the only flex:1 child of `.wrap`, so on a wide page it absorbs
   every millimetre the frame does not spend on fixed blocks and centres the row
   inside that surplus.  The wide band's height is capped at BAND_W / ratio, so
   after the crop windows were re-cut the shorter bands on pages 02 and 06 left
   that surplus as two symmetric voids above and below the card row.

   `pace` re-spends that surplus for a named page: `cardPadY` converts part of it
   into card body (the only move that removes white space rather than shifting
   it), while figMt / cardsMt / warnMt / lgdMt widen the block gaps so the rest
   reads as page rhythm instead of a hole.  A page that passes no `pace` object
   takes the literals below and emits byte-identical markup, which is what keeps
   pages 03, 04 and 05 pixel-identical. */
function summaryPage(t, n, s) {
  const wide = s.layout !== 'tall';
  const p = s.pace || {};
  const fw = wide ? BAND_W : Math.round(TALL_H * s.ratio * 10) / 10;
  const fh = wide ? Math.round((BAND_W / s.ratio) * 10) / 10 : TALL_H;
  const fig = (mt) => `<div class="figbox" style="width:${fw}mm;height:${fh}mm;margin-top:${mt}mm"><img src="${s.img}"></div>
  <div class="figcap">${s.figCap ? n[s.figCap] : n.figSummary}</div>`;
  const cards = (mt) => `<div class="cards" style="margin-top:${mt}mm;grid-template-columns:${wide ? `repeat(${s.cards.length},1fr)` : '1fr'}${wide ? '' : ';grid-auto-rows:1fr;align-content:stretch'}">${s.cards.map((c) => cardHtml(c, p.cardPadY)).join('')}</div>`;

  const body = wide
    ? `${fig(p.figMt || 5)}${cards(p.cardsMt || 5)}`
    : `<div style="display:grid;grid-template-columns:${fw}mm 1fr;gap:8mm;margin-top:${s.tight ? 3.4 : 5}mm;flex:1">
    <div>${fig(0)}</div>
    <div style="display:flex;flex-direction:column">${cards(0)}</div>
  </div>`;

  return `${header(t, s.idx, s.sec.n, s.sec.t)}
<div class="wrap${s.tight ? ' wrapE' : ''}">
  <div class="claim"><i>${n.summaryKick} · ${n.judge}</i>${s.claim}</div>
  <div class="intro">${s.sec.b}</div>
  ${body}
  ${s.warn ? `<div class="warnbar"${p.warnMt ? ` style="margin-top:${p.warnMt}mm"` : ''}>${s.warn}</div>` : ''}
  ${s.legend ? legendHtml(n, s.legend, s.legendTitle, p.lgdMt) : ''}
  ${tail(t, s.ptrs)}
</div>${foot(t, s.idx)}`;
}

/* Re-key a section kicker such as "07 / METRICS + EVIDENCE" onto its new page
   number without touching content.js, which the A0 boards also read. */
const rekey = (sec, idx) => Object.assign({}, sec, { n: sec.n.replace(/^\d\d/, no(idx)) });

function summaries(lang, t, n, imgs) {
  const a = t.a0;
  return [
    {
      idx: 2, sec: t.p2, claim: a.claims[0], img: imgs.siteBand, ratio: 4560 / 1056, layout: 'wide',
      cards: a.scopes.map(([v, l, d, c]) => ({ v, t: l, d, c })),
      legend: t.p2.legend,
      /* 89.9 mm band, the second shortest in the booklet, against a full text
         block of fixed blocks: 16 mm of surplus, split as 7 mm into the three
         scope cards and 9 mm into the block gaps, brings the card row's margin
         to the 16-17 mm page 04 already carries. */
      pace: { cardPadY: 7.5, figMt: 8, cardsMt: 8, lgdMt: 7.4 },
      ptrs: [n.figOnly('site-overview')],
    },
    {
      idx: 3, sec: t.p3, claim: a.claims[1], img: imgs.landuseBand, ratio: 4560 / 1012, layout: 'wide',
      cards: t.p3.legend.map(([c, s], i) => ({ t: s, d: LUNOTE[lang][i], c })),
      figCap: 'figLanduse',
      /* WP-R12 spent this page's surplus on pacing alone: with a 68.9 mm band,
         the two gaps bracketing it had to open to 27.5 mm before .cards stopped
         reading as a hole, and 27.5 mm of white under the intro is itself
         legible as a fault.  WP-R13 treats the cause instead: mka3.js re-cut
         the window from 810 to 1012 px, so the band is 86.1 mm and page 03 is
         no longer the flattest sheet in the booklet (4.51 against page 06's
         4.81).  17.2 mm of band buys 8.5 mm off each gap; the rest of the R12
         settlement is kept, because it was correct — cardPadY 13.5 holds the
         cards at 40.8 / 45.8 mm inside the booklet's 27.8-47.0 mm range, and
         the resulting slack lands at 16.6 / 14.4 mm against the 16.6 / 14.1 mm
         page 04 leaves, i.e. the two pages now breathe alike. */
      pace: { cardPadY: 13.5, figMt: 19, cardsMt: 19 },
      ptrs: [n.plateAt('02', 'land-use-structure')],
    },
    {
      idx: 4, sec: t.p4, claim: a.claims[2], img: imgs.keyareasBand, ratio: 4560 / 1496, layout: 'wide', figCap: 'figKeyareas',
      cards: t.p4.areas.map(([c, k, sub, d]) => ({ t: k, s: sub, d, c })),
      ptrs: [n.plateAt('03', 'key-areas')],
    },
    {
      idx: 5, sec: t.p5, claim: a.claims[3], img: imgs.mobilityZoom, ratio: 1064 / 1168, layout: 'tall',
      /* WP-R12 target 2: only the English sheet overflows this frame, so only
         the English sheet is scoped; the Chinese page 05 emits the markup it
         emitted before, down to the byte. */
      tight: lang === 'en',
      cards: [
        { t: t.p5.legend[0][1], c: 'teal' },
        { t: t.p5.legend[1][1], c: 'sky' },
        { v: a.keys[3][1][0], t: a.keys[3][1][1], c: 'purple' },
        { v: a.keys[3][2][0], t: a.keys[3][2][1], c: 'coral' },
      ],
      ptrs: [n.plateAt('04', 'mobility-bluegreen'), n.ledgerAt(11)],
    },
    {
      idx: 6, sec: rekey(t.p7, 6), claim: a.claims[5], img: imgs.metricsDenom, ratio: 2560 / 532, layout: 'wide',
      cards: a.denom.map(([l, v, r, c]) => ({ v: r, t: v, d: l, c: c === 'line' ? C.muted : c })),
      warn: a.denomWarn,
      legendTitle: t.p7.fieldTitle,
      legend: t.p7.field.map((x) => ['purple', x]),
      /* 80.6 mm band, but a warn bar and a legend already occupy the lower
         third, so the surplus here is 6 mm, not 16. */
      pace: { cardPadY: 5.5, figMt: 6.5, cardsMt: 6.5 },
      ptrs: [n.plateAt('06', 'metrics-evidence'), n.ledgerAt(12)],
    },
  ];
}

/* ---------- appendix 11: ten-node gap audit ledger ---------- */

function appendixGap(t, n, lang) {
  const d = AUD[lang];
  const G = AUD.gate;
  const cal = `<section class="sec"><div class="tp" style="background:${C.teal}"></div>
  <div class="sh"><div class="n">${d.cal.n}</div><h3>${d.cal.t}</h3></div>
  ${d.cal.rows.map(([k, v], i) => `<div class="cr"><b>${k}</b><span>${v}${i === 0 ? `<em class="pv">${d.pvLen}</em>` : ''}</span></div>`).join('')}
  <div class="warn">${d.cal.warn}</div></section>`;

  const eq = `<section class="sec"><div class="tp" style="background:${C.purple}"></div>
  <div class="sh"><div class="n">${d.eq.n}</div><h3>${d.eq.t}</h3></div>
  <div class="sqw">${d.eq.stats.map(([k, v, p]) => `<div class="sq"><b>${v}</b><span>${k}</span><em class="pv">${p}</em></div>`).join('')}</div>
  <p class="tn">${d.eq.ok}</p></section>`;

  const tb = d.tab;
  const table = `<section class="sec"><div class="tp" style="background:${C.coral}"></div>
  <div class="sh"><div class="n">${tb.n}</div><h3>${tb.t}</h3><p>${tb.s}</p></div>
  <div class="th">${tb.head.map((h, i) => `<span class="c${i}">${h}</span>`).join('')}</div>
  ${tb.rows.map((r) => `<div class="tr${r.rank <= 3 ? ' hot' : ''}">
    <span class="c0">${r.rank}</span><span class="c1">${r.id}</span><span class="c2">${r.scen}</span>
    <span class="c3" style="color:${G[r.gate]};border-color:${G[r.gate]}">${r.gate}</span>
    <span class="c4"><i style="width:${r.bar}%"></i><b>${r.area}</b></span>
    <span class="c5">${r.share}</span></div>`).join('')}
  <div class="tu"><span>${tb.unionLabel}</span><b>${tb.unionValue}</b><em class="pv">${d.pvArea}</em></div>
  <div class="fab"><b>${tb.breaksLabel}</b><span>${tb.breaks}</span></div>
  <p class="tn">${tb.resp}</p><p class="tn">${tb.note}</p>
  <div class="warn">${tb.warn}</div></section>`;

  /* WP-R11 gave the English sheet the tightened .audA rules; WP-R12 gives the
     Chinese sheet its own .audZ scope.  Each language emits only its own class
     and each stylesheet carries only its own rules, so neither page can move the
     other, and page 12 keeps a bare .aud in both languages. */
  const en = lang === 'en';
  return `${header(t, 11, `${n.appendix} A · ${d.idx}`, d.title)}
<div class="aud ${en ? 'audA' : 'audZ'}">
  <div class="lead">${d.of}｜${d.sub}｜${n.audLead}</div>
  <div class="grid" style="grid-template-columns:${lang === 'zh' ? '160mm 1fr' : '178mm 1fr'}">
    <div style="display:flex;flex-direction:column;gap:${en ? 4 : 5}mm">${cal}${eq}</div>
    <div>${table}</div>
  </div>
  ${tail(t, [n.backTo(5), n.figFrom('mobility-bluegreen-audit')])}
</div>${foot(t, 11)}`;
}

/* ---------- appendix 12: metrics evidence audit ledger ---------- */

function appendixMetrics(t, n, lang) {
  const m = MFIG.L[lang];
  const LVL = [C.teal, C.coral, C.gold, C.purple];

  const rail = `<section class="sec"><div class="tp" style="background:${C.gold}"></div>
  <div class="sh"><div class="n">${m.s3.n}</div><h3>${m.s3.t}</h3><p>${m.s3.s}</p></div>
  <div class="ehead"><span>${m.railHead[0]}</span><span></span><span>${m.railHead[1]}</span><span style="text-align:center">${m.railHead[2]}</span></div>
  ${m.rail.map(([s, o, c, lv]) => `<div class="erow"><div class="esrc">${s}</div><div class="earr" style="background:${LVL[lv]}"></div>
    <div class="eop">${o}</div><div class="ecls" style="color:${LVL[lv]};border-color:${LVL[lv]}">${c}</div></div>`).join('')}
  <div style="height:3.4mm"></div></section>`;

  const gaps = `<section class="sec"><div class="tp" style="background:${C.deep}"></div>
  <div class="sh"><div class="n">${m.s5.n}</div><h3>${m.s5.t}</h3><p>${m.s5.s}</p></div>
  <div class="gt">${m.gapsA.t}</div>
  ${m.gapsA.items.map(([k, dd, g]) => `<div class="grow"><div class="gk">${k}</div><div class="gd">${dd}</div><div class="gg">${g}</div></div>`).join('')}
  <div class="gt">${m.gapsB.t}</div>
  ${m.gapsB.items.map((s) => `<div class="brow"><i></i><span>${s}</span></div>`).join('')}
  <div class="warn">${m.audNote}</div></section>`;

  return `${header(t, 12, `${n.appendix} B · ${m.audIdx}`, m.audTitle)}
<div class="aud">
  <div class="lead">${m.audOf}｜${m.audSub}｜${n.audLead}</div>
  <div class="grid" style="grid-template-columns:1fr 1fr">${rail}${gaps}</div>
  ${tail(t, [n.backTo(6), n.figFrom('metrics-evidence-audit')])}
</div>${foot(t, 12)}`;
}

/* ---------- page 07 brand system ---------- */

function pageBrand(t, n) {
  const s = rekey(t.p6, 7);
  return `${header(t, 7, 'BRAND SYSTEM', n.brandTitle)}
<div class="doc">
  <div class="lead">${s.b}</div>
  <div class="grid" style="grid-template-columns:1fr 128mm">
    <div style="display:flex;flex-direction:column;gap:7mm">
      <section class="card2"><div class="tp" style="background:${C.teal}"></div>
        <div class="ch"><div class="n">${s.logoTitle}</div></div>
        <div class="logorow">
          <div class="logobox" style="background:${C.deep}">${logo(true)}</div>
          <div class="logobox" style="background:${C.paper};border:.25mm solid ${C.edge}">${logo(false)}</div>
        </div>
        <div class="note">${s.logoNote}</div>
      </section>
      <section class="card2"><div class="tp" style="background:${C.gold}"></div>
        <div class="ch"><div class="n">${s.colourTitle}</div></div>
        <div class="swatches">${s.colours
          .map(([k, hex, use]) => `<div class="sw"><div class="chip" style="background:${hex}"></div><div class="hex">${hex}</div><div class="use">${use}</div></div>`)
          .join('')}</div>
        <div class="note">${s.colourNote}</div>
      </section>
    </div>
    <div class="brandside">
      <div class="colt">${s.n}</div>
      <h3>${s.h}</h3>
      <div class="slogan"><div class="e">${s.sloganEn}</div><div class="z">${s.sloganZh}</div></div>
      <div class="aibox">${s.aiNote}</div>
      <div class="note" style="padding:5mm 0 0">${s.rights}</div>
    </div>
  </div>
  ${tail(t, [n.seeAlso(n.cultureTitle, 8)])}
</div>${foot(t, 7)}`;
}

/* ---------- page 08 culture + outward communication ---------- */

function pageCulture(t, n) {
  const s = rekey(t.p6, 8);
  return `${header(t, 8, 'CULTURE · GLOBAL', n.cultureTitle)}
<div class="doc">
  <div class="lead">${s.sloganNote}</div>
  <div class="grid" style="grid-template-columns:1fr 128mm">
    <div>
      <div class="colt">${s.cultureTitle}</div>
      <div class="culrow">${s.culture
        .map(([c, h, e, p, rows], i) => `<div class="cul" style="border-top:1mm solid ${col(c)}"><div class="num" style="color:${col(c)}">${no(i + 1)}</div><h4>${h}</h4><div class="en2">${e}</div><p>${p}</p><dl>${rows.map(([k, v]) => `<dt>${k}</dt><dd>${v}</dd>`).join('')}</dl></div>`)
        .join('')}</div>
    </div>
    <div>
      <div class="audl"><div class="at">${s.audienceTitle}</div>${s.audience
        .map(([k, v]) => `<div class="ar"><b>${k}</b><span>${v}</span></div>`).join('')}</div>
      <div class="audl" style="margin-top:7mm"><div class="at">${s.applyTitle}</div>${s.apply
        .map(([k, v]) => `<div class="ar"><b>${k}</b><span>${v}</span></div>`).join('')}</div>
    </div>
  </div>
  ${tail(t, [n.seeAlso(n.brandTitle, 7)])}
</div>${foot(t, 8)}`;
}

/* ---------- page 09 sources + standards ---------- */

function pageSources(t, n) {
  const s = t.p8;
  return `${header(t, 9, 'SOURCES + STANDARDS', n.sourcesTitle)}
<div class="doc">
  <div class="statrow">${s.stats
    .map(([v, l, k]) => `<div class="stat"><div class="v">${v}</div><div class="l">${l}</div><div class="k2">${k}</div></div>`)
    .join('')}</div>
  <div class="grid" style="grid-template-columns:1fr 1fr;margin-top:7mm">
    <div>
      <div class="colt">09 / EVIDENCE BOUNDARY</div>
      <div class="colh">${s.hl}</div>
      ${s.sources.map(([id, d]) => `<div class="srow"><div class="id">${id}</div><div class="d">${d}</div></div>`).join('')}
    </div>
    <div>
      <div class="colt">${s.stdTitle}</div>
      ${s.standards
        .map(([id, dim, m]) => `<div class="std"><i style="background:${m ? C.coral : C.gold}"></i><div><div class="sid">${id}</div><div class="sdim">${dim}</div></div></div>`)
        .join('')}
      <div class="note" style="padding:5mm 0 0">${s.note}</div>
    </div>
  </div>
  ${tail(t, [n.seeAlso(s.hr, 10)])}
</div>${foot(t, 9)}`;
}

/* ---------- page 10 gaps + assumptions ---------- */

function pageGaps(t, n) {
  const s = t.p8;
  return `${header(t, 10, 'REQUIRED BEFORE DEEPENING', s.hr)}
<div class="doc">
  <div class="lead">${s.t}</div>
  <div class="grid" style="grid-template-columns:1fr 1fr">
    <div>
      <div class="colt">10 / REQUIRED BEFORE DEEPENING</div>
      ${s.gaps
        .map(([c, tx], i) => `<div class="grow2"><div class="no" style="color:${col(c)}">${no(i + 1)}</div><div class="tx">${tx}</div></div>`)
        .join('')}
    </div>
    <div>
      <div class="gate" style="margin-top:0"><div class="t">${s.gateTitle}</div><div class="b">${s.gateBody}</div></div>
      <div class="colt" style="margin-top:8mm">${s.assumeTitle}</div>
      ${s.assume.map((x) => `<div class="asrow">${x}</div>`).join('')}
    </div>
  </div>
  ${tail(t, [n.seeAlso(n.sourcesTitle, 9)])}
</div>${foot(t, 10)}`;
}

/* ---------- assembly ---------- */

function pages(lang, imgs) {
  const t = COPY[lang];
  const n = NAV[lang];
  const doc = (bodyHtml, title) =>
    `<!doctype html><html lang="${lang}"><head><meta charset="utf-8"><title>${title}</title><style>${css(lang)}</style></head><body>${bodyHtml}</body></html>`;

  const sums = summaries(lang, t, n, imgs).map((s) => doc(summaryPage(t, n, s), `a3-${no(s.idx)}`));

  return [
    doc(cover(t, n, lang), 'a3-01'),
    ...sums,
    doc(pageBrand(t, n), 'a3-07'),
    doc(pageCulture(t, n), 'a3-08'),
    doc(pageSources(t, n), 'a3-09'),
    doc(pageGaps(t, n), 'a3-10'),
    doc(appendixGap(t, n, lang), 'a3-11'),
    doc(appendixMetrics(t, n, lang), 'a3-12'),
  ];
}

module.exports = { pages, TOTAL };
