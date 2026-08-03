# ALO186 AI CMS inceleme paketi — supraharmonik-2-150-khz-olcum-kaynak-ayrimi

> Bu dosya canonical yayına dahil edilmez. PR incelemesi ve insan onayı için üretilmiştir.

## Durum

- State: **approved**
- Risk: **high**
- Model: **gpt-5.6-thinking**
- Kalite: **100/100**
- Benzerlik: **0.11** — https://www.alo186.com/haberler/notr-toprak-gerilimi-yuksek-nedenleri-olcum
- Kelime: **990**

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

- **S1 · IEC** — [IEC 61000-4-30:2025 — Power quality measurement methods](https://webstore.iec.ch/en/publication/71611) — erişim 2026-08-03 — birincil
- **S2 · IEC** — [IEC 61000-4-19:2014 — Immunity to 2 kHz–150 kHz differential-mode disturbances](https://webstore.iec.ch/en/publication/4188) — erişim 2026-08-03 — birincil
- **S3 · CIGRE** — [Assessment of conducted disturbances above 2 kHz in MV and LV power systems](https://electra.cigre.org/310-june-2020/technical-brochures/assessment-of-conducted-disturbances-above-2khz-in-mv-and-lv-power-systems.html) — erişim 2026-08-03 — birincil
- **S4 · IEC** — [IEC 61000-2-4:2024 — Compatibility levels in industrial power systems](https://webstore.iec.ch/en/publication/65717) — erişim 2026-08-03 — birincil

## SEO

- Title: `Supraharmonik 2–150 kHz Ölçüm ve Kaynak Ayrımı`
- H1: `THD normalken cihazlar neden etkilenir? Supraharmonik kanıt planı`
- Description: `2–150 kHz supraharmoniği; EV şarj, GES inverter, UPS ve LED kaynaklarında doğru bant genişliği, eşzamanlı kayıt ve kabul testleriyle ayırın.`
- Canonical: `/haberler/supraharmonik-2-150-khz-olcum-kaynak-ayrimi`
- Birincil anahtar kelime: `supraharmonik 2 150 kHz`

## Doğrudan cevap

THD’nin normal görünmesi 2–150 kHz iletilen bozucuların bulunmadığını kanıtlamaz. EV şarj cihazı, GES inverteri, UPS, LED sürücü veya güç hattı haberleşmesi bu bantta zamanla değişen bileşenler oluşturabilir. Doğru teşhis; 2–9 kHz ve 9–150 kHz için doğrulanmış sensör/analizör, ortak saatli kaynak-mağdur kaydı ve kontrollü A/B işletme senaryolarıyla yapılır; tek spektrum görüntüsünden filtre satın alma kararı verilmez.

## THD normal görünürken neden 2–150 kHz bozucu bileşen olabilir?

Klasik harmonik analiz çoğunlukla temel frekansın katlarını ve daha düşük frekanslı interharmonikleri değerlendirir. Güç elektroniği anahtarlama frekansları, EV şarj cihazları, PV inverterler, LED sürücüler, UPS’ler ve güç hattı haberleşmesi ise 2 kHz ile 150 kHz arasında dar bantlı, geniş bantlı veya zamanla değişen iletilen bileşenler oluşturabilir. Bu nedenle yüzde THD değerinin kabul edilebilir görünmesi, bu frekans aralığında girişim olmadığını kanıtlamaz.

IEC 61000-4-30:2025, 2–9 kHz ve 9–150 kHz aralıkları için ölçüm yöntemlerini ayrı eklerde ele alır. IEC 61000-4-19, AC güç portlarında 2–150 kHz diferansiyel mod bozuculara bağışıklık testlerini tanımlar. CIGRE, supraharmoniklerin bir şebeke periyodu içinde güçlü zaman değişimi gösterebildiğini ve kaynakların genellikle birbiriyle senkron olmadığını vurgular.

- THDv, THDi ve TDD sonuçlarını 2–150 kHz ölçümünden ayrı raporlayın.
- Belirtiyi EV şarj, GES üretim, UPS yükü, LED sürücüleri veya PLC haberleşmesiyle zaman bakımından eşleştirin.
- Tek bir anlık spektrum görüntüsünü kalıcı kök neden kanıtı saymayın.

_Kaynaklar: S1, S2, S3_

## Hangi belirtiler supraharmonik incelemesini haklı kılar?

Tekrarlayan iletişim kopmaları, sayaç veya PLC haberleşme hataları, dokunmatik ekran kararsızlığı, sürücü/UPS beklenmedik alarmı, EV şarj oturumunun belirli yüklerle bozulması veya GES üretimiyle eşzamanlı ekipman etkilenmesi bir ölçüm gerekçesi olabilir. Ancak aynı belirtiler gevşek bağlantı, gerilim çukuru, topraklama/bonding sorunu, RF girişimi, yazılım veya ağ arızasından da kaynaklanabilir.

İnceleme önce olay zaman çizelgesini ve klasik güç kalitesi parametrelerini doğrular; ardından 2–150 kHz bandına geçer. Amaç her elektronik sorunu ‘supraharmonik’ olarak etiketlemek değil, belirtiler ile kaynak açma-kapama durumları arasında tekrarlanabilir ilişki kurmaktır. Kök neden doğrulanmadan filtre, ferrit, trafo veya ekipman değişimi önerilmemelidir.

- Alarm, iletişim ve üretim loglarını ortak zaman referansına alın.
- Gerilim çukuru, kesinti, dengesizlik, klasik harmonik ve topraklama sorunlarını önce ayırın.
- Belirtinin yalnız belirli cihaz, faz, pano veya işletme modunda oluşup oluşmadığını kaydedin.

_Kaynaklar: S1, S3, S4_

## 2–150 kHz ölçüm zinciri nasıl tanımlanmalıdır?

Ölçüm sonucu yalnız analizör modeline bağlı değildir; gerilim probu, akım sensörü, transdüser bant genişliği, örnekleme, anti-alias filtreleme, alıcı bant genişliği, pencere ve kayıt süresi sonucu değiştirir. IEC 61000-4-30:2025, 2–9 kHz ve 9–150 kHz için güncellenmiş yöntemler sunar ve araya giren transdüserlerin etkisinin ayrıca dikkate alınması gerektiğini belirtir.

CIGRE, supraharmoniklerin kısa süreli ve zamanla değişen yapısı nedeniyle popüler tek-spektrum yöntemlerinin önemli özellikleri kaçırabileceğini; STFT gibi zaman-frekans yaklaşımlarının gerekebileceğini açıklar. Rapor; ölçüm noktası, bağlantı şekli, sensör ve analizör bant genişliği, örnekleme, agregasyon, yük durumu ve saat senkronunu yazmalıdır. Evrensel bir tek sayı veya her tesis için aynı alıcı ayarı yayımlanamaz.

- Analizör, prob ve akım sensörünün 150 kHz’e kadar doğrulanmış bant genişliğini belgeleyin.
- 2–9 kHz ile 9–150 kHz sonuçlarını kullanılan yönteme göre ayrı gösterin.
- Uzun trend ile yüksek çözünürlüklü olay kaydını birlikte planlayın.
- Ölçüm zincirinin kendi gürültü tabanını ve doyum sınırını kaydedin.

_Kaynaklar: S1, S2, S3_

## Kaynak, yayılım yolu ve etkilenen cihaz nasıl ayrılır?

Supraharmonikler çoğunlukla iletken yollar boyunca yayılır; şebeke empedansı frekansla ve bağlı yüklerin durumuyla değişir. Aynı kaynak farklı panolarda farklı seviyeler oluşturabilir, birden fazla dönüştürücü ise birbirini güçlendirebilir veya kısmen sönümleyebilir. Bu nedenle yalnız en yüksek spektrumu gördüğünüz cihazı suçlamak doğru değildir.

Güvenli teşhis, yetkili ekip tarafından kontrollü A/B senaryolarıyla yapılır: PV inverter grupları, EVSE’ler, UPS doğrultucusu, LED sürücü grupları veya PLC taşıyıcı sistemleri sırayla işletme durumuna alınır; kaynak tarafı ve etkilenen cihaz tarafında eşzamanlı gerilim/akım kaydı tutulur. Kesme ve devre dışı bırakma işlemleri proses ve can güvenliği risk değerlendirmesi olmadan yapılmamalıdır.

- Kaynak adayı, iletken yol, pano/faz ve etkilenen cihazı ayrı sütunlarda izleyin.
- Kaynak ve mağdur noktada ortak saatli eşzamanlı kayıt kullanın.
- Kontrollü açma-kapama testini yalnız işletme izinleri ve yetkili personelle yapın.
- Common-mode ve differential-mode etkilerinin ölçüm düzenini değiştirebileceğini rapora yazın.

_Kaynaklar: S2, S3, S4_

## İyileştirme kararı hangi kanıtlarla kabul edilmelidir?

İyileştirme, sorunun kaynağı ve kuplaj yolu doğrulandıktan sonra seçilir. Kablo güzergâhı, ekranlama/bonding, uygun giriş filtresi, kaynak cihazın üretici ayarı veya donanım revizyonu, etkilenen cihaz bağışıklığı ve şebeke empedansı seçenekleri birlikte değerlendirilir. Yanlış frekans aralığına seçilmiş bir harmonik filtre veya rastgele ferrit, sorunu çözmeyebilir ve yeni rezonans ya da ısınma oluşturabilir.

Kabul testi öncekiyle aynı ölçüm zinciri, yük durumu ve zaman-frekans yöntemiyle tekrarlanmalıdır. Yalnız spektrum seviyesinin düşmesi değil, gerçek kullanıcı belirtisinin ortadan kalkması ve diğer koruma/haberleşme işlevlerinin bozulmaması gerekir. Mevcut sistem ölçümle yeterli bulunursa yeni filtre veya cihaz almamak geçerli sonuçtur. Enerjili pano ve yüksek frekans ölçümleri yalnız uygun kategori ve bant genişliğine sahip ekipmanla yetkili kişilerce yapılmalıdır.

- Öncesi/sonrası spektrum, zaman-frekans görünümü ve olay logunu aynı raporda karşılaştırın.
- İyileştirmenin başka faz, pano veya haberleşme kanalında olumsuz etki oluşturmadığını doğrulayın.
- Üretici garanti ve EMC talimatlarıyla uyumsuz filtre/ayar değişikliğini kabul etmeyin.

_Kaynaklar: S1, S2, S3, S4_

## Sık sorulan sorular

### Supraharmonik ile klasik harmonik aynı şey midir?

Hayır. Klasik harmonikler temel frekansın katları olarak daha düşük aralıkta incelenir. Supraharmonik terimi çoğunlukla 2–150 kHz iletilen bileşenler için kullanılır; ölçüm bant genişliği ve zaman-frekans davranışı farklıdır.

_Kaynaklar: S1, S3_

### THD düşükse 2–150 kHz girişim olmadığı söylenebilir mi?

Söylenemez. Standart THD ekranı cihaz ve ayara bağlı olarak bu bandı kapsamayabilir. 2–9 kHz ve 9–150 kHz için uygun analizör, sensör, örnekleme ve yöntemle ayrı ölçüm gerekir.

_Kaynaklar: S1, S2_

### EV şarj cihazı veya GES inverter yüksek frekans kaynağıysa arızalı mıdır?

Her anahtarlamalı dönüştürücü belirli bileşenler üretebilir; arıza kararı için ürün emisyon/bağışıklık gereği, ölçüm noktası, şebeke empedansı ve gerçek etki birlikte değerlendirilmelidir. Tek spektrum görüntüsü arıza kanıtı değildir.

_Kaynaklar: S2, S3, S4_

### Aktif harmonik filtre supraharmoniği mutlaka çözer mi?

Hayır. Aktif harmonik filtrenin çalışma bandı ve kontrol amacı 2–150 kHz sorunu kapsamayabilir. Kaynak, kuplaj yolu ve mağdur cihaz doğrulanmadan filtre seçmek etkisiz veya olumsuz olabilir.

_Kaynaklar: S1, S3, S4_

## İnsan onay komutu

PR sahibinin veya repository yetkilisinin yorumu:

```text
/cms approve supraharmonik-2-150-khz-olcum-kaynak-ayrimi
```

Onay iş akışı kalite puanı, kaynak güncelliği, iç linkler, kanibalizasyon ve risk sınırlarını yeniden çalıştırmadan canonical dosya üretmez.
