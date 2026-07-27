# ALO186 Provider Activation ve Go-Live Gates

Bu doküman, GitHub'daki hazır üretim altyapısını gerçek sağlayıcı hesaplarında aktive ederken uygulanacak sıralı kontrol planıdır. Secret değerleri GitHub issue, PR, commit, e-posta veya ekran görüntüsünde tutulmaz.

## Mimari

```text
www.alo186.com
  └─ mevcut statik hosting

api.alo186.com
  └─ Render Frankfurt
      ├─ FastAPI + Knowledge Graph API
      ├─ e-posta worker
      ├─ retention + günlük graph sync cron
      ├─ R2 backup cron
      └─ managed PostgreSQL 16

Dış servisler
  ├─ Postmark SMTP
  ├─ Cloudflare DNS/WAF
  ├─ Cloudflare R2 + Restic
  ├─ Sentry
  └─ Grafana Cloud / Synthetic Monitoring
```

## Gate 0 — GitHub ve kod kalitesi

Tamamlanma kanıtı:

- `main` branch koruması ve checksPass deploy
- API, Knowledge Graph, migration, PostgreSQL, infra ve statik araç CI yeşil
- açık P1 güvenlik inceleme yorumu yok
- destructive migration yok

Komut:

```bash
cd alo186/sureklilik-api
pytest -q
alembic upgrade head
alembic check
```

## Gate 1 — Secret üretimi ve saklama

Yerel güvenli cihazda:

```bash
python alo186/sureklilik-api/scripts/generate_production_secrets.py \
  --format shell \
  --output ~/.config/alo186/production-secrets.env
chmod 600 ~/.config/alo186/production-secrets.env
```

Render secret alanına girilecekler:

