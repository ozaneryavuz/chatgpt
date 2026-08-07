(() => {
  'use strict';
  const $=id=>document.getElementById(id);
  const core=window.Alo186ExtensionSuitability;
  const valueIds=['evaluationMode','voltage','loadPower','powerFactor','loadType','startMultiplier','usage','intendedUse','length','area','ratedCurrent','reelState','woundMaxPower','unwoundMaxPower','environment','applianceClass'];
  const checkIds=['factoryAssembled','labelVerified','damageFree','earthPresent','outdoorRated','thermalProtection','daisyChain','recallChecked'];
  const gateIds=['affiliateNeedAck','affiliateSpecAck','affiliateDisclosureAck'];
  const presets={
    office:{evaluationMode:'existing',voltage:230,loadPower:300,powerFactor:.95,loadType:'electronic',startMultiplier:'',usage:'short',intendedUse:'portable',length:15,area:1.5,ratedCurrent:16,reelState:'none',woundMaxPower:'',unwoundMaxPower:'',environment:'indoor',applianceClass:'classI',factoryAssembled:true,labelVerified:true,damageFree:true,earthPresent:true,outdoorRated:false,thermalProtection:false,daisyChain:false,recallChecked:true},
    garden:{evaluationMode:'planned',voltage:230,loadPower:1200,powerFactor:.8,loadType:'motor',startMultiplier:3,usage:'short',intendedUse:'portable',length:30,area:2.5,ratedCurrent:16,reelState:'unwound',woundMaxPower:1000,unwoundMaxPower:3500,environment:'outdoor',applianceClass:'classI',factoryAssembled:true,labelVerified:true,damageFree:true,earthPresent:true,outdoorRated:true,thermalProtection:true,daisyChain:false,recallChecked:true},
    risky:{evaluationMode:'existing',voltage:230,loadPower:2000,powerFactor:1,loadType:'resistive',startMultiplier:'',usage:'continuous',intendedUse:'heater',length:25,area:1.5,ratedCurrent:10,reelState:'wound',woundMaxPower:800,unwoundMaxPower:3000,environment:'indoor',applianceClass:'classI',factoryAssembled:true,labelVerified:true,damageFree:true,earthPresent:true,outdoorRated:false,thermalProtection:true,daisyChain:false,recallChecked:false}
  };
  let last=null;
  function emit(name,params={}){if(typeof window.Alo186Track==='function')window.Alo186Track(name,params);}
  function values(){const data={};valueIds.forEach(id=>data[id]=$(id).value);checkIds.forEach(id=>data[id]=$(id).checked);return data;}
  function setValues(data){valueIds.forEach(id=>{if(data[id]!=null)$(id).value=String(data[id]);});checkIds.forEach(id=>{$(id).checked=Boolean(data[id]);});}
  const escapeHtml=value=>String(value).replace(/[&<>"']/g,ch=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));
  const list=items=>items.map(item=>`<li>${escapeHtml(item)}</li>`).join('');
  const fmt=(value,digits=1)=>Number(value).toLocaleString('tr-TR',{maximumFractionDigits:digits});
  function updateAffiliate(){const enabled=gateIds.every(id=>$(id).checked);const link=$('productCenterLink');link.classList.toggle('disabled-link',!enabled);link.setAttribute('aria-disabled',enabled?'false':'true');link.tabIndex=enabled?0:-1;}
  function render(result){
    last=result;
    $('results').classList.remove('hidden');
    const labels={compatible:'Yeni ürün için koşullu teknik eşleşme',no_buy:'Mevcut ürün yeterli — satın alma yok',conditional:'Koşullu / etiket doğrulaması gerekli',incompatible:'Uygun değil veya riskli'};
    $('resultStatus').textContent=labels[result.status];$('resultStatus').className=`status ${['compatible','no_buy'].includes(result.status)?'ok':result.status==='conditional'?'warn':'bad'}`;
    $('currentMetric').textContent=`${fmt(result.operatingCurrent)} A`;
    $('dropMetric').textContent=`%${fmt(result.dropPercent)} · ${fmt(result.dropVolts)} V`;
    $('lossMetric').textContent=`${fmt(result.cableLoss,0)} W`;
    $('minimumMetric').textContent=`${result.recommendedArea?fmt(result.recommendedArea):'>4'} mm² · ${result.recommendedRatedCurrent?result.recommendedRatedCurrent:'>16'} A`;
    $('resultSummary').textContent=`${fmt(result.input.loadPower,0)} W · ${fmt(result.input.length,0)} m · ${fmt(result.input.area,2)} mm² · ${fmt(result.input.ratedCurrent,0)} A etiket`;
    $('blockerCard').classList.toggle('hidden',!result.blockers.length);$('blockerList').innerHTML=list(result.blockers);
    $('warningList').innerHTML=list(result.warnings.length?result.warnings:['Belirgin sınır aşımı görülmedi; ürün etiketi, priz-devre ve üretici kılavuzu yine doğrulanmalıdır.']);
    $('checkList').innerHTML=list(result.checks);
    $('professionalPanel').classList.toggle('hidden',!result.professionalRequired);
    $('affiliatePanel').classList.toggle('hidden',!result.commercialAllowed);gateIds.forEach(id=>$(id).checked=false);updateAffiliate();
    $('jsonButton').disabled=false;$('icsButton').disabled=false;
    $('results').focus({preventScroll:true});$('results').scrollIntoView({behavior:window.matchMedia('(prefers-reduced-motion: reduce)').matches?'auto':'smooth',block:'start'});
    emit('extension_suitability_completed',{status:result.status,professional_required:result.professionalRequired,commercial_allowed:result.commercialAllowed,purchase_decision:result.purchaseDecision,drop_band:result.dropPercent<=3?'low':result.dropPercent<=5?'medium':'high'});
  }
  function download(name,content,type){const blob=new Blob([content],{type});const url=URL.createObjectURL(blob);const a=document.createElement('a');a.href=url;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(url),0);}
  document.querySelectorAll('[data-preset]').forEach(button=>button.addEventListener('click',()=>{setValues(presets[button.dataset.preset]);emit('extension_suitability_preset_selected',{preset:button.dataset.preset});}));
  $('extensionForm').addEventListener('submit',event=>{event.preventDefault();try{$('validation').textContent='';render(core.analyze(values()));}catch(error){$('validation').textContent=error.message;$('validation').focus();}});
  $('resetBtn').addEventListener('click',()=>{$('extensionForm').reset();setValues(presets.office);last=null;$('results').classList.add('hidden');$('validation').textContent='';$('jsonButton').disabled=true;$('icsButton').disabled=true;emit('extension_suitability_reset');});
  gateIds.forEach(id=>$(id).addEventListener('change',updateAffiliate));
  $('productCenterLink').addEventListener('click',event=>{if(event.currentTarget.getAttribute('aria-disabled')==='true'){event.preventDefault();return;}emit('extension_product_center_opened',{category:last?.affiliateCategory||'extension_cord'});});
  $('jsonButton').addEventListener('click',()=>{if(!last)return;download('alo186-uzatma-kablosu-teknik-fis.json',JSON.stringify({createdAt:new Date().toISOString(),tool:'ALO186 uzatma kablosu uygunluk testi',result:last.status,purchaseDecision:last.purchaseDecision,commercialAllowed:last.commercialAllowed,metrics:{operatingCurrentA:Number(last.operatingCurrent.toFixed(2)),dropPercent:Number(last.dropPercent.toFixed(2)),dropVolts:Number(last.dropVolts.toFixed(2)),recommendedAreaMm2:last.recommendedArea,recommendedRatedCurrentA:last.recommendedRatedCurrent},personalDataCollected:false,commercialRankingFieldsUsed:[]},null,2),'application/json');});
  $('icsButton').addEventListener('click',()=>{if(!last)return;const d=new Date();d.setDate(d.getDate()+180);const stamp=d.toISOString().replace(/[-:]/g,'').replace(/\.\d{3}/,'');const ics=`BEGIN:VCALENDAR\r\nVERSION:2.0\r\nPRODID:-//ALO186//Uzatma Kablosu Kontrolu//TR\r\nBEGIN:VEVENT\r\nDTSTART:${stamp}\r\nDURATION:PT20M\r\nSUMMARY:Uzatma kablosu veya makarayı yeniden kontrol et\r\nDESCRIPTION:Fiş-priz ısınması, dış kılıf, topraklama, etiket akımı, kesit, IP, makara termiği ve resmî geri çağırma duyurusunu doğrula. Yük veya ortam değiştiyse hesabı yenile.\r\nEND:VEVENT\r\nEND:VCALENDAR\r\n`;download('alo186-uzatma-kablosu-180-gun.ics',ics,'text/calendar');});
  setValues(presets.office);
})();
