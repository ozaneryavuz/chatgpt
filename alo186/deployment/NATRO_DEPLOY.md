# ALO186 Natro / Apache üretim yayın kılavuzu

Bu kılavuz, GitHub Actions tarafından üretilen `alo186-production-overlay` paketini mevcut `www.alo186.com` web köküne güvenli biçimde eklemek içindir. Paket ana sayfayı değiştirmez; yalnız yeni canonical rotaları, `robots.txt`, `sitemap.xml`, `.htaccess` ve 404 sayfasını içerir.

## 1. Yayın öncesi yedek

Natro dosya yöneticisi veya SFTP üzerinden mevcut web kökünün tam yedeğini alın:

```text
public_html/
```

Özellikle şu dosyaları ayrı saklayın:

```text
.htaccess
robots.txt
sitemap.xml
index.html
```

## 2. Doğru artifact

GitHub Actions iş akışından:

```text
alo186-production-overlay
```

artifact'ını indirin. `alo186-pages-preview` yalnız GitHub Pages ön izlemesi içindir ve kök `index.html` yönlendirmesi içerir; canlı sitenin ana sayfasına yüklenmemelidir.

## 3. Checksum doğrulaması

ZIP'i yerel bir klasöre açın ve paketteki `SHA256SUMS` dosyasını doğrulayın:

```bash
sha256sum -c SHA256SUMS
```

Bütün satırlar `OK` dönmelidir.

## 4. Web köküne yükleme

Overlay paketinin **içeriğini** `public_html/` içine yükleyin. Üstte ilave bir klasör oluşturmadan şu yapının oluştuğunu doğrulayın:

```text
public_html/
├── elektrik-portali/
├── edas-bul/
├── karar-motoru/
├── hesaplama/
├── akilli-urun-secimi/
├── isletme-surekliligi/
├── fatura-analizi/
├── robots.txt
├── sitemap.xml
├── .htaccess
└── 404.html
```

## 5. `.htaccess` birleştirme

Mevcut `.htaccess` içinde CMS, WordPress veya özel router kuralları varsa dosyayı doğrudan ezmeyin. `apache.htaccess` içindeki kuralları mevcut dosyanın en başında aşağıdaki sırayla birleştirin:

1. HTTPS / www canonical
2. güvenlik başlıkları
3. MIME ve sıkıştırma
4. mevcut CMS/router kuralları

WordPress kullanılıyorsa `# BEGIN WordPress` bölümüne dokunmayın; ALO186 kurallarını bu bölümün üstüne koyun.

## 6. Dosya izinleri

Önerilen izinler:

```text
klasörler: 755
dosyalar: 644
.htaccess: 644
```

## 7. Yayın smoke testi

Aşağıdaki rotalar HTTP 200 dönmelidir:

```text
https://www.alo186.com/elektrik-portali/
https://www.alo186.com/edas-bul/
https://www.alo186.com/karar-motoru/
https://www.alo186.com/hesaplama/
https://www.alo186.com/akilli-urun-secimi/
https://www.alo186.com/isletme-surekliligi/
https://www.alo186.com/fatura-analizi/
https://www.alo186.com/hesaplama/yedek-guc/
https://www.alo186.com/hesaplama/kesinti-maliyeti/
https://www.alo186.com/robots.txt
https://www.alo186.com/sitemap.xml
```

Kök host aynı yolu tek adımda www hostuna yönlendirmelidir:

```bash
curl -I https://alo186.com/edas-bul/
```

Beklenen:

```text
HTTP 301 veya 308
Location: https://www.alo186.com/edas-bul/
```

Asset kontrolü:

```bash
curl -I https://www.alo186.com/edas-bul/styles.css
curl -I https://www.alo186.com/edas-bul/app.js
```

Beklenen MIME:

```text
text/css
application/javascript veya text/javascript
```

## 8. Fonksiyon testi

- `/edas-bul/`: Marmaris, Ümraniye ve Esenyurt aramalarını deneyin.
- `/karar-motoru/`: “yere düşmüş kablo” akışında 112 önceliği ve ticari CTA yokluğunu doğrulayın.
- `/akilli-urun-secimi/`: satış ortaklığı açıklaması ve `sponsored` ürün bağlantılarını kontrol edin.
- `/isletme-surekliligi/`: örnek veri, localStorage, JSON export/import ve PDF yazdırmayı deneyin.
- `/hesaplama/`: UPS, EV ve kablo hesaplarını örnek değerlerle çalıştırın.

## 9. Search Console ve analitik

Yayın başarılı olduktan sonra:

1. `https://www.alo186.com/sitemap.xml` gönderin.
2. Yeni canonical rotalarda URL Denetimi çalıştırın.
3. Dizine ekleme isteği gönderin.
4. GA4 DebugView ile arama, karar, hesap, affiliate ve süreklilik olaylarını doğrulayın.

## 10. Geri alma

Hata durumunda:

1. yeni route klasörlerini kaldırın,
2. yedek `.htaccess`, `robots.txt` ve `sitemap.xml` dosyalarını geri yükleyin,
3. CDN/Cloudflare önbelleğini temizleyin,
4. önceki ana sayfanın çalıştığını doğrulayın.

## Canlı deploy için gerekli erişim

Bu işlemin otomatik yapılabilmesi için aşağıdakilerden biri gerekir:

- Natro SFTP/FTP host, kullanıcı ve güvenli secret tanımı,
- Natro Git deployment özelliği,
- cPanel API tokenı,
- mevcut site/hosting connector erişimi.

Secret değerleri repository içine yazılmamalı; GitHub Actions Secrets veya hosting secret manager kullanılmalıdır.
