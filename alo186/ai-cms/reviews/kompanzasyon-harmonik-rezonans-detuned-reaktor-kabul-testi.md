# ALO186 AI CMS inceleme paketi — kompanzasyon-harmonik-rezonans-detuned-reaktor-kabul-testi

> Bu dosya canonical yayına dahil edilmez. PR incelemesi ve insan onayı için üretilmiştir.

## Durum

- State: **approved**
- Risk: **high**
- Model: **gpt-5.6-thinking**
- Kalite: **88/100**
- Benzerlik: **0.45** — https://www.alo186.com/haberler/kompanzasyon-harmonik-rezonans-detuned-reaktor-secimi
- Kelime: **994**

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

- **S1 · IEC** — [IEC 61921:2017 — Power capacitors — Low-voltage power factor correction banks](https://webstore.iec.ch/en/publication/26596) — erişim 2026-08-03 — birincil
- **S2 · IEC** — [IEC 60831-1:2014 — Self-healing shunt power capacitors](https://webstore.iec.ch/en/publication/3609) — erişim 2026-08-03 — birincil
- **S3 · IEC** — [IEC 61000-4-7:2002+A1:2008 — Harmonics and interharmonics measurements](https://webstore.iec.ch/en/publication/4228) — erişim 2026-08-03 — birincil
- **S4 · IEC** — [IEC 61000-4-30:2025 — Power quality measurement methods](https://webstore.iec.ch/en/publication/71611) — erişim 2026-08-03 — birincil
- **S5 · Schneider Electric** — [PowerLogic PFC detuned reactors](https://www.se.com/ca/en/product-range/1426-powerlogic-pfc-detuned-reactors/) — erişim 2026-08-03 — birincil

## SEO

- Title: `Kompanzasyonda Harmonik Rezonans ve Detuned Reaktör Kabulü`
- H1: `Kompanzasyon kondansatörleri neden ısınıyor; harmonik rezonans nasıl doğrulanır?`
- Description: `Kompanzasyon panosunda rezonans, kondansatör ve reaktör ısınmasını; harmonik ölçüm, kademe trendi ve termal kabul dosyasıyla doğrulayın.`
- Canonical: `/haberler/kompanzasyon-harmonik-rezonans-detuned-reaktor-kabul-testi`
- Birincil anahtar kelime: `kompanzasyon harmonik rezonans detuned reaktör`

## Doğrudan cevap

Kompanzasyon kondansatörlerinin sık arızalanması yalnız ürün kalitesiyle açıklanamaz. Şebeke ve trafo empedansı ile kondansatör kademeleri belirli bir frekansta rezonans oluşturup mevcut harmonik akım ve gerilimleri büyütebilir; bunun sonucu kondansatör, reaktör, kontaktör, sigorta ve nötr iletkeninde aşırı ısınma görülebilir. Kabul; kademe bazında temel bileşen ve tekil harmonikler, P–Q–güç faktörü, gerilim bozulması, reaktör-kondansatör etiket ve ayar uyumu, termal trend, koruma durumu ve jeneratör modu birlikte kaydedilerek yapılmalıdır. Enerjili panoda ölçüm bağlantısı veya kademe müdahalesi yalnız yetkin ekipçe gerçekleştirilmelidir.

## Kompanzasyon panosunda harmonik rezonans nasıl oluşur?

Kondansatör bankı reaktif güç ihtiyacını karşılamak için kullanılırken, tesisin trafo ve kablo endüktansı ile birlikte frekansa bağlı bir devre oluşturur. Rezonans frekansı tesiste baskın bulunan bir harmonik bileşene yaklaşırsa, küçük bir harmonik kaynak bile pano akımını ve bara gerilim bozulmasını büyütebilir. Bu durum çoğu zaman kondansatör akımında artış, sigorta açması, kontaktör yüzey hasarı, reaktör uğultusu ve sıcaklık yükselmesi olarak görünür.

Detuned reaktör, kondansatörle seri bağlanarak bankın rezonans noktasını baskın harmoniklerin altına taşımayı amaçlar; aktif harmonik filtreyle aynı görevde değildir. Reaktör seçimi, yalnız 'harmonik var' ifadesine değil trafo gücü ve kısa devre empedansı, mevcut ve gelecekteki doğrusal olmayan yükler, kademe kvar değerleri, sistem gerilimi ve tekil harmonik spektrumuna dayanmalıdır.

- Trafo, kablo, jeneratör ve kondansatör bankını aynı tek hat üzerinde gösterin.
- Arızayı yalnız kondansatör markasına bağlamadan tekil harmonik spektrumunu ölçün.
- Detuned reaktör ile aktif harmonik filtrenin görevlerini birbirine karıştırmayın.
- Yeni sürücü, UPS veya EV şarj yükü eklendiğinde rezonans değerlendirmesini yenileyin.

_Kaynaklar: S1, S2, S3, S4, S5_

## Rezonans şüphesinde hangi elektriksel veriler birlikte kaydedilmelidir?

Tek bir THD ekran görüntüsü kabul için yeterli değildir. Ana girişte ve gerekiyorsa kompanzasyon barasında faz bazında aktif ve reaktif güç, güç faktörü, RMS akım-gerilim, gerilim ve akım THD'si ile tekil harmonikler ortak zaman tabanında kaydedilmelidir. Kademe komutları, kontaktör durumu, yük değişimleri ve jeneratör-şebeke modu aynı olay çizelgesine eklenmelidir.

IEC 61000-4-7 harmonik ve ara harmonik ölçüm yöntemlerini, IEC 61000-4-30 ise güç kalitesi parametrelerinin ölçüm ve birleştirme yöntemlerini tanımlar. Ölçüm cihazının sınıfı, CT oranı ve yönü, nominal gerilim, örnekleme süresi, zaman senkronu ve veri boşlukları raporda açıkça gösterilmezse farklı gün veya kademelerin karşılaştırılması yanıltıcı olabilir.

- THD yanında 3., 5., 7., 11. ve 13. gibi tekil bileşenleri yük profiline göre kaydedin.
- Kademe açma-kapama anlarını P, Q, akım ve gerilim trendiyle eşleştirin.
- CT yönü, oranı ve faz eşleşmesini ölçümden önce doğrulayın.
- Şebeke ve jeneratör modlarını aynı kabul sonucu içinde karıştırmayın.

_Kaynaklar: S3, S4_

## Detuned reaktör ile kondansatörün doğru eşleştiği nasıl anlaşılır?

Reaktörün ayar oranı veya tuning frekansı, kondansatörün kvar ve gerilim değeri, sistem frekansı ve üreticinin takım tablosuyla birlikte doğrulanmalıdır. Seri reaktör nedeniyle kondansatör uç gerilimi şebeke geriliminden yüksek olabilir; bu nedenle yalnız bara gerilimine göre seçilmiş standart bir kondansatör uygun olmayabilir. Farklı kademelerde karışık reaktör oranları veya uyumsuz yedek parça, pano rezonansını ve akım paylaşımını değiştirebilir.

Piyasada 135 Hz, 189/190 Hz veya 210/215 Hz gibi değerler görülebilir; bunlar evrensel tercih değildir. Schneider'in detuned ürün bilgileri de seçimin sistem harmonik ortamı ve kondansatör bankı tasarımıyla yapılması gerektiğini gösterir. Kabul dosyasında her kademenin reaktör ürün kodu, endüktans veya ayar oranı, kondansatör ürün kodu, kvar, gerilim ve üretici eşleşme kanıtı yer almalıdır.

- Her kademe için reaktör ve kondansatör etiketini ayrı fotoğraf ve tabloyla kaydedin.
- Tuning frekansını başka tesis veya eski projeden kopyalamayın.
- Seri reaktörün oluşturduğu kondansatör uç gerilimini üretici hesabıyla kontrol edin.
- Uyumsuz yedek parça veya karışık kademe varsa yeniden mühendislik değerlendirmesi yapın.

_Kaynaklar: S1, S2, S5_

## Kademe ve termal kabul testi hangi senaryoları kapsamalıdır?

IEC 61921 alçak gerilim güç faktörü düzeltme banklarının tasarım ve test çerçevesini, IEC 60831-1 ise kendini onaran tip kondansatörlerin performans ve güvenlik gereklerini ele alır. Saha kabulünde her kademe devredeyken faz akımları, akım dengesizliği, kondansatör ve reaktör sıcaklığı, sigorta ve kontaktör bağlantıları, pano havalandırması ve kontrol rölesi davranışı izlenmelidir.

Test düşük, tipik ve yüksek yük dönemlerini; ani yük kaybını, gece düşük yükte kapasitif taşmayı, jeneratör çalışmasını ve kademe boşalma süresini kapsamalıdır. Termal kamera görüntüsü ortam sıcaklığı, yük yüzdesi ve karşılaştırma noktalarıyla kaydedilmeli; yalnız renk paletine bakılarak arıza kararı verilmemelidir. Aşırı sıcak veya yanık kokusu varsa pano güvenli biçimde devreden çıkarılmalıdır.

- Her kademede üç faz akımı ve yüzey sıcaklıklarını aynı yükte karşılaştırın.
- Kontaktör, sigorta, bara ve kablo bağlantılarını termal trendle birlikte inceleyin.
- Kontrol rölesinin kademe alma-bırakma ve boşalma sürelerini doğrulayın.
- Jeneratör modunda kompanzasyon kilidi veya ayrı ayar davranışını test edin.

_Kaynaklar: S1, S2, S4_

## Harmonik rezonans ve detuned reaktör kabul dosyası nasıl hazırlanmalıdır?

Dosya; tek hat, trafo gücü ve uk değeri, kısa devre seviyesi, yük envanteri, kompanzasyon kademe tablosu, CT ve kontrol rölesi bilgileri, reaktör-kondansatör etiketleri, ölçüm cihazı ve kalibrasyonu, P–Q–THD–tekil harmonik trendleri, sıcaklıklar, alarm ve açma olayları, şebeke-jeneratör senaryoları ile geçti-kaldı sonucunu içermelidir. Onarım sonrası aynı ölçüm noktası ve benzer yük koşulunda tekrar test yapılmalıdır.

Ölçüm, mevcut bankın doğru eşleştiğini ve sıcaklıkların kabul sınırında kaldığını gösteriyorsa sırf 'harmonikli tesis' denilerek yeni reaktör, kondansatör veya aktif filtre satın almak gerekmez. CTA: kişisel verisiz kompanzasyon–harmonik–kademe–termal kabul matrisini tamamlayıp yetkin güç kalitesi mühendisine iletin.

- Ham ölçüm, işlenmiş grafik ve karar tablosunu ayrı katmanlarda saklayın.
- Her iddiayı kademe, zaman ve ölçüm noktasıyla izlenebilir hâle getirin.
- Onarım öncesi ve sonrası veriyi aynı yöntemle karşılaştırın.
- Kanıt yeterliyse gereksiz kondansatör, reaktör veya filtre yatırımı yapmayın.

_Kaynaklar: S1, S2, S3, S4, S5_

## Sık sorulan sorular

### Kondansatörlerin sık patlaması mutlaka harmonik olduğu anlamına mı gelir?

Hayır. Aşırı gerilim, yüksek sıcaklık, yanlış kademe seçimi, gevşek bağlantı, yetersiz havalandırma ve uygun olmayan yedek koruma da neden olabilir. Harmonik rezonans ölçümle ayrılmalıdır.

_Kaynaklar: S1, S2, S4_

### Detuned reaktör takılırsa bütün harmonikler temizlenir mi?

Hayır. Detuned reaktör temel olarak kondansatör bankını rezonans ve belirli harmonik büyütme riskinden korumaya yöneliktir; aktif harmonik filtre gibi geniş bant akım kompanzasyonu yapmaz.

_Kaynaklar: S1, S5_

### 189 veya 190 Hz detuned reaktör her tesise uygun mudur?

Hayır. Ayar frekansı sistem frekansı, harmonik spektrumu, trafo ve kondansatör bankı tasarımıyla belirlenir. Üretici örnek değerleri evrensel proje ayarı değildir.

_Kaynaklar: S1, S5_

### THD düşük görünüyorsa rezonans riski yok mudur?

Tek bir anlık THD değeri yeterli değildir. Kademe değişimleri, tekil harmonikler, yük ve jeneratör modu boyunca zaman serisi ile termal davranış birlikte incelenmelidir.

_Kaynaklar: S3, S4_

## İnsan onay komutu

PR sahibinin veya repository yetkilisinin yorumu:

```text
/cms approve kompanzasyon-harmonik-rezonans-detuned-reaktor-kabul-testi
```

Onay iş akışı kalite puanı, kaynak güncelliği, iç linkler, kanibalizasyon ve risk sınırlarını yeniden çalıştırmadan canonical dosya üretmez.
