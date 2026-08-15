(() => {
  'use strict';

  const data=window.Alo186ExactHomeNetworkSafetyV176;
  if(!data)throw new Error('ALO186 ev-ofis ürün verisi yüklenemedi.');

  const $=id=>document.getElementById(id);
  const categoryLabels={all:'Tümü',network:'Ağ',camera:'Kamera',lighting:'Aydınlatma',monitoring:'İzleme ve düzen'};
  let activeCategory='all';

  function escapeHtml(value){
    return String(value??'').replace(/[&<>"']/g,char=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
  }
  function emit(name,params={}){
    const safe={collection:'home_network_safety_v176',...params};
    if(typeof window.Alo186Track==='function'){
      try{window.Alo186Track(name,safe);}catch(_error){}
    }
    const analytics=window.alo186Analytics;
    if(analytics&&typeof analytics.track==='function'){
      try{
        if(typeof analytics.getConsent!=='function'||analytics.getConsent()==='granted')analytics.track(name,safe);
      }catch(_error){}
    }
  }
  function ageDays(value){
    const checked=new Date(`${value}T00:00:00Z`);
    return Number.isNaN(checked.getTime())?Infinity:Math.max(0,Math.floor((Date.now()-checked.getTime())/86400000));
  }
  function fresh(item){return ageDays(item.verifiedAt)<=data.verificationMaxAgeDays;}
  function gateOpen(){
    return Boolean($('gateExisting')?.checked&&$('gateTechnical')?.checked&&$('gateAffiliate')?.checked);
  }
  function filterMatch(category){return activeCategory==='all'||category===activeCategory;}

  function actionMarkup(item,kind){
    if(!fresh(item))return '<span class="blocked-action">Teknik kontrol tarihi yenileniyor</span>';
    if(!gateOpen())return '<button type="button" class="shop locked" disabled aria-disabled="true">Üç onaydan sonra açılır</button>';
    const placement=kind==='exact'?'exact_model':'product_class';
    const label=kind==='exact'?'Amazon ürün sayfasını aç':'Amazon seçeneklerini incele';
    return `<a class="shop" data-affiliate-link data-placement="${placement}" data-item="${escapeHtml(item.id)}" href="${escapeHtml(item.amazonUrl)}" target="_blank" rel="sponsored nofollow noopener"><small>Satış ortaklığı bağlantısı</small>${label}</a>`;
  }

  function list(items){return items.map(item=>`<li>${escapeHtml(item)}</li>`).join('');}

  function exactCard(product){
    return `<article class="card exact-card" id="model-${escapeHtml(product.id)}" data-category="${escapeHtml(product.category)}">
      <div class="card-top"><span class="pill">${escapeHtml(categoryLabels[product.category]||product.category)}</span><span class="freshness">Kontrol: ${escapeHtml(product.verifiedAt)}</span></div>
      <h2>${escapeHtml(product.name)}</h2>
      <p class="model">${escapeHtml(product.brand)} · ${escapeHtml(product.mpn)} · ASIN ${escapeHtml(product.asin)}</p>
      <p><strong>Çözdüğü ihtiyaç:</strong> ${escapeHtml(product.userNeed)}</p>
      <details><summary>Teknik kanıt ve satın almama sınırı</summary><div>
        <h3>Doğrulanan alanlar</h3><ul>${list(product.facts)}</ul>
        <h3>En uygun kullanım</h3><ul>${list(product.bestFor)}</ul>
        <h3>Satın almadan önce</h3><ul>${list(product.evidence)}</ul>
        <h3>Bu durumda almayın</h3><ul>${list(product.noBuyWhen)}</ul>
      </div></details>
      <div class="source-row"><a href="${escapeHtml(product.technicalSource)}" target="_blank" rel="external noopener noreferrer">Üretici teknik kaynağını doğrula ↗</a></div>
      <div class="affiliate-action">${actionMarkup(product,'exact')}</div>
    </article>`;
  }

  function classCard(item){
    return `<article class="card class-card" data-category="${escapeHtml(item.category)}">
      <div class="card-top"><span class="pill">Ürün sınıfı</span><span class="freshness">Kontrol: ${escapeHtml(item.verifiedAt)}</span></div>
      <h2>${escapeHtml(item.name)}</h2>
      <p><strong>Önce doğrulayın:</strong> ${item.evidence.map(escapeHtml).join(' · ')}</p>
      <p><strong>Almayın:</strong> ${escapeHtml(item.noBuyWhen)}</p>
      <div class="source-row"><a href="${escapeHtml(item.tool)}">Ücretsiz teknik kontrolü aç →</a></div>
      <div class="affiliate-action">${actionMarkup(item,'class')}</div>
    </article>`;
  }

  function bindAffiliateEvents(){
    document.querySelectorAll('[data-affiliate-link]').forEach(link=>{
      link.addEventListener('click',()=>emit(
        link.dataset.placement==='exact_model'?'affiliate_home_network_exact_clicked':'affiliate_home_network_class_clicked',
        {item_id:link.dataset.item,placement:link.dataset.placement}
      ));
    });
  }

  function render(){
    const exact=data.products.filter(item=>filterMatch(item.category));
    const classes=data.productClasses.filter(item=>filterMatch(item.category));
    $('exactCount').textContent=String(exact.length);
    $('classCount').textContent=String(classes.length);
    $('exactProducts').innerHTML=exact.map(exactCard).join('');
    $('productClasses').innerHTML=classes.map(classCard).join('');
    const open=gateOpen();
    $('gateStatus').textContent=open
      ? 'Teknik ve ticari sınırlar onaylandı. Bağlantılar yalnız bu oturum için açıldı.'
      : 'Mağaza bağlantıları kapalı. Üç koşulu tamamlayın.';
    $('gatePanel').dataset.open=String(open);
    bindAffiliateEvents();
  }

  function renderFilters(){
    $('filters').innerHTML=Object.entries(categoryLabels).map(([id,label])=>`<button type="button" data-filter="${id}" aria-pressed="${id==='all'}">${escapeHtml(label)}</button>`).join('');
    $('filters').querySelectorAll('[data-filter]').forEach(button=>button.addEventListener('click',()=>{
      activeCategory=button.dataset.filter;
      $('filters').querySelectorAll('[data-filter]').forEach(item=>item.setAttribute('aria-pressed',String(item===button)));
      render();
      emit('affiliate_home_network_filter',{category:activeCategory});
    }));
  }

  function injectKnowledgeGraph(){
    const previous=document.getElementById('alo186-home-network-safety-graph-v176');
    if(previous)previous.remove();
    const script=document.createElement('script');
    script.id='alo186-home-network-safety-graph-v176';
    script.type='application/ld+json';
    script.textContent=JSON.stringify(data.knowledgeGraph(new Date()));
    document.head.appendChild(script);
  }

  document.addEventListener('DOMContentLoaded',()=>{
    renderFilters();
    injectKnowledgeGraph();
    ['gateExisting','gateTechnical','gateAffiliate'].forEach(id=>$(id)?.addEventListener('change',()=>{
      render();
      emit('affiliate_home_network_gate',{open:gateOpen(),field:id});
    }));
    $('resetGate')?.addEventListener('click',()=>{
      ['gateExisting','gateTechnical','gateAffiliate'].forEach(id=>{if($(id))$(id).checked=false;});
      render();
      emit('affiliate_home_network_gate_reset');
    });
    render();
    emit('affiliate_home_network_collection_viewed',{exact_count:data.products.length,class_count:data.productClasses.length,version:data.version});
  });
})();
