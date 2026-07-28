(function(){
  'use strict';

  window.Alo186Track=function(name,params){
    const data=Object.assign({event:name,tool_location:location.pathname},params||{});
    window.dataLayer=window.dataLayer||[];
    window.dataLayer.push(data);
    window.dispatchEvent(new CustomEvent('alo186:event',{detail:data}));
  };

  window.fmt=function(value,digits=1,unit=''){
    return new Intl.NumberFormat('tr-TR',{maximumFractionDigits:digits,minimumFractionDigits:0}).format(value)+(unit?' '+unit:'');
  };

  window.copyText=async function(text,button){
    try{
      await navigator.clipboard.writeText(text);
      if(button){
        const old=button.textContent;
        button.textContent='Kopyalandı';
        setTimeout(()=>button.textContent=old,1600);
      }
    }catch(e){
      alert('Kopyalama başarısız. Metni manuel seçebilirsiniz.');
    }
  };

  document.querySelectorAll('[data-print]').forEach(button=>button.addEventListener('click',()=>window.print()));

  const current=document.currentScript;
  const commonUrl=current&&current.src?current.src:'/hesaplama/common.js';
  const commonPath=new URL(commonUrl,location.href).pathname;
  const basePath=commonPath.endsWith('/hesaplama/common.js')?commonPath.slice(0,-'/hesaplama/common.js'.length):'';
  const publicRoute=route=>`${basePath}${route}`;

  function injectGrowthCards(){
    const normalized=location.pathname.replace(/\/$/,'');
    const isPortal=normalized.endsWith('/elektrik-portali');
    const isGateway=normalized===''||normalized===basePath;
    if(!isPortal&&!isGateway)return;
    const grid=document.querySelector('section.grid');
    if(!grid)return;
    if(!grid.querySelector('[data-alo186-plan-runtime-card]')){
      const plan=document.createElement('a');
      plan.className='card';
      plan.href=publicRoute('/hesaplama/elektrik-planim/');
      plan.dataset.alo186PlanRuntimeCard='true';
      plan.innerHTML=isPortal?'<span class="tag">Tek plan · tekrar ziyaret · profesyonel hazırlık</span><h2>Elektrik Planım</h2><p>Kesinti, bakım, ürün yeniden kontrolü ve çözülmemiş işleri tek kişisel verisiz öncelik planında görün.</p><b>Bugünkü planı aç →</b>':'<strong>Elektrik Planım</strong><p>Kesinti, bakım, ürün yeniden kontrolü ve çözülmemiş işleri tek kişisel verisiz öncelik planında görün.</p><span>Bugünkü planı aç →</span>';
      grid.prepend(plan);
    }
    if(!grid.querySelector('[data-alo186-outcome-runtime-card]')){
      const outcome=document.createElement('a');
      outcome.className='card';
      outcome.href=publicRoute('/hesaplama/cozum-sonucu/');
      outcome.dataset.alo186OutcomeRuntimeCard='true';
      outcome.innerHTML=isPortal?'<span class="tag">Kapalı döngü · satın almama · tekrar önleme</span><h2>Çözüm Sonucu Merkezi</h2><p>Karar, hesap, ürün, bakım veya resmî kanalın gerçekten işe yarayıp yaramadığını izleyin.</p><b>Sonucu kaydet ve izle →</b>':'<strong>Çözüm gerçekten işe yaradı mı?</strong><p>Öneri, ürün, bakım veya resmî kanal sonucunu kişisel veri vermeden kaydedin.</p><span>Sonucu kaydet ve izle →</span>';
      grid.prepend(outcome);
    }
  }

  function loadRuntime(name,dataKey){
    if(window[name]||document.querySelector(`script[${dataKey}]`))return;
    const script=document.createElement('script');
    script.src=new URL(`${name==='Alo186EvidenceWallet'?'evidence-wallet.js':name==='Alo186IntentActionRouter'?'intent-action-router.js':'outcome-bridge.js'}`,commonUrl).href;
    if(name==='Alo186OutcomeBridge')script.dataset.alo186OutcomeBridge='true';
    else script.setAttribute(dataKey,'true');
    script.defer=true;
    document.head.appendChild(script);
  }

  // Compatibility contract retained from the original loader: new URL('outcome-bridge.js',current.src)
  loadRuntime('Alo186OutcomeBridge','data-alo186-outcome-bridge');
  loadRuntime('Alo186EvidenceWallet','data-alo186-evidence-wallet');
  loadRuntime('Alo186IntentActionRouter','data-alo186-intent-router');

  const productCenter=/\/(akilli-urun-secimi|amazon-elektrik-urunleri)\/?$/.test(location.pathname);

  if(productCenter&&!document.querySelector('script[data-alo186-outcome-trust-core]')){
    const coreScript=document.createElement('script');
    coreScript.src=new URL('../urun-eslestirme/outcome-trust-circuit-core.js',commonUrl).href;
    coreScript.dataset.alo186OutcomeTrustCore='true';
    coreScript.addEventListener('load',()=>{
      if(document.querySelector('script[data-alo186-outcome-trust-ui]'))return;
      const uiScript=document.createElement('script');
      uiScript.src=new URL('../urun-eslestirme/outcome-trust-circuit.js',commonUrl).href;
      uiScript.dataset.alo186OutcomeTrustUi='true';
      uiScript.defer=true;
      document.head.appendChild(uiScript);
    },{once:true});
    document.head.appendChild(coreScript);
  }

  function loadDocumentationLayer(){
    if(!productCenter||document.querySelector('script[data-alo186-documentation-core]'))return;
    const documentationCore=document.createElement('script');
    documentationCore.src=new URL('../urun-eslestirme/documentation-growth-core.js',commonUrl).href;
    documentationCore.dataset.alo186DocumentationCore='true';
    documentationCore.addEventListener('load',()=>{
      if(document.querySelector('script[data-alo186-documentation-ui]'))return;
      const documentationUi=document.createElement('script');
      documentationUi.src=new URL('../urun-eslestirme/documentation-growth.js',commonUrl).href;
      documentationUi.dataset.alo186DocumentationUi='true';
      documentationUi.defer=true;
      document.head.appendChild(documentationUi);
    },{once:true});
    document.head.appendChild(documentationCore);
  }

  if(document.readyState==='loading'){
    document.addEventListener('DOMContentLoaded',injectGrowthCards,{once:true});
    document.addEventListener('DOMContentLoaded',loadDocumentationLayer,{once:true});
  }else{
    injectGrowthCards();
    loadDocumentationLayer();
  }
})();
