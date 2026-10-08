/* 逐元素读 computedStyle font-size，取全图下限并报版心溢出。
   口径与 R1-05 中 district-strategy 一致：CSS px × DSF × (768/短边) = 接收分辨率等效 px。 */
const { chromium } = require('playwright-core');
const path = require('path');
(async () => {
  const b = await chromium.launch();
  const ctx = await b.newContext({ viewport: { width: 1200, height: 750 }, deviceScaleFactor: 2.5 });
  for (const f of process.argv.slice(2)) {
    const p = await ctx.newPage();
    await p.goto('file://' + path.resolve(f), { waitUntil: 'load' });
    await p.evaluate(() => document.fonts.ready);
    await p.waitForTimeout(300);
    const r = await p.evaluate(() => {
      const sizes = new Map();
      let n = 0;
      const br = document.body.getBoundingClientRect();
      const over = [];
      document.querySelectorAll('*').forEach((el) => {
        const cs = getComputedStyle(el);
        const fs = parseFloat(cs.fontSize);
        const hasText = Array.from(el.childNodes).some(
          (c) => c.nodeType === 3 && c.textContent.trim().length
        );
        if (hasText) {
          n++;
          const k = fs.toFixed(2);
          sizes.set(k, (sizes.get(k) || 0) + 1);
        }
        const rr = el.getBoundingClientRect();
        if (rr.width > 0 && rr.height > 0 &&
            (rr.right > br.right + 1.5 || rr.bottom > br.bottom + 1.5 ||
             rr.left < br.left - 1.5 || rr.top < br.top - 1.5))
          over.push(el.tagName + '.' + String(el.getAttribute('class') || '').slice(0, 22) +
                    ` r=${rr.right.toFixed(1)} b=${rr.bottom.toFixed(1)} t=${rr.top.toFixed(1)} l=${rr.left.toFixed(1)}`);
      });
      return {
        readings: n,
        sizes: [...sizes.entries()].sort((a, c) => a[0] - c[0]),
        bodyScrollH: document.body.scrollHeight,
        bodyScrollW: document.body.scrollWidth,
        over: over.slice(0, 8),
        nOver: over.length,
      };
    });
    const min = Math.min(...r.sizes.map((s) => parseFloat(s[0])));
    console.log(path.basename(f));
    console.log('  读数项 %d  字号档 %s', r.readings, r.sizes.map((s) => `${s[0]}×${s[1]}`).join(' '));
    console.log('  下限 %s CSS px  → 接收等效 %s px', min.toFixed(2), (min * 2.5 * (768 / 1875)).toFixed(2));
    console.log('  版心 scroll %dx%d  溢出元素 %d %s', r.bodyScrollW, r.bodyScrollH, r.nOver, JSON.stringify(r.over));
    await p.close();
  }
  await b.close();
})();
