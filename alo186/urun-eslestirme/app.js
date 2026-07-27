(() => {
  'use strict';

  const $=id=>document.getElementById(id);
  const catalog=window.Alo186ProductCatalog;
  const matcher=window.Alo186ProductMatcher;
  let selectedCategory=null;

  const guideChecks={
    mini_ups:[
      ['Çıkış gerilimi','Modem ve ONT etiketindeki 5 V, 9 V veya 12 V değeriyle tam eşleşmeli.'],
      ['Jak ve polarite','Jak dış/iç ölçüsü ile merkez artı/eksi polaritesi doğrulanmalı.'],
      ['Toplam watt','Modem + ONT + varsa switch toplamı güvenlik payıyla hesaplanmalı.'],
      ['Geçiş davranışı','Şebeke kesildiğinde yeniden başlatmadan devam edip etmediği doğrulanmalı.']
    ],
    emergency_light:[
      ['Düşük mod süresi','En parlak mod yerine uzun süre kullanılabilen düşük mod süresini karşılaştırın.'],
      ['Fiziksel düğme','Karanlıkta uygulama gerektirmeden açılabilmeli.'],
      ['Pil göstergesi','Şarj seviyesinin önceden görülebilmesi hazırlığı kolaylaştırır.'],
      ['Taşıma ve asma','Odayı aydınlatma ile el feneri ihtiyacını birbirinden ayırın.']
    ],
    smoke_alarm:[
      ['Standart','Ürün ve ambalaj üzerinde EN 14604 uygunluk bilgisini doğrulayın.'],
      ['Test ve düşük pil','Test düğmesi ile sesli düşük pil uyarısı bulunmalı.'],
      ['Sensör ve ömür','Fotoelektrik sensör, üretim tarihi ve son kullanım/ürün ömrü belirtilmeli.'],
      ['Yerleşim','Üretici montaj konumuna uyun; mutfak buharı ve hava akımlarını dikkate alın.']
    ],
    power_station:[
      ['Enerji kapasitesi','Hedef süre için Wh hesabını yapın; etiket kapasitesinin tamamı kullanılamaz.'],
      ['Sürekli ve tepe güç','Motor/kompresör kalkış gücü dahil yükü karşılamalı.'],
      ['Dalga biçimi','Kombi, motor ve hassas cihazlarda saf sinüs gereksinimini doğrulayın.'],
      ['Batarya ve girişler','LiFePO₄ çevrim ömrü, AC/DC/solar giriş sınırları ve konektör uyumunu kontrol edin.']
    ],
    outlet_tester:[
      ['Gösterge kapsamı','LED deseninin hangi temel bağlantı hatalarını gösterebildiğini okuyun.'],
      ['RCD testi','Test akımı ve uyumlu nominal kaçak akım değeri belirtilmeli.'],
      ['Gerilim bölgesi','230 V / Türkiye priz standardıyla uyumlu olmalı.'],
      ['Sınır','Topraklama direnci, izolasyon veya açma süresi ölçümü yerine geçmediğini kabul edin.']
    ]
  };

  function emit(name,params={}){
    if(typeof window.Alo186Track==='function')window.Alo186Track(name,params);
  }

  function renderCategories(){
    $('categoryGrid').innerHTML=catalog.categories.map(category=>`<button type="button" class="category-button" data-category="${category.id}" aria-pressed="false"><strong>${escapeHtml(category.name)}</strong><small>${escapeHtml(category.description)}</small></button>`).join('');
    $('categoryGrid').querySelectorAll('[data-category]').forEach(button=>button.addEventListener('click',()=>selectCategory(button.dataset.category)));
  }

  function selectCategory(id){
    selectedCategory=id;
    const category=catalog.getCategory(id);
    document.querySelectorAll('[data-category]').forEach(button=>button.setAttribute('aria-pressed',button.dataset.category===id?'true':'false'));
    $('requirements').classList.remove('hidden');
    $('requirementsTitle').textContent=category.mode==='direct'?'Teknik minimumları girin':'Satın almadan önce kontrol edin';
    $('requirementFields').innerHTML=requirementMarkup(id,category);
    $('matchBtn').textContent=category.mode==='direct'?'Uygun seçenekleri göster':'Kontrol listesini göster';
    $('validation').textContent='';
    $('results').classList.add('hidden');
    emit('product_category_selected',{category:id,mode:category.mode,risk:category.risk});
    $('requirements').scrollIntoView({behavior:'smooth',block:'nearest'});
  }

  function requirementMarkup(id,category){
    if(id==='powerbank')return `<div class="form-grid"><label class="field"><span>Minimum kapasite</span><select id="minCapacity"><option value="10000">10.000 mAh</option><option value="20000" selected>20.000 mAh</option></select></label><label class="field"><span>Minimum çıkış gücü</span><select id="minOutput"><option value="10">10 W — temel telefon</option><option value="25" selected>25 W — hızlı telefon/tablet</option><option value="65">65 W — uyumlu dizüstü</option><option value="100">100 W — yüksek güçlü dizüstü</option></select></label><label class="check-item field full"><input id="needWireless" type="checkbox"><span><b>Kablosuz şarj gerekli</b><br><small>Kablolu gücü ayrıca kontrol edin.</small></span></label></div>`;
    if(id==='surge_strip')return `<div class="form-grid"><label class="field"><span>Minimum priz sayısı</span><select id="minOutlets"><option value="1">1</option><option value="5" selected>5</option><option value="6">6</option></select></label><label class="field"><span>Minimum enerji sönümleme</span><select id="minJoules"><option value="250">250 J</option><option value="900" selected>900 J</option><option value="1000">1.000 J</option></select></label><label class="check-item field full"><input id="needUsb" type="checkbox"><span><b>USB çıkışı gerekli</b><br><small>USB özelliklerinin hızlı şarj protokolünü ayrıca doğrulayın.</small></span></label></div>`;
    const checks=guideChecks[id]||[];
    return `<p>${escapeHtml(category.description)}</p><div class="guide-list">${checks.map(([title,text])=>`<div class="guide-item"><b>${escapeHtml(title)}</b><span>${escapeHtml(text)}</span></div>`).join('')}</div>`;
  }

  function requirements(){
    if(selectedCategory==='powerbank')return {minCapacityMah:Number(document.getElementById('minCapacity').value),minOutputW:Number(document.getElementById('minOutput').value),wireless:document.getElementById('needWireless').checked};
    if(selectedCategory==='surge_strip')return {minOutlets:Number(document.getElementById('minOutlets').value),minJoules:Number(document.getElementById('minJoules').value),usb:document.getElementById('needUsb').checked};
    return {};
  }

  function runMatch(){
    $('validation').textContent='';
    if(!selectedCategory){$('validation').textContent='Önce bir ihtiyaç seçin.';return;}
    try{
      const req=requirements();
      const result=matcher.match(selectedCategory,req);
      $('results').classList.remove('hidden');
      $('resultTitle').textContent=result.category.name;
      $('requirementsChip').textContent=matcher.requirementsSummary(selectedCategory,req);
      $('resultText').textContent=result.mode==='direct'?`${result.matches.length} teknik eşleşme bulundu. Fiyat ve stok Amazon’da doğrulanır.`:'Bu kategoride ürün adından önce aşağıdaki teknik kontrol listesini tamamlayın.';
      $('directResult').classList.toggle('hidden',result.mode!=='direct');
      $('guideResult').classList.toggle('hidden',result.mode!=='guide');
      if(result.mode==='direct')renderProducts(result,req);else renderGuide(result);
      $('results').scrollIntoView({behavior:'smooth',block:'start'});
      emit('product_match_completed',{category:selectedCategory,mode:result.mode,match_count:result.matches.length,professional_required:result.professionalSelectionRequired});
    }catch(error){$('validation').textContent=error.message;}
  }

  function renderProducts(result,req){
    if(!result.matches.length){
      $('directResult').innerHTML=`<div class="empty-products"><h3>Bu minimumları karşılayan doğrulanmış kart bulunamadı.</h3><p>Genel aramada teknik alanları ve satıcı bilgisini yeniden doğrulayın.</p><a class="btn btn-primary" href="${escapeAttr(result.searchUrl)}" target="_blank" rel="sponsored nofollow noopener">Amazon’da filtreli aramayı aç</a></div>`;
      return;
    }
    $('directResult').innerHTML=result.matches.map(item=>productCard(item)).join('');
    $('directResult').querySelectorAll('[data-product]').forEach(link=>link.addEventListener('click',()=>emit('affiliate_product_clicked',{category:selectedCategory,product_id:link.dataset.product,asin:link.dataset.asin,match_score:Number(link.dataset.score),placement:'smart_matcher'})));
  }

  function productCard(item){
    const p=item.product;
    return `<article class="product-card"><div class="product-head"><span class="rank-label">${escapeHtml(item.label)}</span><h3>${escapeHtml(p.name)}</h3><span class="product-brand">${escapeHtml(p.brand)} · ASIN ${escapeHtml(p.asin)}</span></div><div class="score-row"><strong>${item.score}/100</strong><span>Uygunluk · güven ${escapeHtml(item.confidence||'Orta')}</span></div><div class="product-body"><div><h4>Neden eşleşti?</h4><ul>${item.reasons.map(x=>`<li>${escapeHtml(x)}</li>`).join('')}</ul></div><div><h4>Güçlü yanlar</h4><ul>${p.strengths.map(x=>`<li>${escapeHtml(x)}</li>`).join('')}</ul></div><div><h4>Sınırlar</h4><ul>${p.limits.map(x=>`<li>${escapeHtml(x)}</li>`).join('')}</ul></div>${item.unknowns.length?`<div class="unknowns"><b>Yeniden doğrulayın:</b> ${item.unknowns.map(escapeHtml).join(' ')}</div>`:''}<div class="verification">Teknik liste kontrolü: ${escapeHtml(p.verifiedAt)}<br>${escapeHtml(p.sourceNote)}</div></div><div class="product-actions"><a class="btn btn-primary" data-product="${escapeAttr(p.id)}" data-asin="${escapeAttr(p.asin)}" data-score="${item.score}" href="${escapeAttr(p.url)}" target="_blank" rel="sponsored nofollow noopener">Amazon ürün sayfasını aç</a></div></article>`;
  }

  function renderGuide(result){
    const checks=guideChecks[selectedCategory]||[];
    $('guideResult').innerHTML=`<span class="eyebrow">Rehberli seçim</span><h3>Ürün adından önce bu alanları doğrulayın</h3><div class="guide-list">${checks.map(([title,text])=>`<div class="guide-item"><b>${escapeHtml(title)}</b><span>${escapeHtml(text)}</span></div>`).join('')}</div>${result.professionalSelectionRequired?`<div class="professional-note"><b>Profesyonel seçim sınırı:</b> Bu kategoride bağlantı, tesisat, standart veya ölçüm uyumu yanlış ürün riskini artırır. Sonuç bir uygunluk onayı değildir.</div>`:''}<div class="actions"><a class="btn btn-primary" id="guideAmazonLink" href="${escapeAttr(result.searchUrl)}" target="_blank" rel="sponsored nofollow noopener">Amazon’da teknik ifadelerle ara</a>${result.professionalSelectionRequired?'<a class="btn btn-secondary" href="https://www.alo186.com/iletisim?konu=urun-teknik-secim">Teknik ön değerlendirme</a>':''}</div>`;
    const link=document.getElementById('guideAmazonLink');
    if(link)link.addEventListener('click',()=>emit('affiliate_category_clicked',{category:selectedCategory,placement:'smart_matcher_guide'}));
  }

  function reset(){selectedCategory=null;document.querySelectorAll('[data-category]').forEach(button=>button.setAttribute('aria-pressed','false'));$('requirements').classList.add('hidden');$('results').classList.add('hidden');$('validation').textContent='';window.scrollTo({top:$('matcher').offsetTop-80,behavior:'smooth'});}
  function escapeHtml(value){return String(value??'').replace(/[&<>"]/g,ch=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[ch]));}
  function escapeAttr(value){return escapeHtml(value).replace(/'/g,'&#39;');}

  document.addEventListener('DOMContentLoaded',()=>{
    if(!catalog||!matcher){$('validation').textContent='Ürün kataloğu yüklenemedi.';return;}
    renderCategories();
    $('matchBtn').addEventListener('click',runMatch);
    $('resetBtn').addEventListener('click',reset);
    const query=new URLSearchParams(location.search).get('kategori');
    if(query&&catalog.getCategory(query))selectCategory(query);
  });
})();
