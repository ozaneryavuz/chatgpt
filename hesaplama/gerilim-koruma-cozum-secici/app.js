(() => {
  'use strict';
  const $=id=>document.getElementById(id);
  const core=window.Alo186VoltageProtectionSelector;
  const presets={
    transient:{symptom:'surge',duration:'instant',scope:'one_device',measurement:'none',loadType:'electronics',powerBand:'under1000',phase:'single',continuity:'brief_ok',existing:'none',emergency:false,medical:false},
    restart:{symptom:'outage_restart',duration:'seconds',scope:'one_device',measurement:'none',loadType:'electronics',powerBand:'under1000',phase:'single',continuity:'must_stay_on',existing:'none',emergency:false,medical:false},
    mixed:{symptom:'mixed',duration:'minutes',scope:'whole_home',measurement:'fluctuating',loadType:'unknown',powerBand:'unknown',phase:'single',continuity:'none',existing:'unknown',emergency:false,medical:false},
    building:{symptom:'dim',duration:'continuous',scope:'neighbors',measurement:'low',loadType:'fixed',powerBand:'over1000',phase:'unknown',continuity:'none',existing:'unknown',emergency:false,medical:false}
  };
  function emit(name,params={}){if(typeof window.Alo186Track==='function')window.Alo186Track(name,params);}
  function values(){return {symptom:$('symptom').value,duration:$('duration').value,scope:$('scope').value,measurement:$('measurement').value,loadType:$('loadType').value,powerBand:$('powerBand').value,phase:$('phase').value,continuity:$('continuity').value,existing:$('existing').value,emergency:$('emergency').checked,medical:$('medical').checked};}
  function setValues(data){['symptom','duration','scope','measurement','loadType','powerBand','phase','continuity','existing'].forEach(key=>{if(data[key]!=null)$(key).value=String(data[key]);});$('emergency').checked=Boolean(data.emergency);$('medical').checked=Boolean(data.medical);}
  function escapeHtml(value){return String(value).replace(/[&<>"']/g,ch=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));}
  function list(items){return items.map(item=>`<li>${escapeHtml(item)}</li>`).join('');}
  function updateAffiliate(){const enabled=$('affiliateAck').checked;const link=$('productCenterLink');link.classList.toggle('disabled-link',!enabled);link.setAttribute('aria-disabled',enabled?'false':'true');link.tabIndex=enabled?0:-1;}
  function render(result){
    $('results').classList.remove('hidden');$('solutionMetric').textContent=result.solution.label;$('riskMetric').textContent=result.riskLevel;$('distributionMetric').textContent=result.distributionReport?'Evet':'Hayır / önce teknik kontrol';$('commercialMetric').textContent=result.commercialAllowed?'Düşük riskli rota':'Kapalı';
    $('resultStatus').textContent=result.professionalRequired?'Uzman / resmî kanal gerekli':'Ön değerlendirme tamamlandı';$('resultStatus').className=`status ${result.riskLevel==='Kritik'||result.riskLevel==='Yüksek'?'bad':result.riskLevel==='Orta'?'warn':'ok'}`;
    $('recommendationLabel').textContent=result.solution.label;$('recommendationNote').textContent=result.solution.note;$('reasonList').innerHTML=list(result.reasons);$('limitList').innerHTML=list(result.limits.length?result.limits:['Bu sonuç kesin ürün veya arıza teşhisi değildir.']);$('checkList').innerHTML=list(result.checks);
    $('nextStepText').textContent='Sonucu ürün adıyla değil, ilgili ücretsiz kontrol veya resmî kanal üzerinden doğrulayın.';$('nextStepLink').href=result.solution.nextStepUrl;$('nextStepLink').textContent=result.solution.nextStepLabel;
    $('affiliatePanel').classList.toggle('hidden',!result.commercialAllowed);$('professionalPanel').classList.toggle('hidden',!result.professionalRequired);$('affiliateAck').checked=false;
    if(result.productCategory)$('productCenterLink').href=`https://alo186.com/akilli-urun-secimi?kategori=${encodeURIComponent(result.productCategory)}`;
    updateAffiliate();$('results').focus({preventScroll:true});$('results').scrollIntoView({behavior:window.matchMedia('(prefers-reduced-motion: reduce)').matches?'auto':'smooth',block:'start'});
    emit('voltage_protection_selector_completed',{recommendation:result.recommendation,risk_level:result.riskLevel,professional_required:result.professionalRequired,distribution_report:result.distributionReport,commercial_allowed:result.commercialAllowed,product_category:result.productCategory||'none'});
  }
  document.querySelectorAll('[data-preset]').forEach(button=>button.addEventListener('click',()=>{setValues(presets[button.dataset.preset]);emit('voltage_protection_preset_selected',{preset:button.dataset.preset});}));
  $('selectorForm').addEventListener('submit',event=>{event.preventDefault();try{$('validation').textContent='';render(core.analyze(values()));}catch(error){$('validation').textContent=error.message;$('validation').focus();}});
  $('resetBtn').addEventListener('click',()=>{$('selectorForm').reset();setValues(presets.transient);$('results').classList.add('hidden');$('validation').textContent='';emit('voltage_protection_selector_reset');});
  $('affiliateAck').addEventListener('change',updateAffiliate);
  $('productCenterLink').addEventListener('click',event=>{if($('productCenterLink').getAttribute('aria-disabled')==='true'){event.preventDefault();return;}emit('voltage_protection_product_center_opened',{category:'surge_strip'});});
  $('nextStepLink').addEventListener('click',()=>emit('voltage_protection_next_step_opened',{url:$('nextStepLink').href}));
})();
