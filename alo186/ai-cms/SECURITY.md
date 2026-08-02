# ALO186 AI CMS Güvenlik Sözleşmesi

## Prompt öncesi veri sınırı

GitHub Actions taslak hattı, brief oluşturulduktan hemen sonra ve OpenAI Responses API çağrısından **önce** `input_guard.py` çalıştırır.

Fail-closed engellenen kalıplar:

- kişisel e-posta adresi,
- Türkiye telefon numarası,
- geçerli T.C. kimlik numarası kontrol basamağı,
- TR IBAN,
- etiketlenmiş tesisat, abonelik, sayaç, müşteri veya kimlik numarası,
- `email`, `phone`, `address`, `tckn`, `iban`, `tesisatNo`, `abonelikNo`, `customerNumber` gibi yasak kişisel veri alanları.

Hata çıktısı yalnız JSON alan yolunu ve ihlal türünü gösterir. Yakalanan değer loga, artifacta veya PR yorumuna yazılmaz.

```bash
python alo186/ai-cms/input_guard.py \
  --brief alo186/ai-cms/briefs/<slug>.json
```

Yerel AI üretiminde zorunlu sıra:

```bash
python alo186/ai-cms/cms.py new ...
python alo186/ai-cms/input_guard.py --brief alo186/ai-cms/briefs/<slug>.json
python alo186/ai-cms/cms.py ai-draft --slug <slug>
```

## Anahtar sınırı

- `OPENAI_API_KEY` yalnız GitHub repository secret olarak tutulur.
- Anahtar review branchine, içerik JSON'una, dashboarda, artifacta veya loga yazılmaz.
- Taslak workflow dışında onay ve yayın workflow'ları OpenAI anahtarına erişmez.
- Anahtar en az yetkiyle oluşturulmalı ve 90 günde bir döndürülmelidir.

## GitHub write-token sınırı

- `pull_request_target` kullanılmaz.
- Fork PR üzerinde canonical yayın üreten write-token adımı çalışmaz.
- `/cms approve <slug>` yalnız `OWNER`, `MEMBER` veya `COLLABORATOR` yorumuysa işlenir.
- Branch `ai-cms/*` biçiminde ve aynı repository içinde olmalıdır.
- Onay workflow'u merge yapmaz; son yayın kararı insan merge'idir.

## AI çıktı sınırı

- Responses API çağrısında `store=false` kullanılır.
- Çıktı strict JSON Schema ile sınırlandırılır.
- Model yalnız brief içindeki `S1`, `S2` kaynak özetlerini kullanabilir.
- Modelin yeni URL, mevzuat, sayı, tarih veya standart maddesi uydurması yasaktır.
- AI çıktısı önce `review` durumuna yazılır; canonical HTML veya routing overlay oluşturamaz.

## Yayın güvenliği

Aşağıdaki durumlarda puandan bağımsız yayın durur:

- kaynak yaşı risk sınıfı sınırını aşmışsa,
- high/legal içerikte birincil kaynak yoksa,
- bilinmeyen `sourceRefs` kullanılmışsa,
- canonical rota başka kaynağa aitse,
- benzerlik eşiği `0.78` veya üzerindeyse,
- kişisel iletişim kalıbı bulunursa,
- yasak kesin güvenlik veya resmî kurum iddiası bulunursa,
- high/legal içerikte affiliate CTA açıksa,
- insan editör ve PR onay metadata'sı eksikse,
- kalite puanı 85'in altındaysa.

## Olay müdahalesi

Şüpheli prompt, çıktı veya anahtar sızıntısında:

1. İlgili workflow'u devre dışı bırakın.
2. `OPENAI_API_KEY` anahtarını iptal edip yenisini üretin.
3. AI CMS review branchini ve artifactlarını silin.
4. İlgili commit/PR loglarını secret değerini tekrar yazmadan inceleyin.
5. Canonical yayın oluşmuşsa merge commitini revert edin.
6. Kaynağı, input guard kuralını ve regresyon testini aynı düzeltmede güncelleyin.
