(() => {
  'use strict';

  const core=window.Alo186TrustGrowthCore;
  const catalog=window.Alo186ProductCatalog;
  if(!core||!catalog)return;

  const $=id=>document.getElementById(id);
  const state={categoryId:null,existing:{status:'none',purchaseNeeded:true,reasons:[],missing:[]},quality:null};
  let renderTimer=null;
  let lastEventSignature='';

  function emit(name,params={}){
    const clean=core.sanitizeEvent(params);
    if(core.hasForbiddenEventData(clean))return;
    if(typeof window.Alo186Track==='function')window.Alo186Track(name,clean);
  }

  function escapeHtml(value){return String(value??'').replace(/[&<>"']/g,ch=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));}
  function activeCategoryId(){return document.querySelector('[data-category][aria-pressed="true"]')?.dataset.category||null;}
  function isDirectCategory(id){return id==='powerbank'||id==='surge_strip';}

  function requirementValues(){
    const result={};
    document.querySelectorAll('#requirementFields [data-field]').forEach(input=>{
      result[input.dataset.field]=input.type==='checkbox'?Boolean(input.checked):Number(input.value);
    });
    return result;
  }

  function existingValues(){
    const root=$('existingEquipmentCheck');
    if(!root)return {owned:false};
    const value=name=>root.querySelector(`[data-existing="${name}"]`)?.value||'';
    const selectedBoolean=name=>{
      const raw=value(name);
      return raw===''?null:raw==='true';
    };
    return {
      owned:Boolean(root.querySelector('[data-existing-owned]')?.checked),
      capacityMah:value('capacityMah')===''?null:Number(value('capacityMah')),
      maxOutputW:value('maxOutputW')===''?null:Number(value('maxOutputW')),
      wireless:selectedBoolean('wireless'),
      outlets:value('outlets')===''?null:Number(value('outlets')),
      joules:value('joules')===''?null:Number(value('joules')),
      usb:selectedBoolean('usb')
    };
  }

  function existingFields(categoryId){
    if(categoryId==='powerbank')return `<div class="form-grid existing-grid"><label class="field"><span>Mevcut kapasite</span><select data-existing="capacityMah"><option value="">Etiketten kontrol edeceğim</option><option value="10000">10.000 mAh</option><option value="20000">20.000 mAh</option><option value="30000">30.000 mAh</option><option value="50000">50.000 mAh</option></select></label><label class="field"><span>Mevcut azami çıkış</span><select data-existing="maxOutputW"><option value="">Etiketten kontrol edeceğim</option><option value="10">10 W</option><option value="25">25 W</option><option value="45">45 W</option><option value="65">65 W</option><option value="100">100 W</option><option value="200">200 W</option></select></label><label class="field full"><span>Mevcut üründe kablosuz şarj</span><select data-existing="wireless"><option value="">Bilinmiyor / gerekmiyor</option><option value="true">Var</option><option value="false">Yok</option></select></label></div>`;
    if(categoryId==='surge_strip')return `<div class="form-grid existing-grid"><label class="field"><span>Mevcut priz sayısı</span><select data-existing="outlets"><option value="">Etiketten kontrol edeceğim</option><option value="1">1</option><option value="3">3</option><option value="5">5</option><option value="6">6</option><option value="8">8</option></select></label><label class="field"><span>Mevcut enerji sönümleme</span><select data-existing="joules"><option value="">Joule değeri bilinmiyor</option><option value="250">250 J</option><option value="500">500 J</option><option value="900">900 J</option><option value="1000">1.000 J</option><option value="2000">2.000 J</option></select></label><label class="field full"><span>Mevcut üründe USB çıkışı</span><select data-existing="usb"><option value="">Bilinmiyor / gerekmiyor</option><option value="true">Var</option><option value="false">Yok</option></select></label></div>`;
    return '';
  }

  function ensureExistingPanel(){
    const categoryId=activeCategoryId();
    state.categoryId=categoryId;
    const requirements=$('requirements');
    if(!requirements)return;
    let panel=$('existingEquipmentCheck');
    if(!isDirectCategory(categoryId)){
      panel?.remove();
      state.existing={status:'unsupported',purchaseNeeded:null,reasons:[],missing:[]};
      return;
    }
    if(panel&&panel.dataset.category===categoryId)return;
    panel?.remove();
    panel=document.createElement('section');
    panel.id='existingEquipmentCheck';
    panel.className='existing-equipment-check';
    panel.dataset.category=categoryId;
    panel.innerHTML=`<div class="section-title"><div><span class="step">2A</span><h3>Yeni ürün almadan önce mevcut ekipmanı kontrol edin</h3></div></div><p>Mevcut ürün seçtiğiniz teknik minimumu karşılıyorsa satın almamak geçerli ve önerilen sonuçtur. Buradaki bilgiler kaydedilmez veya sunucuya gönderilmez.</p><label class="check-item"><input type="checkbox" data-existing-owned><span><b>Bu ihtiyaca hizmet eden mevcut bir ürünüm var.</b><br><small>Etiketteki teknik değerleri girerek yeterliliğini kontrol edin.</small></span></label><div class="existing-fields hidden" data-existing-fields>${existingFields(categoryId)}</div><div class="existing-status" data-existing-status role="status"></div>`;
    const actions=requirements.querySelector('.actions');
    requirements.insertBefore(panel,actions||null);
    panel.querySelector('[data-existing-owned]').addEventListener('change',event=>{
      panel.querySelector('[data-existing-fields]').classList.toggle('hidden',!event.target.checked);
      evaluateAndRender();
    });
    panel.querySelectorAll('[data-existing]').forEach(input=>input.addEventListener('change',evaluateAndRender));
  }

  function assessExisting(){
    const categoryId=activeCategoryId();
    if(!isDirectCategory(categoryId))return {status:'unsupported',purchaseNeeded:null,reasons:[],missing:[]};
    return core.assessExistingProduct(categoryId,requirementValues(),existingValues());
  }

  function productSnapshot(card){
    const link=card.querySelector('[data-product]');
    const product=catalog.products.find(item=>item.id===link?.dataset.product);
    const confidence=card.querySelector('.score-row span')?.textContent.replace(/^Uygunluk · güven\s*/i,'').trim()||'';
    const unknownText=card.querySelector('.unknowns')?.textContent.replace(/^Yeniden doğrulayın:\s*/i,'').trim()||'';
    return {
      productId:link?.dataset.product||'',
      score:Number(link?.dataset.score),
      confidence,
      unknowns:unknownText?unknownText.split(/[.;]\s*/).filter(Boolean):[],
      verifiedAt:product?.verifiedAt||''
    };
  }

  function evaluateCard(card){
    const snapshot=productSnapshot(card);
    return {...core.affiliateEligibility({...snapshot,existingStatus:state.existing.status}),snapshot};
  }

  function renderCardConfidence(){
    document.querySelectorAll('#directResult .product-card').forEach(card=>{
      const result=evaluateCard(card);
      let note=card.querySelector('[data-trust-confidence-note]');
      if(!note){
        note=document.createElement('div');
        note.dataset.trustConfidenceNote='true';
        note.className='trust-confidence-note';
        card.querySelector('.product-body')?.appendChild(note);
      }
      note.classList.toggle('is-ready',result.allowed);
      note.classList.toggle('is-blocked',!result.allowed);
      note.innerHTML=result.allowed?`<strong>Yüksek güvenli teknik kart</strong><span>Temel katalog alanları güncel ve eksiksiz görünüyor. Satın alma bağlantısı yine ihtiyaç ve satış ortaklığı kontrolünden geçer.</span>`:`<strong>Doğrudan ürün bağlantısı kapalı</strong><span>${escapeHtml(result.message)}</span>`;
    });
  }

  function catalogStaleCount(categoryId){
    if(!categoryId)return 0;
    const all=catalog.productsFor(categoryId,{now:new Date(),freshOnly:false});
    const fresh=catalog.productsFor(categoryId,{now:new Date(),freshOnly:true});
    return Math.max(0,all.length-fresh.length);
  }

  function decisionState(){
    const categoryId=activeCategoryId();
    const guideVisible=!$('guideResult')?.classList.contains('hidden');
    if(guideVisible)return {score:100,band:'teknik_arac_once',title:'Ürün bağlantısından önce teknik araç',nextAction:'Bu kategori bağlantı, ölçüm veya sabit tesisat riski taşıyor. Ücretsiz hesaplayıcıya veya uzman kontrolüne ilerleyin.',matchCount:0,highConfidenceCount:0,lowConfidenceCount:0,staleCount:0};
    const cards=[...document.querySelectorAll('#directResult .product-card')];
    const assessments=cards.map(evaluateCard);
    const highConfidenceCount=assessments.filter(item=>item.allowed||item.reason==='existing_equipment_adequate').length;
    const lowConfidenceCount=assessments.length-highConfidenceCount;
    const staleCount=catalogStaleCount(categoryId);
    const quality=core.decisionQuality({existingStatus:state.existing.status,matchCount:cards.length,highConfidenceCount,lowConfidenceCount,staleCount});
    return {...quality,matchCount:cards.length,highConfidenceCount,lowConfidenceCount,staleCount};
  }

  function ensureQualityPanel(){
    let panel=$('decisionQuality');
    if(panel)return panel;
    panel=document.createElement('section');
    panel.id='decisionQuality';
    panel.className='content-section decision-quality hidden';
    panel.setAttribute('aria-live','polite');
    panel.innerHTML='<div class="panel"><div class="section-title"><div><span class="eyebrow">Karar kalitesi</span><h2>Satın alma bağlantısından önce hangi aşamadasınız?</h2></div><strong class="quality-score" data-quality-score></strong></div><div class="quality-grid" data-quality-grid></div><div class="quality-summary"><h3 data-quality-title></h3><p data-quality-action></p></div><div class="actions"><button type="button" class="btn btn-primary" data-quality-save>Teknik ihtiyacı 30 gün cihazımda sakla</button><button type="button" class="btn btn-secondary" data-quality-recheck>Teknik minimumlara dön</button></div><small>Mevcut ürün değerleri bu kayda eklenmez. Teknik ihtiyaç dosyası fiyat, stok, satıcı, garanti veya kişisel veri içermez.</small></div>';
    const brief=$('decisionBrief');
    if(brief)brief.parentNode.insertBefore(panel,brief);
    else $('results')?.insertAdjacentElement('afterend',panel);
    panel.querySelector('[data-quality-save]').addEventListener('click',()=>{
      const save=$('saveBriefBtn');
      if(save){save.click();$('decisionBrief')?.scrollIntoView({behavior:'smooth',block:'nearest'});}
      else $('decisionBrief')?.scrollIntoView({behavior:'smooth',block:'nearest'});
    });
    panel.querySelector('[data-quality-recheck]').addEventListener('click',()=>$('requirements')?.scrollIntoView({behavior:'smooth',block:'start'}));
    return panel;
  }

  function renderExistingStatus(){
    const root=$('existingEquipmentCheck');
    if(!root)return;
    const status=root.querySelector('[data-existing-status]');
    const result=state.existing;
    const mapping={
      none:['Mevcut ürün kontrolü atlandı.','Yeni ürün ihtiyacı satın alma kapısında ayrıca onaylanır.'],
      adequate:['Mevcut ürün yeterli görünüyor.','Yeni ürün satın almak gerekmeyebilir; ürün bağlantıları kapalı tutulur.'],
      insufficient:['Mevcut ürün ihtiyacı karşılamıyor.','Eksik teknik alanlar yeni ürün karşılaştırmasında görünür.'],
      unknown:['Mevcut ürün yeterliliği belirlenemedi.','Etiketteki eksik değerler tamamlanmadan ürün bağlantısı açılmaz.']
    };
    const copy=mapping[result.status]||['Mevcut ürün değerlendirmesi tamamlanmadı.',''];
    const details=[...result.reasons,...result.missing].map(item=>`<li>${escapeHtml(item)}</li>`).join('');
    status.className=`existing-status status-${escapeHtml(result.status)}`;
    status.innerHTML=`<strong>${copy[0]}</strong><p>${copy[1]}</p>${details?`<ul>${details}</ul>`:''}`;
  }

  function renderQuality(){
    const results=$('results');
    const panel=ensureQualityPanel();
    if(!results||results.classList.contains('hidden')){panel.classList.add('hidden');return;}
    const quality=decisionState();
    state.quality=quality;
    panel.classList.remove('hidden');
    panel.dataset.band=quality.band;
    panel.querySelector('[data-quality-score]').textContent=quality.band==='teknik_arac_once'?'Araç önce':`${quality.score}/100`;
    panel.querySelector('[data-quality-title]').textContent=quality.title;
    panel.querySelector('[data-quality-action]').textContent=quality.nextAction;
    panel.querySelector('[data-quality-grid]').innerHTML=`<div><small>Mevcut ürün</small><strong>${escapeHtml(existingLabel(state.existing.status))}</strong></div><div><small>Güncel eşleşme</small><strong>${quality.matchCount}</strong></div><div><small>Yüksek güvenli kart</small><strong>${quality.highConfidenceCount}</strong></div><div><small>Eski doğrulama</small><strong>${quality.staleCount}</strong></div>`;
    const signature=JSON.stringify([state.categoryId,state.existing.status,quality.band,quality.matchCount,quality.staleCount]);
    if(signature!==lastEventSignature){
      lastEventSignature=signature;
      emit('product_decision_quality_rendered',{category:state.categoryId||'unknown',existing_status:state.existing.status,readiness_band:quality.band,match_count:quality.matchCount,stale_count:quality.staleCount,purchase_needed:state.existing.purchaseNeeded===true});
      if(quality.band==='dogrulanmis_eslesme_yok'||quality.band==='katalog_yenileme_bekleniyor'||quality.band==='eksik_teknik_veri')emit('product_requirement_gap_detected',{category:state.categoryId||'unknown',reason:quality.band,match_count:quality.matchCount,stale_count:quality.staleCount});
    }
  }

  function existingLabel(status){
    return ({none:'Beyan edilmedi',adequate:'Yeterli',insufficient:'Yetersiz',unknown:'Etiket eksik',unsupported:'Teknik araç gerekir'})[status]||'—';
  }

  function evaluateAndRender(){
    state.categoryId=activeCategoryId();
    state.existing=assessExisting();
    renderExistingStatus();
    renderCardConfidence();
    renderQuality();
    emit('existing_equipment_assessed',{category:state.categoryId||'unknown',status:state.existing.status,purchase_needed:state.existing.purchaseNeeded===true});
  }

  function scheduleRender(){
    window.clearTimeout(renderTimer);
    renderTimer=window.setTimeout(()=>{
      ensureExistingPanel();
      evaluateAndRender();
    },0);
  }

  function bind(){
    document.addEventListener('click',event=>{
      if(event.target.closest?.('[data-category]'))scheduleRender();
      if(event.target.closest?.('#matchBtn'))scheduleRender();
    });
    const result=$('results');
    if(result){
      const observer=new MutationObserver(scheduleRender);
      observer.observe(result,{subtree:true,childList:true,attributes:true,attributeFilter:['class']});
    }
    const requirements=$('requirements');
    if(requirements){
      const observer=new MutationObserver(()=>{if(activeCategoryId())ensureExistingPanel();});
      observer.observe(requirements,{subtree:true,childList:true});
    }
  }

  window.Alo186TrustGrowth={
    getState:()=>({categoryId:state.categoryId,existingStatus:state.existing.status,purchaseNeeded:state.existing.purchaseNeeded,quality:state.quality}),
    evaluateCard,
    refresh:scheduleRender
  };

  document.addEventListener('DOMContentLoaded',()=>{
    bind();
    ensureQualityPanel();
    scheduleRender();
  });
})();
