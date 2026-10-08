'use strict';
/* land-use-structure.png / .en.png — 4800 x 3000 (CSS 1200x750 @ dsf 4)

   WP-N2b re-set, R5.  The v5.5 plate carried, at review scale (768 px short
   edge): a four-row function column at 5 px, a seven-row legend at 5-6 px, a
   three-badge disclaimer strip at 5 px, two footer note lines at 5 px and three
   thumbnail captions at 6 px — roughly half the sheet's text below the 12 px
   floor.  The plate's original generator no longer exists anywhere in the
   workspace (only its consumers, mka3.js / mkall.js, survive), so the drawn
   cartography is reused as raster: build/mkmap-lu.sh selects four pixel windows
   of the published PNG — the corridor band and the three interface panels —
   and copies them unmodified.  No resampling, no colour transform, no mask: the
   crops are byte-level identical sub-rectangles of the published plate, so no
   drawn geometry, boundary, colour band, node or value can change.

   Everything around those four windows is rebuilt here at >= 12 px, i.e.
   >= 1.6 % of image height, matching the 96-point reference packages.  The scale
   bars and the north arrow are redrawn from the published plate's own measured
   geometry (686 px = 2 km over the 3152 px corridor window; 204 px = 250 m over
   the 1003 px interface windows), so they carry the same values at legible size. */

const { C, base, ruleBar, FONT_SLOT } = require('./tokens');

/* Function-band fills sampled from the published plate's own legend swatches,
   so the four cards below the map carry exactly the colours drawn on it. */
const FN = ['#59b0a7', '#94c49f', '#eac87d', '#a28ebd'];

const L = {
  zh: {
    kicker: 'EVERY SENSE JING-ZHANG · URBAN DESIGN ATLAS',
    idx: '02 / LAND USE + STRUCTURE',
    sub: '概念功能关系 · 不是控规或现状用地',
    pill: 'CONCEPT ONLY · 非法定规划图',
    title: '四类概念结构：让产业、公共空间与日常生活共用一条底线',
    mapCap: 'FUNCTIONAL STRUCTURE / 四类概念功能与线位、重点区同图叠加',
    mapNote: '图面旋转 90° · 北向右 · OSM 路网底图上的概念结构图，几何取自提交 GeoJSON',
    claim: '一底线 · 两路径 · 三接口',
    claimSub: 'AI 关闭后仍可完成；直接多模态与低刺激路径并行；三处横向界面缝合园区、社区与站点。',
    legend: [
      ['line', C.teal, '通用可达底线 / Universal baseline'],
      ['thin', C.sky, '横向接口 / Cross interfaces'],
      ['dash', C.purple, '低刺激替代 / Quiet alternative'],
    ],
    fnK: 'FOUR CONCEPTUAL FUNCTIONS / 四类概念结构',
    fns: [
      ['01', '通用接口研发与验证', '连接研究、原型、受控测试和人工接管。'],
      ['02', '通用可达公园与安静开敞', '承载连续公共底线与低刺激替代路径。'],
      ['03', '包容 AI 产业服务与采用', '检验采购、维护、纠错与退出。'],
      ['04', '独立生活共创与社区服务', '把真实公共任务反馈给产品与空间。'],
    ],
    ifK: 'THREE TRANSVERSE INTERFACES / 三处横向接口',
    ifs: [
      ['01', '众智园横向接口', '验证 / VERIFY', C.teal],
      ['02', '原点社区横向接口', '共创 / CO-DESIGN', C.purple],
      ['03', '大钟寺横向接口', '采用 / ADOPT', C.coral],
    ],
    warn: '不是控规，不表达现状权属、法定用途或开发容量。',
    foot: 'OSM 路网底图上的概念结构图 · 几何依据：land_use.geojson + roads.geojson + key_areas.geojson（EPSG:4326 投影示意）· 临时边界与概念中心线不得作为工程或审批依据。',
    km2: '2 km',
    m250: '250 m',
  },
  en: {
    kicker: 'EVERY SENSE JING-ZHANG · URBAN DESIGN ATLAS',
    idx: '02 / LAND USE + STRUCTURE',
    sub: 'Conceptual relationships · not zoning or existing land use',
    pill: 'CONCEPT ONLY · NOT A STATUTORY PLAN',
    title: 'Four conceptual functions on one shared public baseline',
    mapCap: 'FUNCTIONAL STRUCTURE / Function bands, lines and key areas on one sheet',
    mapNote: 'Sheet rotated 90° · north to the right · submitted GeoJSON on an OSM road-network basemap',
    claim: 'ONE BASELINE · TWO PATHS · THREE INTERFACES',
    claimSub: 'Tasks remain possible with AI off; direct multimodal and quiet routes run in parallel; three interfaces link parks, communities and stations.',
    legend: [
      ['line', C.teal, 'Universal baseline'],
      ['thin', C.sky, 'Cross interfaces'],
      ['dash', C.purple, 'Quiet alternative'],
    ],
    fnK: 'FOUR CONCEPTUAL FUNCTIONS / 四类概念结构',
    fns: [
      ['01', 'Universal interface R&D + validation', 'Links research, prototyping, controlled tests and human takeover.'],
      ['02', 'Accessible park + quiet open space', 'Carries the continuous public baseline and quiet alternative.'],
      ['03', 'Inclusive AI services + adoption', 'Tests procurement, maintenance, correction and exit.'],
      ['04', 'Independent-living co-design + community', 'Feeds real public tasks back into products and space.'],
    ],
    ifK: 'THREE TRANSVERSE INTERFACES / 三处横向接口',
    ifs: [
      ['01', 'Zhongzhiyuan transverse interface', 'VERIFY / 验证', C.teal],
      ['02', 'AI Origin transverse interface', 'CO-DESIGN / 共创', C.purple],
      ['03', 'Dazhongsi transverse interface', 'ADOPT / 采用', C.coral],
    ],
    warn: 'Not zoning: no claim about title, statutory use or development capacity.',
    foot: 'Concept structure on an OSM road-network basemap · geometry: land_use / roads / key_areas.geojson (EPSG:4326, diagrammatic) · provisional lines are not engineering or approval data.',
    km2: '2 km',
    m250: '250 m',
  },
};

