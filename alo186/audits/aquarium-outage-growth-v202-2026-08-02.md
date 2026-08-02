# ALO186 akvaryum elektrik kesintisi büyüme paketi v202 — 2026-08-02

## Arama niyeti ve içerik boşluğu

Mevcut ALO186 envanterinde modem/ONT, kombi, buzdolabı, sıcak hava, soğuk zincir, mobil internet, kamera ve genel yedek enerji yolculukları bulunuyor. “Elektrik kesintisinde akvaryum balıkları”, “bataryalı akvaryum hava motoru”, “akvaryum hava pompası kaç saat çalışır” ve “çekvalf elektrik kesintisi” görevleri için ayrı canonical kullanıcı yolculuğu bulunmadığı doğrulandı.

Bu boşluk, ürün listesinden önce canlı güvenliği, elektrik güvenliği, gerçek hava akışı ve Wh–W süre hesabını gerektirir. Tek bir balık yaşam süresi veya evrensel sıcaklık sınırı yayımlanmadı.

## Seçilen üç aksiyon

### 1. Hava pompası çalışma süresi ve oksijen riski önceliği

- Rota: `/hesaplama/akvaryum-elektrik-kesintisi-hava-pompasi-batarya-suresi/`
- W, Wh, verim, batarya rezervi ve hedef saatle süre hesabı.
- Tür için kullanıcı tarafından doğrulanan üst sıcaklık sınırı ve balık davranışıyla risk önceliklendirmesi.
- İnsan elektrik güvenliği riski varsa ticari yol kapalı.
- Gerçek prova yeterliyse “yeni ürün almayın”.

### 2. Üçlü güven kapılı hazırlık seçici

- Rota: `/amazon-elektrik-urunleri/akvaryum-kesinti-hava-pompasi-hazirlik-secici/`
- En fazla üç sınıf: bataryalı kesinti hava pompası, düşük gerilimli USB hava pompası, hava hattı güvenlik seti.
- Statik Amazon bağlantısı yok.
- İhtiyaç, teknik uygunluk ve affiliate ilişkisi ayrı ayrı onaylanınca `alo186rehber-21` ve `rel="sponsored nofollow noopener"` ile bağlantı oluşur.
- Fiyat, stok, satıcı, puan, yorum, teslimat ve garanti yayımlanmaz.

### 3. 30/90 günlük kişisel verisiz test merkezi

- Rota: `/sektor-rehberi/akvaryum-elektrik-kesintisi-30-90-gun-test-merkezi/`
- Pompa gücü, batarya süresi, kuru yerleşim, çekvalf, hava akışı, sıcaklık, yemleme ve acil plan kontrolü.
- Kişisel verisiz JSON kayıt.
- 30 günlük kısa kontrol ve 90 günlük tam prova ICS çıktısı.
- Bütün görevler geçerse satın almama sonucu.

## Kullanıcı yolculuğu

`kesinti araması → insan elektrik güvenliği → balık davranışı ve sıcaklık önceliği → ücretsiz W/Wh hesabı → mevcut pompanın gerçek provası → yalnız doğrulanan eksik ürün sınıfı → üçlü affiliate güven kapısı → 30/90 günlük tekrar test`

Balıklar yüzeyde hava yutuyorsa veya elektrik riski varsa kullanıcı alışveriş akışına değil güvenli havalandırma ve uzman desteğine yönlendirilir.

## Affiliate ürün kategorileri

- Bataryalı veya kesinti modlu akvaryum hava pompası sınıfı.
- Düşük gerilimli USB akvaryum hava pompası sınıfı.
- Hortum, çekvalf ve hava taşı içeren hava hattı güvenlik seti sınıfı.

Powerbank, UPS, jeneratör, balık ilacı, profesyonel yaşam destek sistemi ve canlı hayvan doğrudan önerilmez. Mevcut güvenli güç kaynağı yeterliyse yeni güç ürünü önerilmez.

## Dönüşüm noktaları

