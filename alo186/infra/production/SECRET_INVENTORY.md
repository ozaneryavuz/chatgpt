# ALO186 production secret inventory

Hiçbir gerçek secret değeri bu repository'de tutulmaz. Aşağıdaki tablo yalnız sahiplik, saklama ve rotasyon politikasını tanımlar.

| Secret | Kullanım | Saklama | Rotasyon / etki |
|---|---|---|---|
| `ALO186_TOKEN_SECRET` | Oturum ve tek kullanımlık token imzası | Render generated secret / secret manager | 90–180 gün veya olay sonrası; bütün aktif oturumları geçersiz kılar |
| `ALO186_DATA_ENCRYPTION_KEY` | MFA sırrı, recovery kodu ve outbox payload şifreleme | Render secret | Key migration olmadan değiştirilmez; eski/yeni anahtar destekli re-encryption gerekir |
| `ALO186_METRICS_TOKEN` | `/metrics` bearer erişimi | Render generated secret + Grafana Alloy secret | 90 gün; Alloy ve Render birlikte güncellenir |
| `ALO186_SMTP_USERNAME` | Postmark SMTP kullanıcı/token | Render secret | 90 gün veya Postmark olayı sonrası |
| `ALO186_SMTP_PASSWORD` | Postmark SMTP parola/token | Render secret | 90 gün veya Postmark olayı sonrası |
| `ALO186_SENTRY_DSN` | Sentry proje endpointi | Render secret | Yanlış paylaşım/proje değişimi sonrası |
| `RESTIC_REPOSITORY` | R2 üzerindeki restic repository URI | Render backup cron secret | Bucket/repo taşınmasında |
| `RESTIC_PASSWORD` | Restic repository şifreleme | Render backup cron secret + offline escrow | Düzenli değişim yerine key management prosedürü; kaybı restore'u imkânsız kılar |
| `AWS_ACCESS_KEY_ID` | R2 bucket erişimi | Render backup cron secret | 90 gün veya olay sonrası |
| `AWS_SECRET_ACCESS_KEY` | R2 bucket erişimi | Render backup cron secret | 90 gün veya olay sonrası |
| `CLOUDFLARE_API_TOKEN` | DNS Terraform | GitHub `alo186-production` environment secret veya yerel secure store | 90 gün; yalnız zone DNS read/write |
| `TF_STATE_CREDENTIALS` | Remote Terraform state | CI/remote backend secret | Backend politikasına göre |
| `GRAFANA_CLOUD_API_KEY` | Metrics/log remote write | Grafana Alloy secret | 90 gün veya olay sonrası |
| `RENDER_API_KEY` | Blueprint/API otomasyonu | GitHub environment secret | 90 gün; yalnız gerekli workspace yetkisi |

## Ayrım kuralları

- Token secret, Fernet key, metrics token ve Restic password aynı değer olamaz.
- Dev/test/prod ortamları aynı secretı paylaşamaz.
- Kişisel Cloudflare Global API Key kullanılmaz; zone ile sınırlı API token kullanılır.
- R2 access key yalnız tek backup bucketına erişir; account-wide yönetim yetkisi taşımaz.
- Deploy ve provider tokenları PR workflow'larına açılmaz; protected production environment gerektirir.
- Secretlar artifact, Docker layer, Terraform state output, log veya Sentry event içine yazılmaz.

## Üretim oluşturma

```bash
python alo186/sureklilik-api/scripts/generate_production_secrets.py \
  --format shell \
  --output ~/.config/alo186/production-secrets.env
```

Dosya 0600 izinle oluşturulur. Render paneline aktarıldıktan sonra yerel escrow politikası uygulanır.

## Rotasyon kaydı

Rotasyon sırasında issue/PR yalnız şu metadata'yı taşır:

- secret adı,
- rotasyon tarihi,
- sorumlu,
- bağlı servisler,
- doğrulama sonucu,
- önceki değerin iptal zamanı.

Secret değerin kendisi hiçbir zaman GitHub'a yazılmaz.
