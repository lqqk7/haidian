'use strict';
/* A0 双语展板版面文本字号全量实测（R1-04 复核）。
   口径：对每个板面的 DOM 逐元素读取 computedStyle 的 font-size(px)，按 px × 0.75 = pt
   换算。只计「版面文本层」：元素自身直接持有非空文本节点、可见（非 display:none /
   visibility:hidden / opacity:0 / 零尺寸）、且不在 <svg> 内（SVG 内注记属图版层，
   由 R1-03 / R1-05 另行登记）。图版以 JPEG 嵌入，其内部文字不进入本项量测。
   用法：node typescan.js <html> [<html> ...]  → 逐元素 JSON 读数台账 */
const { chromium } = require('playwright-core');
const path = require('path');

(async () => {
  const b = await chromium.launch();
  const ctx = await b.newContext({ viewport: { width: 1600, height: 1200 } });
  const all = [];
  for (const f of process.argv.slice(2)) {
    const p = await ctx.newPage();
    await p.goto('file://' + path.resolve(f), { waitUntil: 'load' });
    await p.evaluate(() => document.fonts.ready);
    await p.waitForTimeout(400);
    const rows = await p.evaluate(() => {
      const out = [];
      const walk = (el) => {
        if (el.namespaceURI === 'http://www.w3.org/2000/svg') return;
        const cs = getComputedStyle(el);
        if (cs.display === 'none' || cs.visibility === 'hidden' || +cs.opacity === 0) return;
        let own = '';
        for (const n of el.childNodes) if (n.nodeType === 3) own += n.nodeValue;
        own = own.replace(/\s+/g, ' ').trim();
        if (own) {
          const r = el.getBoundingClientRect();
          if (r.width > 0 && r.height > 0) {
            out.push({ tag: el.tagName, cls: String(el.className || '').slice(0, 30),
                       px: +parseFloat(cs.fontSize).toFixed(3), t: own.slice(0, 40) });
          }
        }
        for (const c of el.children) walk(c);
      };
      walk(document.body);
      return out;
    });
    all.push({ file: path.basename(f), n: rows.length, rows });
    await p.close();
  }
  console.log(JSON.stringify(all));
  await b.close();
})();
