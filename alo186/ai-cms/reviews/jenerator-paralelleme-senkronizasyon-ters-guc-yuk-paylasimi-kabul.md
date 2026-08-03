# ALO186 AI CMS inceleme paketi — jenerator-paralelleme-senkronizasyon-ters-guc-yuk-paylasimi-kabul

> Bu dosya canonical yayına dahil edilmez. PR incelemesi ve insan onayı için üretilmiştir.

## Durum

- State: **approved**
- Risk: **high**
- Model: **gpt-5.6-thinking**
- Kalite: **88/100**
- Benzerlik: **0.23** — https://www.alo186.com/haberler/jenerator-ters-guc-reverse-power-alarmi-ansi-32
- Kelime: **892**

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

- **S1 · DEIF** — [AGC 150 — Dynamic Synchronisation](https://documentation.deif.com/r/agc-150-generator-mains-btb-designers-handbook-4189341307-uk/generator-functions/dynamic-synchronisation) — erişim 2026-08-03 — birincil
- **S2 · DEIF** — [AGC 150 — Function Overview](https://documentation.deif.com/r/agc-150-generator-mains-btb-designers-handbook-4189341307-uk/introduction/about/function-overview) — erişim 2026-08-03 — birincil
- **S3 · DEIF** — [AGC 150 — Reverse Power ANSI 32R](https://documentation.deif.com/r/agc-150-generator-mains-btb-designers-handbook-4189341307-uk/ac-protections/generator-protections/reverse-power-ansi-32r) — erişim 2026-08-03 — birincil
- **S4 · Cummins** — [Generator Set Controls](https://www.cummins.com/en-in/generators/generator-set-controls) — erişim 2026-08-03 — birincil

## SEO

- Title: `Jeneratör Paralelleme Testi: Senkronizasyon ve Ters Güç`
- H1: `Jeneratör paralelleme, senkronizasyon ve ters güç korumasıyla nasıl kabul edilir?`
- Description: `Jeneratör paralellemesini faz sırası, senkron kapanma, kW-kVAr yük paylaşımı ve ANSI 32R ters güç testiyle kanıta dayalı kabul edin.`
- Canonical: `/haberler/jenerator-paralelleme-senkronizasyon-ters-guc-yuk-paylasimi-kabul`
- Birincil anahtar kelime: `jeneratör paralelleme senkronizasyon ters güç testi`

## Doğrudan cevap

Jeneratör paralelleme kabulü, senkron rölesinin kesiciyi bir kez kapatmasıyla tamamlanmaz. Faz sırası, gerilim ve frekans farkı, faz açısı, slip frekansı ve kesici kapanma süresi üretici ayarlarıyla doğrulanmalı; kapanma sonrası aktif gücün governor, reaktif gücün AVR tarafından kararlı ve doğru yönde paylaşılması izlenmelidir. Ardından CT polaritesi, kesici geri bildirimi, ters güç ANSI 32R, düşük/yüksek uyarım, haberleşme kaybı, yük atma ve yeniden transfer senaryoları kontrollü biçimde test edilip tek zaman çizelgesinde kaydedilmelidir.

## Paralelleme testinden önce hangi sistem sınırları tanımlanmalıdır?

Önce paralel çalışmanın iki jeneratör arasında mı, jeneratör ile şebeke arasında mı, yoksa birden fazla bara ve bus-tie kesicisiyle mi yapılacağı belirlenmelidir. Her senaryoda güç akış yönü, izin verilen işletme modu, şebekeye ihracat sınırı, nötr-toprak düzeni ve koruma sorumluluğu farklı olabilir.

Tek hat, CT/VT oranları ve polariteleri, kesici yardımcı kontakları, governor ve AVR kontrol tipi, kontrolör yazılım sürümü, haberleşme topolojisi ve kilitlemeler test öncesinde dondurulmalıdır. Yanlış CT yönü veya kesici geri bildirimi senkron kapanma doğru olsa bile güç yönü ve koruma hesaplarını ters gösterebilir.

- Paralel kaynakları ve bütün kesici sınırlarını tek hatta işaretleyin.
- İzin verilen ada, şebekeye paralel ve yük transfer modlarını ayırın.
- CT/VT oranı, polarite ve faz eşleşmesini enjeksiyonla doğrulayın.
- Governor, AVR ve kontrolör sürümlerini kabul dosyasına kaydedin.

_Kaynaklar: S1, S4_

## Senkron kapanma hangi ölçümlerle kabul edilmelidir?

Senkronizasyon; faz sırasının eşleşmesi, iki kaynak gerilimlerinin uygun aralıkta olması, frekans farkı ve faz açısının kesici kapanma anında üretici sınırları içinde kalmasıyla sağlanır. Dinamik senkronizasyonda slip frekansı ve kesicinin mekanik kapanma süresi hesaba katılarak komut, hedef faz çakışmasından önce verilir.

Tek bir başarılı kapanma yeterli değildir. Soğuk motor, sıcak motor, farklı yük seviyeleri ve mümkünse her kaynak yönü için tekrarlı kapanmalar yapılmalı; komut anı, ana kontak kapanma anı, faz açısı, slip, gerilim farkı ve ilk kW-kVAr darbesi yüksek çözünürlüklü olay kaydında karşılaştırılmalıdır.

- Faz sırasını ve ölçü trafosu faz eşleşmesini doğrulayın.
- Kesici kapanma süresini ölçüp kontrolör kompanzasyonuna bağlayın.
- Farklı başlangıç koşullarında tekrarlı senkron kapanma yapın.
- İlk aktif ve reaktif güç darbesini kabul sınırıyla kaydedin.

_Kaynaklar: S1, S2_

## Aktif ve reaktif yük paylaşımı neden ayrı test edilmelidir?

Paralel çalışmada aktif güç paylaşımı esas olarak motor governor ve hız kontrolüyle, reaktif güç paylaşımı ise AVR, gerilim droop veya reaktif güç kontrolüyle yönetilir. kW paylaşımının düzgün olması kVAr paylaşımının da doğru olduğu anlamına gelmez. Dolaşan reaktif akım, bir alternatörü aşırı uyarırken diğerini düşük uyarımda bırakabilir.

Yük basamakları minimum kararlı yükten hedef işletme yüküne kadar artırılmalı; her kademede kW, kVAr, güç faktörü, akım, frekans, gerilim, egzoz sıcaklığı ve kontrol çıkışları trendlenmelidir. Haberleşmeli load-share hattı kesildiğinde sistemin droop veya güvenli ayırma davranışına geçtiği doğrulanmalıdır.

- kW ve kVAr paylaşım hatalarını ayrı yüzdelerle raporlayın.
- Düşük, orta ve yüksek yük basamaklarında kararlılığı izleyin.
- Load-share haberleşme kaybı ve sensör sapması senaryosu uygulayın.
- Dolaşan reaktif akım ve aşırı/düşük uyarım alarmlarını kontrol edin.

_Kaynaklar: S2, S4_

## ANSI 32R ters güç koruması nasıl güvenli test edilmelidir?

Ters güç, mekanik tahrik gücü kaybolduğunda alternatörün şebekeden veya diğer jeneratörlerden aktif güç çekerek motor gibi çalışmasına işaret edebilir. DEIF dokümanlarında 32R fonksiyonu, tüm fazlardan kaynağa doğru ölçülen aktif güce dayalıdır. Üretici ekranındaki örnek varsayılan değerler bütün motor ve tesisler için evrensel ayar değildir.

Fonksiyon testi; onaylı proje ayarı, motor üreticisi limiti, CT polaritesi ve gerçek güç yönü doğrulandıktan sonra ikincil enjeksiyon veya kontrollü yük azaltma yöntemiyle yetkin ekipçe yapılmalıdır. Trip komutu, jeneratör kesicisinin açması, motorun güvenli soğutma/durdurma dizisi ve olay zamanları birlikte kaydedilmelidir.

- 32R ayarını motor ve alternatör üretici verisine bağlayın.
- CT polaritesi ve aktif güç işaretini testten önce doğrulayın.
- İkincil enjeksiyon veya kontrollü saha test yöntemini risk analizine göre seçin.
- Trip, kesici açma ve motor durdurma zamanlarını aynı kayıtta gösterin.

_Kaynaklar: S3, S4_

## Tam yük transfer ve yeniden dönüş testi hangi kanıtları içermelidir?

Basit test yalnız jeneratörü çalıştırabilir; tam kabul ise kaynağı senkronize eder, yükü aktarır, belirli süre yükte tutar, şebekeyi yeniden senkronize eder, yükü geri aktarır ve jeneratörü boşta soğutup durdurur. Bu akış sırasında koruma, kilitleme, breaker failure, acil stop ve haberleşme kaybı senaryoları da doğrulanmalıdır.

Kabul dosyasında tek hat, ayar listesi, senkron kapanma kayıtları, yük paylaşım grafikleri, 32R testi, alarm ve olay kayıtları, kesici zamanları, yakıt ve sıcaklık trendleri ile kapanış maddeleri bulunmalıdır. Mevcut kontrol sistemi bütün senaryoları karşılıyorsa yalnız daha yeni kontrolör almak için değişim yapılmamalıdır.

- Basit, yükte ve tam transfer testlerini ayrı sınıflandırın.
- Şebeke dönüşü ve yük geri transferini gerçek sıralamayla test edin.
- Kesici açmama, haberleşme kaybı ve acil stop sonuçlarını kaydedin.
- Kanıt yeterliyse gereksiz kontrolör veya paralelleme panosu satın almayın.

_Kaynaklar: S1, S3, S4_

## Sık sorulan sorular

### İki jeneratörün voltajı ve frekansı aynıysa paralel bağlanabilir mi?

Tek başına yeterli değildir. Faz sırası, faz açısı, slip frekansı, kesici kapanma süresi, ölçü trafosu eşleşmesi, kilitlemeler ve kapanma sonrası güç paylaşımı da doğrulanmalıdır.

_Kaynaklar: S1, S2_

### Ters güç rölesi yüzde kaç ayarlanmalıdır?

Bütün jeneratörler için geçerli tek bir yüzde yoktur. Motor üreticisinin ters güç dayanımı, tesis işletme modu, CT doğruluğu, geçici yük olayları ve koruma koordinasyonu esas alınmalıdır; kontrolörün fabrika örneği doğrudan proje ayarı değildir.

_Kaynaklar: S3_

### kW paylaşımı düzgünse neden kVAr dolaşımı oluşabilir?

Aktif güç governor tarafından, reaktif güç ise AVR ve gerilim/droop kontrolü tarafından yönetilir. AVR ayarı, gerilim ölçümü veya reaktif load-share hattı uyumsuzsa kW eşitken kVAr dengesiz olabilir.

_Kaynaklar: S2, S4_

### Jeneratör test modunda çalıştıysa paralelleme kabul edilmiş olur mu?

Hayır. Basit test yalnız çalıştırma yapabilir. Tam kabul; senkronizasyon, yük aktarımı, kararlı paylaşım, koruma fonksiyonları, şebekeye yeniden senkron ve yük geri transferi gibi senaryoları kapsamalıdır.

_Kaynaklar: S1, S4_

## İnsan onay komutu

PR sahibinin veya repository yetkilisinin yorumu:

```text
/cms approve jenerator-paralelleme-senkronizasyon-ters-guc-yuk-paylasimi-kabul
```

Onay iş akışı kalite puanı, kaynak güncelliği, iç linkler, kanibalizasyon ve risk sınırlarını yeniden çalıştırmadan canonical dosya üretmez.
