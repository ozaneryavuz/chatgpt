# ALO186 AI CMS insan inceleme paketi

## İçerik

- **Başlık:** UPS EPO ve REPO Acil Kapatma Devresi Kabul Testi
- **Canonical adayı:** `/haberler/ups-epo-repo-acil-kapatma-devresi-kabul-testi`
- **Birincil anahtar ifade:** `UPS EPO REPO kabul testi`
- **Risk sınıfı:** `high`
- **Fırsat puanı:** **97/100**
- **AI CMS kalite hedefi:** **100/100**
- **Durum:** `review`

## Kullanıcı görevi

UPS EPO/REPO işlevini normal, akü ve bypass modlarında; bütün AC/DC kaynaklar, haricî kesiciler, alarm, reset ve kontrollü yeniden başlatma kanıtlarıyla doğrulayan kabul dosyası hazırlamak.

## Kaynak doğrulaması

| ID | Yayıncı | Kaynak | Erişim |
|---|---|---|---|
| S1 | IEC | IEC 62040-1:2017+A1:2021+A2:2022 — UPS Safety Requirements | 2026-08-03 |
| S2 | Schneider Electric | Easy UPS 3M Operation Manual — EPO | 2026-08-03 |
| S3 | Schneider Electric | Easy UPS 3L Operation Manual — Remote EPO | 2026-08-03 |
| S4 | Eaton | UPS RPO and ROO Remote Power Control | 2026-08-03 |
| S5 | Schneider Electric | Configure Input Contacts and Output Relays for Easy UPS | 2026-08-03 |

## AEO, SEO ve kullanıcı faydası

- İlk ekranda bağımsız doğrudan cevap bulunur.
- Beş kaynak bağlı bölüm ve dört görünür SSS hazırlanmıştır.
- Yedi doğrulanmış bağlamsal iç bağlantı eklenmiştir.
- Canonical derleyici `Article`, `FAQPage` ve `BreadcrumbList` üretmelidir.
- Kurumsal yazar `Organization` olmalıdır; `Person`, `Product` ve `Offer` kullanılmamalıdır.
- Birincil CTA kişisel verisiz kabul/ölçüm matrisi ve teknik kanıt dosyasıdır.
- Mevcut sistem bütün senaryoları kanıtla geçiyorsa gereksiz ekipman veya yazılım satın alınmamalıdır.
- Tahmini en yüksek benzerlik `0.47`; fail-closed eşik `0,78`’dir.

## Güvenlik ve mevzuat sınırı

İçerik, EPO'yu izolasyon veya LOTO yerine sunmaz; enerjili UPS, bypass, akü barası, haricî kesici ve kontrol terminallerine kullanıcı müdahalesi önermez. Test yalnız üretici prosedürü, onaylı risk değerlendirmesi ve yetkin ekip ile yapılmalıdır. Affiliate kapalıdır.

## İnsan onayı

```text
/cms approve ups-epo-repo-acil-kapatma-devresi-kabul-testi
```

AI ve bot yorumları onay sayılmaz. Onay sonrası canonical HTML, routing overlay ve ChatGPT Sites önizleme artifactı hazırlanır; ayrıca insan merge'i gerekir.
