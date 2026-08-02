# ALO186 AI CMS v1

ALO186 AI CMS, mevcut statik yayın mimarisini değiştirmeden çalışan **Git-native, kaynak bağlı ve insan onaylı** içerik yönetim katmanıdır.

## Neden ayrı bir CMS?

ALO186 yüzlerce canonical rota, hesaplayıcı, teknik makale, ticari rehber ve hukukî güvenlik kapısı taşıyor. Doğrudan HTML üretmeye devam etmek şu riskleri büyütür:

- aynı arama niyetinde ikinci canonical sayfa,
- kaynak gösterilmeyen AI metni,
- mevzuat veya güvenlik bilgisinin yaşlanması,
- affiliate CTA’nın yüksek riskli içeriğe sızması,
- insan onayı olmadan yayın,
- title/H1/canonical/routing drift’i,
- içerik üretim hızının kalite kapılarından kopması.

AI CMS bu riskleri tek içerik kaydı ve fail-closed yayın akışıyla yönetir.

## Mimari

```text
GitHub workflow_dispatch
        │
        ▼
Brief JSON
        │
        ▼
Prompt öncesi kişisel veri guardı
        │
        ▼
OpenAI Responses API
store=false + Structured Outputs
        │
        ▼
Review durumundaki içerik JSON'u
        │
        ├── Markdown inceleme paketi
        └── noindex HTML önizleme
        │
        ▼
Pull Request
        │
        ▼
/cms approve <slug>
(yalnız repository yetkilisi)
        │
        ▼
Kaynak + kanibalizasyon + risk + kalite doğrulaması
        │
        ▼
Canonical HTML + routing overlay
        │
        ▼
İnsan merge'i
        │
        ▼
Mevcut ALO186 production build ve Pages yayını
```

## Temel ilkeler

1. **AI yayın yapamaz.** AI yalnız `review` durumunda taslak üretir.
2. **İnsan onayı zorunludur.** `approvedBy`, `approvedAt` ve PR numarası olmadan canonical HTML üretilemez.
3. **Kaynak özetleri zorunludur.** Model yalnız brief içindeki `factSummary` alanlarını kullanabilir.
4. **Prompt öncesi veri guardı zorunludur.** Kişisel e-posta, telefon, T.C. kimlik, IBAN ve tesisat/abonelik kimliği OpenAI çağrısından önce fail-closed engellenir.
5. **Yüksek/hukukî riskte affiliate kapalıdır.** Yangın, pano, sabit tesisat, hukuk ve benzeri konularda ticari CTA fail-closed engellenir.
6. **Fiyat/stok/puan/garanti üretilmez.** ALO186 satıcı değildir; `Product`, `Offer`, `Person` ve `ProfilePage` şemaları yasaktır.
7. **Canonical çakışma ve kanibalizasyon engellenir.** Benzerlik eşiği `0.78` üzerindeyse onay durur.
8. **Kaynak erişim yaşı risk sınıfına göre sınırlıdır.** Hukukî içerikte 90, yüksek riskte 180 gün.

## İçerik yaşam döngüsü

```text
brief → review → approved → published → archived
```

- `brief`: konu, niyet, risk, kaynak ve iç link girdileri.
- `review`: AI taslağı üretildi; yayımlanamaz.
- `approved`: yetkili insan editör kalite kapılarını geçerek onayladı.
- `published`: canonical HTML ve routing overlay üretildi.
- `archived`: yeni yayına kapalı tarihsel kayıt.

## Repository yapısı

```text
alo186/ai-cms/
├── briefs/                   # editoryal talepler
├── content/                  # tek kaynak içerik kayıtları
├── previews/                 # noindex önizlemeler; canlı rotaya dahil değil
├── reviews/                  # PR inceleme paketleri
├── prompts/                  # sürümlü kurumsal AI talimatları
├── schema/                   # içerik ve Structured Output şemaları
├── policy.json               # kalite, risk ve yayın politikası
├── input_guard.py            # prompt öncesi PII/müşteri verisi kapısı
├── cms.py                    # CLI ve yayın motoru
├── SECURITY.md               # güvenlik ve olay müdahale sözleşmesi
└── README.md
```

## Gerekli GitHub secret ve variable

Repository secret:

```text
OPENAI_API_KEY
```

İsteğe bağlı repository variable:

```text
ALO186_AI_CMS_MODEL=gpt-5-mini
```

Varsayılan model `policy.json` içinden `gpt-5-mini` olarak gelir. Model değişikliği içerik kaydındaki `editorial.model` alanına yazılır.

API anahtarı yalnız server-side GitHub Action adımında kullanılır; HTML, review dosyası, workflow artifactı veya log içine yazılmaz.

## Yeni taslak oluşturma

GitHub Actions → **ALO186 AI CMS — taslak üret** → Run workflow.

Girdiler:

- `slug`
- `title`
- `topic`
- `intent`
- `primary_keyword`
- `audience`
- `risk_class`
- `sources_json`
- `internal_links_json`
- isteğe bağlı `commerce_category`

### Kaynak JSON örneği

