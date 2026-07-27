# ALO186 Elektrik Sürekliliği API — Üretim Sertleştirme v0.3a

Local-first süreklilik panelini çok kullanıcılı SaaS mimarisine taşıyan FastAPI/PostgreSQL temelidir. v0.3a; production yapılandırma doğrulaması, secret dosyaları, request ID, güvenlik başlıkları, gövde/rate limit, readiness ve temel Prometheus metriklerini ekler.

## Sağlanan yetenekler

- güvenli parola türetme (`scrypt`)
- HMAC imzalı süreli bearer oturumu
- kuruluş/tenant izolasyonu
- yönetici, teknik ekip ve görüntüleyici rolleri
- çoklu kuruluş üyeliği
- lokasyonlar
- P1/P2/P3 kritik yükler
- jeneratör, UPS ve diğer yedek varlıklar
- zaman damgalı varlık testleri
- kesinti olayı başlatma
- P1 kritik yüklere göre otomatik görev üretimi
- zorunlu görevler tamamlanmadan olay kapatmayı engelleme
- kuruluş bazlı audit log
- SQLite geliştirme/test ve PostgreSQL üretim desteği
- production ortamında zayıf secret, SQLite, wildcard CORS/host ve otomatik şema oluşturmayı reddetme
- `*_FILE` ile Docker/Kubernetes secret desteği
- Trusted Host, request ID ve güvenlik başlıkları
- IP tabanlı in-memory sliding-window rate limit
- azami istek gövdesi boyutu
- `/live`, `/ready` ve Prometheus text `/metrics`
- JSON biçimli request logları
- non-root Docker konteyneri ve healthcheck

## Yerel çalıştırma

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export ALO186_ENV=development
export ALO186_TOKEN_SECRET='en-az-32-karakter-rastgele-gizli-deger'
uvicorn app.production:app --reload
```

Swagger:

```text
http://localhost:8000/docs
```

Operasyon endpointleri:

```text
GET /live
GET /ready
GET /metrics
```

## Docker/PostgreSQL geliştirme

```bash
docker compose up --build
```

Konteyner `app.production:app` entrypoint'ini, non-root kullanıcıyı ve `/live` healthcheck'ini kullanır.

## Production yapılandırması

Production başlangıcında aşağıdaki koşullar zorunludur:

- `ALO186_ENV=production`
- PostgreSQL `ALO186_DATABASE_URL` veya `ALO186_DATABASE_URL_FILE`
- en az 32 karakter rastgele `ALO186_TOKEN_SECRET` veya `ALO186_TOKEN_SECRET_FILE`
- wildcard içermeyen `ALO186_ALLOWED_HOSTS`
- wildcard içermeyen `ALO186_ALLOWED_ORIGINS`
- `ALO186_AUTO_CREATE_SCHEMA=false`
- migration'ın uygulama başlamadan önce çalıştırılması

Örnek:

```bash
export ALO186_ENV=production
export ALO186_DATABASE_URL_FILE=/run/secrets/database_url
export ALO186_TOKEN_SECRET_FILE=/run/secrets/token_secret
export ALO186_ALLOWED_HOSTS=api.alo186.com
export ALO186_ALLOWED_ORIGINS=https://www.alo186.com
export ALO186_AUTO_CREATE_SCHEMA=false
uvicorn app.production:app --host 0.0.0.0 --port 8000 --workers 1 --no-server-header
```

`ALO186_TRUST_PROXY_HEADERS=true` yalnız API güvenilir bir reverse proxy arkasındaysa etkinleştirilmelidir. Aksi hâlde istemci tarafından gönderilen `X-Forwarded-For` kullanılmaz.

## API koruma değişkenleri

| Değişken | Varsayılan | Açıklama |
|---|---:|---|
| `ALO186_MAX_REQUEST_BODY_BYTES` | 1.048.576 | Azami istek gövdesi |
| `ALO186_API_RATE_LIMIT_PER_MINUTE` | 120 | IP başına genel API limiti |
| `ALO186_AUTH_RATE_LIMIT_PER_MINUTE` | 12 | Register/login için daha sıkı limit |
| `ALO186_METRICS_ENABLED` | true | Prometheus text endpointi |
| `ALO186_ALLOWED_HOSTS` | yerel hostlar | TrustedHost listesi |
| `ALO186_LOG_LEVEL` | INFO | Structured request log seviyesi |

Mevcut rate limit tek process belleğindedir. Çok worker veya çok pod dağıtımında Redis gibi paylaşımlı limiter v0.4 gereksinimidir; o zamana kadar üretim konteyneri tek worker kullanır.

## Test

```bash
pytest -q
```

Test kapsamı artık şunları da içerir:

- production secret ve config doğrulaması
- secret dosyası okuma
- request ID ve güvenlik başlıkları
- TrustedHost reddi
- istek gövdesi boyut sınırı
- deterministic sliding-window rate limiter
- readiness DB kontrolü
- metrics çıktısı

## Tenant güvenliği

Kuruluş kapsamındaki bütün isteklerde:

```http
Authorization: Bearer <token>
X-Organization-ID: <organization-uuid>
```

başlıkları zorunludur. API, kullanıcının ilgili kuruluş üyeliğini her istekte doğrular.

## Rol matrisi

| İşlem | Admin | Teknik ekip | Görüntüleyici |
|---|---:|---:|---:|
| Verileri görme | ✓ | ✓ | ✓ |
| Lokasyon/yük/varlık ekleme | ✓ | ✓ | — |
| Test kaydı | ✓ | ✓ | — |
| Olay/görev yönetimi | ✓ | ✓ | — |
| Üye ve rol yönetimi | ✓ | — | — |
| Audit log | ✓ | — | — |

## v0.3 içinde kalan işler

- Alembic baseline ve migration smoke testi
- e-posta doğrulama ve parola sıfırlama
- oturum `jti`, logout ve bütün oturumları iptal etme
- başarısız giriş kilidi
- TOTP MFA ve kurtarma kodları
- SMTP/outbox worker
- plan ve tenant kullanım limitleri
- kullanıcı/veri dışa aktarma ve silme talepleri
- backup/restore ve retention worker
- merkezi Redis rate limiter
- Sentry/OpenTelemetry genişlemesi

Bu sürüm güvenli production entrypoint sağlar; ancak yukarıdaki kimlik, migration ve veri yaşam döngüsü işleri tamamlanmadan kamuya açık ücretli SaaS olarak kabul edilmemelidir.
