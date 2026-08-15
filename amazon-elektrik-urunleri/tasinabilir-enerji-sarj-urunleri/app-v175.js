(() => {
  'use strict';

  const data=window.Alo186ExactAffiliateProductsV175;
  if(!data)throw new Error('ALO186 doğrulanmış ürün verisi yüklenemedi.');

  const $=id=>document.getElementById(id);
  const categoryLabels={all:'Tümü',charger:'Şarj',hub:'Hub ve ağ',display:'Görüntü',travel:'Seyahat ve araç'};
  let activeCategory='all';

  function escapeHtml(value){
    return String(value??'').replace(/[&<>"']/g,char=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
  }
  function emit(name,params={}){
    if(typeof window.Alo186Track==='function')window.Alo186Track(name,params);
  }
  function dateOnly(value){
    const date=new Date(`${value}T00:00:00Z`);
    return Number.isNaN(date.getTime())?null:date;
  }
  function ageDays(value){
    const checked=dateOnly(value);
    if(!checked)return Infinity;
    return Math.max(0,Math.floor((Date.now()-checked.getTime())/86400000));
  }
  function fresh(item){return ageDays(item.verifiedAt)<=data.verificationMaxAgeDays;}
  function gateOpen(){
    return Boolean($('gateExisting')?.checked&&$('gateTechnical')?.checked&&$('gateAffiliate')?.checked);
  }
  function filterMatch(category){return activeCategory==='all'||category===activeCategory;}

  function actionMarkup(item,kind){
    if(!fresh(item))return '<span class="blocked-action">Teknik kontrol tarihi yenileniyor</span>';
    if(!gateOpen())return '<button type="button" class="shop locked" disabled>Üç onaydan sonra açılır</button>';
    const placement=kind==='exact'?'exact_model':'product_class';
    return `<a class="shop" data-affiliate-link data-placement="${placement}" data-item="${escapeHtml(item.id)}" href="${escapeHtml(item.amazonUrl)}" target="_blank" rel="sponsored nofollow noopener"><small>Satış ortaklığı bağlantısı</small>${kind==='exact'?'Amazon ürün sayfasını aç':'Amazon seçeneklerini incele'}</a>`;
  }

  function exactCard(product){
    return `<article class="card exact-card" id="model-${escapeHtml(product.id)}" data-category="${escapeHtml(product.category)}">
      <div class="card-top"><span class="pill">${escapeHtml(categoryLabels[product.category]||product.category)}</span><span class="freshness">Kontrol: ${escapeHtml(product.verifiedAt)}</span></div>
      <h2>${escapeHtml(product.name)}</h2>
      <p class="model">${escapeHtml(product.brand)} · ${escapeHtml(product.mpn||'Model kodu yok')} · ASIN ${escapeHtml(product.asin)}</p>
      <p><strong>Çözdüğü ihtiyaç:</strong> ${escapeHtml(product.userNeed)}</p>
      <details><summary>Teknik kanıt ve satın almama sınırı</summary>
        <h3>Doğrulanan alanlar</h3><ul>${product.facts.map(item=>`<li>${escapeHtml(item)}</li>`).join('')}</ul>
        <h3>En uygun kullanım</h3><ul>${product.bestFor.map(item=>`<li>${escapeHtml(item)}</li>`).join('')}</ul>
        <h3>Satın almadan önce</h3><ul>${product.evidence.map(item=>`<li>${escapeHtml(item)}</li>`).join('')}</ul>
        <h3>Bu durumda almayın</h3><ul>${product.noBuyWhen.map(item=>`<li>${escapeHtml(item)}</li>`).join('')}</ul>
      </details>
      <div class="source-row"><a href="${escapeHtml(product.technicalSource)}" target="_blank" rel="external noopener noreferrer">Teknik kaynağı doğrula ↗</a></div>
      <div class="affiliate-action">${actionMarkup(product,'exact')}</div>
    </article>`;
  }

  function classCard(item){
    return `<article class="card class-card" data-category="${escapeHtml(item.category)}">
      <span class="pill">Ürün sınıfı</span><h2>${escapeHtml(item.name)}</h2>
      <p><strong>Önce doğrulayın:</strong> ${item.evidence.map(escapeHtml).join(' · ')}</p>
      <p><strong>Almayın:</strong> ${escapeHtml(item.noBuyWhen)}</p>
      <div class="source-row"><a href="${escapeHtml(item.tool)}">Ücretsiz teknik kontrolü aç →</a></div>
      <div class="affiliate-action">${actionMarkup({...item,verifiedAt:data.generatedAt},'class')}</div>
    </article>`;
  }

  function bindAffiliateEvents(){
    document.querySelectorAll('[data-affiliate-link]').forEach(link=>{
      link.addEventListener('click',()=>emit('affiliate_exact_product_clicked',{
        item_id:link.dataset.item,
        placement:link.dataset.placement,
        collection:'portable_energy_v175'
      }));
    });
  }

  function render(){
    const exact=data.products.filter(item=>filterMatch(item.category));
    const classes=data.productClasses.filter(item=>filterMatch(item.category));
    $('exactCount').textContent=String(exact.length);
    $('exactProducts').innerHTML=exact.map(exactCard).join('');
    $('productClasses').innerHTML=classes.map(classCard).join('');
    const open=gateOpen();
    $('gateStatus').textContent=open
      ? 'Teknik ve ticari sınırlar onaylandı. Bağlantılar bu oturum için açıldı.'
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
      emit('affiliate_exact_product_filter',{category:activeCategory});
    }));
  }

  function appendRevenueHubLink(){
    const related=document.querySelector('.related');
    if(!related||related.querySelector('[data-affiliate-revenue-v177]'))return;
    const link=document.createElement('a');
    link.href='/amazon-elektrik-urunleri/dogrulanmis-tak-calistir-urunler/';
    link.dataset.affiliateRevenueV177='true';
    link.innerHTML='<strong>Powerbank, araç şarjı, kablo ve AA/AAA pil kataloğu</strong><br><small>Güncel doğrulanmış modelleri, 25+ ürün sınıfını ve yedi kullanım paketini birlikte açın.</small>';
    link.addEventListener('click',()=>emit('affiliate_revenue_v177_entry',{placement:'portable_energy_related'}));
    related.appendChild(link);
  }

  function injectKnowledgeGraph(){
    const existing=document.getElementById('alo186-exact-affiliate-graph-v175');
    if(existing)existing.remove();
    const script=document.createElement('script');
    script.id='alo186-exact-affiliate-graph-v175';
    script.type='application/ld+json';
    script.textContent=JSON.stringify({
      '@context':'https://schema.org',
      '@graph':[
        {
          '@type':'DefinedTermSet',
          '@id':'https://alo186.com/amazon-elektrik-urunleri/tasinabilir-enerji-sarj-urunleri/#verified-models',
          name:'ALO186 doğrulanmış tak-çalıştır model kayıtları',
          hasDefinedTerm:data.products.map(item=>({'@id':`https://alo186.com/amazon-elektrik-urunleri/tasinabilir-enerji-sarj-urunleri/#${item.id}`}))
        },
        ...data.products.map(item=>({
          '@type':'DefinedTerm',
          '@id':`https://alo186.com/amazon-elektrik-urunleri/tasinabilir-enerji-sarj-urunleri/#${item.id}`,
          name:item.name,
          termCode:item.mpn||item.asin,
          description:`${item.userNeed}. Teknik kontrol: ${item.verifiedAt}.`,
          inDefinedTermSet:{'@id':'https://alo186.com/amazon-elektrik-urunleri/tasinabilir-enerji-sarj-urunleri/#verified-models'},
          subjectOf:item.technicalSource
        }))
      ]
    });
    document.head.appendChild(script);
  }

  document.addEventListener('DOMContentLoaded',()=>{
    renderFilters();
    appendRevenueHubLink();
    injectKnowledgeGraph();
    ['gateExisting','gateTechnical','gateAffiliate'].forEach(id=>$(id)?.addEventListener('change',()=>{
      render();
      emit('affiliate_exact_product_gate',{open:gateOpen(),field:id});
    }));
    $('resetGate')?.addEventListener('click',()=>{
      ['gateExisting','gateTechnical','gateAffiliate'].forEach(id=>{if($(id))$(id).checked=false;});
      render();
    });
    render();
    emit('affiliate_exact_product_collection_viewed',{exact_count:data.products.length,class_count:data.productClasses.length,version:data.version});
  });
})();