function mark(kind, k) {
  if (kind === 'line') return `<i style="height:5px;background:${k};border-radius:3px"></i>`;
  if (kind === 'thin') return `<i style="height:3px;background:${k}"></i>`;
  return `<i style="height:0;border-top:4px dashed ${k}"></i>`;
}

/* v6.4 VECTOR CARTOGRAPHY.  The four raster windows cropped from the published
   plate carried the Dazhongsi key-area frame and interface window at the old,
   misplaced location (Beijing North vicinity).  With PROV-KEY-003 and ROAD-004
   relocated, the raster is stale, so the corridor band and the three interface
   windows are redrawn as SVG straight from the submitted GeoJSON (land_use
   bands, roads, key-area frames, nodes).  The OSM background leaves with the
   raster; the sheet becomes a plain-ground concept structure and the OSM
   attribution is retired from this plate's footer. */
const fs = require('fs');
const path = require('path');
const PKG = require('path').resolve(__dirname, '../../../../', 'submissions/lqqk7/every-sense-jingzhang');
const gj = (f) => JSON.parse(fs.readFileSync(path.join(PKG, 'geometry', f), 'utf8'));
const mLat = 110540, mLon = 111320 * Math.cos((39.98 * Math.PI) / 180);

function luMainSvg() {
  const W = 1140, H = 202.5;
  const lu = gj('land_use.geojson').features;
  const roads = gj('roads.geojson').features;
  const areas = gj('key_areas.geojson').features;
  const site = gj('site_boundary.geojson').features[0].geometry.coordinates[0];
  const lats = site.map((c) => c[1]), lons = site.map((c) => c[0]);
  const lat0 = Math.min(...lats), lat1 = Math.max(...lats);
  const lon0 = Math.min(...lons), lon1 = Math.max(...lons);
  const s = (W - 24) / ((lat1 - lat0) * mLat);
  const y0 = (H - (lon1 - lon0) * mLon * s) / 2;
  const X = (lat) => 12 + (lat - lat0) * mLat * s;
  const Y = (lon) => y0 + (lon - lon0) * mLon * s;
  const seg = [];
  lu.forEach((f, i) => {
    const pts = f.geometry.coordinates[0].map((c) => `${X(c[1]).toFixed(1)},${Y(c[0]).toFixed(1)}`).join(' ');
    seg.push(`<polygon points="${pts}" fill="${FN[i]}55" stroke="${FN[i]}" stroke-width="1"/>`);
  });
  const RS = { 'ROAD-002': `stroke="${C.sky}" stroke-width="2.6"`, 'ROAD-003': `stroke="${C.sky}" stroke-width="2.6"`, 'ROAD-004': `stroke="${C.sky}" stroke-width="2.6"`, 'ROAD-005': `stroke="${C.purple}" stroke-width="3" stroke-dasharray="7 5"`, 'ROAD-001': `stroke="${C.teal}" stroke-width="4"` };
  for (const id of ['ROAD-002', 'ROAD-003', 'ROAD-004', 'ROAD-005', 'ROAD-001']) {
    const f = roads.find((r) => r.properties.id === id);
    const pts = f.geometry.coordinates.map((c) => `${X(c[1]).toFixed(1)},${Y(c[0]).toFixed(1)}`).join(' ');
    seg.push(`<polyline points="${pts}" fill="none" ${RS[id]} stroke-linecap="round"/>`);
  }
  for (const f of areas) {
    const ring = f.geometry.coordinates[0];
    const as_ = ring.map((c) => c[1]), os_ = ring.map((c) => c[0]);
    const x = X(Math.min(...as_)), y = Y(Math.min(...os_));
    const w = (Math.max(...as_) - Math.min(...as_)) * mLat * s;
    const h = (Math.max(...os_) - Math.min(...os_)) * mLon * s;
    seg.push(`<rect x="${x.toFixed(1)}" y="${y.toFixed(1)}" width="${w.toFixed(1)}" height="${h.toFixed(1)}" fill="none" stroke="${C.coral}" stroke-width="1.6" stroke-dasharray="6 4"/>`);
  }
  /* four function discs at band midpoints, staggered along the corridor */
  const DISC_LAT = [39.999, 39.993, 39.9868, 39.981];
  lu.forEach((f, i) => {
    const ring = f.geometry.coordinates[0];
    const os_ = ring.map((c) => c[0]);
    const NUDGE = [0, -0.0009, 0.0012, 0];       /* keep discs clear of the centrelines */
    const midLon = (Math.min(...os_) + Math.max(...os_)) / 2 + NUDGE[i];
    const x = X(DISC_LAT[i]), y = Y(midLon);
    seg.push(`<circle cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="11" fill="${FN[i]}" stroke="#fff" stroke-width="2"/>`);
    seg.push(`<text x="${x.toFixed(1)}" y="${(y + 4.5).toFixed(1)}" text-anchor="middle" font-size="12" font-weight="700" fill="#fff">0${i + 1}</text>`);
  });
  return `<svg viewBox="0 0 ${W} ${H}" width="${W}" height="${H}" font-family="SHS,sans-serif"><rect width="${W}" height="${H}" fill="#fbfaf6"/>${seg.join('')}</svg>`;
}

