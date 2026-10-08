const { chromium } = require('playwright-core');
const path=require('path');
(async()=>{
  const b=await chromium.launch();
  const ctx=await b.newContext();
  for (const f of process.argv.slice(2)){
    const p=await ctx.newPage();
    await p.goto('file://'+path.resolve(f),{waitUntil:'load'});
    await p.evaluate(()=>document.fonts.ready);
    await p.waitForTimeout(200);
    const r=await p.evaluate(()=>{
      const b=document.body, d=document.documentElement;
      const cs=getComputedStyle(b);
      let over=[];
      const br=b.getBoundingClientRect();
      document.querySelectorAll('*').forEach(el=>{
        const rr=el.getBoundingClientRect();
        if(rr.width>0&&rr.height>0&&(rr.right>br.right+1.5||rr.bottom>br.bottom+1.5||rr.left<br.left-1.5))
          over.push(el.tagName+'.'+(el.className&&el.className.baseVal===undefined?String(el.className).slice(0,24):'')+` r=${rr.right.toFixed(1)} b=${rr.bottom.toFixed(1)}`);
      });
      return {bw:cs.width,bh:cs.height,sw:b.scrollWidth,sh:b.scrollHeight,dsw:d.scrollWidth,dsh:d.scrollHeight,over:over.slice(0,6),n:over.length};
    });
    console.log(path.basename(f), JSON.stringify(r));
    await p.close();
  }
  await b.close();
})();
