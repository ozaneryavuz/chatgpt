# ALO186 DNS, TLS ve E-posta Kayıtları

## Birincil model: Cloudflare DNS + Render TLS

Render `api.alo186.com` için sertifikayı üretir ve yeniler. Cloudflare ilk doğrulama sırasında **DNS only / gri bulut** kullanılmalıdır. Render domain doğrulaması ve HTTPS çalıştıktan sonra proxy ihtiyacı ayrıca test edilebilir.

Render özel alan adı eklenmeden DNS kaydı uygulanmamalıdır.

### Gerekli environment değerleri

```bash
export CLOUDFLARE_API_TOKEN='yalnız Zone.DNS Edit yetkili token'
export CLOUDFLARE_ZONE_ID='...'
export ALO186_RENDER_API_HOSTNAME='alo186-continuity-api.onrender.com'
export ALO186_CLOUDFLARE_PROXY=false
```

Postmark değerleri mevcutsa:

```bash
export POSTMARK_DKIM_HOST='Postmark panelindeki host'
export POSTMARK_DKIM_VALUE='Postmark panelindeki TXT değer'
export POSTMARK_RETURN_PATH_HOST='Postmark panelindeki Return-Path host'
export POSTMARK_RETURN_PATH_VALUE='Postmark panelindeki CNAME hedefi'
```

Önce dry-run:

```bash
python alo186/infrastructure/dns/sync_cloudflare_dns.py
```

Sonra korumalı GitHub Environment veya kontrollü terminalden:

```bash
python alo186/infrastructure/dns/sync_cloudflare_dns.py --apply
```

Araç idempotent çalışır; aynı kayıt varsa değiştirmez. SPF güvenlik nedeniyle otomatik değiştirilmez çünkü alan adında mevcut posta sağlayıcılarının tek SPF kaydında birleştirilmesi gerekir.

## Cloudflare kayıtları

- `api.alo186.com CNAME <render-hostname>`
- `alo186.com CAA 0 issue letsencrypt.org`
- `alo186.com CAA 0 issue pki.goog`
- `_dmarc.alo186.com TXT ...`
- İsteğe bağlı Postmark DKIM ve Return-Path

Render özel alan adı doğrulaması tamamlanmadan `ALO186_CLOUDFLARE_PROXY=true` yapılmamalıdır.

## Natro'da kalınırsa manuel alternatif

Cloudflare nameserver geçişi yapılmayacaksa Natro DNS panelinde:

1. Render dashboard'da API servisine `api.alo186.com` custom domain ekleyin.
2. `api` için CNAME hedefini Render'ın verdiği `*.onrender.com` hostname yapın.
3. `api` üzerinde çakışan A/AAAA/CNAME kayıtlarını kaldırın.
4. Render IPv6 kullanmadığı için `api` AAAA kaydı bırakmayın.
5. CAA kayıtları varsa hem `letsencrypt.org` hem `pki.goog` yetkisini ekleyin.
6. Postmark DKIM TXT ve Return-Path CNAME kayıtlarını paneldeki değerlerle girin.
7. Mevcut SPF kaydını silmeden Postmark talimatını aynı SPF kaydında birleştirin.
8. `_dmarc` kaydını önce `p=none` ile başlatın.
9. Render domain doğrulamasını çalıştırın.
10. Aşağıdaki kontrolleri yapın:

```bash
dig +short CNAME api.alo186.com
curl -I https://api.alo186.com/health/live
openssl s_client -connect api.alo186.com:443 -servername api.alo186.com </dev/null
```

## TLS kabul kriterleri

- HTTP otomatik HTTPS'e yönleniyor.
- Sertifika SAN alanında `api.alo186.com` bulunuyor.
- Sertifikanın bitmesine 21 günden fazla var.
- `/health/live` ve `/health/ready` HTTPS üzerinden 200 dönüyor.
- Güvenlik başlıkları mevcut.
- Render doğrulaması tamamlandıktan sonra istenirse `onrender.com` subdomain devre dışı bırakılıyor.
