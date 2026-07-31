# ALO186 klima BTU ve elektrik altyapısı büyüme denetimi v134

Tarih: 31 Temmuz 2026

## Seçilen modül

**Klima BTU ve Elektrik Altyapısı Uygunluk Testi**

Yeni rota:

`/hesaplama/klima-btu-elektrik-altyapi-uygunluk/`

## Neden bu modül?

Yüksek niyetli kullanıcı soruları:

- 20 metrekare odaya kaç BTU klima
- 9000 mi 12000 BTU mu
- klima için ayrı sigorta gerekir mi
- 12000 BTU klima kaç amper çeker
- klima uzatma kablosuna takılır mı
- büyük BTU klima daha iyi mi

ALO186’de klima yedek güç ve voltaj koruma araçları vardı. Oda soğutma kapasitesiyle gerçek elektrik altyapısını aynı kararda birleştiren özel bir araç yoktu.

## Hesap yaklaşımı

- ENERGY STAR oda alanı–BTU/h tablosu metrik alana dönüştürülür.
- Tablo 2,44 m tavan varsayımına göre tavan oranıyla uyarlanır.
- Yoğun güneşte yüzde 10 artış, yoğun gölgede yüzde 10 azalış uygulanır.
- İkiden fazla her kişi için 600 BTU/h eklenir.
- Mutfak için 4.000 BTU/h eklenir.
- Elektronik ısı yükü W × 3,412 ile yaklaşık BTU/h değerine çevrilir.
- İklim ve izolasyon katsayıları açıkça ALO186 ön planlama payı olarak gösterilir; standart veya proje sonucu sayılmaz.
- Sonuç en yakın yaygın tüketici kapasite sınıfına yuvarlanır.

## Elektrik uygunluğu

Araç BTU/h değerini elektrik W/A değeri saymaz. Aday ürün için:

- gerçek INPUT W;
- etiket A;
- tam model teknik belge;
- üreticinin istediği sigorta/devre;
- mevcut devre akımı;
- ayrı klima devresi;
- topraklama ve RCD;
- split veya portatif bağlantı biçimi

ayrı ayrı doğrulanır.

## Ticari yolu kapatan durumlar

- duman, erime, su, elektrik çarpması ve ısınan/hasarlı bağlantı;
- birden fazla odada parlaklık değişimi veya şebeke/nötr şüphesi;
- aktif kesinti;
- ticari, çok odalı, server/medikal ve 36.000 BTU üzeri senaryo;
- uzatma, çoklayıcı veya adaptör zinciri;
- bilinmeyen/başarısız topraklama ve RCD;
- split klimada ayrı devre eksikliği;
- tam model elektrik şartının bulunmaması;
- mevcut devrenin üretici şartını karşılamaması;
- aşırı küçük veya aşırı büyük aday kapasite.

## Satın almama sonucu

Mevcut klima:

- ön seçim kapasite bandında;
- elektrik altyapısı doğrulanmış;
- sıcak ve nemli gündeki gerçek performans testini geçmiş;
- sıcaklık ve nem konforunu sağlamışsa

araç açık **“Yeni ürün almayın”** sonucu verir.

## Şeffaf satış ortaklığı

- Doğrudan Amazon URL'si eklenmez.
- Ürün sınıfı yalnız güvenli planlama senaryosu ve gerçek teknik açıkta açılır.
- Kullanıcı ihtiyacı, teknik kanıtı ve satış ortaklığı bilgisini üç ayrı onayla kabul eder.
- Bağlantı `rel="sponsored nofollow noopener"` taşır.
- Fiyat, stok, puan, satıcı, teslimat veya garanti yayımlanmaz.
- `Product`, `Offer`, availability ve rating şeması kullanılmaz.

## Gizlilik ve erişilebilirlik

Ad, telefon, e-posta, adres, konum, abonelik veya seri numarası istenmez. Tarayıcı depolaması, geolocation ve haricî veri isteği kullanılmaz. Klavye odağı, `aria-live`, 48 px işlem hedefleri, reduced-motion, forced-colors, mobil kırılımlar, JSON ve yazdır/PDF çıktısı bulunur.

## Kaynak yaklaşımı

- ENERGY STAR Room Air Conditioners: alan tablosu, yoğun güneş/gölge, kişi ve mutfak düzeltmeleri; aşırı büyük cihazın nem alma ve verim riski.
- ENERGY STAR HVAC Quality Installation: gerçek bina özellikleriyle doğru boyutlandırma, hava akışı, montaj ve soğutucu akışkan doğrulaması.
- LG üretici destek dokümanları: klima için ayrı topraklı priz ve çoklayıcı/uzatma yerine doğrudan bağlantı yaklaşımı.

Bu kaynaklar Türkiye için resmî proje, montaj veya ürün uygunluk onayı olarak sunulmaz.
