# ALO186 GitHub → ChatGPT Sites kaynak paketi

Bu dizin, GitHub'daki ALO186 içerik ve yapılandırmasının **ChatGPT Sites'in canlı
yayın otoritesine uygun** biçimde aktarılması için kontrol düzlemidir.

## Mimari

```text
GitHub
  içerik kayıtları + rota envanteri + testler + sürüm + geri alma
      ↓ doğrulanmış kaynak paketi
ChatGPT Sites
  canlı bileşenler + görsel tasarım + özel alan adı + yayın
```

GitHub Pages, Natro deploy dosyaları, Actions workflow'ları, testler, Python enjektörleri,
secretlar ve tanı raporları Sites'e taşınmaz. Sites'e yalnız kullanıcıya değer veren
canonical içerik, veri, yapılandırılmış veri, doğrulanmış araç mantığı ve yayın politikası gider.

## Dosyalar

- `sites-source-manifest.json`: aktarım katmanları, kaynak otoritesi, güvenlik ve çakışma politikası
- `sites-import-prompt.md`: Sites bağlantısı bulunan bir konuşmada doğrudan kullanılacak talimat
- `build_sites_source_package.py`: canonical production bundle'dan güvenli Sites kaynak artifactı üretir
- `test_sites_source_package.py`: paket kapsamı ve sızıntı korumaları için ağsız regresyon
- `.github/workflows/alo186-chatgpt-sites-source.yml`: manuel, ilgili main değişiklikleri ve haftalık çalışma

Üretilen artifact:

```text
alo186-chatgpt-sites-source/
├── sites-source-manifest.json
├── sites-import-prompt.md
├── route-inventory.json
├── source-integrity.json
├── metadata/
└── public/
```

## Taşınan katmanlar

1. Bağımsızlık, güvenlik, kaynak ve affiliate politikaları
2. Ana karar ve resmî yönlendirme deneyimi
3. 81 il ve 21 EDAŞ canonical sayfası
4. Yalnız `published` AI CMS içerikleri
5. Hesaplayıcı ve karar araçlarının deterministik mantığı
6. Güvenlik kapılı Amazon Türkiye ürün yolları
7. Robots, sitemap, llms ve bilgi grafiği kaynakları

## Taşınmayan katmanlar

- `.github/`, workflow ve Pages yayın altyapısı
- `alo186/tests/`, fixture ve raporlar
- `alo186/deployment/` kaynak kodu
- API anahtarları, secrets ve hosting erişim bilgileri
- eski/deprecated hukukî veya ticari iddialar
- onaysız `review` durumundaki yüksek riskli AI CMS taslakları

## Üretim

```bash
python alo186/deployment/build_static_site.py \
  --output /tmp/alo186-canonical \
  --commit "$(git rev-parse HEAD)"

python alo186/sites-sync/build_sites_source_package.py \
  --repo . \
  --bundle /tmp/alo186-canonical \
  --source-commit "$(git rev-parse HEAD)" \
  --out /tmp/alo186-chatgpt-sites-source
```

Sonra artifact içindeki `sites-import-prompt.md`, Sites yazma bağlantısının bulunduğu
bir konuşmada `@Sites` ile uygulanır.

## Güven sınırı

Bu paket belgelenmemiş Sites API'si kullanmaz ve kendi başına canlı yayın yapmaz.
Canlı yayın yalnız kullanıcı tarafından açıkça çağrılan ChatGPT Sites yazma yüzeyinde yapılır.
Yayın tamamlanmadan “Sites'e aktarıldı” iddiası üretilemez; makbuz ve canlı rota doğrulaması gerekir.
