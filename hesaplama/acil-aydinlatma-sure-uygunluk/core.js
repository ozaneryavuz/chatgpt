(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  root.Alo186EmergencyLightingSuitability=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(){
  'use strict';

  const round=(value,digits=2)=>Number(value.toFixed(digits));
  const bool=value=>value===true||value==='true'||value===1||value==='1';
  const enumValue=(value,allowed,fallback)=>allowed.includes(value)?value:fallback;
  const number=(value,name,min,max)=>{
    const parsed=Number(value);
    if(!Number.isFinite(parsed)||parsed<min||parsed>max)throw new Error(`${name} ${min}–${max} aralığında olmalıdır.`);
    return parsed;
  };
  const placementFactors={poor:0.3,average:0.45,good:0.6};

  function analyze(raw){
    const input={
      useCase:enumValue(raw.useCase,['home_room','home_corridor','outdoor','workplace_exit','medical','hazardous'],'home_room'),
      ownership:enumValue(raw.ownership,['candidate','owned'],'candidate'),
      areaM2:number(raw.areaM2,'Alan',2,2000),
      targetLux:number(raw.targetLux,'Hedef aydınlık',1,500),
      lumensPerUnit:number(raw.lumensPerUnit,'Ürün ışık akısı',5,20000),
      units:number(raw.units,'Ürün adedi',1,50),
      placement:enumValue(raw.placement,['poor','average','good'],'average'),
      targetHours:number(raw.targetHours,'Hedef süre',0.5,72),
      declaredRuntimeHours:number(raw.declaredRuntimeHours,'Beyan edilen çalışma süresi',0.5,300),
      lumensVerified:bool(raw.lumensVerified),
      runtimeVerified:bool(raw.runtimeVerified),
      physicalSwitch:bool(raw.physicalSwitch),
      chargeIndicator:bool(raw.chargeIndicator),
      handsFreeMount:bool(raw.handsFreeMount),
      autoOnRequired:bool(raw.autoOnRequired),
      autoOnSupported:bool(raw.autoOnSupported),
      weatherRated:bool(raw.weatherRated),
      damageFree:bool(raw.damageFree),
      drySafeEnvironment:bool(raw.drySafeEnvironment),
      candlesPlanned:bool(raw.candlesPlanned)
    };

    const factor=placementFactors[input.placement];
    const totalLumens=input.lumensPerUnit*input.units;
    const approximateLux=totalLumens*factor/input.areaM2;
    const requiredUnits=Math.max(1,Math.ceil((input.targetLux*input.areaM2)/(input.lumensPerUnit*factor)));
    const runtimeMarginHours=input.declaredRuntimeHours-input.targetHours;
    const illuminationMarginPct=(approximateLux-input.targetLux)/input.targetLux*100;

    const blockers=[];
    const blockerCodes=[];
    const warnings=[];
    const checks=[];
    const block=(code,text)=>{blockerCodes.push(code);blockers.push(text);};

    const professionalRequired=['workplace_exit','medical','hazardous'].includes(input.useCase);
    if(input.useCase==='workplace_exit')block('workplace','İşyeri kaçış yolu ve çıkış aydınlatması mevzuat, fotometrik proje, test ve bakım kaydı gerektirir; taşınabilir tüketici ürünüyle uygunluk verilemez.');
    if(input.useCase==='medical')block('medical','Tıbbi veya bakım amaçlı kritik alanlarda genel şarjlı lamba yönlendirmesi yapılmaz; onaylı sabit acil aydınlatma ve güç sürekliliği gerekir.');
    if(input.useCase==='hazardous')block('hazardous','Yanıcı gaz, buhar, toz veya patlayıcı ortamda genel tüketici lambası kullanılmamalıdır; uygun Ex ekipman ve proje gerekir.');
    if(!input.damageFree)block('damage','Şişmiş pil, çatlak gövde, koku, sıvı teması veya olağandışı ısı bulunan ürünü kullanmayın ya da şarj etmeyin.');
    if(!input.drySafeEnvironment)block('environment','Kuru, serin ve yanıcı maddelerden uzak güvenli kullanım alanı doğrulanmadı.');
    if(input.useCase==='outdoor'&&!input.weatherRated)block('weather','Dış ortam kullanımında ürünün su/toz dayanımı ve üretici kullanım sınırı doğrulanmadı.');
    if(input.candlesPlanned)block('candles','Kesintide ana aydınlatma olarak mum veya açık alev planlanmamalıdır; pilli ya da şarjlı ışık kullanın.');
    if(approximateLux+1e-9<input.targetLux)block('illumination','Girilen adet ve ışık akısı, seçilen alan ve yerleşim varsayımıyla hedef aydınlığı karşılamıyor.');
    if(input.declaredRuntimeHours+1e-9<input.targetHours)block('runtime','Ürünün doğrulanan çalışma süresi hedef kesinti süresinden kısa.');
    if(input.autoOnRequired&&!input.autoOnSupported)block('auto_on','Şebeke kesilince otomatik yanma gerekli ancak ürünün bu işlevi doğrulanmadı.');

    if(!input.lumensVerified)warnings.push('Lümen değeri tam ürün teknik sayfasından doğrulanmadı.');
    if(!input.runtimeVerified)warnings.push('Çalışma süresinin hangi parlaklık modunda verildiği doğrulanmadı.');
    if(!input.physicalSwitch)warnings.push('Elektrik kesilince uygulama veya dokunmatik kontrol olmadan çalışabilen fiziksel düğme doğrulanmadı.');
    if(!input.chargeIndicator)warnings.push('Şarj veya düşük pil göstergesi doğrulanmadı; hazırlık durumu fark edilmeyebilir.');
    if(['home_corridor','outdoor'].includes(input.useCase)&&!input.handsFreeMount)warnings.push('Koridor, merdiven veya dış kullanımda iki eli serbest bırakan askı, kanca, mıknatıs ya da sabit kaide doğrulanmadı.');
    if(input.placement==='good')warnings.push('İyi yerleşim katsayısı, ışığın engellenmeden ve uygun yükseklikte dağıtılacağı varsayımına dayanır.');

    checks.push('Lümen ve çalışma süresini aynı parlaklık modu için üretici teknik sayfasından doğrulayın.');
    checks.push('Lambayı kapı, merdiven ve yürüyüş hattını gölgelemeyecek; kolay erişilen bir noktada tutun.');
    checks.push('Aylık kısa işlev testi yapın ve uzun kesinti sezonu öncesinde tam şarj edin.');
    checks.push('Mum yerine pilli veya şarjlı el feneri ya da fener kullanın.');
    if(input.useCase==='home_corridor')checks.push('Tek noktaya bağımlılığı azaltmak için koridorun iki ucunda bağımsız ışık değerlendirin.');
    if(input.useCase==='outdoor')checks.push('IP sınıfı, çalışma sıcaklığı ve şarj portu kapağını tam model kılavuzundan kontrol edin.');

    const allVerified=input.lumensVerified&&input.runtimeVerified&&input.physicalSwitch&&input.chargeIndicator&&input.damageFree&&input.drySafeEnvironment&&(!input.autoOnRequired||input.autoOnSupported)&&(input.useCase!=='outdoor'||input.weatherRated);
    const lowRisk=['home_room','home_corridor','outdoor'].includes(input.useCase)&&input.areaM2<=120&&input.targetLux<=100&&input.lumensPerUnit<=3000;
    const status=professionalRequired?'professional':blockers.length?'incompatible':warnings.length?'conditional':'compatible';
    const noPurchaseNeeded=input.ownership==='owned'&&status==='compatible';
    const commercialAllowed=Boolean(input.ownership==='candidate'&&status==='compatible'&&allVerified&&lowRisk);

    let recommendedClass='Şarjlı el feneri veya kamp feneri';
    if(input.autoOnRequired)recommendedClass='Şebeke kesilince otomatik yanan şarjlı acil lamba';
    else if(input.useCase==='home_corridor')recommendedClass='Askılı veya sabitlenebilir geniş açılı şarjlı lamba';
    else if(input.useCase==='outdoor')recommendedClass='IP sınıfı doğrulanmış şarjlı fener';
    if(professionalRequired)recommendedClass='Projeli sabit acil aydınlatma sistemi';

    return {
      input,status,blockers,blockerCodes,warnings,checks,professionalRequired,lowRisk,
      factor,totalLumens:round(totalLumens),approximateLux:round(approximateLux,1),requiredUnits,
      runtimeMarginHours:round(runtimeMarginHours,1),illuminationMarginPct:round(illuminationMarginPct,1),
      allVerified,noPurchaseNeeded,commercialAllowed,recommendedClass
    };
  }

  return {analyze,placementFactors};
});
