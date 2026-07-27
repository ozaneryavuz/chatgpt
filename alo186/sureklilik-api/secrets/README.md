# Production secret dosyaları

Bu klasörde **gerçek secret dosyaları Git'e eklenmemelidir**. `docker-compose.production.yml` aşağıdaki dosyaları yerel sunucuda bekler:

```text
secrets/postgres_password.txt
secrets/database_url.txt
secrets/token_secret.txt
secrets/data_encryption_key.txt
secrets/smtp_password.txt
secrets/metrics_token.txt
```

Örnek üretim komutları:

```bash
mkdir -p secrets
umask 077
openssl rand -base64 48 | tr -d '\n' > secrets/postgres_password.txt
openssl rand -base64 48 | tr -d '\n' > secrets/token_secret.txt
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode(), end='')" > secrets/data_encryption_key.txt
openssl rand -base64 48 | tr -d '\n' > secrets/metrics_token.txt
printf '%s' 'SMTP_PAROLANIZ' > secrets/smtp_password.txt
```

`database_url.txt`, `postgres_password.txt` içindeki gerçek parola kullanılarak oluşturulmalıdır:

```text
postgresql+psycopg://alo186:GERCEK_PAROLA@db:5432/alo186
```

Dosya izinleri:

```bash
chmod 600 secrets/*.txt
```

Secret rotasyonu sırasında:

- Token secret değişirse bütün oturumlar geçersiz olur.
- Data encryption key değişmeden önce outbox/MFA şifreli verileri yeniden şifrelenmelidir.
- PostgreSQL parolası ile database URL aynı işlem penceresinde değiştirilmelidir.
- Eski secret dosyaları güvenli biçimde silinmelidir.
