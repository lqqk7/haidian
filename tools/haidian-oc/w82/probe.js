const { chromium } = require('playwright-core');
const path=require('path');
(async()=>{
  const b=await chromium.launch(); const ctx=await b.newContext();
  for (const f of process.argv.slice(2)){
    const p=await ctx.newPage();
    await p.goto('file://'+path.resolve(f),{waitUntil:'load'});
    await p.evaluate(()=>document.fonts.ready); await p.waitForTimeout(200);
    const r=await p.evaluate(()=>{
      const q=s=>document.querySelector(s);
      const R=e=>e?{t:+e.getBoundingClientRect().top.toFixed(1),b:+e.getBoundingClientRect().bottom.toFixed(1),h:+e.getBoundingClientRect().height.toFixed(1)}:null;
      const aud=q('.aud')||q('.wrap');
      const cols=[...document.querySelectorAll('.aud > .grid > div')].map(R);
      return {box:R(aud), grid:R(q('.grid')), cols, ptr:R(q('.ptr')), tail:R(q('.tailrow')), foot:R(q('.foot')), lead:R(q('.lead'))};
    });
    console.log(path.basename(f), JSON.stringify(r));
    await p.close();
  }
  await b.close();
})();
