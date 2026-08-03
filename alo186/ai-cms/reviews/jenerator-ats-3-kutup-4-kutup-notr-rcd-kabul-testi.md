# ALO186 AI CMS inceleme paketi — jenerator-ats-3-kutup-4-kutup-notr-rcd-kabul-testi

> Bu dosya canonical yayına dahil edilmez. PR incelemesi ve insan onayı için üretilmiştir.

## Durum

- State: **approved**
- Risk: **high**
- Model: **gpt-5.6-thinking**
- Kalite: **88/100**
- Benzerlik: **0.46** — https://alo186.com/haberler/jenerator-ats-3-kutup-4-kutup-anahtarlanan-notr-rcd-teshis
- Kelime: **921**

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

- **S1 · IEC** — [IEC 60947-6-1:2026 — Transfer switching equipment](https://webstore.iec.ch/en/publication/90494) — erişim 2026-08-03 — birincil
- **S2 · Schneider Electric / ASCO** — [Neutral Configurations in Transfer Switches — Data Bulletin](https://www.se.com/us/en/download/document/ASC-DB-NCTS/) — erişim 2026-08-03 — birincil
- **S3 · Schneider Electric / ASCO** — [What neutral configurations are available for ASCO Transfer Switches?](https://www.se.com/us/en/faqs/FAQ000220886/) — erişim 2026-08-03 — birincil
- **S4 · Schneider Electric** — [When to Separately Ground a Backup Generator](https://www.se.com/us/en/work/featured-articles/when-to-separately-ground-backup-generator/) — erişim 2026-08-03 — birincil
- **S5 · Schneider Electric** — [Comparison of Neutral Wire Distribution Options for Data Centers](https://www.se.com/us/en/download/document/SPD_WP41_EN/) — erişim 2026-08-03 — birincil

## SEO

- Title: `Jeneratör ATS’de 3 Kutup–4 Kutup, Nötr ve RCD Kabulü`
- H1: `Jeneratör devreye girince RCD atıyorsa ATS nötrü nasıl doğrulanır?`
- Description: `Jeneratör ATS’sinde 3 veya 4 kutuplu transferi, nötr-toprak bağını ve RCD davranışını şebeke ve jeneratör modlarında kabul edin.`
- Canonical: `/haberler/jenerator-ats-3-kutup-4-kutup-notr-rcd-kabul-testi`
- Birincil anahtar kelime: `jeneratör ATS 4 kutup nötr RCD`

## Doğrudan cevap

Jeneratör devreye girince RCD’nin açması yalnız röle arızası değildir. ATS’nin nötrü anahtarlayıp anahtarlamadığı, jeneratör N–PE bağının yeri, aynı anda oluşan bağ sayısı ve RCD’nin kapsadığı iletkenler birlikte doğrulanmalıdır. 3 veya 4 kutup seçimi tesisin topraklama sistemi ve kaynak düzenine bağlıdır. Kabul; tek hat, kaynak–nötr–toprak matrisi, kontak zamanlaması, iki kaynak modunda RCD açma akımı-süresi ve PE sürekliliğiyle yapılır. Enerjili ATS testini yalnız yetkin ekip yapmalıdır.

## ATS’de 3 kutup ile 4 kutup arasındaki karar nasıl verilir?

Üç kutuplu transferde faz iletkenleri değiştirilirken nötr ortak kalır. Dört kutuplu transferde fazlarla birlikte nötr de kaynaklar arasında anahtarlanır. Doğru seçim yalnız jeneratör gücü veya ATS akımına değil, şebeke ve jeneratör nötrlerinin toprakla hangi noktalarda bağlandığına, jeneratörün ayrı türetilmiş kaynak düzenine ve koruma cihazlarının referansına bağlıdır.

IEC 60947-6-1:2026 transfer anahtarlama cihazlarının güncel performans ve test çerçevesini tanımlar. Üretici teknik kaynakları solid, switched ve overlapping neutral seçeneklerinin farklı sistem sonuçları oluşturduğunu gösterir. Projede 3P veya 4P yazması tek başına yeterli değildir; gerçek saha bağlantısı, nötr kontağı ve kaynak topraklama noktaları birlikte doğrulanmalıdır.

- Şebeke, jeneratör, ATS, ana pano ve RCD’leri tek hat üzerinde gösterin.
- Nötrün ATS üzerinden geçip geçmediğini gerçek ürün kodu ve bağlantıyla doğrulayın.
- Jeneratörün ayrı türetilmiş kaynak olarak tasarlanıp tasarlanmadığını belgeleyin.
- Başka tesisten 3P veya 4P kararını kopyalamayın.

_Kaynaklar: S1, S2, S3, S4, S5_

## Nötr–toprak bağları hangi kaynak modlarında kontrol edilmelidir?

Kabul dosyasında şebeke beslemesi, jeneratör beslemesi, transfer geçişi, bakım bypassı ve varsa UPS bypassı için nötr-toprak bağlantı matrisi oluşturulmalıdır. Aynı anda iki N–PE bağı paralel nötr ve koruma iletkeni akımı oluşturabilir; gerekli bağın hiç oluşmaması ise arıza akımı yolunu ve koruma açmasını bozabilir.

Jeneratör gövde topraklaması ile nötrün toprağa bağlanması aynı işlem değildir. Üretici açıklamaları, nötr anahtarlaması ve ayrı topraklama kararının birlikte ele alınması gerektiğini vurgular. Topraklama elektrodu bulunması, tek başına nötr-toprak düzeninin doğru olduğunu kanıtlamaz; bağlantı noktaları ve iletken yolları fiziksel olarak izlenmelidir.

- Her kaynak modunda aktif N–PE bağ sayısını ayrı yazın.
- PE, nötr, gövde ve elektrot iletkenlerini birbirinden ayırın.
- Bypass ve bakım konumlarını kabul matrisine dahil edin.
- Paralel nötr akımını yalnız pens ölçümüyle değil bağlantı şemasıyla da açıklayın.

_Kaynaklar: S2, S3, S4, S5_

## Nötr kontağının transfer zamanlaması neden önemlidir?

Dört kutuplu ATS’de nötr kontağının fazlardan önce kapanması ve fazlardan sonra açılması gibi davranışlar ürün tasarımına göre değişebilir. Overlapping neutral seçeneğinde nötrler kısa süre örtüşebilir; break-before-make düzeninde iki kaynak nötrü ayrılır. Yanlış varsayım, transfer anında referans kayması, hassas yük kesintisi veya koruma istenmeyen açmasına yol açabilir.

Kabulde kaynak gerilimleri, faz kontakları, nötr kontağı, jeneratör kesicisi, ATS konumu ve kritik yük gerilimi ortak zaman çizelgesine kaydedilmelidir. Ürün kılavuzunda beyan edilen geçiş sırası ve gecikme, saha olay kaydıyla karşılaştırılmalıdır. Nötr kontağına enerjili durumda doğrudan müdahale edilmemelidir.

- Faz ve nötr kontaklarının açma-kapama sırasını üretici belgesinden alın.
- Transfer sırasında kritik yükte minimum RMS gerilimi kaydedin.
- ATS mekanik konumu ile gerçek kontak geri bildirimini karşılaştırın.
- Kontrolsüz kaynak paralellemesi veya nötr köprüleme testi yapmayın.

_Kaynaklar: S1, S2, S3, S5_

## RCD testi şebeke ve jeneratör modlarında nasıl yapılmalıdır?

RCD’nin ön panel TEST düğmesi yalnız temel mekanizmayı sınar; kaynak değişiminde gerçek arıza akımı yolunu, açma süresini ve seçiciliği kanıtlamaz. Yetkin ekip şebeke ve jeneratör modlarında RCD’nin kapsadığı bütün aktif iletkenleri, PE sürekliliğini, açma akımı ve süresini, üst-alt RCD koordinasyonunu ve transfer sonrası reset davranışını ayrı ayrı kaydetmelidir.

Jeneratör modunda RCD açıyor fakat şebekede açmıyorsa nötr-toprak bağı, nötrün RCD dışından dönüşü, paralel nötr, yanlış kutup veya ATS kablolaması araştırılmalıdır. RCD’yi köprülemek, eşik değerini kanıtsız büyütmek veya nötrü PE’ye rastgele bağlamak tehlikeyi gizler. Test, gerçek yük ve üretici prosedürüyle kontrollü yapılmalıdır.

- Her RCD için kaynak modu, IΔn, açma akımı ve süresini tabloya yazın.
- RCD’den geçen faz ve nötr iletkenlerini tek hatla eşleştirin.
- Transfer sonrasında alarm, açma ve yeniden enerjilenme sırasını kaydedin.
- Koruma cihazını köprüleyerek veya rastgele N–PE bağı kurarak deneme yapmayın.

_Kaynaklar: S2, S3, S4_

## ATS nötr ve RCD kabul dosyası nasıl teslim edilmelidir?

Teslim paketi; onaylı tek hat, topraklama sistemi, şebeke ve jeneratör nötr düzeni, ATS tam ürün kodu ve kutup yapısı, kontak zamanlaması, bypass konumları, N–PE matrisi, PE sürekliliği, RCD test sonuçları, transfer gerilim trendi, alarm ve olay kayıtları ile geçti-kaldı sonucunu içermelidir. Her revizyon ve saha değişikliği aynı dosyada izlenmelidir.

Mevcut ATS ve koruma düzeni testlerle doğru çalışıyorsa sırf dört kutup daha güvenlidir düşüncesiyle ekipman değişimi gerekmeyebilir. Aynı şekilde üç kutuplu cihazın nötr-toprak mimarisi kanıtlanmadan yeterli olduğu varsayılmamalıdır. CTA: kişisel verisiz kaynak–ATS–nötr–toprak–RCD kabul matrisini yetkin elektrik mühendisine iletin.

- Ürün etiketi, terminal şeması ve saha bağlantısını aynı revizyonda eşleştirin.
- Şebeke, jeneratör, bypass ve transfer geçişini ayrı sonuç satırlarıyla gösterin.
- Test cihazı ve kalibrasyon bilgilerini rapora ekleyin.
- Kanıt yeterliyse gereksiz ATS veya RCD değişimi satın almayın.

_Kaynaklar: S1, S2, S3, S4, S5_

## Sık sorulan sorular

### Jeneratör için ATS mutlaka 4 kutuplu mu olmalıdır?

Hayır. Doğru kutup sayısı, tesisin topraklama ve nötr düzenine, jeneratörün ayrı türetilmiş kaynak sayılıp sayılmamasına ve koruma mimarisine bağlıdır. Tek hat ve saha bağlantısıyla doğrulanmalıdır.

_Kaynaklar: S1, S2, S3, S4_

### 3 kutuplu ATS’de jeneratör nötrü ortak kalabilir mi?

Bazı tasarımlarda evet; ancak ortak nötrün N–PE bağları ve RCD akım yollarıyla uyumu kanıtlanmalıdır. Paralel nötr veya çift bağ oluşmamalıdır.

_Kaynaklar: S2, S3, S4_

### Jeneratör devreye girince RCD atarsa röle değiştirilir mi?

Önce nötr anahtarlaması, N–PE bağları, nötrün RCD dışından dönüşü, kablolama ve gerçek kaçak akım ayrılmalıdır. Kök neden kanıtlanmadan RCD değişimi veya eşik büyütme yapılmamalıdır.

_Kaynaklar: S2, S3, S4_

### RCD TEST düğmesi jeneratör modunun güvenli olduğunu kanıtlar mı?

Hayır. Şebeke ve jeneratör modlarında uygun test cihazıyla açma akımı-süresi, PE sürekliliği ve seçicilik ayrı doğrulanmalıdır.

_Kaynaklar: S1, S2, S3_

## İnsan onay komutu

PR sahibinin veya repository yetkilisinin yorumu:

```text
/cms approve jenerator-ats-3-kutup-4-kutup-notr-rcd-kabul-testi
```

Onay iş akışı kalite puanı, kaynak güncelliği, iç linkler, kanibalizasyon ve risk sınırlarını yeniden çalıştırmadan canonical dosya üretmez.
