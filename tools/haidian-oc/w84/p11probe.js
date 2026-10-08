const { chromium } = require('playwright-core');
const path=require('path');
(async()=>{const b=await chromium.launch();const ctx=await b.newContext({viewport:{width:1588,height:1123},deviceScaleFactor:1});
for(const f of process.argv.slice(2)){const p=await ctx.newPage();
await p.goto('file://'+path.resolve(f),{waitUntil:'load'});await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(300);
const r=await p.evaluate(()=>{const rr=e=>{const c=e.getBoundingClientRect();return {y:+c.y.toFixed(1),h:+c.height.toFixed(1),b:+(c.y+c.height).toFixed(1)};};
const aud=document.querySelector('.aud');const foot=document.querySelector('.foot');
const secs=[...document.querySelectorAll('.aud .sec')].map(s=>({cls:s.querySelector('.n')?s.querySelector('.n').textContent:'?',...rr(s),sh:s.scrollHeight}));
const trs=[...document.querySelectorAll('.tr')];const cols=[...document.querySelector('.aud .grid').children].map(c=>({...rr(c),sh:c.scrollHeight}));
return {aud:{...rr(aud),sh:aud.scrollHeight},foot:rr(foot),cols,secs,lastTr:trs.length?rr(trs[trs.length-1]):null,
 tail:rr(document.querySelector('.tailrow')), ptr:rr(document.querySelector('.ptr'))};});
console.log(path.basename(f),JSON.stringify(r));await p.close();}
await b.close();})();
