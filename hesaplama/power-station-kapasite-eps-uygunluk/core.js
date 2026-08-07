(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  root.Alo186PowerStationSuitability=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(){
  'use strict';
  const round=(value,digits=2)=>Number(value.toFixed(digits));
  const bool=value=>value===true||value==='true'||value===1||value==='1';
  const enumValue=(value,allowed,fallback)=>allowed.includes(value)?value:fallback;
  const number=(value,name,min,max,optional=false)=>{
    if(optional&&(value===''||value==null))return null;
    const parsed=Number(value);
    if(!Number.isFinite(parsed)||parsed<min||parsed>max)throw new Error(`${name} ${min}–${max} aralığında olmalıdır.`);
    return parsed;
  };
  const capacityClasses=[300,500,750,1000,1500,2000,3000,5000,10000];
  const nextCapacity=value=>capacityClasses.find(item=>item>=value)||null;

  function analyze(raw){
    const input={
      loadType:enumValue(raw.loadType,['router','electronics','lighting','fridge','motor','resistive','server','medical','fixed','ev'],'electronics'),
      ownership:enumValue(raw.ownership,['candidate','owned'],'candidate'),
      continuousPowerW:number(raw.continuousPowerW,'Sürekli yük',1,10000),
      surgePowerW:number(raw.surgePowerW,'Kalkış/tepe yükü',1,30000),
      targetHours:number(raw.targetHours,'Hedef çalışma süresi',0.1,72),
      capacityWh:number(raw.capacityWh,'Etiket kapasitesi',100,20000),
      acContinuousW:number(raw.acContinuousW,'AC sürekli güç',100,15000),
      acSurgeW:number(raw.acSurgeW,'AC tepe güç',100,30000),
      efficiency:number(raw.efficiency,'AC dönüşüm verimi',0.5,0.98),
      reservePct:number(raw.reservePct,'Bırakılacak rezerv',0,50),
      transferRequired:bool(raw.transferRequired),
      requiredTransferMs:number(raw.requiredTransferMs,'Yükün izin verdiği geçiş süresi',0,1000,true),
      transferMs:number(raw.transferMs,'Ürünün geçiş süresi',0,1000,true),
      bypassPowerW:number(raw.bypassPowerW,'Bypass gücü',100,15000,true),
      epsSupported:bool(raw.epsSupported),
      pureSine:bool(raw.pureSine),
      acTimeoutDisable:bool(raw.acTimeoutDisable),
      labelVerified:bool(raw.labelVerified),
      manufacturerLoadApproved:bool(raw.manufacturerLoadApproved),
      damageFree:bool(raw.damageFree),
      indoorDryVentilated:bool(raw.indoorDryVentilated),
      directConnection:bool(raw.directConnection),
      needsEarth:bool(raw.needsEarth),
      earthVerified:bool(raw.earthVerified),
      unattendedUse:bool(raw.unattendedUse)
    };
    if(input.surgePowerW<input.continuousPowerW)throw new Error('Kalkış/tepe gücü sürekli güçten küçük olamaz.');
    if(input.acSurgeW<input.acContinuousW)throw new Error('Ürünün tepe gücü sürekli gücünden küçük olamaz.');

    const usableFraction=input.efficiency*(1-input.reservePct/100);
    if(usableFraction<=0)throw new Error('Verim ve rezerv birlikte kullanılabilir enerjiyi sıfırlamamalıdır.');
    const usableWh=input.capacityWh*usableFraction;
    const estimatedRuntimeHours=usableWh/input.continuousPowerW;
    const requiredCapacityWh=(input.continuousPowerW*input.targetHours)/usableFraction;
    const recommendedCapacityWh=nextCapacity(requiredCapacityWh);
    const powerMarginPct=(input.acContinuousW-input.continuousPowerW)/input.acContinuousW*100;
    const surgeMarginPct=(input.acSurgeW-input.surgePowerW)/input.acSurgeW*100;
    const blockers=[],blockerCodes=[],warnings=[],checks=[];
    const block=(code,text)=>{blockerCodes.push(code);blockers.push(text);};
    const pureSineRequired=!['lighting','resistive'].includes(input.loadType);

    if(input.loadType==='medical')block('medical','Tıbbi veya yaşam destek cihazı için genel power station yönlendirmesi yapılmaz; üretici ve sağlık ekibi onaylı güç sürekliliği gerekir.');
    if(input.loadType==='ev')block('ev','Elektrikli araç şarjı taşınabilir power station ürün rotasına uygun değildir.');
    if(input.loadType==='fixed')block('fixed','Sabit tesisat veya pano devresi taşınabilir prizli ürünle beslenmemelidir; uygun transfer ve proje gerekir.');
    if(input.loadType==='server')block('server','Sunucu ve veri kaybına hassas iş istasyonu için 0 ms veya üretici tarafından doğrulanmış UPS mimarisi gerekir; genel EPS yeterli kabul edilmez.');
    if(!input.damageFree)block('damage','Cihazda şişme, çatlak, koku, sıvı teması veya olağandışı ısı varsa kullanmayın.');
    if(!input.indoorDryVentilated)block('environment','Kuru, serin ve havalandırılan güvenli ortam doğrulanmadı.');
    if(!input.directConnection)block('connection','Uzatma, çoklayıcı, erkek–erkek kablo veya bina tesisatına geri besleme kullanılmamalıdır.');
    if(input.needsEarth&&!input.earthVerified)block('earth','Topraklama gerektiren yük için çıkış ve koruma iletkeni düzeni tam modelde doğrulanmadı.');
    if(input.continuousPowerW>input.acContinuousW+1e-9)block('continuous_power','Sürekli yük ürünün AC sürekli güç sınırını aşıyor.');
    if(input.surgePowerW>input.acSurgeW+1e-9)block('surge_power','Kalkış/tepe yükü ürünün belirtilen tepe güç sınırını aşıyor.');
    if(pureSineRequired&&!input.pureSine)block('waveform','Bu yük sınıfında saf sinüs çıkış doğrulanmadan uygunluk verilemez.');
    if(estimatedRuntimeHours+1e-9<input.targetHours)block('runtime_short','Girilen kapasite, verim ve rezervle hedef çalışma süresini karşılamıyor.');

    if(input.transferRequired){
      if(!input.epsSupported)block('eps_missing','Otomatik geçiş gerekiyor ancak EPS/UPS işlevi doğrulanmadı.');
      if(input.requiredTransferMs==null)warnings.push('Yükün tolere ettiği azami geçiş süresi bilinmiyor.');
      if(input.transferMs==null)warnings.push('Power station geçiş süresi tam model kılavuzundan doğrulanmadı.');
      if(input.requiredTransferMs!=null&&input.transferMs!=null&&input.transferMs>input.requiredTransferMs)block('transfer_slow','Ürünün geçiş süresi yükün izin verdiği süreden uzun.');
      if(input.bypassPowerW==null)warnings.push('Şebekeye bağlı EPS kullanımında bypass gücü doğrulanmadı.');
      else if(input.continuousPowerW>input.bypassPowerW+1e-9)block('bypass_power','Yük, ürünün bypass güç sınırını aşıyor.');
    }
    if(input.loadType==='fridge'&&!input.acTimeoutDisable)block('ac_timeout','Aralıklı kompresör yükünde AC çıkışın zaman aşımıyla kapanmayacağı doğrulanmadı.');
    if(['fridge','motor'].includes(input.loadType)&&!input.manufacturerLoadApproved)block('load_approval','Motor/kompresör yükünün tam ürün modeliyle kalkış uyumu üretici tarafından doğrulanmadı.');
    else if(!input.manufacturerLoadApproved)warnings.push('Tam yük türünün ürün kılavuzundaki uyumluluğu doğrulanmadı.');
    if(!input.labelVerified)warnings.push('Kapasite, sürekli/tepe güç, dalga biçimi ve geçiş bilgileri tam model kılavuzundan doğrulanmadı.');
    if(input.loadType==='resistive'&&input.unattendedUse)block('unattended_heat','Isıtıcı, kettle veya ütü gibi rezistif yükler gözetimsiz power station kullanımına yönlendirilmez.');
    if(input.reservePct<10)warnings.push('Yüzde 10’dan düşük rezerv, yaşlanma ve soğuk hava etkisini yeterince karşılamayabilir.');

    checks.push('Etiket Wh kapasitesinin tamamının AC çıkışta kullanılamadığını dikkate alın.');
    checks.push('AC sürekli ve tepe gücü ile yükün gerçek kalkış davranışını aynı anda doğrulayın.');
    checks.push('Cihazı yanıcı maddelerden, su ve ısı kaynaklarından uzak; havalandırılan bir yerde kullanın.');
    if(input.transferRequired)checks.push('EPS geçişini gerçek yükle kontrollü test edin; 0 ms UPS gerektiren cihazlarda kullanmayın.');
    if(input.loadType==='fridge')checks.push('AC çıkış otomatik kapanma süresini kapatın ve batarya seviyesini düzenli kontrol edin.');

    const status=blockers.length?'incompatible':warnings.length?'conditional':'compatible';
    const allVerified=input.labelVerified&&input.manufacturerLoadApproved&&input.damageFree&&input.indoorDryVentilated&&input.directConnection&&(!input.needsEarth||input.earthVerified)&&(!pureSineRequired||input.pureSine);
    const transferMatch=!input.transferRequired||(input.epsSupported&&input.requiredTransferMs!=null&&input.transferMs!=null&&input.transferMs<=input.requiredTransferMs&&input.bypassPowerW!=null&&input.bypassPowerW>=input.continuousPowerW);
    const lowRisk=['router','electronics','lighting','fridge'].includes(input.loadType)&&input.continuousPowerW<=1200&&input.capacityWh<=3000&&!input.unattendedUse;
    const noPurchaseNeeded=input.ownership==='owned'&&status==='compatible';
    const commercialAllowed=Boolean(input.ownership==='candidate'&&status==='compatible'&&allVerified&&transferMatch&&lowRisk);
    const professionalRequired=['server','medical','fixed','ev','motor'].includes(input.loadType)||blockerCodes.includes('earth')||blockerCodes.includes('connection');

    return {
      input,status,blockers,blockerCodes,warnings,checks,pureSineRequired,
      usableWh:round(usableWh),estimatedRuntimeHours:round(estimatedRuntimeHours),requiredCapacityWh:round(requiredCapacityWh),recommendedCapacityWh,
      powerMarginPct:round(powerMarginPct,1),surgeMarginPct:round(surgeMarginPct,1),usableFraction:round(usableFraction,3),
      noPurchaseNeeded,commercialAllowed,professionalRequired,lowRisk,transferMatch
    };
  }

  return {analyze,nextCapacity};
});
