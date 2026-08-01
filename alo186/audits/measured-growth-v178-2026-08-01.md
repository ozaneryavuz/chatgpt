# ALO186 ölçülmüş ihtiyaç ve güvenli affiliate büyüme denetimi v178

Tarih: 1 Ağustos 2026

## Seçilen 3 aksiyon

1. Ev cihazı için W, kullanım süresi, gün ve kullanıcının kendi faturasından girdiği TL/kWh değeriyle aylık enerji ön değerlendirmesi ve 7 günlük ölçüm planı.
2. Elektrik kesintisi öncesinde buzdolabı/dondurucu termometresi, soğutucu kutu ve jel paket açığını ayıran; aktif kesintide ticareti kapatan soğuk zincir hazırlık aracı.
3. Mevcut ürün ve gerçek test kanıtına göre en fazla üç düşük riskli ürün sınıfını gösteren ölçülmüş ihtiyaç listesi; ana ürün merkezinden görünür keşif girişi.

## Arama niyeti ve içerik boşluğu

Karşılanan niyetler: “cihaz ayda kaç kWh yakar”, “watt aylık elektrik maliyeti”, “priz tipi enerji ölçer gerekli mi”, “elektrik kesintisinde buzdolabı termometresi”, “dondurucu kaç saat dayanır”, “soğutucu çanta ve jel buz”, “elektrik kesintisi için ne almalıyım”, “mevcut powerbank yeterli mi”.

Canlı ürün merkezinde 67 ürün seçim yolu ve 120 bağlamsal ürün kartı bulunmasına rağmen kullanıcıların üç soruya tek yerde yanıt veren ortak bir katmanı yoktu: mevcut ürünüm aynı görevi gerçek testte geçiyor mu, ölçüm belirsiz mi ve bu ziyarette en önemli üç açık hangisi? v178 bu boşluğu ürün sayısını artırmadan kapatır.

## Kullanıcı yolculuğu

- Kullanıcı önce enerji tüketimini veya soğuk zincir hazırlığını ücretsiz araçta ölçer.
- Hasar, su, aşırı ısınma, yüksek güçlü yük, sabit tesisat veya aktif kesinti varsa mağaza yolu kapanır.
- Mevcut ürün aynı görevde testi geçtiyse “yeni ürün almayın” sonucu verilir.
- Gerçek ihtiyaç varsa ücretsiz uygunluk aracı, teknik kanıt listesi ve üçlü affiliate onayı gösterilir.
- Ölçülmüş ihtiyaç listesi aynı ziyarette en fazla üç ürün sınıfına izin verir; kalan ihtiyaçları erteler.

## Affiliate ürün kategorileri

Doğrudan düşük riskli ve tak-çalıştır sınıflar: priz tipi enerji ölçer, enerji ölçümlü akıllı priz, buzdolabı/dondurucu termometresi, yalıtımlı soğutucu kutu veya çanta, yeniden kullanılabilir jel paket, modem/ONT mini UPS, USB-C PD powerbank, şarjlı el/kafa feneri, pilli yerel sesli su alarmı, bağımsız kanallı NiMH şarj cihazı, e-marker USB-C kablo ve CAT6 hazır patch kablosu.

Doğrudan affiliate dışında tutulanlar: yüksek güçlü ısıtıcılar, motor/kompresör ölçümü için uygunluğu bilinmeyen priz cihazları, sabit pano elemanları, jeneratör, EV şarjı, GES/BESS, profesyonel soğuk zincir ve gıda güvenliği kararı.

## Dönüşüm noktaları

- Etiket değeri belirsizse 7 günlük ölçüm planından priz tipi ölçüm sınıfına geçiş.
- Soğuk zincir hazırlığında yalnız eksik termometre, soğutucu veya jel pakete geçiş.
- Ana ürün merkezinden “ölçülmüş ihtiyaç listesi” girişine geçiş.
- En fazla üç öncelikli karttan ücretsiz uygunluk aracına ve ardından üçlü affiliate kapısına geçiş.
- GA4 onayı varsa `measured_shortlist_v178_entry_view`, `measured_shortlist_created`, `measured_shortlist_product_select` ve mevcut `affiliate_click` olayları.

## Tekrar ziyaret nedenleri

