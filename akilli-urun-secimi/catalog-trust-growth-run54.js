(function(root,factory){
  const current=root&&root.Alo186ProductCatalog
    ? root.Alo186ProductCatalog
    : (typeof module==='object'&&module.exports ? require('./catalog-qualified-commerce-run53.js') : null);
  const api=factory(current,root);
  if(typeof module==='object'&&module.exports)module.exports=api;
  if(root&&typeof root==='object')root.Alo186ProductCatalog=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(catalog,root){
  'use strict';

  if(!catalog)throw new Error('ALO186 affiliate kataloğu yüklenemedi.');
  if(catalog.__trustGrowthRun54)return catalog;

  const APEX_ORIGIN='https://alo186.com';
  const LEGACY_ORIGIN='https://alo186.com';
  const FORBIDDEN_TYPES=new Set(['Offer','AggregateOffer']);

  function normalizeString(value){
    return String(value).split(LEGACY_ORIGIN).join(APEX_ORIGIN);
  }

  function sanitize(value){
    if(Array.isArray(value))return value.map(sanitize).filter((item)=>item!==null&&item!==undefined);
    if(value&&typeof value==='object'){
      const type=value['@type'];
      if(typeof type==='string'&&FORBIDDEN_TYPES.has(type))return null;
      if(Array.isArray(type)&&type.some((item)=>FORBIDDEN_TYPES.has(item)))return null;
      const next={};
      for(const [key,item] of Object.entries(value)){
        if(key==='offers'||key==='aggregateRating'||key==='review')continue;
        const clean=sanitize(item);
        if(clean!==null&&clean!==undefined)next[key]=clean;
      }
      return next;
    }
    return typeof value==='string'?normalizeString(value):value;
  }

  function containsLegacyOrigin(value){
    return JSON.stringify(value).includes(LEGACY_ORIGIN);
  }

  const previousKnowledgeGraph=typeof catalog.knowledgeGraph==='function'
    ? catalog.knowledgeGraph.bind(catalog)
    : null;
  if(!previousKnowledgeGraph)throw new Error('Affiliate Knowledge Graph işlevi bulunamadı.');

  catalog.knowledgeGraph=(options={})=>sanitize(previousKnowledgeGraph(options));
  catalog.canonicalOrigin=APEX_ORIGIN;
  catalog.canonicalAudit=(options={})=>{
    const graph=catalog.knowledgeGraph(options);
    const serialized=JSON.stringify(graph);
    return {
      canonicalOrigin:APEX_ORIGIN,
      legacyOriginFound:serialized.includes(LEGACY_ORIGIN),
      forbiddenCommerceNodeFound:/\"@type\":\"(?:Offer|AggregateOffer)\"/.test(serialized),
      forbiddenCommercialFieldFound:/\"(?:offers|aggregateRating|review)\"\s*:/.test(serialized),
      productCount:(graph['@graph']||[]).filter((node)=>node&&node['@type']==='Product').length
    };
  };

  const previousSummary=typeof catalog.knowledgeGraphSummary==='function'
    ? catalog.knowledgeGraphSummary.bind(catalog)
    : null;
  if(previousSummary){
    catalog.knowledgeGraphSummary=(options={})=>({
      ...previousSummary(options),
      version:'2026-07-30-run54',
      canonicalOrigin:APEX_ORIGIN,
      canonicalAudit:catalog.canonicalAudit(options)
    });
  }

  catalog.__trustGrowthRun54=true;

  function normalizeDocument(document){
    if(!document)return;
    const canonical=document.querySelector&&document.querySelector('link[rel="canonical"]');
    if(canonical&&canonical.href)canonical.href=normalizeString(canonical.href);
    for(const link of document.querySelectorAll?document.querySelectorAll('a[href^="https://alo186.com"]'):[]){
      link.href=normalizeString(link.href);
    }
    for(const script of document.querySelectorAll?document.querySelectorAll('script[type="application/ld+json"]'):[]){
      try{
        const clean=sanitize(JSON.parse(script.textContent));
        if(clean)script.textContent=JSON.stringify(clean);
      }catch(_error){
        script.textContent=normalizeString(script.textContent||'');
      }
    }
    const generated=document.getElementById&&document.getElementById('alo186-affiliate-knowledge-graph');
    if(generated)generated.remove();
    if(document.head&&typeof document.createElement==='function'){
      const script=document.createElement('script');
      script.id='alo186-affiliate-knowledge-graph';
      script.type='application/ld+json';
      script.dataset.generated='alo186-affiliate-knowledge-graph-run54';
      script.textContent=JSON.stringify(catalog.knowledgeGraph());
      document.head.appendChild(script);
    }
  }

  if(root&&root.document){
    if(root.document.readyState==='loading')root.document.addEventListener('DOMContentLoaded',()=>normalizeDocument(root.document),{once:true});
    else normalizeDocument(root.document);
  }

  return catalog;
});
