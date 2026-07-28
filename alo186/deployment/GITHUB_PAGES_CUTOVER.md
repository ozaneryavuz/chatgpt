# ALO186 — Natro web hosting olmadan GitHub Pages canlı yayın geçişi

Bu runbook, **Natro web hosting veya Natro CDN kullanmadan** ALO186 statik üretim paketini GitHub Pages üzerinde yayınlar. Natro yalnız alan adı kayıt kuruluşu/DNS paneli olarak kalabilir; mevcut e-posta MX ve TXT kayıtları korunur.

## Hedef mimari

```text
GitHub main
  → canonical production builder
  → güvenlik / cihaz hasarı / canonical testleri
  → GitHub Pages hazırlayıcı
  → route bridge + release status + offline emergency cache
  → GitHub Pages
  → www.alo186.com
```

GitHub Pages custom workflow akışı:

- `actions/configure-pages@v5`
- `actions/upload-pages-artifact@v4`
- `actions/deploy-pages@v4`

Ana workflow: `.github/workflows/alo186-github-pages.yml`

## Bir defalık GitHub ayarı

1. `ozaneryavuz/chatgpt` → **Settings** → **Pages**.
2. **Build and deployment / Source** alanında **GitHub Actions** seçin.
3. **Custom domain** alanına `www.alo186.com` yazıp kaydedin.
4. DNS doğrulandıktan ve sertifika hazırlandıktan sonra **Enforce HTTPS** seçeneğini etkinleştirin.
5. Hesap seviyesinde **Settings → Pages → Verified domains** bölümünden `alo186.com` alan adını TXT kaydıyla doğrulayın. TXT kaydını doğrulama sonrasında silmeyin.

> GitHub Actions ile yayınlanan Pages sitelerinde repository içindeki `CNAME` dosyası custom domain ayarını otomatik yapmaz. Domain, repository Pages ayarından tanımlanmalıdır.

## DNS kesintisiz geçiş planı

Önce GitHub Pages custom domain ayarı kaydedilir, sonra DNS değiştirilir. DNS sağlayıcınız Natro olarak kalabilir; yalnız web kayıtları GitHub Pages'e döner.

### `www` kaydı

| Tür | Ad | Değer |
|---|---|---|
| CNAME | `www` | `ozaneryavuz.github.io` |

Repository adı CNAME hedefine eklenmez.

### Apex `alo186.com` kayıtları

| Tür | Ad | Değer |
|---|---|---|
| A | `@` | `185.199.108.153` |
| A | `@` | `185.199.109.153` |
| A | `@` | `185.199.110.153` |
| A | `@` | `185.199.111.153` |

İsteğe bağlı IPv6:

| Tür | Ad | Değer |
|---|---|---|
| AAAA | `@` | `2606:50c0:8000::153` |
| AAAA | `@` | `2606:50c0:8001::153` |
| AAAA | `@` | `2606:50c0:8002::153` |
| AAAA | `@` | `2606:50c0:8003::153` |

### Silinecek veya değiştirilecek web kayıtları

- Apex veya `www` için eski Natro hosting A/CNAME kayıtları
- Eski CDN proxy kayıtları
- Çakışan URL yönlendirmeleri

### Korunacak kayıtlar

- MX kayıtları
- SPF, DKIM ve DMARC TXT kayıtları
- E-posta doğrulama kayıtları
- OpenAI site doğrulama TXT kayıtları
- GitHub Pages alan adı doğrulama TXT kaydı

Wildcard `*` DNS kaydı oluşturmayın.

## TTL ve güvenli geçiş

1. Geçişten birkaç saat önce web kayıtlarının TTL değerini 300 saniyeye indirin.
2. GitHub Pages workflow'unun default `github.io` sürümünde başarıyla deploy olduğunu doğrulayın.
3. Custom domain'i GitHub Pages ayarına ekleyin.
4. `www` CNAME ve apex A kayıtlarını değiştirin.
5. DNS yayılımını ve HTTPS sertifikasını doğrulayın.
6. 24 saat kararlı çalıştıktan sonra TTL'yi 3600 saniye veya normal politikanıza yükseltin.

## Canlı kabul kontrolleri

- `https://www.alo186.com/` HTTP 200
- `https://alo186.com/...` otomatik olarak aynı `www` yoluna yönlenir
- `/alo186-release.json` ve `/pages-release.json` HTTP 200
- `/durum/` üzerinde commit ve kritik rota kontrolleri görünür
- `/edas-bul/`, `/karar-motoru/`, `/hesaplama/`, `/akilli-urun-secimi` HTTP 200
- Cihaz hasarı metni `10 iş günü`
- Sitemap ve canonical origin `https://www.alo186.com`
- Default `github.io/chatgpt` yüzeyi `noindex,follow`
- Custom domain yüzeyi index/follow
- Kritik rehberler ilk ziyaret sonrasında çevrimdışı açılabilir

## Pages'e özel inovatif katmanlar

### Uyarlanabilir base path

Aynı artifact iki şekilde test edilir:

- Custom domain: `/`
- GitHub project site: `/chatgpt`

Default github.io yüzeyi custom domain kurulmadan önce teknik önizleme olarak kullanılabilir; duplicate indeksleme oluşmaması için otomatik `noindex` uygulanır.

### Route bridge

Statik pakette henüz bulunmayan eski iç URL'ler otomatik `noindex` yönlendirme sayfasına dönüştürülür. Böylece Natro'daki eski sayfa bağlantıları kullanıcıyı 404 yerine en yakın güncel karar aracına taşır.

### Offline emergency cache

Service worker şu kritik sayfaları ilk ziyaretten sonra çevrimdışı önbelleğe alır:

- Ana kapı
- EDAŞ bulucu
- 112 / 186 / elektrikçi karar motoru
- Hesaplama merkezi
- Kesinti günlüğü
- Cihaz hasarı başvuru rehberi
- Planlı kesinti rehberi

Bu özellik resmî acil hizmet yerine geçmez; internet kesintisi sırasında daha önce ziyaret edilmiş güvenlik bilgisinin okunabilmesini sağlar.

## Geri alma

DNS geçişinde sorun oluşursa:

1. `www` ve apex web kayıtlarını önceki değerlere geri alın.
2. GitHub Pages custom domain ayarını kaldırmayın; önce DNS'in kararlı dönmesini bekleyin.
3. E-posta kayıtlarına dokunmayın.
4. GitHub Actions artifactındaki `pages-release.json` ve checksum paketini olay kaydı olarak saklayın.

## Resmî GitHub belgeleri

- https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages
- https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/managing-a-custom-domain-for-your-github-pages-site
- https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/verifying-your-custom-domain-for-github-pages
