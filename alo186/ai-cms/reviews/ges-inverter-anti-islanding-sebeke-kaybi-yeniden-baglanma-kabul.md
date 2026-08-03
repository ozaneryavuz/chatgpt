# ALO186 AI CMS insan inceleme paketi

## İçerik

- **Başlık:** GES İnverter Anti-Islanding ve Yeniden Bağlanma Kabul Testi
- **Canonical adayı:** `/haberler/ges-inverter-anti-islanding-sebeke-kaybi-yeniden-baglanma-kabul`
- **Birincil anahtar ifade:** `GES inverter anti-islanding testi`
- **Risk sınıfı:** `legal`
- **Fırsat puanı:** **96/100**
- **AI CMS kalite hedefi:** **100/100**
- **Durum:** `review`

## Kullanıcı görevi

Şebekeye paralel çalışan GES inverterinin şebeke kaybında istenmeyen ada oluşturmadığını; gerilim-frekans, faz kaybı, çoklu inverter, yedekleme çıkışı ve yeniden bağlanma senaryolarında yetkili test kaydıyla kanıtlamak.

## Kaynak doğrulaması

| ID | Yayıncı | Kaynak | Erişim |
|---|---|---|---|
| S1 | IEC | IEC 62116:2014 — Test procedure of islanding prevention measures | 2026-08-03 |
| S2 | IEC | IEC 61727:2004 — Photovoltaic systems, characteristics of the utility interface | 2026-08-03 |
| S3 | IEC | IEC TS 62786-2:2026 — Additional grid-connection requirements for PV generation | 2026-08-03 |
| S4 | EPDK | Elektrik Piyasasında Lisanssız Elektrik Üretimi — resmî mevzuat ve anlaşmalar | 2026-08-03 |
| S5 | IEC | IEC 62446-1:2016+A1:2018 — Grid-connected PV documentation, commissioning and inspection | 2026-08-03 |

## AEO, SEO ve kullanıcı faydası

- İlk ekranda bağımsız doğrudan cevap bulunur.
- 5 kaynak bağlı bölüm ve 4 görünür SSS hazırlanmıştır.
- 7 doğrulanmış bağlamsal iç bağlantı eklenmiştir.
- Canonical derleyici `Article`, `FAQPage` ve `BreadcrumbList` üretmelidir.
- Kurumsal yazar `Organization` olmalıdır; `Person`, `Product` ve `Offer` kullanılmamalıdır.
- Birincil CTA kişisel verisiz kabul/ölçüm matrisi ve teknik kanıt dosyasıdır.
- Mevcut sistem bütün senaryoları kanıtla geçiyorsa gereksiz ekipman veya yazılım satın alınmamalıdır.
- Tahmini en yüksek benzerlik `0.55`; fail-closed eşik `0,78`’dir.

## Güvenlik ve mevzuat sınırı

İçerik; canlı şebeke, sayaç/CT, inverter AC/DC terminalleri veya koruma rölelerine kullanıcı müdahalesi önermez. Anti-islanding testi dağıtım şirketi şartları, onaylı test planı, üretici prosedürü ve yetkin ekip ile yapılmalıdır. Tesis içi test resmî bağlantı/kabul onayının yerine geçmez. Affiliate kapalıdır.

## İnsan onayı

```text
/cms approve ges-inverter-anti-islanding-sebeke-kaybi-yeniden-baglanma-kabul
```

AI ve bot yorumları onay sayılmaz. Onay sonrası canonical HTML, routing overlay ve ChatGPT Sites önizleme artifactı hazırlanır; ayrıca insan merge'i gerekir.
