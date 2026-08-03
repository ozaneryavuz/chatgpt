# ALO186 AI CMS inceleme paketi — ups-epo-repo-acil-kapatma-devresi-kabul-testi

> Bu dosya canonical yayına dahil edilmez. PR incelemesi ve insan onayı için üretilmiştir.

## Durum

- State: **approved**
- Risk: **high**
- Model: **gpt-5.6-thinking**
- Kalite: **88/100**
- Benzerlik: **0.31** — https://www.alo186.com/haberler/ups-epo-rpo-acil-kapatma-nasil-calisir
- Kelime: **947**

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

- **S1 · IEC** — [IEC 62040-1:2017+A1:2021+A2:2022 — UPS Safety Requirements](https://webstore.iec.ch/en/publication/80573) — erişim 2026-08-03 — birincil
- **S2 · Schneider Electric** — [Easy UPS 3M Operation Manual — EPO](https://productinfo.se.com/easyups3m/5d162cef183e8500013dc210/990-5995A%20Easy%20UPS%203M%20Operation%20Manual/English/990-5995%20Easy%20UPS%203M%20Operation_0000255764.xml/%24/EPOREF_0000274034) — erişim 2026-08-03 — birincil
- **S3 · Schneider Electric** — [Easy UPS 3L Operation Manual — Remote EPO](https://productinfo.se.com/easyups3l/990-6287_master-easy-ups-3l-operation/English/990-6287%20Operation%20Easy%20UPS%203L_0000410385.xml/%24/RemoteEPO_0000422154) — erişim 2026-08-03 — birincil
- **S4 · Eaton** — [UPS RPO and ROO Remote Power Control](https://www.eaton.com/us/en-us/products/backup-power-ups-surge-it-power-distribution/backup-power-ups/ups-rpo-roo-remote-power-control.html) — erişim 2026-08-03 — birincil
- **S5 · Schneider Electric** — [Configure Input Contacts and Output Relays for Easy UPS](https://productinfo.se.com/easyups3m/5d162cef183e8500013dc210/990-5995A%20Easy%20UPS%203M%20Operation%20Manual/English/990-5995%20Easy%20UPS%203M%20Operation_0000255764.xml/%24/ConfigureInputContactsAndOutputRelaysREF_0000273640) — erişim 2026-08-03 — birincil

## SEO

- Title: `UPS EPO ve REPO Acil Kapatma Devresi Kabul Testi`
- H1: `UPS EPO ve REPO acil kapatma devresi nasıl güvenle test edilir?`
- Description: `UPS EPO ve REPO kabul testini şebeke, bypass, akü, yük, alarm, reset ve yeniden başlatma kanıtlarıyla hazırlayın; acil kapatmayı izolasyonla karıştırmayın.`
- Canonical: `/haberler/ups-epo-repo-acil-kapatma-devresi-kabul-testi`
- Birincil anahtar kelime: `UPS EPO REPO kabul testi`

## Doğrudan cevap

UPS EPO veya REPO kabulü, düğmeye basınca ekranda alarm görülmesiyle tamamlanmaz. Önce üreticinin bu giriş için tanımladığı davranış okunmalı; ardından normal çalışma, statik bypass, aküden çalışma ve mümkünse bakım senaryolarında doğrultucu, inverter, şarj cihazı, statik bypass, haricî akü kesicisi ve yükün gerçek durumu ayrı ayrı kaydedilmelidir. EPO bazı modellerde yükü tamamen keserken bazı yapılandırmalarda yükü statik bypass üzerinden beslemeye devam edebilir; ayrıca kontrol devresi veya başka enerji kaynakları gerilimli kalabilir. Bu nedenle EPO, gerilimsiz bırakma veya LOTO yerine kullanılamaz.

## EPO, REPO, RPO ve uzaktan açma işlevleri nasıl ayrılmalıdır?

EPO, REPO ve RPO etiketleri üreticiler arasında aynı elektriksel sonucu garanti etmez. Bazı UPS'lerde acil giriş doğrultucu, inverter, şarj cihazı ve statik bypassı kapatıp yükü hemen enerjisiz bırakır; bazı modellerde ise yapılandırmaya bağlı olarak yük statik bypassa aktarılabilir. Uzaktan normal açma-kapama girişi de acil kapatma devresiyle aynı güvenlik fonksiyonu değildir.

Kabul dosyasının ilk sayfasında cihaz modeli, firmware, giriş terminali, kontak mantığı, normal ve acil durum konumu, kablo gözetimi, fabrika ayarı ve sahadaki seçili davranış tek matriste gösterilmelidir. Projede istenen yangın senaryosu ile üretici işlevi uyuşmuyorsa yalnız etiket adına güvenilmemelidir.

- EPO/REPO/RPO ile normal remote on-off girişini ayrı satırlarda gösterin.
- Kontak açık/kapalı mantığını ve kablo kopmasındaki davranışı kaydedin.
- Fabrika ayarı ile sahada seçilmiş konfigürasyonu karşılaştırın.
- Yangın senaryosunda yükün kesilmesi mi, bypassla sürmesi mi istendiğini yazılılaştırın.

_Kaynaklar: S1, S2, S3, S4_

## Şebeke, bypass, akü ve geri besleme kaynakları hangi sırayla doğrulanmalıdır?

EPO komutu UPS çıkışında enerji görülmemesiyle tek başına kabul edilemez. Şebeke girişi, ayrı bypass girişi, dahili veya haricî akü dizisi, ortak akü barası, paralel UPS modülleri ve haricî statik transfer anahtarı gibi bütün kaynaklar tek hat üzerinde işaretlenmelidir. Üretici dokümanı, ana giriş mevcutken kontrol devresinin EPO sonrasında etkin kalabileceğini açıkça belirtebilir.

Haricî akü kesicisinin şönt açtırma bobini, geri besleme koruması veya bina otomasyonuna giden alarm kontağı projede varsa bunların gerçekten çalıştığı bağımsız kanıtlanmalıdır. EPO devresi açıkken yalnız UPS ekranına bakmak yerine uygun ölçüm noktalarında yetkin personel tarafından gerilim durumu, kesici geri bildirimleri ve olay kayıtları birlikte doğrulanmalıdır.

- Tek hatta bütün AC ve DC enerji kaynaklarını işaretleyin.
- Haricî akü kesicisi trip zincirini fonksiyonel olarak sınayın.
- Paralel modüller ve ortak bypass varsa her modülün durumunu kaydedin.
- EPO sonrasında gerilimli kalabilecek kontrol ve yardımcı devreleri açıkça etiketleyin.

_Kaynaklar: S1, S2, S3, S5_

## Acil kapatma senaryoları yük ve işletme modu bazında nasıl test edilir?

Test planı en az normal çevrim içi çalışma, aküden çalışma ve statik bypass senaryolarını içermelidir. Bakım bypassı gerçek EPO zincirinin dışında kalıyorsa bu durum ayrıca görünür hale getirilmelidir. Kritik yüklerin plansız kesilmesini önlemek için test zamanı, yük temsilcisi, geri dönüş yöntemi ve başarısızlıkta güvenli duruş önceden onaylanmalıdır.

Her senaryoda komut zamanı, doğrultucu-inverter-şarj cihazı durumu, statik bypass konumu, çıkış gerilimi, akü kesicisi, haricî kesiciler, alarm ve bina otomasyonu geri bildirimi aynı zaman çizelgesine yazılmalıdır. İşlevin yalnız boşta değil, proje tarafından belirlenen güvenli temsilî yük altında da doğrulanması gerekir.

- Normal, akü ve statik bypass modlarını ayrı test satırları yapın.
- Bakım bypassının EPO dışında kalıp kalmadığını kanıtlayın.
- Komut ile gerçek güç kesilmesi arasındaki süreyi kaydedin.
- Yangın alarmı/BMS sinyali ile UPS olay günlüğünün zaman damgalarını eşleştirin.

_Kaynaklar: S2, S3, S4, S5_

## Reset, kilitleme ve yeniden başlatma güvenliği nasıl kabul edilir?

Acil giriş serbest bırakıldığında UPS'nin kendiliğinden yükü yeniden beslemesi kabul edilmemelidir; beklenen davranış üretici dokümanı, risk değerlendirmesi ve tesis işletme prosedürüyle belirlenmelidir. Fiziksel EPO butonunun kilitli kalması, manuel reset, yetkili yeniden başlatma ve varsa uzaktan komut önceliği ayrı test edilmelidir.

Kablo kısa devresi, kablo kopması, kontak yapışması, yardımcı besleme kaybı ve haberleşme kesintisi gibi arızalar için sistemin güvenli duruşu doğrulanmalıdır. Test sonrası bütün alarmlar temizlenmeli, giriş kontakları normal duruma dönmeli ve kritik yükler kontrollü sıra ile devreye alınmalıdır.

- EPO resetinden sonra otomatik restart olup olmadığını sınayın.
- Fiziksel buton kilidi ve yetkili manuel reset gereğini doğrulayın.
- Kablo kopması ve kontak arızası senaryosunu tasarım kapsamına göre test edin.
- Yeniden başlatmada yük sırası, bypass senkronu ve alarm temizliğini kaydedin.

_Kaynaklar: S1, S3, S4_

## UPS EPO/REPO kabul dosyasında hangi kanıtlar bulunmalıdır?

Teslim dosyası; onaylı tek hat, EPO bağlantı şeması, terminal ve kontak bilgileri, cihaz modeli-firmware-konfigürasyon yedeği, buton yerleşimi, etiketler, test senaryoları, olay günlüğü, kesici geri bildirimleri, ölçüm sonuçları, BMS/yangın paneli eşleşmesi ve imzalı geçti-kaldı tablosunu içermelidir. Her sapma için sorumlu, düzeltme kanıtı ve yeniden test tarihi tanımlanmalıdır.

EPO testi başarılı olsa bile bakım için gerilimsiz çalışma kanıtı ayrıca LOTO ve uygun ölçümle sağlanır. Mevcut EPO zinciri bütün kaynakları ve reset davranışını kanıtla karşılıyorsa sırf daha yeni bir UPS veya uzaktan kapatma modülü satın almak gerekmez.

- EPO işlevini izolasyon ve LOTO prosedüründen ayrı dokümante edin.
- Her güç kaynağı için beklenen ve ölçülen sonucu tek tabloda verin.
- Fotoğraf, olay günlüğü ve test formuna sürüm/tarih bilgisi ekleyin.
- Kanıt yeterliyse gereksiz UPS, buton veya haberleşme modülü değişimi yapmayın.

_Kaynaklar: S1, S2, S3, S4, S5_

## Sık sorulan sorular

### UPS EPO düğmesine basınca bütün gerilimler kesilir mi?

Her zaman değil. Bazı yapılandırmalarda yük statik bypass üzerinden beslenmeye devam edebilir; şebeke mevcutsa kontrol devresi veya haricî akü gibi başka kaynaklar gerilimli kalabilir. Sonuç yalnız model dokümanı ve saha testiyle doğrulanmalıdır.

_Kaynaklar: S2, S3, S5_

### EPO ile bakım için güvenli izolasyon yapılabilir mi?

Hayır. EPO bir acil kontrol fonksiyonudur; bütün enerji kaynaklarının fiziksel olarak ayrıldığını ve gerilimsizliği tek başına kanıtlamaz. Bakım için onaylı LOTO, kesici ayırma ve yetkin personel ölçümü gerekir.

_Kaynaklar: S1, S2_

### REPO ile remote on-off aynı giriş midir?

Genellikle aynı amaç değildir. REPO/RPO acil kapatmaya yöneliktir; remote on-off işletme amaçlı uzaktan açma-kapama fonksiyonudur. Terminal mantığı ve sonuç model dokümanından doğrulanmalıdır.

_Kaynaklar: S4_

### EPO resetlenince UPS otomatik olarak yeniden başlamalı mı?

Evrensel bir cevap yoktur. Tesis risk değerlendirmesi ve üretici davranışı birlikte ele alınmalıdır; kritik yüklerde yetkisiz veya kontrolsüz otomatik yeniden enerjilenme kabul edilmemeli, manuel reset ve yük sırası test edilmelidir.

_Kaynaklar: S1, S3, S4_

## İnsan onay komutu

PR sahibinin veya repository yetkilisinin yorumu:

```text
/cms approve ups-epo-repo-acil-kapatma-devresi-kabul-testi
```

Onay iş akışı kalite puanı, kaynak güncelliği, iç linkler, kanibalizasyon ve risk sınırlarını yeniden çalıştırmadan canonical dosya üretmez.