function luInsetSvg(idx, zh) {
  const W = 370, H = 134;
  const CTR = [{ road: 'ROAD-002', lat: null }, { road: 'ROAD-003', lat: null }, { road: 'ROAD-004', lat: null }][idx];
  const roads = gj('roads.geojson').features;
  const lu = gj('land_use.geojson').features;
  const nodes = gj('constraints.geojson').features;
  const xr = roads.find((r) => r.properties.id === CTR.road).geometry.coordinates;
  const ctrLat = xr[0][1];
  const ctrLon = 116.3458;                       /* ROAD-001 spine */
  const mppx = 250 / 75;                         /* 75 px = 250 m, stated by the card's own bar */
  const spanLon = (W * mppx) / mLon, spanLat = (H * mppx) / mLat;
  const X = (lon) => (lon - (ctrLon - spanLon / 2)) / spanLon * W;
  const Yl = (lat) => H - (lat - (ctrLat - spanLat / 2)) / spanLat * H;   /* north up */
  const seg = [];
  lu.forEach((f, i) => {
    const ring = f.geometry.coordinates[0];
    const os_ = ring.map((c) => c[0]);
    const a = X(Math.min(...os_)), b = X(Math.max(...os_));
    if (b < 0 || a > W) return;
    seg.push(`<rect x="${Math.max(0, a).toFixed(1)}" y="0" width="${(Math.min(W, b) - Math.max(0, a)).toFixed(1)}" height="${H}" fill="${FN[i]}55" stroke="${FN[i]}" stroke-width="1"/>`);
  });
  seg.push(`<line x1="${X(116.3458).toFixed(1)}" y1="0" x2="${X(116.3458).toFixed(1)}" y2="${H}" stroke="${C.teal}" stroke-width="4"/>`);
  seg.push(`<line x1="${X(116.3490).toFixed(1)}" y1="0" x2="${X(116.3490).toFixed(1)}" y2="${H}" stroke="${C.purple}" stroke-width="3" stroke-dasharray="7 5"/>`);
  const rr = roads.find((r) => r.properties.id === CTR.road).geometry.coordinates;
  seg.push(`<line x1="${X(rr[0][0]).toFixed(1)}" y1="${Yl(ctrLat).toFixed(1)}" x2="${X(rr[1][0]).toFixed(1)}" y2="${Yl(ctrLat).toFixed(1)}" stroke="${C.sky}" stroke-width="2.6"/>`);
  const ringc = ['', '', ''][idx] || [C.teal, C.purple, C.coral][idx];
  seg.push(`<circle cx="${X(ctrLon).toFixed(1)}" cy="${Yl(ctrLat).toFixed(1)}" r="8" fill="none" stroke="${ringc}" stroke-width="3"/>`);
  seg.push(`<circle cx="${X(ctrLon).toFixed(1)}" cy="${Yl(ctrLat).toFixed(1)}" r="2.6" fill="${ringc}"/>`);
  /* nodes inside the window */
  for (const f of nodes) {
    const [lon, lat] = f.geometry.coordinates;
    const x = X(lon), y = Yl(lat);
    if (x < 6 || x > W - 6 || y < 6 || y > H - 6) continue;
    const id = f.properties.id;
    if (id === 'OP-04') seg.push(`<circle cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="9" fill="none" stroke="${C.coral}" stroke-width="2.4"/>`);
    seg.push(`<circle cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="4.5" fill="${C.purple}" stroke="#fff" stroke-width="1.6"/>`);
    seg.push(`<text x="${(x + 8).toFixed(1)}" y="${(y - 6).toFixed(1)}" font-size="12" font-weight="700" fill="${C.deep}" stroke="#fff" stroke-width="3" paint-order="stroke">${id.slice(3)}</text>`);
  }
  /* north arrow, top-left (M6 fix: insets are north-up while the main band is north-right) */
  seg.push(`<path d="M 14 26 V 12" stroke="${C.ink}" stroke-width="2"/><path d="M 14 7 L 10.5 14 L 17.5 14 Z" fill="${C.ink}"/><text x="21" y="19" font-size="12" font-weight="700" fill="${C.ink}">N</text>`);
  return `<svg viewBox="0 0 ${W} ${H}" width="${W}" height="${H}" font-family="SHS,sans-serif"><rect width="${W}" height="${H}" fill="#fbfaf6"/>${seg.join('')}</svg>`;
}