```json
[
  {
    "id": "S1",
    "publisher": "EPDK",
    "title": "Resmî düzenleme veya tüketici bilgilendirmesi",
    "url": "https://ornek-resmi-kaynak.gov.tr/belge",
    "accessedAt": "2026-08-02",
    "primary": true,
    "factSummary": "Bu alana yalnız kaynakta gerçekten doğrulanan olgular, tarihler, kapsam ve istisnalar yazılır."
  }
]
```

AI, yeni URL veya kaynak üretemez; yalnız `S1`, `S2` gibi kimlikleri bölümlere ve SSS yanıtlarına bağlar.

## Yerel kullanım

Brief:

```bash
python alo186/ai-cms/cms.py new \
  --slug modem-mini-ups-secimi \
  --title "Modem Mini UPS Uygunluk Rehberi" \
  --topic "Modem ve ONT için mini UPS" \
  --intent "Kullanıcı satın almadan önce gerilim, polarite ve süreyi doğrulamak istiyor" \
  --primary-keyword "modem mini UPS" \
  --audience "Ev kullanıcıları,uzaktan çalışanlar" \
  --risk-class medium \
  --sources-json @/gizli-olmayan-kaynaklar.json
```

OpenAI çağrısından önce zorunlu veri kapısı:

```bash
python alo186/ai-cms/input_guard.py \
  --brief alo186/ai-cms/briefs/modem-mini-ups-secimi.json
```

AI taslağı:

```bash
export OPENAI_API_KEY='...'
python alo186/ai-cms/cms.py ai-draft --slug modem-mini-ups-secimi
```

Doğrulama:

```bash
python alo186/ai-cms/cms.py validate --slug modem-mini-ups-secimi --write
```

İnceleme paketi:

```bash
python alo186/ai-cms/cms.py review-pack --slug modem-mini-ups-secimi --write
```

İnsan onayı:

```bash
python alo186/ai-cms/cms.py approve \
  --slug modem-mini-ups-secimi \
  --reviewer GITHUB_KULLANICI_ADI \
  --pr 123
```

Canonical yayın dosyalarını üretme:

```bash
python alo186/ai-cms/cms.py publish --slug modem-mini-ups-secimi
```

## PR yorumuyla onay

Taslak PR üzerinde repository yetkilisi:

```text
/cms approve modem-mini-ups-secimi
```

yorumunu ekler.

Onay workflow’u:

- yorum sahibinin `OWNER`, `MEMBER` veya `COLLABORATOR` olmasını,
- PR’ın aynı repository branch’inden gelmesini,
- kalite puanının en az 85 olmasını,
- kaynak ve iç linklerin güncel olmasını,
- canonical çakışma bulunmamasını,
- yüksek riskli içerikte affiliate olmamasını

doğrular. Başarılıysa aynı PR branch’ine canonical HTML ve routing overlay ekler. PR yine otomatik merge edilmez.

## Kalite puanı

| Alan | Puan |
|---|---:|
| Metadata | 12 |
| Doğrudan cevap | 10 |
| İçerik derinliği | 18 |
| Kaynaklar | 20 |
| Güvenlik | 15 |
| İç bağlantılar | 10 |
| Benzersizlik | 10 |
| Yapısal veri kapsamı | 5 |
| **Toplam** | **100** |

Onay için minimum: **85/100**.

Puan yalnız gösterge değildir. Canonical çakışma, yasak güvenlik iddiası, eksik birincil kaynak, özel IP URL’si, kişisel iletişim bilgisi veya yanlış risk/commerce birleşimi puandan bağımsız olarak yayını durdurur.

## AI ve veri koruma

- Responses API çağrısı `store=false` kullanır.
- Prompt öncesinde `input_guard.py` çalışır ve yalnız alan yolu/ihlal türü raporlar; yakalanan değer loga yazılmaz.
- Prompt yalnız editoryal brief, kaynak özetleri ve mevcut başlık benzerliklerini taşır.
- Kullanıcı sorgusu, form girdisi, tesisat numarası veya müşteri verisi CMS’e gönderilmez.
- API çağrısı Structured Outputs JSON Schema ile sınırlandırılır.
- Model cevabı doğrudan canlı sayfa değildir.
- İnsan merge’i son yayın kapısıdır.

Resmî OpenAI referansları:

- Responses API: `https://platform.openai.com/docs/api-reference/responses`
- Structured Outputs: `https://platform.openai.com/docs/guides/structured-outputs`
- Model rehberi: `https://platform.openai.com/docs/models`
- Veri kontrolleri: `https://platform.openai.com/docs/models/default-usage-policies-by-endpoint`

## Editoryal dashboard

```bash
python alo186/ai-cms/cms.py dashboard \
  --output /tmp/alo186-ai-cms-dashboard.html
```

Dashboard canlı siteye eklenmez. Workflow artifactı olarak durum, risk, kalite, kaynak sayısı ve hata sayısını gösterir.

## Geri alma

Bir AI CMS içeriğini geri almak için:

1. ilgili PR merge commit’ini revert edin,
2. `alo186/haberler/<slug>/` klasörünü,
3. `alo186/deployment/routing-overlays/ai-cms-<slug>.json` dosyasını,
4. `alo186/ai-cms/content/<slug>.json` kaydını

aynı revert içinde geri alın.

CMS kaydı ile canonical HTML birbirinden bağımsız elle değiştirilmemelidir.
