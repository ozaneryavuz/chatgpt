(() => {
  'use strict';
  const $=id=>document.getElementById(id);
  const core=window.Alo186BackupSelector;
  const presets={
    internet:{continuousW:20,peakW:25,hours:8,transition:'instant',scope:'dc-network',portable:'no',fuel:'no',outdoor:'no',solar:'no',phase:'single'},
    office:{continuousW:250,peakW:500,hours:3,transition:'instant',scope:'plug',portable:'yes',fuel:'no',outdoor:'no',solar:'no',phase:'single'},
    fridge:{continuousW:350,peakW:1200,hours:6,transition:'brief',scope:'motor',portable:'no',fuel:'no',outdoor:'no',solar:'no',phase:'single'},
    business:{continuousW:800,peakW:1800,hours:4,transition:'instant',scope:'plug',portable:'no',fuel:'no',outdoor:'no',solar:'no',phase:'single'}
  };

  function emit(name,params={}){
    if(typeof window.Alo186Track==='function')window.Alo186Track(name,params);
  }
  function values(){
    return {
      continuousW:$('continuousW').value,peakW:$('peakW').value,hours:$('hours').value,
      transition:$('transition').value,scope:$('scope').value,phase:$('phase').value,
      portable:$('portable').value,fuel:$('fuel').value,outdoor:$('outdoor').value,
      solar:$('solar').value,medical:$('medical').checked
    };
  }
  function setValues(data){
    Object.entries(data).forEach(([key,value])=>{const el=$(key);if(el)el.value=String(value);});
    $('medical').checked=false;
  }
  function li(items){return items.map(item=>`<li>${escapeHtml(item)}</li>`).join('');}
  function escapeHtml(value){return String(value).replace(/[&<>"']/g,ch=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));}
  function formatWh(value){return value>=1000?`${(value/1000).toLocaleString('tr-TR',{maximumFractionDigits:2})} kWh`:`${Math.round(value)} Wh`;}
  function render(result){
    $('results').classList.remove('hidden');
    $('recommendationLabel').textContent=result.solution.label;
    $('recommendationNote').textContent=result.solution.note;
    $('continuousMetric').textContent=`${Math.round(result.input.continuousW)} W`;
    $('peakMetric').textContent=`${Math.round(result.input.peakW)} W`;
    $('energyMetric').textContent=formatWh(result.energyWh);
    $('professionalMetric').textContent=result.professionalRequired?'Gerekli':'Düşük riskli ön seçim';
    $('resultStatus').textContent=result.professionalRequired?'Uzman doğrulaması':'Ön seçim tamamlandı';
    $('resultStatus').className=`status ${result.professionalRequired?'bad':'ok'}`;
    $('reasonList').innerHTML=li(result.reasons);
    $('alternativeList').innerHTML=li(result.alternatives);
    $('checkList').innerHTML=li(result.checks);
    $('nextStepText').textContent=`${result.solution.label} için güç, süre ve teknik sınırları ayrıntılı araçta doğrulayın.`;
    $('nextStepLink').href=result.solution.nextStepUrl;
    $('nextStepLink').textContent=result.solution.nextStepLabel;
    $('affiliatePanel').classList.toggle('hidden',!result.commercialAllowed);
    $('professionalPanel').classList.toggle('hidden',!result.professionalRequired);
    $('affiliateAck').checked=false;
    updateAffiliateLink();
    $('results').focus({preventScroll:true});
    $('results').scrollIntoView({behavior:'smooth',block:'start'});
    emit('backup_solution_selector_completed',{recommendation:result.recommendation,professional_required:result.professionalRequired,commercial_allowed:result.commercialAllowed,energy_band:result.energyWh<1000?'under_1kwh':result.energyWh<3000?'1_3kwh':'over_3kwh'});
  }
  function updateAffiliateLink(){
    const enabled=$('affiliateAck').checked;
    const link=$('productCenterLink');
    link.classList.toggle('disabled-link',!enabled);
    link.setAttribute('aria-disabled',enabled?'false':'true');
    link.tabIndex=enabled?0:-1;
  }

  document.querySelectorAll('[data-preset]').forEach(button=>button.addEventListener('click',()=>{
    setValues(presets[button.dataset.preset]);
    emit('backup_solution_preset_selected',{preset:button.dataset.preset});
  }));
  $('selectorForm').addEventListener('submit',event=>{
    event.preventDefault();
    $('validation').textContent='';
    try{render(core.analyze(values()));}
    catch(error){$('validation').textContent=error.message;$('validation').focus();}
  });
  $('resetBtn').addEventListener('click',()=>{
    $('selectorForm').reset();setValues(presets.office);$('results').classList.add('hidden');$('validation').textContent='';
  });
  $('affiliateAck').addEventListener('change',updateAffiliateLink);
  $('productCenterLink').addEventListener('click',event=>{
    if($('productCenterLink').getAttribute('aria-disabled')==='true'){event.preventDefault();return;}
    emit('backup_solution_product_center_opened',{placement:'backup_solution_selector'});
  });
  $('nextStepLink').addEventListener('click',()=>emit('backup_solution_next_tool_opened',{url:$('nextStepLink').href}));
})();