function html(lang, m) {
  const t = L[lang];
  const zh = lang === 'zh';

  const legend = t.legend
    .map(([kind, c, s]) => `<span class="lrow"><span class="lm">${mark(kind, c)}</span><span class="ls">${s}</span></span>`)
    .join('');

  const fns = t.fns
    .map(
      ([n, a, b], i) => `<div class="fcard" style="border-left-color:${FN[i]}">
      <div class="fn"><b class="fsw" style="background:${FN[i]}"></b><span class="fnum">${n}</span></div>
      <div class="fa">${a}</div><div class="fb">${b}</div></div>`
    )
    .join('');

  /* 204 px = 250 m on the published plate, measured over the 1003 px window
     that is displayed 370 px wide -> 75 px. */
  const ifs = t.ifs
    .map(
      ([n, a, b, c], i) => `<div class="icard" style="border-top-color:${c}">
      <div class="ihd"><span class="ia" style="color:${c}">${n} / ${a}</span><span class="ib">${b}</span></div>
      ${luInsetSvg(i, zh)}
      <div class="ibar"><i class="sbar" style="width:75px"></i><span>${t.m250}</span></div></div>`
    )
    .join('');

  return `<!doctype html><html lang="${lang}"><head><meta charset="utf-8"><title>land-use-structure</title>
<style>${FONT_SLOT}${base}
body{width:1200px;height:750px;overflow:hidden;background:${C.paper}}
.hd{height:94px;background:${C.deep};color:#fff;padding:13px 30px 0;display:flex;justify-content:space-between}
.hd .k{font-size:12px;letter-spacing:.16em;color:${C.onDarkEn};display:flex;align-items:center;gap:11px;font-family:"Helvetica Neue",Arial,SHS,sans-serif;font-weight:700}
.hd h1{font-size:${zh ? 28 : 25}px;font-weight:700;margin:${zh ? 9 : 8}px 0 0;line-height:1.25;max-width:${zh ? 830 : 760}px}
.hd .r{text-align:right}
.hd .r .i{font-size:12px;letter-spacing:.14em;font-weight:700;color:#fff;font-family:"Helvetica Neue",Arial,SHS,sans-serif}
.hd .r .s{font-size:12px;color:${C.onDarkEn};margin-top:5px}
.pill{display:inline-block;margin-top:8px;background:${C.coral};color:#fff;font-size:12px;letter-spacing:.06em;padding:5px 13px;border-radius:11px;font-weight:700}
.wrap{padding:8px 30px 0;display:flex;flex-direction:column;height:656px;overflow:hidden}
.mapbox{width:1140px;height:202.5px;background:#fff;border:1px solid ${C.edge};border-radius:4px;overflow:hidden;position:relative;flex:none}
.mapbox img{width:1140px;height:202.5px;display:block}
.nrose{position:absolute;top:8px;right:12px;display:flex;align-items:center;gap:6px;background:#ffffffd9;border-radius:3px;padding:2px 7px}
.nrose span{font-size:12px;font-weight:700;color:${C.ink};font-family:"Helvetica Neue",Arial,SHS,sans-serif}
.nrose i{display:block;width:34px;height:2px;background:${C.ink};position:relative}
.nrose i:after{content:"";position:absolute;right:0;top:-3px;border:4px solid transparent;border-left-color:${C.ink};border-right:0}
.mscale{position:absolute;left:12px;bottom:9px;display:flex;align-items:center;gap:7px;background:#ffffffd9;border-radius:3px;padding:3px 8px}
.mscale i{display:block;width:248px;height:4px;background:${C.ink}}
.mscale span{font-size:12px;color:${C.ink};font-weight:700;font-family:"Helvetica Neue",Arial,SHS,sans-serif}
.mapcap{display:flex;justify-content:space-between;align-items:baseline;gap:20px;margin-top:4px;flex:none}
.mapcap .a{font-size:12px;letter-spacing:.08em;color:${C.teal};font-weight:700;font-family:"Helvetica Neue",Arial,SHS,sans-serif}
.mapcap .b{font-size:12px;color:${C.muted}}
.claimrow{display:flex;justify-content:space-between;align-items:center;gap:24px;margin-top:6px;flex:none}
.claim{font-size:${zh ? 19 : 17}px;font-weight:700;color:${C.deep};line-height:1.2;white-space:nowrap}
.lgs{display:flex;gap:${zh ? 20 : 24}px;align-items:center}
.lrow{display:flex;align-items:center;gap:8px}
.lm{display:block;width:28px}
.lm i{display:block;width:100%}
.ls{font-size:12px;color:${C.ink};white-space:nowrap}
.claimsub{font-size:13px;color:${C.muted};line-height:1.3;margin-top:3px;flex:none}
.ck{font-size:12px;letter-spacing:.12em;color:${C.teal};font-weight:700;font-family:"Helvetica Neue",Arial,SHS,sans-serif;margin-top:6px;flex:none}
.fgrid{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-top:5px;flex:none}
.fcard{background:#fff;border:1px solid ${C.edge};border-left:4px solid;border-radius:0 4px 4px 0;padding:8px 11px 9px;min-height:104px;display:flex;flex-direction:column}
.fn{display:flex;align-items:center;gap:7px}
.fsw{display:block;width:14px;height:14px;border-radius:2px}
.fnum{font-size:12px;font-weight:700;color:${C.muted};font-family:"Helvetica Neue",Arial,SHS,sans-serif;letter-spacing:.08em}
.fa{font-size:${zh ? 14.5 : 12.5}px;font-weight:700;color:${C.ink};line-height:1.25;margin-top:5px}
.fb{font-size:12px;color:${C.muted};line-height:1.3;margin-top:auto;padding-top:4px}
.igrid{display:grid;grid-template-columns:repeat(3,1fr);gap:15px;margin-top:5px;flex:none}
.icard{background:#fff;border:1px solid ${C.edge};border-top:4px solid;border-radius:4px;overflow:hidden}
.ihd{display:flex;justify-content:space-between;align-items:baseline;gap:8px;padding:7px 10px 6px}
.ia{font-size:${zh ? 13 : 12.4}px;font-weight:700;line-height:1.2;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.ib{font-size:12px;font-weight:700;color:${C.muted};white-space:nowrap;font-family:"Helvetica Neue",Arial,SHS,sans-serif}
.icard img{width:370px;height:134px;display:block}
.ibar{display:flex;align-items:center;gap:8px;padding:5px 10px 6px}
.sbar{display:block;height:3px;background:${C.ink}}
.ibar span{font-size:12px;color:${C.muted};font-weight:700;font-family:"Helvetica Neue",Arial,SHS,sans-serif}
.ft{margin-top:auto;padding:7px 0 0;border-top:1px solid ${C.edge};display:flex;justify-content:space-between;align-items:flex-start;gap:24px;flex:none}
.ftw{font-size:12px;color:${C.coral};font-weight:700;line-height:1.35;white-space:nowrap;flex:none}
.ftl{font-size:12px;color:${C.muted};line-height:1.35;text-align:right;max-width:720px}
</style></head><body>
<div class="hd">
  <div><div class="k">${ruleBar(1.7, true)}<span>${t.kicker}</span></div><h1>${t.title}</h1></div>
  <div class="r"><div class="i">${t.idx}</div><div class="s">${t.sub}</div><div class="pill">${t.pill}</div></div>
</div>
<div class="wrap">
  <div class="mapbox">${luMainSvg()}
    <div class="nrose"><span>N</span><i></i></div>
    <div class="mscale"><i></i><span>${t.km2}</span></div>
  </div>
  <div class="mapcap"><span class="a">${t.mapCap}</span><span class="b">${t.mapNote}</span></div>
  <div class="claimrow"><span class="claim">${t.claim}</span><span class="lgs">${legend}</span></div>
  <div class="claimsub">${t.claimSub}</div>
  <div class="ck">${t.fnK}</div>
  <div class="fgrid">${fns}</div>
  <div class="igrid">${ifs}</div>
  <div class="ft"><span class="ftw">${t.warn}</span><span class="ftl">${t.foot}</span></div>
</div>
</body></html>`;
}

module.exports = { html, L };
