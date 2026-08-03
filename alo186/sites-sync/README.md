# ALO186 GitHub → ChatGPT Sites kaynak otoritesi

Bu dizin, GitHub'daki doğrulanmış ALO186 içeriğinin **ChatGPT Sites canlı yayın
otoritesine** uygun biçimde aktarılmasında kullanılacak kaynak manifestini ve doğrudan
`@Sites` uygulama talimatını tutar.

## Tek mimari

```text
GitHub
  içerik + veri + rota + test + sürüm + geri alma
      ↓ alo186-chatgpt-sites-import-<sha> artifactı
ChatGPT Sites
  canlı bileşenler + tasarım + özel alan adı + yayın
```

- Canlı ve görsel sunum otoritesi: **ChatGPT Sites**
- İçerik, veri, kalite, sürüm ve rollback otoritesi: **GitHub**
- Canonical origin: `https://alo186.com`
- DNS: mevcut ChatGPT Sites kayıtları korunur
- GitHub Pages: özel alan adına bağlanmaz

## Tek artifact üreticisi

Canonical exporter:

```text
alo186/deployment/export_chatgpt_sites_bundle_v2.py
```

Politika:

```text
alo186/deployment/chatgpt-sites-export-policy.json
```

Workflow:

```text
.github/workflows/alo186-chatgpt-sites-export.yml
```

Workflow; ilgili `main` değişikliklerinde, pull requestlerde, manuel çağrıda ve her
pazartesi 10:20 Europe/Istanbul saatinde şu artifactı üretir:

```text
alo186-chatgpt-sites-import-<source-sha>
```

## Artifact sözleşmesi

Workflow hem klasörü hem indirilebilir ZIP arşivini yükler. Paket kökü şu dosyaları
içerir:

```text
alo186-chatgpt-sites/
├── sites-import.json             # sayfa bazlı Sites import envanteri
├── sites-source-manifest.json    # P0/P1/P2, güven ve yetki sözleşmesi
├── sites-import-prompt.md        # bağlı @Sites oturumunda uygulanacak talimat
├── SITE_BRIEF.md                 # Sites bilgi mimarisi ve değişmez kurallar
├── IMPORT_ORDER.md               # güvenli aktarım ve yayın sırası
├── SOURCE-AUTHORITY.md           # insan tarafından okunabilir kaynak otoritesi
├── checksums.sha256              # paket içi dosya bütünlüğü
├── content/pages/                # aktarıma hazır Markdown içerikler
├── review/                       # otomatik yayına kapalı inceleme kuyruğu
├── source/                       # gerekli HTML/JS/CSS ve yerel asset referansları
├── policies/
│   └── trust-and-commerce.md
└── data/
    ├── navigation.json
    ├── location-services.json    # 81 il ve 21 dağıtım şirketi
    ├── redirects.json
    ├── export-stats.json
    ├── source-authority.json     # commit, digest ve canlı yayın yetkisi
    └── source-integrity.json     # SHA-256 dosya listesi
```

Aynı artifact yükünde ayrıca:

```text
alo186-chatgpt-sites.zip
```

bulunur. ZIP; Sites aktarımı, arşiv ve geri alma doğrulaması için klasörle aynı
kaynak committen üretilir.

## Bu dizindeki dosyalar

- `sites-source-manifest.json`: aktarım katmanları, P0/P1/P2 sırası, güvenlik,
  affiliate, structured data, gizlilik ve çakışma politikası
- `sites-import-prompt.md`: Sites yazma bağlantısı bulunan konuşmada kullanılacak
  doğrudan uygulama ve yayın talimatı

## Taşınan katmanlar

1. Bağımsızlık, güvenlik, kaynak ve affiliate politikaları
2. Ana karar ve resmî yönlendirme deneyimi
3. 81 il ve 21 özel EDAŞ canonical sayfası
4. Yalnız onaylanmış/yayımlanabilir teknik içerikler
5. Hesaplayıcı ve karar araçlarının deterministik mantığı
6. Güvenlik kapılı Amazon Türkiye ürün yolları
7. Robots, sitemap, llms ve bilgi grafiği kaynakları
8. Redirect ve canonical tekillik haritası

## Taşınmayan katmanlar

- GitHub Actions ve Pages/Natro deploy altyapısı
- testler, fixture, rapor ve Python enjektör kaynakları
- secrets, API anahtarları ve hosting erişimleri
- eski veya onaysız hukukî/ticari iddialar
- `review` durumundaki yüksek riskli içerikler

## Uygulama

Artifact içindeki `sites-import-prompt.md`, Sites bağlantısı bulunan bir konuşmada
`@Sites` ile uygulanır. Sites'in doğal tasarımı korunur; GitHub'daki statik CSS canlı
tasarımı körlemesine ezmez. Yeni ve doğrulanmış içerik, veri, schema ve güvenlik
politikası mevcut Sites bileşenlerine birleştirilir.

Önerilen uygulama sırası:

1. ZIP'i veya artifact klasörünü bağlı Sites oturumuna ekleyin.
2. `sites-import-prompt.md` talimatını `@Sites` ile çalıştırın.
3. Önce P0 güven ve ana navigasyon katmanını, sonra 81 il/21 EDAŞ verisini aktarın.
4. Interaktif araçları deterministik mantıkla port edin; temel cevapları SSR görünür bırakın.
5. Yalnız `sites-import.json` içinde aktarıma hazır işaretlenen affiliate rehberlerini yayımlayın.
6. Redirect, sitemap, canonical ve canlı URL kabulünden sonra `sites-receipt.json` oluşturun.

## Tamamlanma ölçütü

Artifact üretimi canlı yayın değildir. Aktarım yalnız:

1. `@Sites` değişikliği uyguladığında,
2. canlı URL doğrulaması geçtiğinde,
3. kaynak commit ve içerik fingerprint'i içeren `sites-receipt.json` oluştuğunda

başarılı kabul edilir. Belgelenmemiş Sites API'si kullanılmaz.
