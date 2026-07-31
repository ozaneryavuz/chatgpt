# ALO186 sürdürülebilir büyüme denetimi — ev nem ve rutubet v139

Kontrol tarihi: 31 Temmuz 2026

## Seçilen üç aksiyon

1. **Nem ölçer ve nem alma cihazı uygunluk testi**
   - Arama niyeti: `evde nem yüzde kaç olmalı`, `nem ölçer gerekli mi`, `rutubet için nem alma cihazı`, `nem alma cihazı işe yarar mı`.
   - Boşluk: ALO186'te su kaçağı ve sıcaklık alarmı araçları vardı; ancak RH ölçümü, aktif kaynak, yoğuşma, mevcut cihaz ve satın almama sonucunu aynı kararda birleştiren rota yoktu.
   - Affiliate sınıfları: yalnız ölçüm eksikliğinde dijital higrometre; yalnız kaynak giderilmiş ve kalıcı yüksek nem doğrulanmış ev tipi odada taşınabilir nem alma cihazı.
   - Güven sınırı: aktif su-elektrik riski, geniş küf, ticari/medikal/tüm-ev kapsamı ve yeterli mevcut cihaz ticarete dönüşmez.

2. **Nem alma cihazı kWh ve drenaj planı**
   - Arama niyeti: `nem alma cihazı ne kadar elektrik yakar`, `nem alma cihazı kaç saat çalışır`, `tank kaç litre`, `hortum drenajı`.
   - Boşluk: kapasite, tank hacmi ve giriş gücü kullanıcılar tarafından birbirine karıştırılıyor; fiyat kullanmadan W → kWh ve tank çevrimi hesabı eksikti.
   - Dönüşüm: yalnız 7 günlük RH kaydı, giderilmiş kaynak, güvenli priz, doğrulanmış drenaj ve gerçek cihaz eksikliğinde ürün merkezi.
   - Satın almama: mevcut cihaz hedef RH, drenaj ve elektrik görevini karşılıyorsa açık biçimde yeni ürün önerilmez.

3. **Ev rutubet, yoğuşma ve tekrar test merkezi**
   - Tekrar ziyaret: aktif olaydan 7 gün sonra; kaynak onarımı/yeni cihazdan 30 gün sonra; filtre, tank, hortum, priz ve mevsim için 90 gün sonra.
   - Çıktılar: kişisel verisiz P0/P1/P2 görev planı, JSON ve `.ics`.
   - Merkez doğrudan affiliate bağlantısı göstermez; önce ücretsiz araçlara ilerler.

## Kullanıcı yolculuğu

```text
rutubet / yoğuşma araması
→ su ve elektrik güvenliği
→ 3–7 günlük RH kanıtı
→ aktif kaynak / yapı / havalandırma ayrımı
→ mevcut higrometre ve cihaz testi
→ yeterliyse satın almama
→ yalnız doğrulanmış eksikte açık affiliate ürün sınıfı
→ kWh, tank ve drenaj planı
→ 7/30/90 günlük yeniden test
```

## Ticari ve kurumsal sınırlar

- Doğrulanmamış fiyat, stok, puan, yorum, satıcı, teslimat ve garanti kullanılmaz.
- Doğrudan Amazon URL'si eklenmez.
- Affiliate bağlantısı `rel="sponsored nofollow noopener"` taşır ve bağlantıdan önce açıklanır.
- Product, Offer, availability ve aggregateRating şeması kullanılmaz.
- ALO186 kamu kurumu, sağlık kuruluşu, yapı denetim firması, HVAC firması, elektrikçi veya ürün satıcısı gibi gösterilmez.
- Ad, adres, konum, sağlık kaydı, fotoğraf, marka ve seri numarası istenmez.
- localStorage, sessionStorage ve geolocation kullanılmaz.

## Beklenen etki

- **Kullanıcı faydası:** tek ölçüm, küf kokusu veya oda m² değerine dayanarak gereksiz cihaz alma azalır; aktif su kaynağı ürünle gizlenmez; enerji ve drenaj görevi görünür olur.
- **Gelir etkisi:** geniş mevsimsel arama niyeti, önce ölçüm ve kaynak doğrulamasıyla nitelendirilir. Higrometre düşük bariyerli; nem alma cihazı daha yüksek sepet değerli fakat yalnız gerçek ihtiyaçta açılır.
- **Tekrar ziyaret:** yeni mevsim, sızıntı onarımı, filtre/tank bakımı, oda değişimi ve 7/30/90 günlük kontrol doğal geri dönüş nedeni oluşturur.

## Kaynak yaklaşımı

- US EPA: iç bağıl nemin yüzde 60 altında, mümkünse yaklaşık yüzde 30–50 aralığında tutulması; su ve nem kaynağının hızla giderilmesi.
- ENERGY STAR: taşınabilir/tüm-ev ayrımı; kapasitenin ortam koşulu ve test şartlarına bağlı olması; enerji performansında litre/kWh temelli IEF yaklaşımı.
- Kaynaklar Türkiye'de sağlık, yapı, elektrik veya ürün uygunluk onayı olarak sunulmaz; yerel kural, tam model üretici belgesi ve yetkili uzman önceliklidir.
