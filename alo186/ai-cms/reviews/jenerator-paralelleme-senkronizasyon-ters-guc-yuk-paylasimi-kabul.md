# ALO186 AI CMS insan inceleme paketi

## İçerik

- **Başlık:** Jeneratör Paralelleme Testi: Senkronizasyon ve Ters Güç
- **Canonical adayı:** `/haberler/jenerator-paralelleme-senkronizasyon-ters-guc-yuk-paylasimi-kabul`
- **Birincil anahtar ifade:** `jeneratör paralelleme senkronizasyon ters güç testi`
- **Risk sınıfı:** `high`
- **Fırsat puanı:** **95/100**
- **AI CMS kalite hedefi:** **100/100**
- **Durum:** `review`

## Kullanıcı görevi

İki jeneratörün veya jeneratör ile şebekenin faz sırası, senkron kapanma, kesici süresi, kW-kVAr yük paylaşımı, ANSI 32R ters güç, haberleşme kaybı ve tam yük transfer senaryolarıyla güvenli paralel çalıştığını kanıtlayan kabul dosyası hazırlamak.

## Kaynak doğrulaması

| ID | Yayıncı | Kaynak | Erişim |
|---|---|---|---|
| S1 | DEIF | AGC 150 Dynamic Synchronisation | 2026-08-03 |
| S2 | DEIF | AGC 150 Function Overview | 2026-08-03 |
| S3 | DEIF | Reverse Power ANSI 32R | 2026-08-03 |
| S4 | Cummins | Generator Set Controls | 2026-08-03 |

## AEO, SEO ve kullanıcı faydası

- İlk ekranda bağımsız doğrudan cevap bulunur.
- Beş kaynak bağlı bölüm ve dört görünür SSS hazırlanmıştır.
- Yedi doğrulanmış bağlamsal iç bağlantı eklenmiştir.
- Canonical derleyici `Article`, `FAQPage` ve `BreadcrumbList` üretmelidir.
- Kurumsal yazar `Organization` olmalıdır; `Person`, `Product` ve `Offer` kullanılmamalıdır.
- Birincil CTA senkron kapanma, yük paylaşımı ve koruma kabul matrisidir.
- Evrensel senkron veya ters güç ayarı yayımlanmaz; değerler motor, alternatör, şebeke ve proje verisine bağlanır.
- Mevcut kontrol sistemi kanıtla yeterliyse gereksiz kontrolör veya paralelleme panosu satın almama sonucu korunur.
- Tahmini en yüksek benzerlik `0.34`; fail-closed eşik `0,78`’dir.

## Güvenlik sınırı

İçerik enerjili bara, CT/VT, kesici veya governor/AVR ayarlarına kullanıcı müdahalesi önermez. Paralelleme, ikincil enjeksiyon ve koruma trip testleri yalnız yetkin devreye alma ekibi, onaylı proje ve saha risk değerlendirmesiyle yapılmalıdır. Affiliate kapalıdır.

## İnsan onayı

```text
/cms approve jenerator-paralelleme-senkronizasyon-ters-guc-yuk-paylasimi-kabul
```

AI ve bot yorumları onay sayılmaz. Onay sonrası canonical HTML, routing overlay ve ChatGPT Sites önizleme artifactı hazırlanır; ayrıca insan merge’i gerekir.
