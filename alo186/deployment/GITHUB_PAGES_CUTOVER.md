# ALO186 — çift modlu canlı yayın ve GitHub Pages geçişi

Bu runbook, ALO186’in bütün doğrulanmış statik üretim paketini **GitHub Pages** üzerinde yayınlamayı ve geçiş tamamlanana kadar mevcut **ChatGPT Sites / static-snapshot** canlı yüzeyini fail-closed denetlemeyi açıklar.

Natro alan adı kayıt kuruluşu ve DNS sağlayıcısı olarak kalabilir. Web yayını GitHub Pages’e taşınırken MX, SPF, DKIM, DMARC, OpenAI doğrulama ve diğer e-posta/TXT kayıtları korunur.

## Güncel çalışma modeli

```text
GitHub main
  → canonical production builder
  → güvenlik / hukukî süre / canonical / affiliate testleri
  → custom-domain ve /chatgpt artifact kabulü
  → v177 bağlamsal ürün yerleşimleri
  → GitHub Pages hazırsa tam deploy
  → Pages hazır değilse ChatGPT Sites canlı v177 denetimi
  → production makbuzu
```

Ana çift modlu workflow:

```text
.github/workflows/alo186-pages-autobootstrap-live.yml
```

Workflow her **30 dakikada bir** yeniden çalışır:

- GitHub Pages hazırsa bütün ALO186 artifactını yayınlar.
- Pages henüz hazır değilse mevcut `https://alo186.com` canlı yüzeyini ve v177 ürün haritasını doğrular.
- Başarı veya kesin blokaj makbuzunu PR #606 ile P0 issue #21 üzerinde tekilleştirir.

## Hedef canlı sözleşme

- Birincil origin: `https://alo186.com`
- `https://www.alo186.com/...` aynı apex yola yönlenir.
- Final canonical origin: `https://alo186.com`
- GitHub project-site teknik önizlemesi: `https://ozaneryavuz.github.io/chatgpt/`
- Project-site yüzeyi duplicate indekslemeyi önlemek için `noindex,follow` taşır.

## Bir defalık GitHub Pages etkinleştirmesi

Aşağıdaki yöntemlerden yalnız biri yeterlidir.

### Yöntem A — GitHub arayüzü

1. `ozaneryavuz/chatgpt` → **Settings** → **Pages**.
2. **Build and deployment / Source** alanında **GitHub Actions** seçin.
3. **Custom domain** alanına `alo186.com` yazıp kaydedin.
4. DNS doğrulandıktan ve sertifika hazırlandıktan sonra **Enforce HTTPS** seçeneğini etkinleştirin.
5. Hesap seviyesinde **Settings → Pages → Verified domains** bölümünden `alo186.com` alan adını GitHub’ın verdiği TXT kaydıyla doğrulayın.
6. Alan adı doğrulama TXT kaydını doğrulama sonrasında silmeyin.

> GitHub Actions ile yayınlanan Pages sitelerinde repository içindeki `CNAME` dosyası tek başına custom-domain ayarını tamamlamaz. Domain, repository Pages ayarından tanımlanmalıdır.

### Yöntem B — otomatik bootstrap secretı

Repository → **Settings → Secrets and variables → Actions → New repository secret** bölümünde şu secretı oluşturun:

```text
ALO186_PAGES_ADMIN_TOKEN=<fine-grained personal access token>
```

Token yalnız `ozaneryavuz/chatgpt` repository’siyle sınırlandırılmalı ve en az şu repository izinlerini taşımalıdır:

```text
Pages: Read and write
Administration: Read and write
```

Secret değeri issue, PR yorumu, workflow çıktısı veya repository dosyasına yazılmamalıdır.

Secret eklendikten sonra periyodik workflow:

1. Pages sitesini workflow modunda oluşturmayı,
2. `alo186.com` özel alan adını tanımlamayı,
3. tam artifactı yayınlamayı,
4. exact commit ve v177 canlı makbuzunu doğrulamayı

otomatik yeniden dener.

## DNS geçişi

Önce GitHub Pages custom-domain ayarını kaydedin; sonra yalnız web DNS kayıtlarını değiştirin.

### Apex `alo186.com`

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

### `www`

| Tür | Ad | Değer |
|---|---|---|
| CNAME | `www` | `ozaneryavuz.github.io` |

Repository adı CNAME hedefine eklenmez. Final canlı sözleşmede `www`, aynı yolu koruyarak apex `https://alo186.com` adresine yönlenir.

### Silinecek veya değiştirilecek web kayıtları

- Apex veya `www` için eski hosting A/CNAME kayıtları
- Eski web/CDN proxy kayıtları
- Apex ve `www` ile çakışan URL yönlendirmeleri

### Kesinlikle korunacak kayıtlar

- MX kayıtları
- SPF, DKIM ve DMARC TXT kayıtları
- E-posta sağlayıcısı doğrulama kayıtları
- OpenAI site doğrulama TXT kayıtları
- GitHub Pages verified-domain TXT kaydı
- Web dışındaki hizmetlere ait diğer TXT kayıtları

