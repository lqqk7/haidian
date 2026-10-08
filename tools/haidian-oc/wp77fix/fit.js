'use strict';
/* 量测图版文案区块的排版余量：给定 html 与若干 (选择器, 候选文案)，
   报告 body 溢出、元素盒宽高与行数，用于判断改写后是否破版。 */
const { chromium } = require('playwright-core');
const path = require('path');

const JOBS = require(process.argv[2]);

(async () => {
  const b = await chromium.launch();
  const ctx = await b.newContext({ viewport: { width: 1200, height: 750 }, deviceScaleFactor: 1 });
  for (const job of JOBS) {
    const p = await ctx.newPage();
    await p.goto('file://' + path.resolve(job.file), { waitUntil: 'load' });
    await p.evaluate(() => document.fonts.ready);
    await p.waitForTimeout(300);
    const r = await p.evaluate((job) => {
      const out = { file: job.file, cases: [] };
      const probe = (label) => {
        const body = document.body;
        const info = {
          label,
          bodyScroll: [body.scrollWidth, body.scrollHeight],
          docScroll: [document.documentElement.scrollWidth, document.documentElement.scrollHeight],
          els: [],
        };
        for (const sel of job.probes) {
          const el = document.querySelector(sel);
          if (!el) { info.els.push([sel, 'MISSING']); continue; }
          const cs = getComputedStyle(el);
          const lh = parseFloat(cs.lineHeight) || parseFloat(cs.fontSize) * 1.2;
          const rc = el.getBoundingClientRect();
          info.els.push([sel, +rc.width.toFixed(1), +rc.height.toFixed(1),
            Math.round(rc.height / lh), el.textContent.slice(0, 40)]);
        }
        // 容器溢出
        const wrap = document.querySelector('.wrap');
        if (wrap) info.wrap = [wrap.scrollWidth, wrap.clientWidth, wrap.scrollHeight, wrap.clientHeight];
        return info;
      };
      out.cases.push(probe('BEFORE'));
      for (const c of job.candidates || []) {
        for (const [sel, txt] of c.edits) {
          const el = document.querySelector(sel);
          if (el) el.textContent = txt;
        }
        out.cases.push(probe(c.name));
        for (const [sel, , orig] of c.edits) {
          const el = document.querySelector(sel);
          if (el && orig !== undefined) el.textContent = orig;
        }
      }
      return out;
    }, job);
    console.log(JSON.stringify(r, null, 1));
    await p.close();
  }
  await b.close();
})();
