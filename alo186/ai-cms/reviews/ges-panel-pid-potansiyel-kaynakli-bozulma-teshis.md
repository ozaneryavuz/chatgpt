# ALO186 AI CMS insan inceleme paketi

## İçerik

- **Başlık:** GES Panelinde PID Teşhisi: I-V, EL ve Sistem Gerilimi
- **Canonical adayı:** `/haberler/ges-panel-pid-potansiyel-kaynakli-bozulma-teshis`
- **Birincil anahtar ifade:** `GES panel PID teşhisi potansiyel kaynaklı bozulma`
- **Risk sınıfı:** `high`
- **Fırsat puanı:** **92/100**
- **AI CMS kalite hedefi:** **100/100**
- **Durum:** `review`

## Kullanıcı görevi

GES üretim kaybının PID olup olmadığını karşılaştırmalı string verisi, I-V eğrisi, görüntüleme, izolasyon ve modül-sistem gerilim ilişkisiyle kanıtlayan teknik teşhis dosyası hazırlamak.

## Kaynak doğrulaması

| ID | Yayıncı | Kaynak | Erişim |
|---|---|---|---|
| S1 | IEC | IEC TS 62804-1:2025 | 2026-08-03 |
| S2 | IEC | IEC 61215-1-1:2021 | 2026-08-03 |
| S3 | NREL | Potential-Induced Degradation: Critical Review | 2026-08-03 |
| S4 | NREL | PV Degradation Characterization Techniques | 2026-08-03 |

## AEO, SEO ve kullanıcı faydası

- İlk ekranda bağımsız doğrudan cevap bulunur.
- Beş kaynak bağlı bölüm ve dört görünür SSS hazırlanmıştır.
- Yedi doğrulanmış bağlamsal iç bağlantı eklenmiştir.
- Canonical derleyici `Article`, `FAQPage` ve `BreadcrumbList` üretmelidir.
- Kurumsal yazar `Organization` olmalıdır; `Person`, `Product` ve `Offer` kullanılmamalıdır.
- Birincil CTA kişisel verisiz PID teşhis ve öncesi-sonrası kabul dosyasıdır.
- PID kanıtlanmıyorsa gereksiz modül veya anti-PID cihazı satın almama sonucu korunur.
- Tahmini en yüksek benzerlik `0.34`; fail-closed eşik `0,78`’dir.

## Güvenlik sınırı

İçerik kullanıcıya enerjili PV stringi, inverter DC girişi veya topraklama sistemi üzerinde işlem yaptırmaz. Ölçüm ve iyileştirme yalnız yetkin ekip, uygun DC sınıfı cihaz ve saha güvenlik prosedürüyle yürütülmelidir. Affiliate kapalıdır.

## İnsan onayı

```text
/cms approve ges-panel-pid-potansiyel-kaynakli-bozulma-teshis
```

AI ve bot yorumları onay sayılmaz. Onay sonrası canonical HTML, routing overlay ve ChatGPT Sites önizleme artifactı hazırlanır; ayrıca insan merge’i gerekir.
