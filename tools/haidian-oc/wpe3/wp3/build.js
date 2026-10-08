'use strict';
const fs = require('fs');
const path = require('path');

const C = {
  deep: '#10383d', teal: '#177c78', coral: '#d76450',
  purple: '#6b5b95', gold: '#d6a13b', paper: '#f2efe7',
  line: '#cbd3cf', muted: '#68787b', edge: '#e2ddd0',
  onDarkLine: '#5fb3ab', onDarkNode: '#f2efe7', onDarkOrigin: '#e08975',
  onDarkRule: '#3f6165', onDarkCn: '#f2efe7', onDarkEn: '#9ecdc7',
};

/* ---------- logo, inline, fixed colours ---------- */
function logo(c) {
  return `<svg viewBox="0 0 640 200" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="万感京张 EVERY SENSE JING-ZHANG">
  <g fill="none" stroke="${c.line}" stroke-linecap="round" stroke-width="6" stroke-dasharray="0.5 13.5">
    <path d="M34 61H118.41"/><path d="M234 61H149.59"/>
    <path d="M34 139H118.41"/><path d="M234 139H149.59"/>
  </g>
  <g fill="none" stroke="${c.line}" stroke-linecap="round" stroke-width="9">
    <path d="M34 87H94.06"/><path d="M234 87H173.94"/>
    <path d="M34 113H94.06"/><path d="M234 113H173.94"/>
  </g>
  <g fill="none" stroke="${c.node}" stroke-width="7" stroke-linecap="round">
    <path d="M106.18 88.76A30 30 0 0 1 161.82 88.76"/>
    <path d="M161.82 111.24A30 30 0 0 1 106.18 111.24"/>
  </g>
  <circle fill="${c.origin}" cx="134" cy="100" r="6.5"/>
  <path stroke="${c.rule}" stroke-width="1.5" d="M262 52V146"/>
  <text x="288" y="106" fill="${c.cn}" font-family="Georgia, 'Songti SC', serif" font-size="62" letter-spacing="10">万感京张</text>
  <text x="288" y="142" fill="${c.en}" font-family="'Helvetica Neue', Arial, sans-serif" font-size="18.5" font-weight="700" letter-spacing="2.8">EVERY SENSE JING-ZHANG</text>
</svg>`;
}
const logoLight = logo({ line: C.teal, node: C.deep, origin: C.coral, rule: C.line, cn: C.deep, en: C.teal });
const logoDark = logo({ line: C.onDarkLine, node: C.onDarkNode, origin: C.onDarkOrigin, rule: C.onDarkRule, cn: C.onDarkCn, en: C.onDarkEn });

/* ---------- mark construction diagram ---------- */
function markDiagram(L) {
  const num = (x, y, n, col) =>
    `<circle cx="${x}" cy="${y}" r="9" fill="${col}"/><text x="${x}" y="${y + 4.2}" text-anchor="middle" fill="#fff" font-family="Georgia, serif" font-size="11">${n}</text>`;
  return `<svg viewBox="0 0 268 200" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="${L.a11yMark}">
  <circle cx="130" cy="100" r="42" fill="none" stroke="${C.line}" stroke-width="1" stroke-dasharray="3 5"/>
  <g fill="none" stroke="${C.teal}" stroke-linecap="round" stroke-width="6" stroke-dasharray="0.5 13.5">
    <path d="M30 61H114.41"/><path d="M230 61H145.59"/>
    <path d="M30 139H114.41"/><path d="M230 139H145.59"/>
  </g>
  <g fill="none" stroke="${C.teal}" stroke-linecap="round" stroke-width="9">
    <path d="M30 87H90.06"/><path d="M230 87H169.94"/>
    <path d="M30 113H90.06"/><path d="M230 113H169.94"/>
  </g>
  <g fill="none" stroke="${C.deep}" stroke-width="7" stroke-linecap="round">
    <path d="M102.18 88.76A30 30 0 0 1 157.82 88.76"/>
    <path d="M157.82 111.24A30 30 0 0 1 102.18 111.24"/>
  </g>
  <circle fill="${C.coral}" cx="130" cy="100" r="6.5"/>
  <g stroke="${C.muted}" stroke-width="1">
    <path d="M54 35V57"/><path d="M130 35V66"/><path d="M140 100H236"/>
  </g>
  ${num(54, 24, '1', C.teal)}${num(130, 24, '2', C.deep)}${num(248, 100, '3', C.coral)}
</svg>`;
}

/* ---------- grammar extension vignettes ---------- */
const F_SANS = "'PingFang SC','Source Han Sans SC','Helvetica Neue',Arial,sans-serif";
const F_SERIF = "Georgia,'Songti SC',serif";
const F_MONO = "'SF Mono',Menlo,Consolas,monospace";
/* WP-R14: section 03 declares that every published face is Source Han Sans SC
   under SIL OFL 1.1, so the section's own specimens must be set in that family
   and nothing else — no generic tail, which is what silently pulls a commercial
   system face in when a glyph is missing (same rule as the WP-R9 PDF backstop).
   The three roles are separated by weight, tracking and tabular figures, which
   is how the four drawing PDFs already separate them. */
const F_SHS = "'Source Han Sans SC'";

