# ALO186 AI CMS inceleme paketi — ev-sarj-kontaktor-yapismasi-gerilim-algilama-kabul

> Bu dosya canonical yayına dahil edilmez. PR incelemesi ve insan onayı için üretilmiştir.

## Durum

- State: **approved**
- Risk: **high**
- Model: **gpt-5.6-thinking**
- Kalite: **100/100**
- Benzerlik: **0.24** — https://alo186.com/haberler/ev-sarj-kontaktor-yapismasi-weld-detection-cikis-gerilimi
- Kelime: **959**

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

- **S1 · IEC** — [IEC 61851-1:2017 — Electric vehicle conductive charging system](https://webstore.iec.ch/en/publication/33644) — erişim 2026-08-03 — birincil
- **S2 · IEC** — [IEC 61851-1:2017/COR1:2023 — Corrigendum 1](https://webstore.iec.ch/en/publication/89234) — erişim 2026-08-03 — birincil
- **S3 · Texas Instruments** — [TIDA-010239 AC Level 2 charger platform reference design](https://www.ti.com/tool/TIDA-010239) — erişim 2026-08-03 — birincil
- **S4 · Phoenix Contact** — [Starting up the charging controller — contactor monitoring](https://www.phoenixcontact.com/charx-help/ctrl/ac/um/Section05/Sec_5_en.htm) — erişim 2026-08-03 — birincil
- **S5 · Phoenix Contact** — [EV-CC-AC1-M3-CBC-RCM-ETH AC charging controller](https://www.phoenixcontact.com/tr-tr/urunler/ac-sarj-kontroloru-ev-cc-ac1-m3-cbc-rcm-eth-1018701) — erişim 2026-08-03 — birincil

## SEO

- Title: `EV Şarj Kontaktör Yapışması Testi ve Güvenli Kabul`
- H1: `EV şarj kontaktör yapışması testi: çıkış gerilimi ve yardımcı kontak nasıl doğrulanır?`
- Description: `Wallbox welded contactor alarmında bobin komutu, yardımcı kontak ve çıkış gerilimini güvenli fonksiyon testiyle eşleştirerek arızayı doğrulayın.`
- Canonical: `/haberler/ev-sarj-kontaktor-yapismasi-gerilim-algilama-kabul`
- Birincil anahtar kelime: `EV şarj kontaktör yapışması testi`

## Doğrudan cevap

EV şarj kontaktör yapışması, bobin komutu kesildiği hâlde güç kontaklarının açmaması ve çıkışın enerjili kalabilmesidir. Kabul yalnız hata koduyla yapılmaz; kontaktör bobin komutu, yardımcı kontak geri bildirimi ve kontaktör sonrası izole gerilim algılama aynı zaman çizelgesinde eşleştirilmelidir. Uyuşmazlıkta yeni şarj oturumu engellenmeli, alarm görünür kalmalı ve güvenli servis reseti gerekmelidir. Enerjili EVSE içinde testler yalnız yetkin ekip ve üretici prosedürüyle yürütülmelidir.

## EV şarj kontaktör yapışması hangi belirtilerle anlaşılır?

AC wallbox içinde güç kontaktörü, Control Pilot izin verdiğinde araca enerji yolunu açar ve şarj durduğunda bütün aktif iletkenleri tasarımına uygun biçimde ayırır. Bobin komutu kaldırıldığı hâlde çıkış tarafında gerilim kalması, yardımcı kontağın kapanmış görünmesi, kontrolörün welded contactor hatası vermesi veya yeni oturumun güvenlik nedeniyle başlamaması kontaktörün açmadığına işaret edebilir.

IEC 61851-1 EVSE'nin çalışma koşulları, araçla bağlantısı ve elektriksel güvenliği için genel çerçeveyi tanımlar. Hata teşhisinde ekrandaki kod tek başına yeterli değildir; kontaktör bobin komutu, ana kontakların gerçek elektriksel durumu, yardımcı kontak ve çıkış gerilim algılama kanalı aynı zaman çizelgesinde karşılaştırılmalıdır. Enerjili wallbox içinde kullanıcı ölçümü yapılmamalıdır.

- Hata kodunu, tarih-saatini ve şarj oturumu durumunu kaydedin.
- Bobin komutu ile yardımcı kontak geri bildirimini ayrı veri noktaları olarak izleyin.
- Şarj durduktan sonra çıkış gerilimi algılama durumunu üretici prosedürüyle doğrulayın.
- Kapağı açma veya kontaktöre vurma gibi kullanıcı müdahaleleri yapmayın.

_Kaynaklar: S1, S2, S3_

## Yardımcı kontak ve gerilim algılama neden birlikte test edilmelidir?

Yardımcı kontak mekanik pozisyon hakkında geri bildirim verir; ancak yanlış kablolama, kaynak olmuş yardımcı kontak veya ana güç kontaklarıyla mekanik uyumsuzluk nedeniyle tek başına yeterli kanıt olmayabilir. Çıkış tarafındaki izole gerilim algılama ise bobin bırakıldıktan sonra hâlâ şebeke gerilimi bulunup bulunmadığını denetleyebilir. İki bağımsız kanıtın uyumu güvenli arıza sınıflandırmasını güçlendirir.

Texas Instruments'ın AC Level 2 EVSE referans tasarımı, röle ve kontaktör sürücüsünün yanında kaynak olmuş röle/kontaktör algılaması için kontak boyunca izole hat gerilimi ölçümü içerir. Phoenix Contact kontrolör dokümanı da açmayan kontaktörün seçilmiş dijital giriş ve yardımcı kontakla izlenebildiğini açıklar. Saha kabulü tam ürünün gerçek sensör ve giriş mimarisine göre yapılmalıdır.

- Yardımcı kontağın NO/NC tipini ve normal durum mantığını belgeleyin.
- Çıkış gerilim algılamasının hangi fazları ve hangi eşikte izlediğini kılavuzdan alın.
- Bobin kapalı, bobin açık ve enerji kesik senaryolarını ayrı test edin.
- Tek bir dijital girişin bütün güç kutuplarını kanıtladığını varsaymayın.

_Kaynaklar: S3, S4, S5_

## Kontaktör açma ve yapışma algılama fonksiyon testi nasıl planlanır?

Fonksiyon testi gerçek kontağı kasıtlı olarak kaynak yapmayı veya güç iletkenlerini köprülemeyi içermez. Yetkin ekip, üreticinin test modu, onaylı simülatör veya güvenli geri bildirim senaryosuyla bobin komutu kaldırıldığında ana kontakların açıldığını; yardımcı kontak ve gerilim sensörünün beklenen sürede güvenli durumu bildirdiğini doğrular. Test koşulu araçsız ve araçlı oturumlar için ayrı tanımlanabilir.

Şarjın normal bitişi, kullanıcı durdurması, RCD/RDC-DD açması, acil durdurma varsa onun kullanılması, enerji kesilip gelmesi ve kontrolör yeniden başlatması gibi olaylarda kontaktör davranışı kaydedilmelidir. Hata algılanınca yeni oturumun engellenmesi, görünür alarm üretilmesi ve uzaktan sistemde doğru hata kodunun saklanması gerekir; otomatik reset yalnız üretici tarafından güvenli tanımlanmışsa kabul edilir.

- Gerçek kısa devre veya zorla yapışma üretmeden test planı hazırlayın.
- Normal duruş, koruma açması ve enerji geri dönüşünü ayrı senaryolarda sınayın.
- Hata sonrası yeniden şarjın kilitlendiğini ve alarmın görünür olduğunu doğrulayın.
- Alarmı silmeden önce fiziksel ve elektriksel geri bildirimi kaydedin.

_Kaynaklar: S1, S3, S4, S5_

## Welded contactor alarmı her zaman kontaktör değişimi gerektirir mi?

Hayır. Gerçek ana kontak yapışmasının yanında yardımcı kontak kablosu kopması, NO/NC mantığının yanlış seçilmesi, çıkış gerilim sensörü arızası, faz-nötr bağlantı hatası, kontrol beslemesi çökmesi, yazılım zaman aşımı veya kontaktörün mekanik olarak geç bırakması aynı alarmı tetikleyebilir. Bu nedenle parça değişimi öncesinde komut–geri bildirim–gerilim üçlüsü kanıtlanmalıdır.

Kontaktör kontak direnci ve terminal sıcaklığı normal şarj sırasında izlenebilir; gevşek bağlantı veya aşırı ısınma kontak ömrünü azaltabilir. Ancak enerjili terminal torku veya canlı direnç ölçümü kullanıcı işlemi değildir. Kök neden kapanışı; ürün kodu, bobin gerilimi, anahtarlanan akım, oturum sayısı, sıcaklık, koruma olayları ve firmware ile birlikte yapılmalıdır.

- Yardımcı kontak kablosu ve giriş mantığını ana kontaktörden ayrı doğrulayın.
- Gerilim sensörü, kontrol beslemesi ve zaman aşımı olaylarını inceleyin.
- Terminal ısınması ve yük akımını güvenli termal kabul planına ekleyin.
- Kanıt olmadan yalnız kontaktörü veya kontrol kartını değiştirmeyin.

_Kaynaklar: S2, S3, S4, S5_

## EVSE kontaktör güvenliği hangi kabul dosyasıyla teslim edilmelidir?

Teslim dosyası; wallbox ve kontrolör tam ürün kodu, firmware, tek hat, kontaktör marka/model ve kutup sayısı, bobin gerilimi, yardımcı kontak tipi, gerilim algılama noktaları, alarm eşiği ve gecikmesi, CP durumu, RCD/RDC-DD olayı, test senaryoları ve geçti-kaldı sonuçlarını içermelidir. Her soket veya şarj çıkışı ayrı satırda izlenmelidir.

Geçti sonucu; enerji verme komutu olmadan çıkışta tehlikeli gerilim kalmaması, kontaktör açma geri bildiriminin doğru sürede gelmesi, uyuşmazlıkta oturumun engellenmesi ve alarm zincirinin yerel/uzak sistemde görünmesiyle verilir. CTA: kişisel verisiz komut–yardımcı kontak–çıkış gerilimi–alarm matrisi hazırlayın; ölçüm gerçek arızayı göstermiyorsa gereksiz kontaktör veya wallbox satın almayın.

- Her çıkış için komut, yardımcı kontak ve gerilim geri bildirimini eşleştirin.
- Test cihazı, zaman kaynağı ve firmware sürümünü rapora ekleyin.
- Arıza sonrası kilit, manuel reset ve servis dönüşünü ayrı kaydedin.
- Kanıt yeterliyse gereksiz komple wallbox değişiminden kaçının.

_Kaynaklar: S1, S2, S3, S4, S5_

## Sık sorulan sorular

### Wallbox welded contactor alarmı verirse şarj etmeye devam edilir mi?

Hayır. Çıkış enerjisinin güvenli biçimde ayrıldığı doğrulanmadan istasyon hizmete alınmamalı; kullanıcı kapağı açmadan yetkili servis ve elektrik ekibine yönelmelidir.

_Kaynaklar: S1, S3, S4_

### Yardımcı kontak kapalı görünüyorsa ana kontak kesin yapışmış mıdır?

Bu bilgi tek başına ana kontağın yapıştığını göstermez. Yardımcı kontak tipi, kablolama ve giriş mantığı yanlış olabilir; ana güç kontaktörünün durumu çıkış gerilimi algılama ve komut kaydıyla birlikte doğrulanmalıdır.

_Kaynaklar: S3, S4_

### Kontaktör yapışma testi için gerçek kontak kısa devre edilir mi?

Hayır. Gerçek yapışma veya köprüleme oluşturulmaz. Üretici test modu, güvenli simülatör ve bağımsız geri bildirim kanallarıyla kontrollü fonksiyon testi yapılır.

_Kaynaklar: S1, S3, S4_

### Kontaktör değişince alarm otomatik olarak kapanmalı mı?

Model davranışına bağlıdır. Değişimden sonra yardımcı kontak, gerilim sensörü, bobin komutu, olay kaydı ve güvenli reset sırası yeniden kabul edilmelidir.

_Kaynaklar: S2, S4, S5_

## İnsan onay komutu

PR sahibinin veya repository yetkilisinin yorumu:

```text
/cms approve ev-sarj-kontaktor-yapismasi-gerilim-algilama-kabul
```

Onay iş akışı kalite puanı, kaynak güncelliği, iç linkler, kanibalizasyon ve risk sınırlarını yeniden çalıştırmadan canonical dosya üretmez.
