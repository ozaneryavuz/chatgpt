# ALO186 production infrastructure runbook

## 1. Mimari kararı

**Managed Core + Portable Escape Hatch**

```text
www.alo186.com
  └─ mevcut statik web hosting / Natro

api.alo186.com
  └─ Render managed TLS
      ├─ FastAPI web service
      ├─ e-posta worker
      ├─ retention cron
      ├─ R2/Restic backup cron
      └─ Render PostgreSQL 16

Haricî servisler
  ├─ Postmark SMTP
  ├─ Cloudflare DNS/WAF veya Natro DNS
  ├─ Cloudflare R2 yedek deposu
  ├─ Sentry hata/trace
  └─ Grafana Cloud metrics/logs/synthetic
```

Caddy yapılandırması sağlayıcı değişimi veya VPS kurtarma senaryosu için taşınabilir TLS/reverse proxy çıkışıdır.

## 2. RTO / RPO hedefleri

| Olay | RPO | RTO | Temel önlem |
|---|---:|---:|---|
| API instance kaybı | 0 | 15 dk | Render otomatik restart + health check |
| Hatalı uygulama deployu | 0 | 30 dk | önceki image/deploy rollback |
| PostgreSQL mantıksal bozulma | ≤24 saat | 4 saat | PITR + günlük Restic R2 yedeği |
| Render bölge/sağlayıcı sorunu | ≤24 saat | 8 saat | Caddy/VPS fallback + Restic restore |
| Statik site rota bozulması | son release | 1 saat | Natro overlay artifact + checksum + rollback |

İlk ücretli müşteri öncesinde Render PITR planı ve aylık restore tatbikatı başarıyla doğrulanmalıdır.

## 3. Kurulum sırası

### A. Secret üretimi

Yerel güvenli bilgisayarda:

```bash
python alo186/sureklilik-api/scripts/generate_production_secrets.py \
  --format shell \
  --output ~/.config/alo186/production-secrets.env
```

Dosya izinleri 0600 olmalıdır. Değerler issue, PR, e-posta veya CI loguna yazılmaz.

### B. Render Blueprint

1. Render hesabında GitHub repo bağlantısı kurulur.
2. Blueprint olarak kökteki `render.yaml` seçilir.
3. Frankfurt bölgesi ve PostgreSQL planı doğrulanır.
4. `sync:false` değerler panelden girilir:
   - `ALO186_DATA_ENCRYPTION_KEY`
   - `ALO186_SMTP_USERNAME`
   - `ALO186_SMTP_PASSWORD`
   - `ALO186_SENTRY_DSN`
   - `RESTIC_REPOSITORY`
   - `RESTIC_PASSWORD`
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`
5. İlk deploy öncesi `render_predeploy.sh` migration logu kontrol edilir.
6. `/health/live` ve `/health/ready` HTTP 200 vermeden custom domain trafiği açılmaz.

### C. PostgreSQL

- Public IP allow list boş tutulur.
- Uygulama private connection string kullanır.
- Production'da `ALO186_AUTO_CREATE_SCHEMA=false` zorunludur.
- Şema yalnız Alembic pre-deploy ile değişir.
- PITR etkinliği ve saklama süresi provider panelinde doğrulanır.

### D. Postmark

1. `noreply@alo186.com` sender/domain doğrulaması başlatılır.
2. Postmark panelindeki DKIM ve Return-Path kayıtları Cloudflare Terraform veya Natro DNS ile girilir.
3. Aynı alan adı için ikinci SPF TXT kaydı oluşturulmaz; mevcut SPF birleştirilir.
4. DMARC ilk aşamada `p=none`, raporlar sağlıklıysa `quarantine` ve sonra `reject` seviyesine yükseltilir.
5. SMTP test e-postası gönderilir; doğrulama, parola sıfırlama ve kuruluş daveti şablonları test edilir.

### E. DNS ve TLS

1. Render'a `api.alo186.com` custom domain eklenir.
2. `api` CNAME Render hostname'e DNS-only biçimde verilir.
3. Render sertifika durumu verified olur.
4. Cloudflare kullanılıyorsa proxy kontrollü olarak etkinleştirilir.
5. Kök web hostu ile `www` canonical yönlendirmesi ayrı smoke testten geçer.

### F. R2 / Restic

1. Cloudflare R2 bucket oluşturulur.
2. Bucket ile sınırlı access key üretilir.
3. `RESTIC_REPOSITORY` S3/R2 URI olarak girilir.
4. Günlük cron ilk yedeği alır.
5. `restic snapshots`, checksum ve `pg_restore --list` doğrulanır.
6. Aylık GitHub restore drill yalnız R2 secretları girildikten sonra etkinleştirilir.

### G. Sentry ve Grafana

- Sentry project oluşturulur; DSN Render secret olarak girilir.
- PII gönderimi kapalı kalır.
- Grafana Cloud Prometheus remote-write ve Loki log-stream bilgileri girilir.
- `alerts.yml` pilot trafik eşiklerine göre uyarlanır.
- Synthetic monitor production URL'ler yayınlandıktan sonra etkinleştirilir.

## 4. Production preflight

Render veya güvenli CI ortamında tüm production env değerleri yüklüyken:

```bash
python alo186/sureklilik-api/scripts/production_preflight.py
```

DNS/TLS/API dahil:

```bash
python alo186/sureklilik-api/scripts/production_preflight.py \
  --network \
  --api-base https://api.alo186.com \
  --output production-preflight.json
