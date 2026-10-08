/* w88-fb/cap.js — capture the chapter-16 interactive canvas at a fixed pixel
   width so the static fallback panels can be re-cut from the live scene.

   usage: node cap.js <zh|en> <cssWidth> <dpr> <outdir>
   Emits <out>/panel-<lang>-on.png and panel-<lang>-off.png.
*/
const { chromium } = require('playwright-core');
const path = require('path');
const fs = require('fs');

const EXE = process.env.CHROME_EXE ||
  path.join(process.env.HOME,
    'Library/Caches/ms-playwright/chromium-1228/chrome-mac-arm64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing');
const PKG = require('path').resolve(__dirname, '../../../', 'submissions/lqqk7/every-sense-jingzhang');

(async () => {
  const lang = process.argv[2] || 'zh';
  const w = parseInt(process.argv[3] || '910', 10);
  const dpr = parseFloat(process.argv[4] || '1');
  const out = process.argv[5] || path.join(__dirname, 'out');
  fs.mkdirSync(out, { recursive: true });
  const file = 'file://' + path.join(PKG, lang === 'en' ? 'visual/index.en.html' : 'visual/index.html');

  const browser = await chromium.launch({ executablePath: EXE });
  const ctx = await browser.newContext({ viewport: { width: w + 700, height: 1200 }, deviceScaleFactor: dpr });
  const page = await ctx.newPage();
  const errs = [];
  page.on('pageerror', e => errs.push('PAGEERROR: ' + e.message));
  page.on('console', m => { if (m.type() === 'error') errs.push('CONSOLE: ' + m.text()); });
  await page.goto(file, { waitUntil: 'load' });

  // pin the canvas to an exact CSS width, independent of page layout
  await page.addStyleTag({ content:
    `.jz-scene .jz-stage{display:block !important}
     .jz-scene .jz-canvaswrap{width:${w}px !important;max-width:none !important}
     .jz-scene .jz-side{display:none !important}` });
  await page.evaluate(() => window.dispatchEvent(new Event('resize')));
  await page.waitForTimeout(1200);
  await page.locator('.jz-scene .jz-canvaswrap').scrollIntoViewIfNeeded();
  await page.waitForFunction(() => document.querySelector('.jz-scene .jz-canvaswrap')
    .getAttribute('data-ready') === '1', null, { timeout: 15000 });

  const info = await page.evaluate(() => {
    const c = document.querySelector('.jz-scene canvas');
    const r = c.getBoundingClientRect();
    return { css: [r.width, r.height], backing: [c.width, c.height] };
  });
  console.log(lang, 'canvas', JSON.stringify(info));

  // click 1: play guidance flow
  await page.locator('.jz-scene [data-jz="play"]').click();
  await page.waitForTimeout(2200);
  await page.locator('.jz-scene canvas').screenshot({ path: path.join(out, `panel-${lang}-on.png`) });

  // click 2: AI OFF
  await page.locator('.jz-scene [data-jz="off"]').click();
  await page.waitForTimeout(1600);
  await page.locator('.jz-scene canvas').screenshot({ path: path.join(out, `panel-${lang}-off.png`) });

  console.log(errs.length ? errs.join('\n') : 'no console/page errors');
  await browser.close();
})();
