(() => {
  'use strict';
  const $=id=>document.getElementById(id);
  const core=window.Alo186UPSBatterySuitability;
  const valueIds=['upsClass','upsAgeYears','chemistry','batteryAgeYears','physicalState','selfTest','measuredRuntimeMin','requiredRuntimeMin','runtimeTrend','candidateType'];
  const checkIds=['fullyCharged','repeatBatteryAlarm','outageDrop','exactModelVerified','userReplaceable','exactCartridgeVerified','preassembledCartridge','fullSetReplacement','supportActive','externalBatteryPacks','recyclingPlan','lifeSupport'];
  const presets={
    healthy:{upsClass:'desktop',upsAgeYears:3,chemistry:'vrla',batteryAgeYears:2,physicalState:'normal',fullyCharged:true,selfTest:'pass',measuredRuntimeMin:25,requiredRuntimeMin:15,runtimeTrend:'stable',repeatBatteryAlarm:false,outageDrop:false,exactModelVerified:true,userReplaceable:true,exactCartridgeVerified:false,candidateType:'not-selected',preassembledCartridge:false,fullSetReplacement:false,supportActive:true,externalBatteryPacks:false,recyclingPlan:false,lifeSupport:false},
    replace:{upsClass:'desktop',upsAgeYears:4,chemistry:'vrla',batteryAgeYears:4,physicalState:'normal',fullyCharged:true,selfTest:'replace',measuredRuntimeMin:6,requiredRuntimeMin:20,runtimeTrend:'declined',repeatBatteryAlarm:true,outageDrop:true,exactModelVerified:true,userReplaceable:true,exactCartridgeVerified:true,candidateType:'manufacturer-exact',preassembledCartridge:true,fullSetReplacement:true,supportActive:true,externalBatteryPacks:false,recyclingPlan:true,lifeSupport:false},
    old:{upsClass:'desktop',upsAgeYears:8,chemistry:'vrla',batteryAgeYears:5,physicalState:'normal',fullyCharged:true,selfTest:'replace',measuredRuntimeMin:5,requiredRuntimeMin:20,runtimeTrend:'declined',repeatBatteryAlarm:true,outageDrop:false,exactModelVerified:true,userReplaceable:true,exactCartridgeVerified:true,candidateType:'manufacturer-exact',preassembledCartridge:true,fullSetReplacement:true,supportActive:false,externalBatteryPacks:false,recyclingPlan:true,lifeSupport:false}
  };
  const labels={
    'stop-use':'Kullanımı durdurun',service:'Yetkili servis / uzman gerekli','test-first':'Önce tam şarj ve self-test','capacity-review':'Akü değil, kapasite hesabı gerekli','compare-unit':'Akü ile yeni UPS’i karşılaştırın','replace-cartridge':'Kartuş/set değişimi gerekli olabilir','plan-replacement':'Önleyici değişim planı','no-purchase':'Şimdilik satın almayın',monitor:'İzlemeye devam edin'
  };
  const escapeHtml=value=>String(value).replace(/[&<>"']/g,ch=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));
  const list=items=>items.map(item=>`<li>${escapeHtml(item)}</li>`).join('');
  const values=()=>{const data={};valueIds.forEach(id=>data[id]=$(id).value);checkIds.forEach(id=>data[id]=$(id).checked);return data;};
  function setValues(data){valueIds.forEach(id=>{if(data[id]!=null)$(id).value=String(data[id]);});checkIds.forEach(id=>{$(id).checked=Boolean(data[id]);});}
  function emit(name,params={}){if(typeof window.Alo186Track==='function')window.Alo186Track(name,params);}
  function updateAffiliate(){const enabled=$('affiliateAck').checked,link=$('productCenterLink');link.classList.toggle('disabled-link',!enabled);link.setAttribute('aria-disabled',enabled?'false':'true');link.tabIndex=enabled?0:-1;emit('ups_battery_affiliate_acknowledged',{acknowledged:enabled});}
  function render(result){
    $('results').classList.remove('hidden');
    $('resultStatus').textContent=labels[result.status]||'Sonuç';
    $('resultStatus').className=`status ${['no-purchase','replace-cartridge'].includes(result.status)?'ok':['stop-use','service'].includes(result.status)?'bad':'warn'}`;
    $('summary').textContent=result.recommendedAction;
    $('ageMetric').textContent=result.ageSignal;
    $('runtimeMetric').textContent=result.runtimeResult;
    $('chassisMetric').textContent=result.chassisSignal;
    $('candidateMetric').textContent=result.candidateSignal;
    $('blockerCard').classList.toggle('hidden',!result.blockers.length);
    $('blockerList').innerHTML=list(result.blockers);
    $('reasonCard').classList.toggle('hidden',!result.replacementReasons.length);
    $('reasonList').innerHTML=list(result.replacementReasons);
    $('warningList').innerHTML=list(result.warnings.length?result.warnings:['Belirgin ek uyarı yok; tam model kılavuzu yine esas alınmalıdır.']);
    $('checkList').innerHTML=list(result.checks);
    $('noPurchasePanel').classList.toggle('hidden',!result.noPurchaseNeeded);
    $('professionalPanel').classList.toggle('hidden',!result.professionalRequired);
    $('affiliatePanel').classList.toggle('hidden',!result.commercialAllowed);
    $('alternativePanel').classList.toggle('hidden',!result.alternativeRoute);
    if(result.alternativeRoute){$('alternativeLink').href=result.alternativeRoute;$('alternativeLink').textContent=result.status==='capacity-review'?'UPS süre ve kapasite hesabını aç':'Yedek güç toplam maliyet karşılaştırmasını aç';}
    $('affiliateAck').checked=false;updateAffiliate();
    $('results').focus({preventScroll:true});$('results').scrollIntoView({behavior:window.matchMedia('(prefers-reduced-motion: reduce)').matches?'auto':'smooth',block:'start'});
    emit('ups_battery_suitability_completed',{status:result.status,commercial_allowed:result.commercialAllowed,no_purchase_needed:result.noPurchaseNeeded,ups_class:result.input.upsClass,chemistry:result.input.chemistry});
    if(result.noPurchaseNeeded)emit('ups_battery_no_purchase',{reason:'healthy_runtime_and_self_test'});
  }
  document.querySelectorAll('[data-preset]').forEach(button=>button.addEventListener('click',()=>{setValues(presets[button.dataset.preset]);emit('ups_battery_preset_selected',{preset:button.dataset.preset});}));
  $('upsBatteryForm').addEventListener('submit',event=>{event.preventDefault();try{$('validation').textContent='';render(core.analyze(values()));}catch(error){$('validation').textContent=error.message;$('validation').focus();}});
  $('resetBtn').addEventListener('click',()=>{$('upsBatteryForm').reset();setValues(presets.healthy);$('results').classList.add('hidden');$('validation').textContent='';emit('ups_battery_reset');});
  $('affiliateAck').addEventListener('change',updateAffiliate);
  $('productCenterLink').addEventListener('click',event=>{if(event.currentTarget.getAttribute('aria-disabled')==='true'){event.preventDefault();return;}emit('ups_battery_product_center_opened',{category:'ups_aku'});});
  setValues(presets.healthy);
})();
