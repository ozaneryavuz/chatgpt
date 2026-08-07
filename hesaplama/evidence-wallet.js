(function(root,factory){
  const api=factory(root);
  if(typeof module==='object'&&module.exports)module.exports=api;
  if(root&&typeof root==='object')root.Alo186EvidenceWallet=api;
  if(root&&root.document)api.init();
})(typeof globalThis!=='undefined'?globalThis:this,function(root){
  'use strict';

  const STORAGE_KEY='alo186:technical-evidence:v1';
  const MAX_RECORDS=12;
  const TTL_DAYS=45;
  const DAY_MS=86400000;
  const CATEGORIES=new Set(['powerbank','surge_strip','mini_ups','emergency_light','smoke_alarm','power_station','smart_plug','ev_cable']);
  const LABELS={powerbank:'Powerbank',surge_strip:'Akım korumalı grup priz',mini_ups:'Modem/ONT mini UPS',emergency_light:'Acil aydınlatma',smoke_alarm:'Duman alarmı',power_station:'Power station',smart_plug:'Akıllı priz ve enerji ölçer',ev_cable:'Type 2 EV kablosu'};
  const TOOL_ROUTES={
    powerbank:'/hesaplama/powerbank-usb-c-uygunluk/',
    surge_strip:'/hesaplama/akim-korumali-grup-priz-uygunluk/',
    mini_ups:'/hesaplama/modem-internet-yedekleme/',
    emergency_light:'/hesaplama/acil-aydinlatma-sure-uygunluk/',
    smoke_alarm:'/hesaplama/duman-alarmi-yerlesim-bakim-uygunluk/',
    power_station:'/hesaplama/power-station-kapasite-eps-uygunluk/',
    smart_plug:'/hesaplama/akilli-priz-enerji-olcer-uygunluk/',
    ev_cable:'/hesaplama/ev-sarj-kablosu-uygunluk/'
  };
  let memory=[];
  let storageAvailable=true;
  let initialized=false;

  function safePath(value){
    try{
      const raw=String(value||'').trim();
      const url=new URL(raw,'https://alo186.com');
      if(/^https?:\/\//i.test(raw)&&!['www.alo186.com','alo186.com'].includes(url.hostname.toLowerCase()))return'';
      const path=url.pathname.replace(/\/{2,}/g,'/');
      return /^\/[a-zA-Z0-9_\-/.]*$/.test(path)?path.slice(0,180):'';
    }catch(_){return'';}
  }

  function categoryFromPath(value){
    const path=safePath(value).toLowerCase();
    for(const [category,route] of Object.entries(TOOL_ROUTES))if(path===route||path.startsWith(route))return category;
    if(path.includes('powerbank'))return'powerbank';
    if(path.includes('akim-korumali-grup-priz'))return'surge_strip';
    if(path.includes('modem-internet'))return'mini_ups';
    if(path.includes('acil-aydinlatma'))return'emergency_light';
    if(path.includes('duman-alarmi'))return'smoke_alarm';
    if(path.includes('power-station'))return'power_station';
    if(path.includes('akilli-priz'))return'smart_plug';
    if(path.includes('ev-sarj-kablosu'))return'ev_cable';
    return null;
  }

  function sanitize(record,nowValue=new Date()){
    if(!record||typeof record!=='object'||!CATEGORIES.has(record.category))return null;
    const now=nowValue instanceof Date?nowValue:new Date(nowValue);
    const completed=Number.isFinite(Date.parse(record.completedAt))?new Date(record.completedAt):now;
    const expires=Number.isFinite(Date.parse(record.expiresAt))?new Date(record.expiresAt):new Date(completed.getTime()+TTL_DAYS*DAY_MS);
    const toolPath=safePath(record.toolPath||TOOL_ROUTES[record.category]);
    if(!toolPath)return null;
    return{version:1,id:String(record.id||`${record.category}_${completed.getTime().toString(36)}`).replace(/[^a-zA-Z0-9_-]/g,'').slice(0,64),category:record.category,toolPath,completedAt:completed.toISOString(),expiresAt:expires.toISOString(),source:'technical_tool'};
  }

  function read(){
    if(!storageAvailable||!root.localStorage)return prune(memory);
    try{memory=prune(JSON.parse(root.localStorage.getItem(STORAGE_KEY)||'[]'));return memory;}
    catch(_){storageAvailable=false;return prune(memory);}
  }

  function write(records){
    memory=prune(records);
    if(!storageAvailable||!root.localStorage)return memory;
    try{root.localStorage.setItem(STORAGE_KEY,JSON.stringify(memory));}
    catch(_){storageAvailable=false;}
    return memory;
  }

  function prune(records,nowValue=new Date()){
    const now=nowValue instanceof Date?nowValue:new Date(nowValue),latest=new Map();
    (Array.isArray(records)?records:[]).forEach(raw=>{const item=sanitize(raw,now);if(!item)return;const old=latest.get(item.category);if(!old||Date.parse(old.completedAt)<Date.parse(item.completedAt))latest.set(item.category,item);});
    return[...latest.values()].sort((a,b)=>Date.parse(b.completedAt)-Date.parse(a.completedAt)).slice(0,MAX_RECORDS);
  }

  function record(category,toolPath,nowValue=new Date()){
    if(!CATEGORIES.has(category))return null;
    const item=sanitize({category,toolPath:toolPath||TOOL_ROUTES[category]},nowValue);
    const records=read().filter(existing=>existing.category!==category);
    write([item,...records]);
    dispatch('alo186:evidence-updated',item);
    return item;
  }

  function get(category){return read().find(item=>item.category===category)||null;}

  function status(category,nowValue=new Date()){
    const now=nowValue instanceof Date?nowValue:new Date(nowValue),item=get(category);
    if(!item)return{state:'missing',category,label:LABELS[category]||category,toolRoute:TOOL_ROUTES[category]||'/hesaplama/',record:null,daysLeft:null};
    const daysLeft=Math.ceil((Date.parse(item.expiresAt)-now.getTime())/DAY_MS);
    const state=daysLeft<0?'expired':daysLeft<=7?'expiring':'current';
    return{state,category,label:LABELS[category],toolRoute:TOOL_ROUTES[category],record:item,daysLeft};
  }

  function list(nowValue=new Date()){return read().map(item=>status(item.category,nowValue));}

  function clear(category){
    if(category&&!CATEGORIES.has(category))return false;
    const before=read(),after=category?before.filter(item=>item.category!==category):[];
    write(after);
    dispatch('alo186:evidence-updated',{category:category||'all',cleared:true});
    return before.length!==after.length;
  }

  function dispatch(name,detail){if(root.dispatchEvent&&typeof root.CustomEvent==='function')root.dispatchEvent(new root.CustomEvent(name,{detail}));}

  function targetCategory(anchor){
    try{
      const href=anchor.getAttribute('href')||'';
      const url=new URL(href,root.location&&root.location.href?root.location.href:'https://alo186.com');
      if(!/\/akilli-urun-secimi\/?$/.test(url.pathname))return null;
      const query=url.searchParams.get('kategori');
      return CATEGORIES.has(query)?query:categoryFromPath(root.location&&root.location.pathname);
    }catch(_){return null;}
  }

  function clickHandler(event){
    const anchor=event.target&&event.target.closest?event.target.closest('a[href]'):null;
    if(!anchor)return;
    const category=targetCategory(anchor);
    if(!category)return;
    const currentPath=safePath(root.location&&root.location.pathname);
    if(!currentPath.startsWith('/hesaplama/')||currentPath.includes('/cozum-sonucu/')||currentPath.includes('/elektrik-planim/'))return;
    const item=record(category,currentPath);
    if(item&&typeof root.Alo186Track==='function')root.Alo186Track('technical_evidence_recorded',{category,status:'current',placement:'tool_to_product'});
  }

  function init(){
    if(initialized||!root.document)return;
    initialized=true;
    root.document.addEventListener('click',clickHandler,true);
  }

  return{STORAGE_KEY,MAX_RECORDS,TTL_DAYS,CATEGORIES,LABELS,TOOL_ROUTES,safePath,categoryFromPath,sanitize,prune,record,get,status,list,clear,init};
});
