Use @Sites to edit the site with the slug alo186, with:

# ALO186 GitHub → ChatGPT Sites kaynak aktarımı

Bu paketteki `sites-source-manifest.json`, `route-inventory.json`, `source-integrity.json`,
`metadata/` ve `public/` dizinlerini birlikte kaynak kabul et.

## Yayın otoritesi

- Canlı yayın ve görsel sunum: ChatGPT Sites
- İçerik, veri, kalite, sürüm ve geri alma kaynağı: `ozaneryavuz/chatgpt`
- Canonical origin: `https://alo186.com`
- Mevcut ChatGPT Sites özel alan adı ve DNS kayıtlarını koru.
- GitHub Pages'i özel alan adına bağlama.
- Belgelenmemiş veya taklit edilmiş bir Sites API kullanma.

## Uygulama yöntemi

1. Önce `sites-source-manifest.json` içindeki P0 katmanlarını uygula.
2. Mevcut ChatGPT Sites tasarım sistemini, header/footer bileşenlerini ve iyi çalışan
   responsive düzeni koru. GitHub'daki eski statik CSS'yi körlemesine yapıştırma.
3. Aynı rota Sites'te zaten varsa:
   - Sites bileşenini koru,
   - GitHub'daki daha yeni ve doğrulanmış içerik, veri, yapılandırılmış veri,
     güvenlik sınırı ve iç bağlantıları bileşene birleştir,
   - eski hukukî süre, canonical host, fiyat, stok, puan veya resmî kurum iddiasını geri getirme.
4. Yeni canonical rota yoksa aynı path ile oluştur.
5. Araçlarda yalnız görünür metni değil, deterministik karar mantığını, doğrulamaları,
   erişilebilir form etiketlerini, sonuç açıklamalarını ve güvenlik kapılarını taşı.
6. Yalnız `state: published` olan AI CMS kayıtlarını canlıya al.
7. Her yayın partisinden sonra canonical, tek H1, meta description, iç bağlantılar,
   mobil görünüm, klavye odağı ve JSON-LD görünür içerik eşliğini doğrula.

## Zorunlu P0 aktarımı

- Ana karar deneyimi: `/`, `/elektrik-portali`, `/edas-bul`, `/karar-motoru`,
  `/hesaplama/`, `/acil-numaralar/`, `/planli-kesintiler/`
- 81 il sayfası: `/il/{il-slug}/`
- 21 dağıtım şirketi sayfası: `/dagitim-sirketleri/{sirket-slug}/`
- 186 için `Service + ServiceChannel`; özel EDAŞ için `Organization`;
  yalnız gerçek 112 Acil Çağrı Hizmeti için `GovernmentService`
- `robots.txt`, ana sitemap, llms kaynakları ve bilgi grafiği kaynakları
- ALO186 bağımsızlık açıklaması ve 112/186/elektrikçi ayrımı

## Affiliate aktarım kuralları

- Yalnız Amazon Türkiye ve `alo186rehber-21`
- Tüm mağaza bağlantılarında `rel="sponsored nofollow noopener"`
- Aktif yangın, duman, elektrik çarpması, kıvılcım, kopmuş iletken veya can güvenliği
  olayında ürün ve ticari CTA gösterme
- Mevcut güvenli çözüm yeterliyse “yeni ürün almayın” sonucunu koru
- Fiyat, stok, satıcı, puan, yorum, teslimat ve garanti iddiası üretme
- Güncel ve doğrulanmış merchant verisi yoksa `Offer` veya `AggregateRating` ekleme
- Konum/EDAŞ sayfalarında affiliate bağlantısı gösterme

## Yayın sırası

- P0: güvenlik, resmî kanal, çekirdek navigasyon, 81 il/21 EDAŞ, robots/sitemap
- P1: yayımlanmış teknik rehberler, hesaplayıcılar, düşük riskli affiliate karar yolları
- P2: İngilizce sayfalar; yalnız doğal dil, karşılıklı hreflang ve işlev eşitliği sağlanınca

## Kabul ve makbuz

Güvenli ve doğrulanmış P0/P1 değişikliklerini bu açık kullanıcı talebi kapsamında ayrıca
onay sormadan yayınla. Yüksek riskli içerik yalnız GitHub kaydı `published` ise yayınlanabilir.
İşlem sonunda:

- uygulanan, birleştirilen, atlanan ve hata veren rotaları ayrı listele,
- kaynak commit'i ve paket hashini kaydet,
- canlı URL'lerde HTTP 200, canonical, title, H1, JSON-LD ve affiliate güven kapılarını doğrula,
- exact commit platformda açıklanmıyorsa bunu dürüstçe belirt ve canlı içerik fingerprint'i üret,
- `sites-receipt.json` biçiminde yayın makbuzu oluştur.
