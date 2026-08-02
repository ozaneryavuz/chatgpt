# ALO186 elektrik proje tasarım içerikleri v200 — 2026-08-02

## Arama niyeti ve içerik boşluğu

Mevcut ALO186 kapsamı tüketici arızaları, kesinti hazırlığı, UPS/jeneratör/EV ürün kararları ve teknik hesap araçlarında güçlüdür. Bu çalıştırmada arama niyeti çakışmasını önlemek için ürün seçici veya arıza teşhisi yerine profesyonel proje hizmeti öncesi karar boşlukları seçildi:

1. Elektrik proje başlangıcında güç ihtiyacı, kritik yük ve sistem çözümü kararları.
2. Avan projede elektrik odası, şaft, pano, busbar ve kablo güzergâhı koordinasyonu.
3. 62 villa için 22 kW AC ve ortak kullanım için 2×180 kW DC araç şarj altyapısı.

Üç rota farklı proje aşamalarını ve farklı kullanıcı görevlerini hedefler. Başlık, canonical ve ana arama niyetleri birbirini tekrar etmez.

## Seçilen üç aksiyon

### 1. Başlangıç sistem çözümleri rehberi

- Rota: `/sektor-rehberi/elektrik-projesine-baslangic-guc-ihtiyaci-yedek-enerji-sistem-cozumleri/`
- Kullanıcı görevi: Avan projeden önce yük, OG/AG, trafo, jeneratör, UPS, GES, EV ve enerji kalitesi kararlarını kapatmak.
- Ticari değer: Yüksek nitelikli proje ön değerlendirme ve mühendislik hizmeti lead'i.
- Güven sınırı: Kesin trafo/jeneratör gücü veya proje onayı vaat edilmez; girdi ve kanıt gereksinimleri görünürdür.

### 2. Elektrik odası–şaft–pano koordinasyon rehberi

- Rota: `/sektor-rehberi/elektrik-odasi-saft-pano-yerlesim-koordinasyonu/`
- Kullanıcı görevi: Mimari donmadan önce elektrik mahalleri, servis alanı, taşıma rotası, havalandırma, yangın geçişi ve güzergâh rezervlerini koordine etmek.
- Ticari değer: Avan/uygulama proje koordinasyonu, BIM ve saha kontrolü için güçlü B2B lead potansiyeli.
- Güven sınırı: Tek bir standart oda ölçüsü veya ürün markası önerilmez; proje ve ekipman verisi istenir.

### 3. 62 villa EV şarj proje rehberi

- Rota: `/sektor-rehberi/62-villa-22kw-ac-2x180kw-dc-arac-sarj-projesi/`
- Kullanıcı görevi: 1.724 kW aritmetik kurulu gücü doğrudan talep gücü saymadan, dinamik yük yönetimi, sayaçlama, trafo, kablo, koruma, haberleşme ve işletme modelini projelendirmek.
- Ticari değer: Yüksek bütçeli EV altyapı fizibilitesi, uygulama projesi, ihale paketi ve devreye alma lead'i.
- Güven sınırı: EPDK lisansı, dağıtım bağlantı kapasitesi, marka performansı veya belirli araç şarj gücü garanti edilmez.

## Kullanıcı yolculuğu

`arama niyeti → kısa cevap → kapsam/girdiler → teslimler → bağımlılıklar → kritik kontroller → kapsam dışı → kanıt listesi → ilgili iç bağlantılar → güvenli teknik ön değerlendirme CTA`

CTA, kullanıcıyı ürün almaya yönlendirmez. Mimari, yük listesi, bağlantı verisi ve işletme senaryosu hazırlanmadan teklif/ön değerlendirme talebi yapılmaması belirtilir.

## Dönüşüm noktaları

- İletişim sayfasına güvenli teknik ön değerlendirme geçişi.
- Jeneratör, kablo gerilim düşümü, harmonik, kompanzasyon, EV uygunluk ve dinamik yük yönetimi içeriklerine iç bağlantılar.
- Üç yeni rehber arasında karşılıklı bağlar.
- Kanıt listeleri sayesinde proje talebinin kapsam ve veri kalitesinin yükselmesi.

## Tekrar ziyaret nedenleri

- Mimari veya mekanik yük listesi revizyonu.
- Dağıtım şirketi bağlantı görüşü veya kısa devre verisinin gelmesi.
- Trafo, jeneratör, UPS, pano veya şarj cihazı teknik verilerinin değişmesi.
- Etaplama, bütçe, işletme modeli veya EV kullanıcı profilinin güncellenmesi.
- Avan projeden uygulama ve ihale paketine geçiş.

