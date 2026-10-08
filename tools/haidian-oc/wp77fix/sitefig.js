'use strict';
/* site-overview.png / .en.png — 4800 x 3000 (CSS 1200x750 @ dsf 4)

   WP-N2b re-set.  The v5.4 plate carried, at review scale (768 px short edge):
   a 15-row legend at 5-6 px, three key-area thumbnails duplicating the
   standalone key-areas plate, a ten-node strip at 5 px, latitude/longitude
   ticks, and OSM street labels competing with the proposal's own overlay.
   The plate's original generator no longer exists anywhere in the workspace
   (only its consumers, mka3.js / mkall.js, survive), so the drawn map is reused
   as raster: build/mkmap.sh crops the corridor band out of the published PNG and
   fades the low-saturation OSM background while leaving every saturated overlay
   mark — baseline, quiet alternative, node markers, key-area frames — untouched.
   No geometry, boundary, label or value inside the map is redrawn or moved.

   Everything around the map is rebuilt here at >= 12 px, i.e. >= 1.6 % of image
   height, matching the 96-point reference packages. */

/* WP-R10 wingcard re-fit.  Measured on the rendered plate, inside the 1140x264
   mapbox (band raster 3154x730 mapped 1:1 onto it):
     raster "02 AI ORIGIN COMMUNITY - CO-DESIGN" tag  ends at CSS x 831
     leader dashes                                    CSS x 834-956
     leader arrowhead                                 CSS x 956-998
     key-area frame (coral)                           ends at CSS y 173
     cut-off raster wing label                        CSS x 978-1141, y 193-216
   The 330 px card reached to CSS x 810 and stood 70 px tall, so it covered the
   tag's last three glyphs and the whole leader.  At 270 px it starts at CSS
   x 869 and stands 78 px tall (top CSS y 177): the tag clears by 38 px, the
   frame by 4 px, the dashes stay visible, and the arrowhead the card still
   swallows is restated as a CSS head on the card's own left edge, so the leader
   reads dash-head-card.  The label it exists to hide stays fully covered.
   Kept out of the emitted CSS on purpose: fontFaceFor() subsets the font from
   the literal html string, so a comment inside <style> would move the subset. */

const { C, base, ruleBar, FONT_SLOT } = require('./tokens');

/* v6.4 VECTOR MAP.  The raster band reused since WP-N2b carried two defects the
   package can no longer live with: the ten node discs were laid out by NUMBER
   PARITY at even spacing (real positions cluster 3+3+4 inside the key areas;
   worst offset ~8 km), and the Dazhongsi key-area frame sat at Beijing North
   Station, 2.4 km from its namesake.  With the PROV-KEY-003 relocation the
   raster is unfixable, so the corridor band is redrawn as SVG straight from the
   submitted GeoJSON: every line, frame and disc below is projected from
   geometry/*.geojson at build time (equirectangular, north-right, uniform
   scale).  The OSM background goes away with the raster — the band is now a
   plain-ground concept structure diagram, and the OSM attribution moves out of
   the footer (land-use keeps its own).  Node discs are brand purple (palette:
   purple = the ten completion nodes); OP-04 carries a coral breakpoint ring
   tied to the detail plate / dual-state / audible-break anchors. */
const fs = require('fs');
const path = require('path');
const PKG = require('path').resolve(__dirname, '../../../', 'submissions/lqqk7/every-sense-jingzhang');
const gj = (f) => JSON.parse(fs.readFileSync(path.join(PKG, 'geometry', f), 'utf8'));

