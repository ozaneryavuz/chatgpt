(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports){module.exports=api;}
  root.AloCalc=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(){
  const standardSections=[1.5,2.5,4,6,10,16,25,35,50,70,95,120,150,185,240,300];
  function n(v,d=0){const x=Number(v);return Number.isFinite(x)?x:d}
  function positive(v,name){const x=n(v);if(!(x>0))throw new Error((name||'Değer')+' sıfırdan büyük olmalıdır.');return x}
  function ratio(v,name){const x=n(v);if(!(x>0&&x<=1))throw new Error((name||'Oran')+' 0 ile 1 arasında olmalıdır.');return x}
  function round(v,d=2){const p=10**d;return Math.round((v+Number.EPSILON)*p)/p}
  function upsRuntime({loadW,batteryWh,efficiency=.88,usableDepth=.8,aging=.9}){
    loadW=positive(loadW,'Yük');batteryWh=positive(batteryWh,'Batarya kapasitesi');
    efficiency=ratio(efficiency,'Verim');usableDepth=ratio(usableDepth,'Kullanılabilir deşarj');
    aging=ratio(aging,'Yaşlanma katsayısı');
    return {runtimeHours:batteryWh*efficiency*usableDepth*aging/loadW,usableWh:batteryWh*efficiency*usableDepth*aging};
  }
  function requiredBattery({loadW,hours,efficiency=.88,usableDepth=.8,aging=.9,reserve=.2}){
    loadW=positive(loadW,'Yük');hours=positive(hours,'Süre');efficiency=ratio(efficiency,'Verim');
    usableDepth=ratio(usableDepth,'Kullanılabilir deşarj');aging=ratio(aging,'Yaşlanma katsayısı');
    reserve=Math.max(0,n(reserve,.2));
    const base=loadW*hours/(efficiency*usableDepth*aging);
    return {requiredNominalWh:base*(1+reserve),baseNominalWh:base};
  }
  function evCharge({batteryKWh,currentSoc,targetSoc,chargerKW,efficiency=.9,unitPrice=0}){
    batteryKWh=positive(batteryKWh,'Batarya');chargerKW=positive(chargerKW,'Şarj gücü');
    currentSoc=n(currentSoc);targetSoc=n(targetSoc);
    if(currentSoc<0||currentSoc>=100||targetSoc<=currentSoc||targetSoc>100)throw new Error('SOC değerlerini kontrol edin.');
    efficiency=ratio(efficiency,'Verim');unitPrice=Math.max(0,n(unitPrice));
    const batteryEnergy=batteryKWh*(targetSoc-currentSoc)/100;
    const gridEnergy=batteryEnergy/efficiency;
    return {batteryEnergyKWh:batteryEnergy,gridEnergyKWh:gridEnergy,hours:gridEnergy/chargerKW,cost:gridEnergy*unitPrice};
  }
  function conductorRho(material,tempC=20){
    const isAl=String(material).toLowerCase().startsWith('al');
    const rho20=isAl?0.0282:0.0175;
    const alpha=isAl?0.00403:0.00393;
    return rho20*(1+alpha*(n(tempC,20)-20));
  }
  function voltageDrop({system='single',material='copper',lengthM,currentA,sectionMM2,voltageV,tempC=20}){
    lengthM=positive(lengthM,'Uzunluk');currentA=positive(currentA,'Akım');sectionMM2=positive(sectionMM2,'Kesit');voltageV=positive(voltageV,'Gerilim');
    const rho=conductorRho(material,tempC);
    const factor=system==='three'?Math.sqrt(3):2;
    const dropV=factor*currentA*lengthM*rho/sectionMM2;
    return {dropV,dropPercent:dropV/voltageV*100,rho};
  }
  function requiredSection({system='single',material='copper',lengthM,currentA,voltageV,tempC=20,maxDropPercent=3}){
    maxDropPercent=positive(maxDropPercent,'İzin verilen düşüm');
    for(const s of standardSections){
      const r=voltageDrop({system,material,lengthM,currentA,sectionMM2:s,voltageV,tempC});
      if(r.dropPercent<=maxDropPercent)return {sectionMM2:s,...r};
    }
    const last=standardSections[standardSections.length-1];
    return {sectionMM2:null,...voltageDrop({system,material,lengthM,currentA,sectionMM2:last,voltageV,tempC})};
  }
  function chargerCurrent({chargerKW,phase='single',voltageSingle=230,voltageThree=400,pf=.99}){
    chargerKW=positive(chargerKW,'Şarj gücü');pf=ratio(pf,'Güç faktörü');
    return phase==='three'?chargerKW*1000/(Math.sqrt(3)*voltageThree*pf):chargerKW*1000/(voltageSingle*pf);
  }
  return {n,round,upsRuntime,requiredBattery,evCharge,voltageDrop,requiredSection,chargerCurrent,standardSections};
});
