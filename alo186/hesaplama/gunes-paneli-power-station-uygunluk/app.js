(() => {
  'use strict';
  const $=id=>document.getElementById(id);
  const core=window.Alo186SolarInputCompatibility;
  const ids=['panelPower','panelVoc','panelVmp','panelIsc','panelImp','vocTempCoeff','seriesCount','parallelCount','minTemp','mpptMinV','mpptMaxV','absoluteMaxVoc','maxInputCurrent','maxShortCircuitCurrent','maxInputPower','stationCapacity','currentSoc','targetSoc','derating','application'];
  const presets={
    portable:{panelPower:200,panelVoc:24.3,panelVmp:20.5,panelIsc:10.3,panelImp:9.8,vocTempCoeff:.28,seriesCount:1,parallelCount:1,minTemp:0,mpptMinV:11,mpptMaxV:60,absoluteMaxVoc:60,maxInputCurrent:15,maxShortCircuitCurrent:'',maxInputPower:500,stationCapacity:768,currentSoc:20,targetSoc:80,derating:.8,application:'portable',manualVerified:true,connectorKnown:true,factoryCable:true},
    series:{panelPower:200,panelVoc:24.3,panelVmp:20.5,panelIsc:10.3,panelImp:9.8,vocTempCoeff:.28,seriesCount:3,parallelCount:1,minTemp:-10,mpptMinV:30,mpptMaxV:150,absoluteMaxVoc:150,maxInputCurrent:15,maxShortCircuitCurrent:'',maxInputPower:1200,stationCapacity:2000,currentSoc:20,targetSoc:80,derating:.8,application:'portable',manualVerified:true,connectorKnown:true,factoryCable:false},
    overvoltage:{panelPower:400,panelVoc:37.2,panelVmp:31.2,panelIsc:13.8,panelImp:12.9,vocTempCoeff:.29,seriesCount:4,parallelCount:1,minTemp:-10,mpptMinV:30,mpptMaxV:150,absoluteMaxVoc:150,maxInputCurrent:15,maxShortCircuitCurrent:'',maxInputPower:1600,stationCapacity:3600,currentSoc:20,targetSoc:80,derating:.8,application:'fixed',manualVerified:true,connectorKnown:false,factoryCable:false}
  };
  function emit(name,params={}){if(typeof window.Alo186Track==='function')window.Alo186Track(name,params);}
  function values(){const data={};ids.forEach(id=>data[id]=$(id).value);['manualVerified','connectorKnown','factoryCable'].forEach(id=>data[id]=$(id).checked);return data;}
  function setValues(data){ids.forEach(id=>{if(data[id]!=null)$(id).value=String(data[id]);});['manualVerified','connectorKnown','factoryCable'].forEach(id=>{$(id).checked=Boolean(data[id]);});}
  const escapeHtml=value=>String(value).replace(/[&<>"']/g,ch=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));
  const list=items=>items.map(item=>`<li>${escapeHtml(item)}</li>`).join('');
  const fmt=(value,digits=1)=>Number(value).toLocaleString('tr-TR',{maximumFractionDigits:digits});
  function updateAffiliate(){const enabled=$('affiliateAck').checked;const link=$('productCenterLink');link.classList.toggle('disabled-link',!enabled);link.setAttribute('aria-disabled',enabled?'false':'true');link.tabIndex=enabled?0:-1;}
  function render(result){
    $('results').classList.remove('hidden');
    const labels={compatible:'Elektriksel sınırlar içinde',conditional:'Koşullu / kılavuz doğrulaması gerekli',incompatible:'Uyumsuz veya riskli'};
    $('resultStatus').textContent=labels[result.status];$('resultStatus').className=`status ${result.status==='compatible'?'ok':result.status==='conditional'?'warn':'bad'}`;
    $('coldVocMetric').textContent=`${fmt(result.coldVoc)} V`;$('vmpMetric').textContent=`${fmt(result.arrayVmp)} V`;$('currentMetric').textContent=`${fmt(result.arrayImp)} A`;$('powerMetric').textContent=`${fmt(result.estimatedAcceptedPower,0)} W`;
    $('arraySummary').textContent=`${result.panelCount} panel · ${result.input.seriesCount} seri × ${result.input.parallelCount} paralel · ${fmt(result.arrayPower,0)} W etiket toplamı`;
    $('blockerCard').classList.toggle('hidden',!result.blockers.length);$('blockerList').innerHTML=list(result.blockers);
    $('warningList').innerHTML=list(result.warnings.length?result.warnings:['Belirgin sınır aşımı görülmedi; yine de tam model kılavuzu ve kablo/konnektör uyumu doğrulanmalıdır.']);
    $('checkList').innerHTML=list(result.checks);
    $('chargeCard').classList.toggle('hidden',result.idealHours==null);
    if(result.idealHours!=null){$('energyNeed').textContent=`${fmt(result.energyNeed,0)} Wh`;$('chargeHours').textContent=`${fmt(result.idealHours,1)} saat`;$('chargeNote').textContent=`${Math.round(result.input.derating*100)}% gerçek koşul katsayısı ve ${fmt(result.estimatedAcceptedPower,0)} W kabul edilen güç varsayımıyla; bulut, yön, sıcaklık ve şarj eğrisi süreyi uzatabilir.`;}
    $('professionalPanel').classList.toggle('hidden',!result.professionalRequired);
    $('affiliatePanel').classList.toggle('hidden',!result.commercialAllowed);$('affiliateAck').checked=false;updateAffiliate();
    $('results').focus({preventScroll:true});$('results').scrollIntoView({behavior:window.matchMedia('(prefers-reduced-motion: reduce)').matches?'auto':'smooth',block:'start'});
    emit('solar_input_compatibility_completed',{status:result.status,professional_required:result.professionalRequired,commercial_allowed:result.commercialAllowed,panel_count:result.panelCount});
  }
  document.querySelectorAll('[data-preset]').forEach(button=>button.addEventListener('click',()=>{setValues(presets[button.dataset.preset]);emit('solar_input_preset_selected',{preset:button.dataset.preset});}));
  $('compatibilityForm').addEventListener('submit',event=>{event.preventDefault();try{$('validation').textContent='';render(core.analyze(values()));}catch(error){$('validation').textContent=error.message;$('validation').focus();}});
  $('resetBtn').addEventListener('click',()=>{$('compatibilityForm').reset();setValues(presets.portable);$('results').classList.add('hidden');$('validation').textContent='';emit('solar_input_compatibility_reset');});
  $('affiliateAck').addEventListener('change',updateAffiliate);
  $('productCenterLink').addEventListener('click',event=>{if(event.currentTarget.getAttribute('aria-disabled')==='true'){event.preventDefault();return;}emit('solar_input_product_center_opened',{category:'portable_solar'});});
  setValues(presets.portable);
})();
