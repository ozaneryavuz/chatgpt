# ALO186 AI CMS inceleme paketi — kacak-akim-toplam-kacak-butcesi-istenmeyen-acma-teshisi

> Bu dosya canonical yayına dahil edilmez. PR incelemesi ve insan onayı için üretilmiştir.

## Durum

- State: **approved**
- Risk: **high**
- Model: **GPT-5.6 Thinking**
- Kalite: **100/100**
- Benzerlik: **0.37** — https://alo186.com/haberler/kacak-akim-rolesi-toplam-kacak-akim-emc-filtre-ups-surucu
- Kelime: **994**

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

- **S1 · IEC** — [IEC 60364-5-53:2019+A1:2020+A2:2024 — Koruma ve anahtarlama cihazlarının seçimi](https://webstore.iec.ch/en/publication/104394) — erişim 2026-08-03 — birincil
- **S2 · Schneider Electric** — [UPS tesislerinde RCD, toprak kaçağı ve istenmeyen açma](https://www.se.com/us/en/faqs/FAQ000281380/) — erişim 2026-08-03 — birincil
- **S3 · Schneider Electric** — [UPS giriş tarafında RCD ve kümülatif kaçak akım](https://www.se.com/us/en/faqs/FA157373/) — erişim 2026-08-03 — birincil
- **S4 · Schneider Electric** — [Arıza olmadan toprak kaçağı korumasının açma nedenleri](https://www.se.com/eg/en/faqs/FA277483/) — erişim 2026-08-03 — birincil

## SEO

- Title: `Toplam Kaçak Akım Bütçesi ve RCD Açma Teşhisi`
- H1: `Toplam kaçak akım bütçesi nasıl çıkarılır ve RCD neden gereksiz açar?`
- Description: `UPS, inverter, EVSE ve elektronik yüklerde biriken koruma iletkeni akımlarını ölçerek gerçek izolasyon arızasını istenmeyen RCD açmasından ayırın.`
- Canonical: `/haberler/kacak-akim-toplam-kacak-butcesi-istenmeyen-acma-teshisi`
- Birincil anahtar kelime: `toplam kaçak akım bütçesi`

## Doğrudan cevap

RCD’nin sık açması her zaman tek bir arızalı cihaz olduğu anlamına gelmez. UPS, inverter, EVSE, LED sürücüler ve IT güç kaynaklarının EMI filtreleri koruma iletkenine normal çalışma akımı taşıyabilir; aynı koruma cihazı altındaki yükler arttıkça bu akımlar toplanır ve anahtarlama anındaki kısa darbelerle açma eşiğine yaklaşabilir. Güvenli teşhis; devre topolojisi, RCD tipi, nötr karışması, sürekli ve olay anı kaçak akım ölçümü ile yüklerin kontrollü ayrılmasını birlikte kaydetmelidir. Koruma cihazını büyütmek, köprülemek veya iptal etmek ölçüm yerine geçmez.

## Gerçek izolasyon arızası ile toplam normal kaçak akımı nasıl ayırırsınız?

Elektronik cihazların şebeke girişindeki EMI filtreleri, ortak mod gürültüsünü sınırlamak için faz veya nötr ile koruma iletkeni arasında kapasitif yollar kullanabilir. Bu nedenle cihaz sağlamken de küçük koruma iletkeni akımları oluşabilir. Schneider Electric, UPS girişinde görülen kaçağın UPS ile bağlı yüklerin toplamı olduğunu ve çoklu IT yüklerinin 30 mA sınıfı bir korumayı istenmeyen biçimde açtırabileceğini açıklar.

Bu açıklama, gerçek arızanın önemsiz olduğu anlamına gelmez. İzolasyon bozulması, nem, kablo hasarı, nötrlerin farklı RCD grupları arasında karışması ve yanlış N–PE bağlantıları aynı belirtiyi üretebilir. Kanıt dosyası sürekli taban akımı, yük eklenince değişim, olay anı tepe değeri ve izolasyon test sonuçlarını ayrı sütunlarda göstermelidir.

- Her RCD’nin beslediği devre ve yükleri tek hat üzerinde işaretleyin.
- Sürekli koruma iletkeni akımı ile olay anındaki darbeyi ayrı kaydedin.
- Nötr karışması ve istenmeyen N–PE bağlantısını kontrol ettirin.
- Nem, kablo ve cihaz izolasyon bulgularını toplam kaçak bütçesinden ayrı tutun.

_Kaynaklar: S1, S2, S3_

## Kaçak akım bütçesi hangi ölçümlerle hazırlanmalıdır?

Yetkili personel, uygun kaçak akım pensiyle önce ana koruma iletkenindeki veya tüm aktif iletkenlerin birlikte kavrandığı ölçüm noktasındaki artık akımı kaydeder. Ardından kritik yükleri rastgele söküp takmak yerine, onaylı bir sıra içinde devre bazında değişimi izler. Amaç yalnız tek bir anlık değer değil; normal işletme, ilk enerjilenme, UPS transferi, inverter startı, EV şarj başlangıcı ve yüksek yük anlarının karşılaştırılmasıdır.

Ölçüm aralığı ve cihaz bant genişliği raporda belirtilmelidir. Milisaniyelik anahtarlama darbeleri sıradan bir el tipi ölçümde görünmeyebilir. Olay kaydedici veya uygun güç kalitesi analizörü kullanılıyorsa zaman damgası RCD açma kaydı, UPS olay günlüğü ve otomasyon loguyla eşleştirilmelidir.

- Normal işletme taban değerini en az üç farklı yük seviyesinde kaydedin.
- İlk enerjilenme, transfer ve şarj başlangıcını ayrı olay olarak etiketleyin.
- Ölçüm cihazının aralık, bant genişliği ve kalibrasyon bilgisini yazın.
- Aynı saat çizelgesinde RCD, UPS, EVSE ve otomasyon olaylarını birleştirin.

_Kaynaklar: S2, S3, S4_

## RCD tipi, hassasiyet ve selektivite kararı nasıl verilmelidir?

IEC 60364-5-53, güvenlik amaçlı koruma, ayırma ve kontrol cihazlarının seçimi ile tesisini kapsar. Uygun RCD tipi ve eşik; topraklama düzeni, son devre koruma ihtiyacı, güç elektroniğinin üretebileceği artık akım biçimi, üretici talimatı ve yerel mevzuat birlikte değerlendirilerek belirlenmelidir. Tek başına “daha yüksek mA” seçmek veya her devreye aynı tip cihaz koymak doğru koordinasyon değildir.

Schneider kaynakları UPS ve bağlı IT yüklerinde sürekli kaçak, transfer darbeleri, ortak mod filtreleri ve nötr karışmasının açmaya yol açabileceğini; bazı uygulamalarda özel devre, uygun tip veya seçici zaman gecikmeli çözüm gerekebileceğini belirtir. Bu, son devrelerdeki can koruma gereğini kaldırmaz. Üst ve alt kademenin görevleri, açma süreleri ve üretici eğrileri kanıtlanmalıdır.

- Topraklama sistemi ve koruma amacını yazmadan RCD seçmeyin.
- Son devre can koruması ile üst kademe yangın/selektivite görevini ayırın.
- UPS, sürücü ve EVSE üreticisinin artık akım tipini doğrulayın.
- Seçiciliği yalnız etiketle değil, açma süresi ve test sonucu ile kaydedin.

_Kaynaklar: S1, S2, S3_

## Kontrollü yük ayırma ve onarım sonrası kabul nasıl yapılır?

Teşhis sırasında kullanıcıların cihazları tekrar tekrar fişe takması veya panoda devre ayırması güvenli değildir. Yetkili ekip, operasyonel kesinti planına göre yük gruplarını ayırır; her adımda artık akımın ne kadar değiştiğini ve RCD’nin hangi koşulda açtığını kaydeder. Kritik IT, yangın, haberleşme veya sağlık yüklerinde geçici enerji düzeni ayrıca planlanmalıdır.

Bulgu gerçek izolasyon arızasıysa onarım sonrası izolasyon, koruma iletkeni sürekliliği ve RCD fonksiyon testi yapılır. Sorun toplam normal kaçaksa devrelerin güvenli bölünmesi, üreticiye uygun koruma tipi, nötr düzeninin düzeltilmesi veya filtre/topoloji çözümü değerlendirilir. Kabul, normal yük ve en olumsuz beklenen geçiş senaryosunda tekrarlanmalıdır.

- Yük ayırma sırasını operasyon ve güvenlik sorumlularıyla onaylayın.
- Her adımda akım değişimini ve açma zamanını kaydedin.
- Onarım sonrası izolasyon, süreklilik ve RCD testini tekrarlayın.
- Kabulü yalnız boşta değil, gerçek yük ve transfer senaryosunda yapın.

_Kaynaklar: S1, S2, S4_

## Teknik kanıt dosyası hangi sonucu üretmelidir?

Dosya; tek hat, RCD marka/model/tip/eşik, devre listesi, taban kaçak akımı, olay tepe değeri, cihaz grupları, nötr kontrolü, izolasyon sonuçları, olay logları, düzeltme ve tekrar testinden oluşmalıdır. Böylece “RCD bozuk” veya “UPS uyumsuz” gibi erken sonuçlar yerine, ölçülen neden ile düzeltme arasında izlenebilir bağ kurulur.

Mevcut cihazlar üretici sınırları içinde çalışıyor, nötr düzeni doğru ve devre bölünmesiyle güvenli marj sağlanıyorsa yeni UPS, RCD veya filtre satın almak gerekmeyebilir. Buna karşılık izolasyon arızası veya yanlış bağlantı varsa daha dayanıklı RCD seçmek tehlikeyi gizlememelidir. Sonuç, satın alma değil güvenli koruma ve süreklilik kabulüdür.

- Tek hat, ölçüm ve olay loglarını tek dosyada sürümleyin.
- Her düzeltmeyi öncesi–sonrası ölçümle bağlayın.
- Mevcut sistem yeterliyse satın almama sonucunu açıkça yazın.
- Koruma seviyesini düşüren veya RCD’yi devre dışı bırakan çözümü reddedin.

_Kaynaklar: S1, S2, S3, S4_

## Sık sorulan sorular

### Kaçak akım rölesi atıyorsa mutlaka bir cihaz arızalı mıdır?

Hayır. Gerçek izolasyon arızası önemli bir olasılıktır; ancak birden çok elektronik yükün normal filtre akımları, nötr karışması veya kısa anahtarlama darbeleri de aynı koruma altında birleşerek açmaya neden olabilir. Ölçüm yapılmadan arıza veya cihaz değişimi kararı verilmemelidir.

_Kaynaklar: S2, S3, S4_

### 30 mA RCD yerine 100 mA takmak sorunu çözer mi?

Bu değişiklik koruma amacını ve yerel gereklilikleri bozabilir. Eşik, tip ve selektivite; topraklama sistemi, devre görevi, üretici talimatı ve ölçülen artık akım biçimiyle yetkili mühendis tarafından belirlenmelidir. Rastgele eşik büyütmek güvenli çözüm değildir.

_Kaynaklar: S1, S2_

### UPS bağlıyken kaçak akım neden yükselir?

UPS’nin kendi EMI filtreleri ile çıkışına bağlı IT ve elektronik yüklerin koruma iletkeni akımları girişte birlikte görülebilir. Transfer, kapasitör şarjı ve ortak mod anahtarlama darbeleri de kısa süreli artış oluşturabilir.

_Kaynaklar: S2, S3_

### Kaçak akım pensiyle tek ölçüm yeterli midir?

Hayır. Tek anlık değer olay anını kaçırabilir. Normal yük, enerjilenme, transfer, şarj başlangıcı ve farklı devre kombinasyonları zaman damgalı olarak karşılaştırılmalı; izolasyon ve nötr düzeni testleriyle birlikte yorumlanmalıdır.

_Kaynaklar: S2, S4_

## İnsan onay komutu

PR sahibinin veya repository yetkilisinin yorumu:

```text
/cms approve kacak-akim-toplam-kacak-butcesi-istenmeyen-acma-teshisi
```

Onay iş akışı kalite puanı, kaynak güncelliği, iç linkler, kanibalizasyon ve risk sınırlarını yeniden çalıştırmadan canonical dosya üretmez.
