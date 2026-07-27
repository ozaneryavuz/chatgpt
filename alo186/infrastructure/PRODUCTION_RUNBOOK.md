# ALO186 Production Runbook

## 0. Yayın kararı

Üretim açılışı aşağıdaki sekiz kapıdan geçmeden yapılmaz:

1. PostgreSQL paid + PITR
2. Alembic head
3. SMTP domain doğrulaması
4. Secret ve rotasyon kaydı
5. HTTPS/TLS ve DNS
6. Günlük offsite backup + restore tatbikatı
7. Sentry + Grafana + sentetik izleme
8. İlk admin MFA

## 1. Provider hazırlığı

### Render

- Frankfurt workspace/environment oluşturun.
- GitHub repository erişimini verin.
- Blueprint oluştururken dosya yolu:

```text
alo186/infrastructure/render/production.yaml
```

- İlk sync sırasında bütün `sync: false` değerlerini girin.
- Database planını ücretsiz seçmeyin; PITR için paid database kullanın.

### Postmark

- `alo186.com` sender domain.
- `noreply@alo186.com` transactional sender.
- DKIM, Return-Path, SPF ve DMARC işlemlerini `smtp/POSTMARK_RUNBOOK.md` ile tamamlayın.

### Cloudflare R2

- `alo186-db-restic`
- `alo186-db-monthly-vault`
- Her bucket için yalnız gerekli yetkiye sahip ayrı access token önerilir.
- Vault üzerinde 180 günlük lock; Restic bucket üzerinde haricî lifecycle/lock yok.

### Sentry

- FastAPI production project.
- DSN Render secret olarak girilir.
- PII gönderimi kapalıdır.
- Production traces örnekleme başlangıcı %5.

### Grafana Cloud

- Prometheus remote write endpoint, user ID ve API key alın.
- Render Alloy worker secret alanlarına girin.
- `monitoring/GRAFANA_ALERTS.md` alert setini oluşturun.

## 2. Secret bootstrap

```bash
python alo186/infrastructure/secrets/generate_secrets.py \
  --output "$HOME/.config/alo186/production.env"
chmod 600 "$HOME/.config/alo186/production.env"
```

Secret değerlerini:

- Render secret environment,
- GitHub `alo186-production` environment,
- şirket parola kasası

arasında yetki ihtiyacına göre dağıtın. Repository'ye kopyalamayın.

## 3. Blueprint deploy

Render Blueprint sync sonucunda beklenen kaynaklar:

```text
alo186-continuity-api        web
alo186-email-worker          worker
alo186-retention-cron        cron
alo186-r2-backup-cron        cron
alo186-grafana-alloy         worker
alo186-prod-db               PostgreSQL
```

Deploy sırası:

1. PostgreSQL hazır.
2. API image build.
3. `preDeployCommand: alembic upgrade head` başarılı.
4. API `/health/ready` 200.
5. Worker ve cron servisleri başlıyor.
6. Alloy remote write sağlıklı.

### Smoke test

Render hostname üzerinde:

```bash
curl -fsS https://<render-host>/health/live
curl -fsS https://<render-host>/health/ready
curl -fsS -I https://<render-host>/docs
```

Production kayıt testi, gerçek kullanıcı verisi olmadan ayrı pilot e-postasıyla yapılır.

## 4. DNS ve TLS

1. Render API servisine `api.alo186.com` custom domain ekleyin.
2. Render'ın verdiği hostname'i `ALO186_RENDER_API_HOSTNAME` olarak tanımlayın.
3. GitHub DNS workflow'unu önce `apply=false` çalıştırın.
4. Dry-run beklenen değişiklikleri gösteriyorsa `alo186-production` environment onayıyla `apply=true` çalıştırın.
5. İlk doğrulamada Cloudflare proxy kapalı olmalıdır.
6. Render domain doğrulamasını tamamlayın.
7. HTTPS çalıştıktan sonra proxy ihtiyacını ayrı smoke test ile değerlendirin.
8. Render TLS stabil olduktan sonra istenirse `onrender.com` subdomain kapatılır.

### DNS/TLS test

```bash
python alo186/infrastructure/monitoring/production_probe.py \
  --base-url https://api.alo186.com \
  --check-email-dns
```

