# ALO186 AI CMS inceleme paketi — harmonikli-yuk-trafo-k-faktoru-derating-notr-termal-kabul

> Bu dosya canonical yayına dahil edilmez. PR incelemesi ve insan onayı için üretilmiştir.

## Durum

- State: **approved**
- Risk: **high**
- Model: **gpt-5.6-thinking**
- Kalite: **100/100**
- Benzerlik: **0.33** — https://alo186.com/haberler/trafo-k-faktoru-harmonik-derating-nonlineer-yuk-secimi
- Kelime: **979**

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

- **S1 · IEEE Standards Association** — [IEEE C57.110-2018 — Transformer capability with nonsinusoidal load currents](https://standards.ieee.org/ieee/C57.110/5948/) — erişim 2026-08-03 — birincil
- **S2 · Schneider Electric** — [PowerLogic ION7400 — K-factor](https://product-help.schneider-electric.com/PowerLogic-ION7400/en-us/content/09-pq/k-factor.htm?TocPath=Power+quality%7C_____9) — erişim 2026-08-03 — birincil
- **S3 · IEC** — [IEC 61000-4-7:2002+A1:2008 — Harmonics and interharmonics measurement instrumentation](https://webstore.iec.ch/en/publication/4226) — erişim 2026-08-03 — birincil
- **S4 · Schneider Electric** — [PowerLogic ION9000 — Harmonics](https://product-help.se.com/docs/PowerLogic-ION9000/en-us/content/09-pq/harmonics.htm?TocPath=Alerts%7C_____11) — erişim 2026-08-03 — birincil
- **S5 · IEC** — [IEC TS 63222-4:2026 — Harmonic analysis on public electric power network](https://webstore.iec.ch/en/publication/71907) — erişim 2026-08-03 — birincil

## SEO

- Title: `Trafo K-Faktörü ve Derating Hesabı: Harmonikli Yük Kabulü`
- H1: `Trafo K-faktörü ve derating hesabı nasıl doğrulanır?`
- Description: `Harmonikli yüklerde trafo K-faktörünü, nötr akımını, kayıpları ve sıcaklık artışını ölçerek mevcut trafonun derating ve kabul dosyasını hazırlayın.`
- Canonical: `/haberler/harmonikli-yuk-trafo-k-faktoru-derating-notr-termal-kabul`
- Birincil anahtar kelime: `trafo K-faktörü ve derating hesabı`

## Doğrudan cevap

Trafo K-faktörü ve derating hesabı, yalnız akım THD yüzdesi veya etiket kVA ile tamamlanmaz. Faz akımlarının harmonik mertebeleri, RMS yük, nötr akımı, yükün süre profili, ortam ve sargı sıcaklığı, trafo tipi ile üretici kayıp verileri birlikte değerlendirilmelidir. K-faktörü bozulmuş akımın trafodaki ısıl etkisini ağırlıklandırmaya yardımcı olur; ancak mevcut trafonun taşıyabileceği kesin kVA’yı tek başına vermez. Enerjili trafo ve pano ölçümleri yalnız yetkin ekip ve onaylı risk planıyla yapılmalıdır.

## Neden yalnız THDi veya kVA değerine bakmak yeterli değildir?

Doğrusal olmayan yükler akımı sinüsten saptırır ve farklı harmonik mertebeler oluşturur. Aynı RMS akım değerine sahip iki yük, harmonik dağılımları farklıysa trafoda aynı ek kaybı ve sıcaklık artışını oluşturmayabilir. IEEE C57.110-2018, mevcut kuru tip veya yağlı trafonun nonsinüzoidal yük akımlarını besleme kabiliyetini değerlendirmek ve yeni trafonun doğru seçilmesini desteklemek için hesap yöntemleri sunar.

Toplam THDi önemli bir göstergedir; ancak hangi harmoniklerin baskın olduğunu, üçlü harmoniklerin nötrde toplanmasını, yükün ne kadar süre devam ettiğini ve trafo sıcaklık rezervini tek başına göstermez. İnverter, UPS, VFD, LED ve bilgi teknolojisi yükleri saatlik görev profiline göre ayrı gruplandırılmalıdır. Ölçüm, gerçek maksimum talep ve temsilî işletme koşullarını kapsamalıdır.

- Faz RMS akımıyla birlikte tekil harmonik akımları kaydedin.
- Üçlü harmonikler ve nötr akımı için ayrı kanal kullanın.
- Yükün süre profilini ve eşzamanlılığını rapora ekleyin.
- Tek THDi ekran görüntüsünden trafo değişim kararı vermeyin.

_Kaynaklar: S1, S3, S4, S5_

## K-faktörü neyi gösterir, neyi göstermez?

K-faktörü, harmonik akımların mertebe karesiyle ağırlıklandırılan ısıl etkisini ifade eden bir göstergedir. Schneider Electric’in ölçüm açıklamasında K-faktörü, aynı RMS büyüklükteki bozulmuş akımın trafoda sinüzoidal akıma göre ısıl etkisiyle ilişkilendirilir. Yüksek mertebeli akımlar daha güçlü ağırlık aldığı için küçük genlikli bir üst harmonik bile hesapta görünür olabilir.

K-faktörü ölçüm noktasına ve zamana bağlıdır. Bir analizörün gösterdiği anlık değer, trafonun üretici tasarım K sınıfı, harmonik kayıp faktörü veya izin verilen yüküyle aynı kavram değildir. Faz bazında spektrum, ölçüm süresi, maksimum ve yüzde 95 değerleri, analizörün harmonik aralığı ve hesap tanımı raporda yer almalıdır.

- Analizörün K-faktörü tanımını ve harmonik üst sınırını kaydedin.
- Her faz için anlık, maksimum ve temsilî K-faktörünü ayırın.
- Yük K-faktörü ile trafo etiket veya tasarım beyanını aynı alan gibi kullanmayın.
- K-faktörünü sıcaklık ve yük profiliyle birlikte yorumlayın.

_Kaynaklar: S1, S2, S3, S4_

## Harmonik, nötr ve sıcaklık ölçüm planı nasıl kurulur?

Ölçüm planı trafo sekonder ana çıkışı, kritik tali panolar ve nötr iletkeninde ortak zamanlı akım-gerilim spektrumu toplamalıdır. IEC 61000-4-7, 50/60 Hz güç sistemlerinde harmonik ve interharmonik ölçüm cihazları ve gruplama yöntemleri için çerçeve sunar. Analizörün bağlantı biçimi, CT oranı, örnekleme penceresi, faz sırası ve harmonik mertebe aralığı doğrulanmalıdır.

Elektriksel kayıt, termal kanıtla desteklenmelidir. Ortam sıcaklığı, trafo yüzeyi veya üreticinin izin verdiği sensör noktaları, bağlantılar, nötr bara ve kablo sıcaklıkları aynı yük zaman çizelgesine bağlanmalıdır. Termal kamera yüzey sıcaklığı verir; sargı sıcaklığını doğrudan ölçtüğü varsayılmamalıdır. Havalandırma, fan durumu, kirlenme ve oda sıcak hava geri dönüşü de rapora eklenmelidir.

- Faz akımları, nötr akımı, kW, kVA, PF ve harmonik spektrumu ortak zamanla kaydedin.
- CT yönü, oranı ve analizör bağlantı biçimini tek hatla doğrulayın.
- Ortam, trafo, bağlantı ve nötr bara sıcaklıklarını aynı yükte karşılaştırın.
- Yüzey termografisini doğrudan sargı sıcaklığı olarak yorumlamayın.

_Kaynaklar: S1, S3, S4, S5_

## Mevcut trafonun derating veya değişim kararı nasıl verilir?

Derating değerlendirmesi; trafo tipi, anma kayıpları, girdap akımı ve diğer stray loss bileşenleri, harmonik spektrum, maksimum yük, ortam sıcaklığı, soğutma sınıfı ve üretici verilerine dayanmalıdır. IEEE C57.110’daki yöntemler mevcut trafonun nonsinüzoidal yük taşıma kabiliyetini muhafazakâr biçimde değerlendirmeye ve yeni trafo şartnamesini hazırlamaya yardımcı olur. Proje hesabı ilgili trafo verisiyle yetkin mühendis tarafından yapılmalıdır.

Alternatifler yalnız “K-rated trafo satın al” şeklinde sıralanmamalıdır. Yük dağılımı, faz dengeleme, nötr kesiti, VFD/UPS topolojisi, pasif veya aktif filtreleme, ayrı trafo, havalandırma ve işletme sıralaması kök nedene göre karşılaştırılmalıdır. Harmonik filtre kararı PCC gerilim-akım spektrumu ve rezonans incelemesi olmadan verilmemelidir.

- Üretici kayıp, sıcaklık artışı ve soğutma verilerini hesapla eşleştirin.
- Mevcut maksimum talep ile gelecekteki doğrusal olmayan yükleri ayrı senaryolayın.
- Nötr iletkeni ve bağlantıların ısıl kapasitesini trafodan bağımsız kontrol edin.
- Filtre, K-rated trafo veya daha büyük kVA kararını kök neden analizine bağlayın.

_Kaynaklar: S1, S2, S4, S5_

## Trafo harmonik ve termal kabul dosyasında neler bulunmalıdır?

Kabul dosyası; tek hat ve ölçüm noktaları, trafo etiket/üretici verisi, yük envanteri, en az temsilî işletme periyodunun faz-nötr akım trendleri, tekil harmonik spektrumları, K-faktörü, kW-kVA-PF, ortam ve termal kayıtlar, havalandırma durumu, derating hesabı, senaryolar ve imzalı teknik sonuç içermelidir. Ölçüm belirsizliği ve veri boşlukları açıkça yazılmalıdır.

IEC TS 63222-4:2026 kamu şebekelerinde 40. harmoniğe kadar analiz için model, yöntem ve prosedür gerekliliklerini ele alır; saha içi trafo kabulü ise IEEE yöntemi, IEC ölçüm yöntemi, üretici verisi ve tesis koşulları birlikte kullanılarak yapılmalıdır. Mevcut trafo sıcaklık, yük ve hesap sınırlarını kanıtla geçiyorsa yalnız K-faktörü korkusuyla değiştirilmemelidir. CTA: kişisel verisiz harmonik-yük-termal matrisini tamamlayın ve yetkin mühendise derating senaryolarını iletin.

- Spektrum, K-faktörü, yük ve sıcaklığı aynı zaman diliminde raporlayın.
- Normal, yoğun ve arıza/transfer işletme senaryolarını ayırın.
- Hesabın kullandığı trafo kayıp ve ortam varsayımlarını görünür yapın.
- Kanıt uygunsa gereksiz trafo, nötr veya filtre yatırımı yapmayın.

_Kaynaklar: S1, S2, S3, S4, S5_

## Sık sorulan sorular

### Yüksek THDi varsa trafo mutlaka büyütülür mü?

Hayır. Tekil harmonik spektrumu, K-faktörü, gerçek RMS yük, süre profili, nötr akımı, sıcaklık ve trafo kayıp verileri birlikte değerlendirilmeden büyütme kararı verilmemelidir.

_Kaynaklar: S1, S2, S4_

### K-faktörü trafonun yüzde kaç derate edileceğini doğrudan verir mi?

Hayır. K-faktörü harmonik akımların ısıl etkisini ağırlıklandırır; izin verilen yük için trafo tipi, kayıp bileşenleri, üretici verisi ve IEEE C57.110 gibi uygun değerlendirme yöntemi gerekir.

_Kaynaklar: S1, S2_

### Nötr akımı faz akımından yüksek olabilir mi?

Dört iletkenli sistemlerde bazı üçlü harmonikler nötrde aritmetik olarak toplanabilir. Gerçek durum faz ve nötr spektrumu, yük dağılımı ve bağlantı yapısıyla ölçülmelidir.

_Kaynaklar: S3, S4_

### Aktif harmonik filtre trafonun bütün sorunlarını çözer mi?

Hayır. Filtrenin hedef harmonikleri, bağlantı noktası, akım kapasitesi, rezonans ve kontrol performansı projeye göre doğrulanmalıdır. Aşırı yük, havalandırma veya bağlantı problemi ayrı kalabilir.

_Kaynaklar: S1, S4, S5_

## İnsan onay komutu

PR sahibinin veya repository yetkilisinin yorumu:

```text
/cms approve harmonikli-yuk-trafo-k-faktoru-derating-notr-termal-kabul
```

Onay iş akışı kalite puanı, kaynak güncelliği, iç linkler, kanibalizasyon ve risk sınırlarını yeniden çalıştırmadan canonical dosya üretmez.
