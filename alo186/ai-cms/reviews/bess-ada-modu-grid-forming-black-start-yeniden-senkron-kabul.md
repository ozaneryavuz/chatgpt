# ALO186 AI CMS inceleme paketi — bess-ada-modu-grid-forming-black-start-yeniden-senkron-kabul

> Bu dosya canonical yayına dahil edilmez. PR incelemesi ve insan onayı için üretilmiştir.

## Durum

- State: **approved**
- Risk: **legal**
- Model: **gpt-5.6-thinking**
- Kalite: **88/100**
- Benzerlik: **0.40** — https://www.alo186.com/haberler/bess-grid-forming-grid-following-black-start-ada-calismasi
- Kelime: **963**

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

- **S1 · IEC** — [IEC TS 62933-3-3:2022 — Energy Intensive, Islanded Grid and Backup Applications](https://webstore.iec.ch/en/publication/64911) — erişim 2026-08-03 — birincil
- **S2 · IEC** — [IEC 62933-3-1:2025 — Planning and Performance Assessment of EES Systems](https://webstore.iec.ch/en/publication/75427) — erişim 2026-08-03 — birincil
- **S3 · IEC** — [IEC TS 62786-3:2023 — Grid Connection Requirements for Stationary BESS](https://webstore.iec.ch/en/publication/62507) — erişim 2026-08-03 — birincil
- **S4 · TEİAŞ** — [Müstakil Elektrik Depolama Tesisleri İçin Oturan Sistemin Toparlanması Hizmeti](https://www.teias.gov.tr/mustakil-elektrik-depolama-tesisleri-icin-oturan-sistemin-toparlanmasi-hizmeti) — erişim 2026-08-03 — birincil
- **S5 · EPDK** — [Elektrik Piyasası Yan Hizmetler Yönetmeliği ve Anlaşmaları](https://epdk.gov.tr/Detay/Icerik/3-6723/elektrik-piyasasi-yan-hizmetler-yonetmeligi) — erişim 2026-08-03 — birincil
- **S6 · TEİAŞ** — [Elektrik Depolama Ünite veya Tesislerinin Yan Hizmetlerde Kullanılmasına Dair Teknik Kriterler ve Test Prosedürleri](https://www.teias.gov.tr/duyurular/elektrik-depolama-unite-veya-tesislerinin-yan-hizmetlerde-kullanilmasina-dair-teknik-kriterler-ve-test-prosedurleri) — erişim 2026-08-03 — birincil

## SEO

- Title: `BESS Ada Modu ve Black Start Kabul Testi`
- H1: `BESS ada modu, grid-forming ve black start işlevleri nasıl güvenli kabul edilir?`
- Description: `BESS ada modu ve black start kabul testini SoC rezervi, ölü bara enerjilendirme, yük alma, koruma ve yeniden senkron kanıtlarıyla hazırlayın.`
- Canonical: `/haberler/bess-ada-modu-grid-forming-black-start-yeniden-senkron-kabul`
- Birincil anahtar kelime: `BESS ada modu black start kabul testi`

## Doğrudan cevap

BESS ada modu ve black start kabul testi, şebeke kesildiğinde bataryanın yalnız yük beslemesiyle tamamlanmaz. Sistem önce grid-following veya grid-forming olarak sınıflandırılmalı ve gerilimsiz barayı kurma kabiliyeti doğrulanmalıdır. Kabul; minimum SoC ve yardımcı güç rezervi, ölü bara kontrolü, gerilim-frekans oluşturma, kritik yüklerin sıralı alınması, trafo ve motor ilk akımları, GES/jeneratör koordinasyonu, ada korumaları, başarısız başlatmadan güvenli dönüş ve şebeke geri geldiğinde senkron yeniden bağlantı kayıtlarını gerektirir. Tesis içi yedekleme, TEİAŞ'ın oturan sistemin toparlanması hizmetiyle aynı değildir.

## Tesis içi ada işletmesi ile sistem toparlanması hizmeti neden ayrılmalıdır?

Tesis içi ada modu, şebeke kesildiğinde belirlenmiş iç barayı ve kritik yükleri bağımsız beslemeyi amaçlar. Oturan sistemin toparlanması ise elektrik sisteminin yeniden kurulmasına yönelik, anlaşma ve teknik kriterlere bağlı bir yan hizmettir. Aynı batarya her iki teknik kabiliyete sahip görünse bile resmî hizmete katılım otomatik olarak doğmaz.

Kabulün başlangıcında sistem sınırı, bağlantı kesicileri, kritik yük barası, varsa jeneratör ve GES bağlantıları, şebeke oluşturma yetkisi ve resmî yükümlülük belgeleri tek hatta gösterilmelidir. Hangi testin tesis sürekliliği, hangisinin şebeke yan hizmeti için yapıldığı açıkça ayrılmalıdır.

- Ada sınırını ve enerjilendirilecek baraları tek hatta işaretleyin.
- Grid-following ve grid-forming inverter işlevlerini ayrı kaydedin.
- Tesis yedekleme testi ile TEİAŞ yan hizmeti testini karıştırmayın.
- Bağlantı anlaşması, yan hizmet anlaşması ve üretici kabiliyetini ayrı kanıtlayın.

_Kaynaklar: S1, S2, S4, S5_

## Black start için SoC ve yardımcı güç rezervi nasıl belirlenmelidir?

Ölü bara başlatması sırasında yalnız dış yüklere giden enerji değil; BMS, HVAC, yangın algılama, PCS kontrolü, şalt bobinleri, haberleşme, trafonun mıknatıslanması ve motor ilk akımları da dikkate alınmalıdır. Kullanılabilir enerji, ad plakasındaki kWh değerinden farklı olabilir; sıcaklık, SoH, minimum SoC, güç sınırı ve güvenlik rezervi hesaba katılmalıdır.

Kabul öncesinde başlatma enerji bütçesi hazırlanmalı ve en olumsuz makul koşulda tekrarlanabilir başlatma sayısı belirlenmelidir. Yetersiz SoC, yardımcı AC/DC kaynağı kaybı veya HVAC hazır değilse sistemin black start komutunu reddetmesi ya da güvenli duruma dönmesi test edilmelidir.

- SoC, SoH, sıcaklık ve kullanılabilir kWh sınırlarını kaydedin.
- BMS, PCS, HVAC, şalt ve haberleşme yardımcı yüklerini bütçeye ekleyin.
- Trafo mıknatıslanması ve motor ilk akımlarını ayrı senaryolaştırın.
- Düşük SoC veya yardımcı güç kaybında güvenli ret davranışını doğrulayın.

_Kaynaklar: S1, S3, S6_

## Ölü bara enerjilendirme ve kademeli yük alma nasıl test edilir?

Başlatma öncesinde bara gerilimsizliği, kaynak kesicilerinin açık konumu ve geri besleme yollarının kapalı olduğu doğrulanmalıdır. BESS gerilim ve frekansı oluşturduktan sonra boş bara, trafo, küçük sabit yükler, kritik kontrol yükleri ve büyük motorlar önceden tanımlanmış sırayla alınmalıdır. Her adımda gerilim, frekans, RoCoF, akım, kW-kVAr ve PCS sınırları trendlenmelidir.

Yük basamağının büyüklüğü, inverterin geçici akım kabiliyeti ve droop ayarlarıyla uyumlu olmalıdır. Frekans çökmesi, salınım, gerilim çukuru, koruma açması veya BMS güç sınırlaması görülürse yük sırası yeniden tasarlanmalıdır. Tek başarılı başlatma yerine farklı SoC ve yük kombinasyonlarında tekrarlanabilirlik aranmalıdır.

- Ölü bara, kesici ve geri besleme kontrollerini saat damgalı kaydedin.
- Yükleri kritikiyet, ilk akım ve yeniden başlatma ihtiyacına göre sıralayın.
- Her basamakta V, f, RoCoF, P, Q ve akım trendi alın.
- Aşırı büyük yük adımında yük atma ve güvenli toparlanmayı test edin.

_Kaynaklar: S1, S2, S3_

## GES, jeneratör ve şebekeye yeniden bağlanma nasıl koordine edilir?

Ada barasında GES inverteri grid-following ise BESS'in oluşturduğu gerilim ve frekansa bağlanabilir; ancak anti-islanding, güç rampası, minimum yük ve ters güç sınırları birlikte değerlendirilmelidir. Jeneratör devreye alınacaksa senkronizasyon, kW-kVAr yük paylaşımı, governor/AVR davranışı ve hangi kaynağın grid-forming referansı olduğu açık olmalıdır.

Şebeke geri geldiğinde otomatik kapanma yalnız gerilim varlığına göre yapılmamalıdır. Faz sırası, gerilim, frekans, faz açısı, senkron kontrolü, bekleme süresi ve kesici geri bildirimi doğrulanmalı; gerekiyorsa önce ada yükü şebekeye transfer edilip BESS normal moda dönmelidir. Başarısız senkron veya iletişim kaybında kesicinin kapanmadığı kanıtlanmalıdır.

- GES anti-islanding ve ada çalışma izinlerini model bazında doğrulayın.
- Jeneratörle grid-forming referansı ve yük paylaşım rollerini belirleyin.
- Şebekeye yeniden bağlanmada senkron kontrolü ve kesici feedbackini test edin.
- Başarısız senkron, haberleşme kaybı ve yanlış faz sırasını fail-closed sınayın.

_Kaynaklar: S2, S3, S6_

## BESS ada modu ve black start kabul dosyasında neler bulunmalıdır?

Dosya; tek hat, işletme modları, firmware ve parametre yedeği, SoC/SoH rezerv hesabı, yardımcı yük listesi, koruma ayarları, ölü bara kontrolü, yük alma sırası, GES/jeneratör koordinasyonu, senkron kontrolü, olay kayıtları, SCADA komutları, alarm matrisi ve imzalı test sonuçlarını içermelidir. Her senaryo için başlangıç koşulu ve güvenli geri dönüş tanımlanmalıdır.

Sonuç geçti, şartlı geçti veya kaldı olarak sınıflandırılmalıdır. Tekrarlanamayan başlatma, yetersiz enerji rezervi, kararsız gerilim-frekans, yanlış kesici kapanması, korunmasız ada veya senkron dışı yeniden bağlantı varsa kabul verilmemelidir. Mevcut BESS bütün senaryoları kanıtla geçiyorsa yalnız pazarlama dili nedeniyle yeni PCS, EMS veya ek batarya satın almak gereksizdir.

- Testlerin başlangıç SoC, sıcaklık ve yük koşullarını değişmez kaydedin.
- Komut, kesici, koruma, alarm ve ölçümleri ortak zaman çizelgesinde birleştirin.
- Her başarısızlık için güvenli durum ve yeniden test koşulu tanımlayın.
- Kanıt yeterliyse gereksiz kapasite veya kontrolör yatırımı yapmayın.

_Kaynaklar: S1, S2, S3, S4, S5, S6_

## Sık sorulan sorular

### Her BESS sistemi black start yapabilir mi?

Hayır. Birçok sistem grid-following çalışır ve gerilim-frekans referansı olmadan ölü barayı kuramaz. Black start için grid-forming PCS, yardımcı güç, koruma, şalt ve kontrol mimarisinin birlikte tasarlanması ve test edilmesi gerekir.

_Kaynaklar: S1, S2, S3_

### Ada modu ile UPS işlevi aynı mıdır?

Her zaman değil. Transfer süresi, güç kalitesi, yük önceliği, kısa devre akımı, koruma seçiciliği ve çalışma süresi farklı olabilir. Kritik yük için kabul kriteri uygulamanın kesinti toleransına göre ayrıca tanımlanmalıdır.

_Kaynaklar: S1, S3_

### BESS black start yapınca GES otomatik çalışır mı?

Yalnız GES inverterinin oluşturduğu ada şebekesine bağlanmasına izin veren kontrol, anti-islanding ve güç yönetimi tasarımı varsa çalışabilir. Üretici ve proje doğrulaması olmadan GES'in otomatik devreye gireceği varsayılmamalıdır.

_Kaynaklar: S2, S3_

### Tesis içi black start testi TEİAŞ yan hizmetine katılım için yeterli midir?

Hayır. TEİAŞ'ın müstakil depolama tesisleri için oturan sistemin toparlanması hizmeti ayrı anlaşma, teknik kriter ve test prosedürlerine bağlıdır. Tesis içi başarı resmî hizmet kabulü veya gelir garantisi oluşturmaz.

_Kaynaklar: S4, S5, S6_

## İnsan onay komutu

PR sahibinin veya repository yetkilisinin yorumu:

```text
/cms approve bess-ada-modu-grid-forming-black-start-yeniden-senkron-kabul
```

Onay iş akışı kalite puanı, kaynak güncelliği, iç linkler, kanibalizasyon ve risk sınırlarını yeniden çalıştırmadan canonical dosya üretmez.
