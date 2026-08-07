(() => {
  'use strict';
  const $=id=>document.getElementById(id);
  const core=window.Alo186BackupSelector;
  const STORAGE_KEY='alo186_backup_selector_v2';
  const MAX_AGE_MS=30*24*60*60*1000;
  const presets={
    internet:{continuousW:20,peakW:25,hours:8,transition:'instant',scope:'dc-network',portable:'no',fuel:'no',outdoor:'no',solar:'no',phase:'single',medical:false},
    office:{continuousW:250,peakW:500,hours:3,transition:'instant',scope:'plug',portable:'yes',fuel:'no',outdoor:'no',solar:'no',phase:'single',medical:false},
    fridge:{continuousW:350,peakW:1200,hours:6,transition:'brief',scope:'motor',portable:'no',fuel:'no',outdoor:'no',solar:'no',phase:'single',medical:false},
    business:{continuousW:800,peakW:1800,hours:4,transition:'instant',scope:'plug',portable:'no',fuel:'no',outdoor:'no',solar:'no',phase:'single',medical:false}
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
  function sanitizeTechnical(data){
    const allowed=['continuousW','peakW','hours','transition','scope','phase','portable','fuel','outdoor','solar'];
    const clean={};
    allowed.forEach(key=>{if(data&&Object.prototype.hasOwnProperty.call(data,key))clean[key]=String(data[key]);});
    return clean;
  }
  function setValues(data){
    Object.entries(sanitizeTechnical(data)).forEach(([key,value])=>{
      const el=$(key);
      if(el)el.value=String(value);
    });
    $('medical').checked=Boolean(data&&data.medical);
  }
  function save(data){
    try{
      localStorage.setItem(STORAGE_KEY,JSON.stringify({savedAt:Date.now(),input:sanitizeTechnical(data)}));
      $('restoreBtn').hidden=false;
    }catch(_){ }
  }
  function load(){
    try{
      const stored=JSON.parse(localStorage.getItem(STORAGE_KEY)||'null');
      if(!stored||!stored.savedAt||Date.now()-stored.savedAt>MAX_AGE_MS){
        localStorage.removeItem(STORAGE_KEY);
        return null;
      }
      return sanitizeTechnical(stored.input||{});
    }catch(_){return null;}
  }
  function clearStored(){
    try{localStorage.removeItem(STORAGE_KEY);}catch(_){ }
    $('restoreBtn').hidden=true;
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
    $('results').scrollIntoView({behavior:window.matchMedia('(prefers-reduced-motion: reduce)').matches?'auto':'smooth',block:'start'});
    emit('backup_solution_selector_completed',{recommendation:result.recommendation,professional_required:result.professionalRequired,commercial_allowed:result.commercialAllowed,energy_band:result.energyWh<1000?'under_1kwh':result.energyWh<3000?'1_3kwh':'over_3kwh'});
  }
  function calculate(input,{restored=false}={}){
    $('validation').textContent='';
    try{
      const result=core.analyze(input);
      render(result);
      save(input);
      if(restored)emit('backup_solution_selector_restored',{recommendation:result.recommendation});
    }catch(error){$('validation').textContent=error.message;$('validation').focus();}
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
    calculate(values());
  });
  $('restoreBtn').addEventListener('click',()=>{
    const stored=load();
    if(!stored){$('restoreBtn').hidden=true;return;}
    setValues(stored);
    calculate(stored,{restored:true});
  });
  $('resetBtn').addEventListener('click',()=>{
    $('selectorForm').reset();setValues(presets.office);$('results').classList.add('hidden');$('validation').textContent='';clearStored();emit('backup_solution_selector_local_data_cleared');
  });
  $('affiliateAck').addEventListener('change',updateAffiliateLink);
  $('productCenterLink').addEventListener('click',event=>{
    if($('productCenterLink').getAttribute('aria-disabled')==='true'){event.preventDefault();return;}
    emit('backup_solution_product_center_opened',{placement:'backup_solution_selector'});
  });
  $('nextStepLink').addEventListener('click',()=>emit('backup_solution_next_tool_opened',{url:$('nextStepLink').href}));
  $('restoreBtn').hidden=!load();
})();