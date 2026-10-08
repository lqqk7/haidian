const { chromium } = require('playwright-core');
const path=require('path');
(async()=>{ const b=await chromium.launch();
 for(const f of process.argv.slice(2)){
  const ctx=await b.newContext({viewport:{width:1587,height:1123}}); const p=await ctx.newPage();
  await p.goto('file://'+path.resolve(f),{waitUntil:'load'}); await p.evaluate(()=>document.fonts.ready); await p.waitForTimeout(250);
  console.log(path.basename(f), JSON.stringify(await p.evaluate(()=>{
    const mm=x=>+(x/3.7795).toFixed(1);
    const H=s=>{const e=document.querySelector(s);return e?mm(e.getBoundingClientRect().height):null};
    return {ctop:H('.ctop'),h1:H('.cover h1'),sub:H('.sub'),plan:H('.cplan'),bot:H('.cbot'),claim:H('.cclaim'),
      reads:[...document.querySelectorAll('.cr span')].map(e=>mm(e.getBoundingClientRect().height)),
      foot:H('.cfoot'), body:mm(document.body.scrollHeight)};})));
  await ctx.close(); }
 await b.close(); })();
