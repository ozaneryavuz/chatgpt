# ALO186 Elektrik Sürekliliği — Production Runbook

## 1. Mimari karar

**Managed Core + Portable Escape Hatch** kullanılır.

### Managed core

- API, e-posta worker ve cron: Render Frankfurt
- PostgreSQL: Render Managed Postgres, Frankfurt, ücretli plan + connection pool
- Transactional e-posta: Postmark SMTP
- DNS: Cloudflare veya Natro eşdeğer kayıtları
- Yedek: Render PITR + Restic ile Cloudflare R2
- Hata izleme: Sentry
- Metrik/log: Grafana Cloud; portable Docker dağıtımında Grafana Alloy

### Taşınabilir kaçış yolu

- `docker-compose.production.yml`
- `ops/caddy/docker-compose.caddy.yml`
- `ops/monitoring/docker-compose.alloy.yml`
- PostgreSQL custom-format dump + Restic repository

Bu yapı sağlayıcı değişiminde uygulama kodunu değiştirmeden Render'dan bir VPS veya başka bir container platformuna taşınmayı sağlar.

## 2. Hedefler

| Konu | Hedef |
|---|---|
| Uygulama bölgesi | Frankfurt |
| RPO | Yönetilen PITR imkânına ek olarak en fazla 24 saatlik off-site yedek kaybı |
| RTO | Kritik olayda 4 saat içinde API ve DB geri dönüşü |
| TLS uyarı eşiği | Sertifika bitimine 21 gün |
| Health kontrolü | 15 dakikada bir haricî synthetic |
| DB backup | Her gün 01:43 UTC |
| Retention | 14 günlük, 8 haftalık, 12 aylık |
| Restore tatbikatı | Aylık, production dışı ayrı DB üzerinde |
| Secret rotasyonu | SMTP/R2/metrics 90 gün; token secret 180 gün |

## 3. Render bootstrap

1. Render hesabında GitHub deposunu bağlayın.
2. Repository kökündeki `render.yaml` dosyasından Blueprint oluşturun.
3. İlk sync sırasında `sync:false` secret değerlerini girin.
4. `alo186-postgres` için ücretli plan ve PITR/backup ayarını doğrulayın.
5. API pre-deploy logunda `alembic upgrade head` başarısını doğrulayın.
6. `/health/live` ve `/health/ready` HTTP 200 olmadan custom domain eklemeyin.

### Blueprint secret eşlemesi

API ve email worker aynı değerleri kullanmalıdır:

- `ALO186_TOKEN_SECRET`
- `ALO186_DATA_ENCRYPTION_KEY`
- `ALO186_SMTP_USERNAME`
- `ALO186_SMTP_PASSWORD`
- `ALO186_SENTRY_DSN`

Render'ın farklı servislerde bağımsız secret üretmesine izin vermeyin. API'de üretilen token/encryption değerini güvenli biçimde worker'a aynı değer olarak girin.

## 4. Secret bootstrap

Yerel ve çevrimdışı bir makinede:

```bash
cd alo186/sureklilik-api
python ops/secrets/generate_secrets.py --output-dir /secure/alo186-secrets
```

Script secret değerlerini terminale yazdırmaz ve dosyaları `0600` izinle oluşturur.

Dış sağlayıcıdan alınması gereken değerler:

- Postmark Server Token
- Sentry DSN
- Cloudflare R2 bucket-scoped Access Key ID ve Secret Access Key
- R2 account ID ve Restic repository URL

Secret klasörünü Git'e, Drive'a, Slack'e veya e-postaya eklemeyin. Sağlayıcı secret manager'a taşıdıktan sonra güvenli biçimde silin.

## 5. PostgreSQL

### Connection string

Render `postgresql://` biçimi üretir. Uygulama bunu `postgresql+psycopg://` olarak normalize eder.

### Migration

```bash
cd alo186/sureklilik-api
export PYTHONPATH=.
alembic upgrade head
alembic current
alembic check
```

