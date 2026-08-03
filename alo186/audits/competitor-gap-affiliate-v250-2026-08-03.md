# ALO186 Competitor-Gap & Affiliate Optimization v250

**Tarih:** 3 Ağustos 2026  
**Kapsam:** Semantik soru–sorun–çözüm–ürün grafiği, 81 il ve EDAŞ hizmet şemaları, güvenlik kapılı Amazon Türkiye bağlantıları, JS’siz taranabilir kaynak ve AI crawler politikası.

## 1. Uygulanan mimari

### 1.1 Kesintide kombi nasıl korunur?

Kombi uygunluk rehberi ve ürün seçici production build sırasında ortak bir semantik grafiğe bağlanır:

- `Question`: “Kesintide kombi nasıl korunur?”
- `HowTo`: aktif tehlike ayrımı, tam model onayı, gerçek W/VA/Wh ihtiyacı, cihaz sınıfı seçimi, gerçek kesinti testi ve satın almama sonucu
- `ItemList`: teknik göreve göre sıralanan üç cihaz sınıfı
- `Product`: saf sinüs UPS sınıfı, EPS özellikli güç istasyonu sınıfı ve priz tipi enerji ölçer sınıfı

`Product` düğümleri belirli ürün veya sabit güç önerisi değildir. `urun-ups-3000va` ismi yalnız istenen kararlı HTML ankrajıdır; 3000 VA önerisi değildir. Fiyat, stok, satıcı, puan, yorum, teslimat, garanti, `Offer` ve `AggregateRating` yayımlanmaz.

### 1.2 İl ve EDAŞ hizmet ayrımı

Özel dağıtım şirketleri yanlış biçimde kamu kurumu olarak işaretlenmez:

- Yetkili EDAŞ: `Organization`
- 186 kesinti ve dağıtım şebekesi arıza kanalı: `Service`
- Aktif can güvenliği tehlikesinde 112: `GovernmentService`
- Doğru iletişim sırası: `ItemList`
- “Bu ilde elektrik kesintisi için nere aranır?” doğrudan cevabı: `Question`

Bu model, 81 il sayfası ile en az 21 EDAŞ rehberinin final canonical artifactına uygulanır. EDAŞ resmî kesinti kanalı sayfadaki görünür ve doğrulanmış resmî bağlantıdan türetilir.

### 1.3 Akıllı affiliate ankrajları

Düşük riskli ve teknik uygunluk odaklı iki rehbere statik Amazon Türkiye bağlantıları eklenir:

- `id="urun-kesintisiz-guc-kaynagi"`
- `id="urun-asiri-gerilim-korumasi"`

Bütün bağlantılar:

- yalnız `amazon.com.tr` alanına gider,
- `alo186rehber-21` satış ortaklığı etiketini taşır,
- `rel="sponsored nofollow noopener"` kullanır,
- bağlantıdan önce veya aynı blokta görünür satış ortaklığı açıklaması taşır,
- aktif tehlike, arıza bildirimi veya teknik uygunluk belirlenmemiş kullanıcı akışlarında önerilmez.

### 1.4 SSR / statik kaynak sözleşmesi

ALO186 GitHub Pages üzerinde statik server-rendered HTML yayımlar. Final kaynak kodunda:

- “ALO186 Akıllı Yol” görünür metin olarak bulunur,
- “Kişisel hazırlık kontrolü” görünür metin olarak bulunur,
- kombi adımları ve üç ürün sınıfı görünür HTML olarak bulunur,
- üç Amazon Türkiye bağlantısının gerçek `href` değeri kaynak kodda bulunur.

Kullanıcı güvenliği için kombi Amazon bağlantıları ilk durumda `aria-disabled="true"`, `tabindex="-1"` ve `pointer-events:none` ile kilitlidir. Bağlantılar yalnız şu koşulların tamamında açılır:

