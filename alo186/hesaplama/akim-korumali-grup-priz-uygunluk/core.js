(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  root.Alo186SurgeStripSuitability=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(){
  'use strict';

  const VOLTAGE=230;
  const STANDARD_CURRENTS=[6,10,16];
  const LOW_RISK_LOADS=new Set(['electronics','office','av','router']);
  const HARD_BLOCK_LOADS=new Set(['heater','medical','ev','fixed','major_appliance']);
  const RECALL_STATES=new Set(['checked_clear','unknown','recalled']);
  const INDICATOR_STATES=new Set(['verified','unknown','failed']);
  const TEST_STATES=new Set(['passed','not_done','failed']);

  function number(value,name,min,max){
    const parsed=Number(value);
    if(!Number.isFinite(parsed)||parsed<min||parsed>max)throw new Error(`${name} ${min}–${max} aralığında olmalıdır.`);
    return parsed;
  }

  function optionalNumber(value,min,max){
    if(value===null||value===undefined||value==='')return null;
    const parsed=Number(value);
    return Number.isFinite(parsed)&&parsed>=min&&parsed<=max?parsed:null;
  }

  function round(value,digits=1){
    const factor=10**digits;
    return Math.round(value*factor)/factor;
  }

  function nextStandardCurrent(value){
    return STANDARD_CURRENTS.find(item=>item>=value)||16;
  }

  function evaluate(input={}){
    const ownership=input.ownership==='owned'?'owned':'candidate';
    const loadType=String(input.loadType||'electronics');
    const continuousW=number(input.continuousW,'Toplam sürekli yük',1,5000);
    const peakW=number(input.peakW,'Tepe yük',continuousW,8000);
    const hoursDaily=number(input.hoursDaily,'Günlük kullanım',0.1,24);
    const requiredOutlets=number(input.requiredOutlets,'Gerekli priz sayısı',1,12);
    const productOutlets=number(input.productOutlets,'Ürün priz sayısı',1,16);
    const ratedCurrentA=number(input.ratedCurrentA,'Etiket akımı',1,16);
    const ratedPowerW=number(input.ratedPowerW,'Etiket gücü',100,4000);
    const joules=optionalNumber(input.joules,0,10000);
    const usbNeeded=Boolean(input.usbNeeded);
    const usbPorts=number(input.usbPorts??0,'USB portu',0,10);
    const groundStatus=['verified','unknown','absent'].includes(input.groundStatus)?input.groundStatus:'unknown';
    const recallStatus=RECALL_STATES.has(input.recallStatus)?input.recallStatus:'unknown';
    const indicatorState=INDICATOR_STATES.has(input.indicatorState)?input.indicatorState:'unknown';
    const supervisedTest=TEST_STATES.has(input.supervisedTest)?input.supervisedTest:'not_done';

    const labelVerified=Boolean(input.labelVerified);
    const overloadProtection=Boolean(input.overloadProtection);
    const protectionIndicator=Boolean(input.protectionIndicator);
    const damageFree=Boolean(input.damageFree);
    const dryIndoor=Boolean(input.dryIndoor);
    const directWall=Boolean(input.directWall);
    const uncovered=Boolean(input.uncovered);

    const currentA=continuousW/VOLTAGE;
    const peakA=peakW/VOLTAGE;
    const currentCapacityW=ratedCurrentA*VOLTAGE;
    const effectiveCapacityW=Math.min(currentCapacityW,ratedPowerW);
    const continuousUse=hoursDaily>=3;
    const screeningLimitW=effectiveCapacityW*(continuousUse?0.8:1);
    const requiredCurrentA=currentA/(continuousUse?0.8:1);
    const recommendedCurrentA=nextStandardCurrent(requiredCurrentA);
    const recommendedPowerW=Math.ceil((continuousW/(continuousUse?0.8:1))/50)*50;
    const loadRatio=continuousW/effectiveCapacityW;
    const screeningRatio=continuousW/screeningLimitW;

    const blocks=[];
    const failures=[];
    const unknowns=[];
    const warnings=[];
    const positives=[];

    if(HARD_BLOCK_LOADS.has(loadType)){
      const labels={heater:'Isıtıcı, kettle, ütü veya benzeri rezistif yük',medical:'Tıbbi veya yaşam destek cihazı',ev:'Elektrikli araç şarjı',fixed:'Sabit tesisat veya pano devresi',major_appliance:'Klima, çamaşır makinesi, bulaşık makinesi veya büyük beyaz eşya'};
      blocks.push(`${labels[loadType]} için tüketici tipi grup priz ürün rotası kapalıdır.`);
    }else if(!LOW_RISK_LOADS.has(loadType)){
      unknowns.push('Yük türü düşük riskli elektronik kategorisinde doğrulanamadı.');
    }

    if(recallStatus==='recalled')blocks.push('Tam marka-model için geri çağırma veya kullanımı durdurma duyurusu bulundu; ürünü kullanmayın ve ticari rotaya ilerlemeyin.');
    if(recallStatus==='unknown')unknowns.push('Tam marka-model için üretici ve resmî ürün güvenliği / geri çağırma kontrolü tamamlanmadı.');
    if(indicatorState==='failed')blocks.push('Darbe koruma göstergesi korumanın devre dışı olduğunu veya arızayı gösteriyor; ürünü korumalı kabul etmeyin.');
    if(indicatorState==='unknown')unknowns.push('Darbe koruma göstergesinin anlamı ve çalışır durumu üretici kılavuzundan doğrulanmadı.');
    if(ownership==='owned'&&supervisedTest==='failed')blocks.push('Gözetimli gerçek yük testinde ısınma, koku, gevşeklik, kıvılcım veya kesilme oluştu; kullanımı durdurun.');
    if(ownership==='owned'&&supervisedTest==='not_done')unknowns.push('Mevcut ürün için 30 dakikalık gözetimli gerçek yük ve fiş-priz sıcaklık kontrolü yapılmadı.');

    if(!directWall)blocks.push('Grup priz başka bir grup prize, çoklayıcıya veya uzatma kablosuna bağlanmamalıdır.');
    if(!dryIndoor)blocks.push('Ürün yalnız kuru ve üreticinin izin verdiği iç ortamda kullanılmalıdır.');
    if(!damageFree)blocks.push('Kararma, erime, çatlak, gevşeme, koku veya aşırı ısı bulunan ürün kullanılmamalıdır.');
    if(!uncovered)blocks.push('Kablo veya gövde halı, mobilya ya da ısıyı hapseden bir malzemeyle örtülmemelidir.');
    if(groundStatus==='absent')blocks.push('Koruma iletkeni bulunmayan prizde akım korumalı grup priz güvenli koruma katmanı sayılmaz.');
    if(groundStatus==='unknown')unknowns.push('Duvar prizinin koruma iletkeni ve tesisat durumu doğrulanmadı.');
    if(!labelVerified)unknowns.push('Akım, güç, model ve uygunluk işaretleri ürün etiketinden doğrulanmadı.');
    if(!overloadProtection)unknowns.push('Üründe aşırı akım/termik kesici veya eşdeğer koruma doğrulanmadı.');
    if(!protectionIndicator)unknowns.push('Darbe korumasının işlev durumunu gösteren ayrı gösterge doğrulanmadı.');
    if(joules===null||joules<=0)unknowns.push('Joule değeri bilinmiyor; bu değer yalnız karşılaştırma niteliğindedir, tek başına koruma garantisi değildir.');
    if(usbNeeded&&usbPorts<1)failures.push('USB çıkışı ihtiyacı ürün tarafından karşılanmıyor.');
    if(productOutlets<requiredOutlets)failures.push(`Ürün ${productOutlets} prizli; en az ${requiredOutlets} priz gerekiyor.`);
    if(continuousW>screeningLimitW)failures.push(`Sürekli yük ${continuousW} W; görünür güvenlik paylı ön kontrol sınırı yaklaşık ${Math.round(screeningLimitW)} W.`);
    if(peakW>effectiveCapacityW)failures.push(`Tepe yük ${peakW} W; ürünün etiket kapasitesi en fazla ${Math.round(effectiveCapacityW)} W.`);

    if(loadRatio>=0.8)warnings.push(`Etiket kapasitesinin yaklaşık %${Math.round(loadRatio*100)}'i kullanılıyor; bağlantı sıcaklığı ve gerçek etiket sınırı özellikle izlenmelidir.`);
    if(ratedPowerW>currentCapacityW+100)warnings.push(`Etiket gücü ${ratedPowerW} W, ${ratedCurrentA} A × 230 V hesabından yüksek görünüyor; ürün etiketi ve kılavuzu yeniden doğrulanmalıdır.`);
    if(joules!==null&&joules>0)warnings.push(`${joules} J değeri kaydedildi; joule tek başına pano tipi SPD, uygun topraklama, RCD veya ürün güvenliği yerine geçmez.`);

    if(continuousW<=screeningLimitW)positives.push(`Sürekli yük görünür ${continuousUse?'%80':'etiket'} ön kontrol sınırı içinde.`);
    if(peakW<=effectiveCapacityW)positives.push('Tepe yük etiket akım/güç sınırını aşmıyor.');
    if(productOutlets>=requiredOutlets)positives.push(`${productOutlets} priz, gereken ${requiredOutlets} bağlantıyı karşılıyor.`);
    if(groundStatus==='verified')positives.push('Koruma iletkeni durumu yetkili kontrol veya güvenilir kayıtla doğrulandı.');
    if(overloadProtection)positives.push('Aşırı akım/termik koruma özelliği doğrulandı.');
    if(recallStatus==='checked_clear')positives.push('Tam marka-model için güncel geri çağırma / ürün güvenliği kontrolünde kullanım durdurma kaydı bulunmadı.');
    if(indicatorState==='verified')positives.push('Darbe koruma göstergesinin anlamı ve çalışır durumu doğrulandı.');
    if(ownership==='owned'&&supervisedTest==='passed')positives.push('Mevcut ürün 30 dakikalık gözetimli gerçek yük testini ısınma veya bağlantı sorunu olmadan tamamladı.');

    let status='suitable';
    if(blocks.length)status='blocked';
    else if(failures.length)status='insufficient';
    else if(unknowns.length)status='conditional';
    else if(ownership==='owned')status='no_purchase';

    const productRouteAllowed=status==='suitable'&&ownership==='candidate'&&LOW_RISK_LOADS.has(loadType)&&recallStatus==='checked_clear'&&indicatorState==='verified';
    const noPurchase=status==='no_purchase';
    const headline={
      suitable:'Teknik ön koşullar karşılanıyor',
      conditional:'Eksik teknik veya ürün güvenliği kanıtı var',
      insufficient:'Ürün yükü veya bağlantı ihtiyacını karşılamıyor',
      blocked:'Güvenlik nedeniyle ürün yönlendirmesi kapalı',
      no_purchase:'Mevcut ürün yeterli; yeni satın alma gerekmiyor'
    }[status];

    return {
      status,headline,ownership,loadType,continuousW,peakW,hoursDaily,requiredOutlets,productOutlets,ratedCurrentA,ratedPowerW,joules,usbNeeded,usbPorts,
      groundStatus,recallStatus,indicatorState,supervisedTest,
      currentA:round(currentA,2),peakA:round(peakA,2),effectiveCapacityW:Math.round(effectiveCapacityW),screeningLimitW:Math.round(screeningLimitW),
      loadPercent:Math.round(loadRatio*100),screeningPercent:Math.round(screeningRatio*100),recommendedCurrentA,recommendedPowerW,
      productRouteAllowed,noPurchase,blocks,failures,unknowns,warnings,positives,
      productRequirements:{minOutlets:requiredOutlets,minJoules:Math.max(250,joules||250),usb:usbNeeded},
      reviewDays:90,
      reviewChecks:['Tam marka-model geri çağırma ve ürün güvenliği duyurusu','Darbe koruma göstergesinin çalışır durumu','Fiş, priz, kablo ve gövdede ısınma, kararma veya gevşeklik','Bağlı cihazların toplam W ve tepe yükü','Doğrudan duvar prizi ve topraklama koşulu'],
      productRoute:'/akilli-urun-secimi?kategori=surge_strip&gate=local',
      safetyRoute:'/hesaplama/parafudr-risk-testi/',
      decisionRoute:'/karar-motoru'
    };
  }

  return {evaluate,nextStandardCurrent,VOLTAGE};
});
