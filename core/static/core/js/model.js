'use strict';
(() => {
  const parts={
    pc:{cpu:['CPU','Executes the instruction stream. Clock values here are illustrative.'],ram:['RAM','Working storage with a virtual capacity and parity profile.'],storage:['Storage','A block-device interface below files and boot images.'],io:['I/O','The board connections between external devices and the system.']},
    server:{cpu:['Compute','Finite workers and a bounded intake queue.'],ram:['Memory','The working data each request depends on.'],storage:['Storage','Persistent data belongs behind a separate device contract.'],network:['Network','A virtual MTU and connection-capacity profile.'],power:['Power','Conceptual power supply; no electrical measurements are modelled.']},
    'data-center':{racks:['Racks','Virtual nodes and a requested replication policy.'],network:['Fabric','Communication links between conceptual racks.'],cooling:['Cooling','Illustrative heat-load and removal budgets.'],power:['Power','Conceptual supply and distribution.']},
    supercomputer:{cpu:['Compute nodes','A virtual allocation of nodes and workers.'],network:['Interconnect','A requested message and lane profile; no measured traffic.'],ram:['Memory','Conceptual local working storage across the nodes.']},
    satellite:{cpu:['Onboard computer','Packages a virtual telemetry sample stream.'],solar:['Solar arrays','Conceptual power-generation surfaces.'],antenna:['Antenna','A parity exercise at the communication path.'],payload:['Payload','The instruments a real mission would specify.']},
    quantum:{qpu:['Qubit model','An exact ideal two-qubit state calculation.'],control:['Control','A gate request, without physical pulses or calibration.'],chamber:['Cryostat','Conceptual geometry; no materials or temperature simulation.']}
  };
  function geometry(system){const boxes=[];const b=(x,y,z,w,h,d,id,kind='')=>boxes.push({x,y,z,w,h,d,id,kind});const rings=[];
    if(system==='pc'){
      b(0,-.8,0,6,.15,4,'io','board');b(-.8,-.42,0,1.4,.65,1.35,'cpu','cpu');
      for(let i=0;i<3;i++){b(1.2+i*.38,-.18,-.1,.18,1.1,2.45,'ram','ram');for(let j=0;j<5;j++)b(1.16+i*.38,-.1,-1+j*.48,.08,.38,.27,'ram');}
      b(-1.4,-.57,1.35,2.15,.28,.64,'storage','drive');b(-2.6,-.35,-.1,.45,.6,1.9,'io');
      for(let i=0;i<5;i++)b(-.8+i*.38,-.6,-1.7,.18,.16,.18,'io');
    }else if(system==='server'){
      b(0,-.7,0,6.1,.2,3.4,'power','board');b(0,-.45,-1.45,6,.6,.16,'network');
      for(let i=0;i<2;i++)b(-.7+i*1.6,-.36,-.1,1.2,.5,1.2,'cpu','cpu');
      for(let i=0;i<4;i++)b(-1.7+i*.45,-.2,-.45,.12,.7,1.8,'ram','ram');
      for(let i=0;i<3;i++)b(-1.7+i*1.15,-.35,1.05,1,.45,.8,'storage','drive');b(2.3,-.13,0,.8,1,2.6,'power');
    }else if(system==='data-center'){
      b(0,-1.8,0,7,.12,4.7,'power','board');for(let row=0;row<2;row++)for(let i=0;i<3;i++)b(-2.2+i*1.85,-.1,-1.2+row*2.3,1.12,3.3,1.15,'racks','rack');
      b(3,-.4,0,.8,2.7,2.3,'cooling','cooling');b(0,-1.6,2.3,4.8,.24,.28,'network','drive');
    }else if(system==='supercomputer'){
      b(0,-1.45,0,6,.12,4,'network','board');for(let row=0;row<2;row++)for(let i=0;i<4;i++){b(-2.15+i*1.4,-.2,-.9+row*1.7,1.05,2.3,1.2,'cpu','rack');b(-2.15+i*1.4,1.06,-.9+row*1.7,.85,.18,.95,'ram','ram');}
      b(0,-1.16,2,5,.3,.3,'network','drive');
    }else if(system==='satellite'){
      b(0,0,0,1.65,1.7,1.5,'cpu','cpu');for(let side of [-1,1]){b(side*2.85,.05,0,3.5,.1,2.1,'solar','solar');b(side*1.4,.05,0,1.2,.18,.15,'solar');}
      b(0,1.2,0,.8,.6,.8,'payload');b(0,.9,.95,.2,.8,.2,'antenna');rings.push({x:0,y:1.25,z:1.15,r:.75,id:'antenna',vertical:true});
    }else if(system==='quantum'){
      b(0,-1.5,0,3.1,.2,3.1,'chamber','board');for(let i=0;i<5;i++){const y=-1+i*.7,r=1.45-i*.18;rings.push({x:0,y,z:0,r,id:'chamber'});b(0,y,0,r*1.45,.12,r*1.45,'chamber');}
      b(0,-1.15,0,.5,.25,.5,'qpu','cpu');for(let side of [-1,1])b(side*1.35,-.15,0,.12,2.7,.12,'chamber');b(2.3,-.2,0,1.1,2.6,1.5,'control','rack');
    }
    return {boxes,rings};
  }
  class Model{
    constructor(canvas){this.canvas=canvas;this.ctx=canvas.getContext('2d');this.system=canvas.dataset.system||'pc';this.parts=parts[this.system]||parts.pc;this.scene=geometry(this.system);this.yaw=-.55;this.pitch=.45;this.zoom=1;this.selected=canvas.dataset.selected||Object.keys(this.parts)[0];this.telemetry=null;this.panel=canvas.closest('.model-panel');this.drag=null;this.moved=false;
      this.makeButtons();new ResizeObserver(()=>this.draw()).observe(canvas);canvas.addEventListener('pointerdown',e=>{this.drag={x:e.clientX,y:e.clientY};this.moved=false;canvas.setPointerCapture(e.pointerId);});
      canvas.addEventListener('pointermove',e=>{if(!this.drag)return;const dx=e.clientX-this.drag.x,dy=e.clientY-this.drag.y;this.moved=this.moved||Math.abs(dx)+Math.abs(dy)>2;this.yaw+=dx*.008;this.pitch=Math.max(-.15,Math.min(1.1,this.pitch+dy*.005));this.drag={x:e.clientX,y:e.clientY};this.draw();});
      canvas.addEventListener('pointerup',e=>{if(!this.moved){const rect=canvas.getBoundingClientRect();this.pick(e.clientX-rect.left,e.clientY-rect.top);}this.drag=null;});canvas.addEventListener('pointercancel',()=>this.drag=null);
      canvas.addEventListener('wheel',e=>{e.preventDefault();this.zoom=Math.max(.6,Math.min(1.75,this.zoom+(e.deltaY<0?.08:-.08)));this.draw();},{passive:false});
      canvas.addEventListener('keydown',e=>{if(['ArrowLeft','ArrowRight','ArrowUp','ArrowDown','+','-'].includes(e.key)){e.preventDefault();if(e.key==='ArrowLeft')this.yaw-=.15;if(e.key==='ArrowRight')this.yaw+=.15;if(e.key==='ArrowUp')this.pitch=Math.min(1.1,this.pitch+.1);if(e.key==='ArrowDown')this.pitch=Math.max(-.15,this.pitch-.1);if(e.key==='+')this.zoom=Math.min(1.75,this.zoom+.1);if(e.key==='-')this.zoom=Math.max(.6,this.zoom-.1);this.draw();}});
      this.panel?.querySelectorAll('[data-model-action]').forEach(button=>button.addEventListener('click',()=>{const a=button.dataset.modelAction;if(a==='left')this.yaw-=.2;if(a==='right')this.yaw+=.2;if(a==='in')this.zoom=Math.min(1.75,this.zoom+.12);if(a==='out')this.zoom=Math.max(.6,this.zoom-.12);if(a==='reset'){this.yaw=-.55;this.pitch=.45;this.zoom=1;}this.draw();}));
      document.addEventListener('baremetal:state',e=>{if(!this.panel)return;this.telemetry=e.detail;this.select(e.detail.component);});document.addEventListener('baremetal:reset',()=>{this.telemetry=null;this.draw();});this.select(this.selected);this.draw();
    }
    makeButtons(){const holder=this.panel?.querySelector('.component-buttons');if(!holder)return;for(const [key,[name]] of Object.entries(this.parts)){const button=document.createElement('button');button.type='button';button.textContent=name;button.dataset.component=key;button.setAttribute('aria-pressed',String(key===this.selected));button.addEventListener('click',()=>this.select(key,true));holder.append(button);}}
    select(key,navigate=false){if(!this.parts[key])return;this.selected=key;if(this.panel){this.panel.querySelector('.component-name').textContent=this.parts[key][0];this.panel.querySelector('.component-description').textContent=this.parts[key][1];this.panel.querySelectorAll('[data-component]').forEach(b=>{const active=b.dataset.component===key;b.classList.toggle('active',active);b.setAttribute('aria-pressed',String(active));});}
      document.querySelectorAll('[data-component-link]').forEach(a=>a.classList.toggle('component-highlight',a.dataset.componentLink===key));this.draw();
      if(navigate){const routesNode=document.getElementById('component-routes');const routes=routesNode?JSON.parse(routesNode.textContent):null;
        if(routes?.[key]&&key!==this.canvas.dataset.selected){const engine=document.querySelector('.terminal-panel')?.dataset.engine;window.location.href=routes[key]+(engine==='assembly'?'?lang=assembly':'');}
        else if(document.querySelector('.hardware-detail-grid'))document.querySelector(`[data-component-link="${key}"]`)?.click();
      }}
    project(x,y,z){const cy=Math.cos(this.yaw),sy=Math.sin(this.yaw),cp=Math.cos(this.pitch),sp=Math.sin(this.pitch);const rx=x*cy+z*sy,rz=-x*sy+z*cy,ry=y*cp-rz*sp,depth=y*sp+rz*cp;return [this.width/2+rx*this.scale,this.height*.54-ry*this.scale,depth];}
    path(points){const c=this.ctx;c.beginPath();points.forEach((p,i)=>i?c.lineTo(p[0],p[1]):c.moveTo(p[0],p[1]));c.closePath();}
    draw(){const rect=this.canvas.getBoundingClientRect();this.width=rect.width;this.height=rect.height;if(!this.width||!this.height)return;const ratio=Math.min(devicePixelRatio||1,2),c=this.ctx;this.canvas.width=this.width*ratio;this.canvas.height=this.height*ratio;c.scale(ratio,ratio);c.clearRect(0,0,this.width,this.height);this.scale=Math.min(this.width/10,this.height/6.6)*this.zoom;
      // Ground reference: it provides depth without implying an engineering drawing.
      c.strokeStyle='#29432c';c.lineWidth=.6;c.globalAlpha=.35;for(let i=-5;i<=5;i++){const a=this.project(i,-1.9,-5),b=this.project(i,-1.9,5);c.beginPath();c.moveTo(a[0],a[1]);c.lineTo(b[0],b[1]);c.stroke();const d=this.project(-5,-1.9,i),e=this.project(5,-1.9,i);c.beginPath();c.moveTo(d[0],d[1]);c.lineTo(e[0],e[1]);c.stroke();}c.globalAlpha=1;
      const faces=[],bounds=[];const indexes=[[0,1,2,3],[4,5,6,7],[0,1,5,4],[3,2,6,7],[0,3,7,4],[1,2,6,5]];
      for(const box of this.scene.boxes){const {x,y,z,w,h,d}=box;const vertices=[[-1,-1,-1],[1,-1,-1],[1,1,-1],[-1,1,-1],[-1,-1,1],[1,-1,1],[1,1,1],[-1,1,1]].map(([a,b,f])=>this.project(x+a*w/2,y+b*h/2,z+f*d/2));
        const xs=vertices.map(p=>p[0]),ys=vertices.map(p=>p[1]);bounds.push({id:box.id,x:Math.min(...xs),y:Math.min(...ys),w:Math.max(...xs)-Math.min(...xs),h:Math.max(...ys)-Math.min(...ys),depth:vertices.reduce((s,p)=>s+p[2],0)/8});
        indexes.forEach((ix,n)=>{const points=ix.map(i=>vertices[i]);faces.push({points,depth:points.reduce((s,p)=>s+p[2],0)/4,id:box.id,n});});
      }
      faces.sort((a,b)=>a.depth-b.depth);for(const face of faces){this.path(face.points);const chosen=face.id===this.selected;c.fillStyle=chosen?['#365435aa','#213d28e0','#304b31dd','#223c27dd','#29452bdd','#3d6038dd'][face.n]:['#18321eaa','#0a190edc','#142b1bdf','#102618df','#1b3220df','#28412add'][face.n];c.fill();c.strokeStyle=chosen?'#a0dc84':'#557d5b';c.lineWidth=chosen?1.15:.7;c.stroke();}
      for(const box of this.scene.boxes){if(!['rack','solar','cpu','ram','drive'].includes(box.kind))continue;c.strokeStyle=box.id===this.selected?'#91c775':'#496c4d';c.lineWidth=.7;
        if(box.kind==='rack'){for(let i=1;i<7;i++){const y=box.y-box.h/2+box.h*i/7,a=this.project(box.x-box.w*.42,y,box.z+box.d/2+.01),b=this.project(box.x+box.w*.42,y,box.z+box.d/2+.01);c.beginPath();c.moveTo(a[0],a[1]);c.lineTo(b[0],b[1]);c.stroke();const led=this.project(box.x+box.w*.3,y+.05,box.z+box.d/2+.02);c.fillStyle='#80c465';c.fillRect(led[0]-1,led[1]-1,2,2);}}
        if(box.kind==='solar'||box.kind==='board'){for(let i=1;i<6;i++){const a=this.project(box.x-box.w/2+box.w*i/6,box.y+box.h/2+.01,box.z-box.d/2),b=this.project(box.x-box.w/2+box.w*i/6,box.y+box.h/2+.01,box.z+box.d/2);c.beginPath();c.moveTo(a[0],a[1]);c.lineTo(b[0],b[1]);c.stroke();}}
        if(box.kind==='cpu'){const a=this.project(box.x,box.y+box.h/2+.02,box.z);c.font='8px monospace';c.fillStyle='#b2d99b';c.textAlign='center';c.fillText('CORE',a[0],a[1]);}
      }
      for(const ring of this.scene.rings){c.beginPath();for(let i=0;i<=48;i++){const t=i/48*Math.PI*2;const p=this.project(ring.x+Math.cos(t)*ring.r,ring.y+(ring.vertical?Math.sin(t)*ring.r:0),ring.z+(ring.vertical?0:Math.sin(t)*ring.r));i?c.lineTo(p[0],p[1]):c.moveTo(p[0],p[1]);}c.strokeStyle=ring.id===this.selected?'#a0dc84':'#648269';c.lineWidth=1;c.stroke();}
      this.bounds=bounds.sort((a,b)=>b.depth-a.depth);const selected=this.scene.boxes.filter(b=>b.id===this.selected).sort((a,b)=>b.h-a.h)[0];
      if(selected){const p=this.project(selected.x,selected.y+selected.h/2,selected.z);c.setLineDash([2,3]);c.strokeStyle='#99c685';c.beginPath();c.moveTo(p[0],p[1]-2);c.lineTo(p[0]+20,p[1]-22);c.lineTo(p[0]+65,p[1]-22);c.stroke();c.setLineDash([]);c.font='8px monospace';c.textAlign='left';c.fillStyle='#b4e59e';c.fillText(this.parts[this.selected][0].toUpperCase(),p[0]+22,p[1]-27);}
      c.font='7px monospace';c.textAlign='left';c.fillStyle='#5b8161';c.fillText('CONCEPTUAL GEOMETRY / NOT TO SCALE',12,this.height-12);c.textAlign='right';c.fillStyle='#82a875';c.fillText(this.telemetry?'LAST RUN STATE':'VIRTUAL COMPONENT MODEL',this.width-12,this.height-12);
      if(this.telemetry){c.textAlign='left';c.font='8px monospace';c.fillStyle='#b2dba0';c.fillText(`REGISTERS  ${this.telemetry.values.join(' / ')}`,12,19);}
    }
    pick(x,y){const item=this.bounds?.find(b=>x>=b.x&&x<=b.x+b.w&&y>=b.y&&y<=b.y+b.h);if(item)this.select(item.id,true);}
  }
  document.querySelectorAll('.hardware-model').forEach(canvas=>new Model(canvas));
})();
