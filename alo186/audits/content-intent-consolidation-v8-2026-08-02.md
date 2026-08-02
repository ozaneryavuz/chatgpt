# ALO186 güven odaklı içerik niyeti konsolidasyonu v8

Tarih: 2 Ağustos 2026

## Seçim yöntemi

Mevcut teknik makale envanteri, içerik başlıkları, H1 alanları ve kullanıcı görevleri karşılaştırıldı. Bu çalıştırmada yeni ürün veya makale eklemek yerine aynı arama niyetini bölerek kullanıcı karar yükü ve SEO kanibalizasyonu oluşturan üç küme seçildi.

## 1. Jeneratör Reverse Power / ANSI 32R kümesi

Tercih edilen canonical rota:

`/haberler/jenerator-reverse-power-ansi-32r-motoring-ct-polarite-teshis`

Birleştirilen dört tarihsel rota:

- `/haberler/jenerator-ters-guc-reverse-power-alarmi-ansi-32`
- `/haberler/jenerator-ters-guc-reverse-power-alarmi-ansi-32r`
- `/haberler/jenerator-reverse-power-ters-guc-ansi-32r-motoring-koruma`
- `/haberler/jenerator-reverse-power-ansi-32r-negatif-kw-ct-polarite-teshis`

Kullanıcı faydası: negatif kW, motoring, CT/VT faz eşleşmesi, güç yönü ve prime mover tork kaybı tek güncel teşhis zincirinde bulunur.

Beklenen gelir/lead etkisi: beş farklı teknik CTA yerine tek ölçülebilir kurumsal ön değerlendirme rotası; bölünmüş arama ve iç bağlantı sinyallerinin azalması. Gelir, sıralama veya arıza çözümü garantisi verilmez.

## 2. UPS Fan Failure / Overtemperature kümesi

Tercih edilen canonical rota:

`/haberler/ups-fan-failure-overtemperature-hava-akisi-filtre-teshis`

Birleştirilen rota:

`/haberler/ups-fan-failure-overtemperature-yuksek-sicaklik-derating-teshis`

Kullanıcı faydası: fan, tach geri bildirimi, filtre, hava yolu, ortam sıcaklığı, yük, sensör ve termal derating aynı kanıt zincirinde değerlendirilir. Rastgele fan/parça değişimi veya plansız bypass yönlendirmesi yapılmaz.

Beklenen gelir/lead etkisi: UPS bakım ve termal kabul niyeti tek sayfada ölçülür. Affiliate ürün, fiyat, stok, puan veya garanti bilgisi eklenmez.

## 3. Jeneratör Underfrequency / düşük frekans kümesi

Tercih edilen canonical rota:

`/haberler/jenerator-underfrequency-dusuk-frekans-governor-yuk-adimi-teshis`

Birleştirilen rota:

`/haberler/jenerator-underfrequency-dusuk-frekans-governor-hunting-yuk-alma`

Kullanıcı faydası: gerçek frekans, motor devri, yük adımı, governor/actuator, yakıt-hava yolu, derating ve toparlanma süresi tek akışta doğrulanır; ölçümsüz ayar veya parça değişimi teşvik edilmez.

Beklenen gelir/lead etkisi: jeneratör test, devreye alma ve teknik inceleme niyeti tek kabul rotasında toplanır.

## Uygulanan yayın davranışı

Mevcut `content-consolidations.json` altyapısının sürümü 8'e çıkarıldı ve altı yeni alias kaydı eklendi. Mevcut fail-closed üretim hattı:

- Apache destekli yayında gerçek 301 kuralları üretir,
- GitHub Pages artifact'ında `noindex,follow`, `rel=canonical`, meta refresh ve `location.replace` geçiş sayfası oluşturur,
- alias URL'leri sitemap ve release rota envanterinden çıkarır,
- canonical hedefleri sitemapte tutar,
- custom-domain ve project-path paketlerinde base-path uyumunu korur,
- eski paylaşılan URL'leri kaybetmeden kullanıcıyı güncel rehbere taşır.

## Güven ve ticari sınırlar

- Yeni Amazon veya başka mağaza bağlantısı eklenmedi.
- Doğrulanmamış fiyat, stok, puan, satıcı, teslimat ve garanti bilgisi kullanılmadı.
- `Product`, `Offer` veya `AggregateRating` eklenmedi.
- ALO186'in EDAŞ veya kamu kurumu olmadığı yönlendirme sayfalarında görünürdür.
- Kullanıcıya proje onayı, teknik uygunluk, kesin arıza çözümü veya kesintisiz çalışma garantisi verilmez.
- Bu çalıştırmada satın alma dönüşümü yerine organik otorite ve nitelikli teknik lead kalitesi önceliklendirildi.

## Doğrulanan yöntem kaynakları

Google Search Central kaynakları 2 Ağustos 2026 tarihinde yeniden kontrol edildi:

- Canonicalization overview
- Canonical URL belirleme ve duplicate URL birleştirme yöntemleri
- Sitemap overview ve sitemap oluşturma rehberi

Google; redirect ve `rel=canonical` sinyallerinin güçlü, sitemap katılımının daha zayıf bir canonical tercihi olduğunu; iç bağlantıların tercih edilen URL'ye verilmesini ve sitemapte gösterilmek istenen canonical URL'lerin listelenmesini önerir. Canonical seçimi ve indeksleme sonucu garanti değildir.

## Tamamlanamayan kontroller

- Search Console sitemap gönderimi ve URL Inspection için bağlı yazma aracı bulunmuyor.
- Merge sonrasında özel alan adı dağıtımı, CDN/önbellek yenilenmesi ve gerçek HTTP davranışı bağımsız canlı kontrol gerektirir.
- Arama motorlarının yeniden tarama, canonical seçimi ve sıralama etkisi anlık değildir.
