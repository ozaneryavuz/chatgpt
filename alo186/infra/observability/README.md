# ALO186 gözlemlenebilirlik ve alarm katmanı

## Üretim modeli

- API hata yakalama ve trace: Sentry
- Prometheus metrikleri: API `/metrics`
- Uzak metrik deposu ve dashboard: Grafana Cloud
- Render logları: Render Log Stream → Grafana Cloud Loki
- VPS/Caddy fallback logları: Grafana Alloy Docker log source
- Haricî erişim ve TLS: GitHub synthetic workflow veya Grafana Synthetic Monitoring

## API metrikleri

`/metrics` bearer token ile korunur. Alloy değişkenleri:

```text
ALO186_API_METRICS_TARGET=api.alo186.com
ALO186_METRICS_TOKEN=...
GRAFANA_CLOUD_PROMETHEUS_URL=...
GRAFANA_CLOUD_PROMETHEUS_USERNAME=...
GRAFANA_CLOUD_API_KEY=...
```

Alloy doğrulama/çalıştırma örneği:

```bash
alloy validate alo186/infra/observability/config.alloy
alloy run alo186/infra/observability/config.alloy
```

## Loglar

### Render

Render Dashboard → Log Streams bölümünde Grafana Cloud Loki hedefi tanımlanır. API logları JSON biçimindedir ve şu alanları taşır:

- `request_id`
- `method`
- `path`
- `status_code`
- `duration_ms`
- hash'lenmiş istemci bilgisi
- `user_id` ve `organization_id` yalnız operasyon bağlamında

Ham parola, token, MFA sırrı veya outbox payloadı loglanmamalıdır.

### Caddy/VPS

`config.alloy` içindeki Docker discovery bölümü Caddy ve API stdout loglarını Loki'ye gönderir. Docker socket salt okunur bağlanmalı ve Alloy host yetkileri sınırlandırılmalıdır.

## Sentry

Sentry yalnız `ALO186_SENTRY_DSN` doluysa etkinleşir. Kodda:

- `send_default_pii=false`
- küçük request body sınırı
- production ortam etiketi
- Render commit SHA release etiketi
- varsayılan trace örneklemesi %5

kullanılır.

Önerilen alarm hedefleri:

- kritik: e-posta + telefon/push
- warning: e-posta + günlük operasyon özeti
- bilgi: dashboard

## Prometheus alarm kuralları

`alerts.yml` şu koşulları tanımlar:

- 5xx oranı > %5 / 10 dakika
- ortalama gecikme > 1 saniye / 15 dakika
- in-flight istek > 50 / 5 dakika
- process sık yeniden başlama
- haricî API erişim kaybı
- TLS süresi < 21 gün

Grafana Cloud Alerting veya Prometheus ruler'a aktarılmadan önce gerçek trafik tabanı ve plan kapasitesine göre eşikler pilot verisiyle kalibre edilmelidir.

## Synthetic monitoring

GitHub workflow varsayılan olarak kapalıdır. Etkinleştirme:

```text
ALO186_SYNTHETIC_MONITOR_ENABLED=true
ALO186_SYNTHETIC_WEB_BASE=https://www.alo186.com
ALO186_SYNTHETIC_API_BASE=https://api.alo186.com
```

Her 15 dakikada:

- temel web rotaları,
- API liveness/readiness,
- TLS son kullanma süresi

kontrol edilir. Başarısız rapor GitHub Actions artifact'ında saklanır ve workflow kırmızıya düşer.

## Dashboard önerisi

1. İstek/saniye, status ve route dağılımı
2. Ortalama süre ve en yavaş route'lar
3. 5xx/4xx oranı
4. Process uptime ve in-flight istek
5. Auth/register/login/reset/davet endpoint hacmi
6. Outbox pending/retry/failed sayısı
7. DB bağlantı/readiness
8. Synthetic uptime ve TLS gün sayısı
9. Kuruluş/lokasyon/olay aktivasyon iş metrikleri

İş metrikleri Prometheus label'ı olarak kullanıcı veya kuruluş adı taşımamalıdır; yüksek kardinalite ve kişisel veri riski yaratır.
