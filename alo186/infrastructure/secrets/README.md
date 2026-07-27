# ALO186 Secret Yönetimi

Repository yalnız secret **isimlerini, sahipliğini ve rotasyon politikasını** içerir. Gerçek değerler hiçbir zaman Git'e yazılmaz.

## Üretim modeli

- Render servis secret'ları: Render Environment Variables (`sync: false` veya `generateValue`).
- GitHub otomasyon secret'ları: `alo186-production` adlı korumalı GitHub Environment.
- Kurtarma secret'ları: şirket parola kasası + çevrimdışı, erişim kayıtlı ikinci kopya.
- Docker/VPS fallback: `/run/secrets/*` dosyaları ve mevcut `_FILE` desteği.

## İlk secret üretimi

Repository kökünden:

```bash
python alo186/infrastructure/secrets/generate_secrets.py \
  --output "$HOME/.config/alo186/production.env"
```

Araç dosyayı `0600` izinle oluşturur ve değerleri terminale yazmaz.

## Render'a girilecek zorunlu değerler

- `ALO186_DATA_ENCRYPTION_KEY`
- `ALO186_SMTP_USERNAME`
- `ALO186_SMTP_PASSWORD`
- `ALO186_SENTRY_DSN`
- `GRAFANA_CLOUD_PROMETHEUS_URL`
- `GRAFANA_CLOUD_PROMETHEUS_USER`
- `GRAFANA_CLOUD_API_KEY`
- `ALO186_R2_ENDPOINT`
- `ALO186_R2_RESTIC_BUCKET`
- `ALO186_R2_VAULT_BUCKET`
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `RESTIC_PASSWORD`
- `ALO186_BACKUP_HEARTBEAT_URL`

`ALO186_TOKEN_SECRET` ve `ALO186_METRICS_TOKEN` Blueprint tarafından üretilebilir.

## GitHub Environment

`alo186-production` ortamı oluşturulmalı ve production deploy/DNS workflow'larında manuel onay zorunlu kılınmalıdır.

Önerilen secret'lar:

- `CLOUDFLARE_API_TOKEN`
- `CLOUDFLARE_ZONE_ID`
- `RENDER_API_KEY`
- `RENDER_SERVICE_ID`

Önerilen variable'lar:

- `ALO186_PRODUCTION_MONITOR_ENABLED=false` — canlı doğrulama sonrası `true`
- `ALO186_RENDER_API_HOSTNAME`

## Rotasyon kuralları

- Token secret rotasyonu bütün oturumları iptal eder; bakım penceresinde yapılır.
- Data encryption key doğrudan değiştirilemez; önce eski anahtarla çöz, yeni anahtarla şifrele migration'ı gerekir.
- Restic parolası değiştirilirse eski snapshot'lara erişim parolası kurtarma kasasında korunur.
- R2, Cloudflare, Grafana, Render ve SMTP token'ları en az yetkiyle ve ayrı ayrı oluşturulur.
- Ayrılan personelin erişimleri aynı iş günü içinde iptal edilir.

Tam metadata `secret-inventory.yaml` dosyasındadır.
