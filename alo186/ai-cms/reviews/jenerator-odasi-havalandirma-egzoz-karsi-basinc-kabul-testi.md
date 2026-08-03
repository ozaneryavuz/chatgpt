# ALO186 AI CMS inceleme paketi — jenerator-odasi-havalandirma-egzoz-karsi-basinc-kabul-testi

> Bu dosya canonical yayına dahil edilmez. PR incelemesi ve insan onayı için üretilmiştir.

## Durum

- State: **approved**
- Risk: **high**
- Model: **gpt-5.6-thinking**
- Kalite: **88/100**
- Benzerlik: **0.40** — https://alo186.com/haberler/jenerator-odasi-havalandirma-radyator-hava-debisi-hararet
- Kelime: **941**

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

- **S1 · Cummins** — [Power Suite — GenCalc Project Calculations](https://powersuite.cummins.com/) — erişim 2026-08-03 — birincil
- **S2 · Caterpillar** — [Ambient Capability of Enclosed Generator Sets](https://www.cat.com/en_AU/by-industry/electric-power/Articles/White-papers/ambient-capability-of-enclosed-generator-sets.html) — erişim 2026-08-03 — birincil
- **S3 · Caterpillar** — [Designing Backup, Standby and Emergency Power in High-Performance Buildings](https://www.cat.com/en_ZA/by-industry/electric-power/Articles/ep-news/ep-news-designing-backup-standby-and-emergency-power-in-high-performance-buildings.html) — erişim 2026-08-03 — birincil
- **S4 · Caterpillar** — [When and How to Design Parallel Generators](https://www.cat.com/en_IN/by-industry/electric-power/Articles/ep-news/ep-news-when-and-how-to-design-parallel-generators.html) — erişim 2026-08-03 — birincil
- **S5 · Caterpillar** — [Designing Backup, Standby and Emergency Power — Airflow Guidance](https://www.cat.com/en_IN/by-industry/electric-power/Articles/ep-news/ep-news-designing-backup-standby-and-emergency-power-in-high-performance-buildings.html) — erişim 2026-08-03 — birincil

## SEO

- Title: `Jeneratör Odası Havalandırma ve Egzoz Kabul Testi`
- H1: `Jeneratör odası havalandırması ve egzoz karşı basıncı nasıl kabul edilir?`
- Description: `Jeneratör odası havalandırma kabul testini hava debisi, basınç kaybı, sıcak hava dönüşü, egzoz karşı basıncı ve tam yük trendleriyle hazırlayın.`
- Canonical: `/haberler/jenerator-odasi-havalandirma-egzoz-karsi-basinc-kabul-testi`
- Birincil anahtar kelime: `jeneratör odası havalandırma kabul testi`

## Doğrudan cevap

Jeneratör odası havalandırma kabul testi yalnız menfez ölçüsünü kontrol etmekle tamamlanmaz. Modelin yanma ve soğutma hava ihtiyacı, radyatör fanının izin verdiği basınç kaybı, panjur-filtre-susturucu-kanal dirençleri, sıcak havanın yeniden emilmesi ve egzoz hattının toplam karşı basıncı üretici verileriyle hesaplanmalıdır. Ardından jeneratör gerçek veya kontrollü yükte kararlı sıcaklığa ulaşana kadar oda, hava giriş-çıkış, radyatör, soğutma suyu, emme havası ve egzoz değerleri trendlenmelidir. Duman/CO, yüksek sıcaklık kapanması veya karşı basınç sınırı aşımı kabul edilemez.

## Havalandırma ve egzoz hesabı neden jeneratör modelinden başlamalıdır?

Jeneratör odası için tek bir kVA başına menfez alanı bütün projelere uygulanamaz. Fan debisi, yanma havası, radyatör hava akışı, fanın izin verdiği basınç kaybı, egzoz debisi ve maksimum karşı basınç motor ve paket modeline göre değişir. Kabin, uzak radyatör, ses susturucu, filtre, emisyon sonrası arıtma ve rakım koşulları hesabı değiştirir.

Üretici datasheet, uygulama kılavuzu ve seçim hesabı aynı model ve rating için toplanmalıdır. Cummins GenCalc gibi üretici araçları havalandırma, egzoz karşı basıncı ve uzak soğutma hesaplarını ayrı parametreler olarak ele alır; sonuçlar evrensel sabit değil, proje girdileriyle üretilmelidir.

- Model, rating, duty, ortam sıcaklığı ve rakımı kaydedin.
- Yanma havası ile radyatör soğutma havasını ayrı kalemlerde hesaplayın.
- Fan dış statik basınç ve egzoz karşı basınç sınırını üreticiden alın.
- Uzak radyatör, SCR/DPF ve kabin seçeneklerini gerçek konfigürasyonla eşleştirin.

_Kaynaklar: S1, S2_

## Panjur, filtre, susturucu ve kanal kayıpları nasıl doğrulanmalıdır?

Serbest açıklık ile duvar boşluğu aynı değildir. Panjur kanatları, tel kafes, filtre, akustik susturucu, damper ve kanal direnci toplam basınç kaybını oluşturur. Radyatör fanı bu toplam direnci aşamazsa tasarım kâğıt üzerinde yeterli debiye sahip görünse bile gerçek hava akışı düşer ve soğutma suyu sıcaklığı yükselir.

Kabul dosyasında her elemanın debi-basınç kaybı verisi, kanal kesiti, dirsekler, esnek radyatör bağlantısı ve hava çıkışının dış ortam koşulu gösterilmelidir. Oda basıncı, panjur/damper konumu ve fan çalışması yük boyunca ölçülmeli; kapı açılmasına bağlı geçici iyileşme kalıcı çözüm sayılmamalıdır.

- Brüt menfez yerine net serbest alanı ve üretici basınç kaybını kullanın.
- Panjur, filtre, susturucu, damper ve kanal kayıplarını toplayın.
- Radyatör fanının izin verdiği dış statik basınçla karşılaştırın.
- Kapılar kapalı ve normal mimari durumda gerçek oda basıncını ölçün.

_Kaynaklar: S1, S4_

## Radyatör sıcak havasının yeniden emilmesi nasıl engellenir ve test edilir?

Hava girişi ile radyatör çıkışının yakın olması, rüzgâr yönü, dış cephe girintisi veya çoklu jeneratör yerleşimi sıcak havayı tekrar emişe taşıyabilir. Böyle bir recirculation, dış ortam sıcaklığı uygun olsa bile radyatör giriş havasını yükseltir ve jeneratörün ambient capability değerini düşürür.

Giriş ve çıkış noktaları birbirinden ve bina taze hava emişlerinden ayrılmalıdır. Çoklu jeneratör odasında yalnız bütün setlerin tam yükü değil, setlerin bir kısmı çalışırken oluşan farklı hava yolları da incelenmelidir. Gerekli büyük tesislerde CFD çalışması, duman izi veya çok noktalı sıcaklık ölçümüyle desteklenmelidir.

- Dış ortam, oda girişi ve radyatör yüzeyinde çok noktalı sıcaklık ölçün.
- Giriş-çıkış açıklıklarını hâkim rüzgâr ve bina emişleriyle birlikte değerlendirin.
- Bütün setler ve kısmi set kombinasyonlarında hava dolaşımını test edin.
- Sıcak hava geri dönüşünü kapı açık testle gizlemeyin.

_Kaynaklar: S2, S3, S4, S5_

## Egzoz karşı basıncı ve gaz güvenliği hangi kanıtlarla kabul edilmelidir?

Egzoz manifoldundan çıkış noktasına kadar boru çapı, toplam uzunluk, dirsek, esnek bağlantı, susturucu, yağmur şapkası ve varsa emisyon sonrası arıtma elemanı karşı basınca katkı verir. Yüksek karşı basınç motor gücünü, egzoz sıcaklığını ve yakıt tüketimini etkileyebilir; üreticinin maksimum sınırı aşılmamalıdır.

Egzoz borusu ısı yalıtımı, genleşme, askı, kondens tahliyesi ve bina taze hava girişlerinden uzak çıkışla birlikte değerlendirilmelidir. Oda ve komşu hacimlerde duman ya da karbonmonoksit bulunması kabul edilemez. Ölçüm, sıcak egzoz sisteminde yalnız yetkin ekip ve uygun bağlantı noktalarıyla yapılmalıdır.

- Boru, dirsek, susturucu ve arıtma elemanlarının toplam karşı basıncını hesaplayın.
- Tam yükte üretici ölçüm noktasından egzoz karşı basıncını doğrulayın.
- Isı yalıtımı, genleşme kompanzasyonu, askı ve kondens tahliyesini inceleyin.
- Oda ve yakın hava emişlerinde CO/duman bulunmadığını ölçümle kanıtlayın.

_Kaynaklar: S1, S4, S5_

## Tam yük termal kabul dosyası nasıl hazırlanmalıdır?

Jeneratör, gerçek tesis yükü veya uygun yük bankasıyla kararlı sıcaklığa ulaşana kadar çalıştırılmalıdır. Dış ortam, hava giriş ve çıkışı, radyatör ön yüzü, üst-alt tank soğutma suyu, emme havası, yağ, egzoz, oda basıncı, fan/damper durumu, kW-kVAr ve alarm değerleri ortak zaman çizelgesinde kaydedilmelidir. En zor yaz koşulu için üretici ambient capability hesabı ayrıca doğrulanmalıdır.

Sonuç geçti, şartlı geçti veya kaldı olarak sınıflandırılmalıdır. Yüksek soğutma suyu, sıcak hava recirculation, yetersiz hava debisi, egzoz karşı basınç aşımı, CO bulgusu veya kapı açılmadan çalışamama varsa sistem teslim edilmemelidir. Mevcut menfez, kanal ve egzoz sistemi bütün kanıtları geçiyorsa sırf daha büyük ekipman olduğu için ek fan veya susturucu satın almak gereksizdir.

- Kararlı sıcaklığa ulaşana kadar yeterli süre ve yükte trend alın.
- Dış ortam ile radyatör giriş havası sıcaklık farkını raporlayın.
- Alarm, shutdown, damper ve yardımcı fan fonksiyonlarını senaryolu test edin.
- Kanıt yeterliyse gereksiz fan, panjur veya egzoz ekipmanı almayın.

_Kaynaklar: S1, S2, S3, S4, S5_

## Sık sorulan sorular

### Jeneratör odası için menfez alanı yalnız kVA değerinden hesaplanabilir mi?

Hayır. Net serbest alan; modele özgü hava debisi, fan basınç kapasitesi, panjur-filtre-susturucu kayıpları, rakım, ortam sıcaklığı ve kanal geometrisiyle birlikte belirlenmelidir. Tek bir kVA katsayısı güvenli kabul sağlamaz.

_Kaynaklar: S1, S2, S4_

### Jeneratör kapı açıkken ısınmıyorsa havalandırma yeterli midir?

Hayır. Normal işletme mimarisinde kapıların kapalı olması bekleniyorsa kabul de bu durumda yapılmalıdır. Kapı açıldığında sıcaklık düşmesi, çoğu zaman hava yolu veya basınç kaybı yetersizliğine işaret eden bir teşhis bulgusudur.

_Kaynaklar: S2, S3_

### Egzoz borusu çapı büyükse karşı basınç otomatik olarak uygun mudur?

Hayır. Boru uzunluğu, dirsekler, susturucu, esnek bağlantı, çıkış elemanı ve emisyon sonrası arıtma toplam direnci belirler. Maksimum karşı basınç model verisiyle hesaplanmalı ve tam yükte ölçülmelidir.

_Kaynaklar: S1, S4_

### Birden fazla jeneratörde yalnız hepsi çalışırken test yapmak yeterli midir?

Hayır. Kısmi set çalışmasında oda içi hava yolları değişebilir ve çalışan setler kendi sıcak havasını yeniden emebilir. Bütün setler ve olası kısmi kombinasyonlar ayrı kabul senaryosu olmalıdır.

_Kaynaklar: S3, S5_

## İnsan onay komutu

PR sahibinin veya repository yetkilisinin yorumu:

```text
/cms approve jenerator-odasi-havalandirma-egzoz-karsi-basinc-kabul-testi
```

Onay iş akışı kalite puanı, kaynak güncelliği, iç linkler, kanibalizasyon ve risk sınırlarını yeniden çalıştırmadan canonical dosya üretmez.
