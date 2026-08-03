# ALO186 AI CMS inceleme paketi — ups-cikis-kisa-devre-akimi-selektivite-kesici-kabul

> Bu dosya canonical yayına dahil edilmez. PR incelemesi ve insan onayı için üretilmiştir.

## Durum

- State: **approved**
- Risk: **high**
- Model: **gpt-5.6-thinking**
- Kalite: **88/100**
- Benzerlik: **0.43** — https://www.alo186.com/haberler/ups-cikis-kisa-devre-akimi-sigorta-selektivite
- Kelime: **987**

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

- **S1 · IEC** — [IEC 62040-3:2021 — UPS performance and test requirements](https://webstore.iec.ch/en/publication/60140) — erişim 2026-08-03 — birincil
- **S2 · Schneider Electric** — [Galaxy PW 60 kVA UPS technical specifications](https://www.productinfo.schneider-electric.com/galaxypw/viewer?docidentity=SpecificationsFor60KVAUPS33-8A4EF122&extension=xml&lang=en&manualidentity=InstallationGalaxyPW2ndGen10-200KVA-89D560DB) — erişim 2026-08-03 — birincil
- **S3 · Schneider Electric** — [Galaxy VS 400 V technical specifications — short-circuit capability](https://productinfo.se.com/galaxyvs_iec/viewer?docidentity=Bravo1.2_Specifications400V-7873864A&extension=xml&lang=en&manualidentity=TechnicalSpecificationsGalaxyVSUPSW-72242CF8) — erişim 2026-08-03 — birincil
- **S4 · Schneider Electric** — [Selectivity, Cascading and Coordination Guide 2025](https://www.se.com/in/en/download/document/LVPED318033EN/) — erişim 2026-08-03 — birincil
- **S5 · Eaton** — [Low-voltage switchgear fundamentals — selective coordination](https://www.eaton.com/us/en-us/products/low-voltage-power-distribution-control-systems/switchgear-lv/low-voltage-switchgear-fundamentals---eaton.html) — erişim 2026-08-03 — birincil

## SEO

- Title: `UPS Çıkışı Kısa Devre Akımı ve Kesici Selektivite Kabulü`
- H1: `UPS çıkışında kısa devre koruması ve selektivite nasıl doğrulanır?`
- Description: `UPS inverter, akü ve bypass modlarında kısa devre akımını kesici eğrileriyle eşleştirin; kritik yük selektivitesini kabul dosyasıyla kanıtlayın.`
- Canonical: `/haberler/ups-cikis-kisa-devre-akimi-selektivite-kesici-kabul`
- Birincil anahtar kelime: `UPS kısa devre selektivite testi`

## Doğrudan cevap

UPS çıkışındaki kısa devre koruması yalnız şebeke kısa devre hesabıyla seçilemez. İnverter ve akü modunda UPS akımı sınırlı ve zamana bağlı verir; statik veya bakım bypassında ise upstream kaynağın daha yüksek arıza akımı devreye girer. Alt kesicinin zaman-akım eğrisi, UPS’nin mod bazlı akım-zaman verisi, kablo empedansı ve üst kesiciyle birlikte değerlendirilmelidir. Kabul hedefi, arızaya en yakın kesicinin UPS kapanmadan veya sağlıklı yükleri kesmeden açmasıdır; kontrolsüz kısa devre testi yapılmaz.

## UPS kısa devre akımı neden şebeke kısa devre akımı gibi ele alınamaz?

UPS çıkışındaki arıza akımı kaynağa ve zamana bağlıdır. İnverter veya akü modunda güç elektroniği akımı sınırlayabilir ve belirli süre sonra çıkışı kapatabilir; statik bypass ya da bakım bypassında ise arıza akımı upstream şebeke, trafo ve kablo empedansıyla çok daha yüksek olabilir. Bu yüzden tek bir “kA” değeri bütün çalışma modlarını temsil etmez.

IEC 62040-3 tamamlanmış UPS ve onunla çalışan anahtarların performans ve test gereklerini tanımlar. Üretici tabloları modele özgü kısa devre davranışını verir: örneğin Galaxy PW 60 kVA için 60 ms’de 273 A çıkış kısa devre akımı belirtilirken aynı tabloda 10 kA maksimum kısa devre ratingi bulunur. Akım üretme kabiliyeti ile ekipmanın dayanım/rating değeri aynı kavram değildir.

- Normal, akü, statik bypass ve bakım bypass modlarını ayrı kaynak olarak çizin.
- İnverter kısa devre akımını kA dayanım değeriyle karıştırmayın.
- Üreticinin akım-zaman veya önerilen kesici tablosunu model bazında alın.
- Tek hat üzerinde arıza noktasından kaynağa bütün empedansları gösterin.

_Kaynaklar: S1, S2, S3_

## Alt kesici UPS’nin akım sınırlamasıyla nasıl koordine edilir?

Alt devre kesicisinin manyetik veya elektronik açma eşiği, UPS’nin sağlayabildiği arıza akımına hiç ulaşmıyorsa kesici beklenen sürede açmayabilir; UPS akım limitine girip tüm çıkışı kapatabilir. Diğer uçta, bypass modundaki yüksek kısa devre akımı kesicinin kesme kapasitesi, kablo termik dayanımı ve pano kısa devre dayanımıyla uyumlu olmalıdır.

Kabul hesabı; beklenen minimum ve maksimum arıza akımı, arıza çevrim empedansı, iletken uzunluğu-kesiti, UPS’nin zamana bağlı akım limiti, alt ve üst kesicilerin zaman-akım eğrileri ve üretici koordinasyon tablolarını birlikte kullanmalıdır. Ayarlanabilir elektronik trip ünitesi varsa kısa zaman ve ani açma değerleri, upstream–downstream ayrımı bozulmadan belirlenmelidir.

- En uzak devrede minimum arıza akımını hesaplayın veya ölçümle doğrulayın.
- Bypass kaynağında maksimum kısa devre akımını ve kesme kapasitesini karşılaştırın.
- Kablo termik dayanımı ile kesicinin I²t davranışını birlikte inceleyin.
- Kesici ayarını yalnız nominal UPS akımının katı olarak seçmeyin.

_Kaynaklar: S1, S2, S3, S4_

## UPS çıkışında selektivite hangi sonuçla kabul edilir?

Selektivitenin hedefi, alt devredeki arızada yalnız arızaya en yakın koruma cihazının açması ve sağlıklı kritik yüklerin enerjili kalmasıdır. Eaton’ın tanımı da seçici koordinasyonu, downstream aşırı akım cihazının arızayı temizlemesi ve upstream cihazın kapalı kalması olarak açıklar. UPS tarafında buna, inverter akım limitinin ve statik bypass transfer mantığının etkisi eklenir.

Zaman-akım eğrileri yalnız şebeke modunda değil, inverter ve akü modundaki sınırlı akımla da karşılaştırılmalıdır. Alt kesici açmadan UPS çıkışı kapanıyor, statik bypassa transfer oluyor veya upstream kesici bütün barayı kesiyorsa hedeflenen süreklilik sağlanmıyordur. Tam selektivite mümkün değilse sınır akımı, süre ve etkilenen yükler raporda açıkça yazılmalıdır.

- Her alt devre için hedeflenen açacak cihazı tanımlayın.
- İnverter ve bypass modlarında eğri/akım-zaman karşılaştırması yapın.
- UPS kapanma veya transfer eşiğini kesici açma süresiyle karşılaştırın.
- Kısmi selektivite varsa geçerli akım sınırını rapora yazın.

_Kaynaklar: S3, S4, S5_

## Kısa devre ve selektivite nasıl güvenli test edilmelidir?

Kontrolsüz biçimde iletkenleri kısa devre etmek kabul yöntemi değildir. Öncelik; üretici test raporu, doğrulanmış kısa devre hesabı, koruma yazılımı ve kesici koordinasyon tablolarıdır. Fonksiyon doğrulaması gerekiyorsa ikincil enjeksiyon, kesici trip testi, özel düşük enerjili test düzeni veya üreticinin onayladığı yük bankası/prosedür yetkin ekip ve risk analiziyle kullanılır.

Kayıtta arıza simülasyonu başlama anı, UPS modu, çıkış RMS ve tepe akımı, çıkış gerilimi, kesici açma süresi, statik bypass transferi, UPS alarmı ve upstream cihaz durumu aynı zaman tabanında gösterilmelidir. Test, kritik yükler ayrılmış veya kontrollü yedekleme sağlanmış durumda yapılmalı; koruma fonksiyonları geçici olarak devre dışı bırakılmamalıdır.

- Önce hesap, üretici eğrisi ve ikincil enjeksiyonla doğrulama yapın.
- Canlı çıkışta kontrolsüz kısa devre oluşturmayın.
- UPS olay kaydı ile kesici trip zamanını senkron kaydedin.
- Kritik yük ve geri dönüş planı olmadan saha testi başlatmayın.

_Kaynaklar: S1, S2, S4_

## UPS kısa devre–selektivite kabul dosyasında neler bulunmalıdır?

Dosya; UPS modeli, güç ve firmware, tek/çift giriş mimarisi, inverter-akü-bypass kısa devre verileri, SCCR/dayanım değerleri, upstream ve downstream kesici modelleri/ayarları, kablo bilgileri, minimum-maksimum arıza hesabı, zaman-akım eğrileri, selektivite tablosu, test kayıtları ve geçti-kaldı sonucunu içermelidir. Paralel UPS sistemlerinde ortak bypass ve her modülün katkısı ayrıca incelenmelidir.

Sonuç yalnız “kesici açtı” olmamalıdır: hangi cihazın kaç milisaniyede açtığı, UPS’nin kapanıp kapanmadığı, diğer yüklerde gerilim çukuru oluşup oluşmadığı ve bypassa transfer sonucu yazılmalıdır. Mevcut kesiciler bütün modlarda hedefi kanıtla karşılıyorsa gereksiz kesici veya UPS büyütmesi yapılmamalıdır. CTA: kişisel verisiz UPS kaynak-modu–kesici–eğri kabul matrisini yetkin mühendislik ekibine iletin.

- Akım üretme kabiliyeti, SCCR ve kesme kapasitesini ayrı sütunlarda tutun.
- Her çalışma modu için minimum ve maksimum arıza akımını yazın.
- Kısmi selektivitenin sınırını ve etkilenen kritik yükleri belirtin.
- Kanıt yeterliyse gereksiz kesici veya UPS değişimi satın almayın.

_Kaynaklar: S1, S2, S3, S4, S5_

## Sık sorulan sorular

### UPS çıkışında kısa devre olursa sigorta mutlaka hemen açar mı?

Hayır. İnverterin akım limiti kesicinin ani açma eşiğinin altında kalabilir; UPS önce kapanabilir veya bypassa transfer olabilir. Modelin akım-zaman verisi ile kesici eğrisi birlikte incelenmelidir.

_Kaynaklar: S1, S2, S3_

### UPS üzerindeki 10 kA değeri çıkışın 10 kA kısa devre akımı verdiği anlamına mı gelir?

Hayır. Bu değer çoğu tabloda kısa devre rating/dayanım bağlamındadır. İnverterin sağlayabildiği çıkış arıza akımı ayrı ve zamana bağlı bir değerdir; örneğin üretici 60 ms için amper cinsinden ayrıca veri verebilir.

_Kaynaklar: S2, S3_

### UPS devresinde B eğrisi mi C eğrisi mi kullanılmalı?

Evrensel tek cevap yoktur. Yükün kalkış akımı, UPS’nin minimum arıza akımı, kesici açma eğrisi, kablo ve bypass modu birlikte hesaplanmalı; üretici koordinasyon tabloları esas alınmalıdır.

_Kaynaklar: S1, S4_

### Selektivite testi için gerçek kısa devre yapılır mı?

Kontrolsüz kısa devre yapılmaz. Hesap, üretici tabloları, yazılım ve ikincil enjeksiyon önceliklidir; gerekiyorsa üretici onaylı kontrollü test düzeni risk analizi ve yetkin ekiple uygulanır.

_Kaynaklar: S1, S4, S5_

## İnsan onay komutu

PR sahibinin veya repository yetkilisinin yorumu:

```text
/cms approve ups-cikis-kisa-devre-akimi-selektivite-kesici-kabul
```

Onay iş akışı kalite puanı, kaynak güncelliği, iç linkler, kanibalizasyon ve risk sınırlarını yeniden çalıştırmadan canonical dosya üretmez.
