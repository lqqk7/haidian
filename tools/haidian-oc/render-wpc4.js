const { chromium } = require('playwright-core');
const fs = require('fs');
const W = require('path').resolve(__dirname, '.', 'wpc4');

// usage: node render.js seq <fps> <total>   |   node render.js probe <t1,t2,...>
(async () => {
  const mode = process.argv[2] || 'probe';
  const cues = JSON.parse(fs.readFileSync(W + '/cues.json', 'utf8'));
  const b = await chromium.launch();
  const ctx = await b.newContext({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });
  const p = await ctx.newPage();
  const errs = [];
  p.on('pageerror', e => errs.push('PE ' + e));
  p.on('console', m => { if (m.type() === 'error') errs.push('CE ' + m.text()); });
  await p.goto('file://' + W + '/render.html', { waitUntil: 'load' });
  await p.evaluate(([c, t]) => window.__init(c, t), [cues.cues, cues.total]);
  await p.evaluate(() => document.fonts.ready);
  await p.waitForTimeout(600);
  // 预热：把所有图版图片解码一次
  await p.evaluate(async () => {
    await Promise.all([...document.querySelectorAll('.plate img')].map(i => i.decode().catch(() => {})));
  });

  if (mode === 'probe') {
    const ts = (process.argv[3] || '2,8,17,24,31,37,44,49,57').split(',').map(Number);
    for (const t of ts) {
      await p.evaluate(tt => window.__setT(tt), t);
      await p.screenshot({ path: `${W}/probe/p${String(t).replace('.', '_')}.png` });
    }
    console.log('probe done', errs.slice(0, 5));
  } else if (mode === 'range') {
    // node render.js range <fps> <f0> <f1>   —— 仅重渲 [f0, f1] 闭区间帧，其余复用
    const fps = Number(process.argv[3] || 30);
    const f0 = Number(process.argv[4]);
    const f1 = Number(process.argv[5]);
    for (let f = f0; f <= f1; f++) {
      await p.evaluate(tt => window.__setT(tt), f / fps);
      await p.screenshot({ path: `${W}/frames/f${String(f).padStart(5, '0')}.png`, type: 'png' });
      if (f % 100 === 0) process.stdout.write(f + ' ');
    }
    console.log('\nrange', f0, '-', f1, 'errors', errs.slice(0, 5));
  } else {
    const fps = Number(process.argv[3] || 30);
    const total = Number(process.argv[4] || cues.total);
    const N = Math.ceil(total * fps);
    for (let f = 0; f < N; f++) {
      await p.evaluate(tt => window.__setT(tt), f / fps);
      await p.screenshot({ path: `${W}/frames/f${String(f).padStart(5, '0')}.png`, type: 'png' });
      if (f % 100 === 0) process.stdout.write(f + ' ');
    }
    console.log('\nframes', N, 'errors', errs.slice(0, 5));
  }
  await b.close();
})();
