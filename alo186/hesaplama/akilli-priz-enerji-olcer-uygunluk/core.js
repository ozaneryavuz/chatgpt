(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports){module.exports=api;}
  root.Alo186SmartPlugMeter=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(){
  'use strict';
  const VOLTAGE=230;
  const number=(value,name,min,max,optional=false)=>{
    if(optional&&(value===''||value==null))return null;
    const parsed=Number(value);
    if(!Number.isFinite(parsed)||parsed<min||parsed>max)throw new Error(`${name} ${min}–${max} aralığında olmalıdır.`);
    return parsed;
  };
  const enumValue=(value,allowed,fallback)=>allowed.includes(value)?value:fallback;
  const bool=value=>value===true||value==='true'||value===1||value==='1';
  const round=(value,digits=2)=>Number(value.toFixed(digits));

  function recommendedClass(input){
    if(['fixed','ev','multiple','medical'].includes(input.loadType))return 'Pano tipi enerji analizörü / profesyonel ölçüm';
    if(['remote','schedule'].includes(input.goal))return 'Enerji izlemeli akıllı priz';
    if(input.goal==='history')return 'Uzun dönem kayıt sunan enerji izlemeli akıllı priz';
    return 'Priz tipi enerji ölçer';
  }

  function analyze(raw){
    const input={
      loadType:enumValue(raw.loadType,['electronics','lighting','resistive','motor','compressor','multiple','medical','ev','fixed'],'electronics'),
      goal:enumValue(raw.goal,['measure','standby','remote','schedule','history'],'measure'),
      ownership:enumValue(raw.ownership,['candidate','owned'],'candidate'),
      meterType:enumValue(raw.meterType,['plug_meter','smart_plug'],'plug_meter'),
      loadPowerW:number(raw.loadPowerW,'Cihaz gücü',1,10000),
      powerFactor:number(raw.powerFactor,'Güç faktörü',0.2,1),
      startupPowerW:number(raw.startupPowerW,'Kalkış/tepe gücü',1,30000),
      dailyHours:number(raw.dailyHours,'Günlük çalışma süresi',0.1,24),
      standbyPowerW:number(raw.standbyPowerW,'Beklenen standby gücü',0,1000,true),
      desiredHistoryDays:number(raw.desiredHistoryDays,'İstenen kayıt süresi',0,3650,true),
      candidateCurrentA:number(raw.candidateCurrentA,'Ürün etiket akımı',1,32),
      candidatePowerW:number(raw.candidatePowerW,'Ürün etiket gücü',100,7360),
      candidateMinMeasureW:number(raw.candidateMinMeasureW,'Asgari gösterim gücü',0.01,100,true),
      candidateHistoryDays:number(raw.candidateHistoryDays,'Ürünün kayıt süresi',0,3650,true),
      energyMonitoring:bool(raw.energyMonitoring),
      remoteSwitching:bool(raw.remoteSwitching),
      scheduleSupport:bool(raw.scheduleSupport),
      labelVerified:bool(raw.labelVerified),
      manufacturerLoadApproved:bool(raw.manufacturerLoadApproved),
      damageFree:bool(raw.damageFree),
      directWallSocket:bool(raw.directWallSocket),
      indoorDry:bool(raw.indoorDry),
      earthContinuity:bool(raw.earthContinuity),
      needsEarth:bool(raw.needsEarth),
      unattendedUse:bool(raw.unattendedUse)
    };

    const currentA=input.loadPowerW/(VOLTAGE*input.powerFactor);
    const startupCurrentA=input.startupPowerW/(VOLTAGE*input.powerFactor);
    const longRun=input.dailyHours>=2;
    const currentLimitA=input.candidateCurrentA*(longRun?0.8:1);
    const powerLimitW=Math.min(input.candidatePowerW,VOLTAGE*input.candidateCurrentA)*(longRun?0.8:1);
    const dailyKwh=input.loadPowerW*input.dailyHours/1000;
    const annualKwh=dailyKwh*365;
    const blockers=[], blockerCodes=[], warnings=[], checks=[];
    const block=(code,text)=>{blockerCodes.push(code);blockers.push(text);};

    if(input.loadType==='medical')block('medical','Tıbbi veya yaşam destek cihazlarında genel akıllı priz/enerji ölçer yönlendirmesi yapılmaz.');
    if(input.loadType==='ev')block('ev','Elektrikli araç şarjı akıllı priz veya priz tipi enerji ölçer üzerinden yapılmamalıdır.');
    if(input.loadType==='fixed')block('fixed','Sabit tesisat ve pano devreleri için priz tipi ürün yerine yetkili ölçüm ve uygun pano tipi sayaç gerekir.');
    if(input.loadType==='multiple')block('multiple','Grup priz veya çoklu yükün toplam akımı ve kalkış davranışı belirsizdir; cihazları ayrı ölçün.');
    if(!input.damageFree)block('damage','Priz, fiş veya ölçüm cihazında çatlak, gevşeklik, yanık izi ya da aşırı ısınma varsa kullanmayın.');
    if(!input.directWallSocket)block('interposed','Enerji ölçer/akıllı priz uzatma, çoklayıcı veya grup priz üzerinden kullanılmamalıdır.');
    if(!input.indoorDry)block('environment','İç ve kuru ortam uygunluğu doğrulanmadı.');
    if(input.needsEarth&&!input.earthContinuity)block('earth','Sınıf I cihaz için koruma iletkeni sürekliliği doğrulanmadı.');
    if(currentA>input.candidateCurrentA+1e-9)block('current_rating','Tahmini çalışma akımı ürünün nominal akımını aşıyor.');
    if(input.loadPowerW>input.candidatePowerW+1e-9)block('power_rating','Cihaz gücü ürünün nominal watt sınırını aşıyor.');
    if(longRun&&currentA>currentLimitA+1e-9)block('continuous_current','Uzun süreli kullanımda görünür yüzde 80 ön değerlendirme sınırı aşılıyor.');
    if(longRun&&input.loadPowerW>powerLimitW+1e-9)block('continuous_power','Uzun süreli kullanımda görünür yüzde 80 güç ön değerlendirme sınırı aşılıyor.');
    if(startupCurrentA>input.candidateCurrentA+1e-9)block('startup','Kalkış/tepe akımı ürünün nominal akımını aşabilir.');
    if(['motor','compressor'].includes(input.loadType)&&!input.manufacturerLoadApproved)block('inductive','Motor/kompresör yükü için tam ürün modelinin izin verdiği HP, kalkış ve röle sınırı doğrulanmadı.');
    if(!input.energyMonitoring)block('monitoring','Değerlendirilen üründe enerji izleme özelliği doğrulanmadı.');

    if(!input.labelVerified)warnings.push('Akım, watt ve ölçüm özellikleri tam model etiketi/kılavuzundan doğrulanmadı.');
    if(!input.manufacturerLoadApproved&&!['motor','compressor'].includes(input.loadType))warnings.push('Üreticinin tam yük türü uyumluluğu kontrol edilmedi.');
    if(input.goal==='remote'&&!input.remoteSwitching)warnings.push('Uzaktan açma-kapama hedefi var; üründe bu özellik doğrulanmadı.');
    if(input.goal==='schedule'&&!input.scheduleSupport)warnings.push('Zamanlama hedefi var; üründe programlama desteği doğrulanmadı.');
    if(['remote','schedule'].includes(input.goal)&&input.meterType!=='smart_plug')warnings.push('Bu hedef için yalnız gösterge sunan priz tipi wattmetre yeterli değildir.');
    if(input.goal==='standby'){
      if(input.standbyPowerW==null||input.candidateMinMeasureW==null)warnings.push('Standby ölçümü için beklenen düşük güç ve ürünün asgari gösterim/çözünürlük değeri eksik.');
      else if(input.standbyPowerW<input.candidateMinMeasureW)warnings.push('Beklenen standby gücü ürünün belirtilen asgari gösterim değerinin altında.');
    }
    if(input.goal==='history'){
      if(input.desiredHistoryDays==null||input.candidateHistoryDays==null)warnings.push('İstenen ve sunulan kayıt süresi birlikte doğrulanmadı.');
      else if(input.candidateHistoryDays<input.desiredHistoryDays)warnings.push('Ürün geçmiş kayıt süresi hedefinizi karşılamıyor.');
    }
    if(input.loadType==='resistive'&&input.unattendedUse)warnings.push('Isıtıcı, kettle veya ütü gibi rezistif yükleri gözetimsiz/uzaktan çalıştırmak için ürün yönlendirmesi açılmaz.');
    if(input.loadType==='electronics'&&input.loadPowerW>=60&&input.loadPowerW<=75)warnings.push('Bazı 60–75 W adaptörlerde yüksek ilk akım olabilir; üretici yük tablosunu doğrulayın.');

    if(input.goal==='measure'||input.goal==='standby')checks.push('Yerel ekran veya uygulamada W, kWh ve ölçüm çözünürlüğünü doğrulayın.');
    if(['history','remote','schedule'].includes(input.goal))checks.push('Bulut/hesap gereksinimi, veri saklama süresi ve internet kesintisindeki davranışı doğrulayın.');
    if(input.dailyHours>=8)checks.push('Uzun süreli kullanımda ürün sıcaklığını, priz temasını ve üreticinin sürekli yük sınırını periyodik kontrol edin.');
    checks.push('Ürünün tam model ve donanım sürümündeki nominal akım, watt ve desteklenen yük türünü kontrol edin.');
    checks.push('Priz, fiş ve ürün gövdesinde çalışma sırasında olağandışı ısı oluşursa kullanımı durdurun.');
    checks.push('Akıllı priz enerji kesildiğinde varsayılan açık/kapalı davranışını ve manuel düğmesini doğrulayın.');

    const status=blockers.length?'incompatible':warnings.length?'conditional':'compatible';
    const allVerified=input.labelVerified&&input.manufacturerLoadApproved&&input.damageFree&&input.directWallSocket&&input.indoorDry&&(!input.needsEarth||input.earthContinuity);
    const featureMatch=input.energyMonitoring&&
      (input.goal!=='remote'||input.remoteSwitching)&&
      (input.goal!=='schedule'||input.scheduleSupport)&&
      (!['remote','schedule','history'].includes(input.goal)||input.meterType==='smart_plug');
    const lowRisk=['electronics','lighting','resistive'].includes(input.loadType)&&
      input.loadPowerW<=2000&&currentA<=10&&startupCurrentA<=input.candidateCurrentA&&
      !(input.loadType==='resistive'&&input.unattendedUse);
    const noPurchaseNeeded=input.ownership==='owned'&&status==='compatible'&&featureMatch;
    const commercialAllowed=Boolean(input.ownership==='candidate'&&status==='compatible'&&allVerified&&featureMatch&&lowRisk);
    const professionalRequired=['medical','ev','fixed','multiple'].includes(input.loadType)||blockerCodes.includes('earth')||blockerCodes.includes('inductive');

    return {
      input,status,blockers,blockerCodes,warnings,checks,
      currentA:round(currentA),startupCurrentA:round(startupCurrentA),
      dailyKwh:round(dailyKwh,3),annualKwh:round(annualKwh,1),
      continuousLimitA:round(currentLimitA),continuousLimitW:round(powerLimitW),
      recommendedClass:recommendedClass(input),
      noPurchaseNeeded,commercialAllowed,professionalRequired,
      lowRisk,featureMatch
    };
  }

  return {analyze,recommendedClass};
});