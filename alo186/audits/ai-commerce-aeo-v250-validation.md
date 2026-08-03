# ALO186 AI-commerce AEO v250 doğrulama raporu

Tarih: 3 Ağustos 2026

## Uygulanan kapsam

1. Düşük riskli tam ürün kartlarında `Product`, `Recommendation` ve `ItemList` ilişkisi.
2. UPS–taşınabilir güç istasyonu karşılaştırmasında görünür tabloya kalıcı fragment ve `ItemList` + `Table` JSON-LD.
3. Ürün/senaryo bölümlerinde kalıcı `rehber-*` ve `urun-*` kimlikleri.
4. Amazon bağlantılarında `rel="sponsored nofollow noopener"` sözleşmesi.
5. Dinamik ürün eşleştiricide JavaScript gerektirmeyen görünür SSR başlangıç seçenekleri.
6. SSS cevaplarının doğal devamında düşük riskli iç çözüm bağlantıları.
7. Kök `llms.txt` ve AI crawler grupları bulunan `robots.txt`.
8. Custom-domain ve `/chatgpt` artifactları için aynı fail-closed doğrulama.

## Offer politikası

`Offer` desteği kod seviyesinde hazırdır; ancak güncel Amazon Türkiye fiyatı, para birimi, stok durumu, satıcı, doğrulama zamanı ve son geçerlilik tarihi görünür sayfayla aynı anda doğrulanmadan `Offer` yayımlanmaz. Başlangıç kaydı bilinçli olarak boştur.

Bu yaklaşım görünmeyen/eski fiyatı yapılandırılmış veride yayımlamayı, ürün varyantı değiştiğinde yanlış teklif göstermeyi ve Google yapılandırılmış veri kalite kurallarını ihlal etmeyi engeller.

## Yerel Schema.org doğrulaması

Fail-closed test şu kontrolleri yapar:

- bütün dokunulan JSON-LD bloklarının JSON olarak ayrıştırılması,
- `Product`, `Recommendation`, `ItemList`, `Table`, `FAQPage` ve `BreadcrumbList` ilişkilerinin görünür içerikle eşleşmesi,
- doğrulanmış kayıt yokken ürün `Offer` yayımlanmaması,
- ürün kartı ve şema fragmentlerinin mevcut HTML `id` değerlerine bağlanması,
- yinelenen deep-link kimliği bulunmaması,
- affiliate link rel sözleşmesi,
- SSR başlangıç kartlarının final HTML içinde bulunması.

## Google Rich Results Test yorumu

- `Article` ve `BreadcrumbList` tipleri korunur.
- `FAQPage` görünür SSS içeriğiyle eşleştirilir; Google'ın görünür sonuç politikaları zaman içinde değişebilir.
- `Product` verisi Schema.org bakımından ayrıştırılabilir olsa da fiyat/availability veya review/rating bulunmadığı için Product rich result uygunluğu iddia edilmez.
- Google Rich Results Test'in kamuya açık otomasyon API'si bulunmadığından canlı URL doğrulaması deployment sonrasında manuel arayüzden yapılmalıdır.

## Schema.org Validator yorumu

JSON-LD blokları yerel ayrıştırma ve tip sözleşmesinden geçer. Kamu validatorü canlı deployment sonrasında üç örnek URL için tekrar çalıştırılmalıdır:

- akım korumalı priz ürün seçimi,
- UPS–taşınabilir güç istasyonu karşılaştırması,
- akıllı ürün seçimi SSR başlangıç katmanı.

## Başarı ölçütleri

- JSON-LD parse hatası: 0
- eksik affiliate `rel` tokenı: 0
- doğrulanmamış Offer: 0
- SSR ürün sınıfı: 5
- karşılaştırma öğesi: 2
- tam ürün Recommendation: en az 3
- root `llms.txt`: mevcut
- AI crawler grubu: OAI-SearchBot, GPTBot, ChatGPT-User, PerplexityBot, ClaudeBot, Bytespider, Google-Extended
