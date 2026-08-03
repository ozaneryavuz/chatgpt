# ALO186 AI CMS insan inceleme paketi

## İçerik

- **Başlık:** UPS Akü Odası Hidrojen Havalandırması ve Şarj Arızası Kabulü
- **Canonical adayı:** `/haberler/ups-aku-odasi-hidrojen-havalandirma-sarj-arizasi-kabul`
- **Birincil anahtar ifade:** `UPS akü odası havalandırma hesabı`
- **Risk sınıfı:** `high`
- **Fırsat puanı:** **97/100**
- **AI CMS kalite hedefi:** **100/100**
- **Durum:** `review`

## Kullanıcı görevi

UPS veya sabit akü odasında batarya teknolojisi, hücre sayısı, şarj rejimi ve üretici gaz verisine göre hidrojen oluşumunu; doğal veya mekanik havalandırma, fan-alarm interlocku, sıcaklık ve arıza senaryolarıyla kanıtlayan kabul dosyası hazırlamak.

## Kaynak doğrulaması

| ID | Yayıncı | Kaynak | Erişim |
|---|---|---|---|
| S1 | IEC | IEC 62485-2:2010 — Safety requirements for stationary batteries | 2026-08-03 |
| S2 | IEEE/ASHRAE | IEEE/ASHRAE 1635-2022 — Ventilation and Thermal Management of Stationary Batteries | 2026-08-03 |
| S3 | IEEE | IEEE 484-2019 — Installation Design of Vented Lead-Acid Batteries | 2026-08-03 |
| S4 | Schneider Electric | APC UPS battery types and VRLA ventilation guidance | 2026-08-03 |
| S5 | IEEE PES | Battery Gassing Calculator based on IEEE 1635 / ASHRAE 21 | 2026-08-03 |

## AEO, SEO ve kullanıcı faydası

- İlk ekranda bağımsız doğrudan cevap bulunur.
- 5 kaynak bağlı bölüm ve 4 görünür SSS hazırlanmıştır.
- 7 doğrulanmış bağlamsal iç bağlantı eklenmiştir.
- Canonical derleyici `Article`, `FAQPage` ve `BreadcrumbList` üretmelidir.
- Kurumsal yazar `Organization` olmalıdır; `Person`, `Product` ve `Offer` kullanılmamalıdır.
- Birincil CTA kişisel verisiz kabul/ölçüm matrisi ve teknik kanıt dosyasıdır.
- Mevcut sistem bütün senaryoları kanıtla geçiyorsa gereksiz ekipman veya yazılım satın alınmamalıdır.
- Tahmini en yüksek benzerlik `0.42`; fail-closed eşik `0,78`’dir.

## Güvenlik ve mevzuat sınırı

İçerik; akü odasında açık alev, kıvılcım üreten işlem, enerjili DC bara müdahalesi, elektrolit teması veya kullanıcı tarafından şarj ayarı değiştirilmesini önermez. Gaz hesabı üretici verisi, proje koşulları ve yetkin mühendis değerlendirmesiyle yapılmalıdır. Affiliate kapalıdır.

## İnsan onayı

```text
/cms approve ups-aku-odasi-hidrojen-havalandirma-sarj-arizasi-kabul
```

AI ve bot yorumları onay sayılmaz. Onay sonrası canonical HTML, routing overlay ve ChatGPT Sites önizleme artifactı hazırlanır; ayrıca insan merge'i gerekir.