function corridorSvg(lang) {
  const zh = lang === 'zh';
  const W = 1140, H = 264;
  const site = gj('site_boundary.geojson').features[0].geometry.coordinates[0];
  const areas = gj('key_areas.geojson').features;
  const roads = gj('roads.geojson').features;
  const nodes = gj('constraints.geojson').features;
  const lats = site.map((c) => c[1]), lons = site.map((c) => c[0]);
  const lat0 = Math.min(...lats), lat1 = Math.max(...lats);
  const lon0 = Math.min(...lons), lon1 = Math.max(...lons);
  const mLat = 110540, mLon = 111320 * Math.cos((39.98 * Math.PI) / 180);
  const spanX = (lat1 - lat0) * mLat, spanY = (lon1 - lon0) * mLon;
  const s = (W - 44) / spanX;                       /* uniform metres/px */
  const y0 = (H - spanY * s) / 2;
  const X = (lat) => 22 + (lat - lat0) * mLat * s;
  const Y = (lon) => y0 + (lon - lon0) * mLon * s;  /* east points down */
  const seg = [];
  /* site boundary */
  seg.push(`<rect x="${X(lat0).toFixed(1)}" y="${Y(lon0).toFixed(1)}" width="${(spanX * s).toFixed(1)}" height="${(spanY * s).toFixed(1)}" fill="#ffffff" stroke="${C.edge}" stroke-width="1.4"/>`);
  /* key-area frames */
  const AC = { 'PROV-KEY-001': C.teal, 'PROV-KEY-002': C.purple, 'PROV-KEY-003': C.coral };
  for (const f of areas) {
    const ring = f.geometry.coordinates[0];
    const as_ = ring.map((c) => c[1]), os_ = ring.map((c) => c[0]);
    const x = X(Math.min(...as_)), y = Y(Math.min(...os_));
    const w = (Math.max(...as_) - Math.min(...as_)) * mLat * s;
    const h = (Math.max(...os_) - Math.min(...os_)) * mLon * s;
    seg.push(`<rect x="${x.toFixed(1)}" y="${y.toFixed(1)}" width="${w.toFixed(1)}" height="${h.toFixed(1)}" fill="${C.coral}0d" stroke="${C.coral}" stroke-width="1.6" stroke-dasharray="6 4"/>`);
    f._cx = x + w / 2; f._cy = y; f._col = AC[f.properties.id] || C.coral;
  }
  /* roads: cross interfaces first, then quiet, then baseline on top */
  const RSTYLE = {
    'ROAD-002': `stroke="#4AA3C4" stroke-width="3"`,
    'ROAD-003': `stroke="#4AA3C4" stroke-width="3"`,
    'ROAD-004': `stroke="#4AA3C4" stroke-width="3"`,
    'ROAD-005': `stroke="${C.purple}" stroke-width="4" stroke-dasharray="8 6"`,
    'ROAD-001': `stroke="${C.teal}" stroke-width="5"`,
  };
  for (const id of ['ROAD-002', 'ROAD-003', 'ROAD-004', 'ROAD-005', 'ROAD-001']) {
    const f = roads.find((r) => r.properties.id === id);
    const pts = f.geometry.coordinates.map((c) => `${X(c[1]).toFixed(1)},${Y(c[0]).toFixed(1)}`).join(' ');
    seg.push(`<polyline points="${pts}" fill="none" ${RSTYLE[id]} stroke-linecap="round"/>`);
  }
  /* place labels (real coordinates, muted, >=12px) */
  const PLACES = [
    [39.9435, null, zh ? '北京北 · 西直门' : 'Beijing North · Xizhimen', 'start'],
    [39.9668, null, zh ? '大钟寺' : 'Dazhongsi', 'mid'],
    [39.9755, null, zh ? '知春路' : 'Zhichunlu', 'mid'],
    [39.9865, null, zh ? '学院桥' : 'Xueyuan Bridge', 'mid'],
    [40.0035, null, zh ? '清华东路' : 'Qinghua East Rd', 'mid'],
    [40.0245, null, zh ? '北五环' : '5th Ring Rd', 'end'],
  ];
  for (const [lat, , name, anch] of PLACES) {
    const x = X(lat);
    const ta = anch === 'end' ? 'end' : anch === 'start' ? 'start' : 'middle';
    const tx = anch === 'end' ? Math.min(x + 8, W - 6) : anch === 'start' ? Math.max(x - 8, 6) : x;
    seg.push(`<text x="${tx.toFixed(1)}" y="${(Y(lon1) + 16).toFixed(1)}" text-anchor="${ta}" font-size="12" fill="${C.muted}">${name}</text>`);
  }
  /* two wings (diagrammatic arrows, kept from the published narrative) */
  const wingY = Y(lon0) - 6;
  seg.push(`<path d="M ${X(39.955).toFixed(1)} ${(wingY - 14).toFixed(1)} C ${X(39.966).toFixed(1)} ${(wingY - 30).toFixed(1)} ${X(39.984).toFixed(1)} ${(wingY - 30).toFixed(1)} ${X(39.996).toFixed(1)} ${(wingY - 16).toFixed(1)}" fill="none" stroke="${C.teal}" stroke-width="2" stroke-dasharray="5 4" marker-end="url(#ah)"/>`);
  seg.push(`<text x="${X(39.9755).toFixed(1)}" y="${(wingY - 36).toFixed(1)}" text-anchor="middle" font-size="12" font-weight="700" fill="${C.teal}">${zh ? '中关村科技服务翼 · 技术/人才/资本（关系示意）' : 'ZHONGGUANCUN SERVICE WING · DIAGRAMMATIC'}</text>`);
  const wing2Y = Y(lon1) + 30;
  seg.push(`<text x="${X(40.008).toFixed(1)}" y="${(wing2Y + 12).toFixed(1)}" text-anchor="middle" font-size="12" font-weight="700" fill="${C.teal}">${zh ? '小月河场景赋能翼 · 开放场景/真实反馈（关系示意）' : 'XIAOYUEHE SCENARIO WING · DIAGRAMMATIC'}</text>`);
  /* nodes: true positions, brand purple, labels offset alternately */
  const sorted = nodes.slice().sort((a, b) => a.properties.id.localeCompare(b.properties.id));
  sorted.forEach((f, i) => {
    const [lon, lat] = f.geometry.coordinates;
    const x = X(lat), y = Y(lon);
    const id = f.properties.id.slice(3);
    const isBk = f.properties.id === 'OP-04';
    if (isBk) seg.push(`<circle cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="12" fill="none" stroke="${C.coral}" stroke-width="3"/>`);
    seg.push(`<circle cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="6.5" fill="${C.purple}" stroke="#fff" stroke-width="2"/>`);
    const SIDE = { 'OP-08': true, 'OP-09': true, 'OP-03': true };
    const above = f.properties.id in SIDE ? SIDE[f.properties.id] : i % 2 === 0;
    const ly = above ? y - (isBk ? 18 : 12) : y + (isBk ? 27 : 21);
    seg.push(`<text x="${x.toFixed(1)}" y="${ly.toFixed(1)}" text-anchor="middle" font-size="12" font-weight="700" fill="${isBk ? C.coral : C.deep}" stroke="#fff" stroke-width="3" paint-order="stroke">${id}</text>`);
  });
  /* key-area pins */
  const PIN = { 'PROV-KEY-001': ['01', zh ? '众智园 · 验证' : 'Zhongzhiyuan · VERIFY'], 'PROV-KEY-002': ['02', zh ? 'AI 原点社区 · 共创' : 'AI Origin · CO-DESIGN'], 'PROV-KEY-003': ['03', zh ? '大钟寺 · 采用' : 'Dazhongsi · ADOPT'] };
  for (const f of areas) {
    const [num, name] = PIN[f.properties.id];
    const px = f._cx, py = Y(lon0) - 6;
    seg.push(`<line x1="${px.toFixed(1)}" y1="${(py + 4).toFixed(1)}" x2="${px.toFixed(1)}" y2="${f._cy.toFixed(1)}" stroke="${f._col}" stroke-width="1.6"/>`);
    seg.push(`<circle cx="${px.toFixed(1)}" cy="${py.toFixed(1)}" r="10" fill="${f._col}"/>`);
    seg.push(`<text x="${px.toFixed(1)}" y="${(py + 4).toFixed(1)}" text-anchor="middle" font-size="12" font-weight="700" fill="#fff">${num}</text>`);
    const flip = px > W - 250;
    seg.push(`<text x="${(flip ? px - 15 : px + 15).toFixed(1)}" y="${(py + 4).toFixed(1)}" text-anchor="${flip ? 'end' : 'start'}" font-size="12" font-weight="700" fill="${C.deep}" stroke="#fff" stroke-width="3" paint-order="stroke">${name}</text>`);
  }
  /* scale bar + north arrow */
  const kmPx = 1000 * s;
  const sbX = 34, sbY = H - 40;
  seg.push(`<line x1="${sbX.toFixed(1)}" y1="${sbY}" x2="${(sbX + 2 * kmPx).toFixed(1)}" y2="${sbY}" stroke="${C.deep}" stroke-width="2.4"/>`);
  [0, 1, 2].forEach((k) => {
    const x = sbX + k * kmPx;
    seg.push(`<line x1="${x.toFixed(1)}" y1="${sbY - 4}" x2="${x.toFixed(1)}" y2="${sbY + 4}" stroke="${C.deep}" stroke-width="2"/>`);
    seg.push(`<text x="${x.toFixed(1)}" y="${sbY - 8}" text-anchor="middle" font-size="12" fill="${C.deep}">${k}${k === 2 ? ' km' : ''}</text>`);
  });
  seg.push(`<path d="M 20 22 H 44" stroke="${C.deep}" stroke-width="2.4"/><path d="M 52 22 L 42 17 L 42 27 Z" fill="${C.deep}"/><text x="58" y="27" font-size="12" font-weight="700" fill="${C.deep}">N</text>`);
  return `<svg viewBox="0 0 ${W} ${H}" width="${W}" height="${H}" font-family="SHS,sans-serif">
<defs><marker id="ah" markerWidth="8" markerHeight="8" refX="6" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 Z" fill="${C.teal}"/></marker></defs>
<rect width="${W}" height="${H}" fill="#fbfaf6"/>
${seg.join('\n')}
</svg>`;
}