1. Tam kombi modeli için yazılı üretici/servis onayı doğrulanmıştır.
2. Mevcut güvenli sistem ihtiyacı karşılamamaktadır.
3. Gaz/CO, yanık kokusu, ısınan priz, su teması, baca-havalandırma veya sabit tesisat tehlikesi yoktur.
4. Üç ayrı satın almama, teknik uygunluk ve satış ortaklığı onayı tamamlanmıştır.

Böylece botlar JS çalıştırmadan bağlamı ve bağlantıları okuyabilir; kullanıcı ise güvenlik kapısını atlayarak doğrudan mağazaya gidemez.

## 2. Robots ve AI crawler politikası

`robots.txt` içinde aşağıdaki crawler grupları ayrı ve açık `Allow: /` kuralıyla tanımlanır:

- `OAI-SearchBot`
- `GPTBot`
- `ChatGPT-User`
- `PerplexityBot`
- `ClaudeBot`
- `anthropic-ai`
- `Bytespider`
- `Google-Extended`

Genel `User-agent: * / Allow: /` ve apex canonical sitemap kayıtları korunur.

## 3. Schema ve Rich Results doğrulama yaklaşımı

### Deterministik Schema.org sözleşmesi

CI final production bundle üzerinde şunları fail-closed doğrular:

- her v250 JSON-LD bloğunun geçerli JSON olması,
- 81+ il ve 21+ EDAŞ sayfasının gerekli düğümleri taşıması,
- özel EDAŞ’ın `GovernmentService` olarak işaretlenmemesi,
- 112 `GovernmentService` düğümünün 112 kanalını taşıması,
- 186 `Service` düğümünün 186 kanalını taşıması,
- kombi grafiğinde `Question`, `HowTo`, `HowToStep`, `ItemList` ve üç `Product` bulunması,
- yasak dinamik ticari alanların bulunmaması,
- Amazon Türkiye alanı, affiliate etiketi ve rel niteliklerinin eksiksiz olması,
- SSR metin ve bağlantıların script dışındaki HTML kaynakta bulunması,
- robots crawler gruplarının açık olması.

Makine tarafından okunabilir sonuç `alo186-competitor-gap-affiliate-v250-validation` workflow artifactında yayımlanır.

### Google Rich Results sınırı

Schema Markup Validator genel Schema.org kelime dağarcığını doğrular. Google Rich Results Test yalnız Google’ın güncel olarak desteklediği arama görünümü türlerini değerlendirir. `HowTo` Google arama rich result türü olarak artık desteklenmediği için Schema.org açısından geçerli olsa da Rich Results Test’te ayrı zengin sonuç olarak görünmesi beklenmez.

Genel `Product` düğümleri de bilerek `Offer`, fiyat, stok, puan veya yorum içermediğinden Merchant/Product rich result uygunluğu iddia edilmez. Amaç yapay zekâ arama motorlarına problem–çözüm–cihaz sınıfı ilişkisini doğru ve güvenli vermektir. Geçerli structured data, Google veya herhangi bir AI motorunda görünürlük ya da kaynak gösterme garantisi değildir.

## 4. Birincil teknik kaynaklar

- Schema.org HowTo: https://schema.org/HowTo
- Schema.org Product: https://schema.org/Product
- Schema.org ItemList: https://schema.org/ItemList
- Schema.org Organization: https://schema.org/Organization
- Schema.org GovernmentService: https://schema.org/GovernmentService
- Google Search structured data gallery: https://developers.google.com/search/docs/appearance/structured-data/search-gallery
- Google structured data general guidelines: https://developers.google.com/search/docs/appearance/structured-data/sd-policies
- Google HowTo/FAQ rich result change: https://developers.google.com/search/blog/2023/08/howto-faq-changes
- OpenAI crawler documentation: https://platform.openai.com/docs/bots

## 5. Kabul komutu

```bash
python alo186/tests/test_competitor_gap_affiliate_v250.py \
  --bundle /tmp/alo186-v250-site \
  --report /tmp/alo186-v250-validation.json
```

Kabul yalnız canonical build, static smoke, v191 kombi güven regresyonu ve v250 sözleşmelerinin tamamı geçtiğinde başarılıdır.
