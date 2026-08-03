# ALO186 AI CMS inceleme paketi — ges-inverter-anti-islanding-sebeke-kaybi-yeniden-baglanma-kabul

> Bu dosya canonical yayına dahil edilmez. PR incelemesi ve insan onayı için üretilmiştir.

## Durum

- State: **approved**
- Risk: **legal**
- Model: **gpt-5.6-thinking**
- Kalite: **88/100**
- Benzerlik: **0.40** — https://www.alo186.com/haberler/ges-inverter-anti-islanding-ada-calismasi-koruma-testi
- Kelime: **961**

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

- **S1 · IEC** — [IEC 62116:2014 — Test procedure of islanding prevention measures](https://webstore.iec.ch/en/publication/6479) — erişim 2026-08-03 — birincil
- **S2 · IEC** — [IEC 61727:2004 — Photovoltaic systems, characteristics of the utility interface](https://webstore.iec.ch/en/publication/5736) — erişim 2026-08-03 — birincil
- **S3 · IEC** — [IEC TS 62786-2:2026 — Additional grid-connection requirements for PV generation](https://webstore.iec.ch/en/publication/90029) — erişim 2026-08-03 — birincil
- **S4 · EPDK** — [Elektrik Piyasasında Lisanssız Elektrik Üretimi — resmî mevzuat ve anlaşmalar](https://www.epdk.gov.tr/Detay/Icerik/3-0-0-1160/elektrik-piyasasinda-lisanssiz-elektrik-uretimi) — erişim 2026-08-03 — birincil
- **S5 · IEC** — [IEC 62446-1:2016+A1:2018 — Grid-connected PV documentation, commissioning and inspection](https://webstore.iec.ch/en/publication/63726) — erişim 2026-08-03 — birincil

## SEO

- Title: `GES İnverter Anti-Islanding ve Yeniden Bağlanma Kabul Testi`
- H1: `GES inverter anti-islanding ve şebekeye yeniden bağlanma nasıl test edilir?`
- Description: `GES inverterin şebeke kaybında enerjilemeyi kesmesini, ada modu ayrımını, koruma ayarlarını ve güvenli yeniden bağlanmayı zaman kayıtlarıyla kabul edin.`
- Canonical: `/haberler/ges-inverter-anti-islanding-sebeke-kaybi-yeniden-baglanma-kabul`
- Birincil anahtar kelime: `GES inverter anti-islanding testi`

## Doğrudan cevap

Anti-islanding kabulü, şebeke kesildiğinde inverter ekranında bir hata görülmesiyle tamamlanmaz. Şebekeye paralel çıkışın enerji vermeyi hangi sürede bıraktığı, gerilim ve frekans koruma ayarları, faz kaybı, üretim-yük dengesine yakın zor senaryo, çoklu inverter davranışı ve şebeke döndüğünde yeniden bağlanma gecikmesi zaman eşzamanlı kayıtlarla doğrulanmalıdır. Yedekleme veya EPS çıkışı varsa bu kontrollü ada devresi şebekeye paralel çıkıştan fiziksel ve işlevsel olarak ayrılmalıdır. Test, şebekeyi rastgele açıp kapatarak değil, onaylı plan ve yetkin ekip tarafından uygun test düzeniyle yapılmalıdır.

## Anti-islanding, yedekleme ve gerçek ada modu nasıl ayrılır?

Şebekeye paralel PV inverteri, dağıtım şebekesi gerilimsiz kaldığında bağlı hattı beslemeye devam etmemelidir. Anti-islanding işlevi bu istenmeyen ada durumunu algılayıp enerji aktarımını durdurmayı amaçlar. Buna karşılık hibrit inverterin EPS/backup çıkışı veya mikroşebeke kontrolörü, şebekeden güvenli biçimde ayrılmış özel bir bölümde kontrollü ada çalışması yapabilir.

Kabul dosyasında bağlantı noktası, ana ayırma elemanı, inverter AC çıkışı, EPS/backup panosu, transfer cihazı, jeneratör ve batarya tek hatta gösterilmelidir. Kullanıcı “elektrik kesilince GES çalışıyor” ifadesini kullanıyorsa hangi baranın enerjili kaldığı ve şebekeye geri besleme ihtimalinin nasıl engellendiği açıkça kanıtlanmalıdır.

- Şebekeye paralel çıkış ile EPS/backup çıkışını ayrı renk ve kesicilerle gösterin.
- Şebeke ayırma elemanının kutup sayısı ve geri bildirimini kaydedin.
- Jeneratör veya mikroşebeke varsa kontrol otoritesini ve interlockları tanımlayın.
- Anti-islanding ile kontrollü ada işlevini aynı özellik gibi sunmayın.

_Kaynaklar: S1, S2, S3, S4_

## Koruma ayarları ve sertifikalar hangi kanıtlarla doğrulanır?

İnverterin tip testi veya uygunluk sertifikası, kullanılan model ve firmware için önemli bir başlangıç kanıtıdır; ancak sahadaki ülke kodu, gerilim-frekans eşikleri, gecikmeler, yeniden bağlanma süresi ve haricî koruma rölesi ayarlarını tek başına kanıtlamaz. IEC 62116, PV inverterlerde ada önleme performansının tekrarlanabilir laboratuvar testini; IEC 61727 ise şebeke arayüz özelliklerini kapsar.

IEC TS 62786-2:2026, alçak ve orta gerilim PV sistemlerinde bağlantı, koruma, arıza sırasında davranış, güç kontrolü ve uzaktan izleme gerekliliklerini daha geniş sistem bağlamında ele alır. Sahada inverter parametre yedeği, ülke kodu, seri numarası, firmware, koruma rölesi ayarları ve bağlantı anlaşmasının teknik koşulları aynı sürüm tablosunda eşleştirilmelidir.

- Model ve firmware ile sertifika kapsamının aynı olduğunu doğrulayın.
- Ülke kodu ve koruma parametrelerinin ekran görüntüsü veya imzalı çıktısını alın.
- Haricî röle, kontaktör ve kesici geri bildirimlerini inverter işlevinden ayrı gösterin.
- Bağlantı anlaşması ve proje tarihindeki EDAŞ koşullarını yeniden doğrulayın.

_Kaynaklar: S1, S2, S3, S4_

## Şebeke kaybı hangi senaryolarla sınanmalıdır?

Test matrisi tam şebeke kaybının yanında mümkünse faz kaybı, gerilim ve frekans sınırı, haberleşme kesintisi, inverterlerin farklı güç seviyeleri ve çoklu inverter ortak bara davranışını kapsamalıdır. Ada önleme için zorlayıcı koşullardan biri, yerel üretim ile yükün birbirine yakın olduğu durumdur; yalnız inverter boşta veya çok düşük güçteyken yapılan tek açma testi yeterli kanıt sayılmamalıdır.

Her senaryoda bağlantı noktası gerilimi, frekans, inverter AC akımı, aktif-reaktif güç, ana kesici durumu, koruma rölesi olayı ve inverter logu ortak zaman tabanında kaydedilmelidir. Enerjili şebeke ve üretim ekipmanında test yalnız yetkin ekip, onaylı manevra planı ve uygun test cihazıyla yürütülmelidir.

- Tam şebeke kaybı ve faz kaybını ayrı senaryolar yapın.
- Düşük, orta ve yüksek üretim noktalarında davranışı karşılaştırın.
- Çoklu inverterlerde her ünitenin ve ortak korumanın olay zamanını kaydedin.
- Üretim-yük dengesi yakın senaryoyu risk değerlendirmesine göre yetkili test planına ekleyin.

_Kaynaklar: S1, S2, S3, S5_

## Şebeke döndüğünde yeniden bağlanma nasıl kabul edilir?

Şebeke geriliminin geri gelmesi inverterin anında paralel olması gerektiği anlamına gelmez. Gerilim ve frekansın izin verilen aralıkta belirli süre kararlı kalması, yeniden bağlanma gecikmesi, faz senkronu, güç rampası ve varsa uzaktan izin zinciri model ve bağlantı koşullarına göre doğrulanmalıdır. Kısa süreli gerilim dönüşlerinde tekrarlı açma-kapama veya kontaktör çarpması oluşmamalıdır.

EPS veya batarya destekli ada çalışmasından şebekeye dönüşte transfer cihazı, nötr düzeni, jeneratör interlocku ve yüklerin yeniden devreye alınma sırası ayrıca sınanmalıdır. Anti-islanding testi başarılı olsa bile yanlış transfer mantığı şebekeye paralel olmayan başka bir güvenlik problemi oluşturabilir.

- Yeniden bağlanma gecikmesini ve kararlılık penceresini olay kaydından ölçün.
- İlk güç rampasını ve P/Q davranışını trendleyin.
- EPS/backup barasının şebeke dönüşündeki transfer sırasını doğrulayın.
- Başarısız senkron veya tekrar kesinti durumunda güvenli geri dönüşü sınayın.

_Kaynaklar: S2, S3, S4, S5_

## Anti-islanding kabul dosyasında hangi belgeler bulunmalıdır?

Teslim dosyası; onaylı tek hat, bağlantı noktası tanımı, inverter model-seri-firmware, sertifika kapsamı, ülke kodu ve parametre yedeği, haricî koruma rölesi ve kesici matrisi, test senaryoları, kalibre cihaz bilgisi, ortak zamanlı V-f-P-Q-akım trendleri, olay logları, yeniden bağlanma sonuçları ve imzalı geçti-kaldı tablosunu içermelidir.

EPDK lisanssız üretim sayfası, yönetmelik, bağlantı/kullanım anlaşmaları ve başvuru belgelerini resmî süreç altında toplar. Bu nedenle bir laboratuvar sertifikası veya başarılı saha testi, ilgili dağıtım şirketinin proje, bağlantı ve kabul yükümlülüklerinin yerine geçtiği şeklinde sunulmamalıdır. Mevcut inverter ve koruma zinciri bütün senaryoları kanıtla geçiyorsa sırf daha yeni bir inverter satın almak gerekmez.

- Testte kullanılan ayarların son parametre yedeğiyle aynı olduğunu doğrulayın.
- Sertifika, seri numarası ve firmware eşleşmesini dosyada görünür yapın.
- EDAŞ bağlantı ve kabul belgelerini teknik test raporundan ayrı ama bağlantılı saklayın.
- Kanıt yeterliyse gereksiz inverter veya koruma rölesi değişimi önermeyin.

_Kaynaklar: S1, S2, S3, S4, S5_

## Sık sorulan sorular

### Şebeke kesilince on-grid GES inverteri çalışmaya devam eder mi?

Şebekeye paralel çıkış, istenmeyen ada oluşmaması için enerji vermeyi durdurmalıdır. Hibrit sistemde ayrı EPS/backup devresi kontrollü ada olarak çalışabilir; bu devrenin şebekeden güvenli ayrılması gerekir.

_Kaynaklar: S1, S2, S3_

### İnverterin anti-islanding sertifikası saha testini gereksiz yapar mı?

Hayır. Sertifika tip testini destekler; sahadaki ülke kodu, firmware, koruma ayarları, haricî röle/kesici, kablolama ve yeniden bağlanma davranışı ayrıca doğrulanmalıdır.

_Kaynaklar: S1, S3, S5_

### Anti-islanding testi için ana şalteri kapatmak yeterli midir?

Tek bir manevra yalnız sınırlı gözlem sağlar. Faz kaybı, farklı üretim seviyeleri, çoklu inverter, yük-üretim dengesi, koruma olayları ve yeniden bağlanma gibi senaryolar onaylı test planında ele alınmalıdır; kullanıcı kendi başına enerjili manevra yapmamalıdır.

_Kaynaklar: S1, S3, S5_

### Anti-islanding testi geçerse EDAŞ kabulü otomatik tamamlanır mı?

Hayır. Teknik test, bağlantı anlaşması, proje, koruma koordinasyonu, sayaç ve ilgili resmî kabul belgelerinin yerine geçmez. Proje tarihindeki dağıtım şirketi koşulları ayrıca tamamlanmalıdır.

_Kaynaklar: S3, S4_

## İnsan onay komutu

PR sahibinin veya repository yetkilisinin yorumu:

```text
/cms approve ges-inverter-anti-islanding-sebeke-kaybi-yeniden-baglanma-kabul
```

Onay iş akışı kalite puanı, kaynak güncelliği, iç linkler, kanibalizasyon ve risk sınırlarını yeniden çalıştırmadan canonical dosya üretmez.
