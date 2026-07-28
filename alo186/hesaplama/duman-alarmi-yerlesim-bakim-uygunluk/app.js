(() => {
  'use strict';
  const $=id=>document.getElementById(id);
  const core=window.Alo186SmokeAlarmSuitability;

  const presets={
    flat:{useCase:'home',ownership:'candidate',floors:1,basement:false,bedrooms:2,sleepingAreas:1,sleepingLevels:1,existingWorking:1,plannedNew:2,alarmAgeYears:0,cookingDistanceM:4,interconnect:'yes'},
    duplex:{useCase:'home',ownership:'candidate',floors:2,basement:false,bedrooms:3,sleepingAreas:1,sleepingLevels:1,existingWorking:1,plannedNew:4,alarmAgeYears:0,cookingDistanceM:4,interconnect:'yes'},
    rental:{useCase:'short_term',ownership:'owned',floors:1,basement:false,bedrooms:2,sleepingAreas:1,sleepingLevels:1,existingWorking:3,plannedNew:0,alarmAgeYears:4,cookingDistanceM:4,interconnect:'yes'},
    hotel:{useCase:'hotel',ownership:'candidate',floors:3,basement:true,bedrooms:20,sleepingAreas:3,sleepingLevels:3,existingWorking:20,plannedNew:10,alarmAgeYears:0,cookingDistanceM:4,interconnect:'yes'}
  };

  function emit(name,params={}){if(typeof window.Alo186Track==='function')window.Alo186Track(name,params);}
  function setValue(id,value){const element=$(id);if(!element)return;if(element.type==='checkbox')element.checked=Boolean(value);else element.value=String(value);}

  function applyPreset(name){
    const preset=presets[name];
    if(!preset)return;
    Object.entries(preset).forEach(([key,value])=>setValue(key,value));
    const safe=name!=='hotel';
    ['exactModelVerified','certificationVerified','testButton','lowBatteryWarning','manufactureDateKnown','placementVerified','notDisabled','damageFree'].forEach(id=>setValue(id,safe));
    setValue('monthlyTestPassed',name==='rental');
    setValue('accessibilityRequired',false);
    setValue('accessibilitySupported',false);
    setValue('activeEmergency',false);
    $('validation').textContent='';
    emit('smoke_alarm_preset_selected',{preset:name});
  }

  function formData(){
    return {
      useCase:$('useCase').value,ownership:$('ownership').value,floors:$('floors').value,basement:$('basement').checked,
      bedrooms:$('bedrooms').value,sleepingAreas:$('sleepingAreas').value,sleepingLevels:$('sleepingLevels').value,
      existingWorking:$('existingWorking').value,plannedNew:$('plannedNew').value,alarmAgeYears:$('alarmAgeYears').value,
      cookingDistanceM:$('cookingDistanceM').value,interconnect:$('interconnect').value,
      exactModelVerified:$('exactModelVerified').checked,certificationVerified:$('certificationVerified').checked,
      testButton:$('testButton').checked,lowBatteryWarning:$('lowBatteryWarning').checked,manufactureDateKnown:$('manufactureDateKnown').checked,
      monthlyTestPassed:$('monthlyTestPassed').checked,placementVerified:$('placementVerified').checked,notDisabled:$('notDisabled').checked,
      damageFree:$('damageFree').checked,accessibilityRequired:$('accessibilityRequired').checked,
      accessibilitySupported:$('accessibilitySupported').checked,activeEmergency:$('activeEmergency').checked
    };
  }

  function escapeHtml(value){return String(value??'').replace(/[&<>"']/g,char=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));}
  function listMarkup(title,items,className=''){if(!items.length)return'';return `<section class="result-list ${className}"><h3>${escapeHtml(title)}</h3><ul>${items.map(item=>`<li>${escapeHtml(item)}</li>`).join('')}</ul></section>`;}

  function renderGate(result){
    const gate=$('commercialGate');
    gate.classList.remove('hidden');
    if(result.productRouteAllowed){
      gate.className='decision-box affiliate';
      gate.innerHTML=`<span class="eyebrow">Şeffaf ürün rotası</span><h3>Eksik alarm ihtiyacını teknik kriterlerle karşılaştırın</h3><p>ALO186 bazı dış ürün bağlantılarından satış ortaklığı komisyonu kazanabilir; kullanıcıya ek maliyet yansımaz. Fiyat, stok, puan ve garanti ALO186 üzerinde gösterilmez.</p><label class="check-item"><input type="checkbox" data-confirm-need><span><strong>Mevcut çalışan alarm sayım yetersiz.</strong><small>Çalışır ve yeterli alarmlar varsa yeni satın alma gerekmeyebilir.</small></span></label><label class="check-item"><input type="checkbox" data-confirm-affiliate><span><strong>Tam modeli, belgeyi ve satış ortaklığı niteliğini anladım.</strong><small>Test düğmesi, düşük pil uyarısı, üretim tarihi ve bağlantı özelliğini ürün sayfasında yeniden doğrulayacağım.</small></span></label><a class="btn btn-primary disabled-link" data-product-route aria-disabled="true" tabindex="-1" href="${result.productRoute}" rel="nofollow">Akıllı Ürün Merkezi'ni aç</a><button type="button" class="btn btn-secondary" data-no-purchase>Şimdilik satın alma</button>`;
      const checks=[...gate.querySelectorAll('input[type="checkbox"]')];
      const link=gate.querySelector('[data-product-route]');
      const sync=()=>{const enabled=checks.every(item=>item.checked);link.classList.toggle('disabled-link',!enabled);link.setAttribute('aria-disabled',enabled?'false':'true');link.tabIndex=enabled?0:-1;};
      checks.forEach(item=>item.addEventListener('change',sync));
      link.addEventListener('click',event=>{if(link.getAttribute('aria-disabled')==='true'){event.preventDefault();return;}emit('smoke_alarm_product_route_opened',{status:result.status,need_band:result.purchaseNeed>4?'high':result.purchaseNeed>1?'medium':'low'});});
      gate.querySelector('[data-no-purchase]').addEventListener('click',()=>{gate.innerHTML=`<span class="eyebrow">Satın almama seçildi</span><h3>Önce planı ve mevcut alarmları yeniden doğrulayın</h3><p>Yeni ürün almadan önce aylık test, üretim tarihi, mutfak uzaklığı ve gerçek yerleşim krokisini kontrol edin.</p><a class="btn btn-secondary" href="${result.maintenanceRoute}">Bakım planını aç</a>`;emit('smoke_alarm_no_purchase_selected',{status:result.status});});
    }else if(result.noPurchase){
      gate.className='decision-box no-purchase';
      gate.innerHTML=`<span class="eyebrow">Satın almama sonucu</span><h3>Mevcut çalışan alarmlar yeterli görünüyor</h3><p>Aylık test, üretim tarihi, temizlik, pil/ömür sonu uyarısı ve yerleşim kontrolünü sürdürün.</p><a class="btn btn-secondary" href="${result.maintenanceRoute}">Bakım planına ekle</a>`;
      emit('smoke_alarm_no_purchase_rendered',{status:result.status});
    }else if(result.status==='emergency'){
      gate.className='decision-box professional';
      gate.innerHTML=`<span class="eyebrow">Acil güvenlik</span><h3>Ürün karşılaştırmasını bırakın</h3><p>Duman, alev veya aktif alarm varsa binayı terk edin, güvenli yerde 112’yi arayın ve içeri geri dönmeyin.</p><a class="btn btn-primary" href="${result.emergencyRoute}">112'yi ara</a>`;
      emit('smoke_alarm_emergency_rendered',{status:result.status});
    }else{
      gate.className='decision-box professional';
      gate.innerHTML=`<span class="eyebrow">Ticari rota kapalı</span><h3>Önce güvenlik, yerleşim veya belge eksikliğini çözün</h3><p>Bu sonuçta ürün bağlantısı göstermek yanlış güven duygusu oluşturabilir. Otel, işyeri ve bakım tesisinde profesyonel yangın algılama değerlendirmesi gerekir.</p><div class="gate-actions"><a class="btn btn-primary" href="${result.decisionRoute}">112 / uzman yönünü aç</a><a class="btn btn-secondary" href="${result.maintenanceRoute}">Bakım planını aç</a></div>`;
      emit('smoke_alarm_affiliate_blocked',{status:result.status,block_count:result.blocks.length,failure_count:result.failures.length,unknown_count:result.unknowns.length});
    }
  }

  function render(result){
    const section=$('results');
    section.className=`panel result-panel status-${result.status}`;
    $('resultStatus').textContent=result.headline;
    $('resultSummary').textContent=result.status==='suitable'?'Ev tipi düşük riskli ön seçimde adet, yerleşim ve ürün bilgileri karşılanıyor.':result.status==='no_purchase'?'Mevcut çalışan alarmlar görünür ihtiyacı karşılıyor.':'Satın alma veya montajdan önce aşağıdaki engel ve eksikleri giderin.';
    $('minimumMetric').textContent=`${result.minimumAlarms} adet`;
    $('totalMetric').textContent=`${result.totalAfterPlan} adet`;
    $('shortageMetric').textContent=`${result.shortage} adet`;
    $('coverageMetric').textContent=`%${result.coveragePercent}`;
    $('distanceMetric').textContent=`${result.cookingDistanceM.toLocaleString('tr-TR')} m`;
    $('ageMetric').textContent=`${result.alarmAgeYears.toLocaleString('tr-TR')} yıl`;
    $('resultDetails').innerHTML=[listMarkup('Acil veya profesyonel engeller',result.blocks,'danger'),listMarkup('Karşılanmayan koşullar',result.failures,'danger'),listMarkup('Yeniden doğrulanacak bilgiler',result.unknowns,'warning'),listMarkup('Dikkat notları',result.warnings,'warning'),listMarkup('Karşılanan koşullar',result.positives,'success')].join('');
    renderGate(result);
    section.classList.remove('hidden');
    section.focus();
    emit('smoke_alarm_suitability_completed',{status:result.status,use_case:result.useCase,ownership:result.ownership,product_route_allowed:result.productRouteAllowed,coverage_band:result.coveragePercent>=100?'full':result.coveragePercent>=50?'partial':'low'});
  }

  function submit(event){event.preventDefault();$('validation').textContent='';try{render(core.evaluate(formData()));}catch(error){$('validation').textContent=error.message;$('validation').focus();}}
  function reset(){
    $('smokeAlarmForm').reset();$('results').classList.add('hidden');$('commercialGate').classList.add('hidden');$('validation').textContent='';applyPreset('flat');$('arac').scrollIntoView({behavior:'smooth',block:'start'});
  }

  document.addEventListener('DOMContentLoaded',()=>{
    if(!core){$('validation').textContent='Hesap motoru yüklenemedi.';return;}
    document.querySelectorAll('[data-preset]').forEach(button=>button.addEventListener('click',()=>applyPreset(button.dataset.preset)));
    $('smokeAlarmForm').addEventListener('submit',submit);$('resetBtn').addEventListener('click',reset);applyPreset('flat');
  });
})();
