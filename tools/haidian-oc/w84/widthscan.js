'use strict';
/* 第 12 页（核验图单张全幅页）图框宽度的可行区间扫描：在已生成的页面上逐档改写
   .vfig 的 width，读回 .ver 的溢出量与尾行—页脚净空，用来把 SINGLE_MM 定到
   「装得下且尽量大」的一档。只改内联样式量测，不落盘。 */
const { chromium } = require('playwright-core');
const path = require('path');
(async () => {
  const b = await chromium.launch();
  const ctx = await b.newContext({ viewport: { width: 1588, height: 1123 }, deviceScaleFactor: 1 });
  for (const f of process.argv.slice(2)) {
    const p = await ctx.newPage();
    await p.goto('file://' + path.resolve(f), { waitUntil: 'load' });
    await p.evaluate(() => document.fonts.ready);
    await p.waitForTimeout(400);
    const rows = await p.evaluate(async () => {
      const out = [];
      const fig = document.querySelector('.vfig');
      const grid = document.querySelector('.vgrid');
      const ver = document.querySelector('.ver');
      const foot = document.querySelector('.foot');
      const tail = document.querySelector('.ver .tailrow');
      const cap = document.querySelector('.vcap');
      for (let mm = 276; mm >= 200; mm -= 2) {
        fig.style.width = mm + 'mm';
        grid.style.gridTemplateColumns = mm + 'mm';
        await new Promise(r => requestAnimationFrame(r));
        const tb = tail.getBoundingClientRect();
        out.push({ mm, over: ver.scrollHeight - ver.clientHeight,
                   gap: +(foot.getBoundingClientRect().y - (tb.y + tb.height)).toFixed(1),
                   capH: +cap.getBoundingClientRect().height.toFixed(1),
                   imgH: +document.querySelector('.vfig img').getBoundingClientRect().height.toFixed(1) });
      }
      return out;
    });
    console.log('### ' + path.basename(f));
    for (const r of rows) console.log(`  ${r.mm}mm  溢出 ${String(r.over).padStart(4)}  净空 ${String(r.gap).padStart(7)}  图高 ${r.imgH}  图注高 ${r.capH}`);
    await p.close();
  }
  await b.close();
})();
