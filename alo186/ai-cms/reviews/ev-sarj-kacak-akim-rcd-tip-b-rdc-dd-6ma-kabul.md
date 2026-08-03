# ALO186 AI CMS inceleme paketi — ev-sarj-kacak-akim-rcd-tip-b-rdc-dd-6ma-kabul

> Bu dosya canonical yayına dahil edilmez. PR incelemesi ve insan onayı için üretilmiştir.

## Durum

- State: **approved**
- Risk: **high**
- Model: **gpt-5.6-thinking**
- Kalite: **88/100**
- Benzerlik: **0.45** — https://www.alo186.com/haberler/ev-sarj-kacak-akim-type-a-type-b-6ma-rdc-dd
- Kelime: **1081**

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
- **S2 · IEC** — [IEC 62955:2018 — RDC-DD for mode 3 EV charging](https://webstore.iec.ch/en/publication/32963) — erişim 2026-08-03 — birincil
- **S3 · IEC** — [IEC 62423:2009 — Type F and Type B RCDs](https://webstore.iec.ch/en/publication/6998) — erişim 2026-08-03 — birincil
- **S4 · Schneider Electric Türkiye** — [EVlink Home dahili 6 mA RDC-DD ve haricî RCD gereği](https://www.se.com/tr/tr/faqs/FAQ000234506/) — erişim 2026-08-03 — birincil
- **S5 · Schneider Electric Türkiye** — [EVlink Pro AC dahili 6 mA RDC-DD davranışı](https://www.se.com/tr/tr/faqs/FAQ000234461/) — erişim 2026-08-03 — birincil

## SEO

- Title: `EV Şarj Kaçak Akım Koruması: Tip B veya 6 mA RDC-DD`
- H1: `EV şarjda Tip B RCD mi, Tip A + 6 mA RDC-DD mi kullanılmalı?`
- Description: `EV şarj devresinde Tip B RCD ile Tip A + 6 mA RDC-DD seçimini, ürün belgesini ve açma testlerini kanıta dayalı kabul edin.`
- Canonical: `/haberler/ev-sarj-kacak-akim-rcd-tip-b-rdc-dd-6ma-kabul`
- Birincil anahtar kelime: `EV şarj kaçak akım rölesi Tip B`

## Doğrudan cevap

EV şarj devresinde yalnız “30 mA kaçak akım rölesi var” demek yeterli değildir. Şarj elektroniğinin oluşturabileceği düzgün DC artık akım için ya uygun Tip B RCD ya da IEC 62955’e uygun 6 mA RDC-DD ile üreticinin istediği Tip A/F RCD koordinasyonu bulunmalıdır. Kabul; tam ürün referansı ve uygunluk belgesi, haricî RCD tipi, PE sürekliliği, açma akımı-süresi, RDC-DD alarm/kesme ve reset davranışının kaydıyla yapılır. Enerjili pano ve şarj ünitesi içindeki testler yalnız yetkin ekipçe gerçekleştirilmelidir.

## Tip B RCD ile Tip A + 6 mA RDC-DD arasındaki karar nasıl verilir?

Mode 3 AC şarj devresinde temel soru yalnız “kaçak akım rölesi var mı?” değildir. Araç ve şarj elektroniği düzgün DC artık akım oluşturabilir; bu akım, uygun DC algılama yoksa bazı AC veya Tip A koruma cihazlarının doğru çalışmasını etkileyebilir. IEC 60364-7-722 EV besleme devrelerini, IEC 62955 ise mode 3 istasyonlarda kullanılan RDC-DD cihazlarını kapsar.

Uygulama iki ana mimariden biriyle kurulur: düzgün DC artık akıma duyarlı Tip B RCD veya şarj cihazında IEC 62955’e uygun 6 mA RDC-DD ile koordineli en az Tip A RCD. Hangi mimarinin geçerli olduğu istasyonun tam ürün referansı, üretici talimatı, proje ve yürürlükteki ulusal kurallarla doğrulanmalıdır; ürün ailesinin başka bir varyantındaki koruma özelliği varsayılamaz.

- Şarj cihazının tam model ve ürün referansını kaydedin.
- Dahili RDC-DD veya Tip B özelliğini sertifika ve kılavuzla doğrulayın.
- Haricî RCD tipi, kutup sayısı, anma akımı ve IΔn değerini tek hatta gösterin.
- Üretici doğrulaması olmadan Tip A’yı tek başına yeterli kabul etmeyin.

_Kaynaklar: S1, S2, S3, S4, S5_

## Dahili 6 mA koruma gerçekten var mı, nasıl belgelenir?

Aynı ticari seri içinde RDC-DD bulunan, Tip B içeren veya haricî koruma isteyen farklı ürün referansları olabilir. Schneider Electric Türkiye’nin EVlink Home açıklaması dahili 6 mA RDC-DD ile birlikte en az 30 mA Tip A RCD gerektiğini; EVlink Pro AC açıklaması ise RDC-DD’nin üründe bulunduğunu ve Tip B içermeyen referanslarda etkin olduğunu belirtir. Bu, marka genellemesi değil ürün-referansı doğrulamasının önemini gösteren üretici örneğidir.

Kabul dosyasında ürün etiketi, seri numarası, donanım ve firmware sürümü, uygunluk beyanı, IEC 62955 kapsamı, haricî RCD şeması ve varsa dahili öz-test davranışı birlikte bulunmalıdır. “Wallbox’ta DC koruma var” şeklindeki satış ifadesi; eşik, açma yöntemi, arıza sonrası reset ve hangi çıkışları koruduğu belgelenmeden kabul kanıtı sayılmamalıdır.

- Uygunluk beyanı ile ürün etiketindeki referansı eşleştirin.
- RDC-DD’nin hangi soket veya konektörü koruduğunu doğrulayın.
- Dahili öz-test sıklığı ve başarısızlık alarmını üretici belgesinden alın.
- Firmware değişiminden sonra koruma davranışını yeniden doğrulayın.

_Kaynaklar: S2, S4, S5_

## RCD ve RDC-DD fonksiyon testi hangi senaryoları kapsamalıdır?

Ön paneldeki TEST düğmesi mekanizmanın temel işlevini kontrol eder; tesis edilmiş devredeki gerçek açma akımı, açma süresi, iletken kutupları, PE sürekliliği ve RDC-DD–RCD koordinasyonunu tek başına kanıtlamaz. Yetkin ekip, üreticinin izin verdiği uyumlu test cihazıyla AC, pulsating DC ve gerekiyorsa düzgün DC senaryolarını uygular; sonuçları modelin beyan edilen koruma mimarisiyle karşılaştırır.

Test; araç bağlı değilken başlangıç kontrolünü, kontrollü şarj sırasında algılama ve kesmeyi, arıza sonrası kilit veya otomatik reset davranışını, enerji kesilip geldiğinde durumu ve şarj ünitesinin hata kaydını kapsamalıdır. Schneider’in EVlink Pro AC belgesinde 6 mA RDC-DD için periyodik otomatik kontrol açıklanır; ancak otomatik öz-test, haricî RCD’nin tesis kabul testinin yerine geçmez.

- Haricî RCD açma akımı ve süresini uygun cihazla kaydedin.
- Dahili RDC-DD alarmı, kontaktör açması ve yeniden başlatma davranışını test edin.
- Test sonucunu EVSE olay kaydı ve kesici durumuyla aynı zaman çizelgesinde gösterin.
- Gerçek arıza üretmek için iletkenleri kısa devre etmeyin veya korumayı köprülemeyin.

_Kaynaklar: S2, S3, S4, S5_

## Şarj sırasında kaçak akım koruması açarsa kök neden nasıl ayrılır?

Açma olayı doğrudan daha yüksek eşikli bir RCD takılarak çözülmemelidir. Araçtan kaynaklanan DC artık akım, EVSE izolasyon arızası, kablo veya fiş hasarı, nem, N-PE karışması, yanlış RCD tipi, toplam tesis kaçak akımı ve seçicilik eksikliği ayrı olasılıklardır. Hata zamanı; araç, konektör, şarj gücü, hava koşulu ve EVSE olay koduyla eşleştirilmelidir.

Üretici arıza prosedürleri bazı RDC-DD olaylarında aracın bağlantısının kesilmesi veya istasyonun kontrollü yeniden enerjilenmesi gibi modele özgü adımlar tanımlar. Kullanıcı yalnız güvenli dış kontrolleri yapmalı; pano, RCD, kontaktör veya EVSE iç devresine müdahale etmemelidir. Aynı araç farklı istasyonda ve aynı istasyon kontrollü test yüküyle yetkin ekipçe karşılaştırılarak arıza katmanı daraltılabilir.

- Olayı araç, kablo, EVSE ve tesis katmanlarına ayırın.
- RCD tipi veya eşik değerini kanıtsız büyütmeyin.
- N-PE karışması ve toplam kaçak akımı ayrı ölçüm planına alın.
- Arıza tekrarlıyorsa istasyonu kapalı tutup yetkili servise yönlendirin.

_Kaynaklar: S1, S4, S5_

## EV şarj kaçak akım koruması hangi kabul dosyasıyla teslim alınmalıdır?

Teslim dosyası; tek hat, besleme ve topraklama sistemi, EVSE tam referansı, IEC uygunluk belgeleri, dahili RDC-DD veya Tip B kanıtı, haricî RCD bilgileri, kısa devre koruması, PE sürekliliği, açma akımı-süresi, RDC-DD alarm/kesme testi, reset davranışı ve imzalı geçti-kaldı sonucunu içermelidir. Her şarj noktası ayrı devre ve ayrı sonuç satırıyla izlenmelidir.

Koruma mimarisi ve test sonuçları uygun ise sırf “Tip B daha pahalı ve daha iyi” düşüncesiyle uyumlu sistemi değiştirmek gerekmez; aynı şekilde 6 mA ifadesi bulunan fakat belgesi ve haricî RCD koordinasyonu eksik cihaz kabul edilmemelidir. CTA: kişisel verisiz EVSE–RCD–RDC-DD kabul matrisini tamamlayın ve yetkin elektrik mühendisi veya devreye alma ekibine iletin.

- Her soket için ürün referansı ve koruma zincirini ayrı yazın.
- Test cihazı, kalibrasyon, akım ve açma süresini rapora ekleyin.
- Proje, üretici talimatı ve saha uygulamasını aynı revizyonda eşleştirin.
- Kanıt yeterliyse gereksiz RCD veya wallbox değişimi satın almayın.

_Kaynaklar: S1, S2, S3, S4, S5_

## Sık sorulan sorular

### EV şarj için her zaman Tip B kaçak akım rölesi gerekir mi?

Hayır. Uygun çözüm, ürün ve proje şartına göre Tip B RCD veya IEC 62955’e uygun 6 mA RDC-DD ile koordineli en az Tip A RCD olabilir. Tam ürün referansı ve üretici talimatı doğrulanmalıdır.

_Kaynaklar: S1, S2, S3, S4_

### Wallbox içinde 6 mA DC koruma varsa haricî RCD gerekmez mi?

Genellikle hayır. Örneğin Schneider EVlink Home dokümanı dahili 6 mA RDC-DD yanında en az 30 mA Tip A RCD ister. Kesin gereklilik ürün kılavuzu, proje ve ulusal kurallardan alınmalıdır.

_Kaynaklar: S4_

### RCD üzerindeki TEST düğmesine basmak kabul için yeterli mi?

Hayır. TEST düğmesi temel mekanizmayı kontrol eder; gerçek açma akımı-süresi, PE sürekliliği, kutuplar ve RDC-DD koordinasyonu uygun test cihazı ve kayıtla doğrulanmalıdır.

_Kaynaklar: S1, S2, S3_

### Şarj sırasında kaçak akım koruması açarsa daha yüksek mA takılır mı?

Kanıtsız olarak hayır. Önce araç, EVSE, kablo, nem, N-PE karışması, yanlış RCD tipi ve toplam kaçak akım kök nedenleri ayrılmalıdır; koruma eşiğini büyütmek tehlikeyi gizleyebilir.

_Kaynaklar: S1, S2, S5_

## İnsan onay komutu

PR sahibinin veya repository yetkilisinin yorumu:

```text
/cms approve ev-sarj-kacak-akim-rcd-tip-b-rdc-dd-6ma-kabul
```

Onay iş akışı kalite puanı, kaynak güncelliği, iç linkler, kanibalizasyon ve risk sınırlarını yeniden çalıştırmadan canonical dosya üretmez.
