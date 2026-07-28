(() => {
  'use strict';
  const $=id=>document.getElementById(id);
  const core=window.Alo186SmartPlugMeter;
  const valueIds=['loadType','goal','ownership','meterType','loadPowerW','powerFactor','startupPowerW','dailyHours','standbyPowerW','desiredHistoryDays','candidateCurrentA','candidatePowerW','candidateMinMeasureW','candidateHistoryDays'];
  const checkIds=['energyMonitoring','remoteSwitching','scheduleSupport','labelVerified','manufacturerLoadApproved','damageFree','directWallSocket','indoorDry','earthContinuity','needsEarth','unattendedUse'];
  const presets={
    electronics:{loadType:'electronics',goal:'history',ownership:'candidate',meterType:'smart_plug',loadPowerW:180,powerFactor:.9,startupPowerW:300,dailyHours:6,standbyPowerW:3,desiredHistoryDays:30,candidateCurrentA:16,candidatePowerW:3680,candidateMinMeasureW:.1,candidateHistoryDays:365,energyMonitoring:true,remoteSwitching:true,scheduleSupport:true,labelVerified:true,manufacturerLoadApproved:true,damageFree:true,directWallSocket:true,indoorDry:true,earthContinuity:true,needsEarth:true,unattendedUse:false},
    standby:{loadType:'electronics',goal:'standby',ownership:'candidate',meterType:'plug_meter',loadPowerW:12,powerFactor:.6,startupPowerW:40,dailyHours:24,standbyPowerW:1.5,desiredHistoryDays:7,candidateCurrentA:16,candidatePowerW:3680,candidateMinMeasureW:.1,candidateHistoryDays:7,energyMonitoring:true,remoteSwitching:false,scheduleSupport:false,labelVerified:true,manufacturerLoadApproved:true,damageFree:true,directWallSocket:true,indoorDry:true,earthContinuity:true,needsEarth:false,unattendedUse:false},
    heater:{loadType:'resistive',goal:'schedule',ownership:'candidate',meterType:'smart_plug',loadPowerW:2000,powerFactor:1,startupPowerW:2000,dailyHours:4,standbyPowerW:0,desiredHistoryDays:30,candidateCurrentA:16,candidatePowerW:3680,candidateMinMeasureW:.1,candidateHistoryDays:365,energyMonitoring:true,remoteSwitching:true,scheduleSupport:true,labelVerified:true,manufacturerLoadApproved:true,damageFree:true,directWallSocket:true,indoorDry:true,earthContinuity:true,needsEarth:true,unattendedUse:true},
    fridge:{loadType:'compressor',goal:'history',ownership:'candidate',meterType:'smart_plug',loadPowerW:180,powerFactor:.75,startupPowerW:1200,dailyHours:12,standbyPowerW:0,desiredHistoryDays:30,candidateCurrentA:16,candidatePowerW:3680,candidateMinMeasureW:.1,candidateHistoryDays:365,energyMonitoring:true,remoteSwitching:true,scheduleSupport:true,labelVerified:true,manufacturerLoadApproved:false,damageFree:true,directWallSocket:true,indoorDry:true,earthContinuity:true,needsEarth:true,unattendedUse:false}
  };
  const escapeHtml=value=>String(value).replace(/[&<>"']/g,ch=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));
  const list=items=>items.map(item=>`<li>${escapeHtml(item)}</li>`).join('');
  const fmt=(value,digits=2)=>Number(value).toLocaleString('tr-TR',{maximumFractionDigits:digits});
  function values(){const data={};valueIds.forEach(id=>data[id]=$(id).value);checkIds.forEach(id=>data[id]=$(id).checked);return data;}
  function setValues(data){valueIds.forEach(id=>{if(data[id]!=null)$(id).value=String(data[id]);});checkIds.forEach(id=>{$(id).checked=Boolean(data[id]);});toggleFields();}
  function emit(name,params={}){if(typeof window.Alo186Track==='function')window.Alo186Track(name,params);}
  function toggleFields(){
    const goal=$('goal').value;
    $('standbyFields').classList.toggle('hidden',goal!=='standby');
    $('historyFields').classList.toggle('hidden',goal!=='history');
    const smart=$('meterType').value==='smart_plug';
    $('smartFeatures').classList.toggle('muted-panel',!smart);
  }
  function updateAffiliate(){
    const enabled=$('affiliateAck').checked;
    const link=$('affiliateLink');
    link.classList.toggle('disabled-link',!enabled);
    link.setAttribute('aria-disabled',enabled?'false':'true');
    link.tabIndex=enabled?0:-1;
    emit('smart_plug_affiliate_acknowledged',{acknowledged:enabled});
  }
  function render(result){
    $('results').classList.remove('hidden');
    const labels={compatible:'Teknik sınırlar içinde',conditional:'Koşullu / bilgi doğrulaması gerekli',incompatible:'Uygun değil veya güvenlik engeli var'};
    $('resultStatus').textContent=labels[result.status];
    $('resultStatus').className=`status ${result.status==='compatible'?'ok':result.status==='conditional'?'warn':'bad'}`;
    $('currentMetric').textContent=`${fmt(result.currentA)} A`;
    $('startupMetric').textContent=`${fmt(result.startupCurrentA)} A`;
    $('energyMetric').textContent=`${fmt(result.annualKwh,1)} kWh/yıl`;
    $('classMetric').textContent=result.recommendedClass;
    $('summary').textContent=`${$('loadType').selectedOptions[0].text} · ${fmt(result.input.loadPowerW,0)} W · ${fmt(result.input.dailyHours,1)} saat/gün`;
    $('blockerCard').classList.toggle('hidden',!result.blockers.length);
    $('blockerList').innerHTML=list(result.blockers);
    $('warningList').innerHTML=list(result.warnings.length?result.warnings:['Belirgin sınır sorunu görülmedi; tam model etiketi ve üretici kılavuzu yine doğrulanmalıdır.']);
    $('checkList').innerHTML=list(result.checks);
    $('noPurchasePanel').classList.toggle('hidden',!result.noPurchaseNeeded);
    $('professionalPanel').classList.toggle('hidden',!result.professionalRequired);
    $('affiliatePanel').classList.toggle('hidden',!result.commercialAllowed);
    $('affiliateAck').checked=false;updateAffiliate();
    $('results').focus({preventScroll:true});
    $('results').scrollIntoView({behavior:window.matchMedia('(prefers-reduced-motion: reduce)').matches?'auto':'smooth',block:'start'});
    emit('smart_plug_meter_completed',{status:result.status,commercial_allowed:result.commercialAllowed,no_purchase_needed:result.noPurchaseNeeded,load_type:result.input.loadType,goal:result.input.goal,meter_type:result.input.meterType});
    if(result.noPurchaseNeeded)emit('smart_plug_no_purchase',{reason:'owned_product_sufficient'});
    if(!result.commercialAllowed)emit('smart_plug_affiliate_blocked',{status:result.status,professional_required:result.professionalRequired});
  }
  document.querySelectorAll('[data-preset]').forEach(button=>button.addEventListener('click',()=>{setValues(presets[button.dataset.preset]);emit('smart_plug_preset_selected',{preset:button.dataset.preset});}));
  $('smartPlugForm').addEventListener('submit',event=>{event.preventDefault();try{$('validation').textContent='';render(core.analyze(values()));}catch(error){$('validation').textContent=error.message;$('validation').focus();}});
  $('resetBtn').addEventListener('click',()=>{$('smartPlugForm').reset();setValues(presets.electronics);$('results').classList.add('hidden');$('validation').textContent='';emit('smart_plug_reset');});
  $('goal').addEventListener('change',toggleFields);$('meterType').addEventListener('change',toggleFields);
  $('affiliateAck').addEventListener('change',updateAffiliate);
  $('affiliateLink').addEventListener('click',event=>{if(event.currentTarget.getAttribute('aria-disabled')==='true'){event.preventDefault();return;}emit('smart_plug_affiliate_opened',{category:'enerji_izlemeli_akilli_priz'});});
  setValues(presets.electronics);
})();