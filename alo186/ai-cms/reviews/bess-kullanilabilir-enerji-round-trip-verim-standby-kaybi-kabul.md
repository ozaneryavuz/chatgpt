# ALO186 AI CMS inceleme paketi — bess-kullanilabilir-enerji-round-trip-verim-standby-kaybi-kabul

> Bu dosya canonical yayına dahil edilmez. PR incelemesi ve insan onayı için üretilmiştir.

## Durum

- State: **approved**
- Risk: **high**
- Model: **gpt-5.6-thinking**
- Kalite: **100/100**
- Benzerlik: **0.46** — https://www.alo186.com/haberler/enerji-depolama-round-trip-efficiency-soh-kabul-testi
- Kelime: **1016**

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

- **S1 · IEC** — [IEC TS 62933-2-3:2025 — Performance assessment test during site operation](https://webstore.iec.ch/en/publication/77334) — erişim 2026-08-03 — birincil
- **S2 · IEC** — [IEC TS 62933-2-2:2022 — Application and performance testing](https://webstore.iec.ch/en/publication/64570) — erişim 2026-08-03 — birincil
- **S3 · IEC** — [IEC 62933-3-1:2025 — Planning and performance assessment of EES systems](https://webstore.iec.ch/en/publication/75427) — erişim 2026-08-03 — birincil
- **S4 · U.S. Department of Energy FEMP** — [Battery Energy Storage System Evaluation Method](https://www.energy.gov/cmei/femp/articles/battery-energy-storage-system-evaluation-method) — erişim 2026-08-03 — birincil
- **S5 · National Laboratory of the Rockies** — [Performance and Health Test Procedure for Grid Energy Storage Systems](https://research-hub.nlr.gov/en/publications/performance-and-health-test-procedure-for-grid-energy-storage-sys-4/) — erişim 2026-08-03 — birincil

## SEO

- Title: `BESS Round-Trip Verim Kabul Testi ve Kullanılabilir Enerji`
- H1: `BESS round-trip verim kabul testi nasıl yapılır?`
- Description: `BESS kullanılabilir enerjiyi, round-trip verimi, standby kaybını ve SoC sınırlarını ortak sayaç verisiyle ölçüp saha kabul dosyasına dönüştürün.`
- Canonical: `/haberler/bess-kullanilabilir-enerji-round-trip-verim-standby-kaybi-kabul`
- Birincil anahtar kelime: `BESS round-trip verim kabul testi`

## Doğrudan cevap

BESS round-trip verim kabul testi, BMS ekranındaki nominal kWh veya tek bir SoC düşüşüne bakılarak yapılmaz. Şarj ve deşarj enerjisi aynı tanımlı AC veya DC ölçüm sınırında, senkron sayaçlarla kaydedilmeli; başlangıç-bitiş SoC, güç profili, sıcaklık, yardımcı tüketimler, standby süresi ve kullanılabilir enerji penceresi rapora bağlanmalıdır. Test çevrimi uygulama görevini temsil etmeli ve sonuçlar garanti edilen referans koşullarıyla karşılaştırılmalıdır. Canlı DC kabin, bara ve batarya korumasına müdahale yalnız yetkin ekip ve onaylı test planıyla yapılmalıdır.

## Kullanılabilir enerji ve round-trip verim hangi ölçüm sınırında tanımlanır?

Batarya hücrelerinin nominal enerjisi, tesisin bağlantı noktasında kullanabildiği enerjiyle aynı değildir. PCS dönüşüm kayıpları, trafo ve kablo kayıpları, HVAC, yangın algılama, BMS, kontrol sistemi ve diğer yardımcı tüketimler sonuca etki eder. Bu nedenle kabul sözleşmesi ölçüm sınırını açıkça tanımlamalıdır: hücre DC’si, batarya rafı DC’si, PCS AC terminali veya tesis bağlantı noktası.

Round-trip verim, tanımlı sınır içinde sisteme giren şarj enerjisi ile geri alınan deşarj enerjisinin aynı çevrim ve koşullarda karşılaştırılmasıdır. Farklı sayaçlardan, farklı zaman aralıklarından veya biri brüt diğeri net ölçümden alınan değerler doğrudan bölünmemelidir. IEC 62933 serisi, uygulama ve saha işletmesi performansının sistem parametreleri ve test yöntemleriyle değerlendirilmesini destekler.

- AC ve DC ölçüm sınırlarını tek hat üzerinde işaretleyin.
- Yardımcı tüketimlerin sınırın içinde mi dışında mı olduğunu yazın.
- Şarj ve deşarj sayaçlarının zaman tabanını ve işaret yönünü doğrulayın.
- Nominal hücre kWh değerini net saha enerjisi gibi sunmayın.

_Kaynaklar: S1, S2, S3, S4, S5_

## Test öncesi referans koşulları nasıl sabitlenir?

Kullanılabilir enerji; başlangıç ve bitiş SoC sınırları, batarya sıcaklığı, güç seviyesi, hücre dengelemesi, SoH, bekleme süresi ve üretici koruma rezervlerinden etkilenir. Testten önce sistem modeli, yazılım sürümü, BMS/EMS/PCS parametre yedeği, garanti edilen enerji penceresi, maksimum-minimum SoC ve çevresel koşullar aynı kabul formunda toplanmalıdır.

Tek bir yüksek güçlü deşarj, düşük güçlü uzun süreli görevle aynı sonucu vermeyebilir. IEC TS 62933-2-2 uygulamaya özgü görev çevrimleri ve performans testlerini; IEC 62933-3-1 ise planlama, izleme, işletme parametresi toplama ve bakım bağlamını ele alır. Test profili, tesisin peak shaving, yedek güç, arbitraj, frekans hizmeti veya PV öz tüketim görevlerinden hangisini temsil ettiğini belirtmelidir.

- SoC, SoH, sıcaklık ve yazılım sürümünü test başlangıcında dondurun.
- Garanti edilen referans güç, enerji ve çevre koşullarını dosyaya ekleyin.
- Uygulamaya uygun sabit güç veya görev çevrimi seçin.
- Koruma rezervlerini devre dışı bırakarak yapay kapasite üretmeyin.

_Kaynaklar: S1, S2, S3, S5_

## Şarj-deşarj çevrimi ve standby kaybı nasıl ölçülür?

Test, ön koşullandırma gerekiyorsa bunu ayrı kaydetmeli; ardından tanımlı başlangıç SoC’sinden şarj, dinlenme, deşarj ve son dinlenme adımlarını zaman çizelgesinde göstermelidir. Her adımda aktif-reaktif güç, AC ve varsa DC enerji, SoC, hücre sıcaklık aralığı, HVAC gücü, alarm ve curtailment durumu ortak zamanla kaydedilmelidir. Test sırasında güç limiti veya termal derating oluşursa sonuç gizlenmemeli, neden ve süresi raporlanmalıdır.

Standby kaybı, sistemin enerji aktarmadığı ancak kontrol, iklimlendirme ve güvenlik işlevlerini sürdürdüğü süre boyunca ölçülür. National Laboratory of the Rockies tarafından yayımlanan saha prosedürü; round-trip efficiency, standby losses, response, usable energy/SoC gibi ölçütleri periyodik referans testleri ve normal işletme izleme verileriyle birlikte ele alır. Tek bir çevrim, uzun dönem bozulma eğiliminin yerine geçmez.

- Şarj, bekleme, deşarj ve son bekleme adımlarını ayrı enerji sayaçlarıyla raporlayın.
- HVAC ve yardımcı yüklerin anlık güç ve toplam enerjisini kaydedin.
- Termal veya SoC kaynaklı güç kısıtlamalarını olay olarak işaretleyin.
- Standby kaybını enerji aktarımı olmayan tanımlı sürede ölçün.

_Kaynaklar: S1, S4, S5_

## Sayaç, SoC ve veri kalitesi nasıl doğrulanır?

Round-trip verimde birkaç puanlık fark ticari ve teknik kararı değiştirebilir; bu nedenle sayaç sınıfı, CT/PT oranı, enerji işaret yönü, örnekleme aralığı, zaman senkronu ve eksik veri kuralları rapora yazılmalıdır. BMS SoC değeri bir model çıktısıdır; yalnız SoC yüzdesi kullanılarak enerji hesabı yapılmamalı, kalibre enerji sayaçlarıyla karşılaştırılmalıdır.

DOE FEMP yöntemi, sahadaki BESS performansının gerçek şarj-deşarj sayaç zaman serileriyle değerlendirilmesini önerir ve uzun dönem verilerden KPI tahmini yapılabileceğini açıklar. Kabul testindeki kısa referans çevrimi, en azından aylık veya yıllık işletme trendiyle tamamlanırsa kapasite kaybı, standby tüketimindeki artış veya dispatch sapması erken görülebilir.

- Sayaç sınıfı, kalibrasyon, CT/PT oranı ve işaret yönünü doğrulayın.
- Eksik, yinelenen ve saat kaymış verileri ayrı kalite bayrağıyla işaretleyin.
- BMS SoC yüzdesini tek başına enerji ölçümü kabul etmeyin.
- Referans testi normal işletme zaman serisiyle karşılaştırın.

_Kaynaklar: S3, S4, S5_

## BESS kabul dosyasında hangi sonuçlar ve CTA bulunmalıdır?

Teslim dosyası; ölçüm sınırı tek hattı, model-seri-yazılım sürümleri, SoC/SoH ve sıcaklık başlangıcı, görev çevrimi, şarj-deşarj enerji tablosu, yardımcı tüketim, standby kaybı, net kullanılabilir enerji, round-trip verim hesabı, alarm/derating kayıtları, ölçüm belirsizliği ve imzalı geçti-kaldı sonucunu içermelidir. Sonuç, sözleşmedeki garanti noktası ve referans koşullarıyla aynı değilse doğrudan garanti ihlali olarak etiketlenmemeli; önce normalizasyon ve tarafların kabul ettiği hesap yöntemi uygulanmalıdır.

IEC TS 62933-2-3:2025 devreye alma sonrasında saha işletmesinde EES performansını değerlendiren test yöntemlerini tanımlar. Sistem hedefi geçiyorsa sırf daha yüksek etiket kapasitesi için batarya veya PCS değişimi önerilmemelidir. Hedef geçilmiyorsa yazılım sınırı, HVAC, yardımcı tüketim, sayaç hatası, hücre dengesizliği ve gerçek kapasite kaybı ayrı kök nedenler olarak incelenmelidir. CTA: kişisel verisiz BESS performans matrisini tamamlayın ve yetkin kabul ekibine ortak sayaç veri paketini iletin.

- Brüt ve net enerji sonuçlarını aynı tabloda ama ayrı tanımlarla gösterin.
- Round-trip verim formülüne dahil edilen bütün yardımcı yükleri açıklayın.
- Garanti kıyasını aynı ölçüm sınırı ve referans koşulunda yapın.
- Kanıt hedefi geçiyorsa gereksiz batarya veya PCS büyütmesi satın almayın.

_Kaynaklar: S1, S2, S3, S4, S5_

## Sık sorulan sorular

### BESS round-trip verimi nasıl hesaplanır?

Tanımlı aynı ölçüm sınırında ve aynı çevrimde geri verilen deşarj enerjisi, alınan şarj enerjisine bölünür. Yardımcı tüketimlerin sınırın içinde veya dışında oluşu ve başlangıç-bitiş SoC eşitliği açıkça belirtilmelidir.

_Kaynaklar: S1, S2, S5_

### BMS ekranındaki kullanılabilir kWh kabul için yeterli midir?

Hayır. BMS değeri önemli bir işletme göstergesidir ancak kabulde kalibre enerji sayaçları, ortak zamanlı AC/DC ölçümler ve tanımlı SoC-sıcaklık koşullarıyla doğrulanmalıdır.

_Kaynaklar: S1, S3, S4, S5_

### Tek bir şarj-deşarj çevrimi batarya sağlığını kanıtlar mı?

Tek çevrim referans performansı gösterir; uzun dönem kapasite ve verim eğilimi için normal işletme sayaç zaman serileri, periyodik referans testleri ve SoH trendi birlikte izlenmelidir.

_Kaynaklar: S4, S5_

### Düşük verim görülürse batarya hemen değiştirilir mi?

Hayır. Önce ölçüm sınırı, sayaç yönü, yardımcı tüketimler, HVAC, güç kısıtları, yazılım parametreleri, sıcaklık ve SoC eşitliği doğrulanmalıdır. Kök neden kanıtlanmadan değişim kararı verilmemelidir.

_Kaynaklar: S1, S3, S5_

## İnsan onay komutu

PR sahibinin veya repository yetkilisinin yorumu:

```text
/cms approve bess-kullanilabilir-enerji-round-trip-verim-standby-kaybi-kabul
```

Onay iş akışı kalite puanı, kaynak güncelliği, iç linkler, kanibalizasyon ve risk sınırlarını yeniden çalıştırmadan canonical dosya üretmez.