API container'ında `ALO186_RUN_MIGRATIONS=false`; migration yalnız Render `preDeployCommand` ile çalışır. Böylece çoklu instance başlangıcında migration yarışı oluşmaz.

### Credential rotation

1. Render'da yeni managed DB kullanıcısı oluşturun.
2. Blueprint/database reference kullanan servisleri sync edin.
3. API ve worker'ları redeploy edin.
4. Eski kullanıcıyla bağlantı kalmadığını doğrulayın.
5. Eski kullanıcıyı devre dışı bırakın.

## 6. SMTP / Postmark

1. Postmark'ta transactional server ve message stream oluşturun.
2. `noreply@alo186.com` veya alan adı sender signature doğrulayın.
3. Panelin verdiği DKIM ve return-path kayıtlarını Terraform `smtp_dns_records` değişkenine girin.
4. DMARC'ı önce `p=none` ile raporlama modunda başlatın.
5. 2–4 hafta temiz teslimat ve alignment sonrasında `quarantine`, ardından `reject` değerlendirin.
6. Gerçek kullanıcı göndermeden önce test e-postası, bounce ve spam complaint webhook/raporlarını kontrol edin.

Uygulama ayarları:

```text
ALO186_EMAIL_BACKEND=smtp
ALO186_SMTP_HOST=smtp.postmarkapp.com
ALO186_SMTP_PORT=587
ALO186_SMTP_USE_TLS=true
```

Server token kullanıcı adı ve parola olarak kullanılabilir; repository'ye yazılmaz.

## 7. DNS ve TLS

### Cloudflare Terraform

```bash
cd ops/dns/cloudflare
cp terraform.tfvars.example terraform.tfvars
export TF_VAR_cloudflare_api_token='...'
terraform init
terraform fmt -check
terraform validate
terraform plan
terraform apply
```

İlk aşamada `proxy_api=false` kullanın. Render custom domain ve sertifika doğrulandıktan sonra Cloudflare proxy istenirse ayrıca etkinleştirilir.

### Natro alternatifi

Cloudflare'a nameserver taşınmayacaksa Natro DNS panelinde eşdeğer kayıtları manuel oluşturun:

- `CNAME api` → Render API origin hostname
- Postmark DKIM TXT/CNAME kayıtları
- Postmark return-path CNAME
- `_dmarc` TXT

### Portable Caddy

VPS/compose kullanımında:

```bash
docker compose \
  -f docker-compose.production.yml \
  -f ops/caddy/docker-compose.caddy.yml \
  up -d --build
```

Caddy otomatik ACME TLS, HSTS ve güvenlik başlıkları sağlar. `/metrics` dışarı kapalıdır; Alloy iç Docker ağından scrape eder.

## 8. R2 / Restic backup

R2 için yalnız `alo186-backups` bucket'ına Object Read & Write yetkili dar kapsamlı token üretin.

```text
RESTIC_REPOSITORY=s3:https://<ACCOUNT_ID>.r2.cloudflarestorage.com/alo186-backups
AWS_DEFAULT_REGION=auto
```

Günlük cron:

1. `pg_dump --format=custom`
2. SHA-256 checksum
3. Manifest
4. Restic client-side encryption
5. R2 upload
6. 14 günlük / 8 haftalık / 12 aylık retention
7. `restic check`

### Aylık restore tatbikatı

Production'dan ayrı boş bir doğrulama DB'si hazırlayın:

```bash
export ALO186_RESTORE_CONFIRM=YES-RESTORE-ALO186-VERIFY
export ALO186_RESTORE_DATABASE_URL='postgresql://.../alo186_restore_verify'
/opt/alo186/restore_verify.sh
```

Script aynı production URL'sine restore etmeyi reddeder, checksum ve archive list kontrolü yapar, ardından Alembic ve temel tablo sorgularını çalıştırır.

## 9. Monitoring

### Sentry

