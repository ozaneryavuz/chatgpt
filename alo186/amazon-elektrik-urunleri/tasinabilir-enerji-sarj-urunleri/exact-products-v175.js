(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  if(root&&typeof root==='object')root.Alo186ExactAffiliateProductsV175=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(){
  'use strict';

  const version=175;
  const affiliateTag='alo186rehber-21';
  const verificationMaxAgeDays=45;
  const generatedAt='2026-08-01';

  function amazonProductUrl(asin){
    return `https://www.amazon.com.tr/dp/${encodeURIComponent(asin)}?tag=${encodeURIComponent(affiliateTag)}`;
  }
  function amazonSearchUrl(query){
    return `https://www.amazon.com.tr/s?k=${encodeURIComponent(query)}&tag=${encodeURIComponent(affiliateTag)}`;
  }

  const products=[
    {
      id:'spigen-ach08701-20w',category:'charger',asin:'B0DWT5G6QQ',mpn:'ACH08701',brand:'Spigen',
      name:'Spigen ACH08701 20 W USB-C GaN şarj cihazı',verifiedAt:'2026-08-01',
      userNeed:'Telefon veya küçük tablet için kompakt tek portlu USB-C adaptör',
      facts:['20 W etiket gücü','Tek USB-C port','GaN tabanlı kompakt yapı'],
      bestFor:['20 W veya daha düşük USB-C PD cihazlar','Seyahat ve yedek adaptör kullanımı'],
      evidence:['Cihazın kabul ettiği watt','USB-C kablonun cihaz ucuyla uyumu','Tek portun yeterli olması'],
      noBuyWhen:['Mevcut adaptör aynı cihazı güvenli ve yeterli hızda şarj ediyorsa','Birden fazla port veya 20 W üzeri güç gerekiyorsa','Adaptör, priz veya kabloda ısınma ya da fiziksel hasar varsa'],
      technicalSource:'https://www.spigen.com.tr/urun/spigen-20w-usb-c-mini-hizli-sarj-aleti-samsung-pps-sarj-isisini-dusurur-gan-destekli-akim-korumali-guc-adaptoru-iphone-android-ipad-type-c-ee201-white-ach08701'
    },
    {
      id:'ugreen-nexode-90549-140w',category:'charger',asin:'B0B127GW4D',mpn:'90549',brand:'UGREEN',
      name:'UGREEN Nexode 90549 140 W PD 3.1 üç port GaN şarj cihazı',verifiedAt:'2026-08-01',
      userNeed:'100 W üzeri USB-C dizüstü ile telefon veya tableti tek adaptörle şarj etmek',
      facts:['140 W toplam çıkış sınıfı','İki USB-C ve bir USB-A port','PD 3.1 ve PPS','1 m 240 W USB-C kablo'],
      bestFor:['USB PD 3.1 destekli yüksek güçlü dizüstüler','Tek adaptörle birden fazla cihaz kullananlar'],
      evidence:['Dizüstünün kabul ettiği watt','Tek port ve toplam güç dağılımı','USB PD 3.1/EPR desteği','Kablo güç sınıfı'],
      noBuyWhen:['Cihaz 65 W veya daha düşük adaptörle ihtiyacı karşılıyorsa','PD 3.1/EPR desteği doğrulanmadıysa','Yalnız toplam 140 W ibaresi tek cihazda 140 W sanılıyorsa'],
      technicalSource:'https://ugreen.com.tr/urun/ugreen-nexode-140w-usb-type-c-qc-4-0-pd-3-1-gan-3-portlu-hizli-sarj-cihazi/'
    },
    {
      id:'apple-a2452-140w',category:'charger',asin:'B0D232C5JJ',mpn:'A2452',brand:'Apple',
      name:'Apple A2452 140 W USB-C güç adaptörü',verifiedAt:'2026-08-01',
      userNeed:'Uyumlu 16 inç MacBook Pro için tek portlu 140 W güç adaptörü',
      facts:['140 W USB-C adaptör sınıfı','Tek USB-C port','Apple A2452 model ailesi'],
      bestFor:['Apple tarafından 140 W adaptörle desteklenen MacBook Pro modelleri','Tek portlu orijinal güç zinciri isteyenler'],
      evidence:['MacBook tam modeli','Apple tarafından önerilen adaptör gücü','MagSafe 3 veya uygun 240 W USB-C kablo','Kablonun kutu içeriğinde olup olmadığı'],
      noBuyWhen:['Mevcut adaptör önerilen gücü sağlıyorsa','Çoklu cihaz portu gerekiyorsa','Uygun yüksek güçlü kablo bulunmuyorsa'],
      technicalSource:'https://support.apple.com/tr-tr/102378'
    },
    {
      id:'samsung-ep-t6530-65w',category:'charger',asin:'B09W2HP21R',mpn:'EP-T6530NBEGWW',brand:'Samsung',
      name:'Samsung Trio 65 W iki USB-C ve bir USB-A şarj adaptörü',verifiedAt:'2026-07-30',
      userNeed:'Dizüstü, telefon ve küçük cihaz için üç portlu tek adaptör',
      facts:['Tek portta 65 W sınıfı','İki USB-C ve bir USB-A port','Çoklu portta paylaşılan güç'],
      bestFor:['65 W veya daha düşük USB-C dizüstü','Çoklu cihazlı masa ve seyahat seti'],
      evidence:['Tek port güç ihtiyacı','Çoklu port güç paylaşımı','5 A kablo gereksinimi'],
      noBuyWhen:['Mevcut adaptör ve port sayısı yeterliyse','Aynı anda her portta azami güç bekleniyorsa'],
      technicalSource:'https://www.samsung.com/tr/mobile-accessories/65w-power-adapter-trio-black-ep-t6530nbegww/'
    },
    {
      id:'belkin-avc006-4in1',category:'hub',asin:'B08X5168HM',mpn:'AVC006btSGY',brand:'Belkin',
      name:'Belkin CONNECT AVC006 4’ü 1 arada USB-C hub',verifiedAt:'2026-08-01',
      userNeed:'HDMI ve iki USB-A portunu sade bir USB-C hub ile eklemek',
      facts:['HDMI 1.4 ile 4K@30 Hz','İki USB-A 3.0 port','5 Gbps veri sınıfı','100 W’a kadar PD geçiş; hub için 15 W ayrılır'],
      bestFor:['Ethernet veya kart okuyucu gerekmeyen küçük masa düzeni','Seyahat ve toplantı kullanımı'],
      evidence:['Host USB-C portunda görüntü çıkışı','4K@30 Hz sınırının yeterli olması','PD adaptör gücü ve hub tüketimi','Gerekli USB-A port sayısı'],
      noBuyWhen:['4K@60 Hz, Ethernet veya kart okuyucu gerekiyorsa','Host USB-C portu görüntü vermiyorsa','Mevcut hub gerekli portları sağlıyorsa'],
      technicalSource:'https://www.belkin.com/p/usb-c-4-in-1-multiport-adapter/AVC006btSGY.html'
    },
    {
      id:'ugreen-60515-7in1',category:'hub',asin:'B093FKT9BF',mpn:'60515',brand:'UGREEN',
      name:'UGREEN 60515 7’si 1 arada USB-C hub',verifiedAt:'2026-07-30',
      userNeed:'HDMI, Ethernet, kart okuyucu ve USB portlarını tek hubda toplamak',
      facts:['4K@60 Hz HDMI sınıfı','Gigabit Ethernet','İki USB-A 3.0','SD ve microSD','100 W PD geçiş portu'],
      bestFor:['Çok çevre birimli dizüstü kullanımı','Ev-ofis ve mobil iş istasyonu'],
      evidence:['Host görüntü çıkışı','Ethernet ve kart okuyucu ihtiyacı','PD adaptörünün ayrıca bulunması'],
      noBuyWhen:['Kullanılmayacak portlar tek satın alma gerekçesiyse','Host port yeteneği bilinmiyorsa'],
      technicalSource:'https://www.amazon.com.tr/dp/B093FKT9BF'
    },
    {
      id:'ugreen-25911-hdmi21-3m',category:'display',asin:'B0CFF9T3PS',mpn:'25911',brand:'UGREEN',
      name:'UGREEN 25911 HDMI 2.1 Ultra High Speed kablo 3 m',verifiedAt:'2026-08-01',
      userNeed:'HDMI 2.1 kaynak ile ekranda yüksek çözünürlük veya yenileme bağlantısı',
      facts:['48 Gbps HDMI 2.1 sınıfı','8K@60 Hz ve yüksek yenilemeli 4K beyanı','VRR, ALLM ve eARC','3 metre'],
      bestFor:['4K@120 Hz oyun ve monitör zinciri','eARC veya VRR ihtiyacı'],
      evidence:['Kaynak HDMI sürümü','Ekran HDMI sürümü','Hedef çözünürlük ve yenileme','3 m kablo güzergâhı'],
      noBuyWhen:['Mevcut kablo hedef modu kararlı çalıştırıyorsa','Kaynak veya ekran gerekli özelliği desteklemiyorsa'],
      technicalSource:'https://www.amazon.com.tr/dp/B0CFF9T3PS'
    },
    {
      id:'veggieg-vz631-dp14-2m',category:'display',asin:'B0DN61ZDBQ',mpn:'V-Z631',brand:'VegGieg',
      name:'VegGieg V-Z631 DisplayPort 1.4 kablo 2 m',verifiedAt:'2026-08-01',
      userNeed:'DisplayPort kaynak ve monitör arasında yüksek yenileme bağlantısı',
      facts:['DisplayPort 1.4','32,4 Gbps sınıfı','8K@60 Hz, 4K@144 Hz ve 2K@240 Hz beyanı','2 metre'],
      bestFor:['DisplayPort 1.4 ekran kartı ve monitörler','2 m masaüstü bağlantısı'],
      evidence:['Kaynak ve ekran DisplayPort sürümü','Hedef çözünürlük ve yenileme','Ekran kartı ve monitör bant genişliği'],
      noBuyWhen:['Mevcut kablo hedef modu kararlı sağlıyorsa','Kaynak veya monitör gerekli bant genişliğini desteklemiyorsa'],
      technicalSource:'https://www.amazon.com.tr/dp/B0DN61ZDBQ'
    },
    {
      id:'veggieg-vz623-usbc-dp14-2m',category:'display',asin:'B0DK6QPTFQ',mpn:'V-Z623',brand:'VegGieg',
      name:'VegGieg V-Z623 çift yönlü USB-C ↔ DisplayPort 1.4 kablo 2 m',verifiedAt:'2026-07-30',
      userNeed:'USB-C görüntü çıkışını DisplayPort monitöre veya ters yönde bağlamak',
      facts:['Çift yönlü USB-C / DisplayPort beyanı','8K@60 Hz ve 4K@144 Hz sınıfı','2 metre','Şarj geçişi yok'],
      bestFor:['DisplayPort Alt Mode veya Thunderbolt destekli dizüstüler','Yüksek yenilemeli DisplayPort ekranlar'],
      evidence:['USB-C görüntü çıkışı','Kablo yönü','Hedef çözünürlük ve yenileme','Aynı kablodan şarj beklenmemesi'],
      noBuyWhen:['USB-C portunda görüntü çıkışı yoksa','Aynı kablodan şarj gerekiyorsa','Mevcut kablo kararlı çalışıyorsa'],
      technicalSource:'https://www.amazon.com.tr/dp/B0DK6QPTFQ'
    },
    {
      id:'daytona-hc01-usbc-hdmi-18m',category:'display',asin:'B096G51911',mpn:'HC-01',brand:'Daytona',
      name:'Daytona HC-01 USB-C → HDMI görüntü kablosu 1,8 m',verifiedAt:'2026-08-01',
      userNeed:'USB-C cihazı HDMI TV, projektör veya monitöre bağlamak',
      facts:['USB-C → HDMI tek yönlü kullanım','4K@60 Hz ürün beyanı','1,8 metre','Haricî güç gerektirmeyen tak-çalıştır yapı'],
      bestFor:['Sunum ve seyahat bağlantısı','USB-C görüntü çıkışlı dizüstü veya telefonlar'],
      evidence:['Kaynak USB-C görüntü desteği','Hedef HDMI çözünürlük ve yenileme','Kablonun yönü','Şarj geçişi gerekmediği'],
      noBuyWhen:['Kaynak USB-C portunda görüntü çıkışı yoksa','Aynı bağlantıda şarj geçişi gerekiyorsa','Mevcut hub HDMI ihtiyacını karşılıyorsa'],
      technicalSource:'https://www.amazon.com.tr/dp/B096G51911'
    }
  ].map(item=>({...item,amazonUrl:amazonProductUrl(item.asin)}));

  const productClasses=[
    {id:'usb-c-pd',category:'charger',name:'USB-C PD ve PPS şarj cihazları',query:'USB C PD PPS GaN şarj cihazı 45W 65W 100W',tool:'/hesaplama/usb-c-sarj-cihazi-kablo-uygunluk/',evidence:['Cihazın kabul ettiği watt','Tek port ve toplam güç ayrımı','Kablo güç sınıfı'],noBuyWhen:'Mevcut adaptör görevi güvenli biçimde karşılıyorsa.'},
    {id:'usb-c-epr',category:'charger',name:'USB-C 240 W EPR kablolar',query:'USB C 240W EPR e-marker şarj kablosu',tool:'/hesaplama/usb-c-sarj-cihazi-kablo-uygunluk/',evidence:['PD 3.1 EPR gereksinimi','240 W işaretlemesi','Veri ve görüntü ihtiyacının ayrıca kontrolü'],noBuyWhen:'Cihaz 100 W veya altında çalışıyorsa.'},
    {id:'usb-c-hub',category:'hub',name:'USB-C hub ve dock',query:'USB C hub HDMI Ethernet 100W PD 10Gbps',tool:'/hesaplama/usb-c-hub-goruntu-pd-uygunluk/',evidence:['Host görüntü desteği','Gerekli portlar','PD geçiş üst sınırı'],noBuyWhen:'Mevcut hub gerekli bütün görevleri sağlıyorsa.'},
    {id:'hdmi-ultra',category:'display',name:'Ultra High Speed HDMI kablolar',query:'Ultra High Speed HDMI 2.1 sertifikalı kablo',tool:'/hesaplama/hdmi-displayport-cozunurluk-yenileme-uygunluk/',evidence:['Kaynak ve ekran HDMI sürümü','Hedef çözünürlük/yenileme','Kablo uzunluğu'],noBuyWhen:'Mevcut kablo hedef görüntü modunu kararlı sağlıyorsa.'},
    {id:'displayport',category:'display',name:'DisplayPort görüntü kabloları',query:'DisplayPort 1.4 DP40 DP80 kablo',tool:'/hesaplama/hdmi-displayport-cozunurluk-yenileme-uygunluk/',evidence:['Kaynak ve ekran DP sürümü','Çözünürlük/yenileme','Kablo yönü ve uzunluğu'],noBuyWhen:'Sorun sürücü, port veya ekran ayarındaysa.'},
    {id:'travel-adapter',category:'travel',name:'Topraklı seyahat priz adaptörleri',query:'topraklı seyahat priz adaptörü',tool:'/hesaplama/seyahat-priz-adaptoru-voltaj-donusturucu-uygunluk/',evidence:['Cihazın giriş gerilimi/frekansı','Fiş biçimi','Topraklama sürekliliği'],noBuyWhen:'Voltaj dönüştürücü gerekiyorsa veya topraklama kayboluyorsa.'},
    {id:'car-usbc',category:'travel',name:'Araç USB-C PD şarj cihazları',query:'araç USB C PD PPS şarj cihazı 30W 65W',tool:'/hesaplama/arac-12v-priz-inverter-yuk-uygunluk/',evidence:['Araç prizinin 12–24 V ve hasarsız olması','Cihaz güç profili','Tek/çift port paylaşımı'],noBuyWhen:'Araçtaki mevcut USB çıkışı ihtiyacı karşılıyorsa veya priz ısınıyorsa.'},
    {id:'car-inverter',category:'travel',name:'Düşük güçlü araç inverterleri',query:'araç inverter 150W saf sinüs',tool:'/hesaplama/arac-12v-priz-inverter-yuk-uygunluk/',evidence:['Araç priz akım sınırı','Yükün sürekli/tepe wattı','Saf sinüs ihtiyacı'],noBuyWhen:'Isıtıcı, kettle, motorlu veya tıbbi cihaz kullanılacaksa.'},
    {id:'foldable-solar',category:'travel',name:'Katlanabilir güneş panelleri',query:'katlanabilir güneş paneli power station',tool:'/hesaplama/katlanabilir-gunes-paneli-power-station-uygunluk/',evidence:['Power station giriş Voc/Isc/W sınırı','Konnektör ve polarite','Taşınabilir kullanım'],noBuyWhen:'Yalnız watt benzerliğine göre veya sabit GES için seçiliyorsa.'},
    {id:'ethernet-adapter',category:'hub',name:'USB-A / USB-C Gigabit Ethernet adaptörleri',query:'USB C USB A Gigabit Ethernet adaptörü',tool:'/hesaplama/usb-ethernet-adaptoru-port-hiz-uygunluk/',evidence:['Host port tipi','Gerçek ağ hızı','İşletim sistemi desteği'],noBuyWhen:'Cihazda çalışan Ethernet portu zaten varsa.'}
  ].map(item=>({...item,amazonUrl:amazonSearchUrl(item.query)}));

  return {version,affiliateTag,verificationMaxAgeDays,generatedAt,products,productClasses,amazonProductUrl,amazonSearchUrl};
});
