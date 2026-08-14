(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports){module.exports=api;}
  root.Alo186EvHomeCharge=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(){
  'use strict';
  const SQRT3=Math.sqrt(3);
  const SINGLE_V=230;
  const THREE_V=400;
  const number=(value,name,min,max,optional=false)=>{
    if(optional&&(value===''||value==null))return null;
    const parsed=Number(value);
    if(!Number.isFinite(parsed)||parsed<min||parsed>max)throw new Error(`${name} ${min}–${max} aralığında olmalıdır.`);
    return parsed;
  };
  const bool=value=>value===true||value==='true'||value===1||value==='1';
  const enumValue=(value,allowed,fallback)=>allowed.includes(value)?value:fallback;
  const round=(value,digits=2)=>Number(value.toFixed(digits));

  function commonPowerClass(kw){
    const classes=[2.3,3.7,7.4,11,22];
    const match=classes.find(value=>value+1e-9>=kw);
    return match||null;
  }

  function analyze(raw){
    const input={
      usage:enumValue(raw.usage,['private','shared','commercial'],'private'),
      ownership:enumValue(raw.ownership,['candidate','owned'],'candidate'),
      phase:enumValue(raw.phase,['single','three'],'single'),
      batteryKwh:number(raw.batteryKwh,'Batarya kapasitesi',5,250),
      currentSoc:number(raw.currentSoc,'Başlangıç SOC',0,99),
      targetSoc:number(raw.targetSoc,'Hedef SOC',1,100),
      planningEfficiencyPct:number(raw.planningEfficiencyPct,'Planlama verimi',70,100),
      targetHours:number(raw.targetHours,'Hedef süre',0.5,48),
      vehicleAcMaxKw:number(raw.vehicleAcMaxKw,'Araç AC şarj üst sınırı',0.5,43),
      evseMaxKw:number(raw.evseMaxKw,'EVSE azami AC gücü',0.5,43),
      installationMaxKw:number(raw.installationMaxKw,'Doğrulanmış tesisat şarj üst sınırı',0.5,43),
      connectorVerified:bool(raw.connectorVerified),
      vehicleDocsVerified:bool(raw.vehicleDocsVerified),
      evseDocsVerified:bool(raw.evseDocsVerified),
      installationPowerVerified:bool(raw.installationPowerVerified),
      dedicatedCircuit:bool(raw.dedicatedCircuit),
      protectionCoordinationVerified:bool(raw.protectionCoordinationVerified),
      residualProtectionVerified:bool(raw.residualProtectionVerified),
      earthVerified:bool(raw.earthVerified),
      commissioningPassed:bool(raw.commissioningPassed),
      damageFree:bool(raw.damageFree),
      noRecurringTrips:bool(raw.noRecurringTrips),
      directEvseConnection:bool(raw.directEvseConnection),
      loadManagementRequired:bool(raw.loadManagementRequired),
      loadManagementVerified:bool(raw.loadManagementVerified),
      advancedEnergySystem:bool(raw.advancedEnergySystem),
      existingSafeSolutionAdequate:bool(raw.existingSafeSolutionAdequate)
    };

    if(input.targetSoc<=input.currentSoc)throw new Error('Hedef SOC, başlangıç SOC değerinden büyük olmalıdır.');

    const efficiency=input.planningEfficiencyPct/100;
    const batteryEnergyKwh=input.batteryKwh*(input.targetSoc-input.currentSoc)/100;
    const gridEnergyKwh=batteryEnergyKwh/efficiency;
    const siteVehicleCeilingKw=Math.min(input.vehicleAcMaxKw,input.installationMaxKw);
    const effectivePowerKw=Math.min(siteVehicleCeilingKw,input.evseMaxKw);
    const chargeTimeHours=gridEnergyKwh/effectivePowerKw;
    const requiredEffectiveKw=gridEnergyKwh/input.targetHours;
    const targetFeasibleByVehicleAndSite=requiredEffectiveKw<=siteVehicleCeilingKw+1e-9;
    const candidateMeetsTime=targetFeasibleByVehicleAndSite&&input.evseMaxKw+1e-9>=requiredEffectiveKw;
    const candidateWithinUsefulCeiling=input.evseMaxKw<=siteVehicleCeilingKw*1.05+1e-9;
    const approximateCurrentA=input.phase==='three'
      ? (effectivePowerKw*1000)/(SQRT3*THREE_V)
      : (effectivePowerKw*1000)/SINGLE_V;
    const usefulCeilingKw=siteVehicleCeilingKw;
    const usefulClassKw=commonPowerClass(Math.min(requiredEffectiveKw,usefulCeilingKw));

    const bottlenecks=[];
    const epsilon=0.01;
    if(Math.abs(input.vehicleAcMaxKw-effectivePowerKw)<epsilon)bottlenecks.push('Araç içi AC şarj cihazı');
    if(Math.abs(input.evseMaxKw-effectivePowerKw)<epsilon)bottlenecks.push('EVSE / wallbox');
    if(Math.abs(input.installationMaxKw-effectivePowerKw)<epsilon)bottlenecks.push('Doğrulanmış tesisat şarj üst sınırı');

    const blockers=[], blockerCodes=[], warnings=[], checks=[];
    const block=(code,text)=>{blockerCodes.push(code);blockers.push(text);};

    if(input.usage==='commercial')block('commercial','Filo, otel, işyeri ve ticari şarj için talep gücü, eşzamanlılık, yük yönetimi ve proje koordinasyonu gerekir; tüketici tipi wallbox yönlendirmesi açılmaz.');
    if(input.usage==='shared')block('shared','Apartman/ortak otopark senaryosunda ortak alan yetkilendirmesi, sayaçlama, yük yönetimi ve proje koşulları birlikte değerlendirilmelidir.');
    if(input.advancedEnergySystem)block('advanced','PV, batarya depolama, V2H/V2G veya çift yönlü enerji sistemi standart ev wallbox seçicisinden ayrılır; profesyonel sistem tasarımı gerekir.');
    if(!input.damageFree)block('damage','Yanık kokusu, erime, su/nem, hasarlı kablo/konnektör veya olağandışı ısınma varsa şarjı durdurun ve ürün seçimine ilerlemeyin.');
    if(!input.noRecurringTrips)block('trips','MCB/RCD/RCBO veya ana koruma tekrar tekrar açıyorsa daha büyük koruma ya da yeni wallbox seçmeden önce kök neden ölçümle ayrılmalıdır.');
    if(!input.directEvseConnection)block('extension','EV şarjı uzatma, çoklayıcı, genel adaptör veya zincir bağlantı üzerinden değerlendirilmez.');
    if(!input.dedicatedCircuit)block('circuit','EVSE için ayrılmış ve profesyonel olarak doğrulanmış besleme devresi kanıtlanmadı.');
    if(!input.earthVerified)block('earth','PE/topraklama ve koruma düzeni profesyonel olarak doğrulanmadı.');
    if(!input.residualProtectionVerified)block('residual','Tam EVSE modeline uygun RCD/RDC-DD veya eşdeğer artık akım koruma düzeni doğrulanmadı.');
    if(!input.protectionCoordinationVerified)block('protection','Kablo, koruma cihazı ve EVSE koordinasyonu yetkin elektrikçi tarafından doğrulanmadı.');
    if(input.loadManagementRequired&&!input.loadManagementVerified)block('load_management','Bina bağlantı gücü için yük yönetimi gerekli ancak CT/sayaç/fail-safe davranışı doğrulanmadı.');

    if(!input.vehicleDocsVerified)warnings.push('Araç üreticisinin AC şarj üst sınırı tam model dokümanından doğrulanmadı.');
    if(!input.evseDocsVerified)warnings.push('EVSE/wallbox azami güç, bağlantı ve koruma şartları tam model dokümanından doğrulanmadı.');
    if(!input.installationPowerVerified)warnings.push('Tesisat için girilen azami şarj gücü yetkin elektrikçi/proje kaydıyla doğrulanmadı.');
    if(!input.connectorVerified)warnings.push('Araç–EVSE konnektör uyumu tam modelde doğrulanmadı.');
    if(!input.commissioningPassed)warnings.push('Kurulum devreye alma ve gerçek şarj testi başarıyla tamamlanmadı.');
    if(input.planningEfficiencyPct===90)warnings.push('%90 verim yalnız ayarlanabilir ALO186 planlama varsayımıdır; araç/EVSE üreticisinin garanti ettiği sabit değer değildir.');

    if(input.evseMaxKw>input.vehicleAcMaxKw*1.05){
      warnings.push(`EVSE gücü aracın ${round(input.vehicleAcMaxKw,1)} kW AC sınırından yüksek; bu araçta daha büyük wallbox tek başına AC şarjı hızlandırmayabilir.`);
    }
    if(input.evseMaxKw>input.installationMaxKw*1.05){
      warnings.push(`EVSE gücü doğrulanmış tesisat sınırından yüksek; kullanılabilir güç yaklaşık ${round(input.installationMaxKw,1)} kW ile sınırlanır.`);
    }
    if(!targetFeasibleByVehicleAndSite){
      warnings.push(`Hedef süre için yaklaşık ${round(requiredEffectiveKw,1)} kW etkili AC güç gerekir; araç + tesisat tavanı ${round(siteVehicleCeilingKw,1)} kW olduğundan yalnız daha güçlü wallbox bu hedefi sağlayamaz.`);
    } else if(!candidateMeetsTime){
      warnings.push(`Hedef süre için yaklaşık ${round(requiredEffectiveKw,1)} kW etkili AC güç gerekir; değerlendirilen EVSE ${round(input.evseMaxKw,1)} kW ile bu hedefi karşılamıyor.`);
    }

    checks.push('Araç AC şarj sınırını ve konnektör tipini tam model kullanım kılavuzundan doğrulayın.');
    checks.push('EVSE kurulum kılavuzundaki besleme, koruma ve bağlantı şartlarını yetkin elektrikçiyle doğrulayın.');
    checks.push('Kablo kesiti veya sigorta değerini bu yaklaşık akım hesabından seçmeyin; tesis yöntemi, sıcaklık, gerilim düşümü, kısa devre ve üretici koordinasyonu ayrıca projelendirilir.');
    checks.push('Şarj sırasında konnektör, kablo, EVSE ve pano bağlantılarında olağandışı ısı veya tekrar eden açma görülürse kullanımı durdurun.');

    const evidenceVerified=input.connectorVerified&&input.vehicleDocsVerified&&input.evseDocsVerified&&input.installationPowerVerified&&input.dedicatedCircuit&&input.protectionCoordinationVerified&&input.residualProtectionVerified&&input.earthVerified&&input.commissioningPassed&&input.damageFree&&input.noRecurringTrips&&input.directEvseConnection&&(!input.loadManagementRequired||input.loadManagementVerified);
    const hardSafe=blockers.length===0;
    const status=!hardSafe?'incompatible':warnings.length?'conditional':'compatible';
    const expectationFit=targetFeasibleByVehicleAndSite&&candidateMeetsTime;
    const noPurchaseNeeded=Boolean(
      input.existingSafeSolutionAdequate ||
      (input.ownership==='owned'&&hardSafe&&evidenceVerified&&chargeTimeHours<=input.targetHours+1e-9) ||
      (input.ownership==='candidate'&&input.evseMaxKw>input.vehicleAcMaxKw*1.05&&input.installationMaxKw>=input.vehicleAcMaxKw&&input.existingSafeSolutionAdequate)
    );
    const commercialAllowed=Boolean(
      input.usage==='private'&&
      input.ownership==='candidate'&&
      !input.advancedEnergySystem&&
      !input.existingSafeSolutionAdequate&&
      hardSafe&&evidenceVerified&&expectationFit&&candidateWithinUsefulCeiling
    );
    const professionalRequired=Boolean(blockers.length||input.usage!=='private'||input.advancedEnergySystem||!evidenceVerified);

    return {
      input,status,blockers,blockerCodes,warnings,checks,
      batteryEnergyKwh:round(batteryEnergyKwh,2),
      gridEnergyKwh:round(gridEnergyKwh,2),
      effectivePowerKw:round(effectivePowerKw,2),
      chargeTimeHours:round(chargeTimeHours,2),
      requiredEffectiveKw:round(requiredEffectiveKw,2),
      usefulCeilingKw:round(usefulCeilingKw,2),
      usefulClassKw,
      approximateCurrentA:round(approximateCurrentA,1),
      bottlenecks,
      targetFeasibleByVehicleAndSite,candidateMeetsTime,candidateWithinUsefulCeiling,evidenceVerified,
      noPurchaseNeeded,commercialAllowed,professionalRequired,
      affiliateQuery:'elektrikli araç şarj istasyonu wallbox AC EVSE'
    };
  }

  return {analyze,commonPowerClass};
});
