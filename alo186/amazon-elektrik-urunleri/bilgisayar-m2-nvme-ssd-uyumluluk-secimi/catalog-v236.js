(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  if (root && typeof root === 'object') root.Alo186NvmeSsdCatalogV236 = api;
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';
  const version = 236;
  const affiliateTag = 'alo186rehber-21';
  const verificationMaxAgeDays = 45;
  const verifiedAt = '2026-08-03';
  const category = Object.freeze({
    id: 'consumer_pc_nvme_m2_2280_storage_upgrade',
    risk: 'consumer-medium',
    affiliatePolicy: 'after_tool',
    requiredTool: 'embedded-nvme-slot-backup-compatibility-v236',
    professionalOnly: false,
    excludes: Object.freeze(['server-raid-array','life-safety-system','medical-device','industrial-control','live-mains-work','soldering-repair'])
  });
  const products = Object.freeze([
    {
      id: 'kingston-nv3-1tb', asin: 'B0DBR3DZWG', mpn: 'SNV3S/1000G', brand: 'Kingston',
      name: 'Kingston NV3 1 TB M.2 2280 PCIe 4.0 NVMe SSD', verifiedAt,
      userNeed: 'Uyumlu masaüstü veya dizüstü bilgisayarda sistem diski ya da çalışma dosyaları için 1 TB NVMe alanı eklemek.',
      strengths: ['M.2 2280 ve PCIe 4.0 x4 NVMe arayüzü','1 TB modelde 6.000/4.000 MB/sn değerlerine kadar sıralı okuma/yazma sınıfı','Tek yüzlü, düşük güç tüketimine odaklı kompakt tasarım'],
      limitations: ['M.2 SATA yuvasında çalışmaz','Gerçek hız anakart, PCIe nesli, soğutma ve iş yüküne bağlıdır','Yeni disk tek başına yedekleme değildir; ayrı kopya ve geri yükleme testi gerekir'],
      noBuyWhen: 'Cihazınızda M.2 2280 NVMe yuvası yoksa, mevcut kapasite yeterliyse veya klonlama/temiz kurulum ve yedek planı hazır değilse satın almayın.',
      technicalSource: 'https://www.kingston.com/en/ssd/nv3-nvme-pcie-ssd'
    },
    {
      id: 'kioxia-exceria-plus-g3-1tb', asin: 'B0CN5L6FPK', mpn: 'LSD10Z001TG8', brand: 'KIOXIA',
      name: 'KIOXIA EXCERIA PLUS G3 1 TB M.2 2280 PCIe 4.0 NVMe SSD', verifiedAt,
      userNeed: 'PCIe 4.0 destekli uyumlu bilgisayarda büyük dosya, içerik üretimi ve günlük çalışma alanını hızlandırmak.',
      strengths: ['M.2 2280 tek yüzlü yapı ve PCIe 4.0 x4 arayüz','5.000/3.900 MB/sn değerlerine kadar sıralı okuma/yazma sınıfı','NVMe 1.4 ve üreticinin SSD Utility yönetim desteği'],
      limitations: ['PCIe 3.0 sistemlerde geriye uyumlu olsa da ilan edilen üst hızlara erişemez','PS5 veya özel cihaz uyumluluğu yalnız form faktörüyle varsayılamaz','Yoğun yazma ve sıcaklık koşulları performansı etkileyebilir'],
      noBuyWhen: 'Anakart kılavuzu NVMe desteğini doğrulamıyorsa, M.2 yuvası başka aygıtla paylaşılıyorsa veya veri taşıma planı yoksa satın almayın.',
      technicalSource: 'https://europe.kioxia.com/en-europe/personal/ssd/exceria-plus-g3.html'
    },
    {
      id: 'samsung-980-500gb', asin: 'B08THW4S3T', mpn: 'MZ-V8V500BW', brand: 'Samsung',
      name: 'Samsung 980 500 GB M.2 2280 PCIe 3.0 NVMe SSD', verifiedAt,
      userNeed: 'PCIe 3.0 NVMe destekli bilgisayarda işletim sistemi ve temel uygulamalar için ölçülü bir kapasite yükseltmesi yapmak.',
      strengths: ['M.2 2280, PCIe 3.0 x4 ve NVMe 1.4 uyumu','500 GB modelde 3.100/2.600 MB/sn değerlerine kadar sıralı okuma/yazma sınıfı','TRIM, S.M.A.R.T. ve AES 256-bit şifreleme desteği'],
      limitations: ['500 GB kapasite büyük medya arşivi veya çoklu oyun kitaplığı için sınırlı kalabilir','DRAM yerine Host Memory Buffer mimarisi kullanır','M.2 SATA yuvasıyla uyumlu değildir'],
      noBuyWhen: 'Kullanılabilir kapasite hesabı 500 GB üstünü gerektiriyorsa, sistem NVMe desteklemiyorsa veya mevcut disk sağlıklı ve yeterliyse satın almayın.',
      technicalSource: 'https://semiconductor.samsung.com/consumer-storage/internal-ssd/980/'
    }
  ].map((item) => Object.freeze({...item, strengths: Object.freeze(item.strengths), limitations: Object.freeze(item.limitations)})));
  function amazonProductUrl(asin) {
    if (!products.some((item) => item.asin === asin)) throw new Error('Unknown ASIN');
    return `https://www.amazon.com.tr/dp/${encodeURIComponent(asin)}?tag=${encodeURIComponent(affiliateTag)}`;
  }
  function verificationStatus(now = new Date()) {
    const verified = new Date(`${verifiedAt}T00:00:00Z`);
    const current = now instanceof Date ? now : new Date(now);
    const ageDays = Math.floor((current.getTime() - verified.getTime()) / 86400000);
    return Object.freeze({fresh: Number.isFinite(ageDays) && ageDays >= 0 && ageDays <= verificationMaxAgeDays, ageDays, maxAgeDays: verificationMaxAgeDays, verifiedAt});
  }
  return Object.freeze({version, affiliateTag, verificationMaxAgeDays, verifiedAt, category, products, amazonProductUrl, verificationStatus});
});
