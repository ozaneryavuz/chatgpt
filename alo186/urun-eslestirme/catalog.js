(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports){module.exports=api;}
  root.Alo186ProductCatalog=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(){
  const affiliateTag='alo186hazirlik-21';
  const verifiedAt='2026-07-27';

  function amazonProductUrl(asin){
    const base=`https://www.amazon.com.tr/dp/${encodeURIComponent(asin)}`;
    return affiliateTag?`${base}?tag=${encodeURIComponent(affiliateTag)}`:base;
  }
  function amazonSearchUrl(query){
    const base=`https://www.amazon.com.tr/s?k=${encodeURIComponent(query)}`;
    return affiliateTag?`${base}&tag=${encodeURIComponent(affiliateTag)}`:base;
  }

  const categories=[
    {id:'powerbank',name:'Telefon ve mobil cihaz için powerbank',mode:'direct',risk:'consumer',description:'Kapasite, USB-C çıkış gücü ve kablosuz şarj ihtiyacına göre ürün sayfası teknik verilerini karşılaştırır.',searchQuery:'USB C PD powerbank 20000 mAh dijital ekran'},
    {id:'surge_strip',name:'Akım korumalı grup priz',mode:'direct',risk:'consumer',description:'Priz sayısı, joule ve USB ihtiyacına göre tak-çalıştır grup prizleri karşılaştırır. Pano tipi SPD ve topraklamanın yerine geçmez.',searchQuery:'akım korumalı grup priz joule'},
    {id:'mini_ups',name:'Modem ve fiber ONT için mini UPS',mode:'guide',risk:'compatibility',description:'Voltaj, polarite, jak ölçüsü, toplam watt ve geçiş davranışı doğrulanmadan ürün seçilmemelidir.',searchQuery:'modem mini UPS 12V 9V 5V'},
    {id:'emergency_light',name:'Şarjlı acil aydınlatma',mode:'guide',risk:'consumer',description:'Düşük mod çalışma süresi, fiziksel düğme, pil göstergesi ve asma/taşıma biçimini kontrol edin.',searchQuery:'şarjlı acil durum lambası kamp lambası'},
    {id:'smoke_alarm',name:'Fotoelektrik duman alarmı',mode:'guide',risk:'safety',description:'EN 14604 işareti, test düğmesi, düşük pil uyarısı, ses seviyesi ve son kullanım bilgisini doğrulayın.',searchQuery:'EN 14604 fotoelektrik duman dedektörü'},
    {id:'power_station',name:'Taşınabilir güç istasyonu',mode:'guide',risk:'compatibility',description:'Wh kapasitesi, sürekli/tepe güç, dalga biçimi, batarya kimyası ve şarj girişleri yük hesabıyla birlikte seçilmelidir.',searchQuery:'LiFePO4 taşınabilir güç istasyonu power station'},
    {id:'outlet_tester',name:'Priz ve RCD test cihazı',mode:'guide',risk:'measurement',description:'Gösterge yalnız temel bağlantı hatalarını ön kontrol eder; izolasyon, topraklama direnci ve koruma açma testi yerine geçmez.',searchQuery:'priz test cihazı RCD tester'}
  ];

  const products=[
    {
      id:'anker-prime-a1336',category:'powerbank',asin:'B0BYNZXFM2',name:'Anker Prime A1336 20.000 mAh 200 W',brand:'Anker',status:'verified_listing',verifiedAt,
      attributes:{capacityMah:20000,energyWh:72,maxOutputW:200,wireless:false,usbCPorts:2,usbAPorts:1,display:true},
      strengths:['Yüksek USB-C çıkışı','Dijital ekran','20.000 mAh / 72 Wh'],limits:['Yüksek fiyat ve 544 g ağırlık','Samsung SFC 2.0 desteği ürün sayfasında sınırlı belirtilmiş'],
      sourceNote:'ASIN ve teknik ürün sayfası alanları kontrol edildi; fiyat ve stok ALO186 tarafından gösterilmez.',url:amazonProductUrl('B0BYNZXFM2')
    },
    {
      id:'xiaomi-wireless-10000',category:'powerbank',asin:'B09TWRHGWV',name:'Xiaomi 10 W Wireless Power Bank 10.000',brand:'Xiaomi',status:'verified_listing',verifiedAt,
      attributes:{capacityMah:10000,energyWh:null,maxOutputW:10,wireless:true,usbCPorts:1,usbAPorts:null,display:false},
      strengths:['Kablosuz şarj','10.000 mAh','Düşük akım modu'],limits:['Yüksek güçlü dizüstü ihtiyacı için uygun kabul edilmemeli','Kablolu maksimum çıkış üründe yeniden doğrulanmalı'],
      sourceNote:'ASIN, 10.000 mAh ve 10 W kablosuz özellikleri ürün sayfasından kontrol edildi.',url:amazonProductUrl('B09TWRHGWV')
    },
    {
      id:'samsung-eb-u2510x',category:'powerbank',asin:'B0CVGVG7NW',name:'Samsung EB-U2510X 10.000 mAh Kablosuz Powerbank',brand:'Samsung',status:'verified_listing',verifiedAt,
      attributes:{capacityMah:10000,energyWh:null,maxOutputW:null,wireless:true,usbCPorts:null,usbAPorts:null,display:false},
      strengths:['Kablosuz kullanım','10.000 mAh','Kompakt sınıf'],limits:['Çıkış gücü ve port sayısı Amazon ürün sayfasında satın alma öncesi yeniden doğrulanmalı'],
      sourceNote:'ASIN, model ve kapasite ürün sayfasından kontrol edildi; eksik teknik alanlar bilinmiyor olarak tutuldu.',url:amazonProductUrl('B0CVGVG7NW')
    },
    {
      id:'tuncmatik-tsk6136',category:'surge_strip',asin:'B07CST4766',name:'Tunçmatik TSK6136 PowerSurge 5 Priz 1050 J',brand:'Tunçmatik',status:'verified_listing',verifiedAt,
      attributes:{outlets:5,joules:1050,maxCurrentA:10,maxPowerW:null,usbPorts:0,cableM:1.5},
      strengths:['1050 joule','5 çocuk emniyetli priz','1,5 m kablo'],limits:['10 A nominal akım','Pano tipi SPD ve uygun topraklamanın yerine geçmez'],
      sourceNote:'ASIN, 1050 J, 8000 A tepe, 10 A nominal ve 5 priz bilgileri ürün sayfasından kontrol edildi.',url:amazonProductUrl('B07CST4766')
    },
    {
      id:'viko-multilet-6',category:'surge_strip',asin:'B08L9KVRP1',name:'Viko Multilet Şok Korumalı 6’lı Grup Priz',brand:'Viko',status:'verified_listing',verifiedAt,
      attributes:{outlets:6,joules:282,maxCurrentA:16,maxPowerW:3500,usbPorts:0,cableM:1.5},
      strengths:['6 priz','16 A / 3500 W etiket bilgisi','Çocuk koruma'],limits:['282 joule seviyesi','Pano tipi koruma yerine kullanılamaz'],
      sourceNote:'ASIN, 6 priz, 16 A, 3500 W, 282 J ve 1,7 kV koruma seviyesi ürün açıklamasından kontrol edildi.',url:amazonProductUrl('B08L9KVRP1')
    },
    {
      id:'tuncmatik-tsk5015',category:'surge_strip',asin:'B08KW6X13Y',name:'Tunçmatik PowerSurge 5 Priz + USB TSK5015',brand:'Tunçmatik',status:'verified_listing',verifiedAt,
      attributes:{outlets:5,joules:null,maxCurrentA:null,maxPowerW:null,usbPorts:2,cableM:null},
      strengths:['5 priz','USB çıkışları','Elektronik cihaz kullanım senaryosu'],limits:['Joule ve nominal akım satın alma öncesi ürün etiketinden doğrulanmalı'],
      sourceNote:'ASIN, model, 5 priz ve USB özellikleri ürün sayfasından kontrol edildi; bilinmeyen alanlar puanda cezalandırılır.',url:amazonProductUrl('B08KW6X13Y')
    },
    {
      id:'cata-ct9186',category:'surge_strip',asin:'B09YTYTZ4J',name:'Cata CT-9186 Tekli Akım Korumalı Priz 918 J',brand:'Cata',status:'verified_listing',verifiedAt,
      attributes:{outlets:1,joules:918,maxCurrentA:null,maxPowerW:4000,usbPorts:0,cableM:0},
      strengths:['918 joule','Tek cihaz için kompakt kullanım','LED gösterge'],limits:['Tek priz','4000 W ifadesi ürün sayfasında tekrar doğrulanmalı','Pano tipi SPD yerine geçmez'],
      sourceNote:'ASIN, 918 J ve 4000 W ürün başlığı/açıklamasından kontrol edildi.',url:amazonProductUrl('B09YTYTZ4J')
    }
  ];

  function getCategory(id){return categories.find(c=>c.id===id)||null;}
  function productsFor(category){return products.filter(p=>p.category===category&&p.status==='verified_listing');}
  function searchUrl(category){const c=getCategory(category);return c?amazonSearchUrl(c.searchQuery):'https://www.amazon.com.tr';}

  return {affiliateTag,verifiedAt,categories,products,getCategory,productsFor,amazonProductUrl,amazonSearchUrl,searchUrl};
});
