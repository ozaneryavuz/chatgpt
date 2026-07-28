(()=>{
  'use strict';
  const core=window.AloContinuityPassport;
  if(!core) return;

  const STORAGE_KEY='alo186.continuityPassportDraft.v1';
  const STORAGE_TTL_MS=30*24*60*60*1000;
  const MATURITY_HANDOFF_KEY='alo186.continuityMaturityHandoff.v1';
  const STATUS_LABELS={current:'Güncel',due:'Yenileme zamanı',planned:'Planlandı',missing:'Yok'};
  const FACILITY_LABELS={hotel:'Otel / konaklama',site:'Site / apartman',business:'İşletme',other:'Diğer tesis'};

  const form=document.getElementById('passportForm');
  const evidenceList=document.getElementById('evidenceList');
  const evidenceProgress=document.getElementById('evidenceProgress');
  const facilityType=document.getElementById('facilityType');
  const maturityFile=document.getElementById('maturityFile');
  const importStatus=document.getElementById('importStatus');
  const immediateDanger=document.getElementById('immediateDanger');
  const medical=document.getElementById('medical');
  const saveLocal=document.getElementById('saveLocal');
  const validation=document.getElementById('validation');
  const emergencyNotice=document.getElementById('emergencyNotice');
  const restoreBtn=document.getElementById('restoreBtn');
  const resetBtn=document.getElementById('resetBtn');
  const results=document.getElementById('results');
  const passportScore=document.getElementById('passportScore');
  const passportBand=document.getElementById('passportBand');
  const evidenceScore=document.getElementById('evidenceScore');
  const p0Count=document.getElementById('p0Count');
  const reviewDate=document.getElementById('reviewDate');
  const maturitySummary=document.getElementById('maturitySummary');
  const resultTitle=document.getElementById('resultTitle');
  const resultSummary=document.getElementById('resultSummary');
  const professionalNotice=document.getElementById('professionalNotice');
  const evidenceSummary=document.getElementById('evidenceSummary');
  const p0List=document.getElementById('p0List');
  const p1List=document.getElementById('p1List');
  const p2List=document.getElementById('p2List');
  const exportBtn=document.getElementById('exportBtn');
  const printBtn=document.getElementById('printBtn');
  const clearStorageBtn=document.getElementById('clearStorageBtn');
  const businessCta=document.getElementById('businessCta');

  let maturityImport=null;
  let lastEvaluation=null;
  let lastPassport=null;

  function track(event,params){
    window.dataLayer=window.dataLayer||[];
    window.dataLayer.push({event,...(params||{})});
  }

  function renderEvidence(){
    const fragment=document.createDocumentFragment();
    core.EVIDENCE_ITEMS.forEach((item,index)=>{
      const row=document.createElement('article');
      row.className='evidence-row';
      row.dataset.evidence=item.id;
      const critical=item.critical?'<b>Kritik kanıt</b>':'';
      row.innerHTML=`<div class="evidence-copy"><strong>${index+1}. ${item.title}</strong><small>${item.action}</small>${critical}</div><div class="status-options" role="radiogroup" aria-label="${item.title} durumu">${core.STATUS_VALUES.map(status=>`<label class="status-option"><input type="radio" name="evidence-${item.id}" value="${status}"><span>${STATUS_LABELS[status]}</span></label>`).join('')}</div>`;
      fragment.appendChild(row);
    });
    evidenceList.replaceChildren(fragment);
  }

  function checkedValues(containerId){
    return [...document.querySelectorAll(`#${containerId} input[type="checkbox"]:checked`)].map(input=>input.value);
  }

  function readEvidence(){
    const evidence={};
    core.EVIDENCE_ITEMS.forEach(item=>{
      const selected=form.querySelector(`input[name="evidence-${item.id}"]:checked`);
      if(selected) evidence[item.id]=selected.value;
    });
    return evidence;
  }

  function readInput(){
    return {
      facilityType:facilityType.value,
      criticalLoads:checkedValues('criticalLoads'),
      backupSystems:checkedValues('backupSystems'),
      evidence:readEvidence(),
      maturityScore:maturityImport?maturityImport.score:null,
      maturityBand:maturityImport?maturityImport.maturityBand:null
    };
  }

  function answeredEvidenceCount(){
    return Object.keys(readEvidence()).length;
  }

  function updateProgress(){
    const count=answeredEvidenceCount();
    evidenceProgress.textContent=`${count} / ${core.EVIDENCE_ITEMS.length}`;
    evidenceProgress.className=`status ${count===core.EVIDENCE_ITEMS.length?'ok':'warn'}`;
  }

  function showValidation(message){
    validation.textContent=message;
    validation.hidden=!message;
    if(message){validation.focus();validation.scrollIntoView({behavior:'smooth',block:'center'});}
  }

  function setImportStatus(message,tone){
    importStatus.textContent=message;
    importStatus.className=`help ${tone||''}`.trim();
  }

  function maturityFromHandoff(){
    try{
      const payload=JSON.parse(localStorage.getItem(MATURITY_HANDOFF_KEY)||'null');
      if(!payload||!payload.expiresAt||new Date(payload.expiresAt).getTime()<Date.now()) return null;
      return core.parseMaturityImport(payload);
    }catch(_error){return null;}
  }

  function applyMaturity(imported,source){
    maturityImport=imported;
    if(imported.facilityType) facilityType.value=imported.facilityType;
    const band=imported.maturityBand?` · ${imported.maturityBand}`:'';
    setImportStatus(`Olgunluk skoru içe aktarıldı: ${imported.score}/100${band}`,'success');
    track('continuity_passport_maturity_imported',{source,score_bucket:Math.floor(imported.score/10)*10,facility_type:imported.facilityType||'unknown'});
  }

  async function importMaturityFile(file){
    if(!file) return;
    if(file.size>512000){setImportStatus('Dosya 500 KB sınırını aşıyor.','error');return;}
    try{
      const imported=core.parseMaturityImport(await file.text());
      applyMaturity(imported,'file');
    }catch(error){
      maturityImport=null;
      setImportStatus(error&&error.message?error.message:'JSON dosyası okunamadı.','error');
      track('continuity_passport_maturity_import_failed',{});
    }
  }

  function sanitizeDraft(input){
    return {
      version:1,
      savedAt:new Date().toISOString(),
      expiresAt:new Date(Date.now()+STORAGE_TTL_MS).toISOString(),
      facilityType:input.facilityType,
      criticalLoads:input.criticalLoads,
      backupSystems:input.backupSystems,
      evidence:input.evidence,
      maturityScore:input.maturityScore,
      maturityBand:input.maturityBand
    };
  }

  function saveDraft(input){
    if(!saveLocal.checked) return;
    try{
      localStorage.setItem(STORAGE_KEY,JSON.stringify(sanitizeDraft(core.sanitizeInput(input))));
      restoreBtn.hidden=false;
      track('continuity_passport_draft_saved',{facility_type:input.facilityType});
    }catch(_error){track('continuity_passport_draft_save_failed',{});}
  }

  function storedDraft(){
    try{
      const draft=JSON.parse(localStorage.getItem(STORAGE_KEY)||'null');
      if(!draft||!draft.expiresAt||new Date(draft.expiresAt).getTime()<Date.now()){
        localStorage.removeItem(STORAGE_KEY);
        return null;
      }
      return draft;
    }catch(_error){return null;}
  }

  function applyChecks(containerId,values){
    const allowed=new Set(values||[]);
    document.querySelectorAll(`#${containerId} input[type="checkbox"]`).forEach(input=>{input.checked=allowed.has(input.value);});
  }

  function restoreDraft(){
    const draft=storedDraft();
    if(!draft){showValidation('Yüklenecek güncel yerel kayıt bulunamadı.');restoreBtn.hidden=true;return;}
    facilityType.value=draft.facilityType;
    applyChecks('criticalLoads',draft.criticalLoads);
    applyChecks('backupSystems',draft.backupSystems);
    core.EVIDENCE_ITEMS.forEach(item=>{
      const status=draft.evidence&&draft.evidence[item.id];
      const input=form.querySelector(`input[name="evidence-${item.id}"][value="${status}"]`);
      if(input) input.checked=true;
    });
    if(Number.isFinite(Number(draft.maturityScore))) applyMaturity({score:Number(draft.maturityScore),facilityType:draft.facilityType,maturityBand:draft.maturityBand||null},'local_draft');
    medical.checked=false;
    immediateDanger.checked=false;
    saveLocal.checked=true;
    updateProgress();
    showValidation('30 günlük teknik seçimler yüklendi. Acil tehlike ve yaşam destek seçimi güvenlik nedeniyle kaydedilmedi.');
    track('continuity_passport_draft_restored',{facility_type:draft.facilityType});
  }

  function clearStorage(showMessage=true){
    localStorage.removeItem(STORAGE_KEY);
    restoreBtn.hidden=true;
    if(showMessage) showValidation('Bu araca ait yerel kayıt silindi.');
    track('continuity_passport_storage_cleared',{});
  }

  function clearAll(){
    form.reset();
    maturityFile.value='';
    maturityImport=null;
    lastEvaluation=null;
    lastPassport=null;
    results.hidden=true;
    emergencyNotice.hidden=true;
    setImportStatus('Dosya yalnız tarayıcıda okunur; sunucuya gönderilmez.','');
    showValidation('');
    updateProgress();
    track('continuity_passport_reset',{});
  }

  function formatDate(value){
    return new Intl.DateTimeFormat('tr-TR',{day:'2-digit',month:'short',year:'numeric'}).format(new Date(value));
  }

  function fillPriority(target,items){
    target.replaceChildren();
    if(!items.length){
      const li=document.createElement('li');
      li.className='empty';
      li.textContent='Bu seviyede açık oluşmadı.';
      target.appendChild(li);
      return;
    }
    items.slice(0,8).forEach(item=>{
      const li=document.createElement('li');
      li.innerHTML=`<strong>${item.title}:</strong> ${item.action}`;
      target.appendChild(li);
    });
  }

  function renderSummary(evaluation){
    const counts={current:0,due:0,planned:0,missing:0};
    evaluation.evidence.forEach(item=>{counts[item.status]+=1;});
    evidenceSummary.replaceChildren();
    [['current','Güncel'],['due','Yenilenecek'],['planned','Planlandı'],['missing','Yok']].forEach(([key,label])=>{
      const row=document.createElement('div');
      row.className='summary-row';
      const percent=Math.round((counts[key]/core.EVIDENCE_ITEMS.length)*100);
      row.innerHTML=`<span>${label}</span><div aria-hidden="true"><i style="width:${percent}%"></i></div><b>${counts[key]}</b>`;
      evidenceSummary.appendChild(row);
    });
  }

  function renderResult(evaluation,passport){
    passportScore.textContent=`${evaluation.score}/100`;
    passportBand.textContent=evaluation.classification.label;
    evidenceScore.textContent=`${evaluation.evidenceScore}/100`;
    p0Count.textContent=String(evaluation.priorities.p0.length);
    reviewDate.textContent=formatDate(passport.validUntil);
    maturitySummary.textContent=evaluation.input.maturityScore===null?'Olgunluk skoru aktarılmadı':`Olgunluk: ${evaluation.input.maturityScore}/100${evaluation.input.maturityBand?` · ${evaluation.input.maturityBand}`:''}`;
    resultTitle.textContent=`${FACILITY_LABELS[evaluation.input.facilityType]} · ${evaluation.classification.label}`;
    resultSummary.textContent=evaluation.classification.summary;
    professionalNotice.hidden=!(evaluation.professionalReviewRecommended||medical.checked);
    if(medical.checked) professionalNotice.innerHTML='<strong>Yaşam destek yükü için profesyonel plan zorunlu.</strong> Bu pasaport yeterli değildir. Üretici onaylı kapasite, geçiş, alarm, test ve sorumlu planını yetkili uzmanla doğrulayın. Bu seçim JSON ve yerel kayda yazılmadı.';
    else if(evaluation.professionalReviewRecommended) professionalNotice.innerHTML='<strong>Saha doğrulaması önceliklidir.</strong> P0 veya düşük skor; yedek güç, transfer, koruma, topraklama ve testlerde yetkili uzman incelemesini gerektirir.';
    renderSummary(evaluation);
    fillPriority(p0List,evaluation.priorities.p0);
    fillPriority(p1List,evaluation.priorities.p1);
    fillPriority(p2List,evaluation.priorities.p2);
    businessCta.hidden=medical.checked||immediateDanger.checked;
    results.hidden=false;
    results.scrollIntoView({behavior:'smooth',block:'start'});
    results.focus();
  }

  function evaluate(event){
    event.preventDefault();
    showValidation('');
    emergencyNotice.hidden=true;
    if(immediateDanger.checked){
      results.hidden=true;
      businessCta.hidden=true;
      emergencyNotice.hidden=false;
      emergencyNotice.focus();
      track('continuity_passport_emergency_route_shown',{});
      return;
    }
    const missingCount=core.EVIDENCE_ITEMS.length-answeredEvidenceCount();
    if(missingCount>0){showValidation(`Pasaportu oluşturmak için ${missingCount} kanıt alanının durumunu seçin.`);return;}
    const input=readInput();
    lastEvaluation=core.evaluatePassport(input);
    lastPassport=core.createPassport(input,lastEvaluation);
    saveDraft(input);
    renderResult(lastEvaluation,lastPassport);
    track('continuity_passport_completed',{facility_type:input.facilityType,score_band:lastEvaluation.classification.id,score_bucket:Math.floor(lastEvaluation.score/10)*10,p0_count:lastEvaluation.priorities.p0.length,critical_load_count:input.criticalLoads.length,backup_system_count:input.backupSystems.length,maturity_imported:input.maturityScore!==null});
  }

  function exportPassport(){
    if(!lastPassport) return;
    const check=core.validatePassport(lastPassport);
    if(!check.valid){showValidation(`Pasaport doğrulanamadı: ${check.errors.join(' ')}`);return;}
    const blob=new Blob([JSON.stringify(lastPassport,null,2)],{type:'application/json'});
    const url=URL.createObjectURL(blob);
    const link=document.createElement('a');
    link.href=url;
    link.download=`alo186-elektrik-surekliligi-pasaportu-${new Date().toISOString().slice(0,10)}.json`;
    document.body.appendChild(link);link.click();link.remove();URL.revokeObjectURL(url);
    track('continuity_passport_exported',{facility_type:lastPassport.facilityType,score_band:lastPassport.classification.id,p0_count:lastPassport.actions.p0.length});
  }

  renderEvidence();
  updateProgress();
  restoreBtn.hidden=!storedDraft();
  const handoff=maturityFromHandoff();
  if(handoff) applyMaturity(handoff,'maturity_handoff');
  form.addEventListener('change',updateProgress);
  form.addEventListener('submit',evaluate);
  maturityFile.addEventListener('change',()=>importMaturityFile(maturityFile.files&&maturityFile.files[0]));
  restoreBtn.addEventListener('click',restoreDraft);
  resetBtn.addEventListener('click',clearAll);
  exportBtn.addEventListener('click',exportPassport);
  printBtn.addEventListener('click',()=>{if(lastPassport){window.print();track('continuity_passport_printed',{score_band:lastPassport.classification.id});}});
  clearStorageBtn.addEventListener('click',()=>clearStorage(true));
})();
