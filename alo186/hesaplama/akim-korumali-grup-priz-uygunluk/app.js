(() => {
  'use strict';
  const $=id=>document.getElementById(id);
  const core=window.Alo186SurgeStripSuitability;

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
      usbNeeded:$('usbNeeded').checked,
      usbPorts:$('usbPorts').value,
      groundStatus:$('groundStatus').value,
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

  function renderGate(result){
    const gate=$('commercialGate');
    gate.classList.remove('hidden');
    if(result.productRouteAllowed){
      gate.innerHTML=`<span class="eyebrow">Şeffaf ürün rotası</span><h3>Teknik minimumla ürünleri karşılaştırın</h3><p>ALO186 bazı dış ürün bağlantılarından satış ortaklığı komisyonu kazanabilir; kullanıcıya ek maliyet yansımaz. Fiyat, stok, satıcı, puan ve garanti bilgisi ALO186'te gösterilmez ve güncel satıcı sayfasında doğrulanır.</p><label class="check-item"><input type="checkbox" data-confirm-need><span><strong>Mevcut yeterli bir grup prizim yok.</strong><small>Çalışan ve yeterli ürün varsa yeni satın alma gerekmeyebilir.</small></span></label><label class="check-item"><input type="checkbox" data-confirm-affiliate><span><strong>Teknik etiketi ve satış ortaklığı niteliğini anladım.</strong><small>Akım, güç, priz sayısı, koruma göstergesi ve aşırı akım korumasını ürün sayfasında yeniden kontrol edeceğim.</small></span></label><a class="btn btn-primary disabled-link" data-product-route aria-disabled="true" tabindex="-1" href="${result.productRoute}" rel="nofollow">Akıllı Ürün Merkezi'ni aç</a>`;
      const checks=[...gate.querySelectorAll('input[type="checkbox"]')];
      const link=gate.querySelector('[data-product-route]');
      const sync=()=>{
        const enabled=checks.every(item=>item.checked);
        link.classList.toggle('disabled-link',!enabled);
        link.setAttribute('aria-disabled',enabled?'false':'true');
        link.tabIndex=enabled?0:-1;
      };
      checks.forEach(item=>item.addEventListener('change',sync));
      link.addEventListener('click',event=>{
        if(link.getAttribute('aria-disabled')==='true'){event.preventDefault();return;}
        emit('surge_strip_product_route_opened',{status:result.status,load_type:result.loadType});
      });
    }else if(result.noPurchase){
      gate.innerHTML=`<span class="eyebrow">Satın almama sonucu</span><h3>Mevcut ürününüzü kullanmaya devam edin</h3><p>Güvenlik koşulları ve teknik değerler değişmedikçe yeni ürün gerekmiyor. Koruma göstergesini, fiş/kablo sıcaklığını ve yükü düzenli kontrol edin.</p><a class="btn btn-secondary" href="/hesaplama/ekipman-bakim-plani/">Bakım planına ekle</a>`;
      emit('surge_strip_no_purchase_rendered',{status:result.status});
    }else{
      gate.innerHTML=`<span class="eyebrow">Ticari rota kapalı</span><h3>Önce güvenlik veya teknik eksikliği çözün</h3><p>Bu sonuçta ürün bağlantısı göstermek yanlış seçim veya yangın/elektrik çarpması riskini artırabilir.</p><div class="gate-actions"><a class="btn btn-primary" href="${result.safetyRoute}">Parafudr risk testini aç</a><a class="btn btn-secondary" href="${result.decisionRoute}">112 / 186 / elektrikçi kararını aç</a></div>`;
      emit('surge_strip_affiliate_blocked',{status:result.status,block_count:result.blocks.length,failure_count:result.failures.length,unknown_count:result.unknowns.length});
    }
  }

  function render(result){
    const section=$('results');
    section.className=`panel result-panel status-${result.status}`;
    $('resultStatus').textContent=result.headline;
    $('resultSummary').textContent=result.status==='suitable'?'Düşük riskli elektronik yük için görünür teknik ön koşullar karşılanıyor.':result.status==='no_purchase'?'Mevcut ürün yük ve özellik ihtiyacını karşılıyor.':'Satın alma kararından önce aşağıdaki engel ve eksikleri giderin.';
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
    section.classList.remove('hidden');
    section.focus();
    emit('surge_strip_suitability_completed',{status:result.status,load_type:result.loadType,ownership:result.ownership,product_route_allowed:result.productRouteAllowed,load_band:result.loadPercent<50?'low':result.loadPercent<80?'medium':'high'});
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
    $('validation').textContent='';
    applyPreset('office');
    $('arac').scrollIntoView({behavior:'smooth',block:'start'});
  }

  function escapeHtml(value){return String(value??'').replace(/[&<>"']/g,char=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));}

  document.addEventListener('DOMContentLoaded',()=>{
    if(!core){$('validation').textContent='Hesap motoru yüklenemedi.';return;}
    document.querySelectorAll('[data-preset]').forEach(button=>button.addEventListener('click',()=>applyPreset(button.dataset.preset)));
    $('surgeStripForm').addEventListener('submit',submit);
    $('resetBtn').addEventListener('click',reset);
    applyPreset('office');
  });
})();
