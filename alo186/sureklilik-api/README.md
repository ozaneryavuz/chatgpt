# ALO186 Elektrik Sürekliliği API — SaaS Temeli v0.2

Local-first süreklilik panelini gerçek çok kullanıcılı SaaS mimarisine taşıyan FastAPI/PostgreSQL temelidir.

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
- Docker Compose

## Yerel çalıştırma

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export ALO186_TOKEN_SECRET='en-az-32-karakter-rastgele-gizli-deger'
uvicorn app.main:app --reload
```

Swagger:

```text
http://localhost:8000/docs
```

## Docker/PostgreSQL

```bash
docker compose up --build
```

## Test

```bash
pytest -q
```

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

## Üretim öncesi kalan işler

- yönetilen kimlik sağlayıcı veya e-posta doğrulama
- parola sıfırlama ve MFA
- Alembic migration
- rate limiting ve saldırı koruması
- secret manager
- e-posta/web-push bildirimleri
- offline senkronizasyon ve conflict handling
- abonelik/faturalama
- yedekleme, veri saklama ve KVKK süreçleri
- OpenTelemetry/Sentry gözlemlenebilirliği

Bu sürüm gerçek SaaS'ın veri ve yetkilendirme temelidir; tek başına kamuya açık üretim servisi olarak yayınlanmamalıdır.
