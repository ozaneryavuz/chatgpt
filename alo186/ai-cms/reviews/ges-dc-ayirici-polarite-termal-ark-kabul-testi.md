# ALO186 AI CMS inceleme paketi — ges-dc-ayirici-polarite-termal-ark-kabul-testi

> Bu dosya canonical yayına dahil edilmez. PR incelemesi ve insan onayı için üretilmiştir.

## Durum

- State: **approved**
- Risk: **high**
- Model: **gpt-5.6-thinking**
- Kalite: **88/100**
- Benzerlik: **0.15** — https://alo186.com/haberler/ges-inverter-reverse-polarity-ters-kutup-string-polarite-teshis
- Kelime: **992**

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

- **S1 · IEC** — [IEC 60947-3:2020+AMD1:2025 — Switches and switch-disconnectors](https://webstore.iec.ch/en/publication/107159) — erişim 2026-08-03 — birincil
- **S2 · IEC** — [IEC 62548-1:2023+AMD1:2025 — Photovoltaic array design requirements](https://webstore.iec.ch/en/publication/110893) — erişim 2026-08-03 — birincil
- **S3 · IEC** — [IEC 60364-7-712:2025 — Solar photovoltaic power supply installations](https://webstore.iec.ch/en/publication/65748) — erişim 2026-08-03 — birincil
- **S4 · IEC** — [IEC 62446-1:2016+A1:2018 — PV documentation, commissioning tests and inspection](https://webstore.iec.ch/en/publication/63726) — erişim 2026-08-03 — birincil
- **S5 · IEC** — [IEC TS 62446-3:2017 — Outdoor infrared thermography of PV plants](https://webstore.iec.ch/en/publication/28628) — erişim 2026-08-03 — birincil
- **S6 · Schneider Electric** — [Acti9 C60NA-DC, C120NA-DC and SW60-DC PV switch-disconnectors](https://www.se.com/ie/en/product-range/61516-c60nadc/) — erişim 2026-08-03 — birincil

## SEO

- Title: `GES DC Ayırıcı Polarite, Termal Isınma ve Ark Kabul Testi`
- H1: `GES DC ayırıcı polaritesi, ısınması ve ark riski nasıl kabul edilir?`
- Description: `GES DC ayırıcıyı Voc/Isc, kutup bağlantısı, polarite, tork, termal görüntü ve izolasyon kanıtlarıyla kabul edin; AC şalteri veya rastgele aç-kapa testi kullanmayın.`
- Canonical: `/haberler/ges-dc-ayirici-polarite-termal-ark-kabul-testi`
- Birincil anahtar kelime: `GES DC ayırıcı arızası ve kabul testi`

## Doğrudan cevap

GES DC ayırıcı kabulü, kolun OFF konumuna gelmesiyle tamamlanmaz. Cihazın PV için uygun DC gerilim ve akım sınıfı, kutup bağlantı şeması, polarite hassasiyeti, seri bağlanan kontaklar, soğukta maksimum açık devre gerilimi, kısa devre akımı, kablo kesiti, terminal torku ve muhafaza koşulları birlikte doğrulanmalıdır. Temsilî üretimde giriş-çıkış terminalleri ve komşu ekipman termal olarak karşılaştırılmalı; renk değişimi, koku, gevşeklik, ark izi veya dengesiz sıcaklık varsa ayırıcı yük altında kullanıcı tarafından çevrilmemeli, sistem yetkin ekipçe güvenli biçimde izole edilmelidir.

## DC ayırıcı neden yalnız amper değerine göre seçilemez?

PV dizileri gündüz boyunca gerilim üretir ve DC arkı AC'deki gibi her yarım periyotta doğal olarak sönmez. Bu nedenle bir AC şalter veya yalnız nominal amperi uygun görünen cihaz, PV DC ayırma görevi için yeterli değildir. IEC 60947-3, 1 500 V DC'ye kadar switch-disconnector cihazlarının karakteristik ve test çerçevesini; IEC 62548-1 ve IEC 60364-7-712 ise PV tesisatında seçim ve uygulama gerekliliklerini ele alır.

Dosyada cihazın tam model kodu, IEC/EN standardı, DC-PV kullanım amacı, Ue/Uimp, Ie, kullanım kategorisi, kutup sayısı, seri/parallel bağlantı şeması, koşullu kısa devre değeri ve üretici sıcaklık derating bilgileri bulunmalıdır. İnverter üzerindeki dahili ayırıcı ile haricî dizi ayırıcının görevleri de ayrı yazılmalıdır.

- Cihaz etiketinde DC-PV uygulamasını ve standardı doğrulayın.
- Soğuk koşuldaki maksimum Voc ile cihazın Ue değerini karşılaştırın.
- Düzeltilmiş Isc ve sürekli akım koşulunu ürün tablosuyla eşleştirin.
- Dahili inverter ayırıcısı ile sahadaki haricî ayırıcıyı ayrı envanterleyin.

_Kaynaklar: S1, S2, S3, S4_

## Polarite ve kutup bağlantısı nasıl kanıtlanmalıdır?

Bazı DC switch-disconnector cihazları polariteye duyarlı değildir; bazıları ise (+) ve (-) yönünün veya kutupların seri bağlantı sırasının kesin olarak izlenmesini ister. Schneider'in PV ayırıcı ürün bilgisinde aynı ürün ailesinde non-polarized modeller ile polariteye duyarlı SW60-DC'nin ayrıldığı görülür. Bu nedenle aynı fiziksel görünüş veya kol yönü doğru bağlantıyı kanıtlamaz.

Üretici bağlantı şeması sahadaki kablo güzergâhı ve terminal numaralarıyla birebir karşılaştırılmalıdır. Birden çok kutbun seri kullanıldığı yüksek DC gerilim uygulamalarında köprülerin yeri, akım yönü, giriş-çıkış terminalleri ve her iki iletkenin ayrılması açıkça işaretlenmelidir. Polarite kontrolü enerjili terminallere kullanıcı müdahalesiyle değil, yetkili ölçüm ve izolasyon prosedürüyle yapılmalıdır.

- Üretici şemasını pano içine kalıcı ve okunabilir biçimde ekleyin.
- Kutup köprülerini ve akım yönünü fotoğrafla belgeleyin.
- Pozitif ve negatif iletken etiketlerini dizi planıyla eşleştirin.
- Model değişiminde eski cihazın bağlantı şemasını yeni cihaza kopyalamayın.

_Kaynaklar: S1, S2, S4, S6_

## Terminal torku, kablo ve muhafaza koşulları neden kritiktir?

Yanlış kablo kesiti, uyumsuz pabuç, eksik soyma boyu, gevşek tork, mekanik çekme veya su girişi temas direncini artırarak yerel ısınma ve karbonlaşma oluşturabilir. Ayırıcı kabini dış ortamdaysa IP sınıfı, UV dayanımı, yoğuşma, rakor yönü, drenaj, güneş yükü ve pano içi sıcaklık ürün sınırlarıyla birlikte kontrol edilmelidir.

Kurulum kaydında kablo tipi-kesiti, terminal/pabuç kodu, üretici torku, kullanılan kalibre tork aleti, tarih ve uygulayan kişi yer almalıdır. Bağlantıdan sonra gelişigüzel yeniden sıkma yerine üretici prosedürü izlenmeli; enerjili DC terminallerde kontrol veya tork işlemi yapılmamalıdır.

- Kablo ve pabuç uyumunu cihaz üreticisi verisiyle doğrulayın.
- Her terminal için hedef ve uygulanan torku kaydedin.
- Rakor, sızdırmazlık, yoğuşma ve mekanik kablo yükünü kontrol edin.
- Pano içi sıcaklık ve güneş yükü için derating gereğini değerlendirin.

_Kaynaklar: S1, S2, S3, S4, S6_

## Termal inceleme ve ayırma fonksiyonu nasıl kabul edilir?

IEC 62446-1 devreye alma, muayene ve teslim dokümantasyonu için çerçeve sunar; IEC TS 62446-3 ise PV tesislerinde dış ortam termografisinin ekipman, çevre koşulu, prosedür, rapor ve personel yeterliliğini tanımlar. Termal karşılaştırma benzer ışınım ve akım koşullarında, ayırıcının giriş-çıkış terminalleri, kutupları ve komşu bağlantıları arasında yapılmalıdır.

Ayırıcıyı defalarca yük altında açıp kapatmak bir bakım testi değildir ve ark riskini artırabilir. Fonksiyon testi üreticinin izin verdiği işletme koşulunda, onaylı manevra planı ve uygun kişisel koruma ile yetkin ekip tarafından yapılmalıdır. Kolu OFF konumunda olsa bile PV tarafı gündüz enerjili kalabileceğinden, bakım izolasyonu her iki tarafta gerilim yokluğu ve kilitleme-etiketleme ile doğrulanmalıdır.

- Termal görüntüye ışınım, akım, ortam ve pano sıcaklığını ekleyin.
- Benzer kutuplar arasında sıcaklık farkını ve trendini değerlendirin.
- Ark izi, kararma veya olağan dışı ısınmada cihazı kullanıcıya çalıştırmayın.
- OFF konumunu gerilimsizlik kanıtı veya LOTO yerine kullanmayın.

_Kaynaklar: S1, S2, S4, S5_

## GES DC ayırıcı kabul dosyasında hangi kanıtlar bulunmalıdır?

Teslim dosyası; tek hat ve dizi planı, cihaz model/veri sayfası, soğuk Voc ve düzeltilmiş Isc hesabı, kutup-polarite şeması, terminal ve kablo listesi, tork kayıtları, muhafaza/IP kontrolleri, etiket-fotoğraflar, temsilî yükte termal görüntüler, izolasyon ve fonksiyon testi, sapma listesi ve imzalı geçti-kaldı tablosunu içermelidir.

IEC 62548-1'in güncel konsolide sürümü PV dizilerinde kablolama, koruma, switching ve isolation hükümlerini birlikte ele alır. Mevcut ayırıcı model, bağlantı ve termal kabulü kanıtla geçiyorsa sırf daha yeni bir kutu veya marka satın almak gerekmez; fakat polarite hatası, uygunsuz AC cihaz, hasarlı terminal veya ark izi varsa yalnız kolu değiştirmek yeterli onarım sayılmamalıdır.

- Hesap ile cihaz etiketi ve gerçek kablo bağlantısını aynı dosyada eşleştirin.
- Termal görüntüleri normal yük ve çevre koşullarıyla birlikte saklayın.
- Her düzeltmeden sonra tork, izolasyon ve termal yeniden kabul planlayın.
- Kanıt yeterliyse gereksiz ayırıcı veya pano değişimi yapmayın.

_Kaynaklar: S1, S2, S3, S4, S5, S6_

## Sık sorulan sorular

### AC şalter GES DC ayırıcı olarak kullanılabilir mi?

Yalnız fiziksel olarak açıp kapatması yeterli değildir. Cihaz PV DC gerilim, akım, kullanım kategorisi, kutup bağlantısı ve ark söndürme performansı için uygun ve üretici tarafından bu uygulamaya onaylı olmalıdır.

_Kaynaklar: S1, S2, S3_

### DC ayırıcı OFF konumundayken panel tarafı gerilimsiz olur mu?

Genellikle PV dizi tarafı ışık varken gerilim üretmeye devam eder. OFF yalnız tanımlı devreyi ayırır; bakım için bütün kaynaklar, her iki tarafın gerilim durumu ve LOTO yetkin personelce doğrulanmalıdır.

_Kaynaklar: S2, S3, S4_

### DC ayırıcı neden ısınır?

Uyumsuz cihaz veya akım değeri, yanlış polarite/kutup bağlantısı, gevşek terminal, uygunsuz pabuç, yüksek pano sıcaklığı, su/yoğuşma, mekanik kablo yükü veya iç kontak aşınması neden olabilir. Termal görüntü tek başına kök nedeni göstermez; bağlantı ve ürün verisiyle birlikte incelenmelidir.

_Kaynaklar: S1, S2, S5, S6_

### DC ayırıcıyı test etmek için birkaç kez açıp kapatmak doğru mudur?

Rastgele ve yük altında tekrarlı anahtarlama güvenli bir test yöntemi değildir. Üretici prosedürü, izin verilen anahtarlama koşulu, onaylı manevra planı ve yetkin ekip gerekir.

_Kaynaklar: S1, S2, S4_

## İnsan onay komutu

PR sahibinin veya repository yetkilisinin yorumu:

```text
/cms approve ges-dc-ayirici-polarite-termal-ark-kabul-testi
```

Onay iş akışı kalite puanı, kaynak güncelliği, iç linkler, kanibalizasyon ve risk sınırlarını yeniden çalıştırmadan canonical dosya üretmez.