function miniMark(x, y, s, lineCol, nodeCol, originCol) {
  // compact mark, natural width 34 at s=1, centred on (x, y)
  return `<g transform="translate(${x} ${y}) scale(${s})">
    <g fill="none" stroke="${lineCol}" stroke-linecap="round" stroke-width="1.6" stroke-dasharray="0.2 3.4"><path d="M-17 -7H-5"/><path d="M17 -7H5"/><path d="M-17 7H-5"/><path d="M17 7H5"/></g>
    <g fill="none" stroke="${lineCol}" stroke-linecap="round" stroke-width="2.4"><path d="M-17 -2.4H-10.6"/><path d="M17 -2.4H10.6"/><path d="M-17 2.4H-10.6"/><path d="M17 2.4H10.6"/></g>
    <g fill="none" stroke="${nodeCol}" stroke-width="1.9" stroke-linecap="round"><path d="M-5.9 -2.1A6.3 6.3 0 0 1 5.9 -2.1"/><path d="M5.9 2.1A6.3 6.3 0 0 1 -5.9 2.1"/></g>
    <circle fill="${originCol}" cx="0" cy="0" r="1.5"/>
  </g>`;
}

function vgWayfinding(L) {
  let paving = '';
  for (let x = 6; x <= 300; x += 8) paving += `<circle cx="${x}" cy="88" r="1.6" fill="${C.teal}"/>`;
  return `<svg viewBox="0 0 306 100" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="${L.vg[0].alt}">
  <path d="M0 95H306" stroke="${C.line}" stroke-width="1.2"/>${paving}
  <rect x="44" y="8" width="96" height="76" fill="${C.paper}" stroke="${C.deep}" stroke-width="1.4"/>
  ${miniMark(92, 22, 1.05, C.teal, C.deep, C.coral)}
  <path d="M54 32H130" stroke="${C.line}" stroke-width="0.8"/>
  <text x="54" y="46" fill="${C.deep}" font-family="${F_SERIF}" font-size="13">${L.vg[0].sign}</text>
  <text x="54" y="55" fill="${C.teal}" font-family="${F_SANS}" font-size="5.2" letter-spacing="0.4" font-weight="700">COMMON GAUGE GATE</text>
  <path d="M54 61H130" stroke="${C.line}" stroke-width="0.8"/>
  <text x="54" y="72" fill="${C.deep}" font-family="${F_SANS}" font-size="5.8">${L.vg[0].dir}</text>
  <path d="M118 69.6H132M128 66.4L132 69.6L128 72.8" stroke="${C.deep}" stroke-width="1.4" fill="none"/>
  <rect x="54" y="76" width="42" height="6" rx="3" fill="${C.coral}"/>
  <text x="75" y="80.6" text-anchor="middle" fill="#fff" font-family="${F_SANS}" font-size="4.4" font-weight="700">${L.vg[0].aioff}</text>
  <path d="M92 84V95" stroke="${C.deep}" stroke-width="2"/>
  <rect x="160" y="52" width="62" height="32" fill="#fff" stroke="${C.deep}" stroke-width="1.2"/>
  <text x="166" y="62" fill="${C.deep}" font-family="${F_SANS}" font-size="5.6" font-weight="700">${L.vg[0].tactile}</text>
  <g fill="${C.purple}">${Array.from({ length: 12 }, (_, i) => `<circle cx="${167 + i * 4.4}" cy="70" r="1.5"/>`).join('')}</g>
  <g fill="${C.purple}">${Array.from({ length: 12 }, (_, i) => `<circle cx="${167 + i * 4.4}" cy="77" r="1.5"/>`).join('')}</g>
  <path d="M191 84V95" stroke="${C.deep}" stroke-width="1.6"/>
  <path d="M252 34V95" stroke="${C.deep}" stroke-width="2.4"/>
  <circle cx="252" cy="28" r="8" fill="${C.coral}"/>
  <path d="M248.6 28H255.4M252 24.6V31.4" stroke="#fff" stroke-width="1.6"/>
  <text x="252" y="14" text-anchor="middle" fill="${C.deep}" font-family="${F_SANS}" font-size="6">${L.vg[0].help}</text>
</svg>`;
}

function vgPaving(L) {
  const cx = 153, cy = 46, R = 34;
  const half = (dy) => Math.sqrt(R * R - dy * dy).toFixed(2);
  const band = (y, w, dash) => {
    const h = half(Math.abs(y - cy));
    return `<path d="M10 ${y}H${(cx - h).toFixed(2)}" stroke-width="${w}"${dash}/><path d="M296 ${y}H${(+cx + +h).toFixed(2)}" stroke-width="${w}"${dash}/>`;
  };
  let ring = '';
  for (let a = 0; a < 360; a += 15) {
    if (a > 155 && a < 205) continue;
    if (a > 335 || a < 25) continue;
    const r = (a * Math.PI) / 180;
    ring += `<circle cx="${(cx + 22 * Math.cos(r)).toFixed(2)}" cy="${(cy + 22 * Math.sin(r)).toFixed(2)}" r="2.1" fill="${C.purple}"/>`;
  }
  return `<svg viewBox="0 0 306 100" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="${L.vg[1].alt}">
  <rect x="0" y="0" width="306" height="88" fill="#e9e4d6"/>
  <g fill="none" stroke="${C.teal}" stroke-linecap="round">
    ${band(18, 4, ' stroke-dasharray="0.4 7"')}
    ${band(46, 6, '')}
    ${band(74, 4, ' stroke-dasharray="0.4 7"')}
  </g>
  ${ring}
  <circle cx="${cx}" cy="${cy}" r="8" fill="none" stroke="${C.coral}" stroke-width="1.6"/>
  <circle cx="${cx}" cy="${cy}" r="3.6" fill="${C.coral}"/>
  <text x="10" y="97" fill="${C.muted}" font-family="${F_SANS}" font-size="6">${L.vg[1].note1}</text>
  <text x="296" y="97" text-anchor="end" fill="${C.muted}" font-family="${F_SANS}" font-size="6">${L.vg[1].note2}</text>
</svg>`;
}

