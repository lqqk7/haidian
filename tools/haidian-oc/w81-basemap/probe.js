const { chromium } = require('playwright-core');
const path = require('path');
// usage: node probe.js <html> <selector...>
(async () => {
  const [html, ...sels] = process.argv.slice(2);
  const b = await chromium.launch();
  const ctx = await b.newContext({ viewport: { width: 1200, height: 750 }, deviceScaleFactor: 1 });
  const p = await ctx.newPage();
  await p.goto('file://' + path.resolve(html), { waitUntil: 'load' });
  await p.evaluate(() => document.fonts.ready);
  await p.waitForTimeout(400);
  const out = await p.evaluate((ss) => {
    const r = [];
    for (const s of ss) {
      document.querySelectorAll(s).forEach((e, i) => {
        const b = e.getBoundingClientRect();
        r.push({ sel: s, i, x: +b.x.toFixed(1), y: +b.y.toFixed(1),
                 w: +b.width.toFixed(1), h: +b.height.toFixed(1),
                 sh: e.scrollHeight, ch: e.clientHeight,
                 txt: (e.textContent || '').slice(0, 26) });
      });
    }
    return r;
  }, sels);
  for (const o of out) console.log(JSON.stringify(o));
  await b.close();
})();
