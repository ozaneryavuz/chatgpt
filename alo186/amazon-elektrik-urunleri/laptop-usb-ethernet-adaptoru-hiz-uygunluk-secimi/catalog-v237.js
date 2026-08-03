(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports) module.exports=api;
  if(root&&typeof root==='object') root.Alo186UsbEthernetAdapterCatalogV237=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(){
  'use strict';
  const version=237;
  const affiliateTag='alo186rehber-21';
  const verificationMaxAgeDays=45;
  const verifiedAt='2026-08-03';
  const category=Object.freeze({
    id:'consumer_usb_ethernet_adapter_link_speed_measurement',
    risk:'consumer-medium',
    affiliatePolicy:'after_tool',
    requiredTool:'embedded-usb-ethernet-link-measurement-v237',
    professionalOnly:false,
    excludes:Object.freeze(['life-safety-network','medical-communications','fire-alarm-network','industrial-control-network','poe-power-design','fixed-building-cabling-certification'])
  });
  const products=Object.freeze([
    {
      id:'tp-link-ue300c',asin:'B08HQBC678',mpn:'UE300C',brand:'TP-Link',name:'TP-Link UE300C USB-C Gigabit Ethernet Adaptörü',verifiedAt,
      userNeed:'Ethernet portu olmayan USB-C dizüstü veya tablette, Wi-Fi kaynaklı kararsızlığı kablolu gigabit bağlantıyla ayırmak.',
      strengths:['USB-C giriş ve 10/100/1000 Mbps RJ45 çıkış','Windows, macOS, Chrome OS ve Linux desteği','Katlanabilir, hafif ve veri yolu beslemeli tasarım'],
      limitations:['USB-C portunun veri aktarımını desteklemesi gerekir','Gerçek hız modem, switch, kablo ve internet paketinin en yavaş halkasıyla sınırlıdır','PoE güç sağlamaz ve sabit tesisat sertifikasyonu yapmaz'],
      noBuyWhen:'Cihazda çalışan bir Ethernet portu varsa, sorun kablo/modem tarafındaysa veya USB-C portu yalnız şarj destekliyorsa satın almayın.',
      technicalSource:'https://www.tp-link.com/uk/home-networking/computer-accessory/ue300c/',
      amazonStatusSource:'https://www.epey.com/donusturucu/tp-link-ue300c-type-c-to-gigabit-ethernet.html'
    },
    {
      id:'tp-link-ue306',asin:'B09GRL3VCN',mpn:'UE306',brand:'TP-Link',name:'TP-Link UE306 USB 3.0 Gigabit Ethernet Adaptörü',verifiedAt,
      userNeed:'USB-A 3.0 portlu dizüstü, masaüstü veya desteklenen oyun cihazına kablolu gigabit ağ bağlantısı eklemek.',
      strengths:['USB 3.0 Type-A giriş ve 10/100/1000 Mbps RJ45 çıkış','Bağlantı durumunu gösteren LED','Katlanabilir kablo ve kompakt gövde'],
      limitations:['USB 2.0 porta takıldığında gigabit performansı beklenmemelidir','İşletim sistemi veya donanım sürümüne göre sürücü gerekebilir','PoE sağlamaz; yaşam güvenliği veya endüstriyel ağ için uygunluk kanıtı değildir'],
      noBuyWhen:'USB-C dışında uygun USB-A 3.0 port yoksa, mevcut adaptör aynı görevde stabil çalışıyorsa veya arıza Ethernet kablosundaysa satın almayın.',
      technicalSource:'https://www.tp-link.com/uk/home-networking/computer-accessory/ue306/',
      amazonStatusSource:'https://www.epey.com/donusturucu/tp-link-ue306-usb-3-0-to-gigabit-ethernet.html'
    },
    {
      id:'tp-link-ue302c',asin:'B0DSCDGD4G',mpn:'UE302C',brand:'TP-Link',name:'TP-Link UE302C USB-C 2.5 Gigabit Ethernet Adaptörü',verifiedAt,
      userNeed:'2.5G portlu NAS, switch veya bilgisayarda gigabit üstü yerel ağ darboğazını ölçümle doğruladıktan sonra USB-C üzerinden 2.5G bağlantı kurmak.',
      strengths:['USB-C giriş ve 2.5 Gigabit RJ45 çıkış','Windows, macOS, iPadOS, Chrome OS, Linux ve iOS desteği','Alüminyum gövde ve katlanabilir tasarım'],
      limitations:['2.5G faydası için karşı uç, kablo ve switch de 2.5G desteklemelidir','İnternet paketini veya Wi-Fi kapsamasını tek başına artırmaz','PoE sağlamaz; kritik ağlarda profesyonel tasarımın yerine geçmez'],
      noBuyWhen:'Switch/NAS/bilgisayar yalnız 1G ise, Cat5e veya üstü sağlam kablo yoksa ya da ölçümde gigabit darboğazı görülmüyorsa satın almayın.',
      technicalSource:'https://www.tp-link.com/tr/home-networking/mobile-accessory/ue302c/',
      amazonStatusSource:'https://www.epey.com/donusturucu/tp-link-usb-type-c-to-gigabit-ethernet.html'
    }
  ].map((item)=>Object.freeze({...item,strengths:Object.freeze(item.strengths),limitations:Object.freeze(item.limitations)})));
  function amazonProductUrl(asin){
    if(!products.some((item)=>item.asin===asin)) throw new Error('Unknown ASIN');
    return `https://www.amazon.com.tr/dp/${encodeURIComponent(asin)}?tag=${encodeURIComponent(affiliateTag)}`;
  }
  function verificationStatus(now=new Date()){
    const verified=new Date(`${verifiedAt}T00:00:00Z`); const current=now instanceof Date?now:new Date(now);
    const ageDays=Math.floor((current.getTime()-verified.getTime())/86400000);
    return Object.freeze({fresh:Number.isFinite(ageDays)&&ageDays>=0&&ageDays<=verificationMaxAgeDays,ageDays,maxAgeDays:verificationMaxAgeDays,verifiedAt});
  }
  return Object.freeze({version,affiliateTag,verificationMaxAgeDays,verifiedAt,category,products,amazonProductUrl,verificationStatus});
});
