(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports){module.exports=api;}
  root.Alo186UPSBatterySuitability=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(){
  'use strict';
  const bool=value=>value===true||value==='true'||value===1||value==='1';
  const enumValue=(value,allowed,fallback)=>allowed.includes(value)?value:fallback;
  const number=(value,name,min,max)=>{const parsed=Number(value);if(!Number.isFinite(parsed)||parsed<min||parsed>max)throw new Error(`${name} ${min}–${max} aralığında olmalıdır.`);return parsed;};
  const optionalNumber=(value,name,min,max)=>{if(value===''||value==null)return null;return number(value,name,min,max);};
  const round=(value,digits=1)=>value==null?null:Number(value.toFixed(digits));

  function ageSignals(chemistry,batteryAge){
    if(chemistry==='vrla')return {planning:batteryAge>=3,due:batteryAge>=5,label:batteryAge>=5?'5 yıl ve üzeri VRLA — önleyici değişim planı':batteryAge>=3?'3–5 yıl VRLA — yakından izleme':'3 yıl altı VRLA'};
    if(chemistry==='liion')return {planning:batteryAge>=8,due:batteryAge>=10,label:batteryAge>=10?'10 yıl ve üzeri lityum-iyon — üretici planını doğrulayın':batteryAge>=8?'8–10 yıl lityum-iyon — yakından izleme':'8 yıl altı lityum-iyon'};
    return {planning:false,due:false,label:'Kimya bilinmiyor — yaş eşiği uygulanmadı'};
  }

  function analyze(raw){
    const input={
      upsClass:enumValue(raw.upsClass,['desktop','rack','large','unknown'],'unknown'),
      upsAgeYears:number(raw.upsAgeYears,'UPS yaşı',0,25),
      chemistry:enumValue(raw.chemistry,['vrla','liion','unknown'],'unknown'),
      batteryAgeYears:number(raw.batteryAgeYears,'Akü yaşı',0,15),
      physicalState:enumValue(raw.physicalState,['normal','hazard','unknown'],'unknown'),
      fullyCharged:bool(raw.fullyCharged),
      selfTest:enumValue(raw.selfTest,['pass','replace','not-run','unknown'],'unknown'),
      measuredRuntimeMin:optionalNumber(raw.measuredRuntimeMin,'Ölçülen çalışma süresi',0,600),
      requiredRuntimeMin:number(raw.requiredRuntimeMin,'Gerekli çalışma süresi',1,600),
      runtimeTrend:enumValue(raw.runtimeTrend,['stable','declined','always-short','unknown'],'unknown'),
      repeatBatteryAlarm:bool(raw.repeatBatteryAlarm),
      outageDrop:bool(raw.outageDrop),
      exactModelVerified:bool(raw.exactModelVerified),
      userReplaceable:bool(raw.userReplaceable),
      exactCartridgeVerified:bool(raw.exactCartridgeVerified),
      candidateType:enumValue(raw.candidateType,['not-selected','manufacturer-exact','manufacturer-approved','generic-loose','unknown'],'unknown'),
      preassembledCartridge:bool(raw.preassembledCartridge),
      fullSetReplacement:bool(raw.fullSetReplacement),
      supportActive:bool(raw.supportActive),
      externalBatteryPacks:bool(raw.externalBatteryPacks),
      recyclingPlan:bool(raw.recyclingPlan),
      lifeSupport:bool(raw.lifeSupport)
    };

    const blockers=[],blockerCodes=[],warnings=[],checks=[],replacementReasons=[];
    const block=(code,text)=>{blockerCodes.push(code);blockers.push(text);};
    const age=ageSignals(input.chemistry,input.batteryAgeYears);
    const runtimeCoverage=input.measuredRuntimeMin==null?null:input.measuredRuntimeMin/input.requiredRuntimeMin*100;
    const runtimeMeets=runtimeCoverage!=null&&runtimeCoverage>=100;
    const runtimeShort=runtimeCoverage!=null&&runtimeCoverage<100;

    if(input.physicalState==='hazard')block('physical_hazard','Şişme, sızıntı, anormal koku veya aşırı ısı bildirildi. UPS’i güvenle enerjiden ayırın; aküyü şarj etmeye veya çıkarmaya çalışmayın.');
    if(input.physicalState==='unknown')warnings.push('Aküde şişme, sızıntı, koku ve aşırı ısı bulunmadığı doğrulanmadı.');
    if(input.lifeSupport)block('life_support','Tıbbi veya yaşam destek yükünde bu araç ürün seçimi yapmaz. Üretici onaylı süreklilik planı ve yetkili uzman gerekir.');
    if(input.upsClass==='large')block('large_system','3 kVA üzeri, üç fazlı veya yüksek enerjili UPS sınıfı seçildi. Akü değişimi yetkili servis ve güvenli enerji izolasyonu gerektirir.');
    if(input.upsClass==='unknown')warnings.push('UPS sınıfı bilinmiyor; kullanıcı değişimine uygun olup olmadığı kesinleştirilemedi.');
    if(input.externalBatteryPacks)block('external_pack','Haricî batarya kabini veya ek paket bulunan sistemde bütün dizi, DC koruma ve yaş uyumu profesyonel olarak değerlendirilmelidir.');
    if(input.candidateType==='generic-loose')block('generic_loose','Tek tek gevşek veya genel amaçlı aküler, doğrulanmış üretici kartuşu yerine otomatik olarak uygun kabul edilmez. Kablo, sigorta, bağlantı ve sertifika riski vardır.');
    if(!input.userReplaceable)warnings.push('Tam model kılavuzunda akünün kullanıcı tarafından değiştirilebilir olduğu doğrulanmadı.');
    if(!input.exactModelVerified)warnings.push('UPS’in tam model kodu doğrulanmadı. Benzer kasa veya VA değerine göre kartuş seçmeyin.');
    if(!input.exactCartridgeVerified&&input.candidateType!=='not-selected')warnings.push('Aday kartuş kodunun tam UPS modeliyle uyumu üretici belgesinden doğrulanmadı.');
    if(!input.preassembledCartridge&&input.candidateType!=='not-selected')warnings.push('Aday ürün üretici tarafından hazırlanmış tam kartuş/set olarak doğrulanmadı.');
    if(!input.fullSetReplacement&&input.candidateType!=='not-selected')warnings.push('Aynı seri dizide bütün modüllerin birlikte değiştirileceği doğrulanmadı; eski ve yeni aküyü karıştırmayın.');
    if(!input.recyclingPlan&&input.candidateType!=='not-selected')warnings.push('Eski akünün yetkili atık/geri dönüşüm kanalına teslim planı doğrulanmadı.');
    if(!input.supportActive)warnings.push('UPS modelinin güncel üretici desteği veya yedek parça erişimi doğrulanmadı.');

    const testIncomplete=!input.fullyCharged||['not-run','unknown'].includes(input.selfTest);
    if(!input.fullyCharged)warnings.push('Akü tam şarj edilmeden yapılan self-test yanıltıcı olabilir; üreticinin önerdiği şarj süresini tamamlayın.');
    if(input.selfTest==='not-run')warnings.push('Self-test yapılmadı. Normal yük bağlıyken üreticinin talimatına göre test uygulayın.');
    if(input.selfTest==='unknown')warnings.push('Self-test sonucu bilinmiyor.');
    if(input.selfTest==='replace'&&input.fullyCharged)replacementReasons.push('Tam şarj sonrası self-test akü değişimi uyarısı verdi.');
    if(input.repeatBatteryAlarm)replacementReasons.push('Tekrarlayan akü alarmı bildirildi.');
    if(input.outageDrop)replacementReasons.push('Kesintide yükün beklenmedik biçimde kapanması bildirildi.');
    if(runtimeShort&&input.runtimeTrend==='declined')replacementReasons.push('Aynı yükte çalışma süresi geçmişe göre düştü ve gerekli süreyi karşılamıyor.');
    if(age.due)replacementReasons.push(`${age.label}.`);

    const capacityGap=runtimeShort&&input.runtimeTrend==='always-short'&&input.selfTest!=='replace'&&!input.repeatBatteryAlarm;
    if(capacityGap)warnings.push('Çalışma süresi baştan beri yetersizse sorun yalnız akü yaşlanması olmayabilir; UPS kapasitesi veya yük hedefi yeniden hesaplanmalıdır.');
    if(runtimeShort&&input.runtimeTrend==='unknown')warnings.push('Çalışma süresi gerekli hedefi karşılamıyor; geçmişe göre düşüş olup olmadığı bilinmiyor.');
    if(input.measuredRuntimeMin==null)warnings.push('Gerçek yükte ölçülen çalışma süresi girilmedi.');
    if(input.runtimeTrend==='stable'&&runtimeShort)warnings.push('Çalışma süresi kararlı fakat hedefin altında; daha büyük akü takmak yerine UPS ve yük kapasitesini yeniden değerlendirin.');

    const hardReplacement=Boolean((input.selfTest==='replace'&&input.fullyCharged)||input.repeatBatteryAlarm||input.outageDrop||(runtimeShort&&input.runtimeTrend==='declined'));
    const preventiveDue=age.due&&!hardReplacement;
    const oldChassis=input.upsAgeYears>=7;
    const exactCandidate=['manufacturer-exact','manufacturer-approved'].includes(input.candidateType)&&input.exactCartridgeVerified&&input.preassembledCartridge&&input.fullSetReplacement;
    const lowRiskUPS=input.upsClass==='desktop'&&!input.externalBatteryPacks&&input.userReplaceable;
    const professionalRequired=blockers.length>0||!input.userReplaceable||input.upsClass!=='desktop'||input.externalBatteryPacks||input.lifeSupport||input.candidateType==='generic-loose';

    let status='monitor';
    let recommendedAction='Üretici bakım planını izleyin';
    let noPurchaseNeeded=false;
    let commercialAllowed=false;
    let alternativeRoute=null;

    if(blockerCodes.includes('physical_hazard')){
      status='stop-use';recommendedAction='Kullanımı durdurun ve yetkili servis çağırın';
    }else if(blockerCodes.length){
      status='service';recommendedAction='Ürün satın almadan önce yetkili servis/uzman doğrulaması';
    }else if(testIncomplete&&!hardReplacement){
      status='test-first';recommendedAction='Tam şarj ve üretici self-test adımlarını tamamlayın';
    }else if(capacityGap||(runtimeShort&&['stable','unknown'].includes(input.runtimeTrend)&&!hardReplacement)){
      status='capacity-review';recommendedAction='UPS kapasitesini ve kritik yükü yeniden hesaplayın';alternativeRoute='/hesaplama/ups-suresi/';
    }else if(hardReplacement&&oldChassis){
      status='compare-unit';recommendedAction='Akü değişimi ile yeni UPS toplam maliyetini karşılaştırın';alternativeRoute='/hesaplama/yedek-guc-maliyet-karsilastirma/';
    }else if(hardReplacement){
      status='replace-cartridge';recommendedAction='Tam modele uygun kartuş/set değişimini planlayın';
      commercialAllowed=Boolean(lowRiskUPS&&exactCandidate&&input.exactModelVerified&&input.supportActive&&input.physicalState==='normal'&&!input.lifeSupport);
    }else if(preventiveDue){
      status='plan-replacement';recommendedAction='Önleyici değişim planı oluşturun; acele satın alma yapmayın';
    }else if(input.selfTest==='pass'&&runtimeMeets&&input.physicalState==='normal'&&!input.repeatBatteryAlarm&&!input.outageDrop){
      status='no-purchase';recommendedAction='Şimdilik akü satın almayın; periyodik testi sürdürün';noPurchaseNeeded=true;
    }else if(age.planning){
      status='monitor';recommendedAction='Çalışma süresini ve alarm geçmişini daha sık izleyin';
    }

    if(status==='replace-cartridge'&&!commercialAllowed){
      warnings.push('Akü değişim ihtiyacı var; ancak tam model, kullanıcı değişimi ve doğrulanmış kartuş/set şartları tamamlanmadan ürün yönlendirmesi açılmaz.');
    }
    if(status==='plan-replacement')warnings.push('Yaş tek başına arızayı kanıtlamaz; self-test, gerçek runtime ve üretici planıyla tarih belirleyin.');
    if(oldChassis&&!hardReplacement)warnings.push('UPS gövdesi 7 yıl ve üzerindedir; bir sonraki akü yatırımından önce fan, röle, kondansatör, destek ve toplam maliyeti değerlendirin.');

    checks.push('UPS’in tam model kodunu ve üretici kullanıcı kılavuzunu doğrulayın.');
    checks.push('Aküyü üreticinin önerdiği süre boyunca tam şarj edin; normal yük bağlıyken self-test çalıştırın.');
    checks.push('Şişme, sızıntı, koku, aşırı ısı veya erimiş bağlantı varsa kullanımı durdurun.');
    checks.push('Aynı seri dizide eski ve yeni akü/kartuş karıştırmayın; üreticinin tam set talimatını izleyin.');
    checks.push('Akü kutuplarını kısa devre etmeyin; takı, metal alet ve uygunsuz bağlantı kullanmayın.');
    checks.push('Eski aküyü evsel çöpe atmayın; yetkili atık veya geri dönüşüm kanalına teslim edin.');

    return {
      input,status,recommendedAction,ageSignal:age.label,runtimeCoveragePct:round(runtimeCoverage),
      runtimeResult:runtimeCoverage==null?'Ölçülmedi':runtimeMeets?'Gerekli süreyi karşılıyor':`${round(runtimeCoverage)}% karşılıyor`,
      chassisSignal:oldChassis?'7 yıl ve üzeri — yeni UPS karşılaştırması gerekli olabilir':'7 yıl altı',
      candidateSignal:input.candidateType==='not-selected'?'Aday kartuş seçilmedi':exactCandidate?'Tam model kartuş/set doğrulandı':input.candidateType==='generic-loose'?'Genel/gevşek akü — otomatik uyum yok':'Uyumluluk doğrulanmadı',
      blockers,blockerCodes,warnings,checks,replacementReasons,
      commercialAllowed,noPurchaseNeeded,professionalRequired,alternativeRoute,
      hardReplacement,preventiveDue,capacityGap,oldChassis
    };
  }

  return {analyze,ageSignals};
});
