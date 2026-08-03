# ALO186 AI CMS inceleme paketi — vpp-telemetri-setpoint-feedback-veri-boslugu-kabul

> Bu dosya canonical yayına dahil edilmez. PR incelemesi ve insan onayı için üretilmiştir.

## Durum

- State: **approved**
- Risk: **legal**
- Model: **gpt-5.6-thinking**
- Kalite: **88/100**
- Benzerlik: **0.21** — https://alo186.com/haberler/ups-bakim-bypass-geri-besleme-kilitleme-kabul-testi
- Kelime: **1008**

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

- **S1 · TEİAŞ** — [Elektrik Depolama Ünite veya Tesislerinin Yan Hizmetlerde Kullanılmasına Dair Teknik Kriterler ve Test Prosedürleri — 3 Temmuz 2026 duyurusu](https://www.teias.gov.tr/duyurular/elektrik-depolama-unite-veya-tesislerinin-yan-hizmetlerde-kullanilmasina-dair-teknik-kriterler-ve-test-prosedurleri) — erişim 2026-08-03 — birincil
- **S2 · TEİAŞ** — [Elektrik Depolama Ünite veya Tesislerinin Yan Hizmetlerde Kullanılmasına Dair Teknik Kriterler ve Test Prosedürleri — güncel PDF](https://webim.teias.gov.tr/file/70ddcfe5-9018-43f3-b708-4c69399a18a6?download=) — erişim 2026-08-03 — birincil
- **S3 · TEİAŞ** — [Elektrik Depolama Tesislerinin İzlenmesi ve Kontrol Edilmesine İlişkin Usul ve Esaslar](https://webim.teias.gov.tr/file/9dc2089d-bd8a-4399-9dd7-326252daa4f1?download=) — erişim 2026-08-03 — birincil
- **S4 · IEC** — [IEC 61850-7-420:2021 — DER and distribution automation information models](https://webstore.iec.ch/en/publication/34384) — erişim 2026-08-03 — birincil
- **S5 · OpenADR Alliance** — [OpenADR 3 Introduction and Certification Program](https://www.openadr.org/index.php?Itemid=194&catid=20%3Ageneral-site-content&id=210%3Aopenadr-3-0&option=com_content&view=article) — erişim 2026-08-03 — birincil

## SEO

- Title: `VPP Telemetri, Setpoint Geri Bildirimi ve Veri Boşluğu Kabulü`
- H1: `VPP'de komut gönderildi demek neden yetmez, telemetri nasıl kabul edilir?`
- Description: `VPP komutunu; kabul, uygulama, ölçülen P/Q/SoC tepkisi, zaman damgası, veri boşluğu ve güvenli fallback kanıtıyla uçtan uca doğrulayın.`
- Canonical: `/haberler/vpp-telemetri-setpoint-feedback-veri-boslugu-kabul`
- Birincil anahtar kelime: `VPP telemetri kabul testi`

## Doğrudan cevap

VPP'de bir komutun 'gönderildi' görünmesi, kaynağın komutu kabul edip fiziksel olarak uyguladığını kanıtlamaz. Uçtan uca kabul; kaynak kimliği ve yetkisi, komut kimliği ve zaman damgası, kabul/red cevabı, uygulanan setpoint geri bildirimi, bağlantı noktasında ölçülen P–Q–SoC tepkisi, rampa ve süre, kesici/çalışma modu, eksik-gecikmiş-yinelenen veri sınıfları ile haberleşme kaybındaki güvenli yerel davranışı birlikte doğrulamalıdır. Gerçek müşteri kimliği, açık adres, özel anahtar veya canlı kontrol parolası test dosyasına yüklenmemelidir. Teknik kabul, piyasa katılımı veya gelir garantisi değildir.

## Gönderildi, kabul edildi, uygulandı ve ölçüldü durumları nasıl ayrılır?

VPP komut zinciri en az dört aşama içerir: platform komutu üretir, saha ağ geçidi veya DERMS komutu alır, kaynak kontrolörü komutu kabul edip uygular ve sayaç/SCADA bağlantı noktasındaki fiziksel tepkiyi ölçer. Her aşama için ayrı zaman damgası, benzersiz komut kimliği, durum kodu ve hata nedeni tutulmazsa başarılı görünen işlem yanlış kaynağa gitmiş, reddedilmiş veya yerel limitte kırpılmış olabilir.

TEİAŞ'ın güncel depolama yan hizmet kriterleri, belirli hizmetlerde TEİAŞ izleme sistemiyle veri alışverişi için yazılım ve donanım ile performans kanıtı ister; hizmetlerin bağlantı noktasında izlenmesini öngörür. Bu ulusal kriterler belirli güç ve piyasa kapsamlarına yöneliktir. Tesis içi veya dağıtım seviyesindeki bir VPP için de komut ile ölçümün ayrılması iyi mühendislik uygulamasıdır, ancak resmî katılım koşulu gibi genellenmemelidir.

- Her komuta tekil kimlik ve ortak zaman tabanı verin.
- Gönderim, kabul, uygulama ve ölçüm durumlarını ayrı alanlarda tutun.
- Yerel limit veya SoC nedeniyle kırpılan komutu başarı saymayın.
- Bağlantı noktası ölçümünü yalnız cihaz ekranı geri bildirimiyle değiştirmeyin.

_Kaynaklar: S1, S2, S3, S4, S5_

## VPP kaynak envanterinde hangi kimlik ve kabiliyetler doğrulanmalıdır?

Her DER için platform kimliği, tesis ve bağlantı noktası eşleşmesi, cihaz türü, nominal ve kullanılabilir güç/enerji, şarj-deşarj yönü, SoC/SoH, aktif-reaktif güç sınırları, rampa, minimum çalışma süresi, kesici durumu, kontrol modu, yerel öncelikler ve uzaktan kontrol yetkisi tutulmalıdır. Aynı cihazın farklı platformlarda çift kaydı veya yanlış CT yönü toplam VPP kapasitesini ve ölçülen tepkiyi hatalı gösterebilir.

TEİAŞ izleme ve kontrol usulünün SCADA ekinde kullanılabilir enerji, SoH, SoC, aktif güç emreamadeliği ve gerçek zamanlı güç gibi alanlar yer alır. IEC 61850-7-420, fiziksel ve sanal olarak toplanmış DER'ler için ortak bilgi modelleri tanımlar. Kabulde veri alanının adı kadar birimi, işareti, kalite biti, güncelleme sıklığı ve geçerlilik süresi de sözleşmeye bağlanmalıdır.

- DER kimliğini sayaç ve bağlantı noktasıyla eşleştirin.
- MW/MWh, işaret ve şarj-deşarj yönünü test verisiyle doğrulayın.
- SoC, SoH, kullanılabilir enerji ve güç limitlerini ayrı alanlarda tutun.
- Eski veya kalitesiz veriyi güncel kapasite gibi toplamaya dahil etmeyin.

_Kaynaklar: S2, S3, S4_

## Setpoint, rampa ve çalışma modu testi hangi senaryoları kapsamalıdır?

Test; sıfırdan pozitif/negatif aktif güç, reaktif güç veya güç faktörü, farklı rampa hızları, SoC sınırı, kesici açık/kapalı, yerel kontrol önceliği ve acil durdurma senaryolarını kapsar. Komutun kabul cevabı ile gerçek setpoint feedback ve ölçülen P/Q trendi aynı grafikte gösterilir. Hedefe ulaşma süresi, aşım, salınım, kararlı hata ve komutun hangi nedenle sınırladığı kaydedilir.

TEİAŞ'ın 3 Temmuz 2026 kriterleri belirli yan hizmetler için tepki ve izleme koşulları tanımlar; örneğin primer ve sekonder frekans kontrolünde zaman ve rezerv koşulları bulunur. Bu sayılar her VPP ürünü için evrensel SLA değildir. Kabul sınırı ilgili hizmet anlaşması, kaynak modeli, bağlantı şartı ve güncel mevzuattan alınmalı; test sırasında sonradan gevşetilmemelidir.

- Pozitif ve negatif güç yönlerini ayrı test edin.
- Setpoint feedback ile sayaç ölçümünü aynı grafikte gösterin.
- Rampa, aşım, salınım ve kalıcı hatayı ölçün.
- Piyasa hizmeti sınırını başka proje veya ülkeden kopyalamayın.

_Kaynaklar: S1, S2, S3_

## Eksik, gecikmiş veya yinelenen telemetride VPP nasıl güvenli kalır?

Telemetri her örnek için olay zamanı, alım zamanı, sıra numarası ve kalite bilgisi taşımalıdır. Eksik paket, geç gelen veri, yinelenen veri, saat sapması ve kaynak yeniden başlatması ayrı sınıflandırılır. Platformun son değeri sınırsız süre taşımaması, stale eşiğinde kapasiteyi düşürmesi ve raporda veri boşluğunu görünür bırakması gerekir. Sonradan doldurulan veriler gerçek zamanlı performansla karıştırılmamalıdır.

Haberleşme kaybında kaynak; onaylı güvenli yerel moda, son geçerli sınırlı setpointe veya sıfıra dönme gibi proje tarafından tanımlanan davranışı uygular. OpenADR 3 program, event, report ve endpoint etkileşimlerini REST tabanlı bilgi modeliyle ele alır; IEC 61850 bilgi modelleri saha verisinin anlamını standardize eder. Protokol kullanmak tek başına güvenli fallback, siber güvenlik veya performans garantisi değildir.

- Olay ve alım zamanını ayrı kaydedin.
- Stale veri eşiğini ve kapasite düşürme kuralını tanımlayın.
- Haberleşme kaybı fallback'ini kontrollü test edin.
- Sonradan doldurulan veriyi gerçek zamanlı yanıt gibi raporlamayın.

_Kaynaklar: S3, S4, S5_

## VPP telemetri kabul dosyası nasıl oluşturulmalıdır?

Dosya; mimari ve veri akışı, kaynak envanteri, kimlik-yetki matrisi, protokol/sürüm, zaman senkronu, alan sözlüğü, birim ve işaretler, güncelleme ve stale eşikleri, komut kimliği, cevap kodları, setpoint/feedback/ölçüm trendleri, P-Q-SoC-kesici-mod verileri, veri boşlukları, yeniden bağlantı ve fallback sonuçları, test sürümü ve açık maddeleri içermelidir. Ham mesajlar gizli bilgi temizlenerek saklanmalıdır.

Kabul, platformun belirli test koşullarında izlenebilir komut ve ölçüm zinciri oluşturduğunu gösterir; toplayıcılık lisansı, yan hizmet katılımı, kapasite ödemesi veya gelir garantisi değildir. Gerçek müşteri adı, açık adres, sayaç numarası, özel anahtar, erişim tokenı ve canlı kontrol parolası ALO186'e yüklenmemelidir. CTA: kişisel verisiz VPP komut–kabul–feedback–ölçüm–veri boşluğu kabul matrisini SCADA/DERMS ve piyasa uzmanlarına iletin.

- Alan sözlüğü ve test sürümünü dosyaya sabitleyin.
- Ham mesajlardan kimlik ve erişim sırlarını çıkarın.
- Teknik kabul ile mevzuat/piyasa uygunluğunu ayrı imzalatın.
- Kanıt yoksa kapasite veya gelir iddiası yayımlamayın.

_Kaynaklar: S1, S2, S3, S4, S5_

## Sık sorulan sorular

### VPP komutu 'başarılı' görünüyorsa kaynak mutlaka tepki vermiş midir?

Hayır. Başarı yalnız API alındısını gösterebilir. Uygulanan setpoint geri bildirimi ve bağlantı noktasındaki P/Q/SoC ölçümü birlikte doğrulanmalıdır.

_Kaynaklar: S1, S2, S3_

### VPP telemetrisi kaç saniyede bir gelmelidir?

Tek bir evrensel süre yoktur. Yan hizmet, bağlantı şartı, protokol ve kaynak dinamiğine göre sözleşmede belirlenir; güncelleme, gecikme ve stale eşikleri birlikte yazılmalıdır.

_Kaynaklar: S1, S2, S4, S5_

### İnternet kesilirse VPP cihazları son komutta kalmalı mı?

Proje bazlıdır. Güvenli fallback; son geçerli sınırlı setpoint, yerel kontrol veya sıfır güç gibi onaylı davranış olabilir. Sınırsız süre kör biçimde son komutta kalmak kabul edilmemelidir.

_Kaynaklar: S3, S4, S5_

### Bu test VPP'nin TEİAŞ yan hizmetlerine katılabileceğini kanıtlar mı?

Hayır. Teknik telemetri kabulü yalnız veri ve kontrol zincirini doğrular. Güncel TEİAŞ/EPDK kriterleri, performans sertifikası, anlaşma ve piyasa yükümlülükleri ayrıca sağlanmalıdır.

_Kaynaklar: S1, S2, S3_

## İnsan onay komutu

PR sahibinin veya repository yetkilisinin yorumu:

```text
/cms approve vpp-telemetri-setpoint-feedback-veri-boslugu-kabul
```

Onay iş akışı kalite puanı, kaynak güncelliği, iç linkler, kanibalizasyon ve risk sınırlarını yeniden çalıştırmadan canonical dosya üretmez.
