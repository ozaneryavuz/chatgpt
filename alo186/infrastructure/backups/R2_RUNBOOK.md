# ALO186 PostgreSQL Yedekleme ve Felaket Kurtarma

## 3-2-1 mini mimarisi

1. **Render PostgreSQL PITR** — hızlı operasyonel geri dönüş.
2. **Cloudflare R2 Restic deposu** — günlük, client-side şifreli mantıksal yedek.
3. **R2 aylık vault bucket** — ayın ilk günü Restic'ten ayrı anahtarla şifrelenmiş dump + checksum; retention lock ile ayrı hata alanı.

Bu katmanlardan hiçbiri diğerinin yerine geçmez.

## RPO / RTO hedefi

| Senaryo | RPO | RTO hedefi |
|---|---:|---:|
| Yanlış kayıt/silme | PITR penceresi içinde dakikalar | 60 dakika |
| Render DB kaybı | Son günlük R2 yedeği, en çok 24 saat | 2 saat |
| R2 Restic repository bozulması | Aylık şifreli vault | 31 gün | 4 saat |
| Tam sağlayıcı kaybı | R2 + portable Compose/Caddy | 24 saat | 4–8 saat |

## R2 bucket tasarımı

### `alo186-db-restic`

- Restic tarafından yönetilir.
- **Cloudflare lifecycle delete ve bucket lock uygulanmaz.** Restic prune kendi retention politikasını yönetir; dışarıdan obje silme repository'yi bozabilir.
- Yalnız backup/restore access key erişebilir.

### `alo186-db-monthly-vault`

- Ayın ilk günü OpenSSL AES-256-CBC/PBKDF2 ile istemci tarafında şifrelenmiş dump ve şifreli dosyanın SHA-256 checksum'unu alır.
- Restic parolasından ayrı `ALO186_VAULT_ENCRYPTION_KEY` kullanır.
- Cloudflare Bucket Lock ile en az 180 gün silme koruması önerilir.
- Günlük Restic token'ından ayrı access token tercih edilir.
- Uygulama servisi bu bucket'a erişmez.

## R2 secret'ları

```text
ALO186_R2_ENDPOINT=https://<account-id>.r2.cloudflarestorage.com
ALO186_R2_RESTIC_BUCKET=alo186-db-restic
ALO186_R2_VAULT_BUCKET=alo186-db-monthly-vault
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
RESTIC_PASSWORD=...
ALO186_VAULT_ENCRYPTION_KEY=...
ALO186_BACKUP_HEARTBEAT_URL=...
```

Restic ve vault anahtarları aynı olmamalı; ikisi de çevrimdışı kurtarma kasasında sürümlü tutulmalıdır.

## Günlük akış

`alo186-r2-backup-cron`:

1. `pg_dump --format=custom`
2. SHA-256
3. `pg_restore --list` okunabilirlik kontrolü
4. Restic şifreli upload
5. 14 günlük / 8 haftalık / 12 aylık / 3 yıllık retention
6. `restic check`
7. Pazar günleri data subset doğrulaması
8. Ayın ilk günü ayrı anahtarla şifrelenmiş vault kopyası
9. Başarı/fail heartbeat

## Restore tatbikatı

En az üç ayda bir, üretimden ayrı boş PostgreSQL üzerinde:

```bash
export ALO186_R2_ENDPOINT='...'
export ALO186_R2_RESTIC_BUCKET='alo186-db-restic'
export AWS_ACCESS_KEY_ID='...'
export AWS_SECRET_ACCESS_KEY='...'
export RESTIC_PASSWORD='...'
export ALO186_RESTORE_DATABASE_URL='postgresql://.../alo186_restore_drill'
export ALO186_RESTORE_CONFIRM='YES-RESTORE-ALO186'

./alo186/sureklilik-api/infra/backup/restore_verify.sh latest
```

Tatbikatta:

- checksum,
- `pg_restore --list`,
- tam restore,
- Alembic current,
- temel tenant/incident sorguları,
- süre ve hata kaydı

dokümante edilir.

## Aylık vault kurtarma

Vault yalnız Restic deposu birlikte kullanılamaz hale geldiğinde son savunma hattıdır.

```bash
openssl enc -d -aes-256-cbc -pbkdf2 -iter 200000 \
  -in alo186-YYYYMMDDTHHMMSSZ.dump.enc \
  -out alo186-restored.dump \
  -pass env:ALO186_VAULT_ENCRYPTION_KEY

pg_restore --list alo186-restored.dump
```

Ardından yalnız izole bir PostgreSQL veritabanına restore edilir. Şifre çözülmüş dump işlem bitince güvenli biçimde silinir.

## Kurtarma karar ağacı

```text
Tek kayıt/tablo hatası
→ Render PITR ile izole recovery DB
→ doğrula
→ connection string geçişi

Ana DB tamamen kullanılamıyor
→ yeni PostgreSQL
→ en güncel R2 Restic restore
→ Alembic current/check
→ smoke test
→ DNS/API trafiğini aç

Restic repo okunamıyor
→ monthly vault şifreli dump
→ checksum + decrypt
→ yeni DB restore
→ repository yeniden oluştur
```

## Zorunlu alarm

Son başarılı backup heartbeat 26 saati geçerse critical alarm oluşmalıdır. Yedek üretmek tek başına yeterli değildir; restore tatbikatı yapılmamış sistem production-ready sayılmaz.
