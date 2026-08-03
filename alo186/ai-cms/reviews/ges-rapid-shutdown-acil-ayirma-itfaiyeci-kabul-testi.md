# ALO186 AI CMS inceleme paketi — ges-rapid-shutdown-acil-ayirma-itfaiyeci-kabul-testi

> Bu dosya canonical yayına dahil edilmez. PR incelemesi ve insan onayı için üretilmiştir.

## Durum

- State: **approved**
- Risk: **high**
- Model: **gpt-5.6-thinking**
- Kalite: **88/100**
- Benzerlik: **0.21** — https://www.alo186.com/haberler/ges-rapid-shutdown-dc-izolator-afci-farki
- Kelime: **942**

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

- **S1 · IEC** — [IEC 62548-1:2023 — Photovoltaic arrays, design requirements](https://webstore.iec.ch/en/publication/64171) — erişim 2026-08-03 — birincil
- **S2 · IEC** — [IEC 60364-7-712:2025 — Solar photovoltaic power supply installations](https://webstore.iec.ch/en/publication/65748) — erişim 2026-08-03 — birincil
- **S3 · IEC** — [IEC 63257:2026 — Power line communication for DC shutdown equipment](https://webstore.iec.ch/en/publication/64941) — erişim 2026-08-03 — birincil
- **S4 · SMA Solar Technology** — [Rapid Shutdown Equipment](https://manuals.sma.de/SBSExx-US-50/en-US/13317429131.html) — erişim 2026-08-03 — birincil
- **S5 · SolarEdge** — [Safety First with SolarEdge Commercial PV Systems](https://www.solaredge.com/aus/commercial/safety) — erişim 2026-08-03 — birincil

## SEO

- Title: `GES Rapid Shutdown ve Acil Ayırma Kabul Testi`
- H1: `GES rapid shutdown ve itfaiyeci acil ayırma sistemi nasıl kabul edilir?`
- Description: `GES rapid shutdown sisteminde tetikleyici, modül anahtarı, DC gerilim düşümü, etiket ve yeniden başlatmayı kanıta dayalı kabul edin.`
- Canonical: `/haberler/ges-rapid-shutdown-acil-ayirma-itfaiyeci-kabul-testi`
- Birincil anahtar kelime: `GES rapid shutdown kabul testi`

## Doğrudan cevap

GES’te inverteri kapatmak veya AC kesiciyi açmak, bütün çatı DC iletkenlerinin güvenli gerilime indiğini tek başına kanıtlamaz. Rapid shutdown bulunan bir sistemde tetikleyici, inverter/iletişim, modül veya dizi anahtarları ve DC kablo gerilimi uçtan uca test edilmelidir. Kabul; normal–shutdown durum zinciri, belirlenmiş ölçüm noktalarında gerilim-zaman kaydı, etiketleme, yardımcı besleme kaybı ve kontrollü yeniden başlatma ile yapılır. Bu işlev Türkiye’de her tesis için evrensel zorunluluk gibi sunulmamalı; proje ve yetkili merci şartları doğrulanmalıdır.

## Rapid shutdown, AC ayırma ve DC yük ayırıcısı nasıl ayrılır?

AC ana kesicinin açılması inverterin şebekeye enerji vermesini durdurabilir; fakat PV modülleri ışık aldıkça DC üretmeye devam eder. İnverter üzerindeki DC yük ayırıcısı da yalnız kendi bağlantı sınırındaki iletkenleri ayırabilir. Rapid shutdown ise tasarıma bağlı olarak çatı veya dizi dışına çıkan DC iletkenlerin gerilimini azaltmak için iletişimli modül/dizi anahtarlarını içeren ayrı bir sistem görevidir.

IEC 62548-1 PV dizi tasarımında DC kablolama, koruma, switching, topraklama, izolasyon izleme ve ayırma hükümlerini kapsar. IEC 60364-7-712 PV tesisinin modülden bağlantı noktasına kadar seçim ve uygulama gereklerini tanımlar. Bu standartlar, proje kapsamının bütün bileşenleriyle belgelenmesi gerektiğini destekler; rapid shutdown zorunluluğu ise proje ülkesi, yetkili merci ve seçilen ürün sistemine göre ayrıca belirlenmelidir.

- AC kesici, inverter DC ayırıcı ve rapid shutdown tetikleyicisini ayrı etiketleyin.
- Hangi DC iletkenlerin hangi işlevle gerilimden düşürüldüğünü tek hatta gösterin.
- İnverter kapanmasını modül seviyesinde gerilimsizlik saymayın.
- Proje şartını başka ülkenin mevzuatından otomatik kopyalamayın.

_Kaynaklar: S1, S2, S3_

## Tam rapid shutdown sistemi hangi bileşenlerden oluşur?

Tam sistem; tetikleyici veya initiator, inverter ya da haberleşme vericisi, modül/dizi anahtarları, iletişim yolu, yardımcı besleme, kablolama ve durum geri bildiriminden oluşabilir. Tek bir inverterin PVRSE veya rapid shutdown uyumlu olarak listelenmesi, kurulu tesisin bütün işlevleri yerine getirdiğini tek başına göstermez. Tam ürün kodları ve birlikte çalışma listesi doğrulanmalıdır.

IEC 63257:2026, DC shutdown ekipmanının durumunu güç hattı iletişimiyle bileşenlere iletmeyi ve PV dizisinden çıkan DC kabloların gerilimini acil müdahale ekiplerini destekleyecek şekilde azaltma iletişim gerekliliklerini tanımlar. SMA üretici dokümanı da tam sistemin inverter, PV anahtarları ve tetikleyiciden oluştuğunu; işlev etkinleştirilirken uyumlu modül anahtarlarının bulunması gerektiğini açıklar.

- Tetkileyici, inverter/verici, modül anahtarı ve firmware listesini oluşturun.
- Uyumlu bileşen kombinasyonunu üretici belgesiyle doğrulayın.
- İletişim ve yardımcı besleme yollarını tek hatta işleyin.
- Yalnız inverter etiketini tam sistem uygunluğu saymayın.

_Kaynaklar: S3, S4, S5_

## Shutdown komutu ve DC gerilim düşümü nasıl sınanmalıdır?

Test, tesis normal üretimde kararlı iken başlatılmalı; tetikleyici konumu, inverter durumu, dizi veya modül anahtarı geri bildirimi ve seçilmiş DC ölçüm noktaları ortak zaman çizelgesinde kaydedilmelidir. Gerilim ölçüm cihazı beklenen maksimum DC gerilimine uygun olmalı ve yalnız yetkin ekip tarafından üretici prosedürüne göre bağlanmalıdır.

IEC 63257 iletişimli shutdown sistemlerinde normal/shutdown durumunun bütün üretim bileşenlerine yayılmasını ve dizi dışına çıkan DC kablolarda gerilim azaltma işlevini ele alır. Üretici sistemlerinde hedef süre ve gerilim modele ve uyulan kurala göre değişebilir; örneğin bazı hızlı kapatma sistemleri 30 saniyelik bir sınıra göre tasarlanır. Kabul kriteri ilgili proje ve ürün sertifikasından alınmalı, evrensel tek sayı gibi kullanılmamalıdır.

- Başlangıç DC gerilimi, tetikleme saati ve gerilim-zaman eğrisini kaydedin.
- Birden çok string ve çatı bölgesini temsil eden ölçüm noktaları seçin.
- Sadece ekran mesajına değil fiziksel gerilim ve durum geri bildirimine bakın.
- Kontrolsüz DC ayırma veya çıplak iletken ölçümü yapmayın.

_Kaynaklar: S3, S4, S5_

## İletişim veya yardımcı besleme kaybında sistem nasıl davranmalıdır?

Yangın veya şebeke kaybı sırasında AC yardımcı besleme, ağ veya PLC iletişimi aynı anda kaybolabilir. Tasarımın bu durumda shutdowna geçip geçmediği, son durumu koruyup korumadığı veya arıza alarmı ürettiği ürün belgelerinde tanımlanmalıdır. Fail-safe beklentisi varsayımla değil gerçek sistem mimarisiyle doğrulanmalıdır.

SolarEdge güvenlik açıklaması SafeDC ve Rapid Shutdown işlevlerini ark algılama ve sistem alarmlarından ayrı görevler olarak sunar. SMA dokümanı da rapid shutdown işlevinin yalnız uygun PV anahtarları kurulu olduğunda etkinleştirilmesi gerektiğini belirtir. Kabulde iletişim kablosu, tetikleyici yardımcı beslemesi ve seçilmiş modül anahtarı arızası ayrı senaryolarda sınanmalı; arıza, alarm ve geri dönüş davranışı kaydedilmelidir.

- Tetikleyici beslemesi ve iletişim kaybını ayrı test edin.
- Tek bir modül anahtarı yanıt vermediğinde alarmın görünürlüğünü doğrulayın.
- Şebeke kaybı ile kullanıcı tetikleme komutunu birbirinden ayırın.
- Arıza hâlinde otomatik yeniden enerjilenme olup olmadığını kaydedin.

_Kaynaklar: S4, S5_

## Etiketleme ve yeniden başlatma kabulü nasıl tamamlanır?

İtfaiyeci veya acil durum ekibinin yanlış anahtarı kullanmasını önlemek için tetikleyicinin konumu, işlevi, kapsadığı çatı alanı ve sistem durumu kalıcı ve okunabilir biçimde belirtilmelidir. Tek hat, çatı planı ve saha etiketi aynı adlandırmayı kullanmalıdır. Birden fazla inverter veya bina varsa hangi tetikleyicinin hangi alanı kapattığı açık olmalıdır.

Shutdown sonrasında yeniden başlatma; olay nedeni kontrol edilmeden yalnız anahtarı geri çevirmek değildir. Yetkin ekip tetikleyici, DC kablo, modül anahtarları, inverter alarmları ve haberleşmeyi kontrol etmeli; üretici sırasına göre sistemi kademeli devreye almalıdır. CTA: kişisel verisiz tetikleyici–bileşen–gerilim–alarm–yeniden başlatma kabul matrisini PV ve yangın güvenliği ekiplerine iletin.

- Çatı planı, tek hat ve saha etiketlerini aynı kodlarla eşleştirin.
- Her tetikleyicinin kapsadığı inverter/string alanını gösterin.
- Shutdown sonrası fiziksel inceleme ve alarm kapanışını kaydedin.
- Kanıt yeterliyse gereksiz modül anahtarı veya komple inverter değişimi satın almayın.

_Kaynaklar: S1, S2, S3, S4, S5_

## Sık sorulan sorular

### GES ana AC şalterini kapatınca çatıda DC gerilim kalır mı?

Evet, sistem mimarisine bağlı olarak PV modülleri ışık altında DC üretmeye devam edebilir. AC ayırma, rapid shutdown işlevinin tamamlandığını tek başına kanıtlamaz.

_Kaynaklar: S1, S2, S4_

### Her GES’te rapid shutdown zorunlu mudur?

Hayır, bu rehber evrensel Türkiye zorunluluğu ilan etmez. Proje, yetkili merci, ülke kuralı ve ürün sertifika kapsamı ayrı doğrulanmalıdır.

_Kaynaklar: S1, S2, S3_

### İnverter rapid shutdown uyumluysa başka ekipman gerekmez mi?

Her zaman değil. Bazı sistemlerde tam işlev için tetikleyici, modül/dizi anahtarları ve uyumlu iletişim gerekir; tam bileşen zinciri belgelenmelidir.

_Kaynaklar: S3, S4, S5_

### Rapid shutdown sonrası kullanıcı sistemi tekrar açabilir mi?

Acil durum veya arıza nedeni kontrol edilmeden hayır. Yeniden başlatma üretici prosedürü, fiziksel kontrol ve yetkin ekip ile yapılmalıdır.

_Kaynaklar: S4, S5_

## İnsan onay komutu

PR sahibinin veya repository yetkilisinin yorumu:

```text
/cms approve ges-rapid-shutdown-acil-ayirma-itfaiyeci-kabul-testi
```

Onay iş akışı kalite puanı, kaynak güncelliği, iç linkler, kanibalizasyon ve risk sınırlarını yeniden çalıştırmadan canonical dosya üretmez.
