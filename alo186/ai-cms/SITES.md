# ALO186 AI CMS → ChatGPT Sites yayın köprüsü

ALO186’in özel alan adındaki canlı yüzeyi **ChatGPT Sites**, kaynak ve kalite otoritesi **GitHub** olarak çalışır.

```text
AI CMS brief
→ kaynak bağlı AI taslağı
→ noindex önizleme
→ insan PR incelemesi
→ /cms approve <slug>
→ published içerik kaydı + canonical HTML
→ ChatGPT Sites önizleme artifactı
→ açık yayın onayı
→ canlı yayın makbuzu
```

## Neden otomatik deploy yok?

ChatGPT Sites için belgelenmemiş bir API taklit edilmez. Köprü yalnız insan onaylı kaydı deterministik bir teslim paketine dönüştürür. Pakette:

- `publish=false`,
- `humanPreviewRequired=true`,
- `automaticDeployAllowed=false`,
- `undocumentedApiUseAllowed=false`

kalır.

Bu sınır iki farklı yayın sisteminin aynı alan adında kontrolsüz biçimde yarışmasını önler.

## İnsan onayı akışı

AI CMS PR’ında yetkili editör şu yorumu ekler:

```text
/cms approve <slug>
```

Onay workflow’u:

1. yorum sahibinin repository yetkisini doğrular,
2. içerik kaydını `published` durumuna getirir,
3. canonical HTML ve routing overlay üretir,
4. production build ve smoke testini geçirir,
5. aynı artifact içinde ChatGPT Sites teslim paketini oluşturur.

Artifact içeriği:

```text
sites-package.json
canonical.html
content-record.json
sites-preview-prompt.md
sites-receipt-template.json
```

## Ana daldan paketi yeniden üretme

GitHub Actions → **ALO186 AI CMS — ChatGPT Sites teslim paketi** → Run workflow.

Girdiler:

- `slug`: published AI CMS içerik slugı
- `source_ref`: varsayılan `main`; branch, tag veya commit olabilir

Workflow OpenAI API anahtarı kullanmaz. Yalnız kayıt, canonical HTML, insan onayı, kalite, schema ve hash bütünlüğünü doğrular.

## ChatGPT Sites önizlemesi

Artifact içindeki `sites-preview-prompt.md` dosyası şu biçimde başlar:

```text
Use @Sites to edit the site with the slug alo186, with:
```

Prompt; `canonical.html` ve `content-record.json` dosyalarını kaynak kabul eder, önizleme oluşturur ve açık yayın onayı bekler.

Önizlemede kontrol edilecekler:

- rota ve canonical eşleşmesi,
- tek H1,
- title ve meta description,
- `Article`, `FAQPage`, `BreadcrumbList`,
- zorunlu bağımsızlık açıklamaları,
- güvenlik sınırları,
- iç bağlantılar,
- fiyat, stok, puan ve garanti yasağı,
- kişisel veri ve raw analitik girdi yasağı.

## Canlı yayın makbuzu

Yayın sonrasında `sites-receipt-template.json` doldurulur ve şu komutla doğrulanır:

```bash
python alo186/ai-cms/sites_bridge.py \
  validate-receipt \
  --receipt /path/to/sites-receipt.json \
  --package /path/to/sites-package.json
```

Makbuz şu kanıtlar olmadan geçmez:

- package, record ve HTML SHA-256 eşleşmesi,
- kaynak commit eşleşmesi,
- geçerli HTTPS deployment URL,
- HTTP 200,
- canonical, title ve H1 eşleşmesi,
- yapılandırılmış verinin bulunması,
- platformun ChatGPT Sites olduğunun doğrulanması,
- timezone içeren yayın tarihi,
- `liveVerified=true`.

JSON sözleşmesi:

```text
alo186/ai-cms/schema/sites-receipt.schema.json
```

## Node 24

AI CMS workflow’ları:

- `actions/checkout@v6`
- `actions/setup-python@v6`
- `actions/upload-artifact@v7`
- `actions/github-script@v8`

kullanır. Böylece AI CMS hattı eski Node 20 action runtime’ına bağlı kalmaz.

## DNS ve hosting otoritesi

- `alo186.com` ve `www.alo186.com`: ChatGPT Sites DNS kayıtlarında kalır.
- GitHub: kaynak, PR, test, artifact ve geri alma otoritesidir.
- GitHub Pages: özel alan adının birincil canlı yayın sistemi değildir.
- Aynı özel alan adı GitHub Pages’e ayrıca bağlanmaz.
