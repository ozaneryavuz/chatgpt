# ALO186 AI CMS v220

GitHub-native, gizlilik odaklı ve insan onaylı içerik yönetim katmanıdır. AI çıktısı doğrudan canlıya gönderilmez.

## Akış

1. `requests/` altında yapılandırılmış içerik isteği oluşturulur.
2. `generate` komutu OpenAI Responses API ve web aramasıyla şemaya bağlı taslak üretir. API anahtarı yoksa `--offline-scaffold` yalnız editoryal iskelet oluşturur.
3. Taslak `drafts/` altında tutulur; kaynak, teknik kapsam ve güvenlik sınırı kurumsal olarak incelenir.
4. Onaylanan kayıt `approved/` altında `status=approved`, `approval_state=approved`, `approval_scope=institutional` ve `evidence_complete=true` ile saklanır.
5. `compile` deterministik HTML, routing overlay ve yayın kanıtı üretir.
6. Mevcut static build, sitemap, canonical, erişilebilirlik, ticari güvenlik ve canlı kalite kapıları çalışır.
7. Değişiklik yalnız taslak PR olarak açılır; otomatik birleştirme veya otomatik yayın yoktur.

## Komutlar

```bash
python alo186/deployment/ai_cms_v220.py validate
python alo186/deployment/ai_cms_v220.py audit
python alo186/deployment/ai_cms_v220.py generate \
  --request alo186/cms/requests/example.json \
  --offline-scaffold
python alo186/deployment/ai_cms_v220.py generate \
  --request alo186/cms/requests/example.json \
  --model gpt-5-mini
python alo186/deployment/ai_cms_v220.py compile \
  --article alo186/cms/approved/ornek-ups-bakim-karari.json
```

## GitHub Actions

`ALO186 AI CMS v220` workflow'u manuel olarak çalıştırılır. `generate` işlemi için repository secret olarak `OPENAI_API_KEY` gerekir. Model tercihi `ALO186_AI_CMS_MODEL` ortam değişkeni veya workflow girdisiyle değiştirilebilir.

Workflow yalnız yetkili repository kullanıcısı tarafından manuel başlatılır, her çalışmada en fazla bir içerik üretir ve değişiklik varsa taslak PR açar.

## Gizlilik ve güvenlik

- Kişisel profil, kişi şeması, e-posta, kişisel telefon ve açık adres yasaktır.
- Ham API yanıtları, kullanıcı promptları ve issue yazarı saklanmaz.
- AI CMS affiliate bağlantısı, fiyat, stok, puan veya teslimat bilgisi üretmez.
- Orta ve yüksek riskli içerik en az bir resmî/mevzuat kaynağı olmadan derlenemez.
- Onaysız taslak HTML'e çevrilemez.
