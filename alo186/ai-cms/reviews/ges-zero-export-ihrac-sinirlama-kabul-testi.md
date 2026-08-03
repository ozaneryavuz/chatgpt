# ALO186 AI CMS inceleme paketi — ges-zero-export-ihrac-sinirlama-kabul-testi

> Bu dosya canonical yayına dahil edilmez. PR incelemesi ve insan onayı için üretilmiştir.

## Durum

- State: **approved**
- Risk: **high**
- Model: **gpt-5.6-thinking**
- Kalite: **88/100**
- Benzerlik: **0.35** — https://alo186.com/haberler/ges-zero-export-ct-yonu-ihracat-siniri-kabul
- Kelime: **852**

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

- **S1 · EPDK** — [Elektrik piyasasında lisanssız elektrik üretimi](https://www.epdk.gov.tr/Detay/Icerik/3-0-92-0-0-5/Elektrik%20Piyasas%C4%B1) — erişim 2026-08-03 — birincil
- **S2 · SMA Solar Technology** — [Configuring Limitation of Active Power Feed-In](https://manuals.sma.de/HM-20/en-US/1071201163.html) — erişim 2026-08-03 — birincil
- **S3 · SMA Solar Technology** — [Active power limitation with the SMA Data Manager M](https://manuals.sma.de/Business-Systeme-PL/en-US/14620400779.html) — erişim 2026-08-03 — birincil
- **S4 · Huawei** — [Setting Limited Feed-in Parameters](https://support.huawei.com/enterprise/en/doc/EDOC1100273864/e17fd2ae/setting-limited-feed-in-parameters) — erişim 2026-08-03 — birincil

## SEO

- Title: `GES Zero Export: İhracat Sınırlama Kabul Testi`
- H1: `GES zero export nasıl çalışır, sayaç ve haberleşme arızasında nasıl test edilir?`
- Description: `Şebekeye enerji vermemesi gereken GES’te sayaç yönü, faz bazlı ölçüm, kontrol gecikmesi ve haberleşme arızası senaryosunu kanıtlayın.`
- Canonical: `/haberler/ges-zero-export-ihrac-sinirlama-kabul-testi`
- Birincil anahtar kelime: `GES zero export kabul testi`

## Doğrudan cevap

Zero export, inverter gücünü sabit bir yüzdeye kısmak değil; bağlantı noktasındaki çift yönlü sayaç veya güç sensörü verisine göre üretimi kapalı çevrim düzenleyerek şebekeye verilen aktif gücü hedef sınırda tutmaktır. Kabul testi; sayaç yönü ve faz eşlemesi, toplam veya faz bazlı kontrol modu, yükün ani düşmesi, kontrol gecikmesi, haberleşme kopması, cihaz yeniden başlaması ve varsa batarya şarj-deşarjını kapsamalıdır. Üretici dokümanları kontrol çevrimi nedeniyle kısa süreli artık ihracın oluşabileceğini belirttiğinden, “0 kW” sonucu yalnız tek ekran görüntüsüyle değil zaman damgalı yüksek çözünürlüklü kayıtla doğrulanmalıdır.

## Zero export ile sabit güç sınırı arasındaki fark nedir?

Zero export kontrolü, tesisin bağlantı noktasındaki net aktif gücü izler. Tüketim yükseldiğinde inverter üretimi artırabilir; tüketim aniden düştüğünde şebekeye taşmayı önlemek için üretimi azaltır. Bu nedenle yalnız inverter çıkış gücüne bakmak yeterli değildir; kontrolün referansı bağlantı noktasındaki ithalat-ihracat yönlü ölçümdür.

SMA dokümanı 0 kW veya yüzde 0 ayarını zero export olarak tanımlar ve kontrol çevrimi nedeniyle kaçınılmaz küçük bir enerji miktarının şebekeye çıkabileceğini belirtir. Kabul kriteri, dağıtım şirketi şartı ve üretici kabiliyeti birlikte değerlendirilerek güç, enerji ve süre sınırlarıyla yazılmalıdır.

- Kontrol noktasını inverter çıkışı değil şebeke bağlantı noktası olarak tanımlayın.
- kW sınırı ile dönemsel kWh ihracını ayrı ölçün.
- Toplam güç ve faz bazlı sınır seçeneklerini karıştırmayın.
- Kabul toleransını EDAŞ ve üretici dokümanıyla yazılılaştırın.

_Kaynaklar: S1, S2, S3_

## Sayaç yönü ve faz eşlemesi nasıl doğrulanmalıdır?

İhracat sınırlama sistemi yanlış akım trafosu yönü, ters faz sırası, yanlış sayaç oranı veya hatalı bağlantı noktası tanımıyla çalışıyormuş gibi görünebilir. Önce yük açıkken her fazın güç işareti, akım-gerilim eşleşmesi ve toplam aktif güç bağımsız ölçümle karşılaştırılmalıdır.

Huawei sınırlı besleme ayarları toplam güç ile her fazın ayrı sınırlandığı modları ayırır. Üç faz dört iletkenli sistemlerde asimetrik yük varsa yalnız toplam net gücün sıfır görünmesi bir fazdan ihracı gizleyebilir. Şebeke şartı faz bazlı sınır istiyorsa kabul kaydı her faz için tutulmalıdır.

- Sayaç ve CT yönünü kontrollü ithalat durumunda doğrulayın.
- Faz isimlerini inverter, sayaç ve ana panoda eşleştirin.
- Sayaç çarpanı ve haberleşme ölçeklerini kontrol edin.
- Asimetrik yükte her fazın ithalat-ihracat işaretini kaydedin.

_Kaynaklar: S3, S4_

## Ani yük değişiminde kontrol performansı nasıl test edilir?

En kritik senaryo, PV üretimi yüksekken büyük bir tesis yükünün aniden devreden çıkmasıdır. Kontrolör ölçümü alır, komutu hesaplar, haberleşme üzerinden inverterlere gönderir ve inverter çıkışı yeni değere iner. Bu zincirin toplam gecikmesi kısa süreli ihracın büyüklüğünü belirler.

SMA, yük basamaklarını karşılamak için güvenlik mesafesi sağlayan negatif bir sınır değerinin gerekebileceğini; Huawei ise ayar dönemleri, yükseltme eşiği ve kontrol süresi gibi parametreler tanımlar. Test; farklı güneşlenme ve yük seviyelerinde en az üç yük düşürme ve yük artırma olayıyla tekrarlanmalıdır.

- Yüksek üretimde büyük yükü kontrollü olarak azaltma senaryosu oluşturun.
- En yüksek ihracat kW, olay süresi ve olay enerjisini kaydedin.
- Farklı yük ve güneşlenme seviyelerinde testi tekrarlayın.
- Gerekiyorsa güvenlik marjını ölçümle ayarlayın; rastgele değer kullanmayın.

_Kaynaklar: S2, S3, S4_

## Sayaç veya haberleşme arızasında sistem ne yapmalıdır?

Zero export, sayaç verisi ve kontrol haberleşmesine bağımlıdır. Sayaç verisi donarsa, ağ koparsa veya kontrolör yeniden başlarsa inverterin son komutta üretime devam etmesi şebekeye istenmeyen güç verebilir. Bu nedenle fail-safe davranış devreye alma dosyasının zorunlu parçasıdır.

SMA dokümanları haberleşme yokluğunda fallback değerini ve zaman aşımını; Huawei dokümanları sayaç verisi alınamadığında uygulanacak aktif güç çıkış limitini tanımlar. Testte sayaç haberleşmesi, kontrolör-inverter iletişimi ve kontrolör enerjisi ayrı ayrı kesilerek sonuç kaydedilmelidir.

- Sayaç iletişimini ve inverter kontrol iletişimini ayrı test edin.
- Zaman aşımı ve fallback güç değerini belgeleyin.
- Kontrolör yeniden başlarken ihracat kaydını izleyin.
- Arıza halinde güvenli kısıtlama çalışmıyorsa tesisi kabul etmeyin.

_Kaynaklar: S3, S4_

## Teknik kabul ile lisanssız üretim süreci nasıl ayrılır?

Zero export fonksiyonunun çalışması, tesisin bağlantı ve kullanım yükümlülüklerini kendiliğinden ortadan kaldırmaz. EPDK lisanssız üretim sayfası yönetmelik, başvuru belgeleri, bağlantı ve sistem kullanım anlaşmaları ile mahsuplaşma usullerini ayrı resmî dokümanlar olarak yayımlar. Tesisin hukuki bağlantı modeli ilgili EDAŞ ve güncel mevzuattan doğrulanmalıdır.

Kabul dosyasında tek hat, sayaç ve CT şeması, cihaz modelleri ve yazılım sürümleri, ayar ekranları, faz bazlı trend, yük basamağı testleri, haberleşme arızası sonuçları, alarm kayıtları ve imzalı kabul kriterleri bulunmalıdır. Mevcut sistem tüm senaryolarda şartı sağlıyorsa yeni kontrolör veya sayaç satın almak gerekmeyebilir.

- Teknik zero export testini bağlantı izni yerine kullanmayın.
- Cihaz modeli, firmware ve ayar yedeğini dosyalayın.
- Ham trend ile özet kabul tablosunu birlikte saklayın.
- Yeterli sistem varsa gereksiz donanım değişiminden kaçının.

_Kaynaklar: S1, S2, S3, S4_

## Sık sorulan sorular

### Zero export ayarı 0 kW ise şebekeye hiç enerji çıkmaz mı?

Kontrol çevrimi ve yükün ani değişmesi nedeniyle kısa süreli küçük ihracat oluşabilir. Kabul, tek anlık değerle değil yüksek çözünürlüklü güç ve enerji trendiyle ve EDAŞ’ın şartıyla değerlendirilmelidir.

_Kaynaklar: S2, S3_

### Zero export için çift yönlü sayaç veya güç sensörü gerekli mi?

Kapalı çevrim kontrolün bağlantı noktasındaki net gücü bilmesi gerekir. Uyumlu sayaç veya güç sensörü, doğru faz ve yön bağlantısı ile kontrolör-inverter haberleşmesi üretici sistem tasarımına göre doğrulanmalıdır.

_Kaynaklar: S2, S3, S4_

### İletişim kesilirse inverterler ne yapmalıdır?

Üretici sisteminde zaman aşımı ve fallback davranışı tanımlanmalıdır. Sayaç veya kontrol komutu kaybolduğunda çıkışın güvenli sınıra inmesi ayrı arıza testleriyle kanıtlanmalıdır.

_Kaynaklar: S3, S4_

### Zero export kullanmak lisanssız üretim başvurusunu gereksiz yapar mı?

Hayır. Teknik ihracat sınırlaması ile bağlantı, anlaşma, ölçüm ve mevzuat yükümlülükleri ayrı konulardır. Tesis modeli için güncel EPDK ve ilgili dağıtım şirketi şartları doğrulanmalıdır.

_Kaynaklar: S1_

## İnsan onay komutu

PR sahibinin veya repository yetkilisinin yorumu:

```text
/cms approve ges-zero-export-ihrac-sinirlama-kabul-testi
```

Onay iş akışı kalite puanı, kaynak güncelliği, iç linkler, kanibalizasyon ve risk sınırlarını yeniden çalıştırmadan canonical dosya üretmez.
