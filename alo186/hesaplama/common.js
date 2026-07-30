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

  function shortlistCard(isPortal){
    const link=document.createElement('a');
    link.className=isPortal?'card':'tool-card';
    link.href=publicRoute('/hesaplama/teknik-urun-karsilastirma/');
    link.dataset.alo186ShortlistRuntimeCard='true';
    link.innerHTML=isPortal?'<span class="tag">Üç aday · mevcut ürün · satın almama</span><h2>Teknik Ürün Karşılaştırma</h2><p>Marka, fiyat ve puan kullanmadan üç adayın belge kapsamını karşılaştırın; mevcut ürün yeterliyse yeni ürün almayın.</p><b>Teknik kısa listeyi oluştur →</b>':'<span class="eyebrow">Üç aday · teknik belge · karar makbuzu</span><h2>Teknik Ürün Karşılaştırma</h2><p>Power station, mini UPS, powerbank, EV kablosu ve benzeri ürünlerde üç adayı teknik kanıtla karşılaştırın.</p><b>Kısa listeyi oluştur →</b>';
    return link;
  }

  function generatorSafetyCard(isPortal){
    const link=document.createElement('a');
    link.className=isPortal?'card':'tool-card';
    link.href=publicRoute('/hesaplama/jenerator-guvenli-kullanim-testi/');
    link.dataset.alo186GeneratorSafetyCard='true';
    link.innerHTML=isPortal?'<span class="tag">CO · 6,1 m · geri besleme · kablo</span><h2>Jeneratör Güvenli Kullanım Testi</h2><p>Garaj, balkon, egzoz yönü, CO alarmı, uzatma kablosu ve transfer bağlantısını çalıştırmadan önce kontrol edin.</p><b>Güvenlik testini aç →</b>':'<span class="eyebrow">CO · yerleşim · egzoz · bağlantı</span><h2>Jeneratör Güvenli Kullanım Testi</h2><p>6,1 m açıklık mesafesi, CO alarmı, yağmur, kablo, yakıt ve geri besleme riskini tek karar ağacında değerlendirin.</p><b>Jeneratörü çalıştırmadan kontrol et →</b>';
    return link;
  }

  function pumpBackupCard(isPortal){
    const link=document.createElement('a');
    link.className=isPortal?'card':'tool-card';
    link.href=publicRoute('/hesaplama/hidrofor-pompa-yedek-guc-uygunluk/');
    link.dataset.alo186PumpBackupCard='true';
    link.innerHTML=isPortal?'<span class="tag">Hidrofor · kalkış W · Wh · faz</span><h2>Pompa Yedek Güç Uygunluk Testi</h2><p>Hidrofor ve su pompasında etiket akımı, kalkış yöntemi, jeneratör/inverter gücü ve hedef süreyi birlikte değerlendirin.</p><b>Pompa hesabını aç →</b>':'<span class="eyebrow">Pompa · kalkış · jeneratör · inverter</span><h2>Hidrofor ve Pompa Yedek Güç Testi</h2><p>Motorun sürekli W, kalkış W ve batarya Wh ihtiyacını hesaplayın; mevcut kaynak yeterliyse yeni ürün almayın.</p><b>Yedek güç uygunluğunu hesapla →</b>';
    return link;
  }

  function injectGrowthCards(){
    const normalized=location.pathname.replace(/\/$/,'');
    const isPortal=normalized.endsWith('/elektrik-portali');
    const isGateway=normalized===''||normalized===basePath;
    if(isPortal||isGateway){
      const grid=document.querySelector('section.grid');
      if(grid){
        if(!grid.querySelector('[data-alo186-plan-runtime-card]')){
          const plan=document.createElement('a');plan.className='card';plan.href=publicRoute('/hesaplama/elektrik-planim/');plan.dataset.alo186PlanRuntimeCard='true';plan.innerHTML=isPortal?'<span class="tag">Tek plan · tekrar ziyaret · profesyonel hazırlık</span><h2>Elektrik Planım</h2><p>Kesinti, bakım, ürün yeniden kontrolü ve çözülmemiş işleri tek kişisel verisiz öncelik planında görün.</p><b>Bugünkü planı aç →</b>':'<strong>Elektrik Planım</strong><p>Kesinti, bakım, ürün yeniden kontrolü ve çözülmemiş işleri tek kişisel verisiz öncelik planında görün.</p><span>Bugünkü planı aç →</span>';grid.prepend(plan);
        }
        if(!grid.querySelector('[data-alo186-outcome-runtime-card]')){
          const outcome=document.createElement('a');outcome.className='card';outcome.href=publicRoute('/hesaplama/cozum-sonucu/');outcome.dataset.alo186OutcomeRuntimeCard='true';outcome.innerHTML=isPortal?'<span class="tag">Kapalı döngü · satın almama · tekrar önleme</span><h2>Çözüm Sonucu Merkezi</h2><p>Karar, hesap, ürün, bakım veya resmî kanalın gerçekten işe yarayıp yaramadığını izleyin.</p><b>Sonucu kaydet ve izle →</b>':'<strong>Çözüm gerçekten işe yaradı mı?</strong><p>Öneri, ürün, bakım veya resmî kanal sonucunu kişisel veri vermeden kaydedin.</p><span>Sonucu kaydet ve izle →</span>';grid.prepend(outcome);
        }
        if(!grid.querySelector('[data-alo186-pump-backup-card]'))grid.prepend(pumpBackupCard(true));
        if(!grid.querySelector('[data-alo186-generator-safety-card]'))grid.prepend(generatorSafetyCard(true));
        if(!grid.querySelector('[data-alo186-shortlist-runtime-card]'))grid.prepend(shortlistCard(true));
      }
    }

    const isHub=/\/hesaplama\/?$/.test(location.pathname);
    if(isHub){
      const grid=document.querySelector('section.tool-grid');
      if(grid&&!grid.querySelector('[data-alo186-pump-backup-card]'))grid.prepend(pumpBackupCard(false));
      if(grid&&!grid.querySelector('[data-alo186-generator-safety-card]'))grid.prepend(generatorSafetyCard(false));
      if(grid&&!grid.querySelector('[data-alo186-shortlist-runtime-card]'))grid.prepend(shortlistCard(false));
      document.querySelectorAll('strong').forEach(node=>{if(/\d+ çekirdek araç/.test(node.textContent||''))node.textContent=(node.textContent||'').replace(/\d+ çekirdek araç/,'36 çekirdek araç');});
    }

    const productCenter=/\/(akilli-urun-secimi|amazon-elektrik-urunleri)\/?$/.test(location.pathname);
    if(productCenter&&!document.querySelector('[data-alo186-shortlist-product-entry]')){
      const section=document.createElement('section');
      section.className='content-section';
      section.dataset.alo186ShortlistProductEntry='true';
      section.innerHTML=`<div class="panel"><span class="eyebrow">Karşılaştırma öncesi güven kapısı</span><h2>Üç adayı marka ve fiyat kullanmadan karşılaştırın</h2><p>Mevcut ekipmanı dördüncü seçenek olarak koruyun; kritik teknik belge eksikse ürün rotasını açmayın. Karar makbuzu ve 14 günlük yeniden kontrol yalnız tarayıcınızda tutulur.</p><div class="actions"><a class="btn btn-secondary" href="${publicRoute('/hesaplama/teknik-urun-karsilastirma/')}">Teknik kısa listeyi aç</a></div><small>Bu araç doğrudan mağaza bağlantısı, fiyat, stok, puan veya garanti göstermez.</small></div>`;
      const main=document.querySelector('main');if(main)main.insertBefore(section,main.children[1]||null);
    }
  }

  function loadRuntime(name,dataKey){
    if(window[name]||document.querySelector(`script[${dataKey}]`))return;
    const script=document.createElement('script');
    script.src=new URL(`${name==='Alo186EvidenceWallet'?'evidence-wallet.js':name==='Alo186IntentActionRouter'?'intent-action-router.js':'outcome-bridge.js'}`,commonUrl).href;
    if(name==='Alo186OutcomeBridge')script.dataset.alo186OutcomeBridge='true';else script.setAttribute(dataKey,'true');
    script.async=true;document.head.appendChild(script);
  }

  function loadSupportingRuntimes(){
    // Compatibility contract: new URL('outcome-bridge.js',current.src)
    loadRuntime('Alo186OutcomeBridge','data-alo186-outcome-bridge');
    loadRuntime('Alo186EvidenceWallet','data-alo186-evidence-wallet');
    loadRuntime('Alo186IntentActionRouter','data-alo186-intent-router');
  }

  const productCenter=/\/(akilli-urun-secimi|amazon-elektrik-urunleri)\/?$/.test(location.pathname);
  if(productCenter&&!document.querySelector('script[data-alo186-outcome-trust-core]')){
    const coreScript=document.createElement('script');coreScript.src=new URL('../akilli-urun-secimi/outcome-trust-circuit-core.js',commonUrl).href;coreScript.dataset.alo186OutcomeTrustCore='true';coreScript.addEventListener('load',()=>{if(document.querySelector('script[data-alo186-outcome-trust-ui]'))return;const uiScript=document.createElement('script');uiScript.src=new URL('../akilli-urun-secimi/outcome-trust-circuit.js',commonUrl).href;uiScript.dataset.alo186OutcomeTrustUi='true';uiScript.defer=true;document.head.appendChild(uiScript);},{once:true});document.head.appendChild(coreScript);
  }

  function loadDocumentationLayer(){
    if(!productCenter||document.querySelector('script[data-alo186-documentation-core]'))return;
    const documentationCore=document.createElement('script');documentationCore.src=new URL('../akilli-urun-secimi/documentation-growth-core.js',commonUrl).href;documentationCore.dataset.alo186DocumentationCore='true';documentationCore.addEventListener('load',()=>{if(document.querySelector('script[data-alo186-documentation-ui]'))return;const documentationUi=document.createElement('script');documentationUi.src=new URL('../akilli-urun-secimi/documentation-growth.js',commonUrl).href;documentationUi.dataset.alo186DocumentationUi='true';documentationUi.defer=true;document.head.appendChild(documentationUi);},{once:true});document.head.appendChild(documentationCore);
  }

  // common.js final body scripti olarak yayımlanır. DOM mevcutsa büyüme kartlarını
  // DOMContentLoaded sonrasına bırakmak CLS üretir; ilk boyamadan önce senkron ekle.
  if(document.body)injectGrowthCards();
  else document.addEventListener('DOMContentLoaded',injectGrowthCards,{once:true});

  // Kanıt cüzdanı, sonuç köprüsü ve niyet yönlendiricisi ilk boyama için kritik değildir.
  // Mobil ana iş parçacığını rahatlatmak için load sonrasında boşta yükle.
  const scheduleSupportingRuntimes=()=>{
    if('requestIdleCallback'in window)window.requestIdleCallback(loadSupportingRuntimes,{timeout:3000});
    else setTimeout(loadSupportingRuntimes,250);
  };
  if(document.readyState==='complete')scheduleSupportingRuntimes();
  else window.addEventListener('load',scheduleSupportingRuntimes,{once:true});

  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',loadDocumentationLayer,{once:true});
  else loadDocumentationLayer();
})();
