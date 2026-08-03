# ALO186 AI CMS inceleme paketi — kompanzasyon-harmonik-rezonans-detuned-reaktor-kabul

> Bu dosya canonical yayına dahil edilmez. PR incelemesi ve insan onayı için üretilmiştir.

## Durum

- State: **approved**
- Risk: **high**
- Model: **gpt-5.6-thinking**
- Kalite: **88/100**
- Benzerlik: **0.50** — https://www.alo186.com/haberler/kompanzasyon-harmonik-rezonans-detuned-reaktor-secimi
- Kelime: **791**

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

- **S1 · IEC** — [IEC 61642:1997 — Harmoniklerden etkilenen endüstriyel AC şebekelerde filtre ve şönt kondansatör uygulaması](https://webstore.iec.ch/en/publication/5681) — erişim 2026-08-03 — birincil
- **S2 · IEC** — [IEC 63497:2026 — Shunt-connected active correction devices](https://webstore.iec.ch/en/publication/81573) — erişim 2026-08-03 — birincil
- **S3 · Schneider Electric** — [PowerLogic Harmonics Overview](https://www.productinfo.schneider-electric.com/pm1130h_pm1140h_em6438h/pm1130h_pm1140h_em6438h-user-manual/English/BM_PM1130H_PM1140H_EM6438H_0000149806.ditamap.xml/%24/C_PowerQuality_HarmonicsOverview_MediumHybrid_0000154571) — erişim 2026-08-03 — birincil
- **S4 · Schneider Electric** — [PowerLogic ION9000 — Harmonics](https://product-help.schneider-electric.com/PowerLogic-ION9000/en-us/content/09-pq/harmonics.htm) — erişim 2026-08-03 — birincil

## SEO

- Title: `Kompanzasyonda Harmonik Rezonans ve Detuned Reaktör Kabulü`
- H1: `Kompanzasyon panosunda harmonik rezonans nasıl anlaşılır, detuned reaktör nasıl doğrulanır?`
- Description: `Kondansatör arızası ve yüksek akımda rezonans riskini ölçün; detuned reaktör, kademe, sıcaklık ve harmonik kabul dosyasını hazırlayın.`
- Canonical: `/haberler/kompanzasyon-harmonik-rezonans-detuned-reaktor-kabul`
- Birincil anahtar kelime: `kompanzasyon harmonik rezonans detuned reaktör`

## Doğrudan cevap

Kompanzasyon panosunda kondansatörlerin sık arızalanması, kademe sigortalarının açması veya reaktörlerin aşırı ısınması yalnız 'kondansatör kalitesi' sorunu değildir; şebeke kısa devre gücü, mevcut harmonikler, kondansatör kVAr'ı ve reaktör-kondansatör ayar frekansı paralel veya seri rezonans oluşturabilir. Kabul çalışması; kompanzasyon kapalı ve açıkken faz bazlı harmonik spektrum, kondansatör ve reaktör akımı, gerilim, sıcaklık, kademe geçişleri ve reaktif güç davranışını karşılaştırmalıdır. Detuned reaktör yüzdesi katalogdan tahmin edilmemeli; sistem empedansı ve üretici kombinasyonu ile doğrulanmalıdır.

## Harmonik rezonans hangi belirtilerle kendini gösterir?

Şişmiş kondansatör, erimiş sigorta yuvası, uğultulu reaktör, kontaktör yapışması, nötr akımı ve belirli kademelerde ani THD artışı rezonans veya aşırı harmonik yükünün işareti olabilir. Ancak gevşek bağlantı, yetersiz havalandırma, yanlış kademe gücü ve aşırı gerilim de benzer hasar üretir.

IEC 61642, harmonikten etkilenen endüstriyel AC şebekelerde şönt kondansatörlerin ve pasif filtrelerin uygulanmasına rehberlik eder. Bu nedenle arıza analizi yalnız tek kondansatörün kapasite ölçümüne değil, tesisin harmonik kaynakları ve şebeke empedansına dayanmalıdır.

- Arızanın yalnız hangi kademelerde oluştuğunu kaydedin.
- Kompanzasyon kapalı ve açık durumda aynı yükte ölçüm alın.
- Faz bazlı akım, gerilim, THD ve tekil harmonikleri birlikte izleyin.
- Termal hasarı gevşek bağlantı ve havalandırma sorunundan ayırın.

_Kaynaklar: S1, S3, S4_

## Rezonans ölçüm planı nasıl kurulmalıdır?

Ölçüm cihazı, en azından faz bazlı gerilim ve akım harmoniklerini, kademe durumunu ve zaman trendini kaydetmelidir. En yüksek harmonik değer yalnız bir anlık ekran görüntüsüyle değil, yük değişimleri ve kademe anahtarlamalarıyla korele edilmelidir. VFD, UPS, LED sürücü, EVSE ve inverterler ayrı olay işaretleriyle izlenmelidir.

Schneider PowerLogic dokümanları harmoniklerin temel frekansın tam katları olduğunu, nötr akımı ve ekipman ısınması gibi etkiler oluşturabildiğini ve uygun analizörlerle faz bazında incelenmesi gerektiğini belirtir. Ölçüm süresi tesisin vardiya ve yük döngüsünü kapsamalıdır.

- En az bir tam işletme döngüsü boyunca trend kaydedin.
- Kademe açma-kapama zamanlarını harmonik trendine işleyin.
- 5., 7., 11. ve 13. harmonikler dahil tekil spektrumu inceleyin.
- Şebeke gerilimi harmonikleri ile yük akımı harmoniklerini karıştırmayın.

_Kaynaklar: S3, S4_

## Detuned reaktör ve kondansatör uyumu nasıl doğrulanır?

Detuned sistemde reaktör ve kondansatör birlikte belirli bir ayar frekansı oluşturur. Kondansatörün gerçek kapasitesi, reaktör endüktansı, toleranslar, şebeke frekansı ve bağlantı biçimi ayar noktasını değiştirir. Reaktör yüzdesinin tek başına yazılması, gerçek kombinasyonun uyumlu olduğunu kanıtlamaz.

Üretici tablosu; kondansatör nominal gerilimi, reaktör akımı, termik sınıfı, kısa devre dayanımı ve kademe kVAr'ı ile birlikte kullanılmalıdır. Farklı marka veya yaşta parça karışımı varsa tasarım doğrulaması yeniden yapılmalı; yalnız aynı fiziksel boyuta göre parça seçilmemelidir.

- Her kademenin kondansatör ve reaktör ürün kodunu kaydedin.
- Gerçek kapasite ve endüktans değerlerini kabul toleransıyla karşılaştırın.
- Nominal akımın harmonik yük ve tolerans payını kapsadığını doğrulayın.
- Farklı marka kombinasyonunda üretici uyum kanıtı isteyin.

_Kaynaklar: S1, S2_

## Detuned reaktör mü aktif harmonik filtre mi gerekir?

Detuned reaktör, kondansatör bankasını belirli rezonans risklerinden korur ve pasif davranır; tüm harmonik akımları otomatik olarak temizlemez. Aktif harmonik filtre veya statik VAR üreteci ise ölçülen akım bileşenlerine göre dinamik düzeltme yapabilir. İki çözümün görevi ve kabul kriteri aynı değildir.

IEC 63497:2026, şönt bağlı aktif düzeltme cihazlarının harmonik filtreleme, reaktif güç ve dengesizlik kompanzasyonu işlevleri için performans ve güvenlik çerçevesini tanımlar. Yatırım kararı; harmonik kaynak profili, reaktif güç ihtiyacı, yük değişkenliği ve ölçülmüş sonuçlara dayanmalıdır.

- Detuned reaktörü aktif filtre yerine pazarlamayın.
- Reaktif güç ve harmonik hedeflerini ayrı yazın.
- Aktif filtre kapasitesini yalnız toplam kVA'ya göre seçmeyin.
- Mevcut pasif sistem ölçümle yeterliyse gereksiz aktif filtre almayın.

_Kaynaklar: S1, S2_

## Kabul ve bakım dosyasında hangi kanıtlar bulunmalıdır?

Dosyada tek hat, kademe listesi, kondansatör ve reaktör teknik değerleri, şebeke kısa devre bilgisi, kompanzasyon kapalı-açık harmonik trendleri, faz akımları, sıcaklıklar, kademe anahtarlama sayıları ve koruma elemanları bulunmalıdır. Ölçüm enerjili panoda yapıldığından yetkin personel ve uygun iş güvenliği prosedürü zorunludur.

Kabul yalnız reaktif oranların düzelmesiyle bitmemelidir. Her kademenin akımı, sıcaklığı ve harmonik yükü sınırlar içinde kalmalı; bakımda kapasite kaybı, reaktör uğultusu, fan ve termik koruma izlenmelidir. Ölçüm sonucu mevcut sistem güvenli ve yeterliyse yalnız moda göre reaktör veya filtre değişimi yapılmamalıdır.

- Öncesi-sonrası THD ve tekil harmonik tablosu hazırlayın.
- Kademe bazlı akım ve termal görüntüyü aynı yükte karşılaştırın.
- Koruma, fan ve sıcaklık alarm fonksiyonlarını test edin.
- Mevcut sistem yeterliyse satın almama sonucunu rapora yazın.

_Kaynaklar: S1, S2, S3, S4_

## Sık sorulan sorular

### Kondansatörler sık patlıyorsa mutlaka harmonik mi vardır?

Hayır. Aşırı gerilim, sıcaklık, gevşek bağlantı, yanlış kontaktör veya yaşlanma da neden olabilir. Kompanzasyon kapalı-açık harmonik ve termal ölçümle ayrım yapılmalıdır.

_Kaynaklar: S1, S3_

### Detuned reaktör tüm harmonikleri yok eder mi?

Hayır. Temel görevi kondansatör bankasını rezonans ve harmonik aşırı yüküne karşı daha güvenli hale getirmektir. Harmonik azaltma etkisi tasarıma bağlıdır; aktif filtre ile aynı işlev değildir.

_Kaynaklar: S1, S2_

### Reaktör yüzdesi tek başına seçim için yeterli mi?

Hayır. Kondansatör kapasitesi ve gerilimi, reaktör endüktansı, toleranslar, şebeke frekansı, akım ve termik sınıf birlikte doğrulanmalıdır.

_Kaynaklar: S1, S2_

### Aktif harmonik filtre ne zaman düşünülmelidir?

Ölçüm, değişken doğrusal olmayan yüklerin kabul hedeflerini pasif koordinasyonla karşılayamadığını gösteriyorsa değerlendirilir. Kapasite ve performans saha ölçümüne göre belirlenmelidir.

_Kaynaklar: S2, S4_

## İnsan onay komutu

PR sahibinin veya repository yetkilisinin yorumu:

```text
/cms approve kompanzasyon-harmonik-rezonans-detuned-reaktor-kabul
```

Onay iş akışı kalite puanı, kaynak güncelliği, iç linkler, kanibalizasyon ve risk sınırlarını yeniden çalıştırmadan canonical dosya üretmez.
