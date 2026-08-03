# ALO186 AI CMS insan inceleme paketi

## İçerik

- **Başlık:** EV Plug & Charge ISO 15118 Sertifika Kabul Testi
- **Canonical adayı:** `/haberler/ev-plug-charge-iso-15118-sertifika-fallback-kabul`
- **Birincil anahtar ifade:** `ISO 15118 Plug Charge kabul testi`
- **Risk sınıfı:** `legal`
- **Fırsat puanı:** **96/100**
- **AI CMS kalite hedefi:** **100/100**
- **Durum:** `review`

## Kullanıcı görevi

ISO 15118 Plug & Charge akışını EV-EVSE sürümü, EVSE ve sözleşme sertifika zincirleri, yenileme/iptal, CPMS-OCPP, saat, ağ kesintisi ve RFID/uygulama fallback senaryolarıyla uçtan uca kabul etmek.

## Kaynak doğrulaması

| ID | Yayıncı | Kaynak | Erişim |
|---|---|---|---|
| S1 | ISO | ISO 15118-20:2022 — Second Generation Network and Application Layer Requirements | 2026-08-03 |
| S2 | ISO | ISO 15118-20:2022/Amd 1:2026 — AC DER, MCS and Improved Security Concept | 2026-08-03 |
| S3 | Hubject | Plug&Charge Ecosystem | 2026-08-03 |
| S4 | Hubject | Signing a CSR and Obtaining an EVSE Leaf Certificate | 2026-08-03 |
| S5 | Hubject | Requirements for CPMS | 2026-08-03 |
| S6 | CharIN | Certificate Policy Guideline for an ISO 15118 V2G PKI | 2026-08-03 |

## AEO, SEO ve kullanıcı faydası

- İlk ekranda bağımsız doğrudan cevap bulunur.
- Beş kaynak bağlı bölüm ve dört görünür SSS hazırlanmıştır.
- Yedi doğrulanmış bağlamsal iç bağlantı eklenmiştir.
- Canonical derleyici `Article`, `FAQPage` ve `BreadcrumbList` üretmelidir.
- Kurumsal yazar `Organization` olmalıdır; `Person`, `Product` ve `Offer` kullanılmamalıdır.
- Birincil CTA kişisel verisiz kabul/ölçüm matrisi ve teknik kanıt dosyasıdır.
- Mevcut sistem bütün senaryoları kanıtla geçiyorsa gereksiz ekipman veya yazılım satın alınmamalıdır.
- Tahmini en yüksek benzerlik `0.36`; fail-closed eşik `0,78`’dir.

## Güvenlik ve mevzuat sınırı

İçerik gerçek müşteri EMAID, sözleşme sertifikası, token, özel anahtar, ödeme veya lokasyon verisi istemez. Test ortamı ve maskelenmiş log kullanılmalıdır. Plug & Charge uyumu ödeme, roaming veya mevzuat uygunluğu garantisi değildir. Affiliate kapalıdır.

## İnsan onayı

```text
/cms approve ev-plug-charge-iso-15118-sertifika-fallback-kabul
```

AI ve bot yorumları onay sayılmaz. Onay sonrası canonical HTML, routing overlay ve ChatGPT Sites önizleme artifactı hazırlanır; ayrıca insan merge'i gerekir.