function vgCollateral(L) {
  let poster = '';
  for (let y = 48; y <= 62; y += 7) {
    poster += `<path d="M14 ${y}H92" stroke="${C.onDarkLine}" stroke-width="1.5" stroke-opacity="0.55" stroke-linecap="round"/>`;
  }
  return `<svg viewBox="0 0 306 100" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="${L.vg[2].alt}">
  <rect x="8" y="4" width="90" height="92" fill="${C.deep}"/>
  ${poster}
  ${miniMark(53, 26, 1.35, C.onDarkLine, C.paper, C.onDarkOrigin)}
  <text x="14" y="76" fill="${C.paper}" font-family="${F_SERIF}" font-size="12">${L.vg[2].poster}</text>
  <text x="14" y="85" fill="${C.onDarkEn}" font-family="${F_SANS}" font-size="5" letter-spacing="0.6" font-weight="700">HUNDRED-SENSE FORUM</text>
  <text x="14" y="92.5" fill="${C.onDarkEn}" font-family="${F_SERIF}" font-size="5.4">One city. Many ways to sense it.</text>
  <rect x="110" y="12" width="84" height="84" fill="${C.paper}" stroke="${C.deep}" stroke-width="1.2"/>
  ${miniMark(152, 26, 0.95, C.teal, C.deep, C.coral)}
  <path d="M118 38H186M118 45H186M118 52H166" stroke="${C.line}" stroke-width="1.6" stroke-linecap="round"/>
  <text x="118" y="66" fill="${C.deep}" font-family="${F_SANS}" font-size="6.4" font-weight="700">${L.vg[2].booklet}</text>
  <g fill="${C.purple}">${Array.from({ length: 14 }, (_, i) => `<circle cx="${119 + i * 4.6}" cy="74" r="1.4"/>`).join('')}</g>
  <rect x="118" y="82" width="40" height="7" rx="3.5" fill="${C.coral}"/>
  <text x="138" y="87.2" text-anchor="middle" fill="#fff" font-family="${F_SANS}" font-size="4.6" font-weight="700">${L.vg[2].stopTag}</text>
  <rect x="206" y="20" width="92" height="68" fill="#fff" stroke="${C.deep}" stroke-width="1.2"/>
  <rect x="206" y="20" width="92" height="5" fill="${C.teal}"/>
  <text x="214" y="42" fill="${C.deep}" font-family="${F_MONO}" font-size="12">OP-07</text>
  <text x="214" y="52" fill="${C.muted}" font-family="${F_SANS}" font-size="5.6">${L.vg[2].card}</text>
  <g fill="${C.deep}">${Array.from({ length: 16 }, (_, i) => `<circle cx="${215 + i * 4.6}" cy="62" r="1.3"/>`).join('')}</g>
  <rect x="214" y="70" width="52" height="7" rx="3.5" fill="${C.gold}"/>
  <text x="240" y="75.2" text-anchor="middle" fill="${C.deep}" font-family="${F_SANS}" font-size="4.6" font-weight="700">${L.vg[2].noAccount}</text>
</svg>`;
}

