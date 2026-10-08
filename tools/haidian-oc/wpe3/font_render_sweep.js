// 零依赖 CDP 全页扫查：对每一条实际承载中文的层叠字体栈各建一个探针，
// 探针内放该页全部唯一汉字，再用 CSS.getPlatformFontsForNode 读出渲染器实测用字。
// 通过条件：每个探针只用到一款字体，且为随包子集，字形数等于探针字符数（无回退、无缺字）。
const PORT = process.argv[2] || '9333';
const FILES = process.argv.slice(3);

async function http(path, method = 'GET') {
  const r = await fetch(`http://127.0.0.1:${PORT}${path}`, { method });
  return r.json();
}
function cdp(ws) {
  let id = 0; const pending = new Map();
  ws.addEventListener('message', (e) => {
    const m = JSON.parse(e.data);
    if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); }
  });
  return (method, params = {}) => new Promise((res, rej) => {
    const n = ++id;
    pending.set(n, (m) => (m.error ? rej(new Error(method + ': ' + JSON.stringify(m.error))) : res(m.result)));
    ws.send(JSON.stringify({ id: n, method, params }));
  });
}
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

(async () => {
  let fail = 0;
  for (const file of FILES) {
    const target = await http('/json/new?' + encodeURIComponent('file://' + file), 'PUT');
    const ws = new WebSocket(target.webSocketDebuggerUrl);
    await new Promise((r) => ws.addEventListener('open', r));
    const send = cdp(ws);
    await send('Page.enable'); await send('DOM.enable');
    await send('CSS.enable'); await send('Runtime.enable');
    await sleep(2500);
    const ev = async (expr) => (await send('Runtime.evaluate',
      { expression: expr, returnByValue: true, awaitPromise: true })).result.value;

    const info = await ev(`(async()=>{await document.fonts.ready;
      const walk=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT);
      const stacks=new Map(); const all=new Set(); let n;
      while((n=walk.nextNode())){
        const EXEMPT=new Set([0xB7,0x2013,0x2014,0x2018,0x2019,0x201C,0x201D,0x2026]);
        const chars=[...n.nodeValue].filter(c=>c.charCodeAt(0)>0x7f&&!EXEMPT.has(c.charCodeAt(0)));
        if(!chars.length) continue;
        const el=n.parentElement; if(!el||el.closest('noscript')) continue;
        const ff=getComputedStyle(el).fontFamily;
        if(!stacks.has(ff)) stacks.set(ff,{el,chars:new Set()});
        chars.forEach(c=>{stacks.get(ff).chars.add(c); all.add(c);});
      }
      const out=[]; let i=0;
      for(const [ff,v] of stacks){
        const s=document.createElement('span');
        s.setAttribute('data-sweep',String(i));
        s.style.cssText='position:absolute;left:-99999px;top:0;white-space:nowrap';
        s.textContent=[...v.chars].join('');
        v.el.appendChild(s);
        out.push({idx:i,stack:ff,chars:v.chars.size}); i++;
      }
      return {stacks:out,total:all.size};})()`);

    const { root } = await send('DOM.getDocument', { depth: -1 });
    console.log(`\n=== ${file.split('/').slice(-2).join('/')}  唯一非 ASCII ${info.total} 个，承载栈 ${info.stacks.length} 条`);
    for (const s of info.stacks) {
      const { nodeId } = await send('DOM.querySelector', { nodeId: root.nodeId, selector: `[data-sweep="${s.idx}"]` });
      const { fonts } = await send('CSS.getPlatformFontsForNode', { nodeId });
      const used = fonts.map((f) => `${f.familyName}×${f.glyphCount}`).join(' + ');
      const ok = fonts.length === 1 && /ESJZ Sans Subset/.test(fonts[0].familyName) && fonts[0].glyphCount === s.chars;
      if (!ok) fail++;
      console.log(`  ${ok ? 'OK  ' : 'FAIL'} ${s.chars} 字 | 实测用字: ${used}`);
      console.log(`       栈: ${s.stack.slice(0, 110)}`);
    }
    ws.close();
    try { await fetch(`http://127.0.0.1:${PORT}/json/close/${target.id}`, { method: 'PUT' }); } catch (e) {}
  }
  console.log(`\n合计 失败 ${fail} 项`);
  process.exit(fail ? 1 : 0);
})();
