# ALO186 buzdolabı, dondurucu ve soğuk zincir büyüme denetimi v166

Tarih: 1 Ağustos 2026

## Seçilen 3 yüksek potansiyelli aksiyon

1. Elektrik kesintisinde buzdolabı/dondurucu gıda güvenliği karar aracı
2. Buzdolabı/dondurucu yedek güç W–Wh–kalkış uygunluk aracı
3. Kesinti, sıcaklık ve gerçek süre tekrar test merkezi

## Neden bu küme seçildi?

ALO186 ana kullanıcı niyeti elektrik kesintisidir. Can güvenliği sonrasında kullanıcıların en hızlı ekonomik kayıplarından biri soğuk zincirin bozulmasıdır. Mevcut genel “UPS mi taşınabilir güç istasyonu mu?” içeriği kompresörlü yüklerden söz ediyor ancak buzdolabı özelinde gıda kararı, sıcaklık kanıtı, kalkış gücü ve tekrar test yolculuğu bulunmuyordu. Seçilen küme aktif olay, olay öncesi hazırlık ve tekrar ziyaret aşamalarını birbirine bağlar.

## Arama niyetleri

### Bilgi ve acil karar
- elektrik kesilince buzdolabı kaç saat dayanır
- derin dondurucu elektrik kesintisinde kaç saat dayanır
- kesintiden sonra et ve süt ürünleri yenir mi
- çözülmüş gıda tekrar dondurulur mu
- buzdolabı termometresi kaç derece olmalı

### Teknik ve ticari araştırma
- buzdolabı için güç istasyonu kaç watt
- buzdolabı kalkış akımı / kalkış gücü
- 1000 Wh güç istasyonu buzdolabını kaç saat çalıştırır
- buzdolabı için UPS olur mu
- buzdolabı dondurucu termometresi

### Tekrar kullanım
- gerçek kesinti sonrası sıcaklık kaydı
- yeni buzdolabı veya dondurucu kabul testi
- güç istasyonu batarya yaşlanması
- mevsimsel fırtına ve sıcak hava hazırlığı
- termometre pili ve okuma doğrulaması

## İçerik boşluğu

- Kesinti süresi ile gıda sıcaklığı arasındaki ayrım tek kullanıcı yolculuğunda yoktu.
- Genel W–VA–Wh içeriği, kompresör kalkış gücü ve soğuk zincir kararına bağlanmıyordu.
- Aktif olayda affiliate yolunun kapanması ve yalnız hazırlık aşamasında açılması için buzdolabı özelinde fail-closed akış yoktu.
- Termometre, kapı disiplini, gıda tablosu ve gerçek süre testini 7/30/90 günlük döngüye bağlayan tekrar ziyaret nedeni yoktu.

## Kullanıcı yolculuğu

1. Kullanıcı aktif kesintide gıda güvenliği aracına gelir.
2. Araç elektriksel tehlike, süre, kapı, sıcaklık ve buz kristalini ayırır.
3. Aktif olayda hiçbir affiliate bağlantısı gösterilmez.
4. Olay öncesi hazırlıkta kullanıcı yedek güç aracına geçer.
5. Mevcut sistem yeterliyse “Mevcut sistem yeterli — yeni ürün almayın” sonucu verilir.
6. Gerçek ihtiyaçta önce termometre açığı, sonra teknik kanıtı tamamlanmış güç açığı değerlendirilir.
7. Test merkezi JSON ve ICS çıktılarıyla tekrar ziyareti destekler.

## Affiliate ürün kategorileri

- Buzdolabı/dondurucu cihaz termometresi
- Sürekli W, kalkış W, Wh, dalga biçimi ve tam model koşulları doğrulanacak taşınabilir güç istasyonu

Kategori dışı:
- Yakıtlı jeneratör
- Prizden prize geri besleme kablosu
- Uzatma/çoklayıcı/makara
- Market, restoran, otel ve profesyonel soğuk zincir sistemi
- Hasarlı veya geri çağrılmış bataryalı ürün
- Teknik belgesi bulunmayan ürün

Doğrulanmamış fiyat, stok, puan, satıcı, teslimat, garanti ve kesin çalışma süresi kullanılmaz.

## Dönüşüm noktaları

- Gıda güvenliği aracı → yedek güç uygunluk aracı
- Gıda güvenliği aracı → resmî kesinti yönlendirmesi
- Yedek güç aracı → mevcut sistem yeterli sonucu
- Yedek güç aracı → yalnız termometre açığında termometre kategorisi
- Yedek güç aracı → yalnız kanıtlanmış kapasite açığında güç istasyonu kategorisi
- Her iki araç → test merkezi
- Test merkezi → 7/30/90 günlük ICS ve JSON planı

## Tekrar ziyaret nedenleri