- `ALO186_DATA_ENCRYPTION_KEY`
- `ALO186_SMTP_USERNAME`
- `ALO186_SMTP_PASSWORD`
- `ALO186_SENTRY_DSN`
- `RESTIC_REPOSITORY`
- `RESTIC_PASSWORD`
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`

Render tarafından üretilecekler:

- `ALO186_TOKEN_SECRET`
- `ALO186_METRICS_TOKEN`

Tamamlanma kanıtı:

- production preflight hiçbir secret değerini loglamadan geçer
- token ve Fernet anahtarı farklıdır
- metrics endpoint doğru token olmadan 401/403 döner

## Gate 2 — Render API hosting ve PostgreSQL

1. Render Blueprint olarak repo kökündeki `render.yaml` seçilir.
2. Frankfurt bölgesi doğrulanır.
3. `alo186-postgres` managed PostgreSQL 16 oluşturulur.
4. Web, worker ve cron servisleri private DB URL kullanır.
5. Pre-deploy:
   - Alembic `head`
   - `alembic check`
   - DB readiness
   - public Knowledge Graph seed
   işlemlerini tamamlar.

Knowledge Graph üretim değişkenleri:

```text
ALO186_KG_SEED_PUBLIC=true
ALO186_KG_SEED_STRICT=false
ALO186_KG_SEED_TIMEOUT=30
```

Tamamlanma kanıtı:

```bash
curl -fsS https://api.alo186.com/health/live
curl -fsS https://api.alo186.com/health/ready
curl -fsS https://api.alo186.com/api/v1/kg/public/health
```

Beklenen minimumlar:

- live/ready HTTP 200
- graph entity > 100
- graph assertion > 100
- graph health score >= 85
- migration revision `head`

## Gate 3 — SMTP ve e-posta itibarı

Postmark üzerinde:

1. `alo186.com` sending domain eklenir.
2. DKIM ve Return-Path kayıtları DNS'e girilir.
3. Mevcut SPF varsa yeni ayrı SPF kaydı açılmaz; tek kayıt birleştirilir.
4. DMARC ilk aşamada raporlama için `p=none` kullanır.
5. Bounce ve spam complaint webhook'ları sonraki worker fazına hazırlanır.

Test senaryoları:

- e-posta doğrulama
- parola sıfırlama
- kuruluş daveti
- olay başlangıç bildirimi
- retry ve başarısız outbox

Tamamlanma kanıtı:

- Postmark activity log `Delivered`
- DKIM `pass`
- SPF `pass`
- DMARC raporu geliyor
- outbox pending/retry/failed sayıları gözlenebiliyor

## Gate 4 — DNS ve TLS

Cloudflare Terraform yolu:

```bash
cd alo186/infra/dns/cloudflare
terraform init
terraform plan
terraform apply
```

Zorunlu kayıtlar:

- `api.alo186.com` → Render custom domain CNAME
- Postmark DKIM
- Postmark Return-Path
- birleşik SPF
- DMARC

Geçiş sırası:

1. `api` kaydı DNS-only oluşturulur.
2. Render sertifikası verified olur.
3. API ready ve synthetic test yeşil olur.
4. Gerekirse Cloudflare proxy kontrollü açılır.
5. www/kök canonical yönlendirmesi ayrı doğrulanır.

Tamamlanma kanıtı:

```bash
dig +short api.alo186.com
curl -I https://api.alo186.com/health/ready
openssl s_client -connect api.alo186.com:443 -servername api.alo186.com </dev/null
```

- sertifika hostname ile eşleşir
- sertifika süresi 21 günden uzundur
- HTTP → HTTPS tek yönlendirme
- HSTS yalnız doğrulama sonrasında açılır

## Gate 5 — Backup storage ve restore tatbikatı

Cloudflare R2:

- özel bucket
- yalnız ilgili bucket'a erişen sınırlı access key
- public access kapalı
- Restic repository password ayrı secret

İlk yedek:

```bash
restic snapshots
restic check
```

Restore tatbikatı:

1. yeni izole PostgreSQL oluşturulur
2. son snapshot ayrı dizine restore edilir
3. checksum doğrulanır
4. `pg_restore --list` kontrol edilir
5. restore DB'de Alembic revision doğrulanır
6. `kg_entities`, `kg_assertions`, tenant, olay ve audit satır sayıları karşılaştırılır
7. public graph seed tekrar çalıştırılır; tenant graph değişmemelidir

Tamamlanma kanıtı:

- son yedek yaşı < 26 saat
- `restic check` başarılı
- aylık restore drill başarılı
- RPO <= 24 saat, RTO <= 4 saat

## Gate 6 — Monitoring ve alert routing

Sentry:

- PII gönderimi kapalı
- release adı commit SHA içerir
- traces sample rate pilotta %5
- test error Sentry'ye ulaşır

Grafana Cloud:

- `/metrics` bearer/token ile scrape veya Alloy remote-write
- Loki JSON logları request ID içerir
- synthetic monitor:
  - `/health/live`
  - `/health/ready`
  - `/api/v1/kg/public/health`
  - statik kritik rotalar
  - TLS expiry

Knowledge Graph alarmları:

- health score < 85
- entity < 100
- stale assertion > 100
- conflict > 0

Tamamlanma kanıtı:

- test alarmı seçilen iletişim kanalına ulaştı
- alarm içinde runbook URL bulunuyor
- request ID ile Sentry, Render ve Loki kayıtları eşleşiyor

## Gate 7 — Knowledge Graph semantik kalite

İlk production seed:

```bash
python -m app.knowledge_seed sync-public --timeout 30 --strict
```

Doğrulanacak ilişkiler:

```text
Marmaris --partOf--> Muğla
Marmaris --servedBy--> ADM Elektrik
Ümraniye --servedBy--> AYEDAŞ
Esenyurt --servedBy--> BEDAŞ
Kablo yere düştü --routesTo--> 112
Elektrik kesintisi --routesTo--> 186
```

API doğrulama:

```bash
curl -fsS 'https://api.alo186.com/api/v1/kg/public/search?q=Marmaris'
curl -fsS 'https://api.alo186.com/api/v1/kg/public/entities/problem:fallen_conductor/jsonld'
curl -fsS 'https://api.alo186.com/api/v1/kg/public/health'
```

Tamamlanma kanıtı:

- scalar ve entity assertion'larında source/confidence/verifiedAt var
- global public graph tenant API ile değiştirilemiyor
- tenant private graph başka kuruluş tarafından okunamıyor
- son başarılı verification eski başarısızlığı health cezasından kaldırıyor
- conflict ve stale metrikleri sıfır veya kabul edilmiş istisna listesinde

## Gate 8 — Pilot açılışı

İlk üretim pilotu:

- 3 otel
- 2 site yönetimi
- 2 küçük işletme

Canlıya açmadan önce:

- KVKK export/silme testi
- son admin koruması
- tenant izolasyonu
- davet tokenı tek kullanımlılık
- rate limit ve hesap kilidi
- SMTP teslimi
- backup ve restore
- graph health
- incident/P1 görev kapanış koruması

başarılı olmalıdır.

## Sağlayıcı bağımsız kaçış planı

Render bölge veya sağlayıcı sorunu halinde:

- Docker image aynı kalır
- Caddy `Caddyfile` ile TLS/reverse proxy sağlanır
- PostgreSQL R2/Restic restore edilir
- DNS TTL düşürülmüş `api` kaydı yeni origin'e çevrilir
- secret isimleri aynı tutulur
- public graph seed restore sonrasında tekrar çalışır

Bu sayede uygulama mimarisi Render'a işlevsel olarak bağımlı, veri ve uygulama taşınabilirliği bakımından kilitli değildir.