const L = {
  zh: {
    kicker: 'EVERY SENSE JING-ZHANG · URBAN DESIGN ATLAS',
    idx: '01 / SITE OVERVIEW',
    pill: 'CONCEPT ONLY · 非法定规划图',
    title: '万感京张：同一座城市，多种感知，共同完成',
    mapCap: 'CORRIDOR OVERVIEW / 京张走廊总体结构（图面旋转 90°，北向右）',
    mapSrc: '素底概念结构图 · 全部线位、框线与节点由提交 GeoJSON 现算落位',
    logicK: 'MASTERPLAN LOGIC / 总体结构',
    logic: ['一条公共底线', '三座实验院 · 两翼支持网'],
    logicSub: '让 AI 开启或关闭时，公共任务都能被独立完成。',
    scopes: [
      ['43.6 km²', '统筹研究 / Regional research', '公告约值 · 无可用空间边界', 'teal'],
      ['11.41 km²*', '总体设计 / Overall design', '提交 GeoJSON 临时复算', 'sky'],
      ['3 / 368.4 ha', '重点区 / Key areas', '公告约值 · 临时框线', 'coral'],
    ],
    legendK: 'LEGEND / 图例',
    legend: [
      ['line', 'teal', '通用可达底线 / Universal baseline'],
      ['dash', 'purple', '低刺激替代路径 / Quiet alternative'],
      ['thin', '#4AA3C4', '横向接口 / Cross interface'],
      ['dot', 'purple', '独立完成节点 / Task point'],
      ['ring', 'coral', '断点节点 OP-04 / Breakpoint node'],
      ['box', 'coral', '重点区范围 / Key area'],
    ],
    nodesK: '十个独立完成点 / 10 COMPLETION POINTS',
    nodes: [
      ['01', '多模态寻路', 'Multimodal wayfinding', 'purple'],
      ['02', '低刺激路线', 'Quiet route', 'purple'],
      ['03', '同屏服务', 'Multi-channel service', 'purple'],
      ['04', '连续通行', 'Continuous access', 'purple'],
      ['05', '机器人礼让', 'Predictable robot', 'purple'],
      ['06', '易读办事', 'Easy-read process', 'purple'],
      ['07', '遗产解说', 'Multisensory heritage', 'purple'],
      ['08', '等价零售', 'Equivalent retail', 'purple'],
      ['09', '活动负荷', 'Sensory load', 'purple'],
      ['10', 'AI 关闭求助', 'AI-off assistance', 'purple'],
    ],
    nodeNote: '位置为概念测试点，不是批准设施。',
    foot: '素底概念结构图，几何取自提交 GeoJSON（EPSG:4326）· 不用于修订、验证或替代任何规划边界',
    footR: 'WGS84 / EPSG:4326 · 概念结构图',
  },
  en: {
    kicker: 'EVERY SENSE JING-ZHANG · URBAN DESIGN ATLAS',
    idx: '01 / SITE OVERVIEW',
    pill: 'CONCEPT ONLY · NOT A STATUTORY PLAN',
    title: 'Every Sense Jing-Zhang: one city, many ways to sense it, completed together',
    mapCap: 'CORRIDOR OVERVIEW / Jing-Zhang corridor structure (sheet rotated 90°, north to the right)',
    mapSrc: 'Plain-ground concept structure; every line, frame and node placed from the submitted GeoJSON',
    logicK: 'MASTERPLAN LOGIC / Overall structure',
    logic: ['One shared public baseline', 'Three labs · two support wings'],
    logicSub: 'Public tasks stay independently completable, AI on or off.',
    scopes: [
      ['43.6 km²', 'REGIONAL RESEARCH', 'Announced approximate value · no usable polygon', 'teal'],
      ['11.41 km²*', 'OVERALL DESIGN', 'Provisional calculation from submitted GeoJSON', 'sky'],
      ['3 / 368.4 ha', 'KEY AREAS', 'Announced approximate value · provisional boxes', 'coral'],
    ],
    legendK: 'LEGEND',
    legend: [
      ['line', 'teal', 'Universal baseline'],
      ['dash', 'purple', 'Quiet alternative'],
      ['thin', '#4AA3C4', 'Cross interface'],
      ['dot', 'purple', 'Task point'],
      ['ring', 'coral', 'Breakpoint node OP-04'],
      ['box', 'coral', 'Key area'],
    ],
    nodesK: '10 INDEPENDENT COMPLETION POINTS',
    nodes: [
      ['01', 'Multimodal wayfinding', '多模态寻路', 'purple'],
      ['02', 'Quiet route', '低刺激路线', 'purple'],
      ['03', 'Multi-channel service', '同屏服务', 'purple'],
      ['04', 'Continuous access', '连续通行', 'purple'],
      ['05', 'Predictable robot', '机器人礼让', 'purple'],
      ['06', 'Easy-read process', '易读办事', 'purple'],
      ['07', 'Multisensory heritage', '遗产解说', 'purple'],
      ['08', 'Equivalent retail', '等价零售', 'purple'],
      ['09', 'Sensory load', '活动负荷', 'purple'],
      ['10', 'AI-off assistance', 'AI 关闭求助', 'purple'],
    ],
    nodeNote: 'Node positions are conceptual test points, not approved facilities.',
    foot: 'Plain-ground concept structure from the submitted GeoJSON (EPSG:4326) · not for revising, validating or replacing any planning boundary',
    footR: 'WGS84 / EPSG:4326 · conceptual structure',
  },
};

