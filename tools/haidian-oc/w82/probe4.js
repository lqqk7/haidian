const { chromium } = require('playwright-core');
const path=require('path');
(async()=>{ const b=await chromium.launch();
 for(const f of process.argv.slice(2)){
  const ctx=await b.newContext({viewport:{width:1200,height:750}}); const p=await ctx.newPage();
  await p.goto('file://'+path.resolve(f),{waitUntil:'load'}); await p.evaluate(()=>document.fonts.ready); await p.waitForTimeout(250);
  console.log(path.basename(f), JSON.stringify(await p.evaluate(()=>[...document.querySelectorAll('.mlab')].map(e=>e.textContent.trim()+':'+Math.round(e.getBoundingClientRect().height)))));
  await ctx.close(); }
 await b.close(); })();
