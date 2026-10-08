const { chromium } = require('playwright-core');
const path=require('path');
(async()=>{ const b=await chromium.launch();
 const ctx=await b.newContext({viewport:{width:1587,height:1123}}); const p=await ctx.newPage();
 await p.goto('file://'+path.resolve(process.argv[2]),{waitUntil:'load'}); await p.evaluate(()=>document.fonts.ready); await p.waitForTimeout(250);
 console.log(JSON.stringify(await p.evaluate(()=>[...document.querySelectorAll('.cr b')].map(e=>{const c=getComputedStyle(e);const r=e.getBoundingClientRect();return {t:e.textContent,fs:c.fontSize,col:c.color,disp:c.display,w:r.width,h:r.height,vis:c.visibility,op:c.opacity};})),null,1));
 await b.close(); })();
