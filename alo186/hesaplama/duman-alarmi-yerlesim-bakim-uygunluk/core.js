(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  root.Alo186SmokeAlarmSuitability=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(){
  'use strict';

  const HOME_USE_CASES=new Set(['home','rental','short_term']);
  const PROFESSIONAL_USE_CASES=new Set(['hotel','workplace','care']);
  const COOKING_MIN_DISTANCE_M=3.05;
  const MAX_SERVICE_AGE_YEARS=10;

  function number(value,name,min,max){
    const parsed=Number(value);
    if(!Number.isFinite(parsed)||parsed<min||parsed>max)throw new Error(`${name} ${min}–${max} aralığında olmalıdır.`);
    return parsed;
  }

  function integer(value,name,min,max){
    const parsed=number(value,name,min,max);
    if(!Number.isInteger(parsed))throw new Error(`${name} tam sayı olmalıdır.`);
    return parsed;
  }

  function round(value,digits=1){
    const factor=10**digits;
    return Math.round(value*factor)/factor;
  }

  function minimumAlarmCount({floors,basement,bedrooms,sleepingAreas,sleepingLevels}){
    const totalLevels=floors+(basement?1:0);
    const validatedSleepingLevels=Math.min(Math.max(sleepingLevels,1),totalLevels);
    const extraLevelCoverage=Math.max(0,totalLevels-validatedSleepingLevels);
    return {
      totalLevels,
      extraLevelCoverage,
      count:bedrooms+sleepingAreas+extraLevelCoverage
    };
  }

  function evaluate(input={}){
    const useCase=String(input.useCase||'home');
    const ownership=input.ownership==='owned'?'owned':'candidate';
    const floors=integer(input.floors,'Kat sayısı',1,10);
    const basement=Boolean(input.basement);
    const bedrooms=integer(input.bedrooms,'Uyuma odası sayısı',0,30);
    const sleepingAreas=integer(input.sleepingAreas,'Ayrı uyuma alanı sayısı',1,20);
    const totalLevels=floors+(basement?1:0);
    const sleepingLevels=integer(input.sleepingLevels,'Uyuma alanı bulunan kat sayısı',1,totalLevels);
    const existingWorking=integer(input.existingWorking,'Çalışır mevcut alarm sayısı',0,80);
    const plannedNew=integer(input.plannedNew,'Planlanan yeni alarm sayısı',0,80);
    const cookingDistanceM=number(input.cookingDistanceM,'Pişirme cihazına uzaklık',0,50);
    const alarmAgeYears=number(input.alarmAgeYears,'Değerlendirilen alarm yaşı',0,30);
    const interconnect=String(input.interconnect||'unknown');

    const certificationVerified=Boolean(input.certificationVerified);
    const exactModelVerified=Boolean(input.exactModelVerified);
    const testButton=Boolean(input.testButton);
    const lowBatteryWarning=Boolean(input.lowBatteryWarning);
    const manufactureDateKnown=Boolean(input.manufactureDateKnown);
    const monthlyTestPassed=Boolean(input.monthlyTestPassed);
    const placementVerified=Boolean(input.placementVerified);
    const notDisabled=Boolean(input.notDisabled);
    const damageFree=Boolean(input.damageFree);
    const accessibilityRequired=Boolean(input.accessibilityRequired);
    const accessibilitySupported=Boolean(input.accessibilitySupported);
    const activeEmergency=Boolean(input.activeEmergency);

    const minimum=minimumAlarmCount({floors,basement,bedrooms,sleepingAreas,sleepingLevels});
    const totalAfterPlan=existingWorking+plannedNew;
    const shortage=Math.max(0,minimum.count-totalAfterPlan);
    const purchaseNeed=Math.max(0,minimum.count-existingWorking);
    const coveragePercent=minimum.count?Math.min(100,Math.round(totalAfterPlan/minimum.count*100)):100;

    const blocks=[];
    const failures=[];
    const unknowns=[];
    const warnings=[];
    const positives=[];

    if(activeEmergency)blocks.push('Duman, alev veya alarm sesi varsa ürün karşılaştırması yapmayın; binayı terk edin, güvenli yerde 112’yi arayın ve geri dönmeyin.');
    if(PROFESSIONAL_USE_CASES.has(useCase))blocks.push('Otel, işyeri, ortak alan veya bakım tesisinde tekil tüketici alarmı seçimi profesyonel yangın algılama projesinin yerine geçmez.');
    if(!HOME_USE_CASES.has(useCase)&&!PROFESSIONAL_USE_CASES.has(useCase))unknowns.push('Kullanım türü ev tipi düşük riskli senaryoda doğrulanamadı.');
    if(!notDisabled)blocks.push('Pili çıkarılmış, susturulmuş, boyanmış veya devre dışı bırakılmış alarm güvenli kabul edilmez.');
    if(!damageFree)blocks.push('Çatlak, ısı, sıvı, boya, yoğun kir veya fiziksel hasar bulunan alarm kullanılmamalıdır.');
    if(alarmAgeYears>=MAX_SERVICE_AGE_YEARS)failures.push(`Değerlendirilen alarm ${round(alarmAgeYears,1)} yaşında; genel güvenlik rehberlerinde 10 yaşındaki alarmın tamamen değiştirilmesi önerilir.`);
    if(ownership==='owned'&&!monthlyTestPassed)failures.push('Mevcut alarm aylık test düğmesi kontrolünü geçmiyor veya test sonucu bilinmiyor.');
    if(!testButton)failures.push('Test düğmesi doğrulanmadı.');
    if(!lowBatteryWarning)unknowns.push('Düşük pil veya ömür sonu uyarısı doğrulanmadı.');
    if(!manufactureDateKnown)unknowns.push('Üretim tarihi veya değişim tarihi doğrulanmadı; 10 yıllık ürün ömrü izlenemez.');
    if(!exactModelVerified)unknowns.push('Tam marka ve model kodu doğrulanmadı.');
    if(!certificationVerified)unknowns.push('EN 14604 veya satış pazarında geçerli uygunluk/performans belgesi tam model için doğrulanmadı.');
    if(!placementVerified)unknowns.push('Tavan veya yüksek duvar yerleşimi üretici kılavuzuna göre doğrulanmadı.');
    if(cookingDistanceM<COOKING_MIN_DISTANCE_M)failures.push(`Alarm pişirme cihazına ${round(cookingDistanceM,1)} m uzakta; gereksiz alarm riskini azaltmak için resmî ev güvenliği rehberlerinde yaklaşık 3 m uzaklık önerilir.`);
    if(accessibilityRequired&&!accessibilitySupported)failures.push('İşitme güçlüğü bulunan kullanıcı için flaş, titreşim veya uyandırma aksesuarı ihtiyacı karşılanmıyor.');
    if(shortage>0)failures.push(`Plan sonrası ${totalAfterPlan} alarm var; bu görünür yerleşim varsayımında en az ${minimum.count} alarm gerekiyor. ${shortage} adet eksik.`);

    if(minimum.count>1&&interconnect==='no')unknowns.push('Birden fazla alarm için birbirine bağlı çalışma desteği yok; bir alarm çaldığında diğerlerinin de çalması tercih edilmelidir.');
    if(minimum.count>1&&interconnect==='unknown')unknowns.push('Birbirine bağlı çalışma özelliği doğrulanmadı.');
    if(interconnect==='yes')positives.push('Bir alarm çaldığında diğerlerinin de çalmasını sağlayan bağlantı özelliği doğrulandı.');

    if(shortage===0)positives.push(`Planlanan toplam ${totalAfterPlan} alarm, yaklaşık ${minimum.count} adetlik yerleşim ihtiyacını karşılıyor.`);
    if(cookingDistanceM>=COOKING_MIN_DISTANCE_M)positives.push(`Pişirme cihazına uzaklık yaklaşık ${round(cookingDistanceM,1)} m ve 3 m ön kontrol sınırının üzerinde.`);
    if(testButton)positives.push('Test düğmesi var.');
    if(monthlyTestPassed&&ownership==='owned')positives.push('Mevcut alarm aylık test düğmesi kontrolünü geçti.');
    if(manufactureDateKnown&&alarmAgeYears<MAX_SERVICE_AGE_YEARS)positives.push(`Alarm yaşı ${round(alarmAgeYears,1)} yıl ve 10 yıllık genel değişim eşiğinin altında.`);
    if(certificationVerified&&exactModelVerified)positives.push('Tam model ve uygunluk/performans belgesi kullanıcı tarafından doğrulandı.');
    if(accessibilityRequired&&accessibilitySupported)positives.push('İşitme güçlüğü için görsel veya titreşimli uyarı desteği doğrulandı.');

    warnings.push(`Yaklaşık adet hesabı: ${bedrooms} uyuma odası + ${sleepingAreas} ayrı uyuma alanı dışı + ${minimum.extraLevelCoverage} ek kat alarmı.`);
    warnings.push('Bu araç yerel yangın mevzuatı, bina projesi, montaj kılavuzu veya itfaiye değerlendirmesi değildir.');
    if(ownership==='candidate'&&purchaseNeed===0)warnings.push('Çalışır mevcut alarm sayısı görünür ihtiyacı karşılıyor; yeni ürün yerine test ve bakım planı daha uygun olabilir.');

    let status='suitable';
    if(blocks.length)status=activeEmergency?'emergency':'professional';
    else if(failures.length)status='insufficient';
    else if(unknowns.length)status='conditional';
    else if((ownership==='owned'||purchaseNeed===0)&&existingWorking>=minimum.count)status='no_purchase';

    const productRouteAllowed=status==='suitable'&&ownership==='candidate'&&purchaseNeed>0&&HOME_USE_CASES.has(useCase);
    const noPurchase=status==='no_purchase';
    const headline={
      suitable:'Yerleşim ve ürün ön koşulları karşılanıyor',
      conditional:'Eksik ürün veya yerleşim bilgisi var',
      insufficient:'Alarm adedi, konumu veya özelliği yetersiz',
      professional:'Profesyonel yangın algılama değerlendirmesi gerekli',
      emergency:'Acil durumda tahliye ve 112 önceliklidir',
      no_purchase:'Mevcut çalışan alarmlar yeterli; yeni satın alma gerekmiyor'
    }[status];

    return {
      status,headline,useCase,ownership,floors,basement,bedrooms,sleepingAreas,sleepingLevels,
      totalLevels:minimum.totalLevels,minimumAlarms:minimum.count,extraLevelCoverage:minimum.extraLevelCoverage,
      existingWorking,plannedNew,totalAfterPlan,shortage,purchaseNeed,coveragePercent,cookingDistanceM:round(cookingDistanceM,1),alarmAgeYears:round(alarmAgeYears,1),
      productRouteAllowed,noPurchase,blocks,failures,unknowns,warnings,positives,
      productRoute:'/akilli-urun-secimi?kategori=smoke_alarm',
      maintenanceRoute:'/hesaplama/ekipman-bakim-plani/',
      decisionRoute:'/karar-motoru',
      emergencyRoute:'tel:112'
    };
  }

  return {evaluate,minimumAlarmCount,COOKING_MIN_DISTANCE_M,MAX_SERVICE_AGE_YEARS};
});