function vgInterface(L) {
  return `<svg viewBox="0 0 306 100" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="${L.vg[3].alt}">
  <rect x="6" y="6" width="164" height="88" rx="3" fill="#fff" stroke="${C.deep}" stroke-width="1.2"/>
  <rect x="14" y="14" width="46" height="12" rx="6" fill="${C.teal}"/>
  <text x="37" y="22.4" text-anchor="middle" fill="#fff" font-family="${F_SANS}" font-size="6.4" font-weight="700">AI ON</text>
  <text x="66" y="22.4" fill="${C.deep}" font-family="${F_MONO}" font-size="7">=</text>
  <rect x="76" y="14" width="50" height="12" rx="6" fill="${C.paper}" stroke="${C.deep}" stroke-width="1"/>
  <text x="101" y="22.4" text-anchor="middle" fill="${C.deep}" font-family="${F_SANS}" font-size="6.4" font-weight="700">AI OFF</text>
  <text x="132" y="22.4" fill="${C.muted}" font-family="${F_SANS}" font-size="5.4">${L.vg[3].equal}</text>
  <path d="M14 33H162" stroke="${C.line}" stroke-width="0.8"/>
  ${[0, 1, 2].map((i) => `<circle cx="19" cy="${44 + i * 13}" r="3.4" fill="${i === 0 ? C.teal : '#fff'}" stroke="${C.teal}" stroke-width="1.2"/><path d="M30 ${44 + i * 13}H${i === 2 ? 108 : 140}" stroke="${C.line}" stroke-width="2.6" stroke-linecap="round"/>`).join('')}
  <rect x="14" y="76" width="58" height="12" rx="2" fill="${C.coral}"/>
  <text x="43" y="84.4" text-anchor="middle" fill="#fff" font-family="${F_SANS}" font-size="6.4" font-weight="700">${L.vg[3].stop}</text>
  <rect x="82" y="76" width="80" height="12" rx="2" fill="#fff" stroke="${C.deep}" stroke-width="1"/>
  <text x="122" y="84.4" text-anchor="middle" fill="${C.deep}" font-family="${F_SANS}" font-size="6.2">${L.vg[3].human}</text>
  <rect x="184" y="2" width="52" height="96" rx="6" fill="#fff" stroke="${C.deep}" stroke-width="1.2"/>
  <rect x="190" y="10" width="40" height="9" rx="4.5" fill="${C.teal}"/>
  <text x="210" y="16.6" text-anchor="middle" fill="#fff" font-family="${F_SANS}" font-size="5" font-weight="700">AI ON</text>
  ${miniMark(210, 34, 0.85, C.teal, C.deep, C.coral)}
  <path d="M190 48H230M190 55H230M190 62H216" stroke="${C.line}" stroke-width="2" stroke-linecap="round"/>
  <rect x="190" y="72" width="40" height="10" rx="2" fill="${C.coral}"/>
  <text x="210" y="79.2" text-anchor="middle" fill="#fff" font-family="${F_SANS}" font-size="5.4" font-weight="700">${L.vg[3].stop}</text>
  <rect x="250" y="10" width="50" height="80" fill="${C.paper}" stroke="${C.deep}" stroke-width="1.2"/>
  <text x="256" y="24" fill="${C.deep}" font-family="${F_SANS}" font-size="6" font-weight="700">${L.vg[3].paper}</text>
  <path d="M256 32H294M256 39H294M256 46H280" stroke="${C.line}" stroke-width="1.8" stroke-linecap="round"/>
  <g fill="${C.purple}">${Array.from({ length: 9 }, (_, i) => `<circle cx="${257 + i * 4.6}" cy="56" r="1.4"/>`).join('')}</g>
  <text x="256" y="70" fill="${C.muted}" font-family="${F_SANS}" font-size="5.4">${L.vg[3].paperNote}</text>
  <rect x="256" y="76" width="38" height="8" rx="4" fill="${C.gold}"/>
  <text x="275" y="81.8" text-anchor="middle" fill="${C.deep}" font-family="${F_SANS}" font-size="4.8" font-weight="700">${L.vg[3].cash}</text>
</svg>`;
}

