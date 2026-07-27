# ALO186 taşınabilir Caddy TLS fallback'i

Render yerine VPS veya başka bir Docker sağlayıcısına geçilmesi gerektiğinde `api.alo186.com` için yönetilen TLS ve ters proxy katmanı sağlar.

## Kapsam

- Let's Encrypt/ZeroSSL otomatik sertifika yönetimi
- HTTP/1.1, HTTP/2 ve HTTP/3
- API readiness health check
- JSON erişim logu
- HSTS, nosniff, DENY frame, Referrer ve Permissions başlıkları
- API'nin yalnız internal Docker ağı üzerinden Caddy'ye açılması

## Kurulum

1. `docker-compose.yml` içindeki `ghcr.io/REPLACE_WITH_OWNER/...` image değerini gerçek API image etiketiyle değiştirin.
2. `.env.production` dosyasını yalnız sunucuda oluşturun.
3. DNS `api.alo186.com` kaydını VPS IP'sine yönlendirin.
4. 80/443 TCP ve 443 UDP portlarını açın.
5. Çalıştırın:

```bash
docker compose up -d
docker compose logs -f caddy
```

## Doğrulama

```bash
curl -fsS https://api.alo186.com/health/live
curl -fsS https://api.alo186.com/health/ready
openssl s_client -connect api.alo186.com:443 -servername api.alo186.com </dev/null 2>/dev/null \
  | openssl x509 -noout -issuer -subject -dates
```

## Güvenlik

- Caddy admin API kapalıdır.
- API portu hosta publish edilmez; yalnız `backend` ağındadır.
- `.env.production`, Caddy data volume'u ve özel anahtarlar yedekleme/erişim politikasıyla korunmalıdır.
- Birden fazla API replica kullanılacaksa mevcut memory rate limiter Redis'e taşınmadan yatay ölçek açılmamalıdır.

## Geri dönüş

Render'a dönülecekse önce Render custom domain health kontrolünü geçirin, ardından DNS TTL düşürülmüş bakım penceresinde `api` kaydını Render CNAME hedefine çevirin. Eski Caddy servisini DNS yayılımı tamamlandıktan sonra kapatın.