const col = (k) => ({ teal: C.teal, purple: C.purple, coral: C.coral, sky: C.sky, deep: C.deep, muted: C.muted }[k] || k);

function mark(kind, c) {
  const k = col(c);
  if (kind === 'line') return `<i style="height:5px;background:${k};border-radius:3px"></i>`;
  if (kind === 'thin') return `<i style="height:2px;background:${k}"></i>`;
  if (kind === 'dash') return `<i style="height:0;border-top:4px dashed ${k}"></i>`;
  if (kind === 'dot') return `<i style="height:15px;background:transparent;display:flex;align-items:center;justify-content:center"><b style="width:15px;height:15px;border-radius:50%;background:${k};display:block"></b></i>`;
  if (kind === 'ring') return `<i style="height:15px;background:transparent;display:flex;align-items:center;justify-content:center"><b style="width:13px;height:13px;border-radius:50%;border:3px solid ${k};display:block"></b></i>`;
  if (kind === 'box') return `<i style="height:15px;border:2px dashed ${k};background:${k}14;border-radius:2px"></i>`;
  return `<i style="height:15px;background:#dcd8cc;border:1px solid ${C.edge};border-radius:2px"></i>`;
}

function html(lang, mapUrl) {
  const t = L[lang];
  const zh = lang === 'zh';

  const scopes = t.scopes
    .map(
      ([v, lab, note, c]) => `<div class="srow" style="border-left-color:${col(c)}">
      <div class="sv num">${v}</div>
      <div class="sl">${lab}</div>
      <div class="sn">${note}</div></div>`
    )
    .join('');

  const legend = t.legend
    .map(([kind, c, s]) => `<div class="lrow"><span class="lm">${mark(kind, c)}</span><span class="ls">${s}</span></div>`)
    .join('');

  const nodes = t.nodes
    .map(
      ([n, a, b, c]) => `<div class="nrow"><b class="nn" style="background:${col(c)}">${n}</b>
      <span class="na">${a}</span><span class="nb">${b}</span></div>`
    )
    .join('');

  return `<!doctype html><html lang="${lang}"><head><meta charset="utf-8"><title>site-overview</title>
<style>${FONT_SLOT}${base}
body{width:1200px;height:750px;overflow:hidden;background:${C.paper}}
.hd{height:94px;background:${C.deep};color:#fff;padding:15px 30px 0;display:flex;justify-content:space-between}
.hd .k{font-size:12px;letter-spacing:.16em;color:${C.onDarkEn};display:flex;align-items:center;gap:11px;font-family:"Helvetica Neue",Arial,SHS,sans-serif;font-weight:700}
.hd h1{font-size:${zh ? 30 : 21}px;font-weight:700;margin:${zh ? 9 : 8}px 0 0;line-height:1.25;max-width:${zh ? 840 : 830}px}
.hd .r{text-align:right}
.hd .r .i{font-size:12px;letter-spacing:.14em;font-weight:700;color:#fff;font-family:"Helvetica Neue",Arial,SHS,sans-serif}
.pill{display:inline-block;margin-top:12px;background:${C.coral};color:#fff;font-size:12px;letter-spacing:.06em;padding:6px 13px;border-radius:11px;font-weight:700}
.wrap{padding:8px 30px 0;display:flex;flex-direction:column;height:656px;overflow:hidden}
.mapbox{width:1140px;height:264px;background:#fff;border:1px solid ${C.edge};border-radius:4px;overflow:hidden;position:relative;flex:none}
.mapbox img{width:1140px;height:264px;display:block}
.wingcard{position:absolute;right:0;bottom:8px;width:270px;background:#f9f7f0;border:1px solid ${C.edge};border-right:none;border-radius:4px 0 0 4px;padding:7px 13px 7px 12px;box-sizing:border-box}
.wingcard::before{content:"";position:absolute;left:-16px;top:13px;width:0;height:0;border-top:8px solid transparent;border-bottom:8px solid transparent;border-left:16px solid ${C.teal}}
.wingcard .wa{font-size:13px;font-weight:700;color:${C.teal};line-height:1.15;font-family:"Helvetica Neue",Arial,SHS,sans-serif;letter-spacing:.02em}
.wingcard .wb{font-size:12px;color:${C.muted};line-height:1.25;margin-top:2px}
.mapcap{display:flex;justify-content:space-between;align-items:baseline;gap:20px;margin-top:5px;flex:none}
.mapcap .a{font-size:12px;letter-spacing:.08em;color:${C.teal};font-weight:700;font-family:"Helvetica Neue",Arial,SHS,sans-serif}
.mapcap .b{font-size:12px;color:${C.muted}}
.body{display:grid;grid-template-columns:390px 288px 1fr;gap:16px;margin-top:8px;flex:1;min-height:0}
.ck{font-size:12px;letter-spacing:.14em;color:${C.teal};font-weight:700;font-family:"Helvetica Neue",Arial,SHS,sans-serif}
.lg1{font-size:${zh ? 27 : 22}px;font-weight:700;color:${C.deep};line-height:1.25;margin-top:7px}
.lg2{font-size:${zh ? 20 : 17}px;font-weight:700;color:${C.ink};line-height:1.25;margin-top:2px}
.lgs{font-size:13.5px;color:${C.muted};line-height:1.4;margin-top:7px}
.srow{border-left:3px solid;padding:0 0 0 10px;margin-top:8px}
.sv{font-size:25px;font-weight:600;color:${C.deep};line-height:1.05}
.sl{font-size:13px;font-weight:700;margin-top:3px;color:${C.ink}}
.sn{font-size:12px;color:${C.muted};margin-top:2px}
.panel{background:#fff;border:1px solid ${C.edge};border-radius:4px;padding:11px 13px;overflow:hidden}
.lrow{display:grid;grid-template-columns:36px 1fr;gap:10px;align-items:center;padding:10px 0 0}
.lm{display:flex;align-items:center;height:15px}
.lm i{display:block;width:100%}
.ls{font-size:${zh ? 12.6 : 13}px;color:${C.ink};line-height:1.25}
.ngrid{display:grid;grid-template-columns:1fr 1fr;gap:9px 14px;margin-top:10px}
.nrow{display:grid;grid-template-columns:24px 1fr;grid-template-rows:auto auto;column-gap:7px;align-items:center;padding:3px 0 0}
.nn{grid-row:1/3;width:25px;height:25px;border-radius:50%;color:#fff;font-size:12.2px;font-weight:700;display:flex;align-items:center;justify-content:center;font-family:"Helvetica Neue",Arial,SHS,sans-serif}
.na{font-size:${zh ? 13.5 : 13}px;font-weight:700;color:${C.ink};line-height:1.15;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.nb{font-size:12px;color:${C.muted};line-height:1.15;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.nnote{font-size:12px;color:${C.coral};font-weight:700;margin-top:8px}
.ft{margin-top:auto;padding:6px 0 0;border-top:1px solid ${C.edge};display:flex;justify-content:space-between;gap:18px;font-size:12px;color:${C.muted}}
</style></head><body>
<div class="hd">
  <div><div class="k">${ruleBar(1.7, true)}<span>${t.kicker}</span></div><h1>${t.title}</h1></div>
  <div class="r"><div class="i">${t.idx}</div><div class="pill">${t.pill}</div></div>
</div>
<div class="wrap">
  <div class="mapbox">${corridorSvg(lang)}</div>
  <div class="mapcap"><span class="a">${t.mapCap}</span><span class="b">${t.mapSrc}</span></div>
  <div class="body">
    <div>
      <div class="ck">${t.logicK}</div>
      <div class="lg1">${t.logic[0]}</div>
      <div class="lg2">${t.logic[1]}</div>
      <div class="lgs">${t.logicSub}</div>
      ${scopes}
    </div>
    <div class="panel">
      <div class="ck">${t.legendK}</div>
      ${legend}
    </div>
    <div class="panel">
      <div class="ck">${t.nodesK}</div>
      <div class="ngrid">${nodes}</div>
      <div class="nnote">${t.nodeNote}</div>
    </div>
  </div>
  <div class="ft"><span>${t.foot}</span><span>${t.footR}</span></div>
</div>
</body></html>`;
}

module.exports = { html, L };
