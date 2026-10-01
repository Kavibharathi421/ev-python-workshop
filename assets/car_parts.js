// Image-space cut lines share one source image. Returning every group to (0,0)
// restores the approved picture without accumulating transform errors.
(()=>{
 const ns='http://www.w3.org/2000/svg',view=document.getElementById('photo-view');
 const photo=view.querySelector('img'),hero=document.querySelector('.hero');
 const slider=document.getElementById('photo-progress'),status=document.getElementById('photo-phase');
 const toggle=document.getElementById('photo-motion'),reduced=matchMedia('(prefers-reduced-motion: reduce)');
 const outline='M75 662 L100 612 L114 531 Q160 475 233 447 Q384 407 627 396 Q724 293 874 263 Q976 239 1122 267 Q1272 288 1390 367 L1460 361 L1542 347 Q1520 374 1484 384 Q1540 407 1548 483 L1562 635 L1558 661 L1468 667 Q1402 705 1321 670 L664 680 Q548 720 447 678 L123 685 Z';
 const parts=[
  {name:'Front wheel',shape:'<ellipse cx="566" cy="568" rx="123" ry="127"/>',offset:[-150,235],label:[566,726]},
  {name:'Rear wheel',shape:'<ellipse cx="1378" cy="566" rx="110" ry="121"/>',offset:[160,235],label:[1378,720]},
  {name:'Rear spoiler',shape:'<path d="M1360 365 L1460 352 L1555 336 L1540 377 L1475 398 L1375 393 Z"/>',offset:[240,-165],label:[1450,328]},
  {name:'Cabin & glass',shape:'<path d="M605 399 Q730 277 874 252 Q999 235 1135 264 Q1292 291 1403 397 L1200 404 L825 394 Z"/>',offset:[0,-210],label:[1000,228]},
  {name:'Door & mirror',shape:'<path d="M817 395 L1196 399 L1201 646 L829 651 L795 480 L790 353 L850 329 L900 354 L899 392 Z"/>',offset:[40,60],label:[1010,685]},
  {name:'Hood & headlights',shape:'<path d="M117 513 Q272 413 627 391 L818 390 L795 455 L697 493 L463 482 L237 532 Z"/>',offset:[-160,-145],label:[500,378]},
  {name:'Front bumper',shape:'<path d="M60 520 L446 489 L453 683 L64 701 Z"/>',offset:[-270,40],label:[205,716]},
  {name:'Side skirts',shape:'<path d="M445 647 L1320 639 L1510 637 L1580 680 L442 706 Z"/>',offset:[0,245],label:[960,718]},
  {name:'Front fender',shape:'<rect x="0" y="0" width="819" height="941"/>',offset:[-215,-10],label:[635,463]},
  {name:'Rear body',shape:'<rect x="0" y="0" width="1672" height="941"/>',offset:[250,15],label:[1390,437]}
 ];
 function node(tag,attrs,parent){const e=document.createElementNS(ns,tag);for(const [k,v] of Object.entries(attrs))e.setAttribute(k,v);parent?.appendChild(e);return e;}
 const svg=node('svg',{viewBox:'0 0 1672 941',class:'parts-svg',role:'img','aria-label':'Car exterior parts that separate and return to their original alignment'},view.querySelector('.photo-float'));
 const defs=node('defs',{},svg);node('image',{id:'parts-source',href:photo.src,width:1672,height:941},defs);
 const root=node('g',{},svg),previous=[];
 parts.forEach((p,i)=>{
  const clip=node('clipPath',{id:'part-cut-'+i,clipPathUnits:'userSpaceOnUse'},defs);clip.innerHTML=p.shape;
  const mask=node('mask',{id:'part-mask-'+i,maskUnits:'userSpaceOnUse',x:0,y:0,width:1672,height:941,style:'mask-type:luminance'},defs);
  mask.innerHTML='<path fill="white" d="'+outline+'"/><g fill="black">'+previous.join('')+'</g>';previous.push(p.shape);
  p.group=node('g',{'data-image-part':p.name},root);
  node('use',{href:'#parts-source','clip-path':'url(#part-cut-'+i+')',mask:'url(#part-mask-'+i+')'},p.group);
  p.anchor=p.label;
  p.label=node('g',{class:'image-part-label'},p.group);
 });
 parts.forEach(p=>{const [x,y]=p.anchor,width=p.name.length*12+26;node('rect',{x:x-width/2,y:y-25,width,height:34,rx:8,fill:'#102c25',stroke:'#95be77','stroke-width':1},p.label);const text=node('text',{x,y,fill:'#e3f5d5','font-size':22,'text-anchor':'middle','font-family':'Arial'},p.label);text.textContent=p.name;});
 let amount=0,from=0,target=0,elapsed=0,transitioning=false,playing=!reduced.matches,paused=false,hold=0,last=0;
 function draw(){
  const fit=1-amount*.30;
  root.setAttribute('transform',`translate(${836*(1-fit)} ${470*(1-fit)}) scale(${fit})`);
  parts.forEach(p=>{p.group.setAttribute('transform',`translate(${p.offset[0]*amount} ${p.offset[1]*amount})`);p.label.style.opacity=String(Math.max(0,(amount-.65)/.35));});
  svg.style.opacity=amount===0?'0':'1';photo.style.opacity=String(Math.max(0,1-amount*5));
  slider.value=String(Math.round(amount*100));view.dataset.explosion=amount.toFixed(4);
  status.textContent=(amount===0?'ASSEMBLED':amount===1?'PARTS SEPARATED':target>amount?'DISASSEMBLING':'REASSEMBLING')+' / 10 EXTERIOR PARTS';
 }
 function sync(){toggle.textContent=playing?'Pause tour':'Play tour';toggle.setAttribute('aria-pressed',String(playing));}
 function moveTo(value){from=amount;target=value;elapsed=0;hold=0;transitioning=true;if(reduced.matches){amount=target;transitioning=false;draw();}}
 toggle.onclick=()=>{playing=!playing;paused=!playing;sync();};
 document.getElementById('photo-explode').onclick=()=>{playing=false;paused=false;moveTo(1);sync();};
 document.getElementById('photo-assemble').onclick=()=>{playing=false;paused=false;moveTo(0);sync();};
 slider.oninput=()=>{playing=false;transitioning=false;amount=Number(slider.value)/100;target=amount;hold=0;draw();sync();};
 reduced.addEventListener('change',()=>{if(reduced.matches){playing=false;transitioning=false;sync();}});
 function frame(t){requestAnimationFrame(frame);const dt=Math.min((t-last)/1000,.05);last=t;if(paused||document.hidden||!hero.classList.contains('photo-mode'))return;
  if(transitioning){elapsed+=dt;const k=Math.min(elapsed/4,1),ease=k*k*(3-2*k);amount=from+(target-from)*ease;if(k===1){amount=target;transitioning=false;hold=0;}draw();}
  else if(playing){hold+=dt;if(hold>3)moveTo(amount<.5?1:0);}
 }
 view.onpointermove=null;view.onpointerleave();
 document.getElementById('hint').textContent='SEPARATE · EXPLORE · REASSEMBLE';
 document.addEventListener('car-view-change',e=>{if(!e.detail.model)document.getElementById('hint').textContent='SEPARATE · EXPLORE · REASSEMBLE';});
 hero.classList.add('parts-tour');draw();sync();requestAnimationFrame(frame);
})();
