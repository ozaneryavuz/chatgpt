(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports){module.exports=api;}
  root.Alo186EVCableSuitability=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(){
  'use strict';
  const SQRT3=Math.sqrt(3);
  const STANDARD_CURRENTS=[16,20,32];
  const number=(value,name,min,max)=>{const parsed=Number(value);if(!Number.isFinite(parsed)||parsed<min||parsed>max)throw new Error(`${name} ${min}–${max} aralığında olmalıdır.`);return parsed;};
  const enumValue=(value,allowed,fallback)=>allowed.includes(value)?value:fallback;
  const bool=value=>value===true||value==='true'||value===1||value==='1';
  const round=(value,digits=2)=>Number(value.toFixed(digits));
  const powerFor=(phases,current)=>phases==='three'?SQRT3*400*current/1000:230*current/1000;
  const currentFor=(phases,powerKw)=>phases==='three'?powerKw*1000/(SQRT3*400):powerKw*1000/230;
  const standardCurrent=value=>STANDARD_CURRENTS.find(item=>item+1e-9>=value)??null;
  function effectivePhases(vehicle,station,cable){if([vehicle,station,cable].includes('unknown'))return null;return [vehicle,station,cable].includes('single')?'single':'three';}
  function targetPhases(vehicle,station){if([vehicle,station].includes('unknown'))return null;return [vehicle,station].includes('single')?'single':'three';}
  function analyze(raw){
    const input={stationType:enumValue(raw.stationType,['socketed','tethered','unknown'],'unknown'),vehicleInlet:enumValue(raw.vehicleInlet,['type2','type1','unknown'],'unknown'),vehiclePhases:enumValue(raw.vehiclePhases,['single','three','unknown'],'unknown'),vehicleMaxKw:number(raw.vehicleMaxKw,'Araç azami AC gücü',1,43),stationPhases:enumValue(raw.stationPhases,['single','three','unknown'],'unknown'),stationMaxCurrent:number(raw.stationMaxCurrent,'İstasyon azami akımı',6,63),ownership:enumValue(raw.ownership,['candidate','owned'],'candidate'),cableConnector:enumValue(raw.cableConnector,['type2-type2','type1-type2','unknown'],'unknown'),cablePhases:enumValue(raw.cablePhases,['single','three','unknown'],'unknown'),cableRatedCurrent:number(raw.cableRatedCurrent,'Kablo etiket akımı',6,63),cableLength:number(raw.cableLength,'Kablo uzunluğu',1,20),labelVerified:bool(raw.labelVerified),vehicleSpecVerified:bool(raw.vehicleSpecVerified),stationSpecVerified:bool(raw.stationSpecVerified),damageFree:bool(raw.damageFree),storageOk:bool(raw.storageOk),manufacturerCompatibility:bool(raw.manufacturerCompatibility),noExtension:bool(raw.noExtension),lockingWorks:bool(raw.lockingWorks)};
    const blockers=[],blockerCodes=[],warnings=[],checks=[];
    const block=(code,text)=>{blockerCodes.push(code);blockers.push(text);};
    if(input.stationType==='tethered')return {input,status:'not-needed',targetPowerKw:null,cablePowerKw:null,recommendedPhases:null,recommendedCurrent:null,recommendedLabel:'Sabit kablolu istasyonda ayrı Mode 3 kablo gerekmez',limitingComponent:'İstasyonun sabit kablosu',blockers:[],blockerCodes:[],warnings:['İstasyon kablosunda hasar veya uyumsuzluk varsa istasyon işletmecisi ya da yetkili servis değerlendirmelidir.'],checks:['Araç girişinin istasyonun sabit konnektörüyle uyumlu olduğunu doğrulayın.','Kablo ve konnektörde hasar, aşırı kir veya kilitleme sorunu varsa kullanmayın.'],commercialAllowed:false,noPurchaseNeeded:true,professionalRequired:false,overSpecified:false};
    if(input.vehicleInlet==='type1')block('connector','Araç girişi Type 1 olarak seçildi. Type 2–Type 2 Mode 3 kablo doğrudan uyumlu değildir; araç üreticisinin desteklediği kablo veya adaptör çözümü gerekir.');
    if(input.vehicleInlet==='unknown')block('connector_unknown','Araç giriş tipi bilinmiyor. Fiziksel benzerliğe göre ürün seçmeyin.');
    if(input.stationType==='unknown')warnings.push('Şarj noktasının soketli mi yoksa sabit kablolu mu olduğu doğrulanmadı.');
    if(input.cableConnector!=='type2-type2')block('cable_connector','Soketli Type 2 istasyon için değerlendirilen taşınabilir kablo Type 2–Type 2 Mode 3 olmalıdır.');
    if(!input.damageFree)block('damage','Kabloda, konnektörde veya dış kılıfta hasar/aşınma var. Elektrik çarpması riski nedeniyle kullanılmamalıdır.');
    if(!input.noExtension)block('interposed_equipment','Şarj kaynağı ile araç arasına uzatma kablosu, çoklayıcı, zamanlayıcı veya benzeri ekipman eklenmemelidir.');
    if(!input.lockingWorks)block('locking','Konnektörün kilitleme veya tam oturma davranışı doğrulanmadı; şarj başlatılmamalıdır.');
    const targetPhase=targetPhases(input.vehiclePhases,input.stationPhases);
    let targetPowerKw=null,requiredCurrent=null,recommendedCurrent=null;
    if(targetPhase){const stationPower=powerFor(targetPhase,input.stationMaxCurrent);targetPowerKw=Math.min(input.vehicleMaxKw,stationPower);requiredCurrent=currentFor(targetPhase,targetPowerKw);recommendedCurrent=standardCurrent(requiredCurrent);if(recommendedCurrent==null)warnings.push('Hedef akım 32 A taşınabilir tüketici kablosu sınıfının üzerindedir; istasyon ve araç üreticisiyle profesyonel çözüm gerekir.');}else warnings.push('Araç veya istasyon faz yapısı bilinmediği için hedef güç sınıfı kesinleştirilemedi.');
    const effective=effectivePhases(input.vehiclePhases,input.stationPhases,input.cablePhases);
    let cablePowerKw=null;if(effective)cablePowerKw=Math.min(input.vehicleMaxKw,powerFor(effective,Math.min(input.stationMaxCurrent,input.cableRatedCurrent)));
    if(targetPhase&&input.cablePhases!=='unknown'){if(targetPhase==='three'&&input.cablePhases==='single')block('phase_capacity','Tek fazlı kablo, araç ve istasyonun trifaze AC kapasitesini kullanamaz; şarj daha düşük güçte kalır.');}else if(input.cablePhases==='unknown')warnings.push('Kablonun monofaze/trifaze yapısı etiket veya üretici belgesinden doğrulanmadı.');
    if(requiredCurrent!=null&&input.cableRatedCurrent+1e-9<requiredCurrent)block('current_capacity',`Kablo ${input.cableRatedCurrent.toFixed(0)} A etiketli; hedef güç için yaklaşık ${requiredCurrent.toFixed(1)} A gerekir. Kablo şarjı daha düşük akımla sınırlar.`);
    if(!input.labelVerified)warnings.push('Kablonun Type 2, Mode 3, faz, akım ve uzunluk bilgileri tam model etiketinden doğrulanmadı.');
    if(!input.vehicleSpecVerified)warnings.push('Aracın azami AC gücü ve faz desteği üretici belgesinden doğrulanmadı.');
    if(!input.stationSpecVerified)warnings.push('Şarj noktasının fazı ve azami akımı istasyon etiketi veya işletmeci bilgisinden doğrulanmadı.');
    if(!input.manufacturerCompatibility)warnings.push('Araç ve kablo üreticisinin uyumluluk talimatı kontrol edilmedi.');
    if(!input.storageOk)warnings.push('Koruyucu kapak, kuru/temiz saklama ve konnektör koruması doğrulanmadı.');
    if(input.cableLength>10)warnings.push('10 m üzerindeki kablo daha ağır ve zor yönetilir; üreticinin uzunluk, sinyal ve saklama talimatını ayrıca kontrol edin.');
    const overSpecified=Boolean(recommendedCurrent&&input.cableRatedCurrent>recommendedCurrent&&input.cablePhases!=='unknown');
    if(overSpecified)warnings.push(`Hedef için yaklaşık ${recommendedCurrent} A kablo yeterli olabilir; daha yüksek akım etiketi aracın veya istasyonun sınırını aşarak şarjı hızlandırmaz. Gereksiz yüksek sınıf için ürün yönlendirmesi açılmaz.`);
    let limitingComponent='Belirlenemedi';
    if(targetPhase&&cablePowerKw!=null){const vehicle=input.vehicleMaxKw,station=powerFor(targetPhase,input.stationMaxCurrent),cable=powerFor(effective||targetPhase,input.cableRatedCurrent),min=Math.min(vehicle,station,cable);limitingComponent=min===vehicle?'Araç üstü AC şarj cihazı':min===station?'Şarj noktası':'Şarj kablosu';}
    const safetyCodes=['damage','interposed_equipment','locking','connector','connector_unknown','cable_connector'];
    const safetyBlocker=blockerCodes.some(code=>safetyCodes.includes(code));
    const capabilityGap=blockerCodes.some(code=>['phase_capacity','current_capacity'].includes(code));
    const allVerified=input.stationType==='socketed'&&input.vehicleInlet==='type2'&&input.cableConnector==='type2-type2'&&input.labelVerified&&input.vehicleSpecVerified&&input.stationSpecVerified&&input.damageFree&&input.storageOk&&input.manufacturerCompatibility&&input.noExtension&&input.lockingWorks&&targetPhase&&input.cablePhases!=='unknown';
    const lowRiskBand=(recommendedCurrent??99)<=32&&input.cableRatedCurrent<=32&&input.cableLength<=15;
    let status='compatible';if(blockers.length)status='incompatible';else if(warnings.length)status='conditional';
    const targetMet=targetPowerKw!=null&&cablePowerKw!=null&&cablePowerKw+0.05>=targetPowerKw&&!capabilityGap;
    const noPurchaseNeeded=input.ownership==='owned'&&targetMet&&!safetyBlocker&&allVerified;
    const commercialAllowed=Boolean(allVerified&&lowRiskBand&&!noPurchaseNeeded&&!overSpecified&&((input.ownership==='candidate'&&!safetyBlocker)||(input.ownership==='owned'&&capabilityGap&&!safetyBlocker)));
    const professionalRequired=safetyBlocker||!targetPhase||recommendedCurrent==null||input.vehicleInlet!=='type2';
    if(recommendedCurrent&&targetPhase)checks.push(`Hedefi kabloyla sınırlamamak için teknik minimum: ${targetPhase==='three'?'trifaze':'monofaze'} ${recommendedCurrent} A Type 2–Type 2 Mode 3.`);
    checks.push('Gerçek şarj gücü; araç, istasyon ve kablonun desteklediği en düşük güçle sınırlanır.','Kablo etiketinde Type 2, Mode 3, faz sayısı, akım ve üretici/model bilgilerini doğrulayın.','Konnektör, dış kılıf, kilit ve koruyucu kapakta çatlak, ezilme, aşınma veya aşırı kir bulunmamalıdır.','Şarj kaynağı ile araç arasına uzatma, çoklayıcı, adaptör veya haricî zamanlayıcı eklemeyin.','Hasarlı kabloyu onarmaya çalışmayın; üretici veya yetkili servis sürecini izleyin.');
    return {input,status,targetPowerKw:targetPowerKw==null?null:round(targetPowerKw),cablePowerKw:cablePowerKw==null?null:round(cablePowerKw),recommendedPhases:targetPhase,recommendedCurrent,recommendedLabel:recommendedCurrent&&targetPhase?`${targetPhase==='three'?'Trifaze':'Monofaze'} ${recommendedCurrent} A Type 2–Type 2 Mode 3`:'Teknik sınıf doğrulanamadı',limitingComponent,blockers,blockerCodes,warnings,checks,commercialAllowed,noPurchaseNeeded,professionalRequired,overSpecified};
  }
  return {analyze,powerFor,currentFor,effectivePhases,targetPhases};
});