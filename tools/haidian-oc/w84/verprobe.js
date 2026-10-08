'use strict';
/* A3 新增核验图页（12—15）的版心防线量测：
   报告 body/文档溢出、.ver 容器盒与其 scrollHeight、末元素底边与 .foot 顶边净空，
   以及每张 <img> 的自然/呈现尺寸，用于判定图框是否被压缩或溢出版心。 */
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
    const r = await p.evaluate(() => {
      const rr = e => { const c = e.getBoundingClientRect();
        return { y: +c.y.toFixed(1), h: +c.height.toFixed(1), b: +(c.y + c.height).toFixed(1) }; };
      const ver = document.querySelector('.ver'), foot = document.querySelector('.foot');
      const tail = document.querySelector('.ver .tailrow');
      return {
        docScroll: [document.documentElement.scrollWidth, document.documentElement.scrollHeight],
        bodyScroll: [document.body.scrollWidth, document.body.scrollHeight],
        ver: { ...rr(ver), sh: ver.scrollHeight, ch: ver.clientHeight },
        grid: rr(document.querySelector('.vgrid')),
        note: rr(document.querySelector('.vnote')),
        attr: rr(document.querySelector('.vattr')),
        tail: rr(tail), foot: rr(foot),
        imgs: [...document.querySelectorAll('.vfig img')].map(i => ({
          src: i.getAttribute('src').split('/').pop(),
          nat: [i.naturalWidth, i.naturalHeight],
          box: [+i.getBoundingClientRect().width.toFixed(1), +i.getBoundingClientRect().height.toFixed(1)],
        })),
        caps: [...document.querySelectorAll('.vcap')].map(c => ({ ...rr(c), sh: c.scrollHeight })),
      };
    });
    r.gapTailFoot = +(r.foot.y - r.tail.b).toFixed(1);
    r.overflow = r.ver.sh - r.ver.ch;
    console.log(path.basename(f), JSON.stringify(r));
    await p.close();
  }
  await b.close();
})();
