(() => {
  'use strict';
  const $=id=>document.getElementById(id);
  const core=window.Alo186SurgeStripSuitability;
  const qualificationKey='alo186_affiliate_qualification_v1';
  const qualificationTtlMs=30*60*1000;
  let lastResult=null;

  const presets={
    office:{loadType:'office',continuousW:650,peakW:900,hoursDaily:8,requiredOutlets:5,productOutlets:6,ratedCurrentA:16,ratedPowerW:3500,joules:900,usbNeeded:false,usbPorts:0},
    tv:{loadType:'av',continuousW:420,peakW:700,hoursDaily:5,requiredOutlets:5,productOutlets:5,ratedCurrentA:10,ratedPowerW:2300,joules:900,usbNeeded:false,usbPorts:0},
    router:{loadType:'router',continuousW:90,peakW:140,hoursDaily:24,requiredOutlets:4,productOutlets:5,ratedCurrentA:10,ratedPowerW:2300,joules:900,usbNeeded:true,usbPorts:2},
    heater:{loadType:'heater',continuousW:2000,peakW:2000,hoursDaily:4,requiredOutlets:1,productOutlets:5,ratedCurrentA:10,ratedPowerW:2300,joules:900,usbNeeded:false,usbPorts:0}
  };

  function emit(name,params={}){
    if(typeof window.Alo186Track==='function')window.Alo186Track(name,params);
  }

  function setValue(id,value){
    const element=$(id);
    if(!element)return;
    if(element.type==='checkbox')element.checked=Boolean(value);else element.value=String(value);
  }

  function applyPreset(name){
    const preset=presets[name];
    if(!preset)return;
    Object.entries(preset).forEach(([key,value])=>setValue(key,value));
    ['labelVerified','overloadProtection','protectionIndicator','damageFree','dryIndoor','directWall','uncovered'].forEach(id=>setValue(id,name!=='heater'));
    $('groundStatus').value=name==='heater'?'unknown':'verified';
    $('recallStatus').value=name==='heater'?'unknown':'checked_clear';
    $('indicatorState').value=name==='heater'?'unknown':'verified';
    $('supervisedTest').value='not_done';
    $('ownership').value='candidate';
    $('validation').textContent='';
    emit('surge_strip_preset_selected',{preset:name});
  }

  function formData(){
    return {
      ownership:$('ownership').value,
      loadType:$('loadType').value,
      continuousW:$('continuousW').value,
      peakW:$('peakW').value,
      hoursDaily:$('hoursDaily').value,
      requiredOutlets:$('requiredOutlets').value,
      productOutlets:$('productOutlets').value,
      ratedCurrentA:$('ratedCurrentA').value,
      ratedPowerW:$('ratedPowerW').value,
      joules:$('joules').value,
      usbNeeded:$('usbNeeded').value==='true',
      usbPorts:$('usbPorts').value,
      groundStatus:$('groundStatus').value,
      recallStatus:$('recallStatus').value,
      indicatorState:$('indicatorState').value,
      supervisedTest:$('supervisedTest').value,
      labelVerified:$('labelVerified').checked,
      overloadProtection:$('overloadProtection').checked,
      protectionIndicator:$('protectionIndicator').checked,
      damageFree:$('damageFree').checked,
      dryIndoor:$('dryIndoor').checked,
      directWall:$('directWall').checked,
      uncovered:$('uncovered').checked
    };
  }

  function listMarkup(title,items,className=''){
    if(!items.length)return '';
    return `<section class="result-list ${className}"><h3>${escapeHtml(title)}</h3><ul>${items.map(item=>`<li>${escapeHtml(item)}</li>`).join('')}</ul></section>`;
  }

  function saveQualification(result){
    const now=Date.now();
    const receipt={
      schema:'alo186.affiliateQualification.v1',
      category:'surge_strip',
      issuedAt:new Date(now).toISOString(),
      expiresAt:new Date(now+qualificationTtlMs).toISOString(),
      reviewAt:new Date(now+result.reviewDays*86400000).toISOString(),
      personalData:false,
      sourceTool:'surge_strip_suitability_v2',
      requirements:result.productRequirements
    };
    localStorage.setItem(qualificationKey,JSON.stringify(receipt));
    return receipt;
  }

  function renderGate(result){
    const gate=$('commercialGate');
    gate.classList.remove('hidden');
    if(result.productRouteAllowed){
      gate.innerHTML=`<span class="eyebrow">Şeffaf ve teknik kapılı ürün rotası</span><h3>Yalnız gerçek eksik için teknik minimumla karşılaştırın</h3><p>ALO186 ürün satıcısı veya uygunluk kuruluşu değildir. Akıllı Ürün Merkezi'ndeki bazı dış bağlantılar Amazon satış ortaklığı bağlantılarıdır; nitelikli satın alımlardan komisyon kazanılabilir ve kullanıcıya ek maliyet yansımaz. Fiyat, stok, satıcı, puan, teslimat ve garanti ALO186'te yayımlanmaz.</p><label class="check-item"><input type="checkbox" data-confirm-need><span><strong>Mevcut güvenli ve yeterli bir grup prizim yok.</strong><small>Çalışan ve bütün teknik eşikleri karşılayan mevcut ürün varsa yeni satın alma gerekmeyebilir.</small></span></label><label class="check-item"><input type="checkbox" data-confirm-technical><span><strong>Etiket, topraklama, geri çağırma ve koruma göstergesini yeniden kontrol edeceğim.</strong><small>W, A, priz sayısı, joule, aşırı akım koruması ve tam model ürün güvenliği kaydı satıcı sayfasında yeniden doğrulanmalıdır.</small></span></label><label class="check-item"><input type="checkbox" data-confirm-affiliate><span><strong>Sonraki bazı bağlantıların Amazon satış ortaklığı bağlantısı olduğunu anladım.</strong><small>Komisyon, teknik uygunluk veya ürün güvenliği onayı anlamına gelmez.</small></span></label><a class="btn btn-primary disabled-link" data-product-route aria-disabled="true" tabindex="-1" href="${result.productRoute}" rel="sponsored nofollow noopener">Akıllı Ürün Merkezi'ni aç</a><p class="small" data-gate-status>Teknik geçiş yalnız bu tarayıcıda 30 dakika geçerlidir; ad, adres, iletişim, fiyat veya ürün seri numarası kaydedilmez.</p>`;
      const checks=[...gate.querySelectorAll('input[type="checkbox"]')];
      const link=gate.querySelector('[data-product-route]');
      const status=gate.querySelector('[data-gate-status]');
      const sync=()=>{
        const enabled=checks.every(item=>item.checked);
        link.classList.toggle('disabled-link',!enabled);
        link.setAttribute('aria-disabled',enabled?'false':'true');
        link.tabIndex=enabled?0:-1;
      };
      checks.forEach(item=>item.addEventListener('change',sync));
      link.addEventListener('click',event=>{
        if(link.getAttribute('aria-disabled')==='true'){event.preventDefault();return;}
        try{
          saveQualification(result);
          status.textContent='Kişisel verisiz teknik geçiş 30 dakika için oluşturuldu. Teknik minimumları ürün merkezinde düşürmeden karşılaştırın.';
          emit('surge_strip_product_route_opened',{status:result.status,load_type:result.loadType,gate_ttl_minutes:30,confirmation_count:3});
        }catch(_error){
          event.preventDefault();
          status.textContent='Tarayıcı teknik geçiş kaydını oluşturamadı. Ürün rotası güvenlik nedeniyle açılmadı.';
          emit('surge_strip_affiliate_blocked',{status:result.status,reason:'local_gate_storage_failed'});
        }
      });
    }else if(result.noPurchase){
      gate.innerHTML=`<span class="eyebrow">Satın almama sonucu</span><h3>Mevcut ürününüzü kullanmaya devam edin</h3><p>Yük, etiket, topraklama, fiziksel durum, geri çağırma, koruma göstergesi ve gözetimli gerçek yük testi karşılanıyor. Koşullar değişmedikçe yeni ürün aramayın; 90 günlük teknik kontrolü takviminize ekleyin.</p><a class="btn btn-secondary" href="/hesaplama/ekipman-bakim-plani/">Bakım planına ekle</a>`;
      emit('surge_strip_no_purchase_rendered',{status:result.status});
    }else{
      try{localStorage.removeItem(qualificationKey);}catch(_error){}
      gate.innerHTML=`<span class="eyebrow">Ticari rota kapalı</span><h3>Önce güvenlik veya teknik kanıt eksikliğini çözün</h3><p>Bu sonuçta ürün bağlantısı göstermek yanlış seçim, yangın veya elektrik çarpması riskini artırabilir. Geri çağrılmış, koruma göstergesi arızalı veya gerçek testte sorun çıkaran ürünü kullanmayın.</p><div class="gate-actions"><a class="btn btn-primary" href="${result.safetyRoute}">Parafudr risk testini aç</a><a class="btn btn-secondary" href="${result.decisionRoute}">112 / 186 / elektrikçi kararını aç</a></div>`;
      emit('surge_strip_affiliate_blocked',{status:result.status,block_count:result.blocks.length,failure_count:result.failures.length,unknown_count:result.unknowns.length});
    }
  }

  function render(result){
    lastResult=result;
    const section=$('results');
    section.className=`panel result-panel status-${result.status}`;
    $('resultStatus').textContent=result.headline;
    $('resultSummary').textContent=result.status==='suitable'?'Düşük riskli elektronik yük için görünür teknik ve ürün güvenliği ön koşulları karşılanıyor.':result.status==='no_purchase'?'Mevcut ürün yükü, güvenlik kanıtlarını ve gerçek test ihtiyacını karşılıyor.':'Satın alma kararından önce aşağıdaki engel ve eksikleri giderin.';
    $('currentMetric').textContent=`${result.currentA.toLocaleString('tr-TR')} A`;
    $('peakMetric').textContent=`${result.peakA.toLocaleString('tr-TR')} A`;
    $('capacityMetric').textContent=`${result.effectiveCapacityW.toLocaleString('tr-TR')} W`;
    $('screeningMetric').textContent=`${result.screeningLimitW.toLocaleString('tr-TR')} W`;
    $('loadMetric').textContent=`%${result.loadPercent}`;
    $('minimumMetric').textContent=`${result.recommendedCurrentA} A / ${result.recommendedPowerW.toLocaleString('tr-TR')} W+`;
    $('resultDetails').innerHTML=[
      listMarkup('Güvenlik engelleri',result.blocks,'danger'),
      listMarkup('Karşılanmayan teknik koşullar',result.failures,'danger'),
      listMarkup('Yeniden doğrulanacak bilgiler',result.unknowns,'warning'),
      listMarkup('Dikkat notları',result.warnings,'warning'),
      listMarkup('Karşılanan koşullar',result.positives,'success')
    ].join('');
    renderGate(result);
    $('resultTools').classList.remove('hidden');
    section.classList.remove('hidden');
    section.focus();
    emit('surge_strip_suitability_completed',{status:result.status,load_type:result.loadType,ownership:result.ownership,product_route_allowed:result.productRouteAllowed,recall_status:result.recallStatus,indicator_state:result.indicatorState,load_band:result.loadPercent<50?'low':result.loadPercent<80?'medium':'high'});
  }

  function submit(event){
    event.preventDefault();
    $('validation').textContent='';
    try{render(core.evaluate(formData()));}
    catch(error){
      $('validation').textContent=error.message;
      $('validation').focus();
    }
  }

  function reset(){
    $('surgeStripForm').reset();
    $('results').classList.add('hidden');
    $('commercialGate').classList.add('hidden');
    $('resultTools').classList.add('hidden');
    $('validation').textContent='';
    lastResult=null;
    try{localStorage.removeItem(qualificationKey);}catch(_error){}
    applyPreset('office');
    $('arac').scrollIntoView({behavior:'smooth',block:'start'});
  }

  function downloadBlob(filename,type,content){
    const blob=new Blob([content],{type});
    const url=URL.createObjectURL(blob);
    const link=document.createElement('a');
    link.href=url;
    link.download=filename;
    document.body.appendChild(link);
    link.click();
    link.remove();
    setTimeout(()=>URL.revokeObjectURL(url),0);
  }

  function decisionReceipt(result){
    const generatedAt=new Date();
    const reviewAt=new Date(generatedAt.getTime()+result.reviewDays*86400000);
    return {
      schema:'alo186.surgeStripDecision.v2',
      generatedAt:generatedAt.toISOString(),
      reviewAt:reviewAt.toISOString(),
      personalData:false,
      source:'https://alo186.com/hesaplama/akim-korumali-grup-priz-uygunluk/',
      status:result.status,
      headline:result.headline,
      load:{type:result.loadType,continuousW:result.continuousW,peakW:result.peakW,hoursDaily:result.hoursDaily,requiredOutlets:result.requiredOutlets},
      product:{ownership:result.ownership,outlets:result.productOutlets,ratedCurrentA:result.ratedCurrentA,ratedPowerW:result.ratedPowerW,joules:result.joules,recallStatus:result.recallStatus,indicatorState:result.indicatorState,supervisedTest:result.supervisedTest},
      metrics:{currentA:result.currentA,peakA:result.peakA,effectiveCapacityW:result.effectiveCapacityW,screeningLimitW:result.screeningLimitW,loadPercent:result.loadPercent,recommendedCurrentA:result.recommendedCurrentA,recommendedPowerW:result.recommendedPowerW},
      decision:{productRouteAllowed:result.productRouteAllowed,noPurchase:result.noPurchase,blocks:result.blocks,failures:result.failures,unknowns:result.unknowns,warnings:result.warnings,positives:result.positives},
      reviewChecks:result.reviewChecks,
      commercialData:{price:false,stock:false,rating:false,seller:false,warranty:false}
    };
  }

  function downloadJson(){
    if(!lastResult)return;
    downloadBlob('alo186-akim-korumali-grup-priz-teknik-fis.json','application/json;charset=utf-8',JSON.stringify(decisionReceipt(lastResult),null,2));
    emit('surge_strip_json_downloaded',{status:lastResult.status,personal_data:false});
  }

  function icsEscape(value){return String(value).replace(/\\/g,'\\\\').replace(/;/g,'\\;').replace(/,/g,'\\,').replace(/\n/g,'\\n');}
  function dateStamp(date){return date.toISOString().slice(0,10).replace(/-/g,'');}

  function downloadCalendar(){
    if(!lastResult)return;
    const start=new Date(Date.now()+lastResult.reviewDays*86400000);
    const description=`Akım korumalı grup priz için teknik yeniden kontrol:\n- ${lastResult.reviewChecks.join('\n- ')}\nFiyat veya kampanya takibi değildir. ALO186 bağımsız bilgi platformudur.`;
    const ics=['BEGIN:VCALENDAR','VERSION:2.0','PRODID:-//ALO186//Surge Strip Review//TR','CALSCALE:GREGORIAN','BEGIN:VEVENT',`UID:alo186-surge-strip-${Date.now()}@alo186.com`,`DTSTAMP:${new Date().toISOString().replace(/[-:]/g,'').replace(/\.\d{3}Z$/,'Z')}`,`DTSTART;VALUE=DATE:${dateStamp(start)}`,'DURATION:P1D',`SUMMARY:${icsEscape('Akım korumalı grup priz teknik kontrolü')}`,`DESCRIPTION:${icsEscape(description)}`,'URL:https://alo186.com/hesaplama/akim-korumali-grup-priz-uygunluk/','END:VEVENT','END:VCALENDAR'].join('\r\n');
    downloadBlob('alo186-grup-priz-90-gun-kontrol.ics','text/calendar;charset=utf-8',ics);
    emit('surge_strip_calendar_downloaded',{status:lastResult.status,review_days:lastResult.reviewDays,personal_data:false});
  }

  function escapeHtml(value){return String(value??'').replace(/[&<>"']/g,char=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));}

  document.addEventListener('DOMContentLoaded',()=>{
    if(!core){$('validation').textContent='Hesap motoru yüklenemedi.';return;}
    document.querySelectorAll('[data-preset]').forEach(button=>button.addEventListener('click',()=>applyPreset(button.dataset.preset)));
    $('surgeStripForm').addEventListener('submit',submit);
    $('resetBtn').addEventListener('click',reset);
    $('downloadJsonBtn').addEventListener('click',downloadJson);
    $('calendarBtn').addEventListener('click',downloadCalendar);
    $('printBtn').addEventListener('click',()=>window.print());
    applyPreset('office');
  });
})();
