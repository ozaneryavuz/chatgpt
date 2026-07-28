(() => {
  'use strict';
  const $=id=>document.getElementById(id);
  const core=window.Alo186ExtensionLeadCompatibility;
  const ids=['totalPower','peakPower','length','section','productType','reelState','labelUnwoundA','labelWoundA','loadType','environment','rcdProtection','earthRequirement','earthPresent','thermalCutout'];
  const checks=['outdoorRated','manufacturerVerified','daisyChain','permanentUse','damageOrHeat'];
  const presets={
    office:{totalPower:350,peakPower:450,length:10,section:1.5,productType:'lead',reelState:'unwound',labelUnwoundA:16,labelWoundA:'',loadType:'electronics',environment:'indoor',rcdProtection:'yes',earthRequirement:'class1',earthPresent:'yes',thermalCutout:'unknown',outdoorRated:false,manufacturerVerified:true,daisyChain:false,permanentUse:false,damageOrHeat:false},
    reel:{totalPower:1800,peakPower:1800,length:25,section:1.5,productType:'reel',reelState:'wound',labelUnwoundA:16,labelWoundA:5,loadType:'resistive',environment:'indoor',rcdProtection:'yes',earthRequirement:'class1',earthPresent:'yes',thermalCutout:'yes',outdoorRated:false,manufacturerVerified:true,daisyChain:false,permanentUse:false,damageOrHeat:false},
    garden:{totalPower:900,peakPower:2200,length:30,section:1.5,productType:'reel',reelState:'unwound',labelUnwoundA:16,labelWoundA:5,loadType:'motor',environment:'outdoor',rcdProtection:'unknown',earthRequirement:'class1',earthPresent:'yes',thermalCutout:'yes',outdoorRated:true,manufacturerVerified:true,daisyChain:false,permanentUse:false,damageOrHeat:false}
  };
  const escapeHtml=value=>String(value).replace(/[&<>"']/g,ch=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));
  const list=items=>items.map(item=>`<li>${escapeHtml(item)}</li>`).join('');
  const fmt=(value,digits=1)=>Number(value).toLocaleString('tr-TR',{maximumFractionDigits:digits});
  function emit(name,params={}){if(typeof window.Alo186Track==='function')window.Alo186Track(name,params);}
  function values(){const data={};ids.forEach(id=>data[id]=$(id).value);checks.forEach(id=>data[id]=$(id).checked);return data;}
  function setValues(data){ids.forEach(id=>{if(data[id]!=null)$(id).value=String(data[id]);});checks.forEach(id=>{$(id).checked=Boolean(data[id]);});syncFields();}
  function syncFields(){
    const reel=$('productType').value==='reel';
    $('reelFields').classList.toggle('hidden',!reel);
    $('labelWoundA').disabled=!reel;
    $('reelState').disabled=!reel;
    $('thermalCutout').disabled=!reel;
  }
  function updateAffiliate(){const enabled=$('affiliateAck').checked;const link=$('productCenterLink');link.classList.toggle('disabled-link',!enabled);link.setAttribute('aria-disabled',enabled?'false':'true');link.tabIndex=enabled?0:-1;}
  function render(result){
    $('results').classList.remove('hidden');
    const labels={compatible:'Etiket sınırları içinde',conditional:'Koşullu / yeniden doğrulama gerekli',incompatible:'Kullanmayın / uygun değil'};
    $('resultStatus').textContent=labels[result.status];
    $('resultStatus').className=`status ${result.status==='compatible'?'ok':result.status==='conditional'?'warn':'bad'}`;
    $('currentMetric').textContent=`${fmt(result.current)} A`;
    $('ratingMetric').textContent=`${fmt(result.activeRating)} A`;
    $('dropMetric').textContent=`%${fmt(result.voltageDropPct,2)}`;
    $('voltageMetric').textContent=`${fmt(result.deliveredVoltage,1)} V`;
    $('summaryLine').textContent=`${fmt(result.input.totalPower,0)} W sürekli yük · ${fmt(result.input.length,0)} m · ${fmt(result.input.section,2)} mm² bakır · ${result.input.productType==='reel'?'kablo makarası':'uzatma kablosu'}`;
    $('blockerCard').classList.toggle('hidden',!result.blockers.length);$('blockerList').innerHTML=list(result.blockers);
    $('warningCard').classList.toggle('hidden',!result.warnings.length);$('warningList').innerHTML=list(result.warnings);
    $('checkList').innerHTML=list(result.checks);
    $('professionalPanel').classList.toggle('hidden',!result.professionalRequired);
    $('affiliatePanel').classList.toggle('hidden',!result.commercialAllowed);
    $('affiliateAck').checked=false;updateAffiliate();
    $('results').focus({preventScroll:true});$('results').scrollIntoView({behavior:window.matchMedia('(prefers-reduced-motion: reduce)').matches?'auto':'smooth',block:'start'});
    emit('extension_lead_compatibility_completed',{status:result.status,professional_required:result.professionalRequired,commercial_allowed:result.commercialAllowed,voltage_drop_band:result.voltageDropPct>5?'over5':result.voltageDropPct>3?'3to5':'under3'});
  }
  document.querySelectorAll('[data-preset]').forEach(button=>button.addEventListener('click',()=>{setValues(presets[button.dataset.preset]);emit('extension_lead_preset_selected',{preset:button.dataset.preset});}));
  $('productType').addEventListener('change',syncFields);
  $('compatibilityForm').addEventListener('submit',event=>{event.preventDefault();try{$('validation').textContent='';render(core.analyze(values()));}catch(error){$('validation').textContent=error.message;$('validation').focus();}});
  $('resetBtn').addEventListener('click',()=>{$('compatibilityForm').reset();setValues(presets.office);$('results').classList.add('hidden');$('validation').textContent='';emit('extension_lead_compatibility_reset');});
  $('affiliateAck').addEventListener('change',updateAffiliate);
  $('productCenterLink').addEventListener('click',event=>{if(event.currentTarget.getAttribute('aria-disabled')==='true'){event.preventDefault();return;}emit('extension_lead_product_center_opened',{category:'extension_lead'});});
  setValues(presets.office);
})();