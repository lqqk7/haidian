/* w88-fb/shot.js — headless verification of visual/index chapter 16 + 17.
   Renders the interactive scene against the current assets/scene-data.js,
   drives the two real controls ("play guidance flow" then "AI OFF"), and
   writes canvas captures plus a console/error log for review.

   usage: node shot.js <zh|en> <outdir>
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
  const out = process.argv[3] || path.join(__dirname, 'out');
  fs.mkdirSync(out, { recursive: true });
  const file = 'file://' + path.join(PKG, lang === 'en' ? 'visual/index.en.html' : 'visual/index.html');

  const browser = await chromium.launch({ executablePath: EXE });
  const ctx = await browser.newContext({ viewport: { width: 1600, height: 1200 }, deviceScaleFactor: 2 });
  const page = await ctx.newPage();
  const logs = [];
  page.on('console', m => logs.push(m.type() + ': ' + m.text()));
  page.on('pageerror', e => logs.push('PAGEERROR: ' + e.message));
  page.on('requestfailed', r => logs.push('REQFAIL: ' + r.url() + ' ' + (r.failure() || {}).errorText));

  await page.goto(file, { waitUntil: 'load' });
  await page.waitForTimeout(1500);

  const wrap = page.locator('.jz-scene .jz-canvaswrap');
  await wrap.scrollIntoViewIfNeeded();
  await page.waitForFunction(() => {
    const w = document.querySelector('.jz-scene .jz-canvaswrap');
    return w && w.getAttribute('data-ready') === '1';
  }, null, { timeout: 15000 }).catch(e => logs.push('READY-TIMEOUT: ' + e.message));

  const box = await page.locator('.jz-scene canvas').boundingBox();
  logs.push('canvas css box: ' + JSON.stringify(box));
  logs.push('canvas backing: ' + JSON.stringify(await page.evaluate(() => {
    const c = document.querySelector('.jz-scene canvas');
    return { w: c.width, h: c.height };
  })));

  await page.locator('.jz-scene canvas').screenshot({ path: path.join(out, `ch16-${lang}-on.png`) });

  // real click 1: play guidance flow
  await page.locator('.jz-scene [data-jz="play"]').click();
  await page.waitForTimeout(2500);
  await page.locator('.jz-scene canvas').screenshot({ path: path.join(out, `ch16-${lang}-on-play.png`) });

  // real click 2: AI OFF
  await page.locator('.jz-scene [data-jz="off"]').click();
  await page.waitForTimeout(2000);
  await page.locator('.jz-scene canvas').screenshot({ path: path.join(out, `ch16-${lang}-off.png`) });
  logs.push('state after off: ' + await page.getAttribute('.jz-scene', 'data-state'));

  // node button interaction
  await page.locator('.jz-scene [data-node="OP-04"]').click();
  await page.waitForTimeout(600);
  logs.push('OP-04 card name: ' + (await page.textContent('.jz-scene .jz-cname')));
  await page.locator('.jz-scene [data-jz="on"]').click();
  await page.waitForTimeout(800);
  logs.push('state back on: ' + await page.getAttribute('.jz-scene', 'data-state'));

  // chapter 17 three.js
  const c3 = page.locator('.j3-scene .j3-canvaswrap');
  await c3.scrollIntoViewIfNeeded();
  await page.waitForTimeout(4000);
  logs.push('ch17 data-ready: ' + await page.getAttribute('.j3-scene .j3-canvaswrap', 'data-ready'));
  logs.push('ch17 data-view: ' + await page.getAttribute('.j3-scene .j3-canvaswrap', 'data-view'));
  logs.push('ch17 degrade: ' + await page.evaluate(() => {
    const p = document.querySelector('.j3-degrade');
    return p ? (p.hidden ? '(hidden)' : p.textContent) : '(none)';
  }));
  await page.locator('.j3-scene canvas').screenshot({ path: path.join(out, `ch17-${lang}-on.png`) }).catch(e => logs.push('ch17 shot failed: ' + e.message));
  await page.locator('.j3-scene [data-j3="off"]').click().catch(() => {});
  await page.waitForTimeout(1500);
  await page.locator('.j3-scene canvas').screenshot({ path: path.join(out, `ch17-${lang}-off.png`) }).catch(() => {});

  fs.writeFileSync(path.join(out, `log-${lang}.txt`), logs.join('\n'));
  console.log(logs.join('\n'));
  await browser.close();
})();
