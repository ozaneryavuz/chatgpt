(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  if (root && typeof root === 'object') root.Alo186DisplayCableCatalogV229 = api;
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';
  const version = 229;
  const affiliateTag = 'alo186rehber-21';
  const verificationMaxAgeDays = 45;
  const verifiedAt = '2026-08-03';
  const category = Object.freeze({
    id: 'consumer_monitor_display_cable',
    risk: 'consumer-medium',
    affiliatePolicy: 'after_tool',
    requiredTool: 'embedded-display-cable-compatibility-v229',
    professionalOnly: false,
    excludes: Object.freeze(['medical-display-chain','industrial-control-display','critical-signage','safety-monitoring-system','regulated-av-installation'])
  });
  const products = Object.freeze([
    Object.freeze({
      id:'ugreen-displayport-1-4-2m', asin:'B088GQM9CV', mpn:'80392', brand:'UGREEN',
      name:'UGREEN DisplayPort 1.4 8K Kablo 2 m', verifiedAt,
      need:'DisplayPort çıkışlı masaüstü veya dizüstü bilgisayarı DisplayPort girişli monitöre bağlamak.',
      strengths:Object.freeze(['DisplayPort 1.4 sınıfında 8K@60 Hz ve 4K@144 Hz’e kadar üretici beyanı','HDR ile Adaptive-Sync, FreeSync ve G-Sync uyumluluğu','Örgülü dış kaplama ve doğrudan DP–DP bağlantı']),
      limits:Object.freeze(['Gerçek çözünürlük ve yenileme hızı ekran kartı, monitör ve port sürümüyle sınırlıdır','HDMI girişli ekrana doğrudan bağlanmaz','Kablo, yetersiz GPU performansını veya monitör panel sınırını yükseltmez']),
      nobuy:'Cihazlardan biri DisplayPort taşımıyorsa, mevcut kablo hedef çözünürlükte kararlı çalışıyorsa veya sorun sürücü/ekran ayarındaysa satın almayın.',
      source:'https://www.ugreen.com/products/8k-displayport-1-4-cable'
    }),
    Object.freeze({
      id:'ugreen-hdmi-2-1-3m', asin:'B0CFF9T3PS', mpn:'25911', brand:'UGREEN',
      name:'UGREEN HDMI 2.1 Ultra High Speed Kablo 3 m', verifiedAt,
      need:'HDMI 2.1 çıkışlı oyun konsolu, ekran kartı veya medya cihazını HDMI 2.1 ekran ya da AV alıcısına bağlamak.',
      strengths:Object.freeze(['48 Gbps sınıfında HDMI 2.1 ve 8K@60 Hz / 4K@120 Hz desteği','eARC, VRR, ALLM ve dinamik HDR işlevleri','Üç metrelik erişim ve örgülü yapı']),
      limits:Object.freeze(['4K@120 Hz veya 8K için zincirdeki tüm cihazların ve portların aynı özelliği desteklemesi gerekir','Uzunluk, keskin bükülme ve elektromanyetik ortam sinyal kararlılığını etkileyebilir','HDMI 2.1 etiketi kaynak cihazın üretim gücünü veya ekranın panel hızını artırmaz']),
      nobuy:'Hedefiniz 1080p/60 Hz ise, mevcut sertifikalı kablo kararlıysa veya kaynak/ekran HDMI 2.1 özelliklerini desteklemiyorsa satın almayın.',
      source:'https://www.ugreen.com/products/8k-hdmi-2-1-cable'
    }),
    Object.freeze({
      id:'ugreen-usbc-displayport-1-4-2m', asin:'B0C4DB8MLL', mpn:'25158', brand:'UGREEN',
      name:'UGREEN USB-C – DisplayPort 1.4 Kablo 2 m', verifiedAt,
      need:'Görüntü çıkışını destekleyen USB-C veya Thunderbolt bağlantısını DisplayPort monitöre tek kabloyla taşımak.',
      strengths:Object.freeze(['USB-C kaynaktan DisplayPort ekrana tek yönlü görüntü bağlantısı','HBR3, HDR ve 8K@60 Hz / 4K@240 Hz’e kadar ürün sınıfı beyanı','Tak-çalıştır kullanım ve örgülü kablo yapısı']),
      limits:Object.freeze(['USB-C portunun DisplayPort Alt Mode veya Thunderbolt görüntü çıkışını desteklemesi zorunludur','Bağlantı tek yönlüdür; DisplayPort kaynaktan USB-C ekrana çalışmaz','Gerçek çözünürlük ve yenileme hızı kaynak, ekran, işletim sistemi ve DSC desteğine bağlıdır']),
      nobuy:'USB-C portunuz yalnız veri/şarj taşıyorsa, ekranınızda DisplayPort girişi yoksa, ters yönde bağlantı gerekiyorsa veya mevcut kablo kararlıysa satın almayın.',
      source:'https://eu.ugreen.com/en-ro/products/25157'
    })
  ]);
  function amazonProductUrl(asin) {
    if (!products.some((item) => item.asin === asin)) throw new Error('Unknown ASIN');
    return `https://www.amazon.com.tr/dp/${encodeURIComponent(asin)}?tag=${encodeURIComponent(affiliateTag)}`;
  }
  function verificationStatus(now = new Date()) {
    const verified = new Date(`${verifiedAt}T00:00:00Z`);
    const current = now instanceof Date ? now : new Date(now);
    const ageDays = Math.floor((current.getTime() - verified.getTime()) / 86400000);
    return Object.freeze({fresh:Number.isFinite(ageDays)&&ageDays>=0&&ageDays<=verificationMaxAgeDays,ageDays,maxAgeDays:verificationMaxAgeDays,verifiedAt});
  }
  return Object.freeze({version,affiliateTag,verificationMaxAgeDays,verifiedAt,category,products,amazonProductUrl,verificationStatus});
});