/* ---------- copy ---------- */
const ZH = {
  lang: 'zh-CN',
  kicker: 'EVERY SENSE JING-ZHANG / 万感京张',
  title: '品牌系统：把统一轨距译成通用设计',
  subtitle: 'PARALLEL SENSORY LINES + OPEN NODES · LOGO / PALETTE / TYPE / GRAMMAR · AI ON = AI OFF',
  a11yMark: '标志图形构成解析：平行感知线、开放节点与原点',
  s1: { n: '01', t: '标志与图形构成', e: 'IDENTITY AND MARK CONSTRUCTION' },
  onDark: '深底 / ON DARK #10383d',
  onPaper: '浅底 / ON PAPER #f2efe7',
  construction: '图形构成 / MARK CONSTRUCTION',
  cons: [
    ['平行感知线', '两条实线是连续主脊，承载视觉与听觉；两条点线是触觉铺装与低刺激替代线。四条通道并行，不分主次。'],
    ['开放节点', '环体左右留开口：服务可以进入，也可以退出。节点不闭合，不锁定任何一种身体或任何一种设备。'],
    ['原点', '中心一点是万感原点，也是人工求助、人工接管与停止权的落点，永远可见、永远可达。'],
  ],
  consFoot: '四条线的断口沿同一辅助圆排列。统一轨距使不同列车共享同一网络，通用设计使不同身体共享同一座城市。',
  s2: { n: '02', t: '色板与色彩语义', e: 'PALETTE AND COLOUR SEMANTICS' },
  colours: [
    { hex: '#10383d', cn: '深青', en: 'Deep Teal', use: '城市基底与公共底线；深色场景的底色与浅色场景的正文。', ratio: '11.0:1', tag: '正文可用' },
    { hex: '#177c78', cn: '水鸭青', en: 'Rail Teal', use: '连续主脊与 AI ON 路径；导视主色与章节标号。', ratio: '4.4:1', tag: '正文可用' },
    { hex: '#d76450', cn: '珊瑚', en: 'Coral', use: '停止权、急停、人工接管与求助；风险与失败提示。', ratio: '3.1:1', tag: '大字与图形' },
    { hex: '#6b5b95', cn: '紫', en: 'Node Purple', use: 'OP-01—OP-10 十个独立完成节点；触觉点阵与盲文层。', ratio: '5.1:1', tag: '正文可用' },
    { hex: '#d6a13b', cn: '金', en: 'Assumption Gold', use: '待验证假设与京张文化层；补数触发与遗产解释。', ratio: '2.0:1', tag: '仅图形' },
    { hex: '#f2efe7', cn: '米白', en: 'Paper', use: 'AI 关闭后的固定导视、纸质流程与无账户凭据。', ratio: '11.0:1', tag: '深底文字' },
  ],
  colourFoot: '对比度按 WCAG 2.1 在米白 #f2efe7 上复算，米白一栏为其在深青 #10383d 上的数值。深青、水鸭青与紫可用于正文；珊瑚仅用于 24px 以上粗体或图形；金仅作图形与色块；深色底上的文字只使用米白或浅青，不使用未提亮的主色。',
  s3: { n: '03', t: '字体策略', e: 'TYPE STRATEGY' },
  types: [
    { k: '标题 / 中黑', stack: 'Source Han Sans SC Medium · SIL OFL 1.1', sample: '万感京张 Every Sense', font: 'serif', use: '章节标题、三处地标命名与展陈大字。以中黑字重与放宽字距替代衬线字族。' },
    { k: '正文 / 粗黑', stack: 'Source Han Sans SC Bold · SIL OFL 1.1', sample: '一座城市，多种感知', font: 'sans', use: '正文、导视与易读文本。字面开阔，中英混排稳定，远距离可读。' },
    { k: '数据 / 表格数字', stack: 'Source Han Sans SC Regular · SIL OFL 1.1', sample: '11.41 km² OP-01', font: 'mono', use: '指标、节点编号与场景编码。以表格数字等宽对齐，替代等宽字族。' },
  ],
  typeFoot: '三种分工同出一族，以字重、字距与表格数字区分。四册图纸 PDF 经全册字体审计（2026-08-13）：仅嵌入该族三个子集，非 OFL 条目为零；本图版为栅格图，不分发字体程序。Georgia、Helvetica Neue、SF Mono 等商业字体是未来深化的候选方向，须逐项取得商用授权后方可引入。不使用企业商标或人物肖像。导视最小字号、行距与观看距离待现场审计确定。',
  s4: { n: '04', t: '视觉语法延展', e: 'GRAMMAR IN USE' },
  vg: [
    { t: '导视牌', e: 'WAYFINDING', d: '主牌承载图形与双语命名，低位牌提供触觉与盲文层，珊瑚求助柱始终在视线内。', alt: '导视牌延展示意：主牌、低位触觉牌与人工求助柱', sign: '共轨门', dir: '连续主脊 · 无台阶', aioff: 'AI OFF 可用', tactile: '触觉与盲文层', help: '人工求助柱' },
    { t: '触觉铺装', e: 'TACTILE PAVING', d: '平行感知线落地为铺装带，开放节点落地为可绕行的点阵圆，中心是求助柱基座。', alt: '触觉铺装延展示意：平行铺装带与点阵开放节点', note1: '点阵为警示层', note2: '中心为求助柱基座' },
    { t: '活动物料', e: 'EVENT COLLATERAL', d: '海报满版化平行线，手册保留停止提示，票证以等宽编号与触觉条支持无账户使用。', alt: '活动物料延展示意：海报、手册与无账户票证', poster: '百感台', booklet: '共创手册', stopTag: '可随时停止', card: '无账户票证', noAccount: '现金可用' },
    { t: '界面', e: 'INTERFACE', d: '双通道状态常显，停止按钮与转人工同级，纸质版是同一套语法的等价形态。', alt: '界面延展示意：AI 开关等价状态、停止按钮与纸质等价件', equal: '基本服务等价', stop: '停止', human: '转人工服务', paper: '纸质等价件', paperNote: '无需账户', cash: '现金可用' },
  ],
  bannerEn: 'One city. Many ways to sense it.',
  bannerCn: '一座城市，多种感知，共同行走',
  bannerTag: 'INTERNATIONAL LINE / 国际传播句',
  footL: '概念建议 · 临时边界 · 非法定规划 · 非工程线位',
  footR: 'PUBLIC / PROVISIONAL / CONCEPT',
};

