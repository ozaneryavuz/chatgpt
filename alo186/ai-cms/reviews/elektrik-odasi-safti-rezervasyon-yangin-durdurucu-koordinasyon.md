# ALO186 AI CMS insan inceleme paketi

## İçerik

- **Başlık:** Elektrik Odası ve Şaft Rezervasyonu: Koordinasyon ve Yangın Geçişleri
- **Canonical adayı:** `/haberler/elektrik-odasi-safti-rezervasyon-yangin-durdurucu-koordinasyon`
- **Birincil anahtar ifade:** `elektrik odası şaft rezervasyon planı yangın durdurucu koordinasyon`
- **Risk sınıfı:** `high`
- **Fırsat puanı:** **97/100**
- **AI CMS kalite hedefi:** **100/100**
- **Durum:** `review`

## Arama niyeti ve hedef kullanıcı

Elektrik odası ve şaft için tek bir metrekare veya yüzde vermek yerine; ekipman zarfı, taşıma/bakım erişimi, kablo ve busbar yükleri, yangın bölmesi, su ve ısı riski, kuşaklama ve disiplinler arası arayüzleri mimari proje donmadan çözmek. Hedef kitle mimar, proje yöneticisi, elektrik müellifi, statik/mekanik/yangın koordinasyon ekibi, işveren ve BIM uygulama ekibidir.

## Teslim ve kullanıcı faydası

- Oda fonksiyon ve ekipman rezervasyon matrisi
- Şaft zonlama ve kablo/tava doluluk girdileri
- Taşıma, bakım ve ekipman değişim rotası
- Yangın penetrasyon çizelgesi ve fotoğraflı kapanış kanıtı
- Eşpotansiyel kuşaklama ve erişilebilir test noktaları
- Disiplinler arası çakışma ve sorumluluk kapatma kaydı

## Kaynak doğrulaması

| ID | Yayıncı | Kaynak | Erişim |
|---|---|---|---|
| S1 | EMO | 2003 Elektrik İç Tesisleri Proje Hazırlama Yönetmeliği metni | 2026-08-03 |
| S2 | EMO | 2024 değişiklik taslağı duyurusu | 2026-08-03 |
| S3 | ÇŞİDB | 2024 Binaların Yangından Korunması Kılavuzu duyurusu | 2026-08-03 |
| S4 | IEC | IEC 60364-5-52:2009+A1:2024 | 2026-08-03 |
| S5 | IEC | IEC 60364-5-54:2011+A1:2021 | 2026-08-03 |

## AEO, SEO ve site geliştirme sözleşmesi

- İlk ekranda tek ölçü vermeyen güvenli doğrudan cevap bulunur.
- Altı kaynak bağlı bölüm ve dört görünür SSS hazırlanmıştır.
- Yedi doğrulanmış iç bağlantı eklenmiştir.
- Canonical derleyici `Article`, `FAQPage` ve `BreadcrumbList` üretmelidir.
- Mobilde kontrol listeleri tek sütun, dokunma hedefleri en az okunabilir boyutta olmalıdır.
- 2024 taslağı yürürlükteki kesin hüküm gibi sunulmamalıdır.
- Tahmini en yüksek benzerlik `0.34`; fail-closed eşik `0,78`’dir.

## Güvenlik ve ticari sınır

İçerik yangın, ruhsat, statik veya elektrik proje onayı yerine geçmez. Tek bir yangın durdurucu ürününü tüm geçişler için önermez; enerjili oda/şaft müdahalesi yaptırmaz. Affiliate kapalıdır. Kanıtla yeterli mevcut alan veya sistem varsa gereksiz pano, tava veya malzeme satın alınmaması sonucu korunur.

## İnsan onayı

```text
/cms approve elektrik-odasi-safti-rezervasyon-yangin-durdurucu-koordinasyon
```

Onay sonrası canonical HTML, sitemap/routing, breadcrumb, `Article`/`FAQPage` şeması ve mobil önizleme artifactı üretilmeli; içerik çakışma kontrolü geçmeden merge edilmemelidir.
