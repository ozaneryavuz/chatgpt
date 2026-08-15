(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports){module.exports=api;}
  root.Alo186PowerbankUsbC=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(){
  'use strict';

  const number=(value,name,min,max,optional=false)=>{
    if(optional&&(value===''||value==null))return null;
    const parsed=Number(value);
    if(!Number.isFinite(parsed)||parsed<min||parsed>max)throw new Error(`${name} ${min}–${max} aralığında olmalıdır.`);
    return parsed;
  };
  const enumValue=(value,allowed,fallback)=>allowed.includes(value)?value:fallback;
  const bool=value=>value===true||value==='true'||value===1||value==='1';
  const round=value=>Math.round(value*100)/100;

  function energyWh(mode,wh,mah,voltage,label){
    if(mode==='wh')return number(wh,`${label} enerjisi`,1,1000);
    const capacity=number(mah,`${label} kapasitesi`,100,100000);
    const nominal=number(voltage,`${label} nominal gerilimi`,2.5,30);
    return capacity/1000*nominal;
  }

  function analyze(raw){
    const input={
      deviceType:enumValue(raw.deviceType,['phone','tablet','laptop','router','camera','other'],'phone'),
      deviceEnergyMode:enumValue(raw.deviceEnergyMode,['wh','mah'],'wh'),
      deviceWh:raw.deviceWh,
      deviceMah:raw.deviceMah,
      deviceVoltage:raw.deviceVoltage,
      targetCharges:number(raw.targetCharges,'Hedef tam şarj sayısı',0.25,20),
      deviceMinW:number(raw.deviceMinW,'Cihaz asgari giriş gücü',1,240),
      devicePreferredW:number(raw.devicePreferredW,'Cihaz önerilen/azami giriş gücü',1,240),
      bankEnergyMode:enumValue(raw.bankEnergyMode,['wh','mah'],'mah'),
      bankWh:raw.bankWh,
      bankMah:raw.bankMah,
      cellVoltage:raw.cellVoltage,
      transferEfficiency:number(raw.transferEfficiency,'Toplam aktarım verimi',50,95)/100,
      singlePortW:number(raw.singlePortW,'Tek port çıkış gücü',2,240),
      totalOutputW:number(raw.totalOutputW,'Toplam çıkış gücü',2,400),
      simultaneousDevices:number(raw.simultaneousDevices,'Aynı anda bağlı cihaz sayısı',1,8),
      cableW:number(raw.cableW,'Kablo güç etiketi',2,240),
      ownership:enumValue(raw.ownership,['candidate','owned'],'candidate'),
      capacityLabelVerified:bool(raw.capacityLabelVerified),
      usbPdConfirmed:bool(raw.usbPdConfirmed),
      cableRated:bool(raw.cableRated),
      sharedOutputConfirmed:bool(raw.sharedOutputConfirmed),
      manufacturerInstructionsChecked:bool(raw.manufacturerInstructionsChecked),
      damageFree:bool(raw.damageFree),
      recallChecked:bool(raw.recallChecked),
      medicalDevice:bool(raw.medicalDevice)
    };

    if(input.devicePreferredW<input.deviceMinW)throw new Error('Önerilen/azami cihaz gücü, asgari giriş gücünden küçük olamaz.');
    const deviceWh=energyWh(input.deviceEnergyMode,input.deviceWh,input.deviceMah,input.deviceVoltage,'Cihaz bataryası');
    const bankStoredWh=energyWh(input.bankEnergyMode,input.bankWh,input.bankMah,input.cellVoltage,'Powerbank');
    const usableWh=bankStoredWh*input.transferEfficiency;
    const estimatedCharges=usableWh/deviceWh;
    const requiredStoredWh=deviceWh*input.targetCharges/input.transferEfficiency;
    const requiredMah=requiredStoredWh/(input.bankEnergyMode==='mah'?number(input.cellVoltage,'Powerbank nominal gerilimi',2.5,30):3.7)*1000;
    const sharedBudget=input.totalOutputW/input.simultaneousDevices;
    const negotiatedW=Math.min(input.singlePortW,sharedBudget,input.cableW,input.devicePreferredW);
    const approximateChargeHours=deviceWh/Math.max(negotiatedW,0.1)*1.2;

    const blockers=[];
    const blockerCodes=[];
    const warnings=[];
    const checks=[];
    const block=(code,text)=>{blockerCodes.push(code);blockers.push(text);};

    if(!input.damageFree)block('damage','Şişme, ezilme, çatlak, sıvı izi, aşırı ısınma veya yanık kokusu olan powerbank kullanılmamalı ve şarj edilmemelidir.');
    if(!input.recallChecked)block('recall','Üretici geri çağırma ve güvenlik duyurusu kontrol edilmedi. Tam model doğrulanmadan kullanmayın veya satın almayın.');
    if(input.medicalDevice)block('medical','Tıbbi veya yaşam destek cihazında genel powerbank seçimi yeterli değildir; cihaz üreticisi ve yetkili uzman süreklilik çözümünü doğrulamalıdır.');
    if(estimatedCharges+0.01<input.targetCharges)block('capacity',`Tahmini ${estimatedCharges.toFixed(2)} tam şarj, ${input.targetCharges.toFixed(2)} hedefini karşılamıyor.`);
    if(negotiatedW+0.1<input.deviceMinW)block('power',`Kablo, port ve paylaşımlı çıkış sonrası yaklaşık ${negotiatedW.toFixed(1)} W kalıyor; cihazın ${input.deviceMinW.toFixed(1)} W asgari ihtiyacının altında.`);
    if(input.deviceType==='laptop'&&!input.usbPdConfirmed)block('pd','Dizüstü bilgisayar için USB-C Power Delivery desteği doğrulanmadı. Yalnız USB-C konnektörü bulunması yeterli değildir.');

    if(negotiatedW>=input.deviceMinW&&negotiatedW<input.devicePreferredW)warnings.push(`Yaklaşık ${negotiatedW.toFixed(1)} W ile şarj mümkün olabilir; cihazın ${input.devicePreferredW.toFixed(1)} W önerilen/azami seviyesine göre daha yavaş çalışır veya yük altındayken batarya artmayabilir.`);
    if(!input.capacityLabelVerified)warnings.push('Powerbank üzerindeki Wh, mAh, nominal hücre gerilimi ve port çıkış değerleri tam model etiketinden doğrulanmadı.');
    if(!input.cableRated)warnings.push('Kablonun güç etiketi ve gerekiyorsa e-marker/USB-IF uygunluğu doğrulanmadı. Güçlü adaptör tek başına yeterli değildir.');
    if(input.simultaneousDevices>1&&!input.sharedOutputConfirmed)warnings.push('Birden fazla cihaz bağlandığında toplam gücün portlar arasında nasıl paylaşıldığı üretici kılavuzunda doğrulanmadı.');
    if(!input.manufacturerInstructionsChecked)warnings.push('Cihaz ve powerbank üreticisinin önerilen protokol, port ve kablo bilgileri kontrol edilmedi.');
    if(input.transferEfficiency>0.9)warnings.push('Seçilen aktarım verimi iyimserdir; sıcaklık, kablo, cihaz kullanımı ve dönüşüm kayıpları gerçek şarj sayısını azaltabilir.');
    if(bankStoredWh>100)warnings.push('Powerbank 100 Wh üzerindedir. Uçuşta taşıma kuralları havayolu ve ülkeye göre değişebilir; seyahat öncesi resmî taşıyıcı kurallarını kontrol edin.');

    checks.push(`Hedef için yaklaşık en az ${requiredStoredWh.toFixed(1)} Wh depolanmış enerji gerekir.`);
    checks.push(`Powerbank mAh ile etiketleniyorsa ${input.bankEnergyMode==='mah'?input.cellVoltage:3.7} V varsayımında yaklaşık ${Math.ceil(requiredMah/100)*100} mAh gerekir; gerçek ürünün Wh etiketi daha güvenilir karşılaştırmadır.`);
    checks.push(`Tek cihaz için güç zincirinin dar boğazı yaklaşık ${negotiatedW.toFixed(1)} W: powerbank portu, toplam paylaşımlı çıkış, kablo ve cihaz kabul gücünün en düşüğü.`);
    checks.push('USB-C şekli tek başına hızlı şarj veya dizüstü uyumluluğu kanıtlamaz; USB PD profili, port başına güç ve kablo etiketi birlikte doğrulanmalıdır.');
    checks.push('mAh değerlerini doğrudan telefon mAh değeriyle bölmeyin; önce Wh ve görünür aktarım verimi üzerinden karşılaştırın.');

    let status='compatible';
    if(blockers.length)status='incompatible';
    else if(warnings.length)status='conditional';

    const capabilityCodes=['capacity','power','pd'];
    const capabilityOnly=blockerCodes.length>0&&blockerCodes.every(code=>capabilityCodes.includes(code));
    const verifiedForCommerce=input.capacityLabelVerified&&input.cableRated&&input.manufacturerInstructionsChecked&&input.damageFree&&input.recallChecked&&!input.medicalDevice;
    const lowRiskBand=bankStoredWh<=100&&input.devicePreferredW<=100&&input.simultaneousDevices<=3;
    const candidateRoute=input.ownership==='candidate'&&status!=='incompatible';
    const replacementRoute=input.ownership==='owned'&&capabilityOnly;
    const commercialAllowed=verifiedForCommerce&&lowRiskBand&&(candidateRoute||replacementRoute)&&(input.deviceType!=='laptop'||input.usbPdConfirmed);
    const noPurchaseNeeded=input.ownership==='owned'&&status!=='incompatible'&&estimatedCharges>=input.targetCharges&&negotiatedW>=input.deviceMinW;

    return {
      input,
      deviceWh:round(deviceWh),
      bankStoredWh:round(bankStoredWh),
      usableWh:round(usableWh),
      estimatedCharges:round(estimatedCharges),
      requiredStoredWh:round(requiredStoredWh),
      requiredMah:Math.ceil(requiredMah/100)*100,
      sharedBudgetW:round(sharedBudget),
      negotiatedW:round(negotiatedW),
      approximateChargeHours:round(approximateChargeHours),
      status,
      blockers,
      blockerCodes,
      warnings,
      checks,
      commercialAllowed,
      noPurchaseNeeded
    };
  }

  return {analyze,energyWh};
});