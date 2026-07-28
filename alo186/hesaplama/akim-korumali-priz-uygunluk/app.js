(() => {
  'use strict';
  const $=id=>document.getElementById(id);
  const core=window.Alo186SurgeStripSuitability;
  const valueIds=['problemType','loadType','ownership','totalPowerW','powerFactor','startupPowerW','dailyHours','requiredOutlets','requiredUsbPorts','neededCableM','candidateOutlets','candidateUsbPorts','candidateCurrentA','candidatePowerW','candidateJoules','candidateCableM'];
  const checkIds=['surgeClaimVerified','jouleVerified','currentPowerVerified','labelVerified','protectionIndicator','indicatorActive','autoShutoff','breakerOrFuse','manufacturerLoadApproved','groundedWallSocket','earthContinuityKnown','directWallConnection','damageFree','indoorDry','daisyChainPlanned','extensionPlanned'];
  const presets={
    gaming:{problemType:'transient',loadType:'electronics',ownership:'candidate',totalPowerW:650,powerFactor:.9,startupPowerW:900,dailyHours:6,requiredOutlets:5,requiredUsbPorts:0,neededCableM:1.2,candidateOutlets:6,candidateUsbPorts:0,candidateCurrentA:16,candidatePowerW:3500,candidateJoules:1050,candidateCableM:1.5,surgeClaimVerified:true,jouleVerified:true,currentPowerVerified:true,labelVerified:true,protectionIndicator:true,indicatorActive:true,autoShutoff:false,breakerOrFuse:true,manufacturerLoadApproved:true,groundedWallSocket:true,earthContinuityKnown:true,directWallConnection:true,damageFree:true,indoorDry:true,daisyChainPlanned:false,extensionPlanned:false},
    tv:{problemType:'transient',loadType:'av',ownership:'candidate',totalPowerW:350,powerFactor:.9,startupPowerW:550,dailyHours:5,requiredOutlets:4,requiredUsbPorts:0,neededCableM:1,candidateOutlets:5,candidateUsbPorts:0,candidateCurrentA:10,candidatePowerW:2300,candidateJoules:1050,candidateCableM:1.5,surgeClaimVerified:true,jouleVerified:true,currentPowerVerified:true,labelVerified:true,protectionIndicator:true,indicatorActive:true,autoShutoff:false,breakerOrFuse:true,manufacturerLoadApproved:true,groundedWallSocket:true,earthContinuityKnown:true,directWallConnection:true,damageFree:true,indoorDry:true,daisyChainPlanned:false,extensionPlanned:false},
    owned:{problemType:'transient',loadType:'networking',ownership:'owned',totalPowerW:80,powerFactor:.8,startupPowerW:130,dailyHours:24,requiredOutlets:3,requiredUsbPorts:0,neededCableM:1,candidateOutlets:5,candidateUsbPorts:0,candidateCurrentA:10,candidatePowerW:2300,candidateJoules:1050,candidateCableM:1.5,surgeClaimVerified:true,jouleVerified:true,currentPowerVerified:true,labelVerified:true,protectionIndicator:true,indicatorActive:true,autoShutoff:false,breakerOrFuse:true,manufacturerLoadApproved:true,groundedWallSocket:true,earthContinuityKnown:true,directWallConnection:true,damageFree:true,indoorDry:true,daisyChainPlanned:false,extensionPlanned:false},
    voltage:{problemType:'ongoing_voltage',loadType:'electronics',ownership:'candidate',totalPowerW:500,powerFactor:.9,startupPowerW:800,dailyHours:6,requiredOutlets:4,requiredUsbPorts:0,neededCableM:1.5,candidateOutlets:6,candidateUsbPorts:0,candidateCurrentA:16,candidatePowerW:3500,candidateJoules:1050,candidateCableM:1.5,surgeClaimVerified:true,jouleVerified:true,currentPowerVerified:true,labelVerified:true,protectionIndicator:true,indicatorActive:true,autoShutoff:false,breakerOrFuse:true,manufacturerLoadApproved:true,groundedWallSocket:true,earthContinuityKnown:true,directWallConnection:true,damageFree:true,indoorDry:true,daisyChainPlanned:false,extensionPlanned:false}
  };
  const escapeHtml=value=>String(value).replace(/[&<>"']/g,ch=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));
  const list=items=>items.map(item=>`<li>${escapeHtml(item)}</li>`).join('');
  const fmt=(value,digits=2)=>Number(value).toLocaleString('tr-TR',{maximumFractionDigits:digits});
  function values(){const data={};valueIds.forEach(id=>data[id]=$(id).value);checkIds.forEach(id=>data[id]=$(id).checked);return data;}
  function setValues(data){valueIds.forEach(id=>{if(data[id]!=null)$(id).value=String(data[id]);});checkIds.forEach(id=>{$(id).checked=Boolean(data[id]);});}
  function emit(name,params={}){if(typeof window.Alo186Track==='function')window.Alo186Track(name,params);}
  function updateAffiliate(){
    const enabled=$('affiliateAck').checked;
    const link=$('affiliateLink');
    link.classList.toggle('disabled-link',!enabled);
    link.setAttribute('aria-disabled',enabled?'false':'true');
    link.tabIndex=enabled?0:-1;
    emit('surge_strip_affiliate_acknowledged',{acknowledged:enabled});
  }
  function render(result){
    $('results').classList.remove('hidden');
    const labels={compatible:'Teknik sınırlar içinde',conditional:'Koşullu / bilgi doğrulaması gerekli',incompatible:'Uygun değil veya güvenlik engeli var'};
    $('resultStatus').textContent=labels[result.status];
    $('resultStatus').className=`status ${result.status==='compatible'?'ok':result.status==='conditional'?'warn':'bad'}`;
    $('currentMetric').textContent=`${fmt(result.currentA)} A`;
    $('ratioMetric').textContent=`%${fmt(result.loadRatioPct,1)}`;
    $('jouleMetric').textContent=result.targetJoules?`${fmt(result.targetJoules,0)} J rehber sınıfı`:'Surge hedefi yok';
    $('outletMetric').textContent=result.outletSpare>=0?`${fmt(result.outletSpare,0)} boş priz`:`${fmt(Math.abs(result.outletSpare),0)} priz eksik`;
    $('classMetric').textContent=result.recommendedClass;
    $('summary').textContent=`${$('loadType').selectedOptions[0].text} · ${fmt(result.input.totalPowerW,0)} W · ${fmt(result.input.requiredOutlets,0)} priz`;
    $('blockerCard').classList.toggle('hidden',!result.blockers.length);
    $('blockerList').innerHTML=list(result.blockers);
    $('warningList').innerHTML=list(result.warnings.length?result.warnings:['Belirgin uyumsuzluk görülmedi; tam model etiketi, koruma göstergesi ve üretici kılavuzu yine doğrulanmalıdır.']);
    $('checkList').innerHTML=list(result.checks);
    $('noPurchasePanel').classList.toggle('hidden',!result.noPurchaseNeeded);
    $('professionalPanel').classList.toggle('hidden',!result.professionalRequired);
    $('alternatePanel').classList.toggle('hidden',!['ongoing_voltage','neutral_fault','outage_backup'].includes(result.input.problemType));
    $('affiliatePanel').classList.toggle('hidden',!result.commercialAllowed);
    $('affiliateAck').checked=false;updateAffiliate();
    $('results').focus({preventScroll:true});
    $('results').scrollIntoView({behavior:window.matchMedia('(prefers-reduced-motion: reduce)').matches?'auto':'smooth',block:'start'});
    emit('surge_strip_suitability_completed',{status:result.status,commercial_allowed:result.commercialAllowed,no_purchase_needed:result.noPurchaseNeeded,problem_type:result.input.problemType,load_type:result.input.loadType});
    if(result.noPurchaseNeeded)emit('surge_strip_no_purchase',{reason:'owned_product_sufficient'});
    if(!result.commercialAllowed)emit('surge_strip_affiliate_blocked',{status:result.status,professional_required:result.professionalRequired,problem_type:result.input.problemType});
  }
  document.querySelectorAll('[data-preset]').forEach(button=>button.addEventListener('click',()=>{setValues(presets[button.dataset.preset]);emit('surge_strip_preset_selected',{preset:button.dataset.preset});}));
  $('surgeStripForm').addEventListener('submit',event=>{event.preventDefault();try{$('validation').textContent='';render(core.analyze(values()));}catch(error){$('validation').textContent=error.message;$('validation').focus();}});
  $('resetBtn').addEventListener('click',()=>{$('surgeStripForm').reset();setValues(presets.gaming);$('results').classList.add('hidden');$('validation').textContent='';emit('surge_strip_reset');});
  $('affiliateAck').addEventListener('change',updateAffiliate);
  $('affiliateLink').addEventListener('click',event=>{if(event.currentTarget.getAttribute('aria-disabled')==='true'){event.preventDefault();return;}emit('surge_strip_product_center_opened',{category:'surge_strip'});});
  setValues(presets.gaming);
})();
