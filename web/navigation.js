// Task navigation changes presentation only; financial state stays in its owner modules.
const titles={home:'검토 자료',work:'재무 비교',analysis:'문서 분석',search:'근거 검색',review:'검증 기록'};
const stages={compare:'comparison-panel',evidence:'source-panel',notes:'notes-panel'};
export function showStage(name,{focus=false}={}) {
 if(!Object.hasOwn(stages,name))name='compare';
 for(const [key,id] of Object.entries(stages))document.getElementById(id).hidden=key!==name;
 document.querySelectorAll('[data-stage]').forEach(b=>{
  const active=b.dataset.stage===name;
  b.setAttribute('aria-selected',String(active));b.tabIndex=active?0:-1;
  if(active&&focus)b.focus();
 });
}
export function view(name,{history=true,focus=true}={}) {
 if(!Object.hasOwn(titles,name))name='work';
 document.querySelectorAll('.view').forEach(v=>v.hidden=v.id!==name);
 document.body.dataset.view=name;
 if(name==='work')showStage('compare');
 document.querySelector('#route-label').textContent=titles[name];
 document.querySelectorAll('[data-view]').forEach(b=>{
  const active=b.dataset.view===name;b.classList.toggle('active',active);
  if(active)b.setAttribute('aria-current','page');else b.removeAttribute('aria-current');
 });
 if(history&&location.hash!=='#'+name)window.history.pushState(null,'','#'+name);
 if(focus)document.querySelector(`#${name} h1`)?.focus({preventScroll:true});
 window.scrollTo(0,0);
}
export function mountNavigation() {
 document.querySelector('.skip-link').onclick=e=>{e.preventDefault();document.querySelector('#main').focus();};
 document.querySelectorAll('[data-view]').forEach(b=>b.onclick=()=>view(b.dataset.view));
 document.querySelectorAll('[data-stage]').forEach(b=>{
  b.onclick=()=>showStage(b.dataset.stage);
  b.onkeydown=e=>{
   const keys=Object.keys(stages),i=keys.indexOf(b.dataset.stage);
   let next;
   if(e.key==='ArrowRight')next=(i+1)%keys.length;
   if(e.key==='ArrowLeft')next=(i+keys.length-1)%keys.length;
   if(e.key==='Home')next=0;if(e.key==='End')next=keys.length-1;
   if(next!==undefined){e.preventDefault();showStage(keys[next],{focus:true});}
  };
 });
 document.querySelectorAll('[data-return-compare]').forEach(b=>b.onclick=()=>{
  showStage('compare');const title=document.querySelector('#sheet-title');title.focus();title.scrollIntoView({block:'start'});
 });
 document.querySelectorAll('[data-start]').forEach(b=>b.onclick=()=>{
  if(b.dataset.start==='samsung'){showStage('compare');view('work');return;}
  const picker=document.querySelector('#source-document');
  const id=b.dataset.start==='apple'?'apple-2024-10k':'skh2024annual-in-2025oc';
  if(picker.value!==id){picker.value=id;picker.dispatchEvent(new Event('change'));}
  if(b.dataset.start==='skhynix')document.querySelector('#source-calculator').open=true;
  view('analysis');
 });
 window.addEventListener('hashchange',()=>view(location.hash.slice(1),{history:false}));
 window.addEventListener('popstate',()=>view(location.hash.slice(1),{history:false}));
 view(location.hash.slice(1),{history:false,focus:false});
}
