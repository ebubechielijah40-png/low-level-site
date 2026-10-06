'use strict';
(() => {
  // This tab's memory only. No code, identities, or metrics are uploaded.
  const samples=[];
  const record=(kind,detail)=>{samples.push({kind,...detail});if(samples.length>100)samples.shift();};
  const afterPaint=(kind,start,callback)=>{
    if(document.hidden)return;
    // Two frames estimate a paint opportunity; this is not certified INP.
    requestAnimationFrame(()=>requestAnimationFrame(()=>{
      if(document.hidden)return;
      const ms=Math.round((performance.now()-start)*10)/10;record(kind,{ms});callback?.(ms);
    }));
  };
  document.addEventListener('baremetal:request',event=>record('request',event.detail));
  if(typeof PerformanceObserver!=='undefined'){
    for(const type of ['longtask','event']){
      if(!PerformanceObserver.supportedEntryTypes?.includes(type))continue;
      try{new PerformanceObserver(list=>{for(const entry of list.getEntries()){
        if(type==='event'&&!entry.interactionId)continue;
        record(type,{ms:entry.duration,name:entry.name,...(type==='event'?{interactionId:entry.interactionId}:{})});
      }}).observe(type==='event'?{type,buffered:true,durationThreshold:16}:{type,buffered:true});}catch{}
    }
  }
  window.bareMetalPerformance=Object.freeze({record,afterPaint,snapshot(){
    const n=performance.getEntriesByType('navigation')[0];
    return {target_ms:300,scope:'This tab only; paint timings are estimates',
      navigation:n?{ttfb_ms:n.responseStart,transfer_ms:n.responseEnd-n.responseStart,dom_ready_ms:n.domContentLoadedEventEnd}:null,
      samples:samples.map(sample=>({...sample}))};
  }});
})();
