# Render Blueprint Kurulumu

## Blueprint yolu

Render Dashboard → New → Blueprint:

```text
Repository: ozaneryavuz/chatgpt
Branch: main
Blueprint file path: alo186/infrastructure/render/production.yaml
Region: Frankfurt
```

Blueprint şunları oluşturur:

- `alo186-continuity-api` — paid web service
- `alo186-email-worker` — background worker
- `alo186-retention-cron` — günlük KVKK/retention işi
- `alo186-r2-backup-cron` — günlük R2/Restic yedeği
- `alo186-grafana-alloy` — Grafana Cloud metrics forwarder
- `alo186-prod-db` — PostgreSQL 16, basic-1gb, 15 GB, autoscaling, PITR

## İlk sync sırasında girilecek değerler

API:

- `ALO186_DATA_ENCRYPTION_KEY`
- `ALO186_SMTP_USERNAME`
- `ALO186_SMTP_PASSWORD`
- `ALO186_SENTRY_DSN`

Backup cron:

- `ALO186_R2_ENDPOINT`
- `ALO186_R2_RESTIC_BUCKET`
- `ALO186_R2_VAULT_BUCKET`
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `RESTIC_PASSWORD`
- `ALO186_BACKUP_HEARTBEAT_URL`

Grafana Alloy:

- `GRAFANA_CLOUD_PROMETHEUS_URL`
- `GRAFANA_CLOUD_PROMETHEUS_USER`
- `GRAFANA_CLOUD_API_KEY`

`ALO186_TOKEN_SECRET` ve `ALO186_METRICS_TOKEN` Render tarafından otomatik üretilir. Worker'lar bu değerleri API servisinden referans alır.

## Deploy davranışı

- Auto deploy yalnız GitHub kontrolleri başarılıysa çalışır.
- Alembic migration API deploy öncesi `preDeployCommand` olarak çalışır.
- Uygulama runtime sırasında migration çalıştırmaz.
- `/health/ready` PostgreSQL bağlantısını doğrular.
- API custom domain: `api.alo186.com`.
- Render `onrender.com` hostname ilk kurulum ve rollback için açık kalır; custom domain stabil olduktan sonra kapatılabilir.

## PostgreSQL

- Uygulama yalnız Render private `connectionString` kullanır.
- Dış IP allow list boştur.
- Kod, Render'ın `postgresql://` URL'sini otomatik `postgresql+psycopg://` formatına çevirir.
- Paid instance PITR'ı hızlı kurtarma katmanıdır; R2 yedeğinin yerine geçmez.

## Blueprint güncelleme kuralı

Render `sync: false` değişkenleri yalnız ilk Blueprint oluşturma sırasında sorar. Sonradan eklenen yeni secret'lar Dashboard veya Render API üzerinden ayrıca tanımlanmalıdır.

## Üretim kabulü

1. Bütün servisler Frankfurt.
2. DB paid ve PITR görünür.
3. API deploy + migration başarılı.
4. Email worker outbox işliyor.
5. Backup cron R2 snapshot ve heartbeat üretiyor.
6. Alloy Grafana Cloud'a veri yazıyor.
7. Custom domain TLS verified.
8. Production readiness workflow yeşil.