## Beklenen kullanıcı faydası

- İşveren, proje müellifi ve diğer disiplinlerin hangi girdiyi ne zaman sağlaması gerektiği netleşir.
- Erken ekipman siparişi, yetersiz oda/şaft rezervi ve yanlış kurulu güç yaklaşımı riski azalır.
- Teslimler ve kanıtlar teklif karşılaştırmasını ve saha kontrolünü iyileştirir.
- Standart sürümleri ve mevzuatın proje tarihinde yeniden doğrulanması gerektiği görünürdür.

## Beklenen gelir / lead etkisi

- Başlangıç sistem çözümleri: orta-yüksek hacimli, yüksek nitelikli proje lead'i.
- Oda/şaft/pano koordinasyonu: orta hacimli, yüksek B2B hizmet değeri.
- 62 villa EV altyapısı: düşük-orta arama hacmi, çok yüksek proje bütçesi ve lead değeri.

Gelir tahmini verilmemiştir; trafik, iletişim formu, nitelikli görüşme ve teklif dönüşümü ölçülmeden kesin etki iddia edilmez.

## Doğrulanan kaynaklar

- Elektrik İç Tesisleri Proje Hazırlama Yönetmeliği: 03.12.2003 tarihli düzenleme; EMO mevzuat sayfası, kapsam ve proje hizmetleri için kontrol edildi. Konsolide metin ve son değişiklik proje tarihinde yeniden doğrulanmalıdır.
- Çevre, Şehircilik ve İklim Değişikliği Bakanlığı: Binaların Yangından Korunması Hakkında Yönetmelik Kılavuzu'nun 16.12.2024 yayımlandığı doğrulandı.
- EPDK: Şarj Hizmeti Yönetmeliği ve ilgili usul/esasların güncel mevzuat listesinde yer aldığı doğrulandı. EPDK ayrıca temel yönetmeliğin 02.04.2022 tarihli 31797 sayılı Resmî Gazete'de yürürlüğe girdiğini açıklamaktadır.
- IEC 60364-5-52:2009+A1:2024, IEC 60364-5-54:2011+A1:2021, IEC TR 61439-0:2022, IEC 61936-1:2021, IEC 60364-7-722:2018, IEC 61851-1:2017 ve IEC 61439-7:2022 kapsam/sürüm bilgileri IEC Webstore üzerinden kontrol edildi.

## SEO, AEO ve teknik yayın kontrolleri

- Her rotada benzersiz SEO/AEO başlığı ve meta açıklaması.
- Self-referencing canonical.
- Article, FAQPage ve BreadcrumbList yapılandırılmış verisi.
- Mobil viewport, responsive grid ve yatay kaydırılabilir tablolar.
- Üç rota arasında ve mevcut ilgili ALO186 içeriklerine iç bağlantılar.
- Dedicated sitemap: `/sitemap-electric-project-v200.xml`; robots.txt içine kaydedildi.
- Product, Offer ve AggregateRating şeması kullanılmadı.
- Doğrulanmamış fiyat, stok, puan, lisans, yazılım performansı veya uygunluk iddiası kullanılmadı.

## Korunan güven sözleşmesi

- ALO186'in resmî kurum, EDAŞ, TEDAŞ, EMO, GİB veya kamu kuruluşu olmadığı her sayfada görünür.
- Proje onayı, kabul, bağlantı kapasitesi veya mevzuata tam uyum garantisi verilmez.
- Yazılımlar marka/taraf üstünlüğü olmadan, yöntem ve doğrulanabilir çıktı ilkesiyle ele alınır.
- Ürün veya affiliate bağlantısı eklenmedi; gereksiz satın alma yönlendirmesi yapılmadı.
- Standart metinleri uzun alıntılanmadı; yalnız doğrulanmış sürüm ve kapsam bilgisi özetlendi.

## Tamamlanamayan kontroller

- GitHub Pages dağıtımı sonrası özel alan adında HTTP 200, canonical ve yapılandırılmış veri görünürlüğü bu çalıştırma sırasında bağımsız olarak doğrulanamadı.
- Google/Bing indeksleme ve sitemap işleme durumu anlık olarak doğrulanamadı.
- Mevzuat ve TSE ulusal kabul durumu proje başlangıç tarihinde yetkili proje müellifi tarafından tekrar kontrol edilmelidir.
