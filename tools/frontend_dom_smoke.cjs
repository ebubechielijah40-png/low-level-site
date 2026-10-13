/** npm install --no-save jsdom@30.1.1
 * python tools/frontend_fixture.py /tmp/bare-metal-dom
 * node tools/frontend_dom_smoke.cjs /tmp/bare-metal-dom
 * DOM behaviour only: no actual pixels, layout, browser paint or INP claim.
 */
const {JSDOM}=require('jsdom'),fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const fixture=process.argv[2],root=path.join(__dirname,'..');if(!fixture)throw new Error('Pass a disposable fixture folder.');
const results=JSON.parse(fs.readFileSync(path.join(fixture,'results.json'))),wait=ms=>new Promise(resolve=>setTimeout(resolve,ms));
function page(name){
 const dom=new JSDOM(fs.readFileSync(path.join(fixture,name+'.html'),'utf8'),{url:'http://localhost/',runScripts:'outside-only',pretendToBeVisual:true});
 const w=dom.window,stats={clears:0,resizes:0,errors:[]};w.addEventListener('error',e=>stats.errors.push(e.error?.message||e.message));
 w.matchMedia=()=>({matches:true});w.performance.getEntriesByType=()=>[];
 w.HTMLElement.prototype.scrollIntoView=()=>{}; // jsdom has no layout/scroll implementation.
 w.ResizeObserver=class{constructor(cb){this.cb=cb;}observe(target){queueMicrotask(()=>this.cb([{target,contentRect:{width:640,height:320}}]));}};
 w.IntersectionObserver=class{constructor(cb){this.cb=cb;}observe(target){queueMicrotask(()=>this.cb([{target,isIntersecting:true}]));}};
 w.HTMLCanvasElement.prototype.setPointerCapture=()=>{};
 w.HTMLCanvasElement.prototype.getContext=()=>new Proxy({clearRect(){stats.clears++;}},{get:(target,key)=>target[key]||(()=>{})});
 for(const prop of ['width','height']){const descriptor=Object.getOwnPropertyDescriptor(w.HTMLCanvasElement.prototype,prop);Object.defineProperty(w.HTMLCanvasElement.prototype,prop,{...descriptor,set(value){stats.resizes++;descriptor.set.call(this,value);}});}
 let response=results.assembly,delay=0,failure=null;
 w.fetch=async(url)=>{if(url==='/api/draft/')return {ok:true,status:200,headers:{get:()=>null},json:async()=>({saved:true})};await wait(delay);if(failure)throw failure;return {ok:true,status:200,headers:{get:()=> 'app;dur=2.50'},json:async()=>JSON.parse(JSON.stringify(response))};};
 for(const file of ['performance.js','app.js','model.js'])w.eval(fs.readFileSync(path.join(root,'core/static/core/js',file),'utf8'));
 return {dom,w,stats,result(value){response=value;},delay(value){delay=value;},fail(error){failure=error;}};
}
async function completed(p){for(let i=0;i<50&&p.w.document.querySelector('#run-code').disabled;i++)await wait(10);assert(!p.w.document.querySelector('#run-code').disabled,'Run stayed disabled.');}
(async()=>{
 const auth=page('register');try{const d=auth.w.document,b=d.querySelector('[data-target="id_password"]');b.click();assert.equal(d.querySelector('#id_password').type,'text');assert.equal(b.getAttribute('aria-pressed'),'true');assert.equal(d.querySelector('#id_confirm_password').type,'password');b.click();assert.equal(d.querySelector('#id_password').type,'password');assert.deepEqual(auth.stats.errors,[]);}finally{auth.w.close();}
 const p=page('lesson');try{
  const d=p.w.document;
  const editor=d.querySelector('#code-editor'),original=editor.value,restore=d.querySelector('#restore-example');
  const example=d.querySelector('[data-load-example]');
  editor.value='li a0,123\nli a7,1\necall';editor.dispatchEvent(new p.w.Event('input'));
  example.click();assert.equal(editor.value,example.closest('.code-example').querySelector('code').textContent);assert.equal(restore.hidden,false);
  assert.equal(d.querySelector('#run-status').textContent,'IDLE','Loading a program must not execute it.');
  restore.click();assert.equal(editor.value,'li a0,123\nli a7,1\necall');assert.equal(restore.hidden,true);
  editor.value=original;editor.dispatchEvent(new p.w.Event('input'));
  p.delay(120);d.querySelector('#run-code').click();assert.equal(d.querySelector('#run-status').textContent,'RUNNING');assert(d.querySelector('#run-code').disabled);await completed(p);assert.equal(d.querySelector('#run-status').textContent,'COMPLETED');
  for(const name of ['state','trace','encoding'])assert.equal(d.querySelector('#result-'+name).childElementCount,0);
  d.querySelector('[data-result="trace"]').click();assert.equal(d.querySelectorAll('#result-trace tbody tr').length,200);
  const first=d.querySelector('#result-trace table');d.querySelector('[data-result="console"]').click();d.querySelector('[data-result="trace"]').click();assert.equal(d.querySelector('#result-trace table'),first);
  p.result({...results.assembly,trace:[{pc:0,instruction:'changed'}]});d.querySelector('#run-code').click();await completed(p);assert.equal(d.querySelectorAll('#result-trace tbody tr').length,1);assert.match(d.querySelector('#result-trace').textContent,/changed/);
  d.querySelector('[data-result="encoding"]').click();assert(d.querySelectorAll('#result-encoding tbody tr').length>0);await wait(45);
  const snapshot=p.w.bareMetalPerformance.snapshot();assert(snapshot.samples.some(s=>s.kind==='run_result'));assert(snapshot.samples.some(s=>s.kind==='request'&&s.server_ms===2.5));assert(!JSON.stringify(snapshot).includes('mmio_write'));
  d.querySelector('#reset-code').click();assert(!d.querySelector('#result-trace table'));
  p.fail(Object.assign(new Error('Timed out'),{name:'AbortError'}));p.delay(0);d.querySelector('#run-code').click();await completed(p);assert.equal(d.querySelector('#run-status').textContent,'REQUEST ERROR');assert.match(d.querySelector('#output').textContent,/took too long/);assert.deepEqual(p.stats.errors,[]);
 }finally{p.w.close();}
 const model=page('lab');try{
  const d=model.w.document;await wait(45);const resizes=model.stats.resizes,clears=model.stats.clears;
  const asm=d.querySelector('[data-load-example][data-engine="assembly"]'),c=d.querySelector('[data-load-example][data-engine="c"]');
  assert.equal(asm.disabled,true);assert.equal(c.disabled,false);const source=d.querySelector('#code-editor').value;
  asm.click();assert.equal(d.querySelector('#code-editor').value,source);
  c.click();assert.equal(d.querySelector('#code-editor').value,c.closest('.code-example').querySelector('code').textContent);
  d.querySelector('#restore-example').click();assert.equal(d.querySelector('#code-editor').value,source);
  for(let i=0;i<40;i++)d.querySelector('[data-model-action="left"]').click();await wait(35);assert.equal(model.stats.resizes,resizes);assert.equal(model.stats.clears,clears+1);
  model.result(results.ram);d.querySelector('#run-code').click();await completed(model);assert.equal(d.querySelector('[data-component="ram"]').getAttribute('aria-pressed'),'true');assert.equal(d.querySelector('#run-status').textContent,'CHECKS PASSED');d.querySelector('[data-result="state"]').click();assert.match(d.querySelector('#result-state').textContent,/COMPONENT TELEMETRY/);assert.deepEqual(model.stats.errors,[]);
 }finally{model.w.close();}
 const dashboard=page('dashboard');try{await wait(100);const resizes=dashboard.stats.resizes;await wait(100);assert.equal(dashboard.stats.resizes,resizes);assert.deepEqual(dashboard.stats.errors,[]);}finally{dashboard.w.close();}
 console.log('DOM PASS: example load/restore, engine matching, no execution on load, password eyes, pending status, lazy 200-row trace/state/encoding, result refresh, tab reuse, reset, timeout recovery, diagnostics, RAM telemetry, batched draws and buffer reuse. No browser/layout/paint claim.');
})().catch(error=>{console.error(error);process.exitCode=1;});
