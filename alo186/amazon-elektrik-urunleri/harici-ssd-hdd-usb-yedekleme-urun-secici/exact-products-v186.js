(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  if(root&&typeof root==='object')root.Alo186BackupExactProductsV186=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(){
  'use strict';

  const version=186;
  const affiliateTag='alo186rehber-21';
  const verifiedAt='2026-08-01';
  const verificationMaxAgeDays=45;
  const siteOrigin='https://alo186.com';
  const routePath='/amazon-elektrik-urunleri/harici-ssd-hdd-usb-yedekleme-urun-secici/';

  function amazonProductUrl(asin){
    return `https://www.amazon.com.tr/dp/${encodeURIComponent(asin)}?tag=${encodeURIComponent(affiliateTag)}`;
  }
  function dateOnly(value){
    const date=new Date(`${value}T00:00:00Z`);
    return Number.isNaN(date.getTime())?null:date;
  }
  function verificationStatus(item,now=new Date()){
    const checked=dateOnly(item&&item.verifiedAt);
    const today=dateOnly(now.toISOString().slice(0,10));
    if(!checked||!today)return {fresh:false,ageDays:null};
    const ageDays=Math.max(0,Math.floor((today-checked)/86400000));
    return {fresh:ageDays<=verificationMaxAgeDays,ageDays};
  }

  const products=[
    {
      id:'samsung-t7-shield-1tb-black',category:'ssd',asin:'B09VLK9W3S',mpn:'MU-PE1T0S/WW',brand:'Samsung',
      name:'Samsung T7 Shield 1 TB siyah taşınabilir SSD',verifiedAt,
      userNeed:'Sık taşınan büyük dosyalarda hızlı kopyalama, kısa geri yükleme süresi ve fiziksel çevreye karşı daha dayanıklı bir ikinci kopya oluşturmak',
      facts:['1 TB kapasite','USB 3.2 Gen 2 10 Gbps arayüz','1.050 MB/sn’ye kadar sıralı okuma ve 1.000 MB/sn’ye kadar sıralı yazma','Kontrollü test koşullarına dayalı IP65 sınıfı','AES 256-bit donanım şifreleme desteği'],
      bestFor:['Fotoğraf, video ve proje dosyalarını sık taşıyan kullanıcılar','USB 3.2 Gen 2 ve UASP destekli ana cihazda kısa RTO hedefleyen yedekleme düzenleri'],
      evidence:['Ana cihaz ve kablonun USB 3.2 Gen 2 ile UASP desteklemesi','1 TB kapasitenin yedek büyüme payı ve sürüm geçmişi için yeterli olması','Disk sağlık ve gerçek örnek geri yükleme testinin yapılması','Tek kopya yerine bağımsız ikinci veya çevrimdışı kopya planlanması'],
      noBuyWhen:['Mevcut güvenli disk kapasite ve geri yükleme testini karşılıyorsa','Yalnız yüksek arşiv kapasitesi gerekiyor ve hız öncelikli değilse','IP65 ifadesi her koşulda su veya darbe garantisi sanılıyorsa','Devam eden veri kaybı veya fiziksel disk arızası için kurtarma çözümü olarak düşünülüyorsa'],
      technicalSource:'https://www.samsung.com/tr/memory-storage/portable-ssd/t7-shield-1tb-black-external-storage-nvme-1050-mbs-mu-pe1t0s-ww/'
    },
    {
      id:'wd-elements-portable-2tb',category:'hdd',asin:'B06W55K9N6',mpn:'WDBU6Y0020BBK-WESN',brand:'Western Digital',
      name:'WD Elements Portable 2 TB harici HDD',verifiedAt,
      userNeed:'Masaüstünde veya kontrollü taşımada yüksek kapasiteyi SSD maliyetine çıkmadan bağımsız ikinci yedek kopyaya dönüştürmek',
      facts:['2 TB kapasite','USB 3.2 Gen 1 ve USB 3.0 sınıfı bağlantı','Micro-B cihaz konektörü','Yaklaşık 110,5 × 82 × 15 mm boyut ve 130 g ağırlık','Windows için tak-çalıştır; diğer sistemlerde yeniden biçimlendirme gerekebilir'],
      bestFor:['Fotoğraf, belge ve medya arşivinde kapasite öncelikli ikinci kopya','Diskin çoğunlukla sabit ve darbelerden uzak tutulduğu ev-ofis kullanımı'],
      evidence:['2 TB kapasitenin hedef veri, büyüme payı ve sürüm geçmişine yetmesi','Bilgisayarda uygun USB portu ve sağlam kablo bulunması','Dosya sistemi ile işletim sistemi uyumunun doğrulanması','SMART sağlık kontrolü ve örnek dosya geri yükleme testinin yapılması'],
      noBuyWhen:['Sık taşıma, darbe veya çok kısa geri yükleme süresi baskınsa','Mevcut HDD sağlık, kapasite ve geri yükleme testini geçiyorsa','Tek uzun vadeli kopya olarak kullanılacaksa','Tıklama, bağlantı kopması, aşırı ısınma veya devam eden veri kaybı varsa'],
      technicalSource:'https://www.westerndigital.com/products/portable-drives/wd-elements-portable-usb-3-0-hdd?sku=WDBU6Y0020BBK-WESN'
    },
    {
      id:'kingston-datatraveler-max-256gb',category:'usb',asin:'B0B57T5G5L',mpn:'DTMAX/256GB',brand:'Kingston',
      name:'Kingston DataTraveler Max 256 GB USB-C flash bellek',verifiedAt,
      userNeed:'USB-C cihazlar arasında büyük dosyaları hızlı taşımak ve küçük bir çevrimdışı kurtarma veya acil çalışma seti hazırlamak',
      facts:['256 GB kapasite','USB 3.2 Gen 2 arayüz','USB-C konektör','1.000 MB/sn’ye kadar okuma ve 900 MB/sn’ye kadar yazma sınıfı','Yaklaşık 82 × 22 × 9 mm boyut ve 12 g ağırlık'],
      bestFor:['USB-C bilgisayarda hızlı geçici aktarım ve doğrulanmış kurtarma medyası','Ana yedek dışında küçük, taşınabilir ve sınırlı çevrimdışı dosya seti'],
      evidence:['Cihazın USB-C veri aktarımını ve gerekli USB 3.2 hızını desteklemesi','256 GB kapasitenin yalnız seçilen kurtarma veya çalışma setine yetmesi','Önyüklenebilir medya gerekiyorsa işletim sistemi aracının desteklenmesi','Oluşturulan medyanın açılış ve dosya bütünlüğü testinin yapılması'],
      noBuyWhen:['Tek ve uzun vadeli yedek kopya olarak kullanılacaksa','Mevcut USB bellek aynı görevi ve bütünlük testini karşılıyorsa','USB-C portu yalnız şarj destekliyor veya gerekli hız sınıfını sağlamıyorsa','Kayıp veriyi kurtarma ya da arızalı diski onarma ürünü sanılıyorsa'],
      technicalSource:'https://www.kingston.com/tr/usb-flash-drives/datatraveler-max-usb-c-flash-drive'
    },
    {
      id:'sandisk-ultra-dual-drive-go-256gb',category:'usb',asin:'B07YYJL21Z',mpn:'SDDDC3-256G-G46',brand:'SanDisk',
      name:'SanDisk Ultra Dual Drive Go 256 GB USB-C ve USB-A flash bellek',verifiedAt,
      userNeed:'USB-C telefon veya tablet ile USB-A bilgisayar arasında küçük yedek ve aktarım setini ayrı adaptör kullanmadan taşımak',
      facts:['256 GB kapasite','USB-C ve USB-A çift konektör','USB 3.2 Gen 1 arayüz','Uyumlu varyantta 400 MB/sn’ye kadar sıralı okuma sınıfı','Yaklaşık 44,45 × 12,19 × 8,64 mm boyut'],
      bestFor:['USB-C mobil cihaz ile USB-A bilgisayar arasında dosya aktarımı','Ana yedeğin yanında küçük kurtarma veya seyahat dosya seti'],
      evidence:['Telefon veya tabletin USB OTG ve dosya sistemi desteği','USB-A ve USB-C uçların kullanılacak cihazlarla fiziksel uyumu','256 GB kapasitenin seçilen veri seti için yeterli olması','Kopya sonrası checksum veya örnek dosya açma testi'],
      noBuyWhen:['Tek uzun vadeli veri yedeği olarak kullanılacaksa','Mevcut çift uçlu bellek kapasite ve bütünlük testini karşılıyorsa','Mobil cihaz OTG veya gerekli dosya sistemini desteklemiyorsa','Dönen konektör mekanizması veya uçlarda fiziksel hasar varsa'],
      technicalSource:'https://www.sandisk.com/tr-tr/products/usb-flash-drives/sandisk-ultra-dual-drive-go-usb-3-1-type-c?sku=SDDDC3-256G-G46'
    }
  ].map(item=>({...item,amazonUrl:amazonProductUrl(item.asin)}));

  function freshProducts(now=new Date()){
    return products.filter(item=>verificationStatus(item,now).fresh);
  }
  function knowledgeGraph(now=new Date()){
    const fresh=freshProducts(now);
    const termsetId=`${siteOrigin}${routePath}#verified-models`;
    const listId=`${siteOrigin}${routePath}#verified-model-list`;
    const brands=[...new Set(fresh.map(item=>item.brand))].sort((a,b)=>a.localeCompare(b,'tr'));
    return {'@context':'https://schema.org','@graph':[
      {'@type':'DefinedTermSet','@id':termsetId,name:'ALO186 doğrulanmış yedekleme depolama modelleri',hasDefinedTerm:fresh.map(item=>({'@id':`${siteOrigin}${routePath}#${item.id}`}))},
      {'@type':'ItemList','@id':listId,name:'Doğrulanmış yedekleme depolama modelleri',numberOfItems:fresh.length,itemListElement:fresh.map((item,index)=>({'@type':'ListItem',position:index+1,item:{'@id':`${siteOrigin}${routePath}#${item.id}`}}))},
      ...brands.map(name=>({'@type':'Brand','@id':`${siteOrigin}/knowledge-graph/brand/${encodeURIComponent(name.toLowerCase())}#brand`,name})),
      ...fresh.map(item=>({
        '@type':'DefinedTerm','@id':`${siteOrigin}${routePath}#${item.id}`,name:item.name,termCode:item.mpn,
        description:`${item.userNeed}. Teknik kontrol tarihi: ${item.verifiedAt}.`,
        identifier:[{'@type':'PropertyValue',propertyID:'ASIN',value:item.asin},{'@type':'PropertyValue',propertyID:'MPN',value:item.mpn}],
        inDefinedTermSet:{'@id':termsetId},subjectOf:item.technicalSource,
        additionalProperty:item.facts.map((value,index)=>({'@type':'PropertyValue',name:`Doğrulanan teknik alan ${index+1}`,value}))
      }))
    ]};
  }

  return {version,affiliateTag,verifiedAt,verificationMaxAgeDays,siteOrigin,routePath,products,amazonProductUrl,verificationStatus,freshProducts,knowledgeGraph};
});
