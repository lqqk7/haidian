'use strict';
/* 候选文案宽度试算：在真实页面里替换 .mapcap .b，报告 mapcap 高度、
   .body 网格高与左栏所需高，判定是否回到单行且无溢出。 */
const { chromium } = require('playwright-core');
const path = require('path');
const CANDS = [
  null,
  'Concept structure on an OSM road-network basemap; lines, frames and nodes from the submitted GeoJSON',
  'Concept structure on an OSM road-network basemap; every mark placed from the submitted GeoJSON',
  'Concept structure on an OSM road-network basemap; geometry from the submitted GeoJSON',
  'OSM road-network basemap; every line, frame and node placed from the submitted GeoJSON',
  'Concept structure on an OSM road-network basemap; all geometry from the submitted GeoJSON',
];
(async () => {
  const b = await chromium.launch();
  const ctx = await b.newContext({ viewport: { width: 1200, height: 750 }, deviceScaleFactor: 1 });
  const p = await ctx.newPage();
  await p.goto('file://' + path.resolve(process.argv[2]), { waitUntil: 'load' });
  await p.evaluate(() => document.fonts.ready);
  await p.waitForTimeout(300);
  const rows = await p.evaluate((CANDS) => {
    const out = [];
    const el = document.querySelector('.mapcap .b');
    const a = document.querySelector('.mapcap .a');
    const orig = el.textContent;
    for (const c of CANDS) {
      if (c !== null) el.textContent = c;
      const mc = document.querySelector('.mapcap').getBoundingClientRect();
      const grid = document.querySelector('.body').getBoundingClientRect();
      const col = document.querySelector('.body > div');
      const ft = document.querySelector('.ft').getBoundingClientRect();
      const lastSn = [...document.querySelectorAll('.sn')].pop().getBoundingClientRect();
      out.push({
        text: (c === null ? '[BEFORE] ' : '') + (c || orig).slice(0, 58),
        aW: +a.getBoundingClientRect().width.toFixed(1),
        bW: +el.getBoundingClientRect().width.toFixed(1),
        mcH: +mc.height.toFixed(1),
        gridTop: +grid.y.toFixed(1), gridH: +grid.height.toFixed(1),
        colNeed: +col.getBoundingClientRect().height.toFixed(1),
        slack: +(grid.height - col.getBoundingClientRect().height).toFixed(1),
        snBottom: +(lastSn.y + lastSn.height).toFixed(1), ftTop: +ft.y.toFixed(1),
        bodyScroll: [document.body.scrollWidth, document.body.scrollHeight],
      });
      el.textContent = orig;
    }
    return out;
  }, CANDS);
  for (const r of rows) console.log(JSON.stringify(r));
  await b.close();
})();