Wildcard `*` DNS kaydı oluşturmayın.

## TTL ve kesintisiz geçiş

1. Geçişten birkaç saat önce yalnız web kayıtlarının TTL değerini 300 saniyeye indirin.
2. `https://ozaneryavuz.github.io/chatgpt/` teknik önizlemesinin HTTP 200 döndüğünü doğrulayın.
3. GitHub Pages Source alanını `GitHub Actions` yapın veya yönetici tokenını ekleyin.
4. `alo186.com` custom domain ayarının GitHub tarafında kabul edildiğini doğrulayın.
5. Apex A ve `www` CNAME kayıtlarını değiştirin.
6. DNS yayılımını ve TLS sertifikasını doğrulayın.
7. Canlı makbuz exact commit ve v177 kontrollerini geçtikten sonra **Enforce HTTPS** seçeneğini açın.
8. 24 saat kararlı çalışmadan sonra TTL değerini normal politikanıza yükseltin.

## Canlı kabul kriterleri

### Platform ve release

- [ ] GitHub Pages Source = `GitHub Actions`
- [ ] `https://ozaneryavuz.github.io/chatgpt/` HTTP 200
- [ ] `alo186.com` Pages custom domain olarak doğrulanmış
- [ ] Apex ve `www` web DNS kayıtları GitHub Pages’e yönleniyor
- [ ] HTTPS sertifikası ve Enforce HTTPS aktif
- [ ] `/pages-release.json` HTTP 200 ve canlı exact commit’i taşıyor
- [ ] `/alo186-release.json` HTTP 200
- [ ] `/durum/` kritik rotaları yeşil gösteriyor

### Kullanıcı ve rota sözleşmesi

- [ ] `/`, `/elektrik-portali/`, `/edas-bul/`, `/karar-motoru/`, `/hesaplama/` ve `/akilli-urun-secimi/` HTTP 200
- [ ] `/amazon-elektrik-urunleri/konuya-gore-urun-haritasi/` HTTP 200
- [ ] V177 sayfasında `data-alo186-contextual-affiliate-v177` bulunuyor
- [ ] V177 sayfasında tam **3** bağlamsal ürün yerleşimi ve **3** ticari kapı bulunuyor
- [ ] HTML içinde kapısız/statik Amazon bağlantısı bulunmuyor
- [ ] JavaScript asseti `alo186rehber-21` ve `sponsored nofollow noopener` taşıyor
- [ ] `affiliate_context_view`, `affiliate_gate_open` ve `affiliate_product_select` olayları mevcut
- [ ] V177 JavaScript’i `localStorage` veya `document.cookie` kullanmıyor
- [ ] Product, Offer veya AggregateRating şeması yayımlanmıyor

### Hukukî, canonical ve güvenlik sözleşmesi

- [ ] Cihaz hasarı başvuru süresi güncel kaynak sözleşmesine göre **30 gün**
- [ ] Final sitemap ve canonical origin `https://alo186.com`
- [ ] `www`, yolu koruyarak apex domaine yönleniyor
- [ ] Default project-site yüzeyi `noindex,follow`
- [ ] Kritik rehberler ilk çevrimiçi ziyaret sonrasında çevrimdışı açılabiliyor
- [ ] MX, SPF, DKIM, DMARC ve webmail işlevi bozulmadı

## Pages hazır değilken ChatGPT Sites kabulü

GitHub Pages geçişi tamamlanmadan mevcut canlı site aşağıdaki koşulların tümüyle doğrulanırsa geçici canlı makbuz oluşturulabilir:

- Canlı hosting modu ChatGPT Sites / Vinext veya static-snapshot olarak doğrulanır.
- V177 ürün haritası rotası HTTP 200 döner.
- Marker, üç ürün yerleşimi, üç ticari kapı ve affiliate etiketi bulunur.
- V177 JavaScript asseti güvenli `rel` sözleşmesini ve analitik olaylarını taşır.
- Kişisel veri depolama alanı eklenmemiştir.

Bu geçici makbuz GitHub Pages exact-commit geçişinin yerine geçmez; yalnız mevcut canlı Sites yüzeyinin doğrulanmış kullanıcı sözleşmesini kanıtlar.

## Geri alma

DNS veya sertifika geçişinde sorun oluşursa:

1. Yalnız apex ve `www` web kayıtlarını önceki değerlere geri alın.
2. E-posta ve doğrulama TXT kayıtlarına dokunmayın.
3. GitHub Pages custom-domain ayarını hemen silmeyin; önce DNS’in kararlı dönmesini bekleyin.
4. Son başarılı `alo186-full-live-reference` ve `alo186-full-live-receipt` artifactlarını olay kaydı olarak saklayın.
5. P0 issue #21’i canlı exact-commit ve rota makbuzu yeniden geçene kadar açık tutun.

## Resmî GitHub belgeleri

- https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages
- https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/managing-a-custom-domain-for-your-github-pages-site
- https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/verifying-your-custom-domain-for-github-pages
- https://docs.github.com/en/rest/pages/pages#create-a-github-pages-site
