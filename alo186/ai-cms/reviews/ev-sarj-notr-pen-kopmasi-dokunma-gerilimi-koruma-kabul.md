# ALO186 AI CMS inceleme paketi — ev-sarj-notr-pen-kopmasi-dokunma-gerilimi-koruma-kabul

> Bu dosya canonical yayına dahil edilmez. PR incelemesi ve insan onayı için üretilmiştir.

## Durum

- State: **approved**
- Risk: **high**
- Model: **gpt-5.6-thinking**
- Kalite: **88/100**
- Benzerlik: **0.43** — https://alo186.com/haberler/ev-sarj-open-pen-kopmasi-opdd-koruma-kabul
- Kelime: **970**

## Kalite kapıları

- ❌ metadata
- ✅ directAnswer
- ✅ contentDepth
- ✅ sources
- ✅ safety
- ✅ internalLinks
- ✅ uniqueness
- ✅ structuredData

### Hatalar

- Yok

### Uyarılar

- Yok

## AI risk notları

- AI ek risk notu üretmedi.

## Kaynaklar

- **S1 · IEC** — [IEC 60364-7-722:2018 — Supplies for electric vehicles](https://webstore.iec.ch/en/publication/29958) — erişim 2026-08-03 — birincil
- **S2 · IEC** — [IEC 61851-1:2017 — Electric vehicle conductive charging system](https://webstore.iec.ch/en/publication/33644) — erişim 2026-08-03 — birincil
- **S3 · IEC** — [IEC 60364-4-41:2005+A1:2017 — Protection against electric shock](https://webstore.iec.ch/en/publication/60169) — erişim 2026-08-03 — birincil
- **S4 · Institution of Engineering and Technology** — [Open combined protective and neutral conductor detection devices — IET 01:2024](https://electrical.theiet.org/guidance-and-codes-of-practice/publications-by-category/electric-vehicles/open-combined-protective-and-neutral-pen-conductor-detection-devices-opdds) — erişim 2026-08-03 — birincil
- **S5 · Institution of Engineering and Technology** — [New standard to ensure safety for electric vehicle charging equipment](https://www.theiet.org/media/press-releases/press-releases-2024/press-releases-2024-october-december/1-october-2024-new-standard-to-ensure-safety-for-electric-vehicle-charging-equipment) — erişim 2026-08-03 — birincil

## SEO

- Title: `EV Şarjda Nötr/PEN Kopması ve Dokunma Gerilimi Koruması`
- H1: `EV şarj noktasında nötr veya PEN kopması riski nasıl kabul edilir?`
- Description: `EV şarjda nötr/PEN kopması riskini, topraklama sistemini, tam kutuplu ayırmayı ve dokunma gerilimi korumasını kanıta dayalı kabul edin.`
- Canonical: `/haberler/ev-sarj-notr-pen-kopmasi-dokunma-gerilimi-koruma-kabul`
- Birincil anahtar kelime: `EV şarj PEN kopması koruması`

## Doğrudan cevap

EV şarj noktasında nötr veya PEN kopması koruması, yalnız wallbox üzerinde ‘PEN koruması var’ etiketi görülerek kabul edilmez. Önce tesisin TT, TN-S veya TN-C-S gibi topraklama ve besleme düzeni doğrulanır; ardından cihazın tam modeline ait koruma yöntemi, hangi iletkenleri ayırdığı, hata algılama sınırları, kontaktör geri bildirimi ve yeniden başlatma davranışı belgelenir. Birleşik PEN iletkeni bulunmayan tesislerde open PEN çözümü otomatik gereklilik değildir. Enerjili EVSE, dağıtım panosu ve ölçüm elektroduna yalnız yetkin ekip müdahale etmelidir.

## Önce TT, TN-S ve TN-C-S/PEN sistemi nasıl ayrılır?

Open PEN arızası, koruma ile nötr işlevinin dağıtım tarafında aynı iletkende birleştiği düzenlerle ilişkilidir. Bu iletken açık devre olurken faz enerjili kalırsa koruma iletkenine bağlı araç gövdesi ve diğer erişilebilir metal bölümler gerçek toprağa göre tehlikeli bir potansiyele taşınabilir. IEC 60364-7-722 EV besleme devrelerinin özel tesis gereklerini, IEC 60364-4-41 ise TN, TT ve IT düzenlerinde elektrik çarpmasına karşı temel korumayı ele alır.

Türkiye’de her tesisin şebeke ve topraklama düzeni aynı değildir. Proje, tek hat, dağıtım şirketi bağlantı bilgisi, ana pano N–PE düzeni ve saha ölçümü birlikte okunmadan tesise ‘PEN var’ veya ‘TT’dir’ denmemelidir. Haricî elektrot bulunması tek başına TT sistemi kanıtlamaz; nötr ve koruma iletkenlerinin hangi noktada ayrıldığı izlenmelidir.

- Tek hat üzerinde şebeke, nötr, PE ve varsa PEN ayrım noktasını gösterin.
- Ana pano ile EVSE arasındaki N ve PE sürekliliğini belgeleyin.
- Toprak elektrodunu sistem tipinin tek kanıtı saymayın.
- Dağıtım şirketi ekipmanına ve mühürlü bölümlere müdahale etmeyin.

_Kaynaklar: S1, S3, S4_

## Koruma cihazının hangi arızayı algıladığı nasıl doğrulanır?

IEC 61851-1, EVSE’nin çalışma koşulları ve elektriksel güvenlik gerekleri için genel çerçeve sağlar. Open PEN algılama cihazları birleşik koruma-nötr iletkenindeki kopmayı algılayıp aracın tehlikeli metal bölümlerini beslemeden ayırmayı amaçlar. IET 01:2024 bu cihazların üretici ve kurulum tarafındaki davranışına yönelik standartlaştırılmış test yaklaşımı sunar; ancak bu Birleşik Krallık kaynağı Türkiye’deki proje ve mevzuatın yerine geçmez.

Kabul dosyasında dahili PEN koruması ifadesinin hangi ölçüm yöntemine dayandığı, tek veya üç fazda geçerli olup olmadığı, haricî referans elektrodu gerektirip gerektirmediği, hata halinde faz ve nötrün birlikte ayrılıp ayrılmadığı ve koruma işlevinin hangi ürün varyantında bulunduğu yazılmalıdır. Aynı marka ailesindeki farklı model veya firmware davranışı varsayılamaz.

- Tam ürün kodu, donanım ve firmware sürümünü kaydedin.
- Algılama yöntemini ve gerekli referans elektrodunu kılavuzdan doğrulayın.
- Hata halinde açılan bütün kutupları ve kontaktör sayısını gösterin.
- Tek faz için tasarlanmış yöntemi üç fazlı tesise genellemeyin.

_Kaynaklar: S2, S4, S5_

## Nötr/PEN arızası fonksiyon testi hangi sınırlarla yapılmalıdır?

Gerçek şebeke PEN iletkenini açmak, nötrü sökmek veya koruma iletkenini kesmek güvenli bir kabul yöntemi değildir. Yetkin ekip, üreticinin tanımladığı test düzeneği veya uygun simülatörle algılama sınırlarını, ayırma süresini ve bütün kutupların durumunu doğrular. Test cihazı, yöntem, kalibrasyon, ölçüm noktası ve ortam koşulu rapora yazılmalıdır.

Senaryo; şarj başlamadan önceki hata, aktif şarj sırasında algılama, kontaktörün açması, CP durumunun sonlandırılması, olay kaydı, arıza devam ederken tekrar kapanmama ve güvenli koşullar döndükten sonraki manuel veya otomatik reset davranışını kapsar. RCD testi ayrıca yapılır; open PEN algılama ile artık akım koruması aynı görev değildir.

- Şebeke nötrünü veya PEN iletkenini sahada rastgele açmayın.
- Üretici onaylı simülasyon ve ölçüm cihazı kullanın.
- Faz, nötr, PE, kontaktör ve CP durumlarını ortak zaman çizelgesinde kaydedin.
- Open PEN fonksiyon testini RCD açma testinin yerine saymayın.

_Kaynaklar: S1, S2, S4, S5_

## Gerilim düşümü veya şebeke dalgalanması yanlış PEN alarmı oluşturabilir mi?

Gerilim tabanlı algılama kullanan bazı çözümler, uzun kablo, yüksek yük, faz dengesizliği veya normal şebeke sınırlarında ortaya çıkan gerilim düşümünden etkilenebilir. Bu nedenle kabul yalnız boşta yapılan tek ölçüme dayanmamalı; düşük, orta ve yüksek şarj gücünde faz-nötr gerilimi, PE’ye göre potansiyel, yük akımı ve alarm durumu birlikte kaydedilmelidir.

Tekrarlayan PEN veya toprak arızası alarmında koruma devre dışı bırakılmamalı ve eşikler deneme-yanılmayla değiştirilmemelidir. Önce besleme sistemi, kablo gerilim düşümü, gevşek nötr, EVSE bağlantısı, referans elektrodu ve ürün firmware’i ayrı ayrı incelenir. Aynı alarmın farklı araçlarla görülmesi tesis/EVSE katmanını araştırmaya yardımcı olabilir; bu karşılaştırma kesin teşhis değildir.

- Farklı şarj güçlerinde gerilim ve alarm trendini kaydedin.
- Gevşek nötr ile gerçek open PEN olayını ayrı kök nedenler olarak inceleyin.
- Koruma eşiklerini yetkisiz biçimde büyütmeyin.
- Tek araç karşılaştırmasını kesin arıza kanıtı olarak sunmayın.

_Kaynaklar: S1, S4, S5_

## EV şarj nötr/PEN koruması hangi kabul dosyasıyla teslim alınmalıdır?

Teslim dosyası; onaylı tek hat, topraklama sistemi, dağıtım besleme düzeni, EVSE tam ürün referansı, koruma standardı veya uygunluk belgesi, algılama yöntemi, haricî elektrot bilgisi, açılan kutuplar, kontaktör geri bildirimi, RCD testleri, hata simülasyonu, reset davranışı ve imzalı geçti-kaldı sonucunu içermelidir. Çoklu şarj noktalarında her çıkış ayrı satırda izlenmelidir.

Tesis TT veya TN-S düzeninde ise sırf piyasada PEN korumalı ürün öne çıkarılıyor diye gereksiz cihaz değişimi yapılmamalıdır. Buna karşılık birleşik PEN riski bulunan düzende yalnız yazılım etiketi veya satış açıklaması yeterli kabul edilmemelidir. CTA: kişisel verisiz şebeke sistemi–EVSE–ayırma–RCD kabul matrisini tamamlayıp yetkin elektrik mühendisine iletin.

- Her EVSE için sistem tipi ve koruma yöntemini ayrı yazın.
- Ürün etiketi, kılavuz ve uygunluk belgesini aynı referansla eşleştirin.
- Fonksiyon testini ölçüm cihazı ve zaman damgasıyla raporlayın.
- Kanıt yeterliyse gereksiz OPDD, elektrot veya wallbox satın almayın.

_Kaynaklar: S1, S2, S3, S4, S5_

## Sık sorulan sorular

### Her EV şarj istasyonunda open PEN koruması gerekir mi?

Hayır. Gereklilik besleme ve topraklama düzenine, ulusal kurallara, proje tasarımına ve EVSE özelliklerine bağlıdır. Birleşik PEN bulunmayan TT veya TN-S düzeninde aynı çözüm otomatik olarak gerekli değildir.

_Kaynaklar: S1, S3, S4_

### Wallbox üzerinde PEN koruması yazması kabul için yeterli mi?

Hayır. Tam ürün varyantı, algılama yöntemi, hangi kutupların ayrıldığı, uygunluk belgesi, firmware ve saha fonksiyon testi birlikte doğrulanmalıdır.

_Kaynaklar: S2, S4, S5_

### PEN testi için nötr kablosu sökülebilir mi?

Hayır. Gerçek nötr veya PEN iletkenini rastgele açmak tehlikelidir. Üretici tarafından tanımlanmış güvenli simülasyon düzeneği ve yetkin ekip kullanılmalıdır.

_Kaynaklar: S1, S2, S4_

### Open PEN koruması varsa RCD’ye gerek kalmaz mı?

Hayır. Open PEN algılama ile artık akım koruması farklı arızalara karşı çalışır. RCD/RDC-DD mimarisi ve açma testleri ayrıca doğrulanmalıdır.

_Kaynaklar: S1, S2, S3_

## İnsan onay komutu

PR sahibinin veya repository yetkilisinin yorumu:

```text
/cms approve ev-sarj-notr-pen-kopmasi-dokunma-gerilimi-koruma-kabul
```

Onay iş akışı kalite puanı, kaynak güncelliği, iç linkler, kanibalizasyon ve risk sınırlarını yeniden çalıştırmadan canonical dosya üretmez.
