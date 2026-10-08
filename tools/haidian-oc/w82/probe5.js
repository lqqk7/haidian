const { chromium } = require('playwright-core');
const path=require('path');
(async()=>{ const b=await chromium.launch();
 for(const f of process.argv.slice(2)){
  const ctx=await b.newContext({viewport:{width:4494,height:3179}}); const p=await ctx.newPage();
  await p.goto('file://'+path.resolve(f),{waitUntil:'load'}); await p.evaluate(()=>document.fonts.ready); await p.waitForTimeout(300);
  const r=await p.evaluate(()=>{
    const R=e=>e?{t:+e.getBoundingClientRect().top.toFixed(0),b:+e.getBoundingClientRect().bottom.toFixed(0),h:+e.getBoundingClientRect().height.toFixed(0)}:null;
    const q=s=>R(document.querySelector(s));
    return {mm: 3.7795, hdr:q('.b1hdr'), wrap:q('.b1wrap'), claim:q('.b1claim'), fig:q('.b1fig'), cap:q('.b1cap'), foot:q('.b1foot'), body:{h:document.body.scrollHeight}};
  });
  console.log(path.basename(f), JSON.stringify(r));
  await ctx.close(); }
 await b.close(); })();