## 5. SMTP kabul testi

```bash
python alo186/infrastructure/smtp/smtp_probe.py
python alo186/infrastructure/smtp/smtp_probe.py --send
bash alo186/infrastructure/smtp/check_email_dns.sh alo186.com
```

Uygulama üzerinden:

- kayıt doğrulama,
- parola sıfırlama,
- kuruluş daveti,
- olay başlangıç/kapanış

mesajları test edilir. Outbox retry ve duplicate gönderim davranışı gözlenir.

## 6. Backup ve restore kabulü

İlk backup cron sonucunda:

- heartbeat başarılı,
- R2 Restic snapshot mevcut,
- checksum mevcut,
- Grafana/alert kanalı sessiz

olmalıdır.

Sonra izole PostgreSQL üzerinde:

```bash
./alo186/sureklilik-api/infra/backup/restore_verify.sh latest
```

Tam restore yapılmadan production-ready etiketi verilmez.

## 7. Monitoring aktivasyonu

Repository variable:

```text
ALO186_PRODUCTION_MONITOR_ENABLED=true
```

Etkinleştirilmeden önce manual workflow bir kez başarıyla çalışmalıdır.

Gözlenecekler:

- Render health check
- GitHub sentetik DNS/TLS/readiness
- Grafana Prometheus metrikleri
- Sentry errors/regressions
- Backup heartbeat
- Postmark bounce/complaint

## 8. İlk tenant ve pilot

- Pilot tenant gerçek üretim müşterisinden ayrıdır.
- İlk admin e-posta doğrular ve MFA etkinleştirir.
- İkinci admin davet edilir; tek kişi bağımlılığı azaltılır.
- Örnek lokasyon, kritik yük, varlık testi ve olay aç/kapat akışı tamamlanır.
- Audit ve KVKK export çalıştırılır.

## 9. Rollback

### Uygulama deploy hatası

1. Render'da önceki başarılı deploy'a rollback.
2. Readiness ve auth smoke test.
3. Migration geriye uyumsuzsa uygulama rollback'ten önce DB restore/PITR kararı alınır.
4. Migration dosyaları manuel `downgrade` yapılmadan önce veri kaybı analizi yapılır.

### Veri hatası

1. Yazma trafiğini maintenance mode ile durdur.
2. Hata zamanını belirle.
3. Render PITR ile yeni recovery DB oluştur.
4. Recovery DB'yi izole doğrula.
5. API connection string'i recovery DB'ye geçir.
6. Readiness ve tenant testleri sonrası trafiği aç.

### Render bölge/sağlayıcı kaybı

1. Yeni PostgreSQL oluştur.
2. R2 Restic yedeğini restore et.
3. `docker-compose.production.yml` + Caddy fallback'i ayağa kaldır.
4. DNS `api` kaydını fallback hosta geçir.
5. TLS, readiness ve auth smoke test.

## 10. Olay yönetimi

Severity:

- SEV-1: API tamamen kapalı, veri bütünlüğü veya güvenlik ihlali
- SEV-2: Auth/e-posta/tenant fonksiyonu kritik bozuk
- SEV-3: Kısmi özellik veya performans bozulması

Her olayda:

1. İlk tespit zamanı
2. Etkilenen bileşen ve tenant
3. Geçici önlem
4. Kök neden
5. Kalıcı düzeltme
6. Test ve izleme
7. Kullanıcı bildirimi/KVKK değerlendirmesi
8. Postmortem aksiyonları

kaydedilir.

## 11. Aylık operasyon

- Secret yaklaşan rotasyonları
- PostgreSQL depolama ve bağlantı kullanımı
- R2 Restic check
- Backup restore drill takvimi
- Sentry yeni regression'ları
- Grafana alert gürültüsü
- Postmark bounce/complaint
- Kullanılmayan provider token'ları
- Maliyet/tenant ve e-posta/tenant
- Audit retention ve silme talepleri

## Çıkış kriteri

Aşağıdakilerin ekran görüntüsü veya log kaydı issue #29'a eklenir:

- Render Blueprint sync
- Alembic head
- API readiness
- TLS certificate
- Postmark domain verified
- R2 snapshot
- Restore drill
- Grafana metric
- Sentry test event
- GitHub synthetic green
