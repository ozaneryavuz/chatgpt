# ALO186 AI CMS insan inceleme paketi

## İçerik

- **Başlık:** GES DC Ayırıcı Polarite, Termal Isınma ve Ark Kabul Testi
- **Canonical adayı:** `/haberler/ges-dc-ayirici-polarite-termal-ark-kabul-testi`
- **Birincil anahtar ifade:** `GES DC ayırıcı arızası ve kabul testi`
- **Risk sınıfı:** `high`
- **Fırsat puanı:** **95/100**
- **AI CMS kalite hedefi:** **100/100**
- **Durum:** `review`

## Kullanıcı görevi

PV dizisi veya inverter DC girişindeki ayırma cihazının doğru DC-PV sınıfı, gerilim-akım ve kutup konfigürasyonuna sahip olduğunu; polarite, bağlantı torku, çevre koşulu, termal davranış ve güvenli izolasyon kanıtlarıyla doğrulamak.

## Kaynak doğrulaması

| ID | Yayıncı | Kaynak | Erişim |
|---|---|---|---|
| S1 | IEC | IEC 60947-3:2020+AMD1:2025 — Switches and switch-disconnectors | 2026-08-03 |
| S2 | IEC | IEC 62548-1:2023+AMD1:2025 — Photovoltaic array design requirements | 2026-08-03 |
| S3 | IEC | IEC 60364-7-712:2025 — Solar photovoltaic power supply installations | 2026-08-03 |
| S4 | IEC | IEC 62446-1:2016+A1:2018 — PV documentation, commissioning tests and inspection | 2026-08-03 |
| S5 | IEC | IEC TS 62446-3:2017 — Outdoor infrared thermography of PV plants | 2026-08-03 |
| S6 | Schneider Electric | Acti9 C60NA-DC, C120NA-DC and SW60-DC PV switch-disconnectors | 2026-08-03 |

## AEO, SEO ve kullanıcı faydası

- İlk ekranda bağımsız doğrudan cevap bulunur.
- 5 kaynak bağlı bölüm ve 4 görünür SSS hazırlanmıştır.
- 7 doğrulanmış bağlamsal iç bağlantı eklenmiştir.
- Canonical derleyici `Article`, `FAQPage` ve `BreadcrumbList` üretmelidir.
- Kurumsal yazar `Organization` olmalıdır; `Person`, `Product` ve `Offer` kullanılmamalıdır.
- Birincil CTA kişisel verisiz kabul/ölçüm matrisi ve teknik kanıt dosyasıdır.
- Mevcut sistem bütün senaryoları kanıtla geçiyorsa gereksiz ekipman veya yazılım satın alınmamalıdır.
- Tahmini en yüksek benzerlik `0.46`; fail-closed eşik `0,78`’dir.

## Güvenlik ve mevzuat sınırı

İçerik; yük altında DC ayırıcı açma, enerjili PV stringinde kutup değiştirme, kapak açma veya kullanıcı termal ölçümü önermez. PV DC devrelerinde tehlikeli gerilim güneş varken mevcut olabilir; test yalnız onaylı izolasyon, üretici prosedürü ve yetkin ekip ile yapılmalıdır. Affiliate kapalıdır.

## İnsan onayı

```text
/cms approve ges-dc-ayirici-polarite-termal-ark-kabul-testi
```

AI ve bot yorumları onay sayılmaz. Onay sonrası canonical HTML, routing overlay ve ChatGPT Sites önizleme artifactı hazırlanır; ayrıca insan merge'i gerekir.
