# ALO186 AI CMS insan inceleme paketi

## İçerik

- **Başlık:** GES MC4 Konnektör Eşleşmesi ve Krimp Kabulü
- **H1:** Farklı marka MC4 tipi konnektör bağlanır mı? GES DC kabul planı
- **Canonical adayı:** `/haberler/ges-mc4-konnektor-capraz-eslestirme-krimp-kabul`
- **Birincil anahtar ifade:** `GES MC4 konnektör eşleşmesi`
- **Risk sınıfı:** `high`
- **Fırsat puanı:** **94/100**
- **AI CMS kalite hedefi:** **100/100**
- **Durum:** `review` — canonical HTML veya routing overlay henüz yok

## Kullanıcı görevi

PV dizisinde farklı marka veya belirsiz MC4 tipi konektörlerin güvenli eşleşip eşleşmediğini, kullanıcı müdahalesi olmadan ürün ailesi ve saha kabul kanıtlarıyla belirlemek.

## Doğrudan cevap

İki PV konektörün fiziksel olarak birleşmesi güvenli eşleşme kanıtı değildir. Üretici, ürün ailesi, sertifika kapsamı, kablo kesiti ve dış çapı, metal kontak, krimp takımı ve montaj talimatı birlikte doğrulanmalıdır. Farklı markaların çapraz eşleşmesi veya belirsiz krimp varsa bağlantı yük altında ayrılmamalı; yetkili ekip ürün kimliği ve ölçümlü saha kabulü hazırlamalıdır.

## Mevcut içerikten görev ayrımı

PV konektör çapraz eşleşme ve krimp kabulü mevcut AFCI, Riso, string sigortası ve termal derating içeriklerinden ayrı bir saha kabul görevidir.

Tahmini en yüksek başlık/H1 benzerliği: **0.310** — en yakın rota: `/haberler/ges-inverter-afci-dc-ark-hatasi`. Fail-closed AI CMS doğrulaması gerçek envanter üzerinde yeniden hesaplar; `0,78` veya üzeri benzerlikte onay durmalıdır.

## Bölümler ve kaynak bağı

- **“MC4 uyumlu” etiketi neden tek başına eşleşme kanıtı değildir?** — S1, S2, S3
- **Farklı marka çapraz eşleştirme hangi riskleri oluşturur?** — S1, S3
- **Krimp, kablo kesiti ve takım uyumluluğu nasıl doğrulanır?** — S1, S2, S4
- **Saha kabulünde hangi kanıtlar toplanmalıdır?** — S1, S2, S4
- **Kullanıcı neyi kaydetmeli, neyi kesinlikle yapmamalıdır?** — S1, S2, S3, S4

## Kaynak doğrulaması

| Ref | Yayıncı | Kaynak | Erişim | Birincil |
|---|---|---|---|---|
| S1 | IEC | IEC 62852:2014+A1:2020 — Connectors for DC-application in photovoltaic systems | 2026-08-03 | Evet |
| S2 | IEC | IEC 62548-1:2023+A1:2025 — Photovoltaic arrays, design requirements | 2026-08-03 | Evet |
| S3 | Stäubli | Why preventing cross-mating is critical for PV connector safety | 2026-08-03 | Evet |
| S4 | Stäubli | Tools and accessories for photovoltaic connector field installation | 2026-08-03 | Evet |

Bütün teknik iddialar yalnız içerik kaydındaki `factSummary` ve ilgili `S#` kaynak referanslarına dayanmalıdır. Evrensel ürün eşiği, garanti, fiyat, stok veya resmî onay iddiası eklenmemelidir.

## İç bağlantılar

- `/haberler/ges-inverter-afci-dc-ark-hatasi` — Konnektör kaynaklı olası DC ark belirtisini AFCI olay kaydıyla ilişkilendirir.
- `/haberler/ges-inverter-izolasyon-direnci-dusuk-hatasi` — Konnektör, kablo ve nem kaynaklı izolasyon arızası görev ayrımını tamamlar.
- `/haberler/ges-inverter-sicakta-guc-dusuruyor-temperature-derating` — Bağlantı sıcak noktası ile inverterin normal termal güç düşürmesini ayırır.
- `/haberler/ges-inverter-sebeke-gerilimi-yuksek-hatasi` — DC bağlantı kusuru ile AC şebeke gerilimi kaynaklı üretim kaybını ayırır.
- `/hesaplama/gunes-paneli-power-station-uygunluk/` — Düşük gerilimli taşınabilir panel bağlantılarında ayrı teknik uyum aracına yönlendirir.
- `/elektrik-portali` — Kullanıcıyı diğer GES güvenlik ve karar rehberlerine taşır.
- `/kurumsal-elektrik-surekliligi-on-degerlendirme` — Ticari GES için kanıt dosyası ve teknik kabul kapsamını profesyonel sürece bağlar.

## AEO / SEO ve yapılandırılmış veri

- benzersiz title, meta description, H1 ve canonical adayı;
- ilk ekranda bağımsız doğrudan cevap;
- beş kaynak bağlı bölüm ve dört görünür SSS;
- kurumsal `Organization` yazarlığı;
- canonical derleyicide `Article`, `FAQPage` ve `BreadcrumbList`;
- `Product`, `Offer`, `Person` ve `ProfilePage` yasağı;
- kaynak erişim tarihi ve görünür atıf zinciri;
- kullanıcıya teslim edilebilir ölçüm/kabul dosyası.

## Güvenlik ve dönüşüm sınırı

Bu içerik `high` risk sınıfındadır. Affiliate ve ürün satın alma CTA’sı kapalıdır. Enerjili pano, PV DC bağlantısı, makine güvenlik zinciri veya yüksek frekans ölçümü kullanıcı işlemi olarak sunulamaz. Dönüşüm çağrısı; kişisel verisiz kontrol listesi, teknik kanıt dosyası ve yetkili profesyonel ön değerlendirmedir. Mevcut sistem ölçüm ve kayıtlarla yeterliyse satın almama sonucu korunur.

## İnsan onayı

Teknik içerik, kaynak, görev ayrımı, iç bağlantılar ve güvenlik sınırı kabul edilirse PR konuşmasına tam olarak şu yorum eklenmelidir:

```text
/cms approve ges-mc4-konnektor-capraz-eslestirme-krimp-kabul
```

AI veya otomasyon bu komutu veremez. Onay sonrasında canonical HTML, routing overlay ve ChatGPT Sites önizleme artifactı oluşur; zorunlu kontroller geçmeden merge edilmemelidir.