- 7 günlük gerçek kWh ölçümünü tamamlamak.
- 30 gün sonra termometre, soğutucu ve jel paket hazırlığını test etmek.
- 30 gün sonra ihtiyaç listesini yeniden değerlendirip testi geçen ürünleri çıkarmak.
- Yeni cihaz, yeni modem/ONT, yeni buzdolabı/dondurucu, kablo değişikliği veya gerçek kesinti sonrası planı güncellemek.
- JSON ve ICS çıktılarıyla kişisel veri göndermeden ölçüm geçmişini kullanıcının kendi cihazında tutmak.

## Güven sözleşmesi

- Fiyat, stok, puan, satıcı, teslimat, yorum veya garanti bilgisi yayımlanmaz.
- Amazon bağlantıları kaynak HTML’de hazır href olarak bulunmaz; üç ayrı onaydan sonra oluşturulur.
- Bütün mağaza bağlantıları `rel="sponsored nofollow noopener"` ve `alo186rehber-21` etiketi taşır.
- Product, Offer, availability veya aggregateRating şeması kullanılmaz.
- ALO186’in EDAŞ, tedarik şirketi, sağlık/gıda otoritesi, Amazon, üretici, satıcı veya kamu kurumu olmadığı görünür biçimde açıklanır.
- Aktif kesintide soğuk zincir affiliate yolu kapalıdır.
- Mevcut ürün gerçek görevde testi geçtiyse yeni ürün önerilmez.
- Aynı ihtiyaç listesinde en fazla üç ürün sınıfı gösterilir.

## Doğrulanan kaynak çerçevesi

- FDA, “Power Outages: Key Tips for Consumers About Food Safety”: cihaz termometresi hazırlığı, kapakların kapalı tutulması ve sıcaklıkla karar verme.
- FoodSafety.gov, “Food Safety During Power Outage”: buzdolabı/dondurucu için genel süre ve sıcaklık karar tabloları; görünüm veya tatla karar vermeme.
- ENERGY STAR, “Smart Home Energy Management Systems Key Product Criteria”: priz yükü izleme/kontrol cihazlarında güç veya enerji raporlama işlevi.

Bu kaynaklar belirli ürünün uygunluğunu, ürün performansını veya Türkiye’de mevzuata tam uyumu kanıtlamaz. Genel tüketici hazırlığı ve ölçüm yaklaşımı için kullanılmıştır.

## Beklenen kullanıcı faydası

Kullanıcı etiket watt değerini gerçek tüketim sanmaz; kendi faturasındaki birim bedelle şeffaf hesap yapar. Aktif kesintide gecikmiş ürün alışverişine yönelmez. Mevcut ekipman testi geçtiğinde yeni ürün önerilmez. Karar yorgunluğu en fazla üç ürün sınıfıyla azaltılır.

## Beklenen gelir etkisi

- Enerji ölçer ve termometre kategorilerinde yüksek arama niyeti ve düşük teknik risk nedeniyle orta-yüksek nitelikli affiliate potansiyeli.
- Ana ürün merkezindeki 67 seçim yolunu ölçülmüş listeye bağladığı için daha düşük fakat daha nitelikli tıklama oranı beklenir.
- JSON/ICS tekrar ziyaretleri, gerçek ihtiyaç oluştuğunda güvene dayalı yenileme dönüşümünü destekleyebilir.
- Gerçek gelir artışı, tıklama ve satış verisi henüz ölçülmediği için garanti edilmez.

## Teknik ve yayın kontrolleri

Üç benzersiz canonical rota; WebApplication/CollectionPage, FAQPage ve BreadcrumbList; mobil tek sütun; JSON/ICS çıktıları; ana ürün merkezinde idempotent keşif girişi; routing overlay v178; sitemap/search index kabulü; JavaScript söz dizimi; statik Amazon bağlantısı yok; üçlü affiliate kapısı; yüksek riskte fail-closed; Product/Offer şeması yok.

## Tamamlanamayan bağımsız kontroller

GitHub Pages dağıtımının canlı alan adına tamamen yansıması, canlı sitemap, önbellek yenilenmesi, Search Console keşfi, indekslenme ve gerçek affiliate dönüşüm verileri bu çalıştırmada bağımsız olarak doğrulanamaz.
