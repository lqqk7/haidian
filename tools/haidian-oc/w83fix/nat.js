'use strict';
/* 量测 .mapcap 两个 flex 项的单行自然宽度（不换行时所需宽度）。 */
const { chromium } = require('playwright-core');
const path = require('path');
const CANDS = [
  'Concept structure on an OSM road-network basemap; every line, frame and node placed from the submitted GeoJSON',
  'Plain-ground concept structure; every line, frame and node placed from the submitted GeoJSON',
  'Concept structure on an OSM road-network basemap; lines, frames and nodes from the submitted GeoJSON',
  'Concept structure on an OSM road-network basemap; every mark placed from the submitted GeoJSON',
  'Concept structure on an OSM road-network basemap; all geometry from the submitted GeoJSON',
  'On an OSM road-network basemap; every line, frame and node from the submitted GeoJSON',
  'Concept structure on an OSM road-network basemap; geometry from the submitted GeoJSON',
  'Concept structure on an OSM basemap; every line, frame and node from the submitted GeoJSON',
];
(async () => {
  const b = await chromium.launch();
  const ctx = await b.newContext({ viewport: { width: 1200, height: 750 }, deviceScaleFactor: 1 });
  for (const f of process.argv.slice(2)) {
    const p = await ctx.newPage();
    await p.goto('file://' + path.resolve(f), { waitUntil: 'load' });
    await p.evaluate(() => document.fonts.ready);
    await p.waitForTimeout(300);
    const r = await p.evaluate((CANDS) => {
      const meas = (proto, txt) => {
        const s = document.createElement('span');
        s.style.cssText = 'position:absolute;visibility:hidden;white-space:pre;left:-9999px';
        const cs = getComputedStyle(proto);
        for (const k of ['fontFamily', 'fontSize', 'fontWeight', 'letterSpacing', 'fontStyle'])
          s.style[k] = cs[k];
        s.textContent = txt;
        document.body.appendChild(s);
        const w = s.getBoundingClientRect().width;
        s.remove();
        return +w.toFixed(1);
      };
      const A = document.querySelector('.mapcap .a'), B = document.querySelector('.mapcap .b');
      const gap = parseFloat(getComputedStyle(document.querySelector('.mapcap')).gap) || 0;
      const box = document.querySelector('.mapcap').clientWidth;
      const aNat = meas(A, A.textContent);
      const out = { box, gap, aNat, bNatCurrent: meas(B, B.textContent), budget: +(box - gap - aNat).toFixed(1), cands: [] };
      for (const c of CANDS) out.cands.push([meas(B, c), +(box - gap - aNat - meas(B, c)).toFixed(1), c.length, c.slice(0, 70)]);
      return out;
    }, CANDS);
    console.log('### ' + f);
    console.log(JSON.stringify(r, null, 1));
    await p.close();
  }
  await b.close();
})();