- Süre hesabında gerçek kapasite açığı tespit edilmesi.
- Hava akışı veya geri sifon güvenliği eksikliğinin doğrulanması.
- Üç ayrı affiliate onayından sonra dinamik mağaza geçişi.
- Başarılı testte `affiliate_no_buy_selected` olayı.
- 30/90 günlük kontrolde gerçek bakım veya ekipman açığının ortaya çıkması.

## Tekrar ziyaret nedenleri

- Yeni balık, bitki, filtre, hava taşı, ısıtıcı veya daha büyük tank.
- Yaz sıcakları, kış soğuğu, taşınma veya planlı kesinti.
- Batarya yaşlanması, pompa debisi/sesi değişimi, hortum sertleşmesi.
- Gerçek kesinti veya priz/topraklama düzeni değişikliği.
- 30 ve 90 günlük test tarihleri.

## Beklenen kullanıcı faydası

- “Balıklar kaç saat yaşar?” sorusuna yanıltıcı evrensel süre verilmez.
- Hava pompası çalışma süresi ölçülebilir Wh–W hesabına dönüştürülür.
- Islak elektrik ekipmanı ve geri sifon riski ticari akıştan önce ele alınır.
- Mevcut düzen yeterliyse gereksiz satın alma engellenir.
- Hazırlık tek seferlik alışveriş yerine tekrar test edilen bir süreç olur.

## Beklenen gelir etkisi

Arama niyeti acil ve ürün–görev ilişkisi güçlüdür. Sepet değeri genel UPS veya enerji depolama kategorilerinden düşük olabilir; buna karşılık hava pompası ve hava hattı kategorilerinde nitelikli mağaza geçişi beklenir. Bu çalışma gelir veya sipariş garantisi vermez. Trafik, güven kapısı tamamlama, satın almama, mağaza tıklaması ve sipariş verisi ölçülmeden kesin etki iddia edilmez.

## Doğrulanan kaynaklar

Kaynaklar 2 Ağustos 2026 tarihinde kontrol edildi:

- University of Florida IFAS, “Dissolved Oxygen for Fish Production”: sıcak suyun daha az çözünmüş oksijen tuttuğu, balıkların yüzeyde hava yutmasının düşük oksijen belirtisi olabileceği ve acil havalandırmanın önemi.
- Oklahoma State University Extension, “Nitrification and Maintenance in Media Bed Aquaponics”: elektrik/pompa kesintisinde çözünmüş oksijenin azalması ve geçici yüzey hareketi oluşturma yaklaşımı.
- Riverside Public Utilities, “Tips for Pets During Outages”: bataryalı hava pompası, yedek pil ve kesintide yemlemeyi azaltma hazırlığı.
- Aqueon, QuietFlow air pump bilgileri: güç kaybında geri sifon riskini azaltan çekvalf yaklaşımı.

Bu kaynaklar ev tipi her tank için yaşam süresi, debi veya sıcaklık garantisi vermez. Tür özelindeki güncel veteriner/uzman rehberi ve tam model kılavuzu önceliklidir.

## Korunan ticari sözleşme

- ALO186 resmî kurum, EDAŞ, veteriner kliniği, üretici veya satıcı gibi sunulmaz.
- Fiyat, stok, satıcı, puan, yorum, teslimat veya garanti yayımlanmaz.
- Product, Offer ve AggregateRating şeması kullanılmaz.
- Amazon URL'si ilk HTML'de etkin `href` olarak bulunmaz.
- Üçlü güven kapısı olmadan mağaza bağlantısı açılmaz.
- Mevcut sistem yeterliyse yeni ürün alınmaz.
- Islak ekipman, elektrik şüphesi, hasarlı batarya veya profesyonel yaşam destek sisteminde ticari yol kapanır.
- Balık yaşam süresi, hastalık teşhisi veya kesintisiz yaşam desteği garantisi verilmez.
- Kişisel veri ve kalıcı tarayıcı depolaması kullanılmaz.
