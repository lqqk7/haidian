'use strict';
/* Playwright renderer: HTML -> PNG screenshot or print-to-PDF.
   usage:
     node render.js png  <html> <out.png> <cssW> <cssH> <dsf>
     node render.js pdf  <out.pdf> <html1> [html2 ...]        (page size from CSS @page)
*/
const { chromium } = require('playwright-core');
const path = require('path');
const fs = require('fs');

async function main() {
  const mode = process.argv[2];
  const browser = await chromium.launch();
  if (mode === 'png') {
    const [html, out, w, h, dsf] = process.argv.slice(3);
    const ctx = await browser.newContext({
      viewport: { width: Number(w), height: Number(h) },
      deviceScaleFactor: Number(dsf),
    });
    const page = await ctx.newPage();
    await page.goto('file://' + path.resolve(html), { waitUntil: 'load' });
    await page.evaluate(() => document.fonts.ready);
    await page.waitForTimeout(500);
    await page.screenshot({ path: out, type: 'png' });
    console.log('png', out);
  } else if (mode === 'pdf') {
    const out = process.argv[3];
    const htmls = process.argv.slice(4);
    const parts = [];
    const ctx = await browser.newContext();
    for (let i = 0; i < htmls.length; i++) {
      const page = await ctx.newPage();
      await page.goto('file://' + path.resolve(htmls[i]), { waitUntil: 'load' });
      await page.evaluate(() => document.fonts.ready);
      await page.waitForTimeout(400);
      const p = out.replace(/\.pdf$/, `.part${i}.pdf`);
      await page.pdf({ path: p, printBackground: true, preferCSSPageSize: true, pageRanges: '1' });
      parts.push(p);
      await page.close();
    }
    fs.writeFileSync(out + '.parts.json', JSON.stringify(parts));
    console.log('parts', parts.length);
  }
  await browser.close();
}
main().catch((e) => { console.error(e); process.exit(1); });
