(() => {
  'use strict';

  const core=window.Alo186JourneyRetentionCore;
  if(!core)return;

  const $=id=>document.getElementById(id);
  let selectedCategory=null;
  let maintenanceState=readMaintenance();
  let reviews=readReviews();

  function emit(name,params={}){
    const clean=core.sanitizeEvent(params);
    if(core.hasForbiddenEventData(params))return;
    if(typeof window.Alo186Track==='function')window.Alo186Track(name,clean);
  }

  function readJson(key,fallback){
    try{return JSON.parse(localStorage.getItem(key)||JSON.stringify(fallback));}
    catch(error){return fallback;}
  }

  function writeJson(key,value){
    try{localStorage.setItem(key,JSON.stringify(value));return true;}
    catch(error){return false;}
  }

  function readReviews(){return core.sanitizeReviews(readJson(core.reviewStorageKey,[]),new Date());}
  function readMaintenance(){return core.sanitizeMaintenance(readJson(core.maintenanceStorageKey,{}));}

  function escapeHtml(value){return String(value??'').replace(/[&<>'"]/g,char=>({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[char]));}
  function escapeAttr(value){return escapeHtml(value).replace(/`/g,'&#96;');}

  function formatDate(value){
    const date=new Date(`${value}T12:00:00Z`);
    if(Number.isNaN(date.getTime()))return 'Bilinmiyor';
    return new Intl.DateTimeFormat('tr-TR',{day:'numeric',month:'long',year:'numeric',timeZone:'UTC'}).format(date);
  }

  function dueText(item){
    const band=core.dueBand(item.reviewDate,new Date());
    if(band==='overdue')return {band,text:'Yeniden kontrol tarihi geçti'};
    if(band==='today')return {band,text:'Bugün yeniden kontrol edin'};
    if(band==='soon')return {band,text:'Yedi gün içinde yeniden kontrol'};
    return {band,text:`${formatDate(item.reviewDate)} tarihinde yeniden kontrol`};
  }

  function renderJourney(category){
    const journey=core.getJourney(category);
    if(!journey)return;
    selectedCategory=category;
    $('journeyRetention').classList.remove('hidden');
    $('journeyCategoryTitle').textContent=journey.label;
    $('journeyReason').textContent=journey.reviewReason;
    $('journeyStages').innerHTML=[
      ['Öğren',journey.learn,'learn'],
      ['Hesapla / kontrol et',journey.calculate,'calculate'],
      ['Karşılaştır',journey.compare,'compare']
    ].map(([eyebrow,item,stage])=>`<a class="journey-stage" href="${escapeAttr(item.url)}" data-journey-stage="${stage}"><span>${escapeHtml(eyebrow)}</span><strong>${escapeHtml(item.label)}</strong><small>${stage==='compare'?(journey.professionalOnly?'Ürün bağlantısı yerine uzmanlık ve güvenlik sınırı':'Teknik minimum doğrulandıktan sonra ürün sınıfı'):'Satın alma kararı vermeden önce'}</small></a>`).join('');
    $('journeyStages').querySelectorAll('[data-journey-stage]').forEach(link=>link.addEventListener('click',()=>emit('product_journey_stage_opened',{category,stage:link.dataset.journeyStage})));
    renderMaintenance(category);
    $('reviewCategory').value=category;
    renderReviews();
    emit('product_journey_rendered',{category,status:'shown'});
  }

  function renderMaintenance(category){
    const journey=core.getJourney(category);
    const record=maintenanceState[category]||core.maintenanceRecord(category,[],new Date());
    $('maintenanceTitle').textContent=`Mevcut ${journey.label.toLocaleLowerCase('tr')} için satın almadan önce bakım kontrolü`;
    $('maintenanceNotice').textContent=journey.professionalOnly?'Bu liste profesyonel kontrolün yerine geçmez. Enerjili tesisat veya sabit bağlantıya kullanıcı müdahalesi önerilmez.':'Bütün maddeler olumluysa mevcut ürününüz şimdilik kullanılabilir olabilir; bu bir ürün sertifikası değildir.';
    $('maintenanceChecks').innerHTML=journey.maintenance.map((text,index)=>`<label class="maintenance-check"><input type="checkbox" data-maintenance-index="${index}" ${record.checks[index]?'checked':''}><span>${escapeHtml(text)}</span></label>`).join('');
    $('maintenanceChecks').querySelectorAll('[data-maintenance-index]').forEach(box=>box.addEventListener('change',saveMaintenance));
    renderMaintenanceStatus(record);
  }

  function saveMaintenance(){
    const journey=core.getJourney(selectedCategory);
    if(!journey)return;
    const checks=[...$('maintenanceChecks').querySelectorAll('[data-maintenance-index]')].map(box=>box.checked);
    const record=core.maintenanceRecord(selectedCategory,checks,new Date());
    maintenanceState={...maintenanceState,[selectedCategory]:record};
    writeJson(core.maintenanceStorageKey,maintenanceState);
    renderMaintenanceStatus(record);
    emit(record.completed?'ownership_maintenance_completed':'ownership_maintenance_progressed',{category:selectedCategory,status:record.completed?'completed':'in_progress'});
  }

  function renderMaintenanceStatus(record){
    const done=record.checks.filter(Boolean).length;
    const total=record.checks.length;
    const journey=core.getJourney(record.category);
    if(record.completed){
      $('maintenanceStatus').className='journey-status is-good';
      $('maintenanceStatus').textContent=journey.professionalOnly?`${done}/${total} hazırlık kontrolü tamamlandı. Yine de sabit veya yüksek riskli uygulamada yetkili uzman gerekir.`:`${done}/${total} kontrol tamamlandı. Yeni ürün satın almadan mevcut ekipmanı kullanmayı ve ${formatDate(core.addDays(new Date(),30))} tarihinde yeniden kontrol etmeyi değerlendirin.`;
    }else{
      $('maintenanceStatus').className='journey-status';
      $('maintenanceStatus').textContent=`${done}/${total} kontrol tamamlandı. Eksik veya olumsuz bir maddede ürün satın almadan önce nedenini doğrulayın.`;
    }
  }

  function saveReview(){
    const category=$('reviewCategory').value||selectedCategory;
    if(!core.getJourney(category))return;
    const reviewDays=Number($('reviewDays').value||30);
    const reason=$('reviewReason').value||'technical_recheck';
    reviews=core.upsertReview(reviews,{category,reviewDays,reason},new Date());
    if(writeJson(core.reviewStorageKey,reviews)){
      $('reviewStatus').textContent='Yeniden kontrol kaydı yalnız bu tarayıcıda saklandı.';
      emit('decision_review_saved',{category,review_days:reviewDays,reason,status:'saved'});
      renderReviews();
    }else $('reviewStatus').textContent='Tarayıcı kaydı kullanılamadı; tarih saklanmadı.';
  }

  function removeReview(id){
    const item=reviews.find(entry=>entry.id===id);
    reviews=core.removeReview(reviews,id,new Date());
    writeJson(core.reviewStorageKey,reviews);
    renderReviews();
    if(item)emit('decision_review_removed',{category:item.category,status:'removed'});
  }

  function reopenReview(category,band){
    const button=document.querySelector(`[data-category="${CSS.escape(category)}"]`);
    if(button){button.click();$('matcher').scrollIntoView({behavior:'smooth',block:'start'});}
    emit('decision_review_reopened',{category,due_band:band,status:'reopened'});
  }

  function renderReviews(){
    reviews=core.sanitizeReviews(reviews,new Date());
    const container=$('reviewList');
    $('reviewVault').classList.toggle('hidden',reviews.length===0);
    if(!reviews.length){container.innerHTML='';return;}
    container.innerHTML=reviews.map(item=>{
      const journey=core.getJourney(item.category);
      const due=dueText(item);
      return `<article class="review-card ${due.band==='overdue'||due.band==='today'?'is-due':''}"><div><span class="review-band">${escapeHtml(due.text)}</span><h3>${escapeHtml(journey.label)}</h3><p>${escapeHtml(journey.reviewReason)}</p><small>Kayıt: ${escapeHtml(formatDate(item.createdAt))} · Kişisel veri içermez</small></div><div class="review-actions"><button type="button" class="btn btn-primary" data-review-open="${escapeAttr(item.category)}" data-due-band="${escapeAttr(due.band)}">Yeniden değerlendir</button><button type="button" class="btn btn-secondary" data-review-remove="${escapeAttr(item.id)}">Sil</button></div></article>`;
    }).join('');
    container.querySelectorAll('[data-review-open]').forEach(button=>button.addEventListener('click',()=>reopenReview(button.dataset.reviewOpen,button.dataset.dueBand)));
    container.querySelectorAll('[data-review-remove]').forEach(button=>button.addEventListener('click',()=>removeReview(button.dataset.reviewRemove)));
  }

  function clearReviews(){
    reviews=[];
    try{localStorage.removeItem(core.reviewStorageKey);}catch(error){}
    renderReviews();
    $('reviewStatus').textContent='Bütün yeniden kontrol kayıtları cihazınızdan silindi.';
    emit('decision_review_cleared',{status:'cleared'});
  }

  function bindCategoryButtons(){
    document.querySelectorAll('[data-category]').forEach(button=>button.addEventListener('click',()=>renderJourney(button.dataset.category)));
    document.querySelectorAll('[data-intent-category]').forEach(button=>button.addEventListener('click',()=>renderJourney(button.dataset.intentCategory)));
  }

  function init(){
    if(!$('journeyRetention'))return;
    bindCategoryButtons();
    $('saveReviewBtn').addEventListener('click',saveReview);
    $('clearReviewsBtn').addEventListener('click',clearReviews);
    renderReviews();
    const params=new URLSearchParams(location.search);
    const category=params.get('kategori');
    if(core.getJourney(category))renderJourney(category);
  }

  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init);
  else init();
})();
