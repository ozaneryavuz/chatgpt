# ALO186 AI CMS insan inceleme paketi

## İçerik

- **Başlık:** GES İnverter Reaktif Güç Kabul Testi: cos φ ve Q(V)
- **Canonical adayı:** `/haberler/ges-inverter-reaktif-guc-cos-phi-qv-kabul-testi`
- **Birincil anahtar ifade:** `GES inverter reaktif güç kabul testi`
- **Risk sınıfı:** `legal`
- **Fırsat puanı:** **97/100**
- **AI CMS kalite hedefi:** **100/100**
- **Durum:** `review`

## Kullanıcı görevi

GES inverter reaktif güç kontrolünü bağlantı anlaşması, bağlantı noktası V-P-Q ölçümü, işaret yönü, sabit Q/cos φ/Q(V) karakteristiği, haberleşme kaybı ve zaman damgalı kVAr cevabıyla doğrulayan kabul dosyası hazırlamak.

## Kaynak doğrulaması

| ID | Yayıncı | Kaynak | Erişim |
|---|---|---|---|
| S1 | IEC | IEC TS 62786-1:2023 DER bağlantı genel şartları | 2026-08-03 |
| S2 | IEC | IEC TS 62786-2:2026 PV bağlantı ek şartları | 2026-08-03 |
| S3 | SMA | Q, cos φ ve Q(V) reaktif güç kontrolü | 2026-08-03 |
| S4 | TEİAŞ | Reaktif Güç Kontrolü Hizmeti | 2026-08-03 |
| S5 | TEİAŞ | 2026 hibrit santral RGK veri formatları | 2026-08-03 |
| S6 | SMA | Q on Demand 24/7 | 2026-08-03 |

## AEO, SEO ve kullanıcı faydası

- İlk ekranda bağımsız doğrudan cevap bulunur.
- Beş kaynak bağlı bölüm ve dört görünür SSS hazırlanmıştır.
- Yedi doğrulanmış bağlamsal iç bağlantı eklenmiştir.
- Canonical derleyici `Article`, `FAQPage` ve `BreadcrumbList` üretmelidir.
- Kurumsal yazar `Organization` olmalıdır; `Person`, `Product` ve `Offer` kullanılmamalıdır.
- Birincil CTA kişisel verisiz bağlantı noktası ölçüm ve reaktif güç kabul matrisidir.
- Mevcut sayaç, kontrolör ve inverter bütün testleri geçiyorsa gereksiz ekipman değişimi yapılmamalıdır.
- Tahmini en yüksek benzerlik `0.43`; fail-closed eşik `0,78`’dir.

## Güvenlik ve mevzuat sınırı

İçerik, başka tesisten parametre kopyalamayı veya enerjili CT/sayaç/inverter müdahalesini önermez. Dağıtım ve iletim yükümlülükleri ayrı doğrulanmalı; TEİAŞ test formatları yalnız ilgili tesis kapsamına uygulanmalıdır. Affiliate kapalıdır.

## İnsan onayı

```text
/cms approve ges-inverter-reaktif-guc-cos-phi-qv-kabul-testi
```

AI ve bot yorumları onay sayılmaz. Onay sonrası canonical HTML, routing overlay ve ChatGPT Sites önizleme artifactı hazırlanır; ayrıca insan merge’i gerekir.
