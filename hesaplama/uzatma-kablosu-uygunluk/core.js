(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports){module.exports=api;}
  root.Alo186ExtensionSuitability=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(){
  'use strict';

  const COPPER_RESISTIVITY_20C=0.0175;
  const WARM_CONDUCTOR_FACTOR=1.2;
  const AREAS=[0.75,1,1.5,2.5,4];
  const CURRENT_LABELS=[6,10,13,16];

  const number=(value,name,min,max,optional=false)=>{
    if(optional&&(value===''||value==null))return null;
    const parsed=Number(value);
    if(!Number.isFinite(parsed)||parsed<min||parsed>max)throw new Error(`${name} ${min}–${max} aralığında olmalıdır.`);
    return parsed;
  };
  const enumValue=(value,allowed,fallback)=>allowed.includes(value)?value:fallback;
  const bool=value=>value===true||value==='true'||value===1||value==='1';
  const roundUpOption=(value,options)=>options.find(option=>option>=value)??null;

  function voltageDrop({current,length,area,voltage}){
    const loopResistance=2*length*COPPER_RESISTIVITY_20C/area*WARM_CONDUCTOR_FACTOR;
    const drop=current*loopResistance;
    return {loopResistance,drop,percent:(drop/voltage)*100,loss:current*current*loopResistance};
  }

  function recommendArea(current,length,voltage,targetPercent=3){
    return AREAS.find(area=>voltageDrop({current,length,area,voltage}).percent<=targetPercent)??null;
  }

  function analyze(raw){
    const input={
      evaluationMode:enumValue(raw.evaluationMode,['existing','planned'],'existing'),
      voltage:number(raw.voltage,'Şebeke gerilimi',200,250),
      loadPower:number(raw.loadPower,'Cihaz gücü',10,4000),
      powerFactor:number(raw.powerFactor,'Güç faktörü',0.5,1),
      loadType:enumValue(raw.loadType,['electronic','resistive','motor'],'electronic'),
      startMultiplier:number(raw.startMultiplier,'Kalkış akımı katsayısı',1,8,true),
      usage:enumValue(raw.usage,['short','continuous'],'short'),
      intendedUse:enumValue(raw.intendedUse,['portable','heater','cooling','ev','generatorBackfeed','fixed','medical'],'portable'),
      length:number(raw.length,'Tek yön kablo uzunluğu',1,100),
      area:number(raw.area,'İletken kesiti',0.5,6),
      ratedCurrent:number(raw.ratedCurrent,'Ürün etiket akımı',2,16),
      reelState:enumValue(raw.reelState,['none','unwound','wound'],'none'),
      woundMaxPower:number(raw.woundMaxPower,'Sarılı durum azami güç',50,4000,true),
      unwoundMaxPower:number(raw.unwoundMaxPower,'Açılmış durum azami güç',50,5000,true),
      environment:enumValue(raw.environment,['indoor','outdoor','construction','wet','unknown'],'indoor'),
      applianceClass:enumValue(raw.applianceClass,['classI','classII','unknown'],'unknown'),
      factoryAssembled:bool(raw.factoryAssembled),
      labelVerified:bool(raw.labelVerified),
      damageFree:bool(raw.damageFree),
      earthPresent:bool(raw.earthPresent),
      outdoorRated:bool(raw.outdoorRated),
      thermalProtection:bool(raw.thermalProtection),
      daisyChain:bool(raw.daisyChain),
      recallChecked:bool(raw.recallChecked)
    };

    if(!AREAS.includes(input.area))throw new Error('İletken kesiti 0,75 · 1 · 1,5 · 2,5 veya 4 mm² seçeneklerinden biri olmalıdır.');
    if(input.loadType==='motor'&&input.startMultiplier==null)throw new Error('Motorlu yük için etiket veya üretici bilgisindeki kalkış akımı katsayısını girin.');
    if(input.loadType!=='motor'&&input.startMultiplier==null)input.startMultiplier=1;

    const operatingCurrent=input.loadPower/(input.voltage*input.powerFactor);
    const startCurrent=input.loadType==='motor'?operatingCurrent*input.startMultiplier:operatingCurrent;
    const drop=voltageDrop({current:operatingCurrent,length:input.length,area:input.area,voltage:input.voltage});
    const startDrop=voltageDrop({current:startCurrent,length:input.length,area:input.area,voltage:input.voltage});
    const reserveFactor=input.usage==='continuous'?1.25:1.15;
    const recommendedRatedCurrent=roundUpOption(operatingCurrent*reserveFactor,CURRENT_LABELS);
    const recommendedArea=recommendArea(operatingCurrent,input.length,input.voltage,3);

    const blockers=[];
    const warnings=[];
    const checks=[];

    if(!input.damageFree)blockers.push('Kablo, fiş, priz gövdesi veya dış kılıfta hasar/ısınma izi var. Ürün kullanılmamalıdır.');
    if(!input.factoryAssembled)blockers.push('Kullanıcı tarafından birleştirilmiş veya kaynağı belirsiz uzatma seti güvenli tüketici ürünü olarak değerlendirilemez.');
    if(input.daisyChain)blockers.push('Uzatma kablolarını veya grup prizleri art arda bağlamak yük ve temas noktası riskini artırır.');
    if(input.intendedUse==='generatorBackfeed')blockers.push('Erkek–erkek kabloyla jeneratörden bina tesisatına geri besleme ölümcül elektrik çarpması ve yangın riski taşır.');
    if(input.intendedUse==='ev')blockers.push('Elektrikli araç mobil şarj cihazında uzatma kablosu kullanılmamalıdır; üretici onaylı doğrudan ve topraklı priz/devre gerekir.');
    if(input.intendedUse==='fixed')blockers.push('Uzatma kablosu sabit tesisatın veya kalıcı bina kablolamasının yerine kullanılamaz.');
    if(input.intendedUse==='medical')warnings.push('Tıbbi veya yaşam destek cihazında genel uzatma kablosu seçimi yeterli değildir; cihaz üreticisi ve yetkili uzman süreklilik planını doğrulamalıdır.');
    if(input.intendedUse==='heater')warnings.push('Isıtıcı, ütü, su ısıtıcısı ve benzeri uzun süre yüksek güç çeken yüklerde doğrudan duvar prizi ve tesisat uygunluğu tercih edilmelidir; affiliate yolu açılmaz.');
    if(input.intendedUse==='cooling')warnings.push('Buzdolabı, dondurucu, klima veya pompa gibi kompresörlü yüklerde kalkış akımı ve üretici kılavuzu nedeniyle doğrudan priz/devre doğrulaması gerekir; affiliate yolu açılmaz.');

    if(operatingCurrent>input.ratedCurrent)blockers.push(`Yaklaşık çalışma akımı ${operatingCurrent.toFixed(1)} A, ürünün ${input.ratedCurrent.toFixed(1)} A etiket sınırını aşıyor.`);
    else if(operatingCurrent>input.ratedCurrent*0.8)warnings.push('Çalışma akımı ürün etiketinin %80’ini aşıyor; uzun süreli kullanımda daha yüksek etiket akımı ve daha kısa/kalın kablo değerlendirilmelidir.');
    if(recommendedRatedCurrent==null)blockers.push('Gerekli akım rezervi 16 A tüketici uzatma seti sınırını aşıyor; doğrudan uygun devre ve profesyonel çözüm gerekir.');
    if(drop.percent>5)blockers.push(`Yaklaşık sıcak iletken gerilim düşümü %${drop.percent.toFixed(1)}; bu araçtaki %5 üstü güvenli ön değerlendirme bandının dışında.`);
    else if(drop.percent>3)warnings.push(`Yaklaşık gerilim düşümü %${drop.percent.toFixed(1)}; daha kısa veya daha büyük kesitli kablo tercih edin.`);
    if(input.loadType==='motor'&&startDrop.percent>10)warnings.push(`Tahmini kalkış anı gerilim düşümü %${startDrop.percent.toFixed(1)}; motor zor kalkabilir veya koruma açabilir.`);
    if(input.loadType==='motor'&&startCurrent>input.ratedCurrent)warnings.push(`Tahmini kalkış akımı ${startCurrent.toFixed(1)} A, etiket akımını kısa süreli aşabilir; ürün ve cihaz üreticisi kalkış uygunluğunu doğrulamalıdır.`);

    if(input.reelState==='wound'){
      warnings.push('Kablo makarası sarılı bırakılmış. Isı dağılımı azalır; yüksek yükte tamamen açılmalıdır.');
      if(input.woundMaxPower==null)blockers.push('Sarılı durum etiket gücü bilinmiyor; sarılı makara için uygunluk doğrulanamaz.');
      else if(input.loadPower>input.woundMaxPower)blockers.push(`Yük ${Math.round(input.loadPower)} W, makaranın sarılı durumdaki ${Math.round(input.woundMaxPower)} W etiket sınırını aşıyor.`);
    }
    if(input.reelState==='unwound'){
      if(input.unwoundMaxPower==null)warnings.push('Tam açılmış durum azami güç etiketi girilmedi. Makara üzerindeki ayrı sarılı/açılmış güç değerlerini doğrulayın.');
      else if(input.loadPower>input.unwoundMaxPower)blockers.push(`Yük ${Math.round(input.loadPower)} W, makaranın açılmış durumdaki ${Math.round(input.unwoundMaxPower)} W etiket sınırını aşıyor.`);
      if(!input.thermalProtection)warnings.push('Kablo makarasının termik aşırı ısınma koruması doğrulanmadı.');
    }

    if(['outdoor','construction','wet'].includes(input.environment)&&!input.outdoorRated)blockers.push('Dış ortam/şantiye/ıslak çevre için ürünün uygun kablo kılıfı ve IP koruması doğrulanmadı.');
    if(input.environment==='unknown')warnings.push('Kullanım ortamı bilinmiyor; kuru iç ortam ve dış ortam ürün sınıfları birbirinin yerine kabul edilmemelidir.');
    if(input.applianceClass==='classI'&&!input.earthPresent)blockers.push('Koruma sınıfı I cihaz için topraklama kontaklı ve koruma iletkeni sürekliliği doğrulanmış uzatma gerekir.');
    if(input.applianceClass==='unknown'&&!input.earthPresent)warnings.push('Cihazın koruma sınıfı bilinmiyor ve topraklama kontağı doğrulanmadı.');
    if(!input.labelVerified)warnings.push('Etiket akımı, iletken kesiti ve kullanım sınıfı ürün üzerinde veya üretici belgesinde doğrulanmadı.');
    if(!input.recallChecked)warnings.push('Tam marka-model için resmî geri çağırma veya ürün güvenliği duyurusu kontrol edilmedi; ticari rota açılmaz.');

    let status='compatible';
    if(blockers.length)status='incompatible';
    else if(warnings.length)status='conditional';
    else if(input.evaluationMode==='existing')status='no_buy';

    checks.push(`Gerilim düşümü bakımından önerilen en düşük kesit: ${recommendedArea?`${recommendedArea} mm²`:'4 mm² üzerinde mühendislik hesabı'}.`);
    checks.push(`Etiket akımı için hedef: ${recommendedRatedCurrent?`en az ${recommendedRatedCurrent} A`:'16 A tüketici ürününün üzerinde profesyonel çözüm'}.`);
    checks.push('Ürün etiketindeki azami akımı ve varsa sarılı/açılmış güç değerlerini gerçek yükle karşılaştırın.');
    checks.push('Fiş, priz yuvası, kablo girişi, gerilim azaltıcı parça ve dış kılıfta gevşeme, ezilme, renk değişimi veya ısınma izi olmamalıdır.');
    if(input.environment!=='indoor')checks.push('Dış ortamda üreticinin uygun gördüğü kablo kılıfı ve kullanım koşuluna uygun IP sınıfı doğrulanmalıdır; IP44 suya daldırma onayı değildir.');
    if(input.reelState!=='none')checks.push('Kablo makarasını yüksek yükte tamamen açın; ürünün sarılı ve açılmış durum etiketlerini ayrı ayrı dikkate alın.');
    if(input.applianceClass!=='classII')checks.push('Topraklama kontaklarının fiziksel olarak bulunması yetmez; koruma iletkeni sürekliliği güvenilir ürün ve gerektiğinde uygun testle doğrulanmalıdır.');
    checks.push('Uzatma setini kalıcı tesisat, EV şarjı veya jeneratör geri beslemesi için kullanmayın.');
    checks.push('Tam marka-modeli üretici ve resmî ürün güvenliği/geri çağırma kaynaklarında yeniden kontrol edin.');
    if(status==='no_buy')checks.unshift('Mevcut ürün bu girdilerle yeterli görünüyor; yeni ürün aramayın. Altı ay sonra veya yük/ortam değiştiğinde yeniden kontrol edin.');

    const professionalRequired=status==='incompatible'||input.intendedUse!=='portable'||input.loadPower>2300||operatingCurrent>10||input.environment==='construction'||input.environment==='wet'||(input.loadType==='motor'&&startCurrent>16);
    const reelCommercialOk=input.reelState==='none'||(input.reelState==='unwound'&&input.thermalProtection&&input.unwoundMaxPower!=null&&input.loadPower<=input.unwoundMaxPower);
    const earthOk=input.applianceClass==='classII'||input.earthPresent;
    const environmentOk=input.environment==='indoor'||(input.environment==='outdoor'&&input.outdoorRated);
    const commercialAllowed=status==='compatible'&&input.evaluationMode==='planned'&&input.intendedUse==='portable'&&input.loadPower<=2000&&operatingCurrent<=10&&drop.percent<=3&&input.factoryAssembled&&input.labelVerified&&input.damageFree&&!input.daisyChain&&input.recallChecked&&reelCommercialOk&&earthOk&&environmentOk;
    const affiliateCategory=input.reelState!=='none'?'termik-korumali-kablo-makarasi':input.environment==='outdoor'?'dis-ortam-uzatma-kablosu':'toprakli-uzatma-kablosu';
    const purchaseDecision=status==='no_buy'?'no_buy':commercialAllowed?'conditional_purchase':'no_commerce';

    return {
      input,
      operatingCurrent,
      startCurrent,
      dropVolts:drop.drop,
      dropPercent:drop.percent,
      cableLoss:drop.loss,
      startDropPercent:startDrop.percent,
      recommendedRatedCurrent,
      recommendedArea,
      status,
      blockers,
      warnings,
      checks,
      professionalRequired,
      commercialAllowed,
      affiliateCategory,
      purchaseDecision,
      repeatDays:180
    };
  }

  return {analyze,voltageDrop,recommendArea};
});
