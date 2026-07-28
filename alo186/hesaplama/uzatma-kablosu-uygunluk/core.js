(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports){module.exports=api;}
  root.Alo186ExtensionLeadCompatibility=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(){
  'use strict';
  const SUPPLY_VOLTAGE=230;
  const COPPER_RESISTIVITY=0.0175;
  const number=(value,name,min,max,optional=false)=>{
    if(optional&&(value===''||value==null))return null;
    const parsed=Number(value);
    if(!Number.isFinite(parsed)||parsed<min||parsed>max)throw new Error(`${name} ${min}–${max} aralığında olmalıdır.`);
    return parsed;
  };
  const oneOf=(value,allowed,fallback)=>allowed.includes(value)?value:fallback;
  function analyze(raw){
    const input={
      totalPower:number(raw.totalPower,'Toplam sürekli güç',1,4000),
      peakPower:number(raw.peakPower,'Tepe/kalkış gücü',1,8000,true),
      length:number(raw.length,'Kablo uzunluğu',1,100),
      section:number(raw.section,'İletken kesiti',0.75,4),
      productType:oneOf(raw.productType,['lead','reel'],'lead'),
      reelState:oneOf(raw.reelState,['unwound','wound'],'unwound'),
      labelUnwoundA:number(raw.labelUnwoundA,'Açılmış durum etiket akımı',1,16),
      labelWoundA:number(raw.labelWoundA,'Sarılı durum etiket akımı',1,16,true),
      loadType:oneOf(raw.loadType,['electronics','resistive','motor','charger','unknown'],'unknown'),
      environment:oneOf(raw.environment,['indoor','outdoor','wet_work'],'indoor'),
      outdoorRated:Boolean(raw.outdoorRated),
      rcdProtection:oneOf(raw.rcdProtection,['yes','no','unknown'],'unknown'),
      earthRequirement:oneOf(raw.earthRequirement,['class1','class2','unknown'],'unknown'),
      earthPresent:oneOf(raw.earthPresent,['yes','no','unknown'],'unknown'),
      thermalCutout:oneOf(raw.thermalCutout,['yes','no','unknown'],'unknown'),
      manufacturerVerified:Boolean(raw.manufacturerVerified),
      daisyChain:Boolean(raw.daisyChain),
      permanentUse:Boolean(raw.permanentUse),
      damageOrHeat:Boolean(raw.damageOrHeat)
    };
    if(input.peakPower!=null&&input.peakPower<input.totalPower)throw new Error('Tepe/kalkış gücü sürekli güçten küçük olamaz.');
    if(input.productType==='reel'&&input.reelState==='wound'&&input.labelWoundA==null)throw new Error('Makara sarılı kullanılacaksa sarılı durum etiket akımı girilmelidir.');

    const current=input.totalPower/SUPPLY_VOLTAGE;
    const peakCurrent=(input.peakPower??input.totalPower)/SUPPLY_VOLTAGE;
    const activeRating=input.productType==='reel'&&input.reelState==='wound'?input.labelWoundA:input.labelUnwoundA;
    const loopResistance=(2*input.length*COPPER_RESISTIVITY)/input.section;
    const voltageDrop=current*loopResistance;
    const voltageDropPct=voltageDrop/SUPPLY_VOLTAGE*100;
    const deliveredVoltage=SUPPLY_VOLTAGE-voltageDrop;
    const peakVoltageDrop=peakCurrent*loopResistance;
    const utilization=current/activeRating;

    const blockers=[],warnings=[],checks=[];
    if(input.damageOrHeat)blockers.push('Kablo, fiş veya prizde hasar, gevşeklik, yanık kokusu, kararma ya da belirgin ısınma var. Ürünü enerjisiz bırakın ve kullanımdan çıkarın.');
    if(input.daisyChain)blockers.push('Bir uzatma kablosunu başka bir uzatma kablosuna bağlamak uygun değildir; tek parça ve yeterli uzunlukta ürün veya sabit priz gerekir.');
    if(input.permanentUse)blockers.push('Uzatma kablosu kalıcı tesisatın yerine kullanılmamalıdır; uygun noktaya sabit priz/hat için elektrikçi değerlendirmesi gerekir.');
    if(current>activeRating)blockers.push(`Sürekli akım ${current.toFixed(1)} A, kullanım durumundaki ${activeRating.toFixed(1)} A etiket sınırını aşıyor.`);
    if(peakCurrent>activeRating)blockers.push(`Tepe akımı ${peakCurrent.toFixed(1)} A, kullanım durumundaki ${activeRating.toFixed(1)} A etiket sınırını aşıyor; motor/kompresör kalkışı bu ürünle doğrulanamaz.`);
    if(input.productType==='reel'&&input.reelState==='wound')warnings.push('Makara sarılı kullanılıyor. Etiket buna izin verse bile ısı birikimi artar; tam açmak daha güvenli rotadır.');
    if(input.productType==='reel'&&input.thermalCutout!=='yes')blockers.push('Kablo makarasının termik kesicisi açıkça doğrulanmadı. Termik koruması belirtilmeyen makarayı kullanmayın.');
    if(input.environment!=='indoor'&&!input.outdoorRated)blockers.push('Dış ortam veya ıslak/iletken ortam için uygunluk ve IP sınıfı doğrulanmadı. İç ortam uzatma ürünü burada kullanılmamalıdır.');
    if(input.environment==='wet_work'&&input.rcdProtection!=='yes')blockers.push('Islak/iletken veya şantiye benzeri ortamda RCD koruması doğrulanmadı. Kullanım başlamadan uygun koruma ve saha yöntemi uzman tarafından doğrulanmalıdır.');
    else if(input.environment==='outdoor'&&input.rcdProtection!=='yes')warnings.push('Dış ortamda RCD koruması doğrulanmadı; priz devresi ve taşınabilir koruma yöntemi kontrol edilmelidir.');
    if(input.earthRequirement==='class1'&&input.earthPresent!=='yes')blockers.push('Koruma iletkeni gerektiren cihaz için uzatma ürününde topraklama sürekliliği doğrulanmadı.');
    if(input.earthRequirement==='unknown'||input.earthPresent==='unknown')warnings.push('Cihazın koruma sınıfı veya uzatma ürününün topraklama sürekliliği net değil. Etiket ve fiş yapısı doğrulanmalıdır.');
    if(!input.manufacturerVerified)warnings.push('Ürünün tam model etiketindeki akım/güç, sarılı-açılmış kullanım ve ortam bilgileri doğrulanmadı.');
    if(voltageDropPct>5)blockers.push(`Yaklaşık gerilim düşümü %${voltageDropPct.toFixed(1)}. Daha kısa veya daha büyük kesitli tek parça ürün ve üretici doğrulaması gerekir.`);
    else if(voltageDropPct>3)warnings.push(`Yaklaşık gerilim düşümü %${voltageDropPct.toFixed(1)}. Özellikle motor ve hassas yüklerde daha kısa/büyük kesitli ürün değerlendirin.`);
    if(utilization>=0.8&&utilization<=1)warnings.push(`Sürekli yük etiket akımının yaklaşık %${Math.round(utilization*100)}'ini kullanıyor; ortam sıcaklığı, temas kalitesi ve uzun kullanım süresi için daha fazla pay yararlı olabilir.`);
    if(input.loadType==='resistive'&&input.totalPower>1500)warnings.push('Isıtıcı, kettle veya pişirme yükü yüksek ve uzun süreli akım çekebilir; mümkünse doğrudan uygun duvar prizini kullanın.');
    if(input.loadType==='motor')warnings.push('Motor/kompresör ve elektrikli el aleti kalkış akımı ile gerilim düşümü ürün etiketinden ayrıca doğrulanmalıdır.');
    if(input.loadType==='charger'&&input.totalPower>1000)warnings.push('Yüksek güçlü batarya/araç şarjı geçici uzatma yerine üreticinin onayladığı sabit veya özel besleme düzeni gerektirebilir.');
    if(input.loadType==='unknown')warnings.push('Yük türü bilinmiyor; tepe akımı ve sürekli çalışma davranışı doğrulanmadan ürün uygun kabul edilmemelidir.');

    let status='compatible';
    if(blockers.length)status='incompatible';
    else if(warnings.length)status='conditional';

    const professionalRequired=input.environment!=='indoor'||input.permanentUse||input.loadType==='motor'||input.loadType==='charger'||input.totalPower>1500||status==='incompatible';
    const commercialAllowed=status==='compatible'&&input.environment==='indoor'&&!input.permanentUse&&!input.daisyChain&&!input.damageOrHeat&&input.manufacturerVerified&&input.totalPower<=1000&&['electronics','resistive'].includes(input.loadType)&&input.earthRequirement!=='unknown'&&(input.earthRequirement==='class2'||input.earthPresent==='yes')&&(input.productType==='lead'||(input.reelState==='unwound'&&input.thermalCutout==='yes'));

    checks.push('Ürünün etiketindeki azami akımı ve varsa sarılı/açılmış güç değerlerini tam model için doğrulayın.');
    checks.push('Bağlı cihazların aynı anda çektiği toplam gücü ve motor/kompresör varsa kalkış değerini dikkate alın.');
    checks.push('Kablo makarasını yüksek yükte tamamen açın; termik kesiciyi doğru kullanımın yerine koymayın.');
    checks.push('Hasarlı, ezilmiş, gevşek, kararmış veya ısınan fiş/kabloyu kullanımdan çıkarın; bantla geçici onarım yapmayın.');
    checks.push('Uzatma kablosunu kalıcı tesisat, duvar/kapı içi geçiş veya zincirleme bağlantı yerine kullanmayın.');
    if(input.environment!=='indoor')checks.push('Dış/ıslak ortamda ürünün ortam sınıfını, priz kapaklarını, bağlantı noktasının sudan uzaklığını ve RCD korumasını doğrulayın.');

    return {
      input,current,peakCurrent,activeRating,loopResistance,voltageDrop,voltageDropPct,deliveredVoltage,peakVoltageDrop,utilization,
      status,blockers,warnings,checks,professionalRequired,commercialAllowed
    };
  }
  return {analyze,SUPPLY_VOLTAGE};
});