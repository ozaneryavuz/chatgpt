# ALO186 AI CMS inceleme paketi — ges-string-sigortasi-ters-akim-maksimum-seri-sigorta

> Bu dosya canonical yayına dahil edilmez. PR incelemesi ve insan onayı için üretilmiştir.

## Durum

- State: **approved**
- Risk: **high**
- Model: **gpt-5.6-thinking**
- Kalite: **100/100**
- Benzerlik: **0.54** — https://www.alo186.com/haberler/ges-pv-string-sigortasi-ters-akim-nasil-secilir
- Kelime: **933**

## Kalite kapıları

- ✅ metadata
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

- **S1 · IEC** — [IEC 62548-1:2023+A1:2025 — Photovoltaic arrays, Design requirements](https://webstore.iec.ch/en/publication/110893) — erişim 2026-08-03 — birincil
- **S2 · Fronius** — [Fronius Symo / Eco Operating Instructions — String fuses](https://manuals.fronius.com/html/4204101909/en.html) — erişim 2026-08-03 — birincil
- **S3 · SMA Solar Technology** — [Sunny Tripower CORE1 Technical Data — DC input limits](https://manuals.sma.de/STP50-40/en-US/43470603.html) — erişim 2026-08-03 — birincil

## SEO

- Title: `GES String Sigortası: Ters Akım ve Seri Sigorta Sınırı`
- H1: `GES string sigortası ne zaman gerekir? Ters akım ön kontrolü`
- Description: `GES string sigortası ihtiyacını paralel string sayısı, proje Isc, inverter ters akımı ve modül maksimum seri sigorta değeriyle güvenli biçimde inceleyin.`
- Canonical: `/haberler/ges-string-sigortasi-ters-akim-maksimum-seri-sigorta`
- Birincil anahtar kelime: `GES string sigortası`

## Doğrudan cevap

GES string sigortası, paralel stringlerden veya başka bir DC kaynaktan arızalı stringe akabilecek ters akım modül, kablo ya da konektör sınırını aşabilecekse değerlendirilir. Karar; string sayısı, proje Isc değeri, modül maksimum seri sigorta sınırı, inverter reverse-current bilgisi, kablo kapasitesi ve gPV sigortanın DC kesme yeteneğiyle birlikte verilmelidir; bu rehber doğrudan amper seçimi değildir.

## String sigortası hangi arızaya karşı kullanılır?

GES string sigortası, panelin normal çalışma akımını sınırlamak için değil arızalı bir stringe diğer paralel stringlerden veya harici bir DC kaynaktan akabilecek ters akımı kesmek için kullanılır. Bir string kısa devre veya kutup hatası yaşadığında aynı bara üzerindeki sağlıklı stringler arıza noktasını besleyebilir. Bu akım modülün bağlantı iletkenini, konnektörünü, junction box bileşenlerini veya string kablosunu termik olarak zorlayabilir.

IEC 62548-1, PV dizilerinin tasarımında aşırı akım korumasını string sayısı, olası arıza akımı, kablo taşıma kapasitesi ve modül üreticisinin sınırlarıyla birlikte değerlendirir. Bu nedenle “her stringe mutlaka sigorta” ya da “iki stringte hiçbir zaman sigorta gerekmez” biçimindeki tek cümleler yerine, en kötü ters akım yolunun hesaplanması gerekir.

- String sigortasını DC ayırıcı veya AFCI ile aynı görevde kabul etmeyin.
- Normal kısa devre akımı ile paralel stringlerden gelebilecek ters akımı ayrı gösterin.
- Pozitif ve negatif kutupların koruma düzenini inverter topolojisi ve topraklama yaklaşımıyla birlikte doğrulayın.

_Kaynaklar: S1, S2, S3_

## Ters akım ön hesabı hangi girdilerle yapılır?

Ön değerlendirmede paralel bağlı toplam string sayısı, her stringin proje kısa devre akımı, sıcaklık ve ışınım düzeltmeleri, inverterin veya başka DC kaynağın olası geri besleme akımı ve kablo sınırı kaydedilir. Arızalı tek string varsayımında, diğer stringlerin katkısı yaklaşık olarak sağlıklı paralel string sayısıyla ilişkilendirilir; ancak nihai değer standarttaki tasarım katsayıları ve üretici verileriyle belirlenmelidir.

İnverter veri sayfasındaki maksimum giriş akımı veya MPPT akımı, tek başına stringe gelebilecek ters akım değildir. İnverterin DC giriş koruması, olası geri besleme davranışı ve dahili sigorta düzeni marka/model dokümanından doğrulanmalıdır. Birleştirme kutusu, inverter girişi ve string kablosu farklı koruma sınırlarına sahip olabilir.

- Modül Isc ve sıcaklık katsayısı
- Paralel string sayısı ve MPPT dağılımı
- Modül maksimum seri sigorta değeri
- String kablosu kesiti, döşeme ve akım taşıma kapasitesi
- İnverter üreticisinin maksimum reverse current bilgisi
- Dahili veya harici gPV sigorta yuvasının anma sınırı

_Kaynaklar: S1, S2, S3_

## Hangi durumda string sigortası incelemesi zorunlu hâle gelir?

Paralel stringlerden arızalı stringe akabilecek hesap akımı, modül üreticisinin izin verdiği ters akım veya maksimum seri sigorta sınırını aşma ihtimali taşıyorsa string bazlı aşırı akım koruması değerlendirilir. Ayrıca string kablosunun taşıma kapasitesi, konektör ve birleştirme kutusu sınırları da korunmalıdır. Karar yalnız string adedine değil bütün arıza yoluna dayanır.

Fronius dokümanı, string sigortalarının modül üreticisinin belirttiği maksimum seri sigorta değerine ve kullanılan modüllere uygun seçilmesini ister. SMA teknik verileri ise bazı inverterlerde izin verilen maksimum string kısa devre akımı ve maksimum reverse current gibi giriş sınırlarını açıklar. Bu değerler, başka üreticinin inverterine veya farklı modül kombinasyonuna doğrudan taşınamaz.

- Aynı MPPT’ye bağlanan stringleri gerçek bağlantı şemasına göre gruplayın.
- Doğu-batı veya farklı modül/string uzunluklarını aynı kabul etmeyin.
- Yalnız sigorta yuvası bulunduğu için sigorta değerini tahmin etmeyin.

_Kaynaklar: S1, S2, S3_

## gPV sigorta değeri ve kesme kapasitesi nasıl koordine edilir?

Modül etiketindeki maksimum seri sigorta değeri seçilecek sigortanın otomatik anma değeri değildir; aşılmaması gereken üretici sınırıdır. Sigorta, normal işletme ve beklenen çevresel koşullarda istenmeyen açma yapmamalı, arıza akımında ise kablo ve modül sınırları aşılmadan çalışmalıdır. DC gerilim anma değeri, kesme kapasitesi, gPV kullanım kategorisi, kutup düzeni ve sıcaklık deratingi birlikte kontrol edilir.

Sigorta iletkeni korusa bile DC ark riskini, izolasyon hatasını veya ayırma görevini tek başına çözmez. AFCI, izolasyon izleme, DC ayırıcı, SPD ve topraklama farklı tehlikeleri yönetir. Koruma dosyasında her cihazın görevi ve diğer cihazla koordinasyonu ayrı satırda gösterilmelidir.

- Sigorta anma akımı ile modül maksimum seri sigorta sınırını ayırın.
- Sigortanın DC sistem gerilimi ve olası kısa devre akımı için kesme kapasitesini doğrulayın.
- Sigorta yuvası, terminal ve kablonun sıcaklık sınıfını birlikte değerlendirin.
- Yedek sigorta değişiminde aynı tip, anma ve üretici uyumluluğunu belgeleyin.

_Kaynaklar: S1, S2, S3_

## Saha ekibi için güvenli string koruma kanıt dosyası

Kullanıcı veya tesis yöneticisi enerjili DC konnektör açmamalı ve sigorta çekmemelidir. Güvenli görev; modül veri sayfasını, inverter modelini, string sayısını, tek hat şemasını, kablo kesitini ve mevcut sigorta etiketini toplamak; yetkili GES tasarımcısından ters akım hesabı ve koruma koordinasyon tablosu istemektir.

Kanıt dosyasında her MPPT için string matrisi, Isc girdileri, düzeltme katsayıları, olası ters akım, modül maksimum seri sigorta değeri, seçilen gPV sigorta, DC gerilim ve kesme kapasitesi, kablo sınırı ve kabul sonucu bulunmalıdır. Termal iz, renk değişimi, erime, yanık kokusu veya ark izi varsa dizi tekrar enerjilendirilmemeli ve yetkin ekip devreye alınmalıdır.

- Modül ve inverter dokümanlarının tam sürümünü kaydedin.
- As-built string sayısını proje string sayısıyla karşılaştırın.
- Sigorta değişim geçmişi ve tekrarlayan açmaları arıza kaydı olarak saklayın.
- AFCI ve izolasyon alarmlarını sigorta açmasından ayrı zaman çizelgesinde izleyin.

_Kaynaklar: S1, S2, S3_

## Sık sorulan sorular

### İki paralel string varsa sigorta kesinlikle gerekir mi?

Tek başına iki string bilgisi yeterli değildir. Diğer stringden ve inverterden gelebilecek en kötü ters akım; modül, kablo ve üretici sınırlarıyla karşılaştırılmalıdır. Nihai karar IEC 62548-1 ve ekipman dokümanlarına göre projelendirilir.

_Kaynaklar: S1, S2, S3_

### Modüldeki maksimum seri sigorta değeri seçilecek sigorta mıdır?

Hayır. Bu değer üreticinin aşılmamasını istediği üst sınırdır. Seçilecek gPV sigortanın normal akım, tasarım katsayıları, kablo sınırı, DC gerilim ve kesme kapasitesiyle koordine edilmesi gerekir.

_Kaynaklar: S1, S2_

### İnverterde sigorta yuvası varsa herhangi bir gPV sigorta takılabilir mi?

Hayır. İnverterin izin verdiği tip ve anma aralığı, modül maksimum seri sigorta değeri, string akımı, yuva sıcaklık sınırı ve üretici talimatı birlikte doğrulanmalıdır.

_Kaynaklar: S2, S3_

### AFCI string sigortasının yerine geçer mi?

Hayır. AFCI seri DC arkı algılamayı, string sigortası ise uygun tasarımda aşırı ters akımı kesmeyi hedefler. İzolasyon izleme, ayırma ve SPD de farklı koruma görevleridir.

_Kaynaklar: S1, S2, S3_

## İnsan onay komutu

PR sahibinin veya repository yetkilisinin yorumu:

```text
/cms approve ges-string-sigortasi-ters-akim-maksimum-seri-sigorta
```

Onay iş akışı kalite puanı, kaynak güncelliği, iç linkler, kanibalizasyon ve risk sınırlarını yeniden çalıştırmadan canonical dosya üretmez.
