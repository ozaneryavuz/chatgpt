'use strict';

(function(){
  const api=window.Alo186EmergencyLightingSuitability;
  const form=document.getElementById('emergencyLightForm');
  const results=document.getElementById('results');
  const validation=document.getElementById('validation');
  const affiliateBox=document.getElementById('affiliateBox');
  const productLink=document.getElementById('productLink');
  const noPurchase=document.getElementById('noPurchase');
  const professional=document.getElementById('professional');
  const presets={
    room:{useCase:'home_room',areaM2:20,targetLux:20,lumensPerUnit:300,units:2,placement:'average',targetHours:6,declaredRuntimeHours:8},
    corridor:{useCase:'home_corridor',areaM2:12,targetLux:10,lumensPerUnit:150,units:2,placement:'average',targetHours:8,declaredRuntimeHours:10},
    outdoor:{useCase:'outdoor',areaM2:25,targetLux:10,lumensPerUnit:500,units:1,placement:'average',targetHours:5,declaredRuntimeHours:8},
    workplace:{useCase:'workplace_exit',areaM2:100,targetLux:10,lumensPerUnit:500,units:4,placement:'average',targetHours:3,declaredRuntimeHours:3}
  };

  const ids=['useCase','ownership','areaM2','targetLux','lumensPerUnit','units','placement','targetHours','declaredRuntimeHours','lumensVerified','runtimeVerified','physicalSwitch','chargeIndicator','handsFreeMount','autoOnRequired','autoOnSupported','weatherRated','damageFree','drySafeEnvironment','candlesPlanned'];
  const read=()=>Object.fromEntries(ids.map(id=>{const el=document.getElementById(id);return [id,el.type==='checkbox'?el.checked:el.value];}));
  const set=(id,value)=>{const el=document.getElementById(id);if(!el)return;if(el.type==='checkbox')el.checked=Boolean(value);else el.value=value;};
  const text=(id,value)=>{document.getElementById(id).textContent=value;};
  const list=(id,items,empty)=>{const el=document.getElementById(id);el.innerHTML='';(items.length?items:[empty]).forEach(item=>{const li=document.createElement('li');li.textContent=item;el.appendChild(li);});};
  const track=(name,detail={})=>{window.dispatchEvent(new CustomEvent('alo186:analytics',{detail:{name,...detail}}));};

  function applyPreset(name){
    const data=presets[name];
    if(!data)return;
    Object.entries(data).forEach(([id,value])=>set(id,value));
    ['lumensVerified','runtimeVerified','physicalSwitch','chargeIndicator','handsFreeMount','damageFree','drySafeEnvironment'].forEach(id=>set(id,true));
    set('weatherRated',name==='outdoor');
    set('autoOnRequired',false);
    set('autoOnSupported',false);
    set('candlesPlanned',false);
    validation.textContent='Hazır örnek yüklendi; ürün etiketini kendi değerlerinizle değiştirin.';
  }

  function render(result){
    const labels={compatible:'Teknik sınırlar içinde',conditional:'Koşullu — bilgileri doğrulayın',incompatible:'Uygun değil / güvenlik engeli',professional:'Profesyonel tasarım gerekli'};
    results.classList.remove('hidden');
    results.dataset.status=result.status;
    text('resultStatus',labels[result.status]);
    text('summary',result.noPurchaseNeeded?'Mevcut ürün yeterli; yeni satın alma gerekmiyor.':result.recommendedClass);
    text('luxMetric',`${result.approximateLux} lx`);
    text('unitsMetric',`${result.requiredUnits} adet`);
    text('runtimeMetric',`${result.input.declaredRuntimeHours} saat`);
    text('marginMetric',`${result.runtimeMarginHours>=0?'+':''}${result.runtimeMarginHours} saat`);
    text('factorMetric',result.factor.toFixed(2));
    list('blockers',result.blockers,'Engelleyici teknik veya güvenlik bulgusu yok.');
    list('warnings',result.warnings,'Ek doğrulama uyarısı yok.');
    list('checks',result.checks,'Kontrol önerisi yok.');

    affiliateBox.classList.toggle('hidden',!result.commercialAllowed);
    productLink.href='/akilli-urun-secimi?kategori=emergency_light';
    noPurchase.classList.toggle('hidden',!result.noPurchaseNeeded);
    professional.classList.toggle('hidden',!result.professionalRequired);
    track('emergency_light_suitability_rendered',{status:result.status,commercialAllowed:result.commercialAllowed,noPurchaseNeeded:result.noPurchaseNeeded,professionalRequired:result.professionalRequired});
    results.focus();
  }

  form.addEventListener('submit',event=>{
    event.preventDefault();
    validation.textContent='';
    try{render(api.analyze(read()));}
    catch(error){validation.textContent=error.message;validation.focus();}
  });

  document.querySelectorAll('[data-preset]').forEach(button=>button.addEventListener('click',()=>applyPreset(button.dataset.preset)));
  document.getElementById('resetBtn').addEventListener('click',()=>{form.reset();results.classList.add('hidden');affiliateBox.classList.add('hidden');noPurchase.classList.add('hidden');professional.classList.add('hidden');validation.textContent='';applyPreset('room');});
  productLink.addEventListener('click',()=>track('emergency_light_product_guide_opened',{category:'emergency_light'}));
  applyPreset('room');
})();