const EN = {
  lang: 'en',
  kicker: 'EVERY SENSE JING-ZHANG / 万感京张',
  title: 'Brand system: common gauge translated into universal design',
  subtitle: 'PARALLEL SENSORY LINES + OPEN NODES · LOGO / PALETTE / TYPE / GRAMMAR · AI ON = AI OFF',
  a11yMark: 'Mark construction: parallel sensory lines, open node and origin',
  s1: { n: '01', t: 'Identity and mark construction', e: 'LOGO / TWO GROUNDS / GEOMETRY' },
  onDark: 'ON DARK #10383d',
  onPaper: 'ON PAPER #f2efe7',
  construction: 'MARK CONSTRUCTION',
  cons: [
    ['Parallel sensory lines', 'Two solid rails carry the continuous spine for sight and sound; two dotted lines carry tactile paving and the low-stimulus alternative. Four channels run in parallel, none subordinate.'],
    ['Open node', 'The ring keeps openings left and right: a service can be entered and can be left. The node never closes, and never locks in one kind of body or one kind of device.'],
    ['Origin', 'The centre point is Every Sense Origin — where human help, human takeover and the right to stop land. Always visible, always reachable.'],
  ],
  consFoot: 'All four gaps sit on one construction circle. A common gauge lets different trains share one network; universal design lets different bodies share one city.',
  s2: { n: '02', t: 'Palette and colour semantics', e: 'SIX COLOURS / CONTRAST RULES' },
  colours: [
    { hex: '#10383d', cn: 'Deep Teal', en: '深青', use: 'Urban base and the public baseline; dark ground, and body text on paper.', ratio: '11.0:1', tag: 'Body text' },
    { hex: '#177c78', cn: 'Rail Teal', en: '水鸭青', use: 'The continuous spine and the AI ON path; primary signage and section numbers.', ratio: '4.4:1', tag: 'Body text' },
    { hex: '#d76450', cn: 'Coral', en: '珊瑚', use: 'Right to stop, emergency stop, human takeover and help; risk and failure notices.', ratio: '3.1:1', tag: 'Large text only' },
    { hex: '#6b5b95', cn: 'Node Purple', en: '紫', use: 'The ten independent-completion nodes OP-01—OP-10; tactile dot grids and braille layers.', ratio: '5.1:1', tag: 'Body text' },
    { hex: '#d6a13b', cn: 'Assumption Gold', en: '金', use: 'Unverified assumptions and the Jing-Zhang cultural layer; refill triggers and heritage interpretation.', ratio: '2.0:1', tag: 'Graphics only' },
    { hex: '#f2efe7', cn: 'Paper', en: '米白', use: 'Fixed signage, paper procedures and no-account receipts once AI is off.', ratio: '11.0:1', tag: 'Text on dark' },
  ],
  colourFoot: 'Contrast recomputed under WCAG 2.1 against paper #f2efe7; the paper row is measured against deep teal #10383d. Deep teal, rail teal and node purple are cleared for body text; coral only above 24px bold or as graphics; gold as graphics and fills only. Text on dark ground uses paper or light teal, never the unlightened primary.',
  s3: { n: '03', t: 'Type strategy', e: 'ONE FAMILY / THREE WEIGHTS' },
  types: [
    { k: 'Display / Medium', stack: 'Source Han Sans SC Medium · SIL OFL 1.1', sample: '万感京张 Every Sense', font: 'serif', use: 'Section titles, landmark names and exhibition display. Medium weight with open tracking, in place of a serif family.' },
    { k: 'Text / Bold', stack: 'Source Han Sans SC Bold · SIL OFL 1.1', sample: 'One city, many senses', font: 'sans', use: 'Body copy, signage and easy-read text. Open apertures, stable CJK-Latin mixing, legible at distance.' },
    { k: 'Data / Tabular', stack: 'Source Han Sans SC Regular · SIL OFL 1.1', sample: '11.41 km² OP-01', font: 'mono', use: 'Metrics, node identifiers and scenario codes. Tabular figures align columns, in place of a mono family.' },
  ],
  typeFoot: 'Three roles, one family, separated by weight, tracking and tabular figures. Full-book audit of the four drawing PDFs (2026-08-13): zero non-OFL entries; this plate is raster and embeds no font. Georgia, Helvetica Neue and SF Mono stay candidates, to be cleared face by face for commercial use. No corporate marks or portraits. Signage minimum size, leading and viewing distance to be set on site.',
  s4: { n: '04', t: 'Grammar in use', e: 'SIGNAGE / PAVING / COLLATERAL / INTERFACE' },
  vg: [
    { t: 'Wayfinding', e: 'SIGNAGE', d: 'The main panel carries the mark and bilingual name, a low panel adds tactile and braille layers, and the coral help post stays in view.', alt: 'Wayfinding extension: main panel, low tactile panel and human help post', sign: '共轨门', dir: 'Step-free spine', aioff: 'WORKS AI OFF', tactile: 'Tactile + braille', help: 'Human help post' },
    { t: 'Tactile paving', e: 'GROUND', d: 'Parallel sensory lines become paving bands; the open node becomes a dot-grid circle that can be walked around, with the help post at its centre.', alt: 'Tactile paving extension: parallel bands and a dot-grid open node', note1: 'Dot grid is the warning layer', note2: 'Centre is the help post base' },
    { t: 'Event collateral', e: 'PRINT', d: 'Posters flood-fill the parallel lines, booklets keep the stop notice, and tickets stay usable without an account through mono codes and a tactile strip.', alt: 'Event collateral extension: poster, booklet and no-account ticket', poster: '百感台', booklet: 'Co-design booklet', stopTag: 'STOP ANY TIME', card: 'No-account ticket', noAccount: 'CASH ACCEPTED' },
    { t: 'Interface', e: 'SCREEN', d: 'Both channel states stay visible, stop ranks equal to human handover, and the paper version is the same grammar in an equivalent form.', alt: 'Interface extension: AI on/off equivalence, stop control and paper equivalent', equal: 'equivalent', stop: 'STOP', human: 'Talk to a person', paper: 'Paper equivalent', paperNote: 'No account needed', cash: 'CASH OK' },
  ],
  bannerEn: 'One city. Many ways to sense it.',
  bannerCn: '一座城市，多种感知，共同行走',
  bannerTag: 'INTERNATIONAL LINE / 国际传播句',
  footL: 'Concept proposal · provisional boundaries · not statutory planning · not engineering alignments',
  footR: 'PUBLIC / PROVISIONAL / CONCEPT',
};