- Gerçek elektrik kesintisi
- Yeni buzdolabı/dondurucu
- Yeni termometre veya pil
- Kapı contası, servis veya yer değişikliği
- Yedek güç bataryasında azalan süre
- Geri çağırma veya güvenlik uyarısı
- Mevsimsel fırtına, aşırı sıcak veya uzun kesinti hazırlığı
- Aile kullanım düzeninin değişmesi

## Beklenen kullanıcı faydası

- Gıdayı tadına bakarak test etme riski azalır.
- 4/24/48 saat eşikleri garanti gibi değil, sıcaklık ve kapı kanıtıyla yorumlanır.
- Kullanıcı yalnız yüksek VA veya Wh değerine bakarak yanlış güç kaynağı seçmez.
- Prizden prize geri besleme ve uzatma zinciri satış yolu olarak sunulmaz.
- Çalışan mevcut sistem gereksiz yere değiştirilmez.
- Tek seferlik alışveriş yerine ölçülebilir kabul ve tekrar test kültürü oluşur.

## Beklenen gelir etkisi

- Gıda güvenliği aracı: doğrudan gelir düşük, organik trafik ve güven etkisi yüksek.
- Termometre kategorisi: düşük sepet, açık ihtiyaç, düşük yanlış ürün riski; gelir etkisi orta.
- Taşınabilir güç istasyonu kategorisi: yüksek sepet ve yüksek niyet; güven kapıları nedeniyle daha az fakat daha nitelikli tıklama; gelir etkisi yüksek.
- Test merkezi: doğrudan gelir düşük, tekrar ziyaret ve gelecekte oluşan doğrulanmış ihtiyaca etkisi yüksek.

## Güven sözleşmesi

- Aktif kesintide affiliate kapalı.
- Elektriksel tehlike, su, yangın, batarya hasarı veya geri çağırmada affiliate kapalı.
- Profesyonel soğuk zincirde affiliate kapalı.
- Üretici ve tam model kanıtı yoksa affiliate kapalı.
- Dalga biçimi ve gerçek test bilinmiyorsa güç istasyonu affiliate yolu kapalı.
- Mevcut sistem yeterliyse satın almama sonucu.
- Üç ayrı affiliate onayı.
- rel="sponsored nofollow noopener".
- Product, Offer, availability ve aggregateRating şeması yok.
- Kişisel veri ve kalıcı tarayıcı depolaması yok.
- ALO186’in resmî kurum olmadığı görünür biçimde açıklanır.

## Doğrulanan kaynaklar

- USDA FSIS, Keep Your Food Safe During Emergencies: refrigerator about 4 hours; full freezer about 48 hours, half-full about 24 hours; do not taste food.
  https://www.fsis.usda.gov/food-safety/safe-food-handling-and-preparation/emergencies/keep-your-food-safe-during-emergencies
- FDA, Food and Water Safety During Power Outages: appliance thermometers, 4 °C / -18 °C planning values, post-outage assessment.
  https://www.fda.gov/food/buy-store-serve-safe-food/food-and-water-safety-during-power-outages-and-floods
- FoodSafety.gov, product-based power outage safety charts.
  https://www.foodsafety.gov/food-safety-charts/food-safety-during-power-outage
- IEC 60335-2-24:2025, edition 9, valid publication for refrigerating appliance safety.
  https://webstore.iec.ch/en/publication/75938
- IEC 62040-1:2017+AMD1:2021+AMD2:2022, consolidated UPS safety requirements.
  https://webstore.iec.ch/en/publication/80573
- CPSC, 4 September 2025 portable power station fire warning; exact model recall control rationale.
  https://www.cpsc.gov/Warnings/2025/CPSC-Warns-Consumers-to-Immediately-Stop-Using-Aeiusny-Power-Stations-Due-to-Risk-of-Serious-Injury-or-Death-from-Fire-Sold-on-Amazon

## Ölçüm önerisi

- Gıda aracı → yedek güç aracı geçiş oranı
- Yedek güç aracı “mevcut sistem yeterli” oranı
- Affiliate kutusunun açılma oranı ve üçlü onay tamamlanma oranı
- Termometre ve güç istasyonu kategori tıklamalarının ayrı takibi
- 7/30/90 günlük ICS indirme oranı
- 30 ve 90 gün içinde doğrudan geri dönüş
- Organik sorgu kümeleri ve Search Console tıklama/konum değişimi

## Yayın notu

Canonical, FAQPage, BreadcrumbList, Article/WebApplication yapılandırılmış verisi, mobil tek sütun düzeni, iç bağlantılar, routing overlay ve kalite sözleşmesi eklendi. Sitemap üretimi mevcut build/routing sistemi üzerinden bu canonical rotaları kabul edecek şekilde overlay ile beslenir. Canlı alan adına yansıma, CDN önbelleği, Search Console keşfi ve arama motoru indekslenmesi bu çalışma anında bağımsız olarak doğrulanamaz.