- `ALO186_SENTRY_DSN` girildiğinde entegrasyon otomatik açılır.
- `send_default_pii=false`
- request body capture kapalı
- Başlangıç trace örnekleme: `%10`
- Alarm: 5 dakikada yüksek hata oranı, yeni regression ve kritik auth endpoint hataları

Sentry'ye e-posta, token, açık adres veya tesisat numarası tag olarak eklenmez.

### Grafana Cloud / Alloy

Portable compose ortamında:

```bash
docker compose \
  -f docker-compose.production.yml \
  -f ops/monitoring/docker-compose.alloy.yml \
  up -d
```

Alloy:

- API `/metrics` endpointini özel `X-Metrics-Token` ile scrape eder.
- Prometheus remote_write ile Grafana Cloud'a gönderir.
- Docker loglarını Loki'ye yollar.
- WAL ile kısa ağ kesintilerinde metrik tamponu sağlar.

Render managed ortamında Render log/metric exporter veya ayrı private collector kullanılabilir; Alloy compose konfigürasyonu kaçış yolu içindir.

### Haricî synthetic

GitHub repository variable:

```text
ALO186_PRODUCTION_MONITOR_ENABLED=true
ALO186_API_BASE_URL=https://api.alo186.com
ALO186_SMTP_HOST=smtp.postmarkapp.com
```

Workflow her 15 dakikada:

- DNS çözümleme
- TLS süresi
- `/health/live`
- `/health/ready`
- SMTP STARTTLS

kontrol eder. Sonuç artifact ve job summary olarak saklanır.

## 10. Production readiness

Secret/env değerleri sağlandıktan sonra:

```bash
python ops/production_readiness.py --online --api-url https://api.alo186.com
```

Hard failure varsa üretim deploy'u yapılmaz. Backup/Sentry eksikleri warning olarak görünür ancak ücretli pilot öncesi tamamlanmaları zorunludur.

## 11. Alarm eşikleri

| Alarm | Eşik | İlk aksiyon |
|---|---|---|
| API down | 2 ardışık synthetic | Render event/log, readiness ve DB kontrolü |
| Readiness fail | 1 kontrol | PostgreSQL bağlantı ve migration |
| TLS expiry | <21 gün | DNS/proxy/ACME doğrulaması |
| 5xx oranı | 5 dk içinde >%2 | Sentry regression ve release rollback |
| p95 latency | 15 dk >750 ms | DB pool, slow endpoint ve instance CPU |
| Email outbox backlog | >100 veya oldest >10 dk | SMTP, worker ve retry durumu |
| Backup age | >26 saat | Cron/R2/Restic secret kontrolü |
| Restore drill | >35 gün | Ayrı DB üzerinde restore_verify |
| Login 429 | Baz çizginin 3 katı | Bot/brute-force analizi |

## 12. Incident ve rollback

1. Incident başlangıç saatini ve request ID'yi kaydedin.
2. Kullanıcı etkisini belirleyin: auth, e-posta, tenant data, olay yönetimi.
3. Son deployment ile korelasyon varsa Render rollback kullanın.
4. Migration geri döndürülecekse önce yedek alın; destructive downgrade otomatik uygulanmaz.
5. Token veya SMTP/R2 secret sızıntısında ilgili credential'ı hemen rotate edin.
6. Kullanıcı verisi etkilenmişse KVKK olay değerlendirmesi başlatın.
7. Olay sonrasında root cause, kalıcı düzeltme ve test ekleyin.

## 13. Gerçek kaynak oluşturma sınırı

Repository içindeki IaC ve workflow'lar uygulanmıştır. Ancak aşağıdakiler sağlayıcı tokenları girilmeden oluşturulamaz:

- Render servis ve database instance'ları
- Postmark server/sender doğrulaması
- Cloudflare DNS kayıtları
- R2 bucket ve credentials
- Sentry project
- Grafana Cloud stack

Bu değerler sağlandığında Blueprint/Terraform/synthetic akışı manuel tahmin yerine tekrar üretilebilir deployment sağlar.
