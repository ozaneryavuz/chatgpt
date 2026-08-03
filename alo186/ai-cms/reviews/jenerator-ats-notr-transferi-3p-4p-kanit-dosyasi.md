# ALO186 AI CMS inceleme paketi — jenerator-ats-notr-transferi-3p-4p-kanit-dosyasi

> Bu dosya canonical yayına dahil edilmez. PR incelemesi ve insan onayı için üretilmiştir.

## Durum

- State: **approved**
- Risk: **high**
- Model: **gpt-5.6-thinking**
- Kalite: **100/100**
- Benzerlik: **0.36** — https://www.alo186.com/haberler/jenerator-ats-3-kutuplu-4-kutuplu-notr-transferi-rcd
- Kelime: **936**

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

- **S1 · IEC** — [IEC 60364-5-55:2011+A1:2012+A2:2016 — Low-voltage electrical installations, Part 5-55](https://webstore.iec.ch/en/publication/25534) — erişim 2026-08-03 — birincil
- **S2 · Schneider Electric ASCO** — [Neutral Configurations in Transfer Switches](https://www.se.com/us/en/download/document/ASC-DB-NCTS/) — erişim 2026-08-03 — birincil
- **S3 · Schneider Electric** — [Comparison of Neutral Wire Distribution Options for Data Centers](https://www.se.com/us/en/download/document/SPD_WP41_EN/) — erişim 2026-08-03 — birincil

## SEO

- Title: `Jeneratör ATS Nötr Transferi: 3P/4P Kanıt Dosyası`
- H1: `Jeneratör ATS’de nötr ne zaman anahtarlanır? 3P/4P kanıt planı`
- Description: `Jeneratör ATS nötr transferinde 3P/4P kararını; N–PE bağı, ayrı türetilmiş kaynak, RCD testi ve saha kabul kanıtlarıyla doğrulayın.`
- Canonical: `/haberler/jenerator-ats-notr-transferi-3p-4p-kanit-dosyasi`
- Birincil anahtar kelime: `jeneratör ATS nötr transferi`

## Doğrudan cevap

Jeneratör ATS nötr transferinde 3P veya 4P seçimi yalnız faz sayısına göre yapılmaz. Jeneratörün ayrı türetilmiş kaynak olup olmadığı, şebeke ve jeneratördeki N–PE bağları, ATS’nin nötr kontak sırası, RCD yerleşimi ve topraklama sistemi birlikte doğrulanmalıdır. Sonuç; tek hat, bağlantı şeması ve ölçümlü saha kabul dosyasıyla kanıtlanmalıdır.

## 3P veya 4P kararı neden tek satırdan verilemez?

Jeneratör ATS nötr transferi, yalnız transfer şalterinin kutup sayısını seçmek değildir. Karar; şebeke kaynağının nötr-toprak bağı, jeneratör sargı bağlantısı, jeneratör üzerindeki N–PE bağı, tesisin topraklama sistemi, RCD yerleşimi ve ATS’nin kontak sırasıyla birlikte değerlendirilir. Aynı cihaz bir projede nötrü anahtarlamadan kullanılabilirken başka bir projede nötrün fazlarla birlikte güvenli biçimde ayrılması gerekebilir.

IEC 60364-5-55, düşük gerilim jeneratör setlerinin tesisata bağlanmasında koruma, ayırma, nötr ve topraklama düzeninin sistem bütünlüğü içinde ele alınmasını ister. Bu nedenle “üç fazsa 4 kutuplu olmalıdır” veya “nötr hiçbir zaman anahtarlanmaz” gibi evrensel cümleler güvenli proje kararı değildir; tek hat şeması ve kaynak sınıflandırması kanıtlanmalıdır.

- Şebeke ve jeneratör kaynaklarının nötr referansını ayrı ayrı işaretleyin.
- ATS’nin faz ve nötr kontaklarının açma-kapama sırasını üretici dokümanından doğrulayın.
- Ana dağıtım panosu, jeneratör panosu ve ATS içindeki bütün N–PE bağlantı noktalarını tek çizimde gösterin.

_Kaynaklar: S1, S2_

## Ayrı türetilmiş kaynak kararı hangi kanıtlarla verilir?

Jeneratör nötrü şebeke nötründen transfer sırasında tamamen ayrılıyor ve jeneratör tarafında tanımlı bir nötr-toprak bağlantısı bulunuyorsa jeneratör ayrı türetilmiş kaynak yaklaşımıyla ele alınabilir. Bu senaryoda üç faz ile birlikte nötrün de anahtarlanması, kaynaklar arasında istenmeyen paralel nötr yolu kalmaması ve seçilen kaynağın kendi referansının korunması için 4 kutuplu ATS çözümü gündeme gelir.

Nötr şebeke tarafına sürekli bağlı kalıyor ve sistemde yalnız ana servis noktasında tanımlı N–PE bağı kullanılıyorsa solid neutral düzeni uygulanabilir. Jeneratör üzerinde ikinci bir N–PE bağı bırakılırsa normal yük akımının bir bölümü koruma iletkeni, kablo tavaları veya metal borular üzerinden dolaşabilir. Kanıt dosyası, bu iki mimariden hangisinin seçildiğini ve seçilmeyen mimarinin neden uygulanmadığını açıkça yazmalıdır.

- Jeneratör üretici bağlantı şeması ve nötr bond bilgisi
- ATS marka/model, kutup sayısı ve neutral switching tipi
- Tesis topraklama sistemi ve ana eşpotansiyel bağlantı noktası
- Tek hat üzerinde normal ve jeneratör çalışma durumlarının ayrı gösterimi

_Kaynaklar: S1, S2, S3_

## RCD, UPS ve elektronik yükler nötr kararını nasıl etkiler?

RCD, fazlardan çıkan akımla nötrden dönen akım arasındaki farkı izler. Yanlış nötr-toprak topolojisi veya iki farklı N–PE bağı, dönüş akımının bir bölümünü RCD ölçüm toroidinin dışından taşıyabilir ve jeneratör devreye girdiğinde açmaya neden olabilir. Bu durum RCD’nin daha yüksek mA değerli bir cihazla değiştirilerek giderilecek bir arıza değildir; kaynak topolojisi ve gerçek kaçak akımlar ölçülmelidir.

UPS, frekans konvertörü, EV şarj cihazı ve EMC filtreli elektronik yükler normal işletmede kaçak bileşenleri oluşturabilir. Transfer anında nötrün erken açılması veya geç kapanması, hassas yüklerde referans kayması ve geçici gerilimlere yol açabilir. Overlapping neutral veya özel anahtarlama seçenekleri yalnız ATS üreticisinin dokümanı, proje koruma koordinasyonu ve saha kabul testiyle kullanılmalıdır.

- RCD açma akımı ve açma süresini şebeke ve jeneratör modunda ayrı kaydedin.
- Toplam artık akımı kaçak akım pensiyle devre ve kaynak bazında karşılaştırın.
- UPS bypass, jeneratör ve şebeke modlarında nötr sürekliliğini üretici prosedürüne göre doğrulayın.

_Kaynaklar: S1, S2, S3_

## Jeneratör ATS nötr transferi saha kabul planı

Yayınlanabilir kanıt dosyasının temel çıktısı, tasarım varsayımını saha testiyle bağlayan bir kabul tablosudur. Testler enerjili panoda kullanıcı tarafından yapılmamalıdır. Yetkili ekip; enerjisiz süreklilik kontrolleri, N–PE bağ noktası doğrulaması, ATS mekanik ve elektriksel çalışma sırası, PE sürekliliği, çevrim empedansı, RCD testi ve gerçek yük transferini tanımlı bir sırayla yürütmelidir.

Her test için cihaz seri numarası, kalibrasyon durumu, ölçüm noktası, şebeke/jeneratör çalışma modu, beklenen değer, ölçülen değer ve kabul sonucu kaydedilmelidir. Test yalnız “çalıştı” ifadesiyle kapatılmamalı; transfer sırasında alarm, nötr akımı, faz gerilimleri ve kritik yük davranışı zaman damgasıyla ilişkilendirilmelidir.

- Tek hat ve as-built bağlantı şeması eşleşmesi
- N–PE bağ noktalarının görsel ve ölçümsel doğrulaması
- ATS faz/nötr kontak sırası ve mekanik kilitleme testi
- Şebeke ve jeneratör modunda RCD açma süresi
- Kritik yüklerle gerçek transfer ve yeniden transfer kaydı
- Uygunsuzluk, sorumlu taraf ve kapanış kanıtı

_Kaynaklar: S1, S2, S3_

## Kullanıcı hangi bilgiyi toplamalı, neyi yapmamalıdır?

Kullanıcı için somut fayda, panoyu açmak değil doğru teknik ekibi doğru kanıtla yönlendirmektir. ATS marka ve modelini, jeneratör bağlantı şemasını, RCD’nin yalnız hangi çalışma modunda açtığını, etkilenen devreleri ve son bakım tarihini kaydedin. Tek hat şeması yoksa bunun hazırlanmasını; varsa sahadaki bağlantıyla karşılaştırılmasını talep edin.

Elektrik çarpması, ark, duman, yanık kokusu veya iletken ısınması varsa tekrar transfer denemesi yapmayın. Nötr-toprak köprüsü eklemeyin, RCD’yi devre dışı bırakmayın ve ATS kutup bağlantısını değiştirmeyin. Çıktı, yetkili elektrik mühendisi ile jeneratör/ATS servisinin ortak kabul formuna dönüştürülmelidir.

- Fotoğraf yerine cihaz etiketi ve tek hat referansı kaydedin.
- Arızanın şebekede mi, jeneratörde mi, yalnız transfer anında mı oluştuğunu ayırın.
- Servisten yapılan değişikliği değil, değişiklik sonrası test sonuçlarını isteyin.

_Kaynaklar: S1, S2_

## Sık sorulan sorular

### Jeneratör için her zaman 4 kutuplu ATS gerekir mi?

Hayır. Nötrün anahtarlanması, jeneratörün ayrı türetilmiş kaynak olup olmamasına, N–PE bağ noktasına ve tesisin topraklama düzenine bağlıdır. 3P/4P seçimi tek hat şeması ve üretici ATS dokümanıyla doğrulanmalıdır.

_Kaynaklar: S1, S2_

### Jeneratör nötrünü toprağa bağlamak RCD sorununu çözer mi?

Rastgele yeni bir N–PE bağı eklemek sorunu büyütebilir. Aynı sistemde iki bağ paralel dönüş akımı oluşturabilir. Bağın yeri, ATS’nin nötr anahtarlaması ve kaynak sınıflandırması birlikte projelendirilmelidir.

_Kaynaklar: S1, S2_

### Overlapping neutral her hassas yükte gerekli midir?

Hayır. Örtüşmeli nötr özel bir transfer çözümüdür; ATS üreticisinin tasarımı, geçiş sırası, koruma koordinasyonu ve yük davranışı doğrulanmadan genel çözüm olarak kullanılamaz.

_Kaynaklar: S2, S3_

### Kabul dosyasında yalnız RCD testi yeterli midir?

Hayır. Tek hat, N–PE bağları, PE sürekliliği, ATS kontak sırası, çevrim empedansı, şebeke/jeneratör gerilimleri ve gerçek yük transfer kaydı birlikte bulunmalıdır.

_Kaynaklar: S1, S2, S3_

## İnsan onay komutu

PR sahibinin veya repository yetkilisinin yorumu:

```text
/cms approve jenerator-ats-notr-transferi-3p-4p-kanit-dosyasi
```

Onay iş akışı kalite puanı, kaynak güncelliği, iç linkler, kanibalizasyon ve risk sınırlarını yeniden çalıştırmadan canonical dosya üretmez.
