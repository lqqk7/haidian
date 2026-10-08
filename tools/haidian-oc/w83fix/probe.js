'use strict';
/* 量测 site-overview 图版左栏与页脚的垂直关系：报告 body 溢出、.body 网格盒、
   左栏各行盒与 .ft 盒，用于判定压字与修复余量。 */
const { chromium } = require('playwright-core');
const path = require('path');

(async () => {
  const b = await chromium.launch();
  const ctx = await b.newContext({ viewport: { width: 1200, height: 750 }, deviceScaleFactor: 1 });
  for (const f of process.argv.slice(2)) {
    const p = await ctx.newPage();
    await p.goto('file://' + path.resolve(f), { waitUntil: 'load' });
    await p.evaluate(() => document.fonts.ready);
    await p.waitForTimeout(300);
    const r = await p.evaluate(() => {
      const rr = (el) => { const c = el.getBoundingClientRect();
        return [+c.x.toFixed(1), +c.y.toFixed(1), +c.width.toFixed(1), +c.height.toFixed(1)]; };
      const body = document.body;
      const col = document.querySelector('.body > div');
      const out = {
        bodyScroll: [body.scrollWidth, body.scrollHeight],
        docScroll: [document.documentElement.scrollWidth, document.documentElement.scrollHeight],
        wrap: rr(document.querySelector('.wrap')),
        grid: rr(document.querySelector('.body')),
        gridScrollH: document.querySelector('.body').scrollHeight,
        ft: rr(document.querySelector('.ft')),
        col1: rr(col), col1ScrollH: col.scrollHeight,
        rows: [], panels: [], ftSpans: [],
      };
      for (const el of col.children) out.rows.push([el.className, ...rr(el), el.textContent.trim().slice(0, 46)]);
      for (const el of col.querySelectorAll('.srow > *')) out.rows.push(['  ' + el.className, ...rr(el), el.textContent.trim().slice(0, 46)]);
      for (const el of document.querySelectorAll('.body > .panel')) out.panels.push([el.className, ...rr(el), el.scrollHeight]);
      for (const el of document.querySelectorAll('.ft > span')) out.ftSpans.push([...rr(el), el.textContent.trim().slice(0, 90)]);
      const mc = document.querySelector('.mapcap');
      out.mapcap = [...rr(mc), mc.scrollWidth, mc.clientWidth];
      return out;
    });
    console.log('### ' + f);
    console.log(JSON.stringify(r, null, 1));
    await p.close();
  }
  await b.close();
})();
