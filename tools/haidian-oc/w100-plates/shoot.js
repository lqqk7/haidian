'use strict';
/* w100-plates renderer — HTML -> PNG band + width assertions.
   体裁沿用 wp4b/render.js（Playwright + Chromium 无头截图）与 w81-basemap/probe.js
   （渲后 getBoundingClientRect 探测）。
   usage: node shoot.js <html> <out.png> <cssW> <cssH> <dsf>
   渲染前先跑溢出/叠印断言，任一失败以非零码退出且不写文件。 */
const { chromium } = require('playwright-core');
const path = require('path');

(async () => {
  const [html, out, w, h, dsf] = process.argv.slice(2);
  const browser = await chromium.launch();
  const ctx = await browser.newContext({
    viewport: { width: Number(w), height: Number(h) },
    deviceScaleFactor: Number(dsf),
  });
  const page = await ctx.newPage();
  const errs = [];
  page.on('pageerror', e => errs.push('PE ' + e));
  await page.goto('file://' + path.resolve(html), { waitUntil: 'load' });
  await page.evaluate(() => document.fonts.ready);
  await page.waitForTimeout(400);

  const rep = await page.evaluate(() => {
    const R = el => el.getBoundingClientRect();
    const vw = document.documentElement.clientWidth;
    const vh = document.documentElement.clientHeight;
    const over = [];      // 溢出容器 / 画布
    const clip = [];      // 自身内容被容器裁掉
    const collide = [];   // 同行相邻文本节点叠印

    document.querySelectorAll('*').forEach(el => {
      const r = R(el);
      if (r.width <= 0 || r.height <= 0) return;
      const tag = el.className || el.tagName;
      // 1. 画布边界
      if (r.right > vw + 0.5 || r.bottom > vh + 0.5 || r.left < -0.5 || r.top < -0.5)
        over.push(`${tag} canvas r=${r.right.toFixed(1)}/${vw} b=${r.bottom.toFixed(1)}/${vh}`);
      // 2. 自身内容被裁
      if (el.scrollWidth > Math.ceil(r.width) + 1 || el.scrollHeight > Math.ceil(r.height) + 1)
        clip.push(`${tag} scroll=${el.scrollWidth}x${el.scrollHeight} box=${r.width.toFixed(0)}x${r.height.toFixed(0)}`);
      // 3. 越出直接父容器的内容盒
      const p = el.parentElement;
      if (p && p !== document.body && p !== document.documentElement) {
        const pr = R(p);
        if (r.right > pr.right + 0.6 || r.bottom > pr.bottom + 0.6 || r.left < pr.left - 0.6)
          over.push(`${tag} parent r=${r.right.toFixed(1)}>${pr.right.toFixed(1)} b=${r.bottom.toFixed(1)}>${pr.bottom.toFixed(1)}`);
      }
    });

    // 4. 徽标/标题一类同层文本互相叠印
    const leaves = [...document.querySelectorAll('*')].filter(
      el => el.children.length === 0 && (el.textContent || '').trim());
    for (let i = 0; i < leaves.length; i++)
      for (let j = i + 1; j < leaves.length; j++) {
        const a = R(leaves[i]), b = R(leaves[j]);
        if (leaves[i].contains(leaves[j]) || leaves[j].contains(leaves[i])) continue;
        const ox = Math.min(a.right, b.right) - Math.max(a.left, b.left);
        const oy = Math.min(a.bottom, b.bottom) - Math.max(a.top, b.top);
        if (ox > 1 && oy > 1)
          collide.push(`"${leaves[i].textContent.trim().slice(0, 20)}" x "${leaves[j].textContent.trim().slice(0, 20)}" ${ox.toFixed(1)}x${oy.toFixed(1)}`);
      }
    return { over, clip, collide, sw: document.body.scrollWidth, sh: document.body.scrollHeight, vw, vh };
  });

  const bad = rep.over.length + rep.clip.length + rep.collide.length;
  console.log(JSON.stringify({
    html: path.basename(html), body: `${rep.sw}x${rep.sh}`, viewport: `${rep.vw}x${rep.vh}`,
    overflow: rep.over.length, clipped: rep.clip.length, overprint: rep.collide.length,
    pageerrors: errs.length,
  }));
  [...rep.over, ...rep.clip, ...rep.collide].slice(0, 20).forEach(s => console.log('  ! ' + s));
  errs.slice(0, 5).forEach(s => console.log('  ' + s));

  if (bad === 0 && errs.length === 0) {
    await page.screenshot({ path: out, type: 'png' });
    console.log('OK ->', out);
  } else {
    console.log('ASSERTION FAILED — no png written');
  }
  await browser.close();
  process.exit(bad === 0 && errs.length === 0 ? 0 : 1);
})();
