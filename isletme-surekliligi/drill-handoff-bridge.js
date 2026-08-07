(() => {
  'use strict';

  const store=window.Alo186ContinuityStore;
  if(!store||typeof localStorage==='undefined'||typeof store.validateDrillHandoff!=='function'||typeof store.importDrillHandoff!=='function')return;

  const PANEL_STORAGE_KEY='alo186_continuity_pilot_v1';
  const MATURITY_KEY='alo186.continuityMaturityHandoff.v1';
  const DRILL_KEY='alo186.continuity-drill-handoff.v1';
  const DRILL_SCHEMA='alo186.continuity-drill-handoff.v1';
  const originalValidate=store.validateMaturityHandoff.bind(store);
  const originalImport=store.importMaturityHandoff.bind(store);

  function parse(key){
    try{return JSON.parse(localStorage.getItem(key)||'null');}catch(_error){return null;}
  }

  store.validateMaturityHandoff=(raw,at)=>raw&&raw.schema===DRILL_SCHEMA?store.validateDrillHandoff(raw,at):originalValidate(raw,at);
  store.importMaturityHandoff=(state,raw,at)=>{
    if(!raw||raw.schema!==DRILL_SCHEMA)return originalImport(state,raw,at);
    const sourcePayload=parse(MATURITY_KEY);
    const candidate=sourcePayload&&sourcePayload.schema===DRILL_SCHEMA?sourcePayload:raw;
    return store.importDrillHandoff(state,candidate,at);
  };

  function validPending(){
    const raw=parse(MATURITY_KEY);
    const checked=raw&&raw.schema===DRILL_SCHEMA?store.validateDrillHandoff(raw):originalValidate(raw);
    if(checked.valid)return true;
    try{localStorage.removeItem(MATURITY_KEY);}catch(_error){}
    return false;
  }

  function bridgeDrill(){
    if(validPending())return false;
    const raw=parse(DRILL_KEY),checked=store.validateDrillHandoff(raw);
    if(!checked.valid){try{localStorage.removeItem(DRILL_KEY);}catch(_error){}return false;}
    try{
      localStorage.setItem(MATURITY_KEY,JSON.stringify(raw));
      localStorage.removeItem(DRILL_KEY);
      return true;
    }catch(_error){return false;}
  }

  const bridged=bridgeDrill();

  function formatDate(value){
    const date=new Date(value);return Number.isNaN(date.getTime())?'—':new Intl.DateTimeFormat('tr-TR',{dateStyle:'short',timeStyle:'short'}).format(date);
  }

  function relabelDrillActions(){
    let state;try{state=JSON.parse(localStorage.getItem(PANEL_STORAGE_KEY)||'null');}catch(_error){state=null;}
    if(!state||typeof state!=='object')return;
    const actions=new Map((Array.isArray(state.improvementActions)?state.improvementActions:[]).map(item=>[item.id,item]));
    document.querySelectorAll('[data-improvement-toggle]').forEach(input=>{
      const action=actions.get(input.dataset.actionId),small=input.closest('label')?.querySelector('small');
      if(action?.source==='outage-drill'&&small){
        const desired=`${small.textContent.split(' · ')[0]} · Kesinti Tatbikatı bulgusu`;
        if(small.textContent!==desired)small.textContent=desired;
      }
    });
    const imports=[
      ...(Array.isArray(state.maturityImports)?state.maturityImports:[]).map(item=>({...item,type:'maturity'})),
      ...(Array.isArray(state.drillImports)?state.drillImports:[]).map(item=>({...item,type:'drill'}))
    ].sort((a,b)=>new Date(b.importedAt)-new Date(a.importedAt));
    const latest=imports[0],source=document.getElementById('improvementSource');
    if(latest?.type==='drill'&&source){
      const desired=`${latest.score}/100 · Kesinti Tatbikatı · ${formatDate(latest.importedAt)}`;
      if(source.textContent!==desired)source.textContent=desired;
    }
  }

  document.addEventListener('DOMContentLoaded',()=>{
    const raw=parse(MATURITY_KEY),isDrill=raw&&raw.schema===DRILL_SCHEMA;
    if(isDrill){
      const banner=document.getElementById('maturityHandoff'),eyebrow=banner?.querySelector('.eyebrow'),accept=document.getElementById('acceptHandoffBtn');
      if(eyebrow)eyebrow.textContent='Kesinti Tatbikatı aktarımı hazır';
      if(accept)accept.textContent='Tatbikat bulgularını içe aktar';
      accept?.addEventListener('click',()=>{
        window.dataLayer=window.dataLayer||[];
        window.dataLayer.push({event:'continuity_drill_handoff_import_started',handoff_schema:DRILL_SCHEMA});
      });
    }
    const target=document.getElementById('iyilestirme');
    if(target)new MutationObserver(()=>queueMicrotask(relabelDrillActions)).observe(target,{childList:true,subtree:true});
    queueMicrotask(relabelDrillActions);
    if(bridged){
      window.dataLayer=window.dataLayer||[];
      window.dataLayer.push({event:'continuity_drill_handoff_detected',handoff_schema:DRILL_SCHEMA});
    }
  });
})();
