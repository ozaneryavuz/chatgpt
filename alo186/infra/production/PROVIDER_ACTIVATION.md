# ALO186 Provider Aktivasyonu

Bu belge, kaynak kodu ve otomasyonları gerçek Render, Cloudflare, Postmark, R2, Sentry ve Grafana kaynaklarına bağlamak için uygulanacak tek kontrollü sıradır.

## 0. Kaynak kalite kapısı

Provider hesabı oluşturulmadan ve ücretli kaynak açılmadan önce PR üzerinde şu kontrollerin tamamı yeşil olmalıdır:

- Render Blueprint resmî JSON Schema
- ALO186 Render semantik doğrulaması
- PostgreSQL URL ve metrics auth regresyonları
- ShellCheck
- Caddy 2.11.4 config ve Compose
- VPS ve Render Grafana Alloy config
- API ve backup Docker build
- Terraform validate
- Secret generator ve production preflight

Bu kapı, sağlayıcı maliyeti doğmadan önce hatalı konfigürasyonu yakalamak için zorunludur.

## 1. GitHub Environment

Repository Settings → Environments altında:

```text
alo186-production
```

oluşturun.

Önerilen korumalar:

- Required reviewer: en az 1 kişi
- Deployment branches: yalnız `main`
- Prevent self-review: ekip büyüdüğünde açık
- Environment secret'larının repository secret'larıyla karıştırılmaması

### GitHub Environment secrets

```text
CLOUDFLARE_API_TOKEN
CLOUDFLARE_ZONE_ID
POSTMARK_DKIM_VALUE
POSTMARK_SMTP_USERNAME
POSTMARK_SMTP_PASSWORD
POSTMARK_RETURN_PATH_VALUE
R2_ACCESS_KEY_ID
R2_SECRET_ACCESS_KEY
RESTIC_PASSWORD
RENDER_DEPLOY_HOOK_URL
```

### GitHub Environment variables

```text
ALO186_RENDER_API_HOSTNAME
ALO186_R2_ENDPOINT
ALO186_R2_BUCKET
ALO186_SMTP_TEST_RECIPIENT
POSTMARK_DKIM_HOST
POSTMARK_RETURN_PATH_HOST
```

### Repository variables

Canlı yayın doğrulamasından önce:

```text
ALO186_SYNTHETIC_MONITOR_ENABLED=false
```

Readiness başarılı olduktan sonra:

```text
ALO186_SYNTHETIC_MONITOR_ENABLED=true
```

## 2. Render `sync:false` değerleri

Blueprint oluşturulurken veya Render Dashboard'da:

### API

```text
ALO186_DATA_ENCRYPTION_KEY
ALO186_SMTP_USERNAME
ALO186_SMTP_PASSWORD
ALO186_SENTRY_DSN
```

### Backup cron

```text
RESTIC_REPOSITORY=s3:https://<account-id>.r2.cloudflarestorage.com/<bucket>
RESTIC_PASSWORD
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
ALO186_BACKUP_HEARTBEAT_URL
```

### Grafana Alloy

```text
GRAFANA_CLOUD_PROMETHEUS_URL
GRAFANA_CLOUD_PROMETHEUS_USERNAME
GRAFANA_CLOUD_API_KEY
```

`ALO186_TOKEN_SECRET` ve `ALO186_METRICS_TOKEN` Render tarafından otomatik üretilir; email ve retention worker bunları API servisinden referans alır.

## 3. En az yetki

- Cloudflare token: yalnız `alo186.com` zone DNS edit/read.
- R2 key: yalnız ALO186 backup bucket read/write/list.
- Postmark token: yalnız ALO186 transactional server.
- Grafana token: yalnız metrics publish.
- Render deploy hook: yalnız API servisi deploy.
- Sentry DSN public ingestion anahtarıdır; yine de repository'ye yazılmaz.

## 4. Aktivasyon sırası

### A. Secret bootstrap

```bash
python alo186/sureklilik-api/scripts/generate_production_secrets.py \
  --format shell \
  --output ~/.config/alo186/production-secrets.env
```

Dosya 0600 izniyle üretilir. Değerleri Render'a taşıyın ve şirket parola kasasında yedekleyin.

### B. R2

1. `ALO186 R2 backup repository bootstrap` workflow'unu `apply=false` çalıştırın.
2. Beklenen bucket adı doğruysa korumalı onayla `apply=true` çalıştırın.
3. Restic repository init ve check yeşil olmalıdır.

### C. Render

1. Kök `render.yaml` Blueprint olarak bağlanır.
2. Paid PostgreSQL ve bütün servisler Frankfurt olarak doğrulanır.
3. `sync:false` değerleri girilir.
4. İlk deploy ve Alembic pre-deploy tamamlanır.
5. Render hostname üzerinde `/health/live` ve `/health/ready` kontrol edilir.
6. API servisinde deploy hook oluşturulup GitHub Environment'a eklenir.

### D. Postmark

1. Sender domain eklenir.
2. DKIM ve Return-Path değerleri GitHub Environment'a eklenir.
3. SPF ikinci kayıt açmadan mevcut kayıtla birleştirilir.
4. DMARC önce `p=none` ile başlatılır.

### E. DNS

1. `ALO186 production DNS reconcile` workflow'u `apply=false`, `proxy_api=false` çalıştırılır.
2. Dry-run yalnız beklenen `api`, DMARC, DKIM ve Return-Path değişikliklerini göstermelidir.
3. Render custom domain eklenmişse `apply=true` çalıştırılır.
4. İlk doğrulama Cloudflare DNS-only yapılır.
5. Render TLS verified olduktan sonra proxy ancak ayrıca test edilerek açılır.

### F. Monitoring

1. Sentry DSN girilir ve kontrollü test event doğrulanır.
2. Grafana Alloy worker'da remote-write değerleri girilir.
3. Grafana Cloud'da ALO186 metrics görülür.
4. Backup heartbeat monitor URL'si Render backup cron'a girilir.

### G. Final readiness

`ALO186 production readiness gate` workflow'u çalıştırılır:

- Cloudflare DNS dry-run
- SMTP TLS/auth
- SPF/DMARC/DKIM/Return-Path
- R2 bucket ve Restic check
- Web/API/DNS/TLS sentetik kontrol

Bütün adımlar yeşil olmadan gerçek müşteri verisi alınmaz.

### H. Sürekli izleme

```text
ALO186_SYNTHETIC_MONITOR_ENABLED=true
```

yapılır. On beş dakikalık monitor başarısızlıkta tek GitHub alert issue açar; iyileşince aynı issue'yu kapatır.

## 5. Gerçek aktivasyon kanıtları

Issue içinde secret değeri göstermeden şu kanıtlar saklanır:

- Render Blueprint sync ekranı
- PostgreSQL paid/PITR durumu
- Alembic head
- API readiness JSON
- `api.alo186.com` TLS
- Postmark domain verified
- Restic snapshot listesi
- İzole restore drill özeti
- Grafana ilk metric timestamp'i
- Sentry test event ID
- GitHub readiness run URL'si

## 6. Geri alma

- DNS apply beklenmedik sonuç verirse reconciler dry-run ile hedef kaydı gösterir; Cloudflare kayıt geçmişi veya Terraform desired state ile eski değer geri girilir.
- Render deploy bozuksa son başarılı deploy'a rollback yapılır.
- DB migration sorunu varsa trafik açılmaz; PITR veya izole recovery DB üzerinden karar verilir.
- R2 init/backup başarısızsa ücretli müşteri onboarding'i durdurulur.
