# ALO186 Elektrik Sürekliliği API — Üretim Sertleştirme v0.3

Local-first süreklilik panelini çok kullanıcılı, tenant izolasyonlu ve üretim öncesi güvenlik katmanları tamamlanmış FastAPI/PostgreSQL SaaS temeline taşır.

## Sağlanan yetenekler

### Kimlik ve güvenlik

- `scrypt` parola türetme
- veri tabanında izlenen, iptal edilebilir süreli bearer oturumları
- logout, bütün oturumları kapatma ve cihaz/oturum listesi
- e-posta doğrulama
- parola sıfırlama
- başarısız giriş sayacı ve geçici hesap kilidi
- TOTP MFA
- tek kullanımlık MFA kurtarma kodları
- Fernet ile MFA ve outbox payload şifreleme
- IP tabanlı sliding-window global ve auth rate limiting
- istek gövdesi boyut sınırı
- TrustedHost, request ID ve güvenlik başlıkları
- production config fail-fast kontrolleri
- Docker/Kubernetes `_FILE` secret desteği

### Tenant ve ürün

- kuruluş/tenant izolasyonu
- admin, technician ve viewer rolleri
- çoklu kuruluş üyeliği
- lokasyonlar
- P1/P2/P3 kritik yükler
- jeneratör, UPS ve yedek güç varlıkları
- zaman damgalı varlık testleri
- kesinti olayı ve otomatik görev üretimi
- zorunlu görevler tamamlanmadan olay kapanış engeli
- kuruluş bazlı audit log
- pilot/site/hotel/business/enterprise plan limitleri
- kullanım ve kalan limit endpointi

### E-posta ve operasyon

- şifreli transactional email outbox
- console ve SMTP backend
- retry/backoff kullanan e-posta worker
- olay başlangıç/kapanış e-posta bildirimleri
- liveness ve database readiness endpointleri
- JSON structured logging
- request count, duration ve in-flight Prometheus text metrikleri
- Alembic migration sistemi
- checksum ve retention destekli PostgreSQL backup/restore
- retention worker
- non-root, read-only üretim container örneği

### KVKK ve veri yaşam döngüsü

- kullanıcı veri dışa aktarımı
- kuruluş veri dışa aktarımı
- tek yönetici korumalı hesap silme talebi
- kuruluş silme talebi
- bekleme süreli silme
- süresi dolmuş session, token, outbox ve audit retention temizliği
- tarihsel olay/test/audit kayıtlarında kullanıcı referansını anonimleştirme

## Yerel geliştirme

```bash
cd alo186/sureklilik-api
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
export ALO186_ENV=development
export ALO186_TOKEN_SECRET='en-az-32-karakter-rastgele-gizli-deger'
export ALO186_DATA_ENCRYPTION_KEY='AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA='
export ALO186_AUTO_CREATE_SCHEMA=true
uvicorn app.main:app --reload
```

Swagger:

```text
http://localhost:8000/docs
```

## Migration

Yeni veritabanı veya v0.2 şeması:

```bash
export PYTHONPATH=.
alembic upgrade head
alembic current
alembic check
```

Production ortamında:

```text
ALO186_AUTO_CREATE_SCHEMA=false
ALO186_RUN_MIGRATIONS=true
```

kullanılır. Uygulama başlangıç komutu `alembic upgrade head` sonrasında Uvicorn'u başlatır.

## Docker geliştirme

```bash
cp .env.example .env
# .env içindeki secret ve SMTP alanlarını düzenleyin
docker compose up --build
```

## Production Compose

Secret dosyalarını `secrets/README.md` talimatıyla oluşturun ve ardından:

```bash
export ALO186_SMTP_HOST=smtp.example.com
export ALO186_SMTP_USERNAME=noreply@alo186.com
export ALO186_SMTP_FROM_EMAIL=noreply@alo186.com
docker compose -f docker-compose.production.yml up -d --build
```

API yalnız `127.0.0.1:8000` üzerinde yayınlanır. Dış erişim TLS sonlandıran reverse proxy veya yönetilen platform üzerinden verilmelidir.

Production compose şu servisleri çalıştırır:

- PostgreSQL
- API
- e-posta outbox worker
- günlük retention worker
- günlük checksum'lı PostgreSQL backup worker

## Background worker

```bash
python -m app.worker email-once --limit 50
python -m app.worker email-loop --interval 15
python -m app.worker retention-once
```

## Yedekleme ve geri yükleme

```bash
export ALO186_DATABASE_URL='postgresql+psycopg://...'
export ALO186_BACKUP_DIR=/secure/backups
sh scripts/backup_postgres.sh
```

Geri yükleme:

