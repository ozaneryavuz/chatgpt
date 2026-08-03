# ALO186 AI CMS inceleme paketi — vfd-motor-rulman-akimi-dvdt-filtre-kabul

> Bu dosya canonical yayına dahil edilmez. PR incelemesi ve insan onayı için üretilmiştir.

## Durum

- State: **approved**
- Risk: **high**
- Model: **gpt-5.6-thinking**
- Kalite: **88/100**
- Benzerlik: **0.29** — https://www.alo186.com/haberler/surucu-dvdt-sinus-filtre-motor-kablosu-rulman-akimi
- Kelime: **1019**

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

- **S1 · IEC** — [IEC TS 60034-25:2022 — AC electrical machines used in power drive systems](https://webstore.iec.ch/en/publication/66456) — erişim 2026-08-03 — birincil
- **S2 · IEC** — [IEC 61800-3:2022 — EMC requirements for power drive systems](https://webstore.iec.ch/en/publication/65056) — erişim 2026-08-03 — birincil
- **S3 · IEC** — [IEC 61800-5-1:2022 — Safety requirements for power drive systems](https://webstore.iec.ch/en/publication/62103) — erişim 2026-08-03 — birincil
- **S4 · ABB** — [Baldor-Reliance shaft grounded motors](https://www.abb.com/global/en/areas/motion/motors-generators/low-voltage-motors/nema-ac-motors-portfolio/hvac-motors/shaft-grounding-motors) — erişim 2026-08-03 — birincil
- **S5 · ABB** — [RPM AC Inverter Duty motors](https://www.abb.com/global/en/areas/motion/motors-generators/low-voltage-motors/nema-ac-motors-portfolio/variable-speed-ac-motors/rpm-ac/rpm-ac-inverter-duty) — erişim 2026-08-03 — birincil

## SEO

- Title: `VFD Motor Rulman Akımı ve dv/dt Kabul Rehberi`
- H1: `İnverter motorunda rulman akımı ve dv/dt riski nasıl kanıtlanır?`
- Description: `VFD–motor–kablo uyumunu; dv/dt, common-mode gerilim, ekranlama, bonding, rulman akımı ve filtre kabul ölçümleriyle doğrulayın.`
- Canonical: `/haberler/vfd-motor-rulman-akimi-dvdt-filtre-kabul`
- Birincil anahtar kelime: `VFD motor rulman akımı dv dt filtre`

## Doğrudan cevap

VFD’li motorda rulman arızası görüldüğünde yalnız rulman markasını veya sürücüyü değiştirmek yeterli teşhis değildir. Doğru kabul dosyası; sürücü modeli ve anahtarlama ayarını, motorun converter-duty uygunluğunu, kablo tipi ve uzunluğunu, ekranın 360 derece sonlandırılmasını, eşpotansiyel bonding’i, motor terminalindeki gerilim kenarlarını ve şaft/rulman akımı belirtilerini birlikte kaydeder. Ölçüm ve üretici sınırları kök nedeni doğruluyorsa dv/dt veya sinüs filtre, common-mode çözümü, yalıtılmış yatak ya da şaft topraklama elemanı seçilir; mevcut kurulum yeterliyse gereksiz ekipman eklenmez.

## Rulman izi, motor sesi veya sürücü alarmı tek başına neden yeterli değildir?

VFD beslemesi, motor terminallerine hızlı gerilim kenarları ve common-mode gerilim taşıyabilir. Kablo ve motor empedansları gerilim yansımasını etkileyebilir; common-mode akım ise gövde, ekran, PE, kaplin ve yataklar üzerinden farklı yollar bulabilir. Bunun sonucu yatakta elektriksel boşalma, fluting izi veya gürültü olabilir. Ancak yağlama, hizasızlık, mekanik yük, titreşim ve kirlenme de benzer hasar üretir.

IEC TS 60034-25:2022, converter-fed motor performansı, sürücü–motor arayüzü, kurulum ve güncellenmiş şaft akımları bölümünü kapsar. Bu nedenle inceleme; arıza geçmişini, rulman fotoğrafını, titreşim ve sıcaklığı, motor izolasyon sınıfını, kabloyu ve sürücü ayarlarını tek olay zaman çizelgesinde birleştirmelidir.

- Rulman hasar tipini elektriksel ve mekanik olasılıklarla birlikte sınıflandırın.
- Motor, sürücü ve kablo nameplate/veri sayfasını aynı dosyada toplayın.
- Anahtarlama frekansı ve kontrol modundaki son değişiklikleri kaydedin.
- Rulman değişiminden sonra kök neden ölçümü yapılmadan dosyayı kapatmayın.

_Kaynaklar: S1, S4, S5_

## VFD–motor–kablo uyum matrisi hangi alanları içermelidir?

Matris; besleme gerilimi, sürücü çıkış topolojisi, anahtarlama frekansı, motorun converter-capable veya converter-duty tanımı, izolasyon sistemi, kablo tipi, ekran yapısı, motor kablosu uzunluğu, çıkış reaktörü/filtre ve üretici izinlerini içermelidir. Evrensel bir kablo uzunluğu sınırı yayımlanamaz; aynı uzunluk farklı sürücü, motor ve kabloda farklı terminal gerilimi oluşturabilir.

IEC 61800-5-1, güç sürücü sistemlerini elektriksel, termal, yangın, mekanik ve enerji tehlikeleri açısından ele alır. Motor terminali ve filtre üzerinde ölçüm yapılırken uygun kategori, bant genişliği, diferansiyel prob ve güvenli bağlantı yöntemi kullanılmalıdır. Sıradan multimetre, hızlı dv/dt veya common-mode geçişlerini kanıtlamak için yeterli değildir.

- Sürücü, motor, kablo ve filtre üretici dokümanlarını sürüm/tarih ile kaydedin.
- Motor kablo uzunluğunu gerçek güzergâh üzerinden ölçün.
- İzolasyon ve motor terminal gerilimi sınırını üreticiye göre doğrulayın.
- Ölçüm cihazı kategori ve bant genişliği uygunluğunu rapora yazın.

_Kaynaklar: S1, S3_

## Bonding ve motor kablosu ekranı neden rulman akımı kararından önce kontrol edilir?

Yüksek frekanslı common-mode akımlar düşük frekanslı topraklama direnci ölçümünden farklı yollar izler. Uzun pigtail ekran bağlantısı, boyalı yüzey, gevşek kablo rakoru, kesintili PE, zayıf motor gövde bonding’i veya kaplin üzerinden rastlantısal dönüş yolu yüksek frekans empedansını artırabilir. Bu durumda yalnız şaft topraklama fırçası eklemek belirtileri azaltabilir ancak sistemdeki temel dönüş yolunu düzeltmeyebilir.

IEC 61800-3:2022, ayarlanabilir hızlı güç sürücü sistemleri için EMC emisyon ve bağışıklık gereklerini tanımlar. Saha kabulünde ekranın sürücü ve motor uçlarında üretici talimatına uygun 360 derece sonlandırılması, pano montaj plakası ve motor gövdesi arasındaki bonding, paralel PE yolu ve sinyal kablolarının ayrımı görsel ve ölçümsel olarak doğrulanmalıdır.

- Ekran sonlandırmasını iki uçta fotoğraf ve parça bilgisiyle belgeleyin.
- Boyalı/oksitli yüzey ve uzun pigtail bağlantılarını tespit edin.
- Motor gövdesi, sürücü panosu ve makine şasesi bonding yolunu izleyin.
- Güç, encoder ve haberleşme kablolarının güzergâh ayrımını kontrol edin.

_Kaynaklar: S2, S3, S5_

## Şaft gerilimi, rulman akımı ve motor terminali nasıl ölçülür?

Ölçüm planı önce güvenli erişim ve cihaz yeterliliğini doğrular. Motor terminalindeki faz-faz ve faz-toprak hızlı geçişleri uygun yüksek gerilim diferansiyel probuyla; şaft gerilimi ise bu amaç için tasarlanmış temas yöntemi ve osiloskopla ölçülür. Akım pensinin bant genişliği ve minimum algılama seviyesi, kısa süreli boşalma darbelerini yakalayabilecek düzeyde olmalıdır.

Tek dalga biçimi kök neden değildir. Kayıtlar motor hızı, yükü, anahtarlama frekansı, kablo sıcaklığı ve sürücü işletme modu ile eşleştirilmelidir. Rulman hasarı varsa titreşim spektrumu, yağlama ve hizalama bulguları da eklenir. ABB’nin VFD kullanımına yönelik motor ürünleri, bearing-current azaltımı için entegre şaft topraklama fırçası veya halkası kullanan çözümlerin bulunduğunu gösterir; bu, her motorda aynı çözümün otomatik seçileceği anlamına gelmez.

- Motor terminali ve şaft ölçümünde ortak zaman ve işletme durumu kullanın.
- Osiloskop/prob bant genişliği ve güvenlik kategorisini kaydedin.
- Farklı hız, yük ve anahtarlama frekanslarında tekrar ölçün.
- Elektriksel bulguları titreşim, sıcaklık ve yağlama verisiyle korele edin.

_Kaynaklar: S1, S4, S5_

## dv/dt filtresi, sinüs filtresi, yalıtılmış yatak veya şaft topraklama nasıl seçilir?

Çözüm kök nedene göre seçilmelidir. Motor terminalindeki hızlı kenar ve yansıma baskınsa üretici onaylı çıkış reaktörü, dv/dt veya sinüs filtresi değerlendirilebilir. Common-mode dönüş yolu ve şaft gerilimi baskınsa bonding düzeltmesi, common-mode çözümü, şaft topraklama elemanı veya uygun tarafta yalıtılmış yatak gündeme gelebilir. Büyük motorlarda iki yatak ve bağlı makine üzerinden akım yolları ayrıca incelenmelidir.

Kabul testi, müdahale öncesiyle aynı hız, yük, kablo ve ölçüm zincirinde tekrarlanır. Terminal dalga biçimi, şaft gerilimi/boşalma olayları, gövde akımı, EMC belirtisi, motor sıcaklığı ve sürücü alarmı birlikte karşılaştırılır. Filtre eklendiğinde gerilim düşümü, ısınma, tork davranışı ve üretici ayarları yeniden doğrulanmalıdır. ABB’nin inverter-duty motorlarında şaft grounding brush kullanması, bearing current azaltımı için bir tasarım seçeneğini gösterir; nihai çözüm saha ölçümü ve tüm sistem üreticilerinin sınırlarıyla kabul edilmelidir.

- Müdahaleyi ölçülen kök neden ve üretici onayıyla eşleştirin.
- Öncesi/sonrası testini aynı işletme noktasında yapın.
- Filtre sonrası sıcaklık, tork ve sürücü ayarını yeniden doğrulayın.
- Mevcut sistem sınırlar içindeyse ek filtre veya yatak elemanı satın almayın.

_Kaynaklar: S1, S2, S3, S4, S5_

## Sık sorulan sorular

### VFD her motorda rulman akımı oluşturur mu?

VFD common-mode gerilim üretebilir, ancak zararlı rulman akımının oluşması motor, kablo, grounding/bonding, mekanik bağlantı, güç ve sürücü topolojisine bağlıdır. Ölçüm olmadan her motorda aynı hasar varsayılamaz.

_Kaynaklar: S1, S2_

### Motor kablosu uzunsa mutlaka dv/dt filtresi gerekir mi?

Hayır. Kablo uzunluğu önemli bir girdidir, fakat karar sürücü ve motor üreticisinin sınırları, kablo özellikleri ve motor terminalindeki ölçümle verilmelidir. Evrensel tek metre sınırı doğru değildir.

_Kaynaklar: S1, S3_

### Şaft topraklama halkası yalıtılmış yatak yerine geçer mi?

Her sistemde değil. Akım yolu, motor gücü, iki yatak, kaplin ve bağlı makine değerlendirilmelidir. Bazı tasarımlarda grounding elemanı, bazı tasarımlarda yalıtılmış yatak veya birlikte çözüm gerekebilir.

_Kaynaklar: S1, S4, S5_

### Standart topraklama direnci düşükse common-mode sorunu olmaz mı?

Olabilir. Düşük frekanslı topraklama ölçümü, yüksek frekanstaki ekran ve bonding empedansını tek başına göstermez. Ekran sonlandırması, geniş yüzeyli bonding ve gerçek akım yolu ayrıca incelenmelidir.

_Kaynaklar: S2, S3_

## İnsan onay komutu

PR sahibinin veya repository yetkilisinin yorumu:

```text
/cms approve vfd-motor-rulman-akimi-dvdt-filtre-kabul
```

Onay iş akışı kalite puanı, kaynak güncelliği, iç linkler, kanibalizasyon ve risk sınırlarını yeniden çalıştırmadan canonical dosya üretmez.
