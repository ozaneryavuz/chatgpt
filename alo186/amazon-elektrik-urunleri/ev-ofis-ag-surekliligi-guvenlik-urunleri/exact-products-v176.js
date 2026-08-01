(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  if(root&&typeof root==='object')root.Alo186ExactHomeNetworkSafetyV176=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(){
  'use strict';

  const version=176;
  const affiliateTag='alo186rehber-21';
  const generatedAt='2026-08-01';
  const verificationMaxAgeDays=45;
  const siteOrigin='https://alo186.com';
  const routePath='/amazon-elektrik-urunleri/ev-ofis-ag-surekliligi-guvenlik-urunleri/';

  function amazonProductUrl(asin){
    return `https://www.amazon.com.tr/dp/${encodeURIComponent(asin)}?tag=${encodeURIComponent(affiliateTag)}`;
  }
  function amazonSearchUrl(query){
    return `https://www.amazon.com.tr/s?k=${encodeURIComponent(query)}&tag=${encodeURIComponent(affiliateTag)}`;
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
      id:'tp-link-tl-pa7017p-kit',category:'network',asin:'B0859MDSFX',mpn:'TL-PA7017P KIT',brand:'TP-Link',
      name:'TP-Link TL-PA7017P KIT AV1000 priz geçişli powerline başlangıç kiti',verifiedAt:'2026-08-01',
      userNeed:'Yeni Ethernet kablosu çekmeden aynı elektrik tesisatı üzerinden uzak bir odadaki tek cihazı kablolu ağa bağlamak',
      facts:['HomePlug AV2 ve 1000 Mbps fiziksel bağlantı sınıfı','Bir Gigabit Ethernet portu','16 A sınıfı priz geçişi','2,7 W azami, 2,3 W tipik ve 0,5 W bekleme tüketimi','128 bit AES powerline güvenliği'],
      bestFor:['Modem ile masaüstü bilgisayar, TV veya oyun konsolu arasında kablo çekilemeyen evler','Ürünü doğrudan duvar prizinde gerçek hız testiyle değerlendirecek kullanıcılar'],
      evidence:['İki prizin aynı elektrik sisteminde ve uygun devre yolunda bulunması','Powerline adaptörlerinin uzatma kablosu yerine doğrudan duvar prizine takılması','Gerçek indirme, yükleme ve gecikme testinin yapılması','Priz geçişindeki bağlı yükün 16 A ve tesisat sınırlarını aşmaması'],
      noBuyWhen:['Mevcut Ethernet veya Wi-Fi bağlantısı görevi kararlı biçimde karşılıyorsa','Ayrı sayaç, pano, faz veya yoğun elektriksel parazit nedeniyle bağlantı kurulamadıysa','1000 Mbps ibaresi gerçek internet hızının garantisi sanılıyorsa','UPS, parafudr veya tesisat onarımı yerine kullanılacaksa'],
      technicalSource:'https://www.tp-link.com/tr/home-networking/powerline/tl-pa7017p-kit/'
    },
    {
      id:'tp-link-tl-sg105',category:'network',asin:'B00A128S24',mpn:'TL-SG105',brand:'TP-Link',
      name:'TP-Link TL-SG105 beş port Gigabit yönetilemeyen masaüstü switch',verifiedAt:'2026-08-01',
      userNeed:'Modem veya yönlendiricideki tek Ethernet bağlantısını beş Gigabit porta kadar sade ve fansız bir ağ dağıtımına genişletmek',
      facts:['Beş adet 10/100/1000 Mbps RJ45 port','Auto-Negotiation ve Auto-MDI/MDIX','Yapılandırma gerektirmeyen tak-çalıştır sınıf','IEEE 802.1p trafik önceliği ve IGMP Snooping'],
      bestFor:['Ev-ofis bilgisayar, TV, oyun konsolu ve NAS bağlantıları','PoE veya gelişmiş VLAN yönetimi gerektirmeyen küçük kablolu ağlar'],
      evidence:['İnternet ve yerel ağ cihazlarının gerçekten Gigabit port desteklemesi','Kullanılacak Ethernet kablolarının en az Cat5e/Cat6 ve sağlam olması','Beş portun yeterli olduğunun ve PoE gerekmeyeceğinin doğrulanması'],
      noBuyWhen:['Yönlendiricinin mevcut portları yeterliyse','PoE, 2.5G, VLAN, link aggregation veya yönetilebilir ağ özellikleri gerekiyorsa','Elektrik kesintisinde çalışması bekleniyor fakat adaptörü yedeklenmiyorsa'],
      technicalSource:'https://www.tp-link.com/tr/business-networking/unmanaged-switch/tl-sg105/'
    },
    {
      id:'tapo-c310',category:'camera',asin:'B08JLR2751',mpn:'Tapo C310',brand:'Tapo',
      name:'Tapo C310 2K 3 MP dış mekân Wi-Fi ve Ethernet güvenlik kamerası',verifiedAt:'2026-08-01',
      userNeed:'Ev girişini veya dış alanı Wi-Fi ya da Ethernet üzerinden yerel kayıt ve hareket bildirimiyle izlemek',
      facts:['2304 × 1296 piksel 3 MP görüntü','Wi-Fi veya Ethernet ağ bağlantısı','IP66 dış ortam koruması','Yaklaşık 30 metre kızılötesi gece görüşü','İki yönlü ses ve microSD yerel kayıt'],
      bestFor:['Elektrik ve ağ erişimi bulunan konut dış alanları','Bulut hizmeti zorunlu olmadan microSD ile yerel kayıt isteyen kullanıcılar'],
      evidence:['Montaj noktasında güvenli ve üreticiye uygun enerji beslemesi','Wi-Fi kapsaması veya Ethernet kablo güzergâhı','Görüntülenecek alan için mahremiyet ve mevzuat sınırları','Donanım sürümüne uygun microSD kapasitesi ve yazılım güncelliği'],
      noBuyWhen:['Bataryalı veya tamamen kablosuz çalışma bekleniyorsa','Mevcut kamera görüş, kayıt ve bildirim ihtiyacını karşılıyorsa','Profesyonel CCTV, uzun süreli yasal kayıt veya merkezi alarm sistemi yerine kullanılacaksa','Montaj için tehlikeli yüksekte çalışma ya da açık elektrik müdahalesi gerekiyorsa'],
      technicalSource:'https://www.tp-link.com/tr/home-networking/cloud-camera/tapo-c310/'
    },
    {
      id:'tapo-c200',category:'camera',asin:'B07XLML2YS',mpn:'Tapo C200',brand:'Tapo',
      name:'Tapo C200 1080p yatay ve dikey hareketli iç mekân Wi-Fi kamerası',verifiedAt:'2026-08-01',
      userNeed:'Ev içinde tek odanın geniş açılı izlenmesi, hareket bildirimi ve iki yönlü ses ihtiyacını düşük kurulum karmaşıklığıyla karşılamak',
      facts:['1920 × 1080 piksel görüntü','360 derece yatay ve 114 derece dikey hareket','Yaklaşık 9 metre kızılötesi gece görüşü','İki yönlü ses ve hareket bildirimi','microSD yerel depolama; kapasite donanım sürümüne göre doğrulanmalı'],
      bestFor:['İç mekânda evcil hayvan, giriş veya tek oda takibi','Gizlilik modu ve yerel kayıt seçeneğini kullanacak kullanıcılar'],
      evidence:['Yalnız 2.4 GHz Wi-Fi kapsamasının yeterli olması','Kamera konumunun özel yaşam alanlarını gereksiz kaydetmemesi','Tam donanım sürümü, firmware ve microSD uyumluluğunun kontrolü'],
      noBuyWhen:['Dış ortam veya yağmura açık kullanım planlanıyorsa','Ethernet ya da PoE bağlantısı zorunluysa','Mevcut kamera aynı alanı yeterli kalitede izliyorsa','Yaşam güvenliği, bebek sağlığı veya profesyonel alarm sistemi için tek güvenlik katmanı sayılacaksa'],
      technicalSource:'https://www.tapo.com/tr/product/smart-camera/tapo-c200/'
    },
    {
      id:'yeelight-ylyd04yi',category:'lighting',asin:'B07XGJ163F',mpn:'YLYD04YI',brand:'Yeelight',
      name:'Yeelight YLYD04YI kablosuz şarj pedli çıkarılabilir gece lambası',verifiedAt:'2026-08-01',
      userNeed:'Yatak başında düşük seviyeli gece ışığı ile Qi uyumlu telefonu aynı masaüstü cihazında şarj etmek',
      facts:['Qi kablosuz şarj pedi','Çıkarılabilir manyetik gece lambası','Yaklaşık 10 lm sıcak ve 30 lm soğuk ışık sınıfı','2700 K ve 5000 K iki ışık rengi','950 mAh dahili lityum polimer batarya ve 15 W azami cihaz gücü'],
      bestFor:['Gece yön bulma ve başucu aydınlatması','Qi uyumlu telefon ve sade masa düzeni'],
      evidence:['Telefonun Qi kablosuz şarj desteği','Kılıf kalınlığının üretici sınırına uygunluğu','5–12 V / 2 A giriş sağlayan güvenli adaptör ve kablo','Işığın acil aydınlatma değil konfor ürünü olduğunun anlaşılması'],
      noBuyWhen:['Mevcut gece lambası ve şarj cihazı ihtiyacı karşılıyorsa','Telefon Qi desteklemiyorsa','Kaçış yolu veya mevzuata tabi acil aydınlatma yerine kullanılacaksa','Islak ortam, aşırı ısınma veya hasarlı kablo/priz koşulu varsa'],
      technicalSource:'https://www.yeelight.com/en_US/product/fuji'
    }
  ].map(item=>({...item,amazonUrl:amazonProductUrl(item.asin)}));

  const productClasses=[
    {id:'powerline-kit',category:'network',name:'Powerline ağ başlangıç kitleri',query:'HomePlug AV2 Gigabit priz geçişli powerline kit',tool:'/hesaplama/modem-internet-yedekleme/',evidence:['aynı elektrik sistemi','gerçek priz bazlı hız testi','doğrudan duvar prizi kullanımı'],noBuyWhen:'Wi-Fi veya Ethernet zaten yeterliyse ya da ayrı pano/faz bağlantısı doğrulanmadıysa.'},
    {id:'gigabit-switch',category:'network',name:'Yönetilemeyen Gigabit masaüstü switch',query:'5 port Gigabit yönetilemeyen metal switch',tool:'/hesaplama/kamera-nvr-poe-yedek-guc-uygunluk/',evidence:['port sayısı','Gigabit uç cihazlar','PoE ve yönetim ihtiyacı'],noBuyWhen:'Mevcut yönlendirici portları yeterliyse veya PoE/2.5G/VLAN gerekiyorsa.'},
    {id:'usb-ethernet-adapter',category:'network',name:'USB 3.0 Gigabit Ethernet adaptörü',query:'USB 3.0 Gigabit Ethernet RJ45 adaptör',tool:'/hesaplama/usb-c-hub-goruntu-pd-uygunluk/',evidence:['USB-A veya USB-C port tipi','işletim sistemi sürücüsü','Gigabit ağ ve kablo'],noBuyWhen:'Cihazda çalışan Ethernet portu varsa veya USB portu gerekli hızı sağlayamıyorsa.'},
    {id:'cat6-patch-cable',category:'network',name:'Cat6 hazır Ethernet patch kablosu',query:'Cat6 UTP hazır Ethernet patch kablo saf bakır',tool:'/hesaplama/kablo-gerilim-dusumu/',evidence:['gerekli uzunluk','RJ45 uç kalitesi','saf bakır ile CCA ayrımı'],noBuyWhen:'Mevcut kablo hatasız Gigabit bağlantı sağlıyorsa veya sabit bina kablolaması uzmanlık gerektiriyorsa.'},
    {id:'indoor-wifi-camera',category:'camera',name:'İç mekân hareketli Wi-Fi kamera',query:'iç mekan 2K pan tilt WiFi kamera microSD gizlilik modu',tool:'/hesaplama/kamera-nvr-poe-yedek-guc-uygunluk/',evidence:['Wi-Fi kapsaması','gizlilik alanları','microSD donanım sürümü'],noBuyWhen:'Dış ortam, PoE, profesyonel kayıt veya mevcut kameradan farklı gerçek ihtiyaç yoksa.'},
    {id:'outdoor-network-camera',category:'camera',name:'Dış mekân Wi-Fi ve Ethernet kamera',query:'IP66 2K dış mekan WiFi Ethernet güvenlik kamerası microSD',tool:'/hesaplama/kamera-nvr-poe-yedek-guc-uygunluk/',evidence:['IP koruma','güvenli enerji ve kablo güzergâhı','mahremiyet ve görüş alanı'],noBuyWhen:'Bataryalı çalışma bekleniyorsa veya profesyonel CCTV tasarımının yerine kullanılacaksa.'},
    {id:'surveillance-microsd',category:'camera',name:'Kamera için yüksek dayanımlı microSD kart',query:'high endurance microSD güvenlik kamerası 128GB 256GB',tool:'/hesaplama/kamera-nvr-poe-yedek-guc-uygunluk/',evidence:['kamera azami kapasitesi','dayanıklılık sınıfı','format ve kayıt döngüsü'],noBuyWhen:'Mevcut kart sağlık ve kapasite testini geçiyorsa veya bulut/NVR kayıt kullanılacaksa.'},
    {id:'camera-junction-box',category:'camera',name:'Dış kamera için su geçirmez bağlantı kutusu',query:'IP66 kamera bağlantı kutusu cable junction box',tool:'/hesaplama/ev-elektrik-guvenligi-kontrolu/',evidence:['kamera tabanı uyumu','IP contası ve kablo rakoru','montaj yüzeyi'],noBuyWhen:'Üretici bağlantı kiti zaten yeterliyse veya enerji bağlantısı yetkin kişi gerektiriyorsa.'},
    {id:'wireless-nightlight',category:'lighting',name:'Kablosuz şarj pedli gece lambası',query:'Qi kablosuz şarj gece lambası çıkarılabilir',tool:'/hesaplama/acil-aydinlatma-sure-uygunluk/',evidence:['Qi desteği','giriş adaptörü','ışık seviyesi ve kullanım amacı'],noBuyWhen:'Mevcut ışık ve şarj cihazı yeterliyse veya acil aydınlatma yerine kullanılacaksa.'},
    {id:'motion-nightlight',category:'lighting',name:'Hareket sensörlü düşük güçlü gece lambası',query:'hareket sensörlü gece lambası düşük güç sıcak ışık',tool:'/hesaplama/oda-aydinlatma-lumen-kelvin-uygunluk/',evidence:['algılama alanı','ışık rengi ve parlaklık','priz veya pil tipi'],noBuyWhen:'Mevcut koridor ışığı güvenli yön bulmayı sağlıyorsa veya kaçış yönlendirmesi yerine kullanılacaksa.'},
    {id:'water-leak-alarm',category:'monitoring',name:'Pilli yerel su kaçağı alarmı',query:'pilli su kaçağı alarmı yüksek ses düşük pil uyarısı',tool:'/karar-motoru/',evidence:['sensör yerleşimi','alarm ses seviyesi','düşük pil ve periyodik test'],noBuyWhen:'Aktif su baskını varsa veya drenaj, pompa ve onarımın yerine kullanılacaksa.'},
    {id:'cable-label-set',category:'monitoring',name:'Ağ ve adaptör kablo etiket seti',query:'kendinden laminasyonlu kablo etiket seti ağ adaptör',tool:'/hesaplama/ekipman-bakim-plani/',evidence:['kablo çapı','ısı ve nem ortamı','okunabilir kodlama standardı'],noBuyWhen:'Mevcut etiketler kalıcı ve okunaklıysa veya proje kodlama standardı belirlenmediyse.'}
  ].map(item=>({...item,amazonUrl:amazonSearchUrl(item.query),verifiedAt:generatedAt}));

  function freshProducts(now=new Date()){
    return products.filter(item=>verificationStatus(item,now).fresh);
  }

  function knowledgeGraph(now=new Date()){
    const fresh=freshProducts(now);
    const termsetId=`${siteOrigin}${routePath}#verified-models`;
    const listId=`${siteOrigin}${routePath}#model-list`;
    const brands=[...new Set(fresh.map(item=>item.brand))].sort();
    const graph=[
      {'@type':'DefinedTermSet','@id':termsetId,name:'ALO186 doğrulanmış ev-ofis ağ ve güvenlik model kayıtları',hasDefinedTerm:fresh.map(item=>({'@id':`${siteOrigin}${routePath}#${item.id}`}))},
      {'@type':'ItemList','@id':listId,name:'Doğrulanmış ev-ofis ağ ve güvenlik modelleri',numberOfItems:fresh.length,itemListElement:fresh.map((item,index)=>({'@type':'ListItem',position:index+1,item:{'@id':`${siteOrigin}${routePath}#${item.id}`}}))},
      ...brands.map(name=>({'@type':'Brand','@id':`${siteOrigin}/knowledge-graph/brand/${encodeURIComponent(name.toLowerCase())}#brand`,name})),
      ...fresh.map(item=>({
        '@type':'DefinedTerm','@id':`${siteOrigin}${routePath}#${item.id}`,name:item.name,termCode:item.mpn,
        description:`${item.userNeed}. Teknik kontrol tarihi: ${item.verifiedAt}.`,
        identifier:[{'@type':'PropertyValue',propertyID:'ASIN',value:item.asin},{'@type':'PropertyValue',propertyID:'MPN',value:item.mpn}],
        inDefinedTermSet:{'@id':termsetId},subjectOf:item.technicalSource,
        additionalProperty:item.facts.map((value,index)=>({'@type':'PropertyValue',name:`Doğrulanan teknik alan ${index+1}`,value}))
      }))
    ];
    return {'@context':'https://schema.org','@graph':graph};
  }

  return {version,affiliateTag,generatedAt,verificationMaxAgeDays,siteOrigin,routePath,products,productClasses,amazonProductUrl,amazonSearchUrl,verificationStatus,freshProducts,knowledgeGraph};
});