/* ---------- page ---------- */
function page(L) {
  const swatches = L.colours.map((c) => `
    <div class="sw">
      <div class="chip" style="background:${c.hex};${c.hex === '#f2efe7' ? 'box-shadow:inset 0 0 0 1.5px #d3ccbb' : ''}"></div>
      <div class="swb">
        <div class="swn">${c.cn}<em>${c.en}</em></div>
        <div class="swh"><code>${c.hex}</code><span class="rt">${c.ratio}<i>${c.tag}</i></span></div>
        <p>${c.use}</p>
      </div>
    </div>`).join('');

  const types = L.types.map((t, i) => `
    <div class="card" style="border-top-color:${[C.deep, C.teal, C.purple][i]}">
      <div class="ck">${t.k}</div>
      <div class="cs">${t.stack}</div>
      <div class="sample ${t.font}">${t.sample}</div>
      <p>${t.use}</p>
    </div>`).join('');

  const vgs = [vgWayfinding(L), vgPaving(L), vgCollateral(L), vgInterface(L)];
  const grammar = L.vg.map((v, i) => `
    <div class="card vg" style="border-top-color:${[C.teal, C.purple, C.gold, C.coral][i]}">
      <div class="vgart">${vgs[i]}</div>
      <div class="ck">${v.t}<em>${v.e}</em></div>
      <p>${v.d}</p>
    </div>`).join('');

  const cons = L.cons.map((c, i) => `
    <li><span class="num" style="background:${[C.teal, C.deep, C.coral][i]}">${i + 1}</span><b>${c[0]}</b>${c[1]}</li>`).join('');

  return `<!doctype html><html lang="${L.lang}"><head><meta charset="utf-8"><title>${L.title}</title><style>
*{box-sizing:border-box;margin:0;padding:0}
html,body{width:2400px;height:1500px;overflow:hidden}
body{background:${C.paper};color:${C.deep};font-family:${F_SANS};-webkit-font-smoothing:antialiased;text-rendering:geometricPrecision}
.page{width:2400px;height:1500px;display:flex;flex-direction:column}
.topbar{height:16px;background:${C.deep};flex:none}
.body{flex:1;padding:40px 76px 34px;display:flex;flex-direction:column}
.head{flex:none;height:138px;border-bottom:1px solid ${C.line};display:flex;flex-direction:column;justify-content:flex-start}
.kicker{font-size:16px;font-weight:800;letter-spacing:1.8px;color:${C.teal}}
h1{font-size:52px;font-weight:700;line-height:1.14;letter-spacing:-.6px;margin-top:10px}
.sub{margin-top:11px;font-size:14px;font-weight:700;letter-spacing:1.5px;color:${C.muted}}
.sections{flex:1;display:flex;flex-direction:column;gap:26px;padding-top:18px}
section{display:flex;flex-direction:column;gap:12px;min-height:0}
.s1{flex:0 0 310px}.s2{flex:0 0 232px}.s3{flex:0 0 214px}.s4{flex:0 0 294px}
.sh{flex:none;height:22px;display:flex;align-items:baseline;gap:12px}
.sh b{font-size:17px;font-weight:800;color:${C.teal}}
.sh em{font-style:normal;font-size:12px;font-weight:700;letter-spacing:1.4px;color:${C.muted}}
.row{flex:1;display:flex;gap:20px;min-height:0}
.card{background:#fff;border:1px solid ${C.edge};border-top:4px solid ${C.teal};padding:16px 20px 18px;display:flex;flex-direction:column;min-width:0}
.ck{font-size:14px;font-weight:800;letter-spacing:.6px}
.ck em{font-style:normal;font-weight:700;font-size:10.5px;letter-spacing:1.3px;color:${C.muted};margin-left:8px}
.cs{margin-top:5px;font-size:11.5px;font-weight:600;letter-spacing:.4px;color:${C.teal};font-family:${F_MONO}}
.card p{margin-top:auto;font-size:12.5px;line-height:1.5;color:${C.muted}}
/* 01 */
.lg{flex:0 0 684px;justify-content:space-between}
.lg.dark{background:${C.deep};border-color:${C.deep};border-top-color:${C.paper}}
.lg.dark .ck{color:${C.paper}}
.lg .lgwrap{display:flex;align-items:center;justify-content:center;flex:1}
.lg svg{width:596px;height:186px;display:block}
.cons{flex:1;min-width:0}
.cons ol{list-style:none;margin-top:10px;display:flex;flex-direction:column;gap:7px}
.cons li{position:relative;padding-left:32px;font-size:12.2px;line-height:1.4;color:${C.muted}}
.cons li b{color:${C.deep};font-weight:800;margin-right:6px}
.num{position:absolute;left:0;top:1px;width:20px;height:20px;border-radius:50%;color:#fff;font-family:${F_SERIF};font-size:12px;display:flex;align-items:center;justify-content:center}
.consfoot{margin-top:auto;padding-top:8px;border-top:1px solid ${C.edge};font-size:11.5px;line-height:1.45;color:${C.muted}}
.consart{flex:0 0 300px;display:flex;align-items:center;justify-content:center}
.consart svg{width:300px;height:224px}
/* 02 */
.sw{flex:1;background:#fff;border:1px solid ${C.edge};display:flex;flex-direction:column;min-width:0}
.chip{height:66px;flex:none}
.swb{padding:12px 16px 14px;display:flex;flex-direction:column;flex:1}
.swn{font-size:18px;font-weight:800}
.swn em{font-style:normal;font-size:11px;font-weight:700;letter-spacing:1px;color:${C.muted};margin-left:8px}
.swh{margin-top:5px;display:flex;align-items:center;justify-content:space-between;gap:8px}
.swh code{font-family:${F_MONO};font-size:13px;font-weight:600;color:${C.deep};letter-spacing:.3px}
.rt{font-family:${F_MONO};font-size:11px;font-weight:700;color:${C.teal};text-align:right;line-height:1.25}
.rt i{display:block;font-style:normal;font-family:${F_SANS};font-size:9.5px;font-weight:700;letter-spacing:.6px;color:${C.muted}}
.swb p{margin-top:auto;padding-top:7px;font-size:11.5px;line-height:1.42;color:${C.muted}}
.note{flex:none;font-size:11.5px;line-height:1.4;color:${C.muted};padding-top:2px}
.note b{color:${C.deep};font-weight:800}
/* 03 */
.sample{margin-top:10px;font-size:26px;line-height:1.24;color:${C.deep};padding-bottom:8px;border-bottom:1px solid ${C.edge};font-family:${F_SHS}}
.sample.serif{font-weight:500;letter-spacing:2.4px}
.sample.sans{font-weight:700;letter-spacing:0}
.sample.mono{font-weight:400;font-size:24px;letter-spacing:1.2px;font-variant-numeric:tabular-nums}
.s3 .cs{font-family:${F_SHS};font-weight:700}
/* The three type cards used to size to their own content, which left the row
   short of the section width; with one family named three times the copy is
   shorter still, so the row is shared equally the way section 02 already does. */
.s3 .card{flex:1}
.s3 .card p{padding-top:8px}
/* 04 */
.vg{padding:14px 16px 16px}
.vgart{flex:none;height:163px;background:${C.paper};display:flex;align-items:center;justify-content:center;margin-bottom:10px}
.vgart svg{width:100%;height:100%;display:block}
.vg .ck{font-size:13.5px}
.vg p{margin-top:6px;font-size:11.5px;line-height:1.42}
/* banner + footer */
.banner{flex:none;height:58px;margin-top:16px;background:${C.deep};display:flex;align-items:center;padding:0 26px;gap:24px}
.banner .en{font-family:${F_SERIF};font-size:30px;color:${C.paper};letter-spacing:.2px}
.banner .cn{font-size:19px;font-weight:700;color:${C.onDarkEn};letter-spacing:2px}
.banner .tag{margin-left:auto;font-size:11px;font-weight:700;letter-spacing:1.6px;color:#7ba49f}
.foot{flex:none;height:52px;display:flex;align-items:flex-end;justify-content:space-between;padding-bottom:2px;font-size:12px;font-weight:700;letter-spacing:.8px}
.foot .l{color:${C.muted}}
.foot .r{color:${C.teal};letter-spacing:1.6px}
</style></head><body><div class="page">
<div class="topbar"></div>
<div class="body">
  <header class="head">
    <div class="kicker">${L.kicker}</div>
    <h1>${L.title}</h1>
    <div class="sub">${L.subtitle}</div>
  </header>
  <div class="sections">

    <section class="s1">
      <div class="sh"><b>${L.s1.n} / ${L.s1.t}</b><em>${L.s1.e}</em></div>
      <div class="row">
        <div class="card lg dark"><div class="ck">${L.onDark}</div><div class="lgwrap">${logoDark}</div></div>
        <div class="card lg" style="background:${C.paper}"><div class="ck">${L.onPaper}</div><div class="lgwrap">${logoLight}</div></div>
        <div class="card cons" style="border-top-color:${C.coral}">
          <div style="display:flex;gap:20px;flex:1;min-height:0">
            <div style="flex:1;min-width:0;display:flex;flex-direction:column">
              <div class="ck">${L.construction}</div>
              <ol>${cons}</ol>
              <div class="consfoot">${L.consFoot}</div>
            </div>
            <div class="consart">${markDiagram(L)}</div>
          </div>
        </div>
      </div>
    </section>

    <section class="s2">
      <div class="sh"><b>${L.s2.n} / ${L.s2.t}</b><em>${L.s2.e}</em></div>
      <div class="row">${swatches}</div>
      <div class="note">${L.colourFoot}</div>
    </section>

    <section class="s3">
      <div class="sh"><b>${L.s3.n} / ${L.s3.t}</b><em>${L.s3.e}</em></div>
      <div class="row">${types}</div>
      <div class="note">${L.typeFoot}</div>
    </section>

    <section class="s4">
      <div class="sh"><b>${L.s4.n} / ${L.s4.t}</b><em>${L.s4.e}</em></div>
      <div class="row">${grammar}</div>
    </section>

  </div>
  <div class="banner">
    <span class="en">${L.bannerEn}</span>
    <span class="cn">${L.bannerCn}</span>
    <span class="tag">${L.bannerTag}</span>
  </div>
  <div class="foot"><span class="l">${L.footL}</span><span class="r">${L.footR}</span></div>
</div>
</div></body></html>`;
}

const out = __dirname;
fs.writeFileSync(path.join(out, 'brand-system.html'), page(ZH));
fs.writeFileSync(path.join(out, 'brand-system.en.html'), page(EN));
console.log('built 2 html');
