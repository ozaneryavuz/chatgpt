(()=>{
  'use strict';
  const $=id=>document.getElementById(id);
  const core=window.Alo186PowerStationSuitability;
  const valueIds=['loadType','ownership','continuousPowerW','surgePowerW','targetHours','capacityWh','acContinuousW','acSurgeW','efficiency','reservePct','requiredTransferMs','transferMs','bypassPowerW'];
  const checkIds=['transferRequired','epsSupported','pureSine','acTimeoutDisable','labelVerified','manufacturerLoadApproved','damageFree','indoorDryVentilated','directConnection','needsEarth','earthVerified','unattendedUse'];
  const presets={
    router:{loadType:'router',ownership:'candidate',continuousPowerW:25,surgePowerW:40,targetHours:8,capacityWh:300,acContinuousW:300,acSurgeW:600,efficiency:.86,reservePct:15,transferRequired:true,requiredTransferMs:50,transferMs:20,bypassPowerW:300,epsSupported:true,pureSine:true,acTimeoutDisable:true,labelVerified:true,manufacturerLoadApproved:true,damageFree:true,indoorDryVentilated:true,directConnection:true,needsEarth:false,earthVerified:false,unattendedUse:false},
    office:{loadType:'electronics',ownership:'candidate',continuousPowerW:180,surgePowerW:320,targetHours:4,capacityWh:1000,acContinuousW:1200,acSurgeW:1600,efficiency:.85,reservePct:15,transferRequired:true,requiredTransferMs:25,transferMs:20,bypassPowerW:1200,epsSupported:true,pureSine:true,acTimeoutDisable:true,labelVerified:true,manufacturerLoadApproved:true,damageFree:true,indoorDryVentilated:true,directConnection:true,needsEarth:true,earthVerified:true,unattendedUse:false},
    fridge:{loadType:'fridge',ownership:'candidate',continuousPowerW:150,surgePowerW:900,targetHours:8,capacityWh:1500,acContinuousW:1800,acSurgeW:2700,efficiency:.84,reservePct:20,transferRequired:true,requiredTransferMs:100,transferMs:30,bypassPowerW:1800,epsSupported:true,pureSine:true,acTimeoutDisable:true,labelVerified:true,manufacturerLoadApproved:true,damageFree:true,indoorDryVentilated:true,directConnection:true,needsEarth:true,earthVerified:true,unattendedUse:false},
    server:{loadType:'server',ownership:'candidate',continuousPowerW:400,surgePowerW:650,targetHours:2,capacityWh:1500,acContinuousW:1800,acSurgeW:2700,efficiency:.85,reservePct:15,transferRequired:true,requiredTransferMs:0,transferMs:30,bypassPowerW:1800,epsSupported:true,pureSine:true,acTimeoutDisable:true,labelVerified:true,manufacturerLoadApproved:true,damageFree:true,indoorDryVentilated:true,directConnection:true,needsEarth:true,earthVerified:true,unattendedUse:false}
  };
  const escape=value=>String(value).replace(/[&<>"']/g,ch=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));
  const list=items=>items.map(item=>`<li>${escape(item)}</li>`).join('');
  const fmt=(value,digits=2)=>Number(value).toLocaleString('tr-TR',{maximumFractionDigits:digits});
  function values(){const data={};valueIds.forEach(id=>data[id]=$(id).value);checkIds.forEach(id=>data[id]=$(id).checked);return data;}
  function setValues(data){valueIds.forEach(id=>{if(data[id]!=null)$(id).value=String(data[id]);});checkIds.forEach(id=>{$(id).checked=Boolean(data[id]);});toggleFields();}
  function emit(name,params={}){if(typeof window.Alo186Track==='function')window.Alo186Track(name,params);}
  function toggleFields(){const shown=$('transferRequired').checked;$('transferFields').classList.toggle('muted-panel',!shown);$('requiredTransferMs').disabled=!shown;$('transferMs').disabled=!shown;$('bypassPowerW').disabled=!shown;}
  function updateAffiliate(){const enabled=$('affiliateAck').checked;const link=$('affiliateLink');link.classList.toggle('disabled-link',!enabled);link.setAttribute('aria-disabled',enabled?'false':'true');link.tabIndex=enabled?0:-1;emit('power_station_affiliate_acknowledged',{acknowledged:enabled});}
  function render(result){
    $('results').classList.remove('hidden');
    const labels={compatible:'Teknik sınırlar içinde',conditional:'Koşullu / bilgi doğrulaması gerekli',incompatible:'Uygun değil veya güvenlik engeli var'};
    $('resultStatus').textContent=labels[result.status];$('resultStatus').className=`status ${result.status==='compatible'?'ok':result.status==='conditional'?'warn':'bad'}`;
    $('runtimeMetric').textContent=`${fmt(result.estimatedRuntimeHours)} saat`;
    $('capacityMetric').textContent=`${fmt(result.requiredCapacityWh,0)} Wh`;
    $('usableMetric').textContent=`${fmt(result.usableWh,0)} Wh`;
    $('classMetric').textContent=result.recommendedCapacityWh?`${fmt(result.recommendedCapacityWh,0)} Wh sınıfı`:'10.000 Wh üzeri / profesyonel';
    $('summary').textContent=`${$('loadType').selectedOptions[0].text} · ${fmt(result.input.continuousPowerW,0)} W · hedef ${fmt(result.input.targetHours,1)} saat`;
    $('blockerCard').classList.toggle('hidden',!result.blockers.length);$('blockerList').innerHTML=list(result.blockers);
    $('warningList').innerHTML=list(result.warnings.length?result.warnings:['Belirgin sınır sorunu görülmedi; tam model kılavuzu ve gerçek yük testi yine gereklidir.']);
    $('checkList').innerHTML=list(result.checks);
    $('noPurchasePanel').classList.toggle('hidden',!result.noPurchaseNeeded);
    $('professionalPanel').classList.toggle('hidden',!result.professionalRequired);
    $('affiliatePanel').classList.toggle('hidden',!result.commercialAllowed);
    $('affiliateAck').checked=false;updateAffiliate();
    $('results').focus({preventScroll:true});$('results').scrollIntoView({behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'auto':'smooth',block:'start'});
    emit('power_station_suitability_completed',{status:result.status,commercial_allowed:result.commercialAllowed,no_purchase_needed:result.noPurchaseNeeded,load_type:result.input.loadType,transfer_required:result.input.transferRequired});
    if(result.noPurchaseNeeded)emit('power_station_no_purchase',{reason:'owned_product_sufficient'});
    if(!result.commercialAllowed)emit('power_station_affiliate_blocked',{status:result.status,professional_required:result.professionalRequired,blocker_codes:result.blockerCodes.join(',')});
  }
  document.querySelectorAll('[data-preset]').forEach(button=>button.addEventListener('click',()=>{setValues(presets[button.dataset.preset]);emit('power_station_preset_selected',{preset:button.dataset.preset});}));
  $('powerStationForm').addEventListener('submit',event=>{event.preventDefault();try{$('validation').textContent='';render(core.analyze(values()));}catch(error){$('validation').textContent=error.message;$('validation').focus();}});
  $('resetBtn').addEventListener('click',()=>{$('powerStationForm').reset();setValues(presets.office);$('results').classList.add('hidden');$('validation').textContent='';emit('power_station_reset');});
  $('transferRequired').addEventListener('change',toggleFields);$('affiliateAck').addEventListener('change',updateAffiliate);
  $('affiliateLink').addEventListener('click',event=>{if(event.currentTarget.getAttribute('aria-disabled')==='true'){event.preventDefault();return;}emit('power_station_affiliate_opened',{category:'power_station'});});
  setValues(presets.office);
})();