```bash
export ALO186_RESTORE_CONFIRM=YES-RESTORE-ALO186
sh scripts/restore_postgres.sh /secure/backups/alo186-YYYYMMDDTHHMMSSZ.dump
```

Geri yükleme mutlaka ayrı bir ortamda periyodik olarak test edilmelidir. Yalnız yedek dosyası üretmek yeterli değildir.

## Health ve metrics

```text
GET /health/live
GET /health/ready
GET /metrics
```

`ALO186_METRICS_TOKEN` tanımlıysa metrics endpointi `X-Metrics-Token` başlığı gerektirir.

## Tenant başlıkları

Kuruluş kapsamındaki bütün isteklerde:

```http
Authorization: Bearer <token>
X-Organization-ID: <organization-uuid>
```

başlıkları zorunludur. API, oturumu ve kuruluş üyeliğini her istekte doğrular.

## Önemli auth endpointleri

```text
POST /api/v1/auth/register
POST /api/v1/auth/login
POST /api/v1/auth/logout
POST /api/v1/auth/logout-all
GET  /api/v1/auth/sessions
DELETE /api/v1/auth/sessions/{session_id}
POST /api/v1/auth/email-verification/request
POST /api/v1/auth/email-verification/confirm
POST /api/v1/auth/password-reset/request
POST /api/v1/auth/password-reset/confirm
POST /api/v1/auth/mfa/setup
POST /api/v1/auth/mfa/enable
POST /api/v1/auth/mfa/recovery-codes
POST /api/v1/auth/mfa/disable
```

## Plan limitleri

| Plan | Lokasyon | Üye | Kritik yük | Varlık |
|---|---:|---:|---:|---:|
| pilot | 3 | 3 | 25 | 10 |
| site | 10 | 25 | 100 | 30 |
| hotel | 10 | 50 | 250 | 100 |
| business | 20 | 50 | 300 | 120 |
| enterprise | sınırsız | sınırsız | sınırsız | sınırsız |

Kullanım:

```text
GET /api/v1/billing/usage
```

Bu sürüm limitleri uygular; gerçek ödeme sağlayıcısı ve webhook entegrasyonu v0.4+ kapsamındadır.

## KVKK endpointleri

```text
GET  /api/v1/privacy/me/export
POST /api/v1/privacy/me/delete-request
GET  /api/v1/privacy/organization/export
POST /api/v1/privacy/organization/delete-request
```

Hesap silme, kullanıcının tek yönetici olduğu etkin kuruluş varsa engellenir. Yönetici devri veya kuruluş silme talebi gerekir.

## Rol matrisi

| İşlem | Admin | Teknik ekip | Görüntüleyici |
|---|---:|---:|---:|
| Verileri görme | ✓ | ✓ | ✓ |
| Lokasyon/yük/varlık ekleme | ✓ | ✓ | — |
| Test kaydı | ✓ | ✓ | — |
| Olay/görev yönetimi | ✓ | ✓ | — |
| Üye ve rol yönetimi | ✓ | — | — |
| Audit log / kuruluş export | ✓ | — | — |

## Test

```bash
pytest -q
python -m compileall -q app
```

CI ayrıca:

- Alembic boş DB migration smoke testi,
- `alembic check`,
- shell script syntax,
- production config reddetme testleri,
- auth/MFA/reset/session testleri,
- tenant/rol/incident regresyon testleri,
- plan ve KVKK testleri

çalıştırır.

## Üretime çıkış kontrol listesi

- [ ] PostgreSQL yönetilen veya güvenli yedekli ortamda
- [ ] Secret dosyaları/secret manager hazırlanmış
- [ ] TLS reverse proxy ve HSTS aktif
- [ ] SMTP DKIM/SPF/DMARC doğrulanmış
- [ ] `EMAIL_VERIFICATION_REQUIRED=true`
- [ ] Alembic head uygulanmış
- [ ] Backup ve restore tatbikatı yapılmış
- [ ] Metrics yalnız iç ağ veya token ile erişiliyor
- [ ] Loglarda açık e-posta, parola, token ve tesisat bilgisi yok
- [ ] KVKK aydınlatma, saklama ve silme prosedürleri yayımlanmış
- [ ] Pilot tenant verisi üretim verisinden ayrılmış
- [ ] İlk yönetici MFA'yı etkinleştirmiş

## Sonraki v0.4 işleri

- gerçek ödeme sağlayıcısı/webhook
- davet tabanlı kullanıcı onboarding
- web-push/VAPID
- Redis/managed rate limiter ve distributed worker lock
- tam OpenTelemetry collector ve haricî hata izleme
- offline sync ve conflict resolution
- merkezi web panelinin API'ye bağlanması
