# Elektrik Sürekliliği Olgunluk Skoru

Otel, site ve işletmelerin elektrik sürekliliği yönetim disiplinini kişisel veri istemeden ön değerlendiren ücretsiz B2B araçtır.

## Model

- 8 boyut
- 24 kapalı uçlu soru
- Yanıt değerleri: Hayır `0`, Kısmen `0,5`, Evet `1`
- Soru bazlı görünür ağırlık
- 0–100 toplam skor
- Kırılgan, Reaktif, Kontrollü, Dirençli ve İleri sonuç bantları
- En zayıf üç boyut
- Kritik temel boşluklar
- Önceliğe göre 30/60/90 günlük plan

Skor ALO186 heuristiğidir. ISO 22301 sertifikası, elektrik projesi, uygunluk raporu veya resmî denetim değildir.

## Gizlilik

- Ad, şirket, telefon, e-posta, adres, abonelik ve serbest metin yoktur.
- Tesis türü ve teknik kapalı uçlu yanıtlar tarayıcıda en fazla 30 gün saklanabilir.
- Acil tehlike ve tıbbi/yaşam destek yükü seçimleri kalıcı depolamaya yazılmaz.
- JSON yönetici özetinde ham yanıtlar ve hassas seçimler bulunmaz.

## Güvenlik

- Yangın, duman, elektrik çarpması, kıvılcım veya düşmüş iletkende skor yerine 112 önceliği gösterilir.
- Sabit tesisat, transfer, jeneratör, UPS/batarya, trifaze ve hassas yüklerde saha doğrulaması gerekir.
- Affiliate ürün bağlantısı yoktur.
- Düşük skor tek başına ekipman satın alma gerekçesi değildir.

## Büyüme akışı

```text
Ücretsiz olgunluk skoru
→ 30/60/90 günlük yönetici planı
→ Elektrik Sürekliliği Paneli
→ çok kullanıcılı SaaS
→ aylık abonelik
```

## Analytics

PII içermeyen olaylar:

- `continuity_maturity_assessment_completed`
- `continuity_maturity_emergency_route_shown`
- `continuity_maturity_draft_restored`
- `continuity_maturity_exported`
- `continuity_maturity_printed`
- `continuity_maturity_panel_opened`
- `continuity_maturity_reset`

## Test

```bash
node alo186/tests/test_continuity_maturity_score.js
```

Test; skor bantları, monotonluk, kritik boşluk, plan sıralaması, localStorage allowlist ve süre sonu, export veri minimizasyonu, canonical, JSON-LD, PII/Amazon yasağı, erişilebilirlik ve mobil sözleşmeleri kapsar.
