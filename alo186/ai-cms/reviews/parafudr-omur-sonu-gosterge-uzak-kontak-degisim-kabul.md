# ALO186 AI CMS inceleme paketi — parafudr-omur-sonu-gosterge-uzak-kontak-degisim-kabul

> Bu dosya canonical yayına dahil edilmez. PR incelemesi ve insan onayı için üretilmiştir.

## Durum

- State: **approved**
- Risk: **high**
- Model: **gpt-5.6-thinking**
- Kalite: **88/100**
- Benzerlik: **0.29** — https://www.alo186.com/haberler/parafudr-gosterge-kirmizi-yesil-uzak-kontak-degisim
- Kelime: **935**

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

- **S1 · IEC** — [IEC 61643-11:2025 — AC low-voltage surge protective devices](https://webstore.iec.ch/en/publication/65314) — erişim 2026-08-03 — birincil
- **S2 · IEC** — [IEC 60364-5-53:2019+A1:2020+A2:2024 — Selection and erection](https://webstore.iec.ch/en/publication/104394) — erişim 2026-08-03 — birincil
- **S3 · Schneider Electric** — [When does the Resi9 SPD need to be replaced?](https://www.se.com/nz/en/faqs/FAQ000264974/) — erişim 2026-08-03 — birincil
- **S4 · Schneider Electric** — [ASCO Model 450/460/480 SPD installation and operation manual](https://www.se.com/us/en/download/document/SPD-UM-SPIOMM450460480/) — erişim 2026-08-03 — birincil
- **S5 · Schneider Electric** — [Surgelogic Push To Test diagnostic function](https://www.se.com/us/en/faqs/FA123373/) — erişim 2026-08-03 — birincil

## SEO

- Title: `Parafudr Ömür Sonu Göstergesi ve Değişim Kabulü`
- H1: `Parafudr kırmızı gösterge verdiğinde ne yapılır?`
- Description: `Parafudr kırmızı/sönük göstergesini, termik ayırıcıyı, yedek korumayı ve uzaktan alarmı doğrulayın; kartuş değişimini kabul dosyasıyla tamamlayın.`
- Canonical: `/haberler/parafudr-omur-sonu-gosterge-uzak-kontak-degisim-kabul`
- Birincil anahtar kelime: `parafudr kırmızı gösterge değişim`

## Doğrudan cevap

Parafudr kırmızı veya sönük gösterge verdiğinde renk anlamı önce tam ürün kılavuzundan doğrulanmalıdır. Bazı modellerde kırmızı bayrak kartuşun ömür sonuna ulaştığını ve değiştirilmesi gerektiğini, bazı LED’lerde ise besleme ya da bağlantı sorunu dahil servis ihtiyacını gösterir. Kabul; termik ayırıcı ile yedek sigorta/kesicinin ayrılması, doğru uyumlu kartuş, LOTO ve gerilimsizlik, bağlantı-tork kontrolü, uzaktan kuru kontak/BMS alarmı ve değişim sonrası gösterge testinin kayıt altına alınmasıyla tamamlanır.

## Parafudr kırmızı veya sönük gösterge verdiğinde ilk karar nedir?

Parafudrun görsel göstergesi modelin koruma modülü ve termik ayırıcısı hakkında durum bilgisi verir; renk anlamı evrensel değildir. Schneider Resi9 örneğinde beyaz gösterge korumanın sürdüğünü, kırmızı gösterge kartuşun değiştirilmesi gerektiğini belirtir. Diğer cihazlarda yeşil LED’in sönmesi besleme, bağlantı veya modül arızasına işaret edebilir. Bu nedenle gösterge her zaman ürün kılavuzuyla okunmalıdır.

Kırmızı bayrağı bantla kapatmak, alarmı yalnız susturmak veya kartuşu yeniden takıp 'düzeldi' saymak korumayı geri getirmez. Öte yandan sönük LED de kartuşun kesin öldüğünü tek başına kanıtlamayabilir; önce yetkin personel doğru gerilim, faz ve bağlantının mevcut olduğunu üretici prosedürüne göre doğrular. Enerjili panoda kullanıcı müdahalesi yapılmamalıdır.

- SPD’nin tam ürün kodu ve gösterge açıklamasını kılavuzdan doğrulayın.
- Renk veya LED anlamını başka marka/modelden kopyalamayın.
- Alarmı susturmayı korumanın geri gelmesi sanmayın.
- Kırmızı/sönük durumda kritik yükleri korunuyor varsaymayın.

_Kaynaklar: S1, S3, S4, S5_

## Ömür sonu göstergesi, termik ayırıcı ve yedek sigorta nasıl ayrılır?

SPD içindeki doğrusal olmayan eleman darbeler ve sürekli anormal gerilim nedeniyle yaşlanabilir. Dahili termik ayırıcı güvenli biçimde devreden çıkarak durum göstergesini değiştirebilir. Bunun yanında haricî yedek sigorta veya kesici kısa devre/arıza akımını yönetir. Kartuş göstergesinin sağlam olması haricî yedek korumanın kapalı veya sağlam olduğunu tek başına göstermez.

IEC 61643-11:2025 SPD performans ve güvenlik testlerini; IEC 60364-5-53 ise koruma, ayırma, anahtarlama ve izleme cihazlarının seçimi/tesisini kapsar. Kabulde SPD tipi ve Uc/Up/In/Imax/Iimp değerleri kadar üreticinin SCPD tablosu, prospektif kısa devre akımı, sigorta-kesici durumu, bağlantı iletkenleri ve topraklama yolu da kontrol edilmelidir.

- Dahili termik ayırıcı ile haricî SCPD’yi ayrı satırlarda gösterin.
- Yedek sigorta/kesici model ve anma değerini üretici tablosuyla eşleştirin.
- Faz, nötr ve N-PE modüllerinin durumunu ayrı kontrol edin.
- Yanmış veya ısınmış bağlantıyı yalnız kartuş değişimiyle kapatmayın.

_Kaynaklar: S1, S2, S4_

## Test düğmesi ve uzaktan alarm kontağı gerçekte neyi doğrular?

Bazı endüstriyel SPD’lerde test düğmesi gösterge, alarm ve teşhis devresini sınar; cihazın yıldırım darbesi altında gerçek koruma kapasitesini yeniden üretmez. Schneider Surgelogic örneğinde düğme LED ve sesli alarm teşhisini test eder, arızalı fazda kırmızı gösterge servis gerektirir. Dolayısıyla test düğmesinin başarılı olması bütün MOV/koruma yollarının saha darbesine karşı yeni olduğu anlamına gelmez.

Kuru kontak veya uzaktan transfer kontağı BMS, SCADA ya da yangın/teknik alarm sistemine “servis/değişim” bilgisini taşıyabilir. Kabulde normal, alarm ve enerjisiz durum kontak mantığı; kablo kopması, yardımcı besleme kaybı, alarm susturma ve BMS mesajı birlikte test edilmelidir. Uzaktan alarmın çalışması görsel pano kontrolünün ve periyodik bakımın yerine geçmez.

- Test düğmesinin yalnız teşhis devresini mi sınadığını kılavuzdan okuyun.
- Kuru kontak NO/NC mantığını normal ve arıza durumunda kaydedin.
- BMS alarm metni ile gerçek faz/modül durumunu eşleştirin.
- Alarm susturulduğunda kalıcı arıza göstergesinin görünür kaldığını doğrulayın.

_Kaynaklar: S3, S4, S5_

## Kartuş değişimi hangi kontrollerle tamamlanmalıdır?

Değişim yalnız aynı fiziksel yuvaya uyan bir kartuş takmak değildir. Yeni modülün ürün ailesi, kutup, Uc, Tip/Test Class, Up ve darbe akımı değerleri ana tabanla uyumlu olmalı; üretici farklı kartuşların karıştırılmasına izin vermelidir. Değişimden önce enerji güvenli biçimde kesilir, LOTO uygulanır ve gerilimsizlik yetkin ekipçe doğrulanır.

Eski modülün arıza nedeni araştırılmadan yeni kartuş takılırsa sürekli aşırı gerilim, yanlış şebeke sistemi, gevşek bağlantı, yetersiz SCPD veya N-PE hatası yeni modülü tekrar bozabilir. Değişim sonrası tork, iletken uzunluğu, yedek koruma, gösterge, uzaktan kontak ve BMS alarm reseti kontrol edilir; tarih, faz ve modül kodu bakım kaydına yazılır.

- Yalnız üreticinin uyumlu gösterdiği kartuşu kullanın.
- LOTO ve gerilimsizlik doğrulaması olmadan kartuş çekmeyin.
- Kök neden olarak sürekli aşırı gerilim ve bağlantı ısınmasını inceleyin.
- Değişim sonrası gösterge, kuru kontak ve alarm resetini test edin.

_Kaynaklar: S1, S2, S3, S4_

## Parafudr bakım ve değişim kabul dosyası nasıl oluşturulur?

Dosyada tek hat, pano konumu, SPD taban ve kartuş ürün kodları, tip/sınıf, Uc-Up-Iimp-In-Imax, bağlantı kesiti ve yaklaşık toplam uzunluğu, topraklama sistemi, yedek koruma, görsel gösterge, uzaktan kontak, son kontrol tarihi, olay geçmişi ve değiştirilen modüller bulunmalıdır. Çok fazlı sistemde her faz ve N-PE modülü ayrı satırda izlenmelidir.

Parafudr için herkese uyan sabit bir takvim ömrü ilan edilmemelidir. Üretici talimatı, durum göstergesi, uzaktan alarm, yıldırım/arıza olayı ve periyodik pano kontrolü birlikte karar verir. Sistem göstergeleri normal, bağlantılar ve SCPD uygun ise yalnız yaşı nedeniyle kartuş değiştirmek gerekmeyebilir. CTA: kişisel verisiz SPD durum–SCPD–alarm–değişim matrisini bakım ekibine teslim edin.

- Her modülü faz ve pano konumuyla tekilleştirin.
- Yıldırım, aşırı gerilim ve sigorta açma olaylarını zaman çizelgesine ekleyin.
- Değişim nedenini ve yeni kartuş kodunu imzalı kaydedin.
- Kanıt normal ise gereksiz kartuş veya komple SPD değişimi satın almayın.

_Kaynaklar: S1, S2, S3, S4, S5_

## Sık sorulan sorular

### Parafudr göstergesi kırmızıysa elektrik çalışmaya devam eder mi?

Tesis enerjili kalabilir ancak ilgili SPD kartuşu koruma dışı olabilir. Kırmızı göstergenin anlamı model kılavuzundan doğrulanmalı ve yetkin personel güvenli değişim planlamalıdır.

_Kaynaklar: S3, S4_

### Parafudrun test düğmesi yıldırıma karşı koruduğunu kanıtlar mı?

Genellikle hayır. Bazı cihazlarda düğme LED, alarm ve teşhis devresini test eder; gerçek darbe koruma kapasitesini saha şartında yeniden test etmez.

_Kaynaklar: S4, S5_

### Kırmızı kartuşu aynı amperde herhangi bir marka ile değiştirebilir miyim?

Hayır. Taban-kartuş uyumu, Uc, tip/test sınıfı, Up ve darbe akımı değerleri ile üretici onayı gerekir. Fiziksel olarak uyması elektriksel koordinasyonu kanıtlamaz.

_Kaynaklar: S1, S2, S3_

### Parafudr kaç yılda bir değiştirilir?

Herkes için geçerli tek süre yoktur. Üretici bakım talimatı, durum göstergesi, alarm, olay geçmişi, çevre koşulları ve saha kontrolü birlikte değerlendirilir.

_Kaynaklar: S1, S3, S4_

## İnsan onay komutu

PR sahibinin veya repository yetkilisinin yorumu:

```text
/cms approve parafudr-omur-sonu-gosterge-uzak-kontak-degisim-kabul
```

Onay iş akışı kalite puanı, kaynak güncelliği, iç linkler, kanibalizasyon ve risk sınırlarını yeniden çalıştırmadan canonical dosya üretmez.
