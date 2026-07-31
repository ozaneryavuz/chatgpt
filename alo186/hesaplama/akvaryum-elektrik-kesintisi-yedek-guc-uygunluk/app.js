(() => {
  'use strict';
  const ROUTE='/hesaplama/akvaryum-elektrik-kesintisi-yedek-guc-uygunluk/';
  const PRODUCT_ROUTES={
    battery_air_pump:'/akilli-urun-secimi?intent=akvaryum-pilli-hava-motoru',
    ups:'/akilli-urun-secimi?intent=akvaryum-ups',
    power_station:'/amazon-elektrik-urunleri/tasinabilir-guc-istasyonu-secimi'
  };
  const n=(value)=>Number.isFinite(Number(value))?Math.max(0,Number(value)):0;
  const round10=(value)=>Math.ceil(value/10)*10;
  const round50=(value)=>Math.ceil(value/50)*50;
  const selectedLoad=(input)=>{
    const loads={
      air:n(input.airW),
      circulation:n(input.circulationW),
      filter:n(input.filterW),
      returnPump:n(input.returnPumpW),
      heater:n(input.heaterW),
      chiller:n(input.chillerW),
      lighting:n(input.lightingW),
      other:n(input.otherW)
    };
    let keys=['air'];
    if(input.backupPlan==='air_flow')keys=['air','circulation'];
    if(input.backupPlan==='bio_flow')keys=['air','circulation','filter','returnPump'];
    if(input.backupPlan==='full')keys=Object.keys(loads);
    return {loads,totalW:keys.reduce((sum,key)=>sum+loads[key],0),keys};
  };
  const calculate=(input)=>{
    const selected=selectedLoad(input);
    const targetHours=n(input.targetHours);
    const requiredW=round10(selected.totalW*1.25);
    const requiredVA=round50(requiredW/0.7);
    const requiredWh=round10((selected.totalW*targetHours)/0.85/0.8);
    return {...selected,targetHours,requiredW,requiredVA,requiredWh,thermalW:n(input.heaterW)+n(input.chillerW)};
  };
  const decide=(input)=>{
    const metrics=calculate(input);
    if(input.electricalEmergency)return {code:'electrical_emergency',level:'stop',title:'Önce elektrik ve su temas riskini güvenle ayırın',metrics,commerce:false};
    if(input.livestockDistress)return {code:'livestock_distress',level:'stop',title:'Canlılarda stres belirtisi varsa ürün seçimini bırakıp acil havalandırma ve uzman desteğine geçin',metrics,commerce:false};
    if(input.connection==='unsafe')return {code:'unsafe_connection',level:'stop',title:'Islak, yerde veya damlama döngüsü olmayan bağlantıyı düzeltmeden yedek güç kullanmayın',metrics,commerce:false};
    if(metrics.totalW<=0 || metrics.targetHours<=0)return {code:'missing_load',level:'warn',title:'Kritik yük ve hedef süreyi gerçek değerlerle girin',metrics,commerce:false};
    if(input.loadEvidence==='estimated')return {code:'evidence',level:'warn',title:'Tahmini değer yerine cihaz etiketi, teknik belge veya priz ölçümü kullanın',metrics,commerce:false};
    if(input.systemType==='reef' && input.backupPlan==='air_only')return {code:'reef_plan',level:'warn',title:'Resif sisteminde yalnız hava motorunu bütün yaşam desteği planı saymayın',metrics,commerce:false};
    if(input.backupPlan==='full' && metrics.thermalW>500)return {code:'thermal_load',level:'warn',title:'Isıtıcı veya soğutucu yükünü taşınabilir tüketici çözümüne zorlamayın',metrics,commerce:false};
    if(input.scenario==='active' && input.sourceStatus!=='existing')return {code:'active_outage',level:'warn',title:'Aktif kesintide yeni ürün teslimatını anlık çözüm saymayın',metrics,commerce:false};

    if(input.sourceStatus==='existing'){
      const enoughW=n(input.sourceW)>=metrics.requiredW;
      const enoughVA=n(input.sourceVA)>=metrics.requiredVA;
      const enoughWh=n(input.sourceWh)>=metrics.requiredWh;
      const compatible=input.waveform==='approved';
      const transferOk=input.continuity==='restart_ok' || input.transferTest==='success';
      const runtimeOk=input.runtimeTest==='success';
      if(enoughW && enoughVA && enoughWh && compatible && transferOk && runtimeOk){
        return {code:'no_buy',level:'good',title:'Mevcut kaynak yeterli — yeni ürün almayın',metrics,commerce:false};
      }
      if(input.runtimeTest==='failed')return {code:'runtime_fail',level:'warn',title:'Etiket kapasitesi yeterli görünse de gerçek süre testi başarısız',metrics,commerce:false};
      if(input.transferTest==='restart' && input.continuity==='no_restart')return {code:'transfer_fail',level:'warn',title:'Kesintide yeniden başlama hedefi karşılanmıyor',metrics,commerce:false};
    }

    let productClass='power_station';
    if(input.backupPlan==='air_only' && metrics.totalW<=25)productClass='battery_air_pump';
    else if(input.continuity==='no_restart')productClass='ups';
    const titles={
      battery_air_pump:'Önce düşük güçlü otomatik veya pilli havalandırma sınıfını karşılaştırın',
      ups:'Pompa ve havalandırmanın kesintide durmaması için UPS sınıfını karşılaştırın',
      power_station:'Uzun süreli kritik akış için yeterli W ve Wh değerine sahip güç istasyonu sınıfını karşılaştırın'
    };
    return {code:productClass,level:'warn',title:titles[productClass],metrics,commerce:input.scenario!=='active',productClass};
  };

  if(typeof module!=='undefined' && module.exports){module.exports={ROUTE,PRODUCT_ROUTES,selectedLoad,calculate,decide};return;}
  const $=(id)=>document.getElementById(id);
  const form=$('aquariumForm');
  const result=$('result');
  const sourceStatus=$('sourceStatus');
  const existingFields=$('existingFields');
  const getInput=()=>({
    electricalEmergency:$('electricalEmergency').checked,
    livestockDistress:$('livestockDistress').checked,
    scenario:$('scenario').value,
    systemType:$('systemType').value,
    backupPlan:$('backupPlan').value,
    continuity:$('continuity').value,
    connection:$('connection').value,
    airW:$('airW').value,circulationW:$('circulationW').value,filterW:$('filterW').value,
    returnPumpW:$('returnPumpW').value,heaterW:$('heaterW').value,chillerW:$('chillerW').value,
    lightingW:$('lightingW').value,otherW:$('otherW').value,targetHours:$('targetHours').value,
    loadEvidence:$('loadEvidence').value,sourceStatus:sourceStatus.value,
    sourceW:$('sourceW').value,sourceVA:$('sourceVA').value,sourceWh:$('sourceWh').value,
    waveform:$('waveform').value,transferTest:$('transferTest').value,runtimeTest:$('runtimeTest').value
  });
  const metric=(label,value,small='')=>`<div class="metric"><span>${label}</span><strong>${value}</strong><small>${small}</small></div>`;
  const explain=(code)=>({
    electrical_emergency:'Su ve elektrik aynı alandadır. Islak ekipmana yaklaşmayın; enerjiyi yalnız güvenli noktadan ayırın ve gerekirse 112 çağırın.',
    livestock_distress:'Yüzeyde soluma, ani davranış değişikliği veya hızlı sıcaklık değişiminde biyolojik risk ürün alışverişinden önce gelir. Havalandırma, su sıcaklığı ve su kalitesini izleyin; veteriner veya deneyimli akvaryum uzmanından destek alın.',
    unsafe_connection:'Yedek kaynak kuru, yüksek ve iyi havalandırılan yerde olmalı; kabloda damlama döngüsü ve uygun koruma düzeni bulunmalıdır.',
    missing_load:'Sıfır yük veya sıfır süre ile ürün boyutlandırılamaz.',
    evidence:'Model adına veya forum tahminine göre değil, gerçek giriş wattına göre hesap yapılmalıdır.',
    reef_plan:'Resif akvaryumunda dönüş pompası, sirkülasyon, ısı yönetimi ve canlı yükü birlikte değerlendirilir.',
    thermal_load:'Isıtıcı ve chiller enerji bütçesini hızla büyütür. Önce havalandırma ve akış gibi kritik yükleri ayırın; yüksek güçlü ısı yükü için profesyonel çözüm değerlendirin.',
    active_outage:'Henüz satın alınmamış ürün devam eden kesintide canlıları korumaz. Mevcut güvenli kaynak, manuel havalandırma ve uzman yönlendirmesi önceliklidir.',
    no_buy:'Güç, enerji, çıkış uyumu, transfer ve gerçek süre kanıtları birlikte yeterli.',
    runtime_fail:'Akü yaşı, sıcaklık, gerçek yük ve inverter kayıpları nedeniyle pratik süre etiket hesabından kısa olabilir.',
    transfer_fail:'Pompa veya hava motoru kesinti geçişinde duruyorsa kesintisizlik hedefi sağlanmıyor.',
    battery_air_pump:'Düşük güçlü yalnız havalandırma senaryosunda büyük bir AC kaynak yerine daha sade çözüm yeterli olabilir.',
    ups:'Kesintide pompa veya hava motorunun durmaması isteniyorsa gerçek transfer testi belirleyicidir.',
    power_station:'Uzun süre için nominal Wh yanında sürekli W, dalga biçimi ve gerçek yük testi doğrulanmalıdır.'
  }[code]||'Teknik kanıtları tamamlayın.');
  const render=(decision)=>{
    const m=decision.metrics;
    let extra='';
    if(decision.commerce){
      extra=`<div class="affiliate"><strong>Şeffaf satış ortaklığı kapısı</strong><p>Ürün sınıfı yalnız gerçek teknik açık bulunduğu için gösteriliyor. Sonraki dış mağaza bağlantılarından ALO186 komisyon kazanabilir; kullanıcıya ek maliyet yansımaz.</p><div class="checks">
        <label class="check"><input id="confirmGap" type="checkbox">Mevcut güvenli çözümün kritik yük ve hedef süreyi karşılamadığını doğruladım.</label>
        <label class="check"><input id="confirmSpecs" type="checkbox">W, VA, Wh, dalga biçimi, transfer ve suya karşı bağlantı düzenini tam modelde yeniden kontrol edeceğim.</label>
        <label class="check"><input id="confirmAffiliate" type="checkbox">Sonraki bağlantının satış ortaklığı bağlantısı olabileceğini anlıyorum.</label>
      </div><a id="productLink" class="button primary" href="${PRODUCT_ROUTES[decision.productClass]}" rel="sponsored nofollow noopener" aria-disabled="true">Uygun ürün sınıfını aç</a></div>`;
    }
    result.className=`panel result ${decision.level}`;
    result.innerHTML=`<h2>${decision.title}</h2><div class="metrics">
      ${metric('Kritik seçili yük',`${Math.round(m.totalW)} W`,m.keys.join(' + '))}
      ${metric('Sürekli güç alt sınırı',`${m.requiredW} W`,'%25 rezerv dahil')}
      ${metric('Yaklaşık UPS alt sınırı',`${m.requiredVA} VA`,'W sınırı ayrıca doğrulanır')}
      ${metric('Nominal enerji ihtiyacı',`${m.requiredWh} Wh`,`${m.targetHours} saat hedef`)}
    </div><div class="callout ${decision.level==='stop'?'danger':decision.level==='good'?'good':''}"><strong>Neden?</strong> ${explain(decision.code)}</div>${extra}
    <div class="actions"><button id="printBtn" class="button" type="button">Yazdır / PDF</button><button id="jsonBtn" class="button" type="button">Teknik sonucu JSON indir</button><button id="icsBtn" class="button" type="button">90 günlük test takvimi indir</button></div>`;
    result.classList.remove('hidden');result.focus();
    $('printBtn')?.addEventListener('click',()=>globalThis.print());
    $('jsonBtn')?.addEventListener('click',()=>downloadJson(decision));
    $('icsBtn')?.addEventListener('click',downloadIcs);
    ['confirmGap','confirmSpecs','confirmAffiliate'].forEach(id=>$(id)?.addEventListener('change',updateAffiliate));
  };
  const updateAffiliate=()=>{
    const link=$('productLink');if(!link)return;
    const enabled=['confirmGap','confirmSpecs','confirmAffiliate'].every(id=>$(id)?.checked);
    link.setAttribute('aria-disabled',String(!enabled));
  };
  const saveBlob=(content,type,name)=>{const blob=new Blob([content],{type});const url=URL.createObjectURL(blob);const a=document.createElement('a');a.href=url;a.download=name;a.click();URL.revokeObjectURL(url);};
  const downloadJson=(decision)=>saveBlob(JSON.stringify({schema:'alo186-aquarium-continuity-v1',route:ROUTE,createdAt:new Date().toISOString(),personalData:false,result:decision},null,2),'application/json','alo186-akvaryum-yedek-guc-sonucu.json');
  const pad=(v)=>String(v).padStart(2,'0');
  const stamp=(date)=>`${date.getUTCFullYear()}${pad(date.getUTCMonth()+1)}${pad(date.getUTCDate())}T${pad(date.getUTCHours())}${pad(date.getUTCMinutes())}00Z`;
  const downloadIcs=()=>{const start=new Date();start.setDate(start.getDate()+90);start.setHours(10,0,0,0);const end=new Date(start.getTime()+30*60*1000);const ics=`BEGIN:VCALENDAR\r\nVERSION:2.0\r\nPRODID:-//ALO186//Akvaryum Yedek Güç Testi//TR\r\nBEGIN:VEVENT\r\nUID:akvaryum-${Date.now()}@alo186.com\r\nDTSTAMP:${stamp(new Date())}\r\nDTSTART:${stamp(start)}\r\nDTEND:${stamp(end)}\r\nSUMMARY:Akvaryum yedek güç ve havalandırma testi\r\nDESCRIPTION:Hava motoru, pompa, akü, kablo, damlama döngüsü, transfer ve gerçek süre testini kontrollü biçimde doğrulayın. Canlılarda stres belirtisi varsa ürün testi yapmayın.\r\nEND:VEVENT\r\nEND:VCALENDAR\r\n`;saveBlob(ics,'text/calendar','alo186-akvaryum-90-gunluk-test.ics');};
  sourceStatus.addEventListener('change',()=>existingFields.classList.toggle('hidden',sourceStatus.value!=='existing'));
  form.addEventListener('submit',(event)=>{event.preventDefault();render(decide(getInput()));});
  form.addEventListener('reset',()=>setTimeout(()=>{existingFields.classList.add('hidden');result.className='panel result hidden';result.innerHTML='';},0));
})();
