const { chromium } = require('playwright-core');
const path=require('path');
(async()=>{
  const b=await chromium.launch(); const ctx=await b.newContext();
  for (const f of process.argv.slice(2)){
    const p=await ctx.newPage();
    await p.goto('file://'+path.resolve(f),{waitUntil:'load'});
    await p.evaluate(()=>document.fonts.ready); await p.waitForTimeout(200);
    const r=await p.evaluate(()=>{
      const out=[];
      document.querySelectorAll('.sec, .sec > *, .sq, .tu, .tn, .warn, .fab, .th, .tr').forEach(e=>{
        const R=e.getBoundingClientRect();
        out.push([e.className.slice(0,14), +R.height.toFixed(1)].join(':'));
      });
      return out;
    });
    console.log(path.basename(f), r.join(' | '));
    await p.close();
  }
  await b.close();
})();
