'use strict';
const { chromium } = require('playwright-core');
const fs = require('fs'), path = require('path');
const [file, ...cands] = process.argv.slice(2);
(async () => {
  const b = await chromium.launch();
  const ctx = await b.newContext({ viewport: { width: 1200, height: 750 }, deviceScaleFactor: 1 });
  const src = fs.readFileSync(file, 'utf8');
  const OLD = process.env.CAP_OLD;
  for (const c of cands) {
    const html = src.replace(OLD, c);
    const tmp = file + '.probe.html';
    fs.writeFileSync(tmp, html);
    const p = await ctx.newPage();
    await p.goto('file://' + path.resolve(tmp), { waitUntil: 'load' });
    await p.evaluate(() => document.fonts.ready);
    const r = await p.evaluate(() => {
      const m = document.querySelector('.mapcap');
      return { cap: m.offsetHeight, a: m.querySelector('.a').offsetHeight, bb: m.querySelector('.b').offsetHeight };
    });
    console.log(JSON.stringify(r), '|', c.slice(0, 70));
    await p.close();
    fs.unlinkSync(tmp);
  }
  await b.close();
})().catch(e => { console.error(e); process.exit(1); });
