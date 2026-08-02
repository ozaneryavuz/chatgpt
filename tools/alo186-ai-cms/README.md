# ALO186 AI CMS v220

ALO186 için **GitHub kaynaklı, ChatGPT Sites hedefli, fail-closed headless içerik yönetim sistemi**.

Bu klasör canlı siteye paketlenmez. Kullanıcıların görmemesi gereken kuyruk, puan, kanıt, yayın talimatı ve makbuzlar `tools/` altında kalır.

## Mimari

```text
Kullanıcı niyeti / fırsat
        ↓
queue.json
        ↓
mevcut rota + canonical + H1 envanteri
        ↓
çakışma, kaynak, güven, ticaret ve gizlilik kapıları
        ↓
en yüksek puanlı en fazla 3 brief
        ↓
ChatGPT Sites aktarım paketi + önizleme talimatı
        ↓
manuel yayın onayı
        ↓
Sites yayın makbuzu + canlı doğrulama
```

- **Canlı platform:** ChatGPT Sites (`alo186`)
- **Kaynak ve sürüm sistemi:** GitHub
- **Yayın ilkesi:** önizleme ve insan onayı olmadan canlı deploy yok
- **AI sağlayıcı anahtarı:** gerekmez; sistem OpenAI API çağrısı yapmaz
- **Sites entegrasyonu:** belgelenmemiş bir API taklit edilmez. CMS, `@Sites` tarafından uygulanabilen makine okunur paket ve prompt üretir.

## Komutlar

Depo kökünde:

```bash
python tools/alo186-ai-cms/cms.py --repo . audit \
  --output /tmp/alo186-ai-cms-audit.json

python tools/alo186-ai-cms/cms.py --repo . plan \
  --out-dir /tmp/alo186-ai-cms-plan \
  --limit 3 \
  --source-commit "$(git rev-parse HEAD)"

python tools/alo186-ai-cms/cms.py --repo . validate-draft draft.json
python tools/alo186-ai-cms/cms.py --repo . validate-receipt receipt.json
```

## Kuyruk sözleşmesi

Yeni fırsatlar `queue.json > items` alanına eklenir. `ready` durumu ancak şu koşullarla kullanılabilir:

- puan yayın eşiğini geçer;
- önerilen rota mevcut değildir;
- mevcut title/H1/canonical envanteriyle niyet çakışması yoktur;
- en az üç güncel kaynak ve iki birincil kaynak vardır;
- en az altı çalışan iç bağlantı vardır;
- içerik türüne uygun schema tipleri tanımlıdır;
- güvenlik sınırı ve dönüşüm olayı belirlenmiştir;
- riskli kümelerde affiliate yolu kapalıdır.

Durum akışı:

```text
discovery → research → ready → drafted → validated → sites-ready → published
                         ↘ hold / rejected
```

## Çalıştırma çıktıları

`plan` komutu şunları üretir:

- `audit-report.json`: envanter ve kalite bulguları
- `plan-summary.json`: seçilen ilk üç içerik
- `briefs/<id>.json`: AI/ChatGPT üretim sözleşmesi
- `sites-package.json`: ChatGPT Sites rota işlemleri
- `sites-publish-prompt.md`: doğrudan `@Sites` talimatı
- `dashboard.html`: indirilebilir yönetim görünümü

Paketin `publish` alanı varsayılan olarak `false` kalır. Canlı deploy sonrasında `sites-receipt.schema.json` sözleşmesine uygun makbuz üretilir.

## Fail-closed korumalar

- düşük puanlı `ready/published` içerik reddedilir;
- aynı rota veya canonical yinelenemez;
- yüksek niyet benzerliği ayrı rota açamaz;
- eski kaynak, eksik claim veya yetersiz birincil kaynak reddedilir;
- dizi içinde saklanan `Product`, `Offer`, `AggregateRating`, `Person` ve `ProfilePage` tipleri de yakalanır;
- riskli içerikte affiliate açılamaz;
- raw kullanıcı girdileri analitiğe gönderilemez;
- CMS dosyaları public `alo186/` ağacına konamaz;
- workflow hata bastırmaz ve `continue-on-error` kullanmaz.

## Yeni fırsat ekleme

1. GitHub’da **ALO186 AI CMS içerik fırsatı** issue formunu doldur.
2. Kaynaklar doğrulandıktan sonra fırsatı `queue.json` biçimine dönüştür.
3. `audit` ve `plan` workflow’unu çalıştır.
4. İlk üç briefi ChatGPT ile taslağa dönüştür.
5. `validate-draft` kapısını geçir.
6. `sites-publish-prompt.md` ile `@Sites` önizlemesi oluştur.
7. Önizleme kabulünden sonra deploy et ve yayın makbuzunu kaydet.
