const { chromium } = require('playwright-core');
const path=require('path');
(async()=>{
  const b=await chromium.launch();
  for (const spec of process.argv.slice(2)){
    const [f,w,h]=spec.split('@');
    const ctx=await b.newContext({viewport:{width:+(w||1200),height:+(h||750)}});
    const p=await ctx.newPage();
    await p.goto('file://'+path.resolve(f),{waitUntil:'load'});
    await p.evaluate(()=>document.fonts.ready); await p.waitForTimeout(250);
    const r=await p.evaluate(()=>{
      const bad=[];
      document.querySelectorAll('.mval,.key .v,.key,.mcard,.mlab,.sq,.tu').forEach(e=>{
        if(e.scrollWidth>e.clientWidth+0.6) bad.push(e.className+' sw='+e.scrollWidth+' cw='+e.clientWidth+' «'+e.textContent.trim().slice(0,26)+'»');
      });
      const bd=document.body;
      const rows=[...document.querySelectorAll('.mval')].map(e=>e.textContent.trim()+'='+Math.round(e.getBoundingClientRect().width)+'/'+Math.round(e.parentElement.getBoundingClientRect().width));
      const keys=[...document.querySelectorAll('.key .v')].map(e=>e.textContent.trim()+'='+Math.round(e.scrollWidth)+'/'+Math.round(e.clientWidth)+' h'+Math.round(e.getBoundingClientRect().height));
      return {sw:bd.scrollWidth,sh:bd.scrollHeight,bad,rows,keys};
    });
    console.log(path.basename(f), JSON.stringify(r));
    await ctx.close();
  }
  await b.close();
})();
