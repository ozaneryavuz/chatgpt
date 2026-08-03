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

## Bu çalıştırmanın öncelikli 3 deltası

Aşağıdaki üç değişikliği P0/P1 genel aktarımından önce uygula ve aynı yayın partisinde canlıya al:

### 1. Kombi kesintisi karar aracı

- Canonical rota: `/hesaplama/kombi-kesinti-yedek-guc-uygunluk/`
- Paket kaynağı: `public/hesaplama/kombi-kesinti-yedek-guc-uygunluk/`
- Gazlı kombi, elektrikli kombi ve ısı pompasını ayrı karar yollarında ele al.
- Etiket W, tepe W, hedef süre, gerçek Wh, saf sinüs, topraklama ve nötr-toprak/RCD doğrulamasını taşı.
- Gaz kokusu, CO belirtisi, su teması, yanık kokusu, kıvılcım veya elektrik çarpması belirtisinde ticari yolu kapat.
- Mevcut güvenli çözüm kontrollü testte hedefi karşılıyorsa “yeni ürün almayın” sonucunu göster.
- Bu rota doğrudan Amazon bağlantısı vermesin; yalnız doğrulanmış eksikte ilgili teknik seçiciye ilerlesin.

### 2. Ürün merkezini katalogdan görev-temelli karar merkezine dönüştür

- Canonical rota: `/amazon-elektrik-urunleri/`
- Paket kaynağı: `public/amazon-elektrik-urunleri/`
- Canlıdaki “96 ürün seçim yolu”, “154 ASIN/model” ve benzeri hızla eskiyen sayaçları kaldır.
- İlk ekranda ürün adedi yerine kullanıcının çalışır tutmak istediği görevi seçtir.
- Genel bakış kartlarındaki doğrudan Amazon bağlantılarını kaldır; önce ilgili ALO186 hesaplayıcı veya teknik seçiciye yönlendir.
- Modem/ONT, NAS, kamera-NVR-PoE, ev tipi alarm paneli, CPAP hazırlığı ve mobil internet sürekliliğini yüksek niyetli öncelikli yollar olarak göster.
- Affiliate bağlantısı yalnız ihtiyaç, teknik uygunluk ve görünür satış ortaklığı açıklaması tamamlandıktan sonra açılsın.
- Fiyat, stok, satıcı, puan, yorum, teslimat veya garanti iddiası ekleme.

### 3. Fiyat bağımsız tekrar ziyaret döngüsü

- `/hesaplama/kesinti-kiti-donemsel-kontrolu/` rotasını ürün merkezi ve hazırlık akışlarından görünür bağla.
- Kullanıcıya kişisel veri istemeyen 30 ve 90 günlük yerel `.ics` hazırlık kontrolü sun.
- Hatırlatma; UPS/mini UPS çalışma süresi, modem-ONT değişimi, batarya şişmesi/ısınması, yeni kritik yük ve kesinti sıklığı değişimini yeniden kontrol ettirsin.
- Ad, e-posta, telefon, açık adres, tesisat veya abonelik numarası isteme; ham yanıtları analitiğe gönderme.
- Mevcut sistem güvenli ve yeterliyse satın almama sonucunu koru.

Bu üç delta için yayın sonrası canlı kabul ölçütleri:

- Üç canonical URL HTTP 200 vermeli.
- Her sayfada tek H1, self-canonical ve görünür bağımsızlık açıklaması bulunmalı.
- Kombi ve ürün merkezi temel cevabı JavaScript kapalıyken kaynak HTML'de okunabilmeli.
- Ürün merkezi üst düzey kartlarında doğrudan `amazon.com.tr` bağlantısı bulunmamalı.
- Açılan her Amazon bağlantısı `rel="sponsored nofollow noopener"` taşımalı ve öncesinde görünür affiliate açıklaması olmalı.
- Aktif tehlike yolunda çalışan ticari bağlantı sayısı sıfır olmalı.

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
