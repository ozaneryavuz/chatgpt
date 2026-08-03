# ALO186 AI CMS insan inceleme paketi

## İçerik

- **Başlık:** BESS Ada Modu ve Black Start Kabul Testi
- **Canonical adayı:** `/haberler/bess-ada-modu-grid-forming-black-start-yeniden-senkron-kabul`
- **Birincil anahtar ifade:** `BESS ada modu black start kabul testi`
- **Risk sınıfı:** `legal`
- **Fırsat puanı:** **96/100**
- **AI CMS kalite hedefi:** **100/100**
- **Durum:** `review`

## Kullanıcı görevi

BESS'in grid-following ve grid-forming yeteneklerini ayırarak; SoC/yardımcı güç rezervi, ölü bara enerjilendirme, kademeli yük alma, GES-jeneratör koordinasyonu, ada koruması ve şebekeye yeniden senkron geçişi kanıtlayan kabul dosyası hazırlamak.

## Kaynak doğrulaması

| ID | Yayıncı | Kaynak | Erişim |
|---|---|---|---|
| S1 | IEC | IEC TS 62933-3-3:2022 ada ve yedek güç uygulamaları | 2026-08-03 |
| S2 | IEC | IEC 62933-3-1:2025 EES planlama ve performans | 2026-08-03 |
| S3 | IEC | IEC TS 62786-3:2023 BESS şebeke bağlantısı | 2026-08-03 |
| S4 | TEİAŞ | Müstakil depolama için oturan sistemin toparlanması | 2026-08-03 |
| S5 | EPDK | Elektrik Piyasası Yan Hizmetler Yönetmeliği | 2026-08-03 |
| S6 | TEİAŞ | 3 Temmuz 2026 depolama yan hizmet teknik kriterleri | 2026-08-03 |

## AEO, SEO ve kullanıcı faydası

- İlk ekranda bağımsız doğrudan cevap bulunur.
- Beş kaynak bağlı bölüm ve dört görünür SSS hazırlanmıştır.
- Yedi doğrulanmış bağlamsal iç bağlantı eklenmiştir.
- Canonical derleyici `Article`, `FAQPage` ve `BreadcrumbList` üretmelidir.
- Kurumsal yazar `Organization` olmalıdır; `Person`, `Product` ve `Offer` kullanılmamalıdır.
- Birincil CTA kişisel verisiz SoC rezervi, ölü bara, yük alma ve yeniden senkron kabul matrisidir.
- Mevcut BESS bütün senaryoları geçiyorsa gereksiz ek batarya, PCS veya EMS satın alınmamalıdır.
- Tahmini en yüksek benzerlik `0.39`; fail-closed eşik `0,78`’dir.

## Güvenlik ve mevzuat sınırı

İçerik kullanıcıya enerjili DC kabin, bara, kesici veya koruma devresinde müdahale yaptırmaz. Tesis içi ada/black start başarısı, TEİAŞ yan hizmet kabulü veya gelir garantisi sayılmaz. Affiliate kapalıdır.

## İnsan onayı

```text
/cms approve bess-ada-modu-grid-forming-black-start-yeniden-senkron-kabul
```

AI ve bot yorumları onay sayılmaz. Onay sonrası canonical HTML, routing overlay ve ChatGPT Sites önizleme artifactı hazırlanır; ayrıca insan merge’i gerekir.
