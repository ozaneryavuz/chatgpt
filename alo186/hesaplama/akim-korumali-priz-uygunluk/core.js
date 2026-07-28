(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports){module.exports=api;}
  root.Alo186SurgeStripSuitability=api;
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

  function targetJoules(loadType,problemType){
    if(problemType==='extra_outlets')return 0;
    if(['electronics','networking','av'].includes(loadType))return 1000;
    if(['lighting','small_appliance'].includes(loadType))return 400;
    return 1000;
  }

  function recommendedClass(input,target){
    if(input.problemType==='ongoing_voltage')return 'Gerilim koruma çözüm seçici / yetkili ölçüm';
    if(input.problemType==='neutral_fault')return '186 veya yetkili elektrikçi değerlendirmesi';
    if(input.problemType==='outage_backup')return 'UPS, power station veya yedek güç hesabı';
    if(input.problemType==='extra_outlets')return 'Etiket akımına uygun standart grup priz';
    return target>=1000?'En az 1.000 J rehber sınıfı, koruma göstergeli grup priz':'En az 400 J rehber sınıfı, koruma göstergeli grup priz';
  }

  function analyze(raw){
    const input={
      problemType:enumValue(raw.problemType,['transient','lightning','extra_outlets','ongoing_voltage','neutral_fault','outage_backup'],'transient'),
      loadType:enumValue(raw.loadType,['electronics','networking','av','lighting','small_appliance','motor_compressor','heater','medical','ev','fixed'],'electronics'),
      ownership:enumValue(raw.ownership,['candidate','owned'],'candidate'),
      totalPowerW:number(raw.totalPowerW,'Toplam cihaz gücü',1,10000),
      powerFactor:number(raw.powerFactor,'Güç faktörü',0.2,1),
      startupPowerW:number(raw.startupPowerW,'Kalkış/tepe gücü',1,30000),
      dailyHours:number(raw.dailyHours,'Günlük çalışma süresi',0.1,24),
      requiredOutlets:number(raw.requiredOutlets,'Gerekli priz sayısı',1,24),
      requiredUsbPorts:number(raw.requiredUsbPorts,'Gerekli USB portu',0,12),
      neededCableM:number(raw.neededCableM,'Gerekli kablo mesafesi',0,20),
      candidateOutlets:number(raw.candidateOutlets,'Ürün priz sayısı',1,24),
      candidateUsbPorts:number(raw.candidateUsbPorts,'Ürün USB portu',0,12),
      candidateCurrentA:number(raw.candidateCurrentA,'Ürün etiket akımı',1,32),
      candidatePowerW:number(raw.candidatePowerW,'Ürün etiket gücü',100,7360),
      candidateJoules:number(raw.candidateJoules,'Joule değeri',0,10000,true),
      candidateCableM:number(raw.candidateCableM,'Ürün kablo uzunluğu',0,20),
      surgeClaimVerified:bool(raw.surgeClaimVerified),
      jouleVerified:bool(raw.jouleVerified),
      currentPowerVerified:bool(raw.currentPowerVerified),
      labelVerified:bool(raw.labelVerified),
      protectionIndicator:bool(raw.protectionIndicator),
      indicatorActive:bool(raw.indicatorActive),
      autoShutoff:bool(raw.autoShutoff),
      breakerOrFuse:bool(raw.breakerOrFuse),
      manufacturerLoadApproved:bool(raw.manufacturerLoadApproved),
      groundedWallSocket:bool(raw.groundedWallSocket),
      earthContinuityKnown:bool(raw.earthContinuityKnown),
      directWallConnection:bool(raw.directWallConnection),
      damageFree:bool(raw.damageFree),
      indoorDry:bool(raw.indoorDry),
      daisyChainPlanned:bool(raw.daisyChainPlanned),
      extensionPlanned:bool(raw.extensionPlanned)
    };

    const currentA=input.totalPowerW/(VOLTAGE*input.powerFactor);
    const startupCurrentA=input.startupPowerW/(VOLTAGE*input.powerFactor);
    const longRun=input.dailyHours>=2;
    const continuousCurrentLimit=input.candidateCurrentA*(longRun?0.8:1);
    const continuousPowerLimit=Math.min(input.candidatePowerW,VOLTAGE*input.candidateCurrentA)*(longRun?0.8:1);
    const loadRatio=Math.max(currentA/input.candidateCurrentA,input.totalPowerW/input.candidatePowerW);
    const target=targetJoules(input.loadType,input.problemType);
    const jouleMargin=input.candidateJoules==null||target===0?null:input.candidateJoules-target;
    const outletSpare=input.candidateOutlets-input.requiredOutlets;
    const blockers=[],blockerCodes=[],warnings=[],checks=[];
    const block=(code,text)=>{blockerCodes.push(code);blockers.push(text);};

    if(input.problemType==='ongoing_voltage')block('ongoing_voltage','Sürekli düşük/yüksek gerilim, tekrarlayan cihaz kapanması veya uzun süren dalgalanma tak-çalıştır akım korumalı prizle çözülmez.');
    if(input.problemType==='neutral_fault')block('neutral_fault','Nötr kopması şüphesi, fazlar arası dengesiz parlaklık veya olağandışı gerilimde cihazları ayırın; 186 veya yetkili elektrikçi gerekir.');
    if(input.problemType==='outage_backup')block('outage_backup','Akım korumalı priz enerji kesintisinde yedekleme sağlamaz; UPS, power station veya başka bir yedek güç çözümü gerekir.');
    if(input.loadType==='medical')block('medical','Tıbbi veya yaşam destek cihazında genel tüketici grup prizi için ürün yönlendirmesi yapılmaz.');
    if(input.loadType==='ev')block('ev','Elektrikli araç şarjı akım korumalı grup priz veya çoklayıcı üzerinden yapılmamalıdır.');
    if(input.loadType==='fixed')block('fixed','Sabit tesisat ve pano devreleri için priz tipi ürün yerine yetkili proje ve pano tipi SPD değerlendirmesi gerekir.');
    if(input.loadType==='heater')block('heater','Isıtıcı, kettle veya ütü gibi yüksek güçlü rezistif yükler için grup priz affiliate yönlendirmesi açılmaz.');
    if(input.loadType==='motor_compressor'&&!input.manufacturerLoadApproved)block('motor','Motor veya kompresörün kalkış akımı ve tam ürün modelinin izin verdiği yük türü doğrulanmadı.');
    if(input.daisyChainPlanned)block('daisy_chain','Grup prizleri birbirine bağlamak aşırı yük ve ısınma riskini artırır; uygun priz sayılı tek ürün veya sabit tesisat kullanın.');
    if(input.extensionPlanned)block('extension','Akım korumalı prizi uzatma kablosuyla birlikte kullanmayın; yeterli uzunlukta tek ürün seçin.');
    if(!input.directWallConnection)block('direct_wall','Ürün doğrudan uygun duvar prizine bağlanmalıdır.');
    if(!input.groundedWallSocket||!input.earthContinuityKnown)block('ground','Topraklı duvar prizi ve koruma iletkeni doğrulanmadan surge koruma uygun kabul edilmez.');
    if(!input.damageFree)block('damage','Fiş, kablo, gövde veya prizlerde gevşeklik, kararma, erime, yanık kokusu ya da aşırı ısı varsa kullanmayın.');
    if(!input.indoorDry)block('environment','İç ve kuru ortam uygunluğu doğrulanmadı.');
    if(currentA>input.candidateCurrentA+1e-9)block('current_rating','Tahmini çalışma akımı ürünün nominal akımını aşıyor.');
    if(input.totalPowerW>input.candidatePowerW+1e-9)block('power_rating','Toplam cihaz gücü ürünün nominal watt sınırını aşıyor.');
    if(longRun&&currentA>continuousCurrentLimit+1e-9)block('continuous_current','Uzun süreli kullanımda görünür yüzde 80 ön değerlendirme akım sınırı aşılıyor.');
    if(longRun&&input.totalPowerW>continuousPowerLimit+1e-9)block('continuous_power','Uzun süreli kullanımda görünür yüzde 80 ön değerlendirme güç sınırı aşılıyor.');
    if(startupCurrentA>input.candidateCurrentA+1e-9)block('startup','Kalkış/tepe akımı ürünün nominal akımını aşabilir.');
    if(input.requiredOutlets>input.candidateOutlets)block('outlets','Ürün priz sayısı ihtiyacı karşılamıyor; çoklayıcı eklemek yerine daha fazla prizli tek ürün seçin.');
    if(input.neededCableM>input.candidateCableM+1e-9)block('cable','Ürün kablosu gerekli mesafeye yetmiyor; uzatma eklemek yerine uygun kablo uzunluğunda ürün seçin.');
    if(input.ownership==='owned'&&input.protectionIndicator&&!input.indicatorActive)block('indicator_off','Mevcut üründe koruma göstergesi aktif değil; koruma devresi tükenmiş veya arızalı olabilir.');

    if(input.problemType==='extra_outlets')warnings.push('İhtiyaç yalnız priz sayısını artırmaksa surge koruma için ek ödeme gerekmeyebilir; etiket akımı uygun standart grup priz yeterli olabilir.');
    if(['transient','lightning'].includes(input.problemType)&&!input.surgeClaimVerified)warnings.push('Ürün yalnız grup priz olabilir; surge/protection/suppression iddiası tam modelde doğrulanmadı.');
    if(target>0&&(input.candidateJoules==null||!input.jouleVerified))warnings.push('Joule değeri tam model etiketi veya üretici teknik sayfasından doğrulanmadı.');
    else if(target>0&&input.candidateJoules<target)warnings.push(`Girilen ${input.candidateJoules} J, seçilen kullanım için görünür ${target} J rehber sınıfının altında.`);
    if(!input.currentPowerVerified)warnings.push('Nominal akım ve güç değerleri tam model etiketi/kılavuzundan birlikte doğrulanmadı.');
    if(!input.labelVerified)warnings.push('Tam model, bölgesel fiş/priz standardı ve ürün etiketi doğrulanmadı.');
    if(!input.protectionIndicator)warnings.push('Koruma devresinin hâlâ çalıştığını gösteren görünür gösterge doğrulanmadı.');
    if(input.requiredUsbPorts>input.candidateUsbPorts)warnings.push('Ürün USB port sayısı ihtiyacı karşılamıyor; haricî adaptör yerleşimini ayrıca planlayın.');
    if(!input.breakerOrFuse)warnings.push('Üründe aşırı akım için sıfırlanabilir kesici veya sigorta özelliği doğrulanmadı.');
    if(input.problemType==='lightning')checks.push('Priz tipi ürün yalnız son koruma katmanıdır; bina topraklaması, eşpotansiyel bağlantı ve pano tipi SPD ayrıca değerlendirilmelidir.');
    if(!input.autoShutoff)checks.push('Koruma devresi tükendiğinde enerjiyi otomatik kesen özellik varsa üretici kılavuzundan doğrulayın.');
    checks.push('Koruma göstergesinin anlamını tam model kılavuzundan kontrol edin; yalnız enerji ışığı korumanın aktif olduğunu kanıtlamaz.');
    checks.push('Joule, nominal akım, watt, priz sayısı ve kablo uzunluğunu satın alma sayfasından değil tam model etiketi/teknik sayfasından doğrulayın.');
    checks.push('Tak-çalıştır surge koruma; sürekli düşük/yüksek gerilim, nötr kopması, kesinti veya pano tipi SPD ihtiyacının yerine geçmez.');
    checks.push('Fiş veya prizde çalışma sırasında olağandışı ısı, koku, gevşeme ya da renk değişimi olursa kullanımı durdurun.');

    const status=blockers.length?'incompatible':warnings.length?'conditional':'compatible';
    const capacityMatch=!blockerCodes.some(code=>['current_rating','power_rating','continuous_current','continuous_power','startup','outlets','cable'].includes(code));
    const protectionMatch=input.problemType==='extra_outlets'||(input.surgeClaimVerified&&input.jouleVerified&&input.candidateJoules!=null&&input.candidateJoules>=target&&input.protectionIndicator);
    const allVerified=input.currentPowerVerified&&input.labelVerified&&input.damageFree&&input.indoorDry&&input.directWallConnection&&input.groundedWallSocket&&input.earthContinuityKnown;
    const lowRisk=['electronics','networking','av','lighting','small_appliance'].includes(input.loadType)&&input.totalPowerW<=2300&&currentA<=10&&!input.daisyChainPlanned&&!input.extensionPlanned;
    const noPurchaseNeeded=Boolean(input.ownership==='owned'&&blockers.length===0&&capacityMatch&&(input.problemType==='extra_outlets'||protectionMatch)&&(input.protectionIndicator?input.indicatorActive:true));
    const commercialAllowed=Boolean(input.ownership==='candidate'&&status==='compatible'&&allVerified&&protectionMatch&&lowRisk&&['transient','lightning'].includes(input.problemType));
    const professionalRequired=Boolean(['ongoing_voltage','neutral_fault'].includes(input.problemType)||['medical','ev','fixed','heater','motor_compressor'].includes(input.loadType)||blockerCodes.includes('ground'));

    return {
      input,status,blockers,blockerCodes,warnings,checks,
      currentA:round(currentA),startupCurrentA:round(startupCurrentA),
      loadRatioPct:round(loadRatio*100,1),continuousCurrentLimit:round(continuousCurrentLimit),continuousPowerLimit:round(continuousPowerLimit),
      targetJoules:target,jouleMargin,outletSpare,
      recommendedClass:recommendedClass(input,target),
      noPurchaseNeeded,commercialAllowed,professionalRequired,lowRisk,protectionMatch,capacityMatch
    };
  }

  return {analyze,targetJoules,recommendedClass};
});
