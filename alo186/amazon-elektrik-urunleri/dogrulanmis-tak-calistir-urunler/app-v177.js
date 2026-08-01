(() => {
  'use strict';

  const $=id=>document.getElementById(id);
  const catalog=window.Alo186ProductCatalog;
  const engine=window.Alo186AffiliateRevenueV177;
  const state={data:null,activeCategories:null,query:''};

  function escapeHtml(value){return String(value??'').replace(/[&<>"']/g,char=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));}
  function emit(name,params={}){if(typeof window.Alo186Track==='function')window.Alo186Track(name,params);}
  function gateOpen(){return Boolean($('gateExisting')?.checked&&$('gateTechnical')?.checked&&$('gateAffiliate')?.checked);}
  function normalized(value){return String(value||'').toLocaleLowerCase('tr-TR').normalize('NFKD').replace(/[\u0300-\u036f]/g,'').replace(/ı/g,'i');}
  function matches(item){
    const categoryOk=!state.activeCategories||state.activeCategories.has(item.category);
    if(!categoryOk)return false;
    if(!state.query)return true;
    const surface=normalized([item.name,item.brand,item.mpn,item.userNeed,...(item.facts||[]),...(item.evidence||[])].join(' '));
    return surface.includes(state.query);
  }
  function list(items){return `<ul>${(items||[]).map(item=>`<li>${escapeHtml(item)}</li>`).join('')}</ul>`;}

  function affiliateAction(item,placement){
    if(!gateOpen())return '<button type="button" class="shop locked" disabled>Üç onaydan sonra açılır</button>';
    const label=placement==='exact'?'Amazon ürün sayfasını aç':'Amazon seçeneklerini incele';
    return `<a class="shop" data-affiliate-link data-product-title="${escapeHtml(item.name)}" data-product-category="${escapeHtml(item.rawCategory||item.category)}" data-placement="${placement}" data-item="${escapeHtml(item.id)}" href="${escapeHtml(item.amazonUrl)}" target="_blank" rel="sponsored nofollow noopener"><small>Satış ortaklığı bağlantısı</small>${label}</a>`;
  }

  function exactCard(item){
    return `<article class="card exact-card" data-kind="exact" data-category="${escapeHtml(item.category)}">
      <div class="card-top"><span class="pill">${escapeHtml(state.data.categoryLabels[item.category]||item.category)}</span><span class="freshness">Kontrol: ${escapeHtml(item.verifiedAt)}</span></div>
      <h3>${escapeHtml(item.name)}</h3>
      <p class="model">${escapeHtml(item.brand)}${item.mpn?` · ${escapeHtml(item.mpn)}`:''} · ASIN ${escapeHtml(item.asin)}</p>
      <p><strong>Çözdüğü ihtiyaç:</strong> ${escapeHtml(item.userNeed)}</p>
      <details><summary>Teknik kanıt ve satın almama sınırı</summary>
        <h4>Doğrulanan güçlü alanlar</h4>${list(item.facts)}
        <h4>En uygun kullanım</h4>${list(item.bestFor)}
        <h4>Satın almadan önce doğrulayın</h4>${list(item.evidence)}
        <h4>Bu durumda almayın</h4>${list(item.noBuyWhen)}
      </details>
      <div class="source-row"><a href="${escapeHtml(item.technicalSource)}"${/^https?:/.test(item.technicalSource)?' target="_blank" rel="external noopener noreferrer"':''}>${escapeHtml(item.sourceLabel)} →</a></div>
      <div class="affiliate-action">${affiliateAction(item,'exact')}</div>
    </article>`;
  }

  function classCard(item){
    return `<article class="card class-card" data-kind="class" data-category="${escapeHtml(item.category)}">
      <div class="card-top"><span class="pill">Ürün sınıfı</span><span class="freshness">Teknik arama</span></div>
      <h3>${escapeHtml(item.name)}</h3>
      <p><strong>Önce doğrulayın:</strong> ${(item.evidence||[]).map(escapeHtml).join(' · ')}</p>
      <p><strong>Almayın:</strong> ${escapeHtml(item.noBuyWhen)}</p>
      <div class="source-row"><a href="${escapeHtml(item.tool)}">Ücretsiz uygunluk kontrolünü aç →</a></div>
      <div class="affiliate-action">${affiliateAction(item,'search')}</div>
    </article>`;
  }

  function bindAffiliateEvents(){
    document.querySelectorAll('[data-affiliate-link]').forEach(link=>link.addEventListener('click',()=>emit('affiliate_revenue_v177_click',{item_id:link.dataset.item,placement:link.dataset.placement,collection:'verified_plug_and_play_v177'})));
  }

  function render(){
    if(!state.data)return;
    const exact=state.data.products.filter(matches);
    const classes=state.data.productClasses.filter(matches);
    $('exactProducts').innerHTML=exact.length?exact.map(exactCard).join(''):'<p class="empty">Bu filtrede güncel doğrulanmış model bulunamadı. Ürün sınıflarındaki teknik aramayı kullanın.</p>';
    $('productClasses').innerHTML=classes.length?classes.map(classCard).join(''):'<p class="empty">Aramanızla eşleşen ürün sınıfı bulunamadı.</p>';
    $('visibleCount').textContent=String(exact.length+classes.length);
    $('gateStatus').textContent=gateOpen()?'Teknik ve ticari sınırlar onaylandı. Bağlantılar bu oturum için açıldı.':'Mağaza bağlantıları kapalı. Üç koşulu tamamlayın.';
    $('gatePanel').dataset.open=String(gateOpen());
    bindAffiliateEvents();
  }

  function categoryCounts(){
    const counts={};
    for(const item of [...state.data.products,...state.data.productClasses])counts[item.category]=(counts[item.category]||0)+1;
    return counts;
  }

  function renderFilters(){
    const counts=categoryCounts();
    const labels=state.data.categoryLabels;
    const keys=['all',...Object.keys(labels).filter(key=>key!=='all'&&counts[key])];
    $('filters').innerHTML=keys.map(key=>`<button type="button" data-filter="${key}" aria-pressed="${key==='all'}">${escapeHtml(labels[key])}${key==='all'?'':` <small>${counts[key]}</small>`}</button>`).join('');
    $('filters').querySelectorAll('[data-filter]').forEach(button=>button.addEventListener('click',()=>{
      const key=button.dataset.filter;
      state.activeCategories=key==='all'?null:new Set([key]);
      $('filters').querySelectorAll('[data-filter]').forEach(item=>item.setAttribute('aria-pressed',String(item===button)));
      $('bundles').querySelectorAll('[data-bundle]').forEach(item=>item.setAttribute('aria-pressed','false'));
      render();
      emit('affiliate_revenue_v177_filter',{category:key});
    }));
  }

  function renderBundles(){
    $('bundles').innerHTML=state.data.bundles.map(bundle=>`<button type="button" class="bundle" data-bundle="${escapeHtml(bundle.id)}" aria-pressed="false"><strong>${escapeHtml(bundle.name)}</strong><span>${escapeHtml(bundle.description)}</span><small>${bundle.categories.map(key=>state.data.categoryLabels[key]||key).join(' · ')}</small></button>`).join('');
    $('bundles').querySelectorAll('[data-bundle]').forEach(button=>button.addEventListener('click',()=>{
      const bundle=state.data.bundles.find(item=>item.id===button.dataset.bundle);
      state.activeCategories=new Set(bundle.categories);
      $('bundles').querySelectorAll('[data-bundle]').forEach(item=>item.setAttribute('aria-pressed',String(item===button)));
      $('filters').querySelectorAll('[data-filter]').forEach(item=>item.setAttribute('aria-pressed','false'));
      render();
      document.getElementById('modelsTitle')?.scrollIntoView({behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'auto':'smooth'});
      emit('affiliate_revenue_v177_bundle',{bundle_id:bundle.id,categories:bundle.categories.join(',')});
    }));
  }

  function injectKnowledgeGraph(){
    const old=document.getElementById('alo186-affiliate-revenue-graph-v177');
    if(old)old.remove();
    const script=document.createElement('script');
    script.id='alo186-affiliate-revenue-graph-v177';
    script.type='application/ld+json';
    const page='https://alo186.com/amazon-elektrik-urunleri/dogrulanmis-tak-calistir-urunler/';
    script.textContent=JSON.stringify({'@context':'https://schema.org','@graph':[
      {'@type':'CollectionPage','@id':`${page}#page`,name:'Doğrulanmış Tak-Çalıştır Elektrik Ürünleri',url:page,mainEntity:{'@id':`${page}#models`}},
      {'@type':'ItemList','@id':`${page}#models`,name:'ALO186 güncel doğrulanmış düşük riskli ürün modelleri',numberOfItems:state.data.products.length,itemListElement:state.data.products.map((item,index)=>({'@type':'ListItem',position:index+1,item:{'@type':'Product','@id':`${page}#${item.id}`,name:item.name,sku:item.id,mpn:item.mpn||undefined,identifier:{'@type':'PropertyValue',propertyID:'ASIN',value:item.asin},brand:{'@type':'Brand',name:item.brand},category:item.rawCategory,dateModified:item.verifiedAt,subjectOf:item.technicalSource}}))},
      {'@type':'DefinedTermSet','@id':`${page}#classes`,name:'ALO186 düşük riskli affiliate ürün sınıfları',hasDefinedTerm:state.data.productClasses.map(item=>({'@type':'DefinedTerm','@id':`${page}#class-${item.id}`,name:item.name,termCode:item.id,description:`${(item.evidence||[]).join(', ')}. Satın almama sınırı: ${item.noBuyWhen}`}))}
    ]});
    document.head.appendChild(script);
  }

  async function boot(){
    if(!catalog||!engine)throw new Error('ALO186 ürün kataloğu yüklenemedi.');
    const response=await fetch('./opportunities-v177.json',{headers:{Accept:'application/json'}});
    if(!response.ok)throw new Error(`Ürün niyeti verisi yüklenemedi: ${response.status}`);
    state.data=engine.build(catalog,await response.json(),new Date());
    $('modelStat').textContent=String(state.data.stats.exactProducts);
    $('classStat').textContent=String(state.data.stats.productClasses);
    $('bundleStat').textContent=String(state.data.stats.bundles);
    $('freshnessStat').textContent=`${state.data.verificationMaxAgeDays} gün`;
    renderFilters();
    renderBundles();
    injectKnowledgeGraph();
    ['gateExisting','gateTechnical','gateAffiliate'].forEach(id=>$(id)?.addEventListener('change',()=>{render();emit('affiliate_revenue_v177_gate',{open:gateOpen(),field:id});}));
    $('resetGate')?.addEventListener('click',()=>{['gateExisting','gateTechnical','gateAffiliate'].forEach(id=>{if($(id))$(id).checked=false;});render();});
    $('catalogSearch')?.addEventListener('input',event=>{state.query=normalized(event.target.value.trim());render();});
    $('clearFilters')?.addEventListener('click',()=>{state.activeCategories=null;state.query='';$('catalogSearch').value='';renderFilters();$('bundles').querySelectorAll('[data-bundle]').forEach(item=>item.setAttribute('aria-pressed','false'));render();});
    render();
    emit('affiliate_revenue_v177_view',{exact_count:state.data.stats.exactProducts,class_count:state.data.stats.productClasses,bundle_count:state.data.stats.bundles,version:state.data.version});
  }

  document.addEventListener('DOMContentLoaded',()=>boot().catch(error=>{
    console.error(error);
    $('loadStatus').hidden=false;
    $('loadStatus').textContent='Ürün kataloğu şu anda yüklenemedi. Ücretsiz teknik araçlar kullanılmaya devam edebilir.';
  }));
})();