```

Kritik failure sıfır olmadan canlı müşteri verisi alınmaz.

## 5. Go-live kontrol listesi

- [ ] Blueprint ve infra CI yeşil
- [ ] PostgreSQL migration head doğru
- [ ] API live/ready 200
- [ ] Sentry test event ulaştı
- [ ] SMTP doğrulama e-postası ulaştı
- [ ] Davet e-postası ulaştı ve tek kullanımlı token çalıştı
- [ ] CORS yalnız www origin
- [ ] TrustedHost yalnız api hostu
- [ ] Rate limit ve hesap kilidi testi geçti
- [ ] R2 yedek snapshot oluştu
- [ ] İzole restore drill geçti
- [ ] Grafana metrics/log akışı görüldü
- [ ] TLS süresi 21 günden uzun
- [ ] Synthetic monitor yeşil
- [ ] KVKK export/silme akışı test edildi
- [ ] Statik site yeni API base URL ile bağlandı

## 6. Olay runbookları

### API erişilemiyor

1. Render service events ve deploy loglarını kontrol edin.
2. `/health/live` başarısızsa process/image; `/health/ready` başarısızsa DB/migration odaklı ilerleyin.
3. Son başarılı deploya rollback yapın.
4. DNS/TLS ve Cloudflare proxy durumunu kontrol edin.
5. 30 dakika içinde düzelmezse Caddy/VPS fallback planını başlatın.

### API 5xx

1. Sentry son release hata kümelerini inceleyin.
2. Request ID ile Render/Loki logunu eşleştirin.
3. DB connection, migration revision ve outbox worker durumunu kontrol edin.
4. Veri bütünlüğü etkisi varsa yazma işlemlerini bakım moduna alın.
5. Fix yerine risk yüksekse rollback yapın.

### Yüksek gecikme

1. En yavaş route ve DB sorgularını ayırın.
2. PostgreSQL CPU/connection/storage metriğini kontrol edin.
3. Worker ve API aynı kaynak limitine takılıyorsa worker ölçeğini ayırın.
4. Birden fazla API replica yalnız Redis tabanlı limiter/idempotency tamamlandıktan sonra açılır.

### Sık yeniden başlama

1. OOM, health check timeout ve migration loop arayın.
2. `ALO186_RUN_MIGRATIONS=false` olduğunu; migration'ın yalnız pre-deployda çalıştığını doğrulayın.
3. Secret/config validation hatalarını inceleyin.

### TLS yenileme

1. Render custom domain durumunu kontrol edin.
2. DNS CNAME hedefi ve proxy durumunu doğrulayın.
3. Cloudflare proxy varsa geçici DNS-only testini bakım penceresinde yapın.
4. Caddy fallback'te ACME rate limit ve data volume kalıcılığını kontrol edin.

### E-posta gönderilmiyor

1. Outbox pending/retry/failed sayılarını kontrol edin.
2. Postmark SMTP credential ve server activity loglarını inceleyin.
3. DKIM/Return-Path/DMARC durumunu doğrulayın.
4. Worker tekil claim/idempotency tamamlanana kadar birden fazla email worker replica açmayın.

### Yedek başarısız

1. R2 credential, bucket scope ve repository URI'yi kontrol edin.
2. `restic check` ve son başarılı snapshot zamanını inceleyin.
3. Render PITR'nin etkin olduğunu doğrulayın.
4. 24 saat içinde yeni doğrulanmış yedek alınamıyorsa üretim yazma riskini yönetime bildirin.

## 7. Rollback

### Uygulama

- Render Dashboard → Deploys → son başarılı image/deploy → rollback.
- Migration geriye uyumlu değilse yalnız uygulama rollback yeterli değildir; migration runbooku uygulanır.
- Destructive downgrade production'da otomatik çalıştırılmaz.

### Veritabanı

1. Mevcut DB snapshot alınır.
2. PITR ile ayrı instance oluşturulur.
3. Tutarlılık ve Alembic revision doğrulanır.
4. Trafik kontrollü olarak yeni DB'ye çevrilir.
5. Restic restore son çaredir ve checksum + izole testten sonra uygulanır.

### DNS

- TTL önceden düşürülür.
- API CNAME önceki doğrulanmış origin'e geri alınır.
- Proxy/TLS durumu health check geçmeden değişmez.

## 8. Secret rotasyonu

| Secret | Rotasyon |
|---|---|
| SMTP credential | 90 gün veya olay sonrası |
| R2 access key | 90 gün veya olay sonrası |
| Metrics token | 90 gün |
| Sentry DSN | olay/yanlış paylaşım sonrası |
| Token secret | planlı bakım; bütün oturumları geçersiz kılar |
| Fernet veri anahtarı | key rotation migration olmadan doğrudan değişmez |
| Restic password | repository key rotation prosedürüyle |

Token ve veri şifreleme anahtarları aynı değer olamaz. Eski Fernet anahtarındaki veriler yeniden şifrelenmeden anahtar değiştirilmez.

## 9. Operasyon sahipliği

Tek kişi yönetiminde haftalık rutin:

- Pazartesi: backup ve restore durumu
- Salı: Sentry hata kümeleri
- Çarşamba: Grafana kapasite/gecikme
- Perşembe: SMTP/outbox ve bounce
- Cuma: bağımlılık/secret/cost gözden geçirme

Aylık:

- restore drill
- TLS/DNS kontrolü
- kullanıcı/tenant/plan kullanım raporu
- KVKK silme ve retention raporu
- maliyet ve marj takibi
