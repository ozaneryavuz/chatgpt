(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports){module.exports=api;}
  root.Alo186SolarInputCompatibility=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(){
  'use strict';
  const clamp=(value,min,max)=>Math.min(max,Math.max(min,value));
  const number=(value,name,min,max,optional=false)=>{
    if(optional&&(value===''||value==null))return null;
    const parsed=Number(value);
    if(!Number.isFinite(parsed)||parsed<min||parsed>max)throw new Error(`${name} ${min}–${max} aralığında olmalıdır.`);
    return parsed;
  };
  const integer=(value,name,min,max)=>{
    const parsed=number(value,name,min,max);
    if(!Number.isInteger(parsed))throw new Error(`${name} tam sayı olmalıdır.`);
    return parsed;
  };
  function analyze(raw){
    const input={
      panelPower:number(raw.panelPower,'Panel gücü',10,1000),
      panelVoc:number(raw.panelVoc,'Panel Voc',1,250),
      panelVmp:number(raw.panelVmp,'Panel Vmp',1,250),
      panelIsc:number(raw.panelIsc,'Panel Isc',0.1,40),
      panelImp:number(raw.panelImp,'Panel Imp',0.1,40),
      vocTempCoeff:number(raw.vocTempCoeff,'Voc sıcaklık katsayısı',0.05,1),
      seriesCount:integer(raw.seriesCount,'Seri panel sayısı',1,12),
      parallelCount:integer(raw.parallelCount,'Paralel dizi sayısı',1,8),
      minTemp:number(raw.minTemp,'En düşük hücre/ortam sıcaklığı',-40,25),
      mpptMinV:number(raw.mpptMinV,'MPPT alt gerilim sınırı',1,250),
      mpptMaxV:number(raw.mpptMaxV,'MPPT üst çalışma gerilimi',2,300),
      absoluteMaxVoc:number(raw.absoluteMaxVoc,'Mutlak azami PV gerilimi',2,350),
      maxInputCurrent:number(raw.maxInputCurrent,'Azami PV çalışma akımı',0.1,100),
      maxShortCircuitCurrent:number(raw.maxShortCircuitCurrent,'Azami kısa devre akımı',0.1,150,true),
      maxInputPower:number(raw.maxInputPower,'Azami PV giriş gücü',10,10000),
      stationCapacity:number(raw.stationCapacity,'Power station kapasitesi',50,10000,true),
      currentSoc:number(raw.currentSoc,'Başlangıç doluluk oranı',0,100,true),
      targetSoc:number(raw.targetSoc,'Hedef doluluk oranı',1,100,true),
      derating:number(raw.derating,'Gerçek koşul katsayısı',0.5,0.95),
      application:['portable','vehicle','fixed','unknown'].includes(raw.application)?raw.application:'unknown',
      manualVerified:Boolean(raw.manualVerified),
      connectorKnown:Boolean(raw.connectorKnown),
      factoryCable:Boolean(raw.factoryCable)
    };
    if(input.panelVmp>=input.panelVoc)throw new Error('Panel Vmp değeri Voc değerinden küçük olmalıdır.');
    if(input.panelImp>input.panelIsc)throw new Error('Panel Imp değeri Isc değerini aşmamalıdır.');
    if(input.mpptMinV>=input.mpptMaxV)throw new Error('MPPT alt sınırı üst çalışma sınırından küçük olmalıdır.');
    if(input.mpptMaxV>input.absoluteMaxVoc)throw new Error('MPPT çalışma üst sınırı mutlak azami Voc değerini aşamaz.');
    const chargeInputs=[input.stationCapacity,input.currentSoc,input.targetSoc];
    const chargeInputCount=chargeInputs.filter(value=>value!=null).length;
    if(chargeInputCount!==0&&chargeInputCount!==3)throw new Error('Yaklaşık şarj süresi için kapasite, başlangıç ve hedef doluluk birlikte girilmelidir.');
    if(input.currentSoc!=null&&input.targetSoc<=input.currentSoc)throw new Error('Hedef doluluk başlangıç doluluğundan büyük olmalıdır.');

    const coldRise=1+(input.vocTempCoeff/100)*Math.max(0,25-input.minTemp);
    const arrayVocStc=input.panelVoc*input.seriesCount;
    const coldVoc=arrayVocStc*coldRise;
    const arrayVmp=input.panelVmp*input.seriesCount;
    const arrayIsc=input.panelIsc*input.parallelCount;
    const arrayImp=input.panelImp*input.parallelCount;
    const panelCount=input.seriesCount*input.parallelCount;
    const arrayPower=input.panelPower*panelCount;
    const currentLimitedPower=arrayVmp*Math.min(arrayImp,input.maxInputCurrent);
    const estimatedAcceptedPower=Math.max(0,Math.min(arrayPower,input.maxInputPower,currentLimitedPower));
    const acceptedRatio=arrayPower>0?estimatedAcceptedPower/arrayPower:0;

    const blockers=[],warnings=[],checks=[];
    if(coldVoc>=input.absoluteMaxVoc)blockers.push(`Soğuk koşul Voc değeri ${coldVoc.toFixed(1)} V ile cihazın ${input.absoluteMaxVoc.toFixed(1)} V mutlak sınırına ulaşıyor veya aşıyor.`);
    else if(coldVoc>input.absoluteMaxVoc*0.95)warnings.push('Soğuk koşul Voc değeri mutlak sınıra çok yakın; daha geniş mühendislik payı gerekir.');
    if(arrayVmp<input.mpptMinV)blockers.push(`Dizi Vmp değeri ${arrayVmp.toFixed(1)} V ile MPPT alt sınırı ${input.mpptMinV.toFixed(1)} V altında.`);
    if(arrayVmp>input.mpptMaxV)blockers.push(`Dizi Vmp değeri ${arrayVmp.toFixed(1)} V ile MPPT çalışma üst sınırı ${input.mpptMaxV.toFixed(1)} V üzerinde.`);
    if(input.maxShortCircuitCurrent!=null&&arrayIsc>input.maxShortCircuitCurrent)blockers.push(`Toplam Isc ${arrayIsc.toFixed(1)} A, belirtilen ${input.maxShortCircuitCurrent.toFixed(1)} A kısa devre akımı sınırını aşıyor.`);
    if(arrayImp>input.maxInputCurrent)warnings.push(`Toplam Imp ${arrayImp.toFixed(1)} A, cihazın ${input.maxInputCurrent.toFixed(1)} A giriş akımını aşıyor; bazı cihazlar akımı sınırlar, bazıları bu diziyi kabul etmez. Tam model kılavuzu gerekir.`);
    if(arrayPower>input.maxInputPower)warnings.push(`Panel etiket toplamı ${Math.round(arrayPower)} W, cihazın ${Math.round(input.maxInputPower)} W PV giriş sınırını aşıyor; uyumlu olsa bile güç kırpılması olabilir.`);
    if(!input.manualVerified)warnings.push('Power station veya MPPT cihazının tam model kılavuzundaki PV giriş değerleri doğrulanmadı.');
    if(!input.connectorKnown)warnings.push('Konnektör tipi ve polarite doğrulanmadı. Aynı görünen DC konnektörler farklı polarite veya pin düzeni kullanabilir.');
    if(!input.factoryCable)warnings.push('Fabrika kablosu/adaptörü dışında uzatma, dönüştürücü veya ek bağlantı kullanılıyor; kablo akımı, polarite ve temas kaybı ayrıca doğrulanmalıdır.');
    if(input.application!=='portable')warnings.push('Araç/karavan, çatı veya sabit tesisat senaryosu taşınabilir tüketici ürünü sınırını aşar; koruma, kablo, ayırma ve topraklama tasarımı gerekir.');

    let status='compatible';
    if(blockers.length)status='incompatible';
    else if(warnings.length)status='conditional';

    const energyNeed=input.stationCapacity!=null?input.stationCapacity*(input.targetSoc-input.currentSoc)/100:null;
    const idealHours=energyNeed!=null&&estimatedAcceptedPower>0?energyNeed/(estimatedAcceptedPower*input.derating):null;
    const professionalRequired=input.application!=='portable'||input.seriesCount>2||input.parallelCount>2||coldVoc>60||arrayPower>800||status==='incompatible';
    const commercialAllowed=status==='compatible'&&input.application==='portable'&&input.manualVerified&&input.connectorKnown&&input.factoryCable&&input.seriesCount<=2&&input.parallelCount<=2&&coldVoc<=60&&arrayPower<=800;

    checks.push('Panel etiketindeki Voc, Vmp, Isc, Imp ve sıcaklık katsayısını tam model veri sayfasından doğrulayın.');
    checks.push('Cihazın MPPT çalışma aralığı, mutlak azami Voc, akım ve güç sınırlarını aynı PV giriş portu için doğrulayın.');
    checks.push('Seri bağlantıda gerilimlerin, paralel bağlantıda akımların toplandığını dikkate alın.');
    checks.push('Konnektör, polarite, kablo akımı ve üreticinin izin verdiği seri/paralel mimariyi kontrol edin.');
    checks.push('Soğuk havada Voc yükseldiği için yalnız 25 °C etiket değerine göre sınırda tasarım yapmayın.');
    if(arrayPower>input.maxInputPower||arrayImp>input.maxInputCurrent)checks.push('Aşırı panelleme veya akım sınırlama davranışını üreticinin tam model kılavuzunda açıkça doğrulayın.');

    return {
      input,
      panelCount,
      arrayVocStc,
      coldVoc,
      arrayVmp,
      arrayIsc,
      arrayImp,
      arrayPower,
      estimatedAcceptedPower,
      acceptedRatio:clamp(acceptedRatio,0,1),
      energyNeed,
      idealHours,
      status,
      blockers,
      warnings,
      checks,
      professionalRequired,
      commercialAllowed
    };
  }
  return {analyze};
});
