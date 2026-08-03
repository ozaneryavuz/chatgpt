# ALO186 AI CMS inceleme paketi — elektrik-kesintisi-sonrasi-otomatik-yeniden-baslatma

> Bu dosya canonical yayına dahil edilmez. PR incelemesi ve insan onayı için üretilmiştir.

## Durum

- State: **approved**
- Risk: **high**
- Model: **gpt-5.6-thinking**
- Kalite: **100/100**
- Benzerlik: **0.18** — https://alo186.com/hesaplama/kombi-elektrik-kesintisi-sonrasi-guvenli-yeniden-baslatma/
- Kelime: **983**

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

- **S1 · ISO** — [ISO 14118:2017 — Safety of machinery, prevention of unexpected start-up](https://www.iso.org/standard/66460.html) — erişim 2026-08-03 — birincil
- **S2 · IEC** — [IEC 60204-1:2016+A1:2021 — Electrical equipment of machines](https://webstore.iec.ch/en/publication/71256) — erişim 2026-08-03 — birincil
- **S3 · ISO** — [ISO 14119:2024 — Interlocking devices associated with guards](https://www.iso.org/standard/75942.html) — erişim 2026-08-03 — birincil

## SEO

- Title: `Kesinti Sonrası Otomatik Yeniden Başlatma Güvenliği`
- H1: `Elektrik gelince makine neden kendiliğinden başlamamalı? Kabul planı`
- Description: `Kesinti sonrası makinenin beklenmedik başlamasını; PLC hafızası, auto-restart, interlock, depolanmış enerji ve kademeli yük testleriyle önleyin.`
- Canonical: `/haberler/elektrik-kesintisi-sonrasi-otomatik-yeniden-baslatma`
- Birincil anahtar kelime: `kesinti sonrası otomatik yeniden başlatma`

## Doğrudan cevap

Elektriğin geri gelmesi makine için tek başına start komutu olmamalıdır. PLC’de kalıcı talep, sürücü auto-restart ayarı, iki telli kumanda, uzaktan otomasyon, farklı kontrol beslemeleri veya depolanmış mekanik enerji beklenmedik hareket oluşturabilir. Güvenli sonuç; risk değerlendirmesi, interlock matrisi, manuel reset/start ayrımı ve şebeke-jeneratör-UPS senaryolarında ölçümlü yeniden başlatma testiyle kanıtlanır.

## Elektriğin geri gelmesi neden otomatik çalışma komutu değildir?

Bir kesinti sona erdiğinde besleme geriliminin geri gelmesi, makinenin hareket etmesi için tek başına yeterli ve güvenli bir komut olmamalıdır. Kesinti sırasında operatör tehlike bölgesine girmiş, malzeme sıkışmış, pnömatik veya hidrolik enerji kalmış ya da uzaktaki otomasyon yeniden başlama talebi tutmuş olabilir. Bu nedenle güç dönüşü ile üretim yeniden başlatma kararı birbirinden ayrılmalıdır.

ISO 14118, beklenmeyen çalışmayı yalnız elektrik enerjisiyle sınırlamaz; hidrolik, pnömatik, yerçekimi, yaylar ve dış etkiler dâhil tüm enerji kaynaklarından doğan hareketi ele alır. IEC 60204-1 de makine elektrik ekipmanı, kontrol devreleri, sürücüler, acil durdurma ve teknik dokümantasyonu bütün olarak değerlendirir. Kabul dosyasının ilk sorusu “enerji geldi mi?” değil, “güvenli yeniden başlatma koşullarının tümü doğrulandı mı?” olmalıdır.

- Şebeke, jeneratör, UPS ve manuel bypass modlarında güç dönüş senaryolarını ayrı tanımlayın.
- Kesinti anında hareket eden ekipman, proses ve tehlike bölgesinde kalabilecek kişileri belirleyin.
- Elektrik dışındaki depolanmış enerji kaynaklarını yeniden başlatma analizine ekleyin.

_Kaynaklar: S1, S2_

## Kontrol devresi, kontaktör ve PLC hafızası nasıl incelenir?

Klasik üç telli start-stop devresinde kontaktör bobininin enerjisi kesilince tutma devresi düşer ve besleme geri geldiğinde yeni bir start komutu gerekir. Ancak iki telli sürekli komut, PLC’de kalıcı bit, uzaktan otomasyon talebi, frekans inverterinde auto-restart parametresi veya bina otomasyonunun son durumu geri yüklemesi makineyi kendiliğinden başlatabilir. Her kontrol kaynağı ve öncelik sırası belgelenmelidir.

Yalnız kontaktör eklemek veya bir parametreyi kapatmak bütün sistemi güvenli yapmaz. Sürücünün STO işlevi, güvenlik rölesi, kapı interlockları, acil stop zinciri, proses izinleri ve mekanik durum birlikte değerlendirilir. Kontrol gücü UPS’ten, motor gücü jeneratörden veya farklı panolardan geliyorsa kaynakların farklı zamanlarda dönmesi beklenmedik komut sırası oluşturabilir.

- Start talebinin kaynağını: buton, PLC, BMS, SCADA, zaman saati veya uzak erişim olarak kaydedin.
- Kalıcı PLC bitleri ve sürücü auto-restart parametrelerini tam program/yedek sürümüyle doğrulayın.
- Kontrol ve güç beslemelerinin şebeke, UPS ve jeneratör üzerindeki dönüş zamanlarını ölçün.

_Kaynaklar: S1, S2, S3_

## Koruyucu kapı ve interlocklar yeniden başlatmada hangi görevi yapar?

Koruyucu kapı interlocku açıldığında tehlikeli hareketin durması gerekir; fakat kapının tekrar kapanması tek başına makineyi başlatma komutu sayılmamalıdır. ISO 14119, koruyucularla ilişkili interlocking cihazlarının tasarım ve seçimini ve öngörülebilir biçimde devre dışı bırakılmalarını azaltan önlemleri ele alır. Sinyalin işlenmesi ve beklenmeyen çalışmanın önlenmesi, ISO 14118 ve ilgili fonksiyonel güvenlik standartlarıyla birlikte değerlendirilir.

Kesintiden sonra reset işlevi, tehlike bölgesinin görülebilirliği, operatörün kontrol konumu ve prosesin durumu risk değerlendirmesine göre tasarlanmalıdır. Reset butonunun güvenlik fonksiyonunu köprülemesi, interlock girişinin yazılımla zorlanması veya acil stopun normal durdurma aracı gibi kullanılması kabul edilmez. Her koruma işlevi gerçek arıza ve güç dönüş senaryosunda test edilmelidir.

- Kapı kapanması, acil stop reseti ve makine start komutunu ayrı olaylar olarak kaydedin.
- Interlockların mekanik montajını, kodlama tipini ve kaçınma/yenilgi riskini inceleyin.
- Tehlike bölgesi görünmüyorsa ilave reset, uyarı veya bölgesel kontrol ihtiyacını risk analiziyle belirleyin.

_Kaynaklar: S1, S3_

## Tesis genelinde kademeli yeniden başlatma planı nasıl kurulur?

Bir tesisin bütün pompaları, fanları, kompresörleri ve proses hatları aynı anda dönerse yüksek kalkış akımı, basınç darbesi, proses taşması veya jeneratör aşırı yükü oluşabilir. Güvenli plan; can güvenliği ve kritik yardımcı sistemleri önce, proses yüklerini ise doğrulanan sıra ve gecikmelerle devreye alır. Ancak zaman gecikmesi tek başına güvenlik fonksiyonu değildir; her ekipmanın yerel izin ve interlockları sağlanmalıdır.

Şebeke dönüşü, ATS yeniden transferi, UPS bypass geçişi ve jeneratör cooldown süreci ayrı test senaryolarıdır. Her senaryoda besleme gerilimi, kontrol gücü, haberleşme, güvenlik zinciri, motor akımı, proses geri bildirimi ve operatör onayı zaman damgasıyla kaydedilir. Yeniden başlatma sırası mevcut elektrik kapasitesi kadar proses güvenliğine de göre tasarlanır.

- Kritik emniyet yardımcılarını, proses ön koşullarını ve normal üretim yüklerini sınıflandırın.
- Her yük için manuel onay, otomatik izin, gecikme ve başarısızlık davranışını tabloya yazın.
- Jeneratör ve şebeke modunda kademeli yük alma testini ayrı gerçekleştirin.
- Başarısız ekipmanın sıradaki diğer ekipmanları nasıl etkilediğini doğrulayın.

_Kaynaklar: S1, S2_

## Yeniden başlatma kabul dosyasında neler bulunmalıdır?

Kabul dosyası tek hat şeması, kontrol mimarisi, enerji kaynakları, risk değerlendirmesi, PLC/sürücü sürümleri, interlock matrisi ve test kayıtlarını bir araya getirmelidir. Test; kısa kesinti, uzun kesinti, kontrol gücünün önce veya sonra dönmesi, uzak komutun aktif kalması, kapı açık olması, acil stop aktif olması ve proses geri bildiriminin kaybolması gibi senaryoları kapsar. Beklenen güvenli durum ve gerçek sonuç yan yana kaydedilir.

Kullanıcı enerjili panoda kontaktör köprülememeli, PLC bitlerini zorlamamalı, güvenlik rölesini bypass etmemeli veya sürücü auto-restart ayarını deneme amacıyla değiştirmemelidir. Ekipman kesintiden sonra kendiliğinden hareket ettiyse olay saati, hangi kaynakta olduğu, aktif alarm ve operatör konumu kaydedilip makine güvenli biçimde devre dışı bırakılmalıdır. Mevcut kontrol tasarımı bütün senaryolarda doğrulanıyorsa gereksiz donanım değişimi yapılmaması geçerli sonuçtur.

- Test cihazı, yazılım sürümü, senaryo, beklenen durum, gerçek sonuç ve sorumluyu kaydedin.
- Her değişiklikten sonra bütün ilgili güvenlik fonksiyonlarını yeniden test edin.
- Yakın kaza veya beklenmedik hareketi yalnız ‘elektrik gidip geldi’ notuyla kapatmayın.

_Kaynaklar: S1, S2, S3_

## Sık sorulan sorular

### Elektrik geldiğinde motorun kendiliğinden başlaması her zaman arıza mıdır?

Bazı süreçler kontrollü otomatik yeniden başlatma için tasarlanabilir; ancak bu davranış risk değerlendirmesi, izinler, interlocklar, uyarılar ve testlerle kanıtlanmalıdır. Güç dönüşünün tek başına start komutu olması güvenli varsayım değildir.

_Kaynaklar: S1, S2_

### Sürücüde auto-restart kapatılırsa sorun tamamen çözülür mü?

Hayır. PLC hafızası, iki telli komut, uzak otomasyon, kontaktör devresi, farklı kontrol beslemeleri ve mekanik depolanmış enerji de beklenmedik hareket oluşturabilir. Bütün komut ve enerji zinciri değerlendirilmelidir.

_Kaynaklar: S1, S2_

### Koruyucu kapıyı kapatmak makineyi tekrar başlatabilir mi?

Kapının kapanması koruma koşulunun geri geldiğini gösterebilir; fakat tek başına başlatma komutu olmamalıdır. Reset ve start işlevleri risk değerlendirmesine göre ayrılmalı, interlockların yenilgiye karşı tasarımı doğrulanmalıdır.

_Kaynaklar: S1, S3_

### Jeneratör devreye girince bütün yükler aynı anda başlayabilir mi?

Bu, elektrik kapasitesi ve proses güvenliği açısından risk oluşturabilir. Kritik yardımcılar ve proses yükleri tanımlı sırayla alınmalı; her ekipmanın yerel izinleri ve başarısızlık davranışı şebeke ve jeneratör modunda test edilmelidir.

_Kaynaklar: S1, S2_

## İnsan onay komutu

PR sahibinin veya repository yetkilisinin yorumu:

```text
/cms approve elektrik-kesintisi-sonrasi-otomatik-yeniden-baslatma
```

Onay iş akışı kalite puanı, kaynak güncelliği, iç linkler, kanibalizasyon ve risk sınırlarını yeniden çalıştırmadan canonical dosya üretmez.
