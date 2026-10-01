'use strict';
(() => {
  const q = (s, root = document) => root.querySelector(s);
  const qa = (s, root = document) => [...root.querySelectorAll(s)];
  const el = (tag, text, cls) => {const n=document.createElement(tag); if(text!==undefined)n.textContent=String(text);if(cls)n.className=cls;return n;};
  const csrf=()=>q('.csrf-source input')?.value || '';
  async function request(url,data){
    const response=await fetch(url,{method:'POST',headers:{'Content-Type':'application/json','X-CSRFToken':csrf()},body:JSON.stringify(data),credentials:'same-origin'});
    let result;try{result=await response.json();}catch{throw new Error('The server returned an unreadable response. Refresh or sign in again.');}
    if(!response.ok || result.error)throw new Error(result.error || `Request failed (${response.status}).`);
    return result;
  }
  qa('.password-toggle').forEach(button=>button.addEventListener('click',()=>{
    const input=document.getElementById(button.dataset.target),show=input.type==='password';input.type=show?'text':'password';
    button.setAttribute('aria-pressed',String(show));button.setAttribute('aria-label',`${show?'Hide':'Show'} ${q(`label[for="${input.id}"]`).textContent.toLowerCase()}`);
  }));
  q('.menu-toggle')?.addEventListener('click',()=>{document.body.classList.toggle('menu-open');q('.menu-toggle').setAttribute('aria-expanded',String(document.body.classList.contains('menu-open')));});
  document.addEventListener('click',e=>{if(document.body.classList.contains('menu-open')&&!e.target.closest('.sidebar,.menu-toggle')){document.body.classList.remove('menu-open');q('.menu-toggle').setAttribute('aria-expanded','false');}});
  const clock=()=>qa('.clock').forEach(n=>n.textContent=new Date().toLocaleTimeString([], {hour:'2-digit',minute:'2-digit',hour12:false}));clock();if(q('.clock'))setInterval(clock,30000);
  function tabs(selector,attr,prefix){qa(selector).forEach(button=>button.addEventListener('click',()=>{
    qa(selector).forEach(n=>{const active=n===button;n.classList.toggle('active',active);n.setAttribute('aria-selected',String(active));q(`#${prefix}${n.dataset[attr]}`).hidden=!active;});
  }));}
  tabs('[data-doc]','doc','doc-');tabs('[data-result]','result','result-');
  q('#playground-language')?.addEventListener('change',e=>{window.location.href=`/playground/?lang=${encodeURIComponent(e.target.value)}`;});
  function table(headers,rows){const wrap=el('div',undefined,'table-scroll'),t=el('table',undefined,'data-table'),thead=el('thead'),tr=el('tr');
    headers.forEach(h=>tr.append(el('th',h)));thead.append(tr);t.append(thead);const body=el('tbody');
    rows.forEach(row=>{const r=el('tr');row.forEach(v=>r.append(el('td',typeof v==='object'?JSON.stringify(v):v)));body.append(r);});t.append(body);wrap.append(t);return wrap;
  }
  function bootScreen(r){if(!q('#boot-screen'))return;q('#boot-screen').textContent=r.screen ?? r.output ?? '';q('#boot-screen-status').textContent='BOOTED / HALTED';}
  function showResult(r){
    const failed=Boolean(r.errors?.length);q('#output').textContent=failed?r.errors.join('\n'):r.output || '(program completed without console output)';
    const status=q('#run-status');status.textContent=failed?'ERROR':r.passed?'CHECKS PASSED':r.checks?.length?'CHECK TARGETS':'COMPLETED';status.className='run-status '+(failed?'error':'ok');
    q('#run-metric').textContent=`${r.steps ?? 0} interpreter steps`;
    q('#checks').replaceChildren();(r.checks||[]).forEach(c=>{const item=el('div',`${c.passed?'✓':'×'} ${c.name}`,`check-item ${c.passed?'':'fail'}`);
      if(!c.passed&&'expected'in c)item.append(el('small',`Expected ${JSON.stringify(c.expected)} · Actual ${JSON.stringify(c.actual)}`));q('#checks').append(item);});
    const state=q('#result-state');state.replaceChildren();const s=r.state||{};
    if(!Object.keys(s).length)state.append(el('p','No state is available for this result.','muted'));
    for(const [key,value] of Object.entries(s)){
      state.append(el('h4',key.replaceAll('_',' ').toUpperCase()));
      if(Array.isArray(value)&&value.length&&typeof value[0]==='object'){const headers=Object.keys(value[0]);state.append(table(headers,value.map(row=>headers.map(h=>row[h]))));}
      else if(value&&typeof value==='object')state.append(table(['Name / address','Value'],Object.entries(value).map(([k,v])=>[key==='mmio'?`0x${Number(k).toString(16).toUpperCase()}`:k,v])));
      else state.append(el('pre',value));
    }
    if(r.model){state.append(el('h4','COMPONENT TELEMETRY'));const entries=Object.entries(r.model).filter(([k])=>!['component','values'].includes(k));state.append(table(['Property','Value'],entries));document.dispatchEvent(new CustomEvent('baremetal:state',{detail:r.model}));}
    const trace=q('#result-trace');trace.replaceChildren();const rows=r.trace||[];
    if(rows.length&&typeof rows[0]==='object'){const headers=Object.keys(rows[0]);trace.append(table(headers,rows.map(row=>headers.map(h=>row[h]))));}
    else trace.append(el('pre',rows.join('\n')||'No trace recorded.'));
    if(rows.length===200)trace.append(el('p','The trace view retains the first 200 records.','muted'));
    const enc=q('#result-encoding');enc.replaceChildren();
    if(r.listing?.length)enc.append(table(['PC','Word','Assembly','Line'],r.listing.map(row=>[`0x${row.pc.toString(16)}`,row.hex,row.assembly,row.line])));
    if(r.image_hex){enc.append(el('h4','IMAGE BYTES / LITTLE-ENDIAN WHERE APPLICABLE'));const lines=[];
      for(let i=0;i<r.image_hex.length;i+=32)lines.push(`${(i/2).toString(16).padStart(4,'0')}  ${r.image_hex.slice(i,i+32).match(/.{1,2}/g).join(' ')}`);enc.append(el('pre',lines.join('\n')));}
    if(!enc.childNodes.length)enc.append(el('p','This interpreter does not emit native instruction bytes.','muted'));
    if(!failed)bootScreen(r);
  }
  const terminal=q('.terminal-panel'),editor=q('#code-editor');
  if(editor){
    const ext={c:'c',assembly:'s',machine:'hex',rust:'rs',verilog:'v',boot:'asm'};q('#code-file').textContent=`${terminal.dataset.engine==='boot'?'boot':'main'}.${ext[terminal.dataset.engine]}`;
    const key=`baremetal:${document.body.dataset.user||'guest'}:${terminal.dataset.draft}`;const starter=JSON.parse(q('#starter-code').textContent);let saveTimer,pending=false;
    // Local backup is used only when an earlier failed autosave was explicitly marked pending.
    try{const local=JSON.parse(localStorage.getItem(key)||'null');if(local?.pending){editor.value=local.code;q('#draft-status').textContent='Recovered local draft';pending=true;}}catch{}
    function position(){const before=editor.value.slice(0,editor.selectionStart),lines=before.split('\n');q('#editor-position').textContent=`Ln ${lines.length}, Col ${lines.at(-1).length+1}`;}
    function lines(){q('#line-numbers').textContent=Array.from({length:editor.value.split('\n').length},(_,i)=>i+1).join('\n');position();}
    async function save(){
      const code=editor.value;try{await request('/api/draft/',{key:terminal.dataset.draft,code});
        if(code===editor.value){pending=false;q('#draft-status').textContent='Saved';try{localStorage.setItem(key,JSON.stringify({code,pending:false}));}catch{}}
      }catch{q('#draft-status').textContent='Saved locally · offline';}
    }
    function changed(){pending=true;lines();q('#draft-status').textContent='Unsaved changes';try{localStorage.setItem(key,JSON.stringify({code:editor.value,pending:true}));}catch{}clearTimeout(saveTimer);saveTimer=setTimeout(save,900);}
    editor.addEventListener('input',changed);editor.addEventListener('click',position);editor.addEventListener('keyup',position);editor.addEventListener('scroll',()=>q('#line-numbers').scrollTop=editor.scrollTop);
    editor.addEventListener('keydown',e=>{if(e.key==='Tab'){e.preventDefault();const a=editor.selectionStart,z=editor.selectionEnd;editor.setRangeText('    ',a,z,'end');changed();}if((e.ctrlKey||e.metaKey)&&e.key==='Enter'){e.preventDefault();q('#run-code').click();}});
    q('#reset-code').addEventListener('click',()=>{editor.value=starter;changed();q('#run-status').textContent='RESET';q('#run-status').className='run-status';q('#output').textContent='Starter restored. Run to inspect it.';q('#checks').replaceChildren();document.dispatchEvent(new Event('baremetal:reset'));});
    q('#run-code').addEventListener('click',async()=>{
      const button=q('#run-code');button.disabled=true;q('#run-status').textContent='RUNNING';q('#run-status').className='run-status';
      try{const r=await request('/api/execute/',{code:editor.value,language:terminal.dataset.engine,context_kind:terminal.dataset.contextKind,context_id:terminal.dataset.contextId||null});showResult(r);}
      catch(e){q('#output').textContent=e.message;q('#checks').replaceChildren();q('#run-status').textContent='REQUEST ERROR';q('#run-status').className='run-status error';if(q('#boot-screen-status'))q('#boot-screen-status').textContent='BOOT FAILED';}
      finally{button.disabled=false;}
    });
    window.addEventListener('pagehide',()=>{if(pending)fetch('/api/draft/',{method:'POST',headers:{'Content-Type':'application/json','X-CSRFToken':csrf()},body:JSON.stringify({key:terminal.dataset.draft,code:editor.value}),keepalive:true}).catch(()=>{});});
    lines();if(pending)saveTimer=setTimeout(save,900);
  }
  q('#save-boot')?.addEventListener('click',async()=>{const button=q('#save-boot');button.disabled=true;
    try{const r=await request('/api/boot/save/',{code:editor.value,name:q('#project-name').value,project_id:button.dataset.projectId||null});q('#boot-save-status').textContent='Image saved. Opening your project…';window.location.href=r.url;}
    catch(e){q('#boot-save-status').textContent=e.message;}
    finally{button.disabled=false;}
  });
  q('#boot-saved')?.addEventListener('click',async()=>{const button=q('#boot-saved');button.disabled=true;
    try{showResult(await request(button.dataset.url,{}));}catch(e){q('#boot-screen').textContent=e.message;q('#boot-screen-status').textContent='BOOT FAILED';}finally{button.disabled=false;}
  });
  qa('form[action$="/delete/"]').forEach(form=>form.addEventListener('submit',e=>{if(!confirm('Delete this saved boot image?'))e.preventDefault();}));
  const pixel=q('.pixel-signal');
  if(pixel){const ctx=pixel.getContext('2d');const reduce=matchMedia('(prefers-reduced-motion: reduce)').matches;let frame=0;
    function draw(){const box=pixel.getBoundingClientRect(),ratio=devicePixelRatio||1;pixel.width=box.width*ratio;pixel.height=box.height*ratio;ctx.scale(ratio,ratio);ctx.clearRect(0,0,box.width,box.height);
      const unit=7,columns=Math.floor(box.width/unit),rows=Math.floor(box.height/unit);for(let x=0;x<columns;x++){const centre=rows*.5+Math.sin(x*.2+frame*.016)*rows*.12;for(let y=0;y<rows;y++){
        const d=Math.abs(y-centre),inside=d<5+(Math.sin(x*.4+frame*.013)+1)*4;if(inside&&((x*7+y*3)%5!==0)){ctx.fillStyle=d<2?'#8ad06f':'#345b31';ctx.fillRect(x*unit,y*unit,4,4);}}}
      frame++;if(!reduce&&frame<600)requestAnimationFrame(draw);
    }draw();if(reduce)new ResizeObserver(draw).observe(pixel);
  }
})();
