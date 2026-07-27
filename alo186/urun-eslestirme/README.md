# ALO186 Akıllı Ürün Eşleştirme v1

Kullanıcıyı genel Amazon aramasına göndermeden önce ihtiyacı teknik minimumlara dönüştürür. Doğrudan eşleştirmeye uygun kategorilerde en fazla üç ürün kartı; teknik veya güvenlik uyumu gerektiren kategorilerde kontrol listesi ve profesyonel sınır gösterir.

## Kapsam

### Doğrudan ürün eşleştirme

- Powerbank
- Akım korumalı grup priz

Bu kategorilerde ASIN ve Amazon ürün sayfasındaki temel teknik alanlar kontrol edilmiştir. Fiyat, stok, teslimat, satıcı ve kampanya ALO186 üzerinde kopyalanmaz.

### Rehberli seçim

- Modem/fiber ONT mini UPS
- Şarjlı acil aydınlatma
- Fotoelektrik duman alarmı
- Taşınabilir güç istasyonu
- Priz/RCD test cihazı

Voltaj, polarite, tesisat, standart, ölçüm veya yük hesabı gerektiren kategorilerde doğrudan “uygun ürün” iddiası yapılmaz.

## Amazon satış ortaklığı

Affiliate etiketi:

```text
alo186hazirlik-21
```

Ürün linkleri doğrudan ASIN sayfasına, kategori rehberleri teknik ifadeler içeren Amazon aramasına gider. Bağlantılarda `rel="sponsored nofollow noopener"` kullanılır.

## Veri ilkeleri

- Ürün kartında statik fiyat ve stok tutulmaz.
- Bilinmeyen teknik alanlar açıkça gösterilir.
- Yüksek minimum gereksinim bilinmeyen teknik değerle eşleştirilemez.
- Komisyon teknik olarak uygunsuz ürünü listeye sokamaz.
- “Doğrulandı” ifadesi ASIN ve liste teknik alanlarının kontrol edildiği anlamına gelir; laboratuvar testi veya bağımsız sertifikasyon anlamına gelmez.

## Dosyalar

- `catalog.js` — kategori, ürün, ASIN ve doğrulama kayıtları
- `matcher-core.js` — teknik eleme ve puanlama
- `app.js` — dinamik gereksinim ve kart akışı
- `index.html` — kullanıcı arayüzü ve affiliate açıklaması
- `styles.css` — responsive ürün kartları
- `../tests/test_product_matcher.js` — katalog ve güvenlik testleri

## Test

```bash
node alo186/tests/test_product_matcher.js
```

## Yayın rotası

```text
/akilli-urun-secimi
```

Mevcut `/amazon-elektrik-urunleri` merkezi bu araca “Akıllı eşleştirme” CTA'sı vermeli; mevcut 50 kategori rehberi korunmalıdır.

## Sonraki katalog genişlemesi

Issue #5 tamamlanmadan önce aşağıdaki kategorilerde üçer doğrulanmış kart hedeflenir:

- mini UPS
- acil aydınlatma
- duman alarmı
- taşınabilir güç istasyonu
- priz test cihazı

Katalog genişlemesi stok/fiyat kopyalamadan, teknik alan ve ASIN doğrulama kuyruğuyla yapılmalıdır.
