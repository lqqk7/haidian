'use strict';
const { chromium } = require('playwright-core');
const path = require('path');
const A = [
 'CORRIDOR OVERVIEW / Jing-Zhang corridor structure (sheet rotated 90°, north to the right)',
 'CORRIDOR OVERVIEW (sheet rotated 90°, north to the right)',
 'CORRIDOR OVERVIEW / Jing-Zhang structure (sheet rotated 90°, north to the right)',
 'CORRIDOR OVERVIEW / Jing-Zhang corridor (rotated 90°, north to the right)',
 'CORRIDOR OVERVIEW / Jing-Zhang corridor structure (rotated 90°, north right)',
 'CORRIDOR OVERVIEW / sheet rotated 90°, north to the right',
 'CORRIDOR OVERVIEW / Jing-Zhang corridor (sheet rotated 90°)',
];
const B = [
 'Concept structure on an OSM road-network basemap; every line, frame and node placed from the submitted GeoJSON',
 'Concept structure on an OSM road-network basemap; every line, frame and node from the submitted GeoJSON',
 'Concept structure on an OSM road-network basemap; lines, frames and nodes from the submitted GeoJSON',
];
(async () => {
  const b = await chromium.launch();
  const ctx = await b.newContext({ viewport: { width: 1200, height: 750 }, deviceScaleFactor: 1 });
  const p = await ctx.newPage();
  await p.goto('file://' + path.resolve(process.argv[2]), { waitUntil: 'load' });
  await p.evaluate(() => document.fonts.ready);
  await p.waitForTimeout(300);
  const r = await p.evaluate(([A, B]) => {
    const meas = (sel, txt) => {
      const proto = document.querySelector(sel);
      const s = document.createElement('span');
      s.style.cssText = 'position:absolute;visibility:hidden;white-space:pre;left:-9999px';
      const cs = getComputedStyle(proto);
      for (const k of ['fontFamily','fontSize','fontWeight','letterSpacing','fontStyle']) s.style[k]=cs[k];
      s.textContent = txt; document.body.appendChild(s);
      const w = s.getBoundingClientRect().width; s.remove(); return +w.toFixed(1);
    };
    return { a: A.map(t=>[meas('.mapcap .a',t), t]), b: B.map(t=>[meas('.mapcap .b',t), t]) };
  }, [A, B]);
  console.log('BOX 1140  GAP 20  -> aNat+bNat must be <= 1120');
  for (const [w,t] of r.a) console.log('A %s  %s', String(w).padStart(6), t);
  for (const [w,t] of r.b) console.log('B %s  %s', String(w).padStart(6), t);
  await b.close();
})();
