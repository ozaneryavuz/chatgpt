(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports){module.exports=api;}
  root.Alo186UPSBatterySuitability=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(){
  'use strict';
  const number=(value,name,min,max)=>{const parsed=Number(value);if(!Number.isFinite(parsed)||parsed<min||parsed>max)throw new Error(`${name} ${min}–${max} aralığında olmalıdır.`);return parsed;};
  const enumValue=(value,allowed,fallback)=>allowed.includes(value)?value:fallback;
  const bool=value=>value===true||value==='true'||value===1||value==='1';
  const round=(value,digits=1)=>Number(value.toFixed(digits));
  function analyze(raw){
    const input={
      upsType:enumValue(raw.upsType,['desktop','rack','online','unknown'],'unknown'),
      upsVa:number(raw.upsVa,'UPS gücü',300,20000),
      upsAgeYears:number(raw.upsAgeYears,'UPS yaşı',0,25),
      batteryChemistry:enumValue(raw.batteryChemistry,['vrla','lithium','unknown'],'unknown'),
      batteryAgeYears:number(raw.batteryAgeYears,'Akü yaşı',0,20),
      ambientC:number(raw.ambientC,'Ortam sıcaklığı',0,50),
      runtimeNowMinutes:number(raw.runtimeNowMinutes,'Mevcut çalışma süresi',0,1440),
      runtimeRequiredMinutes:number(raw.runtimeRequiredMinutes,'Gerekli çalışma süresi',1,1440),
      selfTest:enumValue(raw.selfTest,['pass','fail','not-run'],'not-run'),
      replaceAlarm:bool(raw.replaceAlarm),
      physicalSafe:bool(raw.physicalSafe),
      fullyChargedBeforeTest:bool(raw.fullyChargedBeforeTest),
      normalLoadTested:bool(raw.normalLoadTested),
      exactUpsModelKnown:bool(raw.exactUpsModelKnown),
      cartridgeCodeKnown:bool(raw.cartridgeCodeKnown),
      exactSpecsMatch:bool(raw.exactSpecsMatch),
      manufacturerUserReplaceable:bool(raw.manufacturerUserReplaceable),
      manualChecked:bool(raw.manualChecked),
      supportChecked:bool(raw.supportChecked),
      allModulesSameAge:bool(raw.allModulesSameAge),
      batterySystem:enumValue(raw.batterySystem,['internal-single','multiple-modules','external-cabinet','unknown'],'unknown'),
      criticalLoad:bool(raw.criticalLoad),
      medicalLoad:bool(raw.medicalLoad)
    };
    const blockers=[],blockerCodes=[],warnings=[],checks=[];
    const block=(code,text)=>{blockerCodes.push(code);blockers.push(text);};
    const runtimeMargin=input.runtimeNowMinutes-input.runtimeRequiredMinutes;
    const runtimeAdequate=runtimeMargin>=0;
    const replacementSignal=input.replaceAlarm||input.selfTest==='fail'||!runtimeAdequate;
    if(!input.physicalSafe)block('physical_hazard','Şişme, sızıntı, koku veya aşırı ısınma bildirildi. UPS’i kullanmaya/şarj etmeye devam etmeyin; güvenli biçimde enerjiden ayırıp yetkili servis sürecini izleyin.');
    if(input.medicalLoad)block('medical','Tıbbi veya yaşam destek yükünde genel ürün yönlendirmesi yapılmaz; üretici ve uzman tarafından doğrulanmış süreklilik planı gerekir.');
    if(input.criticalLoad)warnings.push('Kritik işletme yükünde yalnız akü değişimine güvenmeyin; kontrollü runtime ve transfer testiyle yedekliliği doğrulayın.');
    if(input.ambientC>25)warnings.push('25°C üzerindeki ortam VRLA akü ömrünü hızla kısaltabilir; havalandırma ve gerçek batarya sıcaklığı kontrol edilmelidir.');
    if(input.selfTest==='not-run')warnings.push('Tam şarj sonrası normal yükle üretici self-test’i çalıştırılmadı. Akü satın almadan önce test sonucu doğrulanmalıdır.');
    if(input.selfTest!=='not-run'&&!input.fullyChargedBeforeTest)warnings.push('Self-test öncesinde akünün tam şarj olduğu doğrulanmadı; test sonucu yanıltıcı olabilir.');
    if(input.selfTest!=='not-run'&&!input.normalLoadTested)warnings.push('Self-test veya runtime kontrolü normal yükle yapılmadı; gerçek süre ihtiyacı doğrulanmalıdır.');
    if(!input.exactUpsModelKnown)warnings.push('UPS’in tam model kodu bilinmiyor; doğru kartuş kodu güvenle eşleştirilemez.');
    if(!input.cartridgeCodeKnown)warnings.push('Üreticinin tam model için önerdiği kartuş kodu doğrulanmadı.');
    if(!input.exactSpecsMatch)warnings.push('Gerilim, Ah/Wh, kimya, konnektör ve adet eşleşmesi doğrulanmadı.');
    if(!input.manufacturerUserReplaceable)warnings.push('Üretici bu modelin kullanıcı tarafından akü değişimine açık olduğunu doğrulamıyor; UPS kasasını açmayın.');
    if(!input.manualChecked)warnings.push('Tam modelin akü değişim ve güvenlik kılavuzu kontrol edilmedi.');
    if(!input.supportChecked)warnings.push('UPS’in destek durumu ve toplam cihaz yaşı kontrol edilmedi.');
    if(input.batterySystem!=='internal-single')warnings.push('Çoklu modül, haricî akü kabini veya belirsiz batarya sistemi profesyonel servis ve bütün dizi değerlendirmesi gerektirir.');
    if(!input.allModulesSameAge)warnings.push('Aynı seri/dizide eski ve yeni modülleri karıştırmayın; üretici talimatına göre tüm ilgili modülleri birlikte değerlendirin.');
    const compareUps=input.upsAgeYears>=7||!input.supportChecked;
    if(input.upsAgeYears>=7)warnings.push('UPS gövdesi 7 yıl veya daha yaşlı. Fan, röle ve kondansatör ömrü nedeniyle yalnız akü değişimini yeni UPS ile toplam maliyet açısından karşılaştırın.');
    if(input.batteryChemistry==='unknown')warnings.push('Akü kimyası bilinmiyor; VRLA ve lityum kartuşlar birbirinin yerine kullanılamaz.');
    if(input.batteryChemistry==='vrla'&&input.batteryAgeYears>=3)checks.push('VRLA akü 3 yıl veya daha yaşlı; yaş tek başına karar değildir fakat runtime ve self-test yakın izlenmelidir.');
    if(input.batteryChemistry==='lithium')warnings.push('Lityum UPS bataryasında yalnız üreticinin tam model için onayladığı modül ve servis yöntemi kullanılmalıdır.');
    if(runtimeAdequate)checks.push(`Mevcut yaklaşık çalışma süresi gerekli süreden ${round(runtimeMargin)} dakika daha uzun.`);else checks.push(`Mevcut yaklaşık çalışma süresi gerekli süreden ${round(Math.abs(runtimeMargin))} dakika kısa.`);
    checks.push('Tam model ve kartuş kodunu seri numarasıyla karıştırmadan üretici sayfasından doğrulayın.','UPS kasasını açmayın; yalnız üreticinin kullanıcı değişimine açık akü erişim panelini ve kılavuzunu kullanın.','Akü değişiminden sonra tam şarj, self-test ve normal yükte kontrollü runtime testi yapın.','Eski aküyü üretici veya yetkili geri dönüşüm kanalına teslim edin.');
    const professionalRequired=Boolean(blockerCodes.length||input.upsType!=='desktop'||input.upsVa>3000||input.batterySystem!=='internal-single'||input.criticalLoad||input.medicalLoad||input.batteryChemistry==='lithium');
    const exactVerified=input.exactUpsModelKnown&&input.cartridgeCodeKnown&&input.exactSpecsMatch&&input.manufacturerUserReplaceable&&input.manualChecked&&input.allModulesSameAge;
    const lowRiskBand=input.upsType==='desktop'&&input.upsVa<=3000&&input.batterySystem==='internal-single'&&input.batteryChemistry==='vrla'&&input.physicalSafe&&!input.criticalLoad&&!input.medicalLoad;
    const noPurchaseNeeded=Boolean(!replacementSignal&&runtimeAdequate&&input.selfTest==='pass'&&!input.replaceAlarm&&input.physicalSafe);
    const retestFirst=Boolean(!blockerCodes.length&&(input.selfTest==='not-run'||!input.fullyChargedBeforeTest||!input.normalLoadTested));
    const commercialAllowed=Boolean(replacementSignal&&exactVerified&&lowRiskBand&&!compareUps&&!retestFirst&&!professionalRequired);
    let status='monitor';
    if(blockerCodes.length)status='stop';
    else if(professionalRequired)status='professional';
    else if(compareUps&&replacementSignal)status='compare-ups';
    else if(retestFirst)status='retest';
    else if(replacementSignal&&exactVerified)status='replace-battery';
    else if(replacementSignal)status='information-needed';
    else if(noPurchaseNeeded)status='monitor';
    else status='conditional';
    let confidence=0;
    [input.exactUpsModelKnown,input.cartridgeCodeKnown,input.exactSpecsMatch,input.manufacturerUserReplaceable,input.manualChecked,input.supportChecked,input.fullyChargedBeforeTest,input.normalLoadTested,input.allModulesSameAge,input.selfTest!=='not-run'].forEach(v=>{if(v)confidence+=10;});
    return {input,status,runtimeMargin:round(runtimeMargin),runtimeAdequate,replacementSignal,compareUps,retestFirst,confidence,blockers,blockerCodes,warnings,checks,professionalRequired,noPurchaseNeeded,commercialAllowed,exactVerified,lowRiskBand};
  }
  return {analyze};
});