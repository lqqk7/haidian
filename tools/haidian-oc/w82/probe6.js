const { chromium } = require('playwright-core');
const path=require('path');
(async()=>{ const b=await chromium.launch();
 for(const f of process.argv.slice(2)){
  const ctx=await b.newContext({viewport:{width:4494,height:3179}}); const p=await ctx.newPage();
  await p.goto('file://'+path.resolve(f),{waitUntil:'load'}); await p.evaluate(()=>document.fonts.ready); await p.waitForTimeout(300);
  console.log(path.basename(f), JSON.stringify(await p.evaluate(()=>{
    const px2mm=x=>+(x/3.7795).toFixed(1);
    const o={};
    o.idx=px2mm(document.querySelector('.b1idx').getBoundingClientRect().height);
    o.rows=[...document.querySelectorAll('.b1idx .ix .v, .b1idx .note')].map(e=>px2mm(e.getBoundingClientRect().height));
    o.cap=px2mm(document.querySelector('.b1cap').getBoundingClientRect().bottom);
    o.footT=px2mm(document.querySelector('.b1foot').getBoundingClientRect().top);
    o.bodyH=px2mm(document.body.scrollHeight);
    return o;})));
  await ctx.close(); }
 await b.close(); })();
