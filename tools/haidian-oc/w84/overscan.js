'use strict';
/* 版心防线全量扫描：在与 @page 等价的视口下加载每个页源，报告
   (a) 任何滚动容器的纵/横向溢出（scrollHeight/Width 超出 clientHeight/Width 超过 1 px）；
   (b) 任何可见元素的盒越出 body 盒（body 设了 overflow:hidden，越界即被裁切）。
   用法：node overscan.js <w> <h> <html> [...] */
const { chromium } = require('playwright-core');
const path = require('path');
(async () => {
  const [w, h] = process.argv.slice(2, 4).map(Number);
  const b = await chromium.launch();
  const ctx = await b.newContext({ viewport: { width: w, height: h }, deviceScaleFactor: 1 });
  let bad = 0;
  for (const f of process.argv.slice(4)) {
    const p = await ctx.newPage();
    await p.goto('file://' + path.resolve(f), { waitUntil: 'load' });
    await p.evaluate(() => document.fonts.ready);
    await p.waitForTimeout(400);
    const r = await p.evaluate(() => {
      const clip = [], out = [];
      const bb = document.body.getBoundingClientRect();
      for (const el of document.querySelectorAll('body *')) {
        if (el.namespaceURI === 'http://www.w3.org/2000/svg') continue;
        const cs = getComputedStyle(el);
        if (cs.display === 'none' || cs.visibility === 'hidden' || +cs.opacity === 0) continue;
        const c = el.getBoundingClientRect();
        if (c.width === 0 || c.height === 0) continue;
        const tag = el.tagName + '.' + String(el.className || '').slice(0, 24);
        const dy = el.scrollHeight - el.clientHeight, dx = el.scrollWidth - el.clientWidth;
        if ((dy > 1 || dx > 1) && cs.overflow !== 'visible')
          out.push([tag, 'scroll +' + dy + '/+' + dx]);
        const ov = Math.max(bb.top - c.top, c.bottom - bb.bottom, bb.left - c.left, c.right - bb.right);
        if (ov > 1) clip.push([tag, '越界 ' + ov.toFixed(1) + ' px',
                               (el.textContent || '').replace(/\s+/g, ' ').trim().slice(0, 40)]);
      }
      return { clip, out, body: [bb.width, bb.height] };
    });
    const n = r.clip.length + r.out.length;
    if (n) bad++;
    console.log(`${n ? '✗' : ' '} ${path.basename(f)}  body ${r.body[0]}x${r.body[1]}  裁切 ${r.clip.length}  滚动溢出 ${r.out.length}`);
    for (const x of r.clip.slice(0, 6)) console.log('     裁切 ', JSON.stringify(x));
    for (const x of r.out.slice(0, 6)) console.log('     溢出 ', JSON.stringify(x));
    await p.close();
  }
  console.log(bad ? `异常页 ${bad}` : '全部页源无裁切、无滚动溢出');
  await b.close();
})();
