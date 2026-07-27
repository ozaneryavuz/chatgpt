# ALO186 production deployment runbook

Bu runbook GitHub `main` dalındaki statik ALO186 modüllerini mevcut `www.alo186.com` web köküne **ana sayfayı silmeden** yayınlamak için hazırlanmıştır.

## 1. Pipeline ne yayınlar?

`build_static_site.py`, `routing-manifest.json` dosyasından yalnız canonical ürün rotalarını oluşturur:

- `/elektrik-portali`
- `/edas-bul`
- `/karar-motoru`
- `/hesaplama/`
- `/akilli-urun-secimi`
- `/isletme-surekliligi`
- `/fatura-analizi`
- `/hesaplama/yedek-guc`
- `/hesaplama/kesinti-maliyeti`

Bundle köküne ayrıca:

- `.htaccess`
- `robots.txt`
- `sitemap.xml`
- `alo186-release.json`
- `checksums.sha256`

eklenir.

Bundle **kök `index.html` içermez**; mevcut canlı ana sayfayı değiştirmez.

## 2. Önce artifact ile manuel doğrulama

GitHub Actions → **ALO186 üretim yayın paketi ve opsiyonel deploy** → son başarılı build → `alo186-production-site` artifact.

Arşiv içeriğini yerelde doğrulama:

```bash
sha256sum -c alo186-production-site.tar.gz.sha256
mkdir release
 tar -xzf alo186-production-site.tar.gz -C release
python alo186/deployment/smoke_static_site.py --bundle release
```

## 3. Repository variables

GitHub Repository Settings → Secrets and variables → Actions → Variables:

| Değişken | Değer |
|---|---|
| `ALO186_PRODUCTION_DEPLOY_ENABLED` | İlk testte `false`; onaydan sonra `true` |
| `ALO186_DEPLOY_METHOD` | `ssh` veya `ftps` |
| `ALO186_DEPLOY_PATH` | Web kökü; ör. `/home/kullanici/public_html` veya `/public_html` |

Production environment adı:

```text
alo186-production
```

İlk gerçek yayın öncesinde environment protection rule ve manuel onay kullanılması önerilir.

## 4. SSH seçeneği

Actions secrets:

| Secret | Açıklama |
|---|---|
| `ALO186_DEPLOY_HOST` | SSH sunucusu |
| `ALO186_DEPLOY_USER` | SSH kullanıcısı |
| `ALO186_DEPLOY_SSH_KEY` | Yalnız deploy yetkili özel anahtar |
| `ALO186_DEPLOY_KNOWN_HOSTS` | `ssh-keyscan` sonucu; StrictHostKeyChecking açıktır |

Sunucuda deploy kullanıcısı yalnız gerekli web kökü altına yazabilmelidir.

Pipeline `rsync` kullanır ancak `--delete` kullanmaz. Mevcut canlı dosyaları topluca silmez.

## 5. FTPS seçeneği

Actions secrets:

| Secret | Açıklama |
|---|---|
| `ALO186_DEPLOY_HOST` | FTPS sunucusu |
| `ALO186_DEPLOY_USER` | FTPS kullanıcısı |
| `ALO186_DEPLOY_PASSWORD` | FTPS parolası |

FTPS sertifika doğrulaması kapatılmaz. Düz FTP desteklenmez.

## 6. Apache / Natro shared hosting

Bundle içindeki `.htaccess`:

- kök alan adını aynı path ile `www` hostuna 301 yönlendirir,
- extensionless canonical ürün rotalarını ilgili `index.html` dosyasına internal rewrite eder,
- temel güvenlik başlıklarını ekler,
- dizin listelemeyi kapatır.

Yayından önce hosting panelinde şunları doğrulayın:

- Apache `mod_rewrite` etkin,
- `.htaccess` kullanımına izin var,
- web kökü doğru,
- mevcut farklı `.htaccess` kurallarıyla çakışma yok.

Mevcut `.htaccess` varsa dosyayı körlemesine değiştirmeyin; ALO186 kurallarını mevcut dosyaya birleştirin.

## 7. Nginx / VPS

`nginx-alo186-routes.conf` örneğini site konfigürasyonuna uyarlayın:

- sertifika yollarını girin,
- `root` değerini gerçek web köküne çevirin,
- `nginx -t` çalıştırın,
- kontrollü reload yapın.

```bash
sudo nginx -t
sudo systemctl reload nginx
```

## 8. Yayın sonrası zorunlu smoke test

Pipeline deploy sonrasında otomatik çalıştırır:

```bash
python alo186/deployment/smoke_live_routes.py --base-url https://www.alo186.com
```

Kontrol edilenler:

- final HTTP 200,
- final hostun `www` olması,
- title ve beklenen içerik işareti,
- canonical URL,
- CSS/JS HTTP durumu,
- CSS/JS MIME türü,
- `robots.txt` ve `sitemap.xml`.

## 9. Geri alma

İlk yayın öncesinde web kökü yedeği alınmalıdır.

SSH örneği:

```bash
ssh deploy@host 'tar -C /home/kullanici/public_html -czf /home/kullanici/backups/alo186-before-$(date +%Y%m%d-%H%M).tar.gz .'
```

Geri alma yalnız ALO186 tarafından değiştirilen route klasörleri, `robots.txt`, `sitemap.xml` ve `.htaccess` için yapılmalıdır.

## 10. Search Console ve GA4

Smoke test başarılı olduktan sonra:

1. `https://www.alo186.com/sitemap.xml` Search Console'a gönderilir.
2. `/edas-bul`, `/karar-motoru`, `/akilli-urun-secimi`, `/isletme-surekliligi` URL denetimi yapılır.
3. Canonical seçimi ve mobil tarama kontrol edilir.
4. GA4 DebugView ile temel olaylar doğrulanır:
   - `location_result_action_clicked`
   - `electrical_decision_completed`
   - `product_match_completed`
   - `affiliate_product_clicked`
   - `continuity_incident_started`

## 11. Güvenlik notu

Repository secret'larını kaynak koda, issue yorumuna veya artifact içine yazmayın. Deploy anahtarı üretim sunucusunda shell/root yetkisi taşımamalı; yalnız web kökü için en az yetki ilkesine göre sınırlandırılmalıdır.
