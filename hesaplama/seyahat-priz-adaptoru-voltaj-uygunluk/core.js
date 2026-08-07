(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  root.Alo186TravelAdapter=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(){
  'use strict';

  const destinations={
    eu:{id:'eu',label:'Türkiye ve Avrupa C/F',plug:'C/F',voltage:230,frequency:50,frequencyLabel:'50 Hz',search:'Avrupa Type C F seyahat adaptörü topraklı'},
    uk:{id:'uk',label:'Birleşik Krallık ve İrlanda G',plug:'G',voltage:230,frequency:50,frequencyLabel:'50 Hz',search:'Türkiye fişi Type G İngiltere seyahat adaptörü topraklı sigortalı'},
    us:{id:'us',label:'ABD ve Kanada A/B',plug:'A/B',voltage:120,frequency:60,frequencyLabel:'60 Hz',search:'Türkiye fişi Type A B ABD seyahat adaptörü topraklı'},
    japan:{id:'japan',label:'Japonya A/B',plug:'A/B',voltage:100,frequency:null,frequencyLabel:'50/60 Hz (bölgeye göre)',search:'Türkiye fişi Japonya Type A B seyahat adaptörü'},
    au:{id:'au',label:'Avustralya ve Yeni Zelanda I',plug:'I',voltage:230,frequency:50,frequencyLabel:'50 Hz',search:'Türkiye fişi Type I Avustralya seyahat adaptörü topraklı'},
    ch:{id:'ch',label:'İsviçre J',plug:'J',voltage:230,frequency:50,frequencyLabel:'50 Hz',search:'Türkiye fişi Type J İsviçre seyahat adaptörü'},
    unknown:{id:'unknown',label:'Diğer veya bilinmiyor',plug:'?',voltage:null,frequency:null,frequencyLabel:'doğrulanmalı',search:''}
  };

  const roundUp=(value,step)=>Math.ceil(value/step)*step;
  const finite=(value)=>Number.isFinite(Number(value));
  const supportsFrequency=(label,destinationHz)=>{
    if(label==='50_60')return true;
    if(label==='50')return destinationHz===50;
    if(label==='60')return destinationHz===60;
    return false;
  };

  function evaluate(raw={}){
    const input={
      destination:String(raw.destination||'unknown'),
      deviceType:String(raw.deviceType||'electronics'),
      minV:Number(raw.minV),
      maxV:Number(raw.maxV),
      frequency:String(raw.frequency||'unknown'),
      deviceW:Number(raw.deviceW),
      earthClass:String(raw.earthClass||'unknown'),
      existingAdapter:String(raw.existingAdapter||'none'),
      adapterMaxV:Number(raw.adapterMaxV||0),
      adapterMaxA:Number(raw.adapterMaxA||0),
      adapterMaxW:Number(raw.adapterMaxW||0),
      adapterEarth:String(raw.adapterEarth||'unknown'),
      safetyEvidence:String(raw.safetyEvidence||'unknown'),
      recallChecked:String(raw.recallChecked||'unknown'),
      hazard:Boolean(raw.hazard),
      adapterDamaged:Boolean(raw.adapterDamaged),
      tripDate:String(raw.tripDate||'')
    };

    const errors=[];
    if(!finite(input.minV)||!finite(input.maxV)||input.minV<1||input.maxV<input.minV||input.maxV>500)errors.push('Cihaz etiketindeki giriş gerilimi aralığını doğru girin.');
    if(!finite(input.deviceW)||input.deviceW<1||input.deviceW>5000)errors.push('Cihaz gücü 1–5000 W arasında olmalıdır.');
    if(errors.length)return {status:'invalid',title:'Girdileri kontrol edin',errors,commerceAllowed:false};

    const destination=destinations[input.destination]||destinations.unknown;
    const base={input,destination,requiredW:roundUp(input.deviceW*1.25,10),requiredA:destination.voltage?Math.ceil((input.deviceW*1.25/destination.voltage)*10)/10:null,commerceAllowed:false,affiliateQuery:null,actions:[],warnings:[],reasons:[]};

    if(input.hazard||input.adapterDamaged||(input.existingAdapter==='yes'&&input.recallChecked==='no')){
      return {...base,status:'emergency',title:'Kullanmayı durdurun',summary:'Hasarlı, gevşek, aşırı ısınan veya olumsuz güvenlik duyurusu bulunan adaptörü prize takmayın.',actions:['Adaptörü enerjisiz bırakın ve tekrar kullanmayın.','Yanık kokusu, kıvılcım, erime veya elektrik çarpması riski varsa güvenli alana geçin; acil durumda 112’yi arayın.','Ürünün modelini yetkili ürün güvenliği veya üretici duyurusundan kontrol edin.']};
    }

    if(destination.id==='unknown'){
      return {...base,status:'evidence',title:'Hedef ülkenin priz ve şebeke bilgisini doğrulayın',summary:'Priz tipi, nominal gerilim ve frekans bilinmeden ürün bağlantısı açılmaz.',actions:['Hedef konaklama veya resmî elektrik/priz kaynağından priz tipini doğrulayın.','Cihazın INPUT etiketindeki V, Hz ve W/A değerlerini kaydedin.','Doğrulama tamamlanınca aracı yeniden çalıştırın.']};
    }

    if(input.deviceType==='medical'){
      return {...base,status:'professional',title:'Tıbbi cihazda üretici onayı gerekir',summary:'Tıbbi veya yaşam destek cihazı için genel seyahat adaptörü seçimi uygun değildir.',actions:['Cihaz üreticisinin seyahat ve güç kaynağı talimatını izleyin.','Gerekli yedek güç ve adaptör için yetkili servis veya sağlık kuruluşuyla doğrulayın.']};
    }

    const voltageCompatible=input.minV<=destination.voltage&&input.maxV>=destination.voltage;
    const frequencyCompatible=destination.frequency===null?input.frequency==='50_60':supportsFrequency(input.frequency,destination.frequency);
    const plugNeeded=destination.plug!=='C/F';
    const highPower=['heater','motor'].includes(input.deviceType)||input.deviceW>1000;

    if(!voltageCompatible){
      return {...base,status:'voltage_mismatch',title:'Priz adaptörü voltajı dönüştürmez',summary:`Cihaz etiketi ${input.minV}–${input.maxV} V; hedef şebeke yaklaşık ${destination.voltage} V. Yalnız fiş biçimini değiştiren adaptör bu uyumsuzluğu çözmez.`,actions:['Cihaz üreticisinden uygun voltaj dönüştürücü veya çift gerilimli alternatif doğrulayın.','Saç kurutma, ısıtıcı, su ısıtıcı ve motorlu yüksek güçlü cihazlarda küçük seyahat dönüştürücüsü kullanmayın.','Uygunluk kanıtı olmadan ürünü prize takmayın.']};
    }

    if(input.frequency==='unknown'){
      return {...base,status:'evidence',title:'Frekans etiketini doğrulayın',summary:`Hedef şebeke ${destination.frequencyLabel}. Cihazın 50/60 Hz kabulü bilinmeden kesin uygunluk verilemez.`,actions:['Cihaz veya adaptör INPUT etiketindeki Hz satırını kontrol edin.','Motor, saat, pompa ve zamanlama kullanan cihazlarda frekans farkını üreticiyle doğrulayın.']};
    }

    if(destination.frequency===null&&input.frequency!=='50_60'){
      return {...base,status:'evidence',title:'Japonya’daki hedef bölgenin frekansını doğrulayın',summary:'Japonya’da şebeke frekansı bölgeye göre 50 veya 60 Hz olabilir. Tek frekanslı cihazda şehir/bölge bilgisi doğrulanmadan ürün yolu açılmaz.',actions:['Konaklama veya cihaz üreticisi üzerinden hedef bölgenin 50/60 Hz bilgisini doğrulayın.','Motor, saat ve pompa gibi frekansa duyarlı cihazları kanıt olmadan çalıştırmayın.']};
    }

    if(!frequencyCompatible){
      return {...base,status:'frequency_mismatch',title:'Frekans uyumu doğrulanmadı',summary:`Cihaz etiketi ${input.frequency==='50'?'50':'60'} Hz; hedef şebeke ${destination.frequencyLabel}. Fiş adaptörü frekansı değiştirmez.`,actions:['Cihazı üretici onayı olmadan çalıştırmayın.','Hedef ülkede uygun cihaz kullanmayı veya profesyonel dönüştürme çözümünü değerlendirin.','Frekans uyumsuzluğu giderilmeden affiliate veya mağaza yoluna ilerlemeyin.']};
    }

    if(highPower){
      return {...base,status:'professional',title:'Yüksek güçlü cihaz için genel adaptör rotası kapalı',summary:'Isıtıcı, saç kurutma, ütü, su ısıtıcı ve motorlu yüksek güçlü cihazlarda temas, topraklama, sigorta ve sürekli akım riski vardır.',actions:['Cihaz çift gerilimli değilse hedef ülkede uygun cihaz kullanın.','Yalnız ülkeye özel, topraklamayı koruyan ve sürekli güç değeri açık ürünleri üretici talimatıyla doğrulayın.','Adaptörleri art arda bağlamayın ve çoklu prizle yükü büyütmeyin.']};
    }

    if(!plugNeeded){
      return {...base,status:'no_buy',title:'Yeni priz adaptörü gerekmiyor',summary:'Türkiye/Avrupa C/F fiş biçimi ve cihazın gerilim-frekans etiketi hedef şebekeyle uyumlu görünüyor.',actions:['Fiş, kablo ve adaptörde hasar olmadığını kontrol edin.','Cihaz üreticisinin ülkeye özel uyarılarını yeniden okuyun.','Mevcut şarj cihazınız yeterliyse yeni ürün almayın.']};
    }

    const capacityLimits=[];
    if(input.adapterMaxW>0)capacityLimits.push(input.adapterMaxW);
    if(input.adapterMaxA>0)capacityLimits.push(input.adapterMaxA*destination.voltage);
    const adapterCapacityW=capacityLimits.length?Math.min(...capacityLimits):0;
    const earthRequired=input.earthClass==='earth_required';
    const existingAdequate=input.existingAdapter==='yes'&&
      input.safetyEvidence==='yes'&&input.recallChecked==='yes'&&
      input.adapterMaxV>=destination.voltage&&adapterCapacityW>=base.requiredW&&
      (!earthRequired||input.adapterEarth==='yes');

    if(input.existingAdapter==='yes'&&existingAdequate){
      return {...base,status:'no_buy',title:'Mevcut adaptör teknik eşikleri karşılıyor',summary:`Mevcut adaptör en az ${base.requiredW} W planlama gücünü, ${destination.voltage} V sınıfını ve gerekli topraklama koşulunu karşılıyor.`,actions:['Seyahatten önce gevşeklik, ısınma ve fiziksel hasar kontrolü yapın.','Adaptörün geri çağırma durumunu model numarasıyla yeniden kontrol edin.','Mevcut ürün yeterliyse yeni ürün almayın.']};
    }

    if(input.earthClass==='unknown'){
      return {...base,status:'evidence',title:'Topraklama sınıfını doğrulayın',summary:'Cihazın koruma sınıfı bilinmeden iki kutuplu veya topraklı adaptör seçilemez.',actions:['Cihazda çift kare Class II sembolü olup olmadığını kontrol edin.','Topraklı fişi olan cihazda topraklamayı kesen adaptör kullanmayın.']};
    }

    const reason=[];
    if(input.existingAdapter==='none')reason.push('uygun adaptör yok');
    if(input.existingAdapter==='yes'&&input.safetyEvidence!=='yes')reason.push('güvenlik/standart kanıtı eksik');
    if(input.existingAdapter==='yes'&&input.recallChecked!=='yes')reason.push('geri çağırma kontrolü eksik');
    if(input.existingAdapter==='yes'&&input.adapterMaxV<destination.voltage)reason.push('gerilim sınıfı yetersiz');
    if(input.existingAdapter==='yes'&&adapterCapacityW<base.requiredW)reason.push('sürekli güç/akım değeri yetersiz');
    if(input.existingAdapter==='yes'&&earthRequired&&input.adapterEarth!=='yes')reason.push('topraklama sürekliliği doğrulanmadı');

    const query=earthRequired?`${destination.search} en az ${base.requiredW}W`:`${destination.search} ${base.requiredW}W`;
    return {...base,status:'conditional_purchase',commerceAllowed:true,affiliateQuery:query,title:'Ülkeye özel adaptör kategorisi değerlendirilebilir',summary:`Cihaz etiketi hedef şebekeyle uyumlu; yalnız fiş biçimi için en az ${base.requiredW} W${base.requiredA?` / ${base.requiredA} A`:''} sınıfı ve ${earthRequired?'topraklamayı koruyan':'cihaz sınıfına uygun'} adaptör gerekir.`,reasons:reason,actions:['Ürünün yalnız fiş dönüştürdüğünü; voltaj ve frekans dönüştürmediğini doğrulayın.','Priz standardı, azami V/A/W, topraklama, sigorta ve koruyucu perde bilgisini ürün belgesinden kontrol edin.','Adaptörleri birbirine veya gevşek çoklayıcılara bağlamayın.','Fiyat, stok, satıcı ve garanti bilgilerini mağaza sayfasında yeniden doğrulayın.']};
  }

  return {destinations,evaluate};
});
