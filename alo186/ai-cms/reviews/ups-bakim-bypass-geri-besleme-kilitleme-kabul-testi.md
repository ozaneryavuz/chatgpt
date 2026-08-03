# ALO186 AI CMS inceleme paketi — ups-bakim-bypass-geri-besleme-kilitleme-kabul-testi

> Bu dosya canonical yayına dahil edilmez. PR incelemesi ve insan onayı için üretilmiştir.

## Durum

- State: **approved**
- Risk: **high**
- Model: **gpt-5.6-thinking**
- Kalite: **88/100**
- Benzerlik: **0.31** — https://www.alo186.com/haberler/ups-statik-bypass-bakim-bypass-farki-gecis-proseduru
- Kelime: **905**

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

- **S1 · IEC** — [IEC 62040-1:2017+AMD1:2021+AMD2:2022 — UPS Safety Requirements](https://webstore.iec.ch/en/publication/80573) — erişim 2026-08-03 — birincil
- **S2 · Schneider Electric** — [Galaxy VL — Backfeed Protection](https://www.productinfo.schneider-electric.com/galaxyvl_ul/990-93888-ess-energy-storage-system-for-ul9540-galaxy-vl-ups-and-galaxy-lithium-ion-battery-cabinets-installation/English/990-93888%20Installation%20ESS%20for%20Galaxy%20VL%20with%20Lithium-ion_DD00802806.xml/%24/BackfeedProtection_GVL_0000506413) — erişim 2026-08-03 — birincil
- **S3 · Schneider Electric** — [Easy UPS 3S Pro — Transfer from Maintenance Bypass to Normal Operation](https://www.productinfo.schneider-electric.com/easyups3s_pro_iec/990-66230-easy-ups-3s-pro-for-external-batteries-operation/English/990-66230%20Operation%20Easy%20UPS%203S%20Pro%2010_15_20_30_40%20kVA%2C%20380_400_415%20V_DD00871242.xml/%24/TransferaParallelSystemfromMaintenanceBypassOperationtoNormal_DD01113540) — erişim 2026-08-03 — birincil
- **S4 · Schneider Electric** — [Galaxy VL Maintenance Bypass Cabinet — Decommission or Move](https://www.productinfo.schneider-electric.com/galaxyvl_iec/990-91381_master-galaxy-vl-maintenance-bypass-cabinet-for-iec-installation/Turkish/990-91381%20Maintenance%20Bypass%20Cabinet%20for%20IEC_tr_0000536583.xml/%24/DecommissionorMovetheMaintenanceBypassCabinettoaNewLocation_GVLMBCA250K500H_tr_DD00787621) — erişim 2026-08-03 — birincil

## SEO

- Title: `UPS Bakım Bypass Testi: Geri Besleme ve Kilitleme Kabulü`
- H1: `UPS bakım bypassı geri besleme ve kilitleme testleriyle nasıl güvenli kabul edilir?`
- Description: `UPS bakım bypassını şalter sırası, geri besleme koruması, mekanik-elektrik kilitleme ve gerilimsizlik kanıtıyla güvenli biçimde kabul edin.`
- Canonical: `/haberler/ups-bakim-bypass-geri-besleme-kilitleme-kabul-testi`
- Birincil anahtar kelime: `UPS bakım bypass geri besleme kilitleme testi`

## Doğrudan cevap

UPS bakım bypassı, yalnız MBB şalteri kapatıldığında yükün enerjili kalmasıyla kabul edilmiş sayılmaz. Güvenli kabul; üreticiye özgü şalter sırasının uygulanması, inverter ile bypassın senkron olduğunun doğrulanması, yanlış eşzamanlı şalter konumlarının mekanik veya anahtarlı kilitlemeyle engellenmesi, bypass girişinde geri besleme korumasının fonksiyon testi ve UPS üzerinde çalışılacak terminallerde gerilimsizliğin ölçülmesiyle yapılır. Her geçişte yük gerilimi, frekansı, olay kaydı, şalter geri bildirimleri ve alarm durumu aynı zaman çizelgesinde kaydedilmelidir.

## Statik bypass, bakım bypassı ve sistem izolasyonu neden ayrı değerlendirilmelidir?

Statik bypass, yükü inverter yerine bypass kaynağına yarı iletken anahtar üzerinden aktarır; bakım bypassı ise yükü UPS güç katından fiziksel olarak ayırabilmek için haricî veya dahili mekanik bir yol oluşturur. Bu iki işlev aynı değildir. Statik bypassa geçiş bakım personelinin UPS giriş, çıkış veya DC terminallerinde güvenle çalışabileceği anlamına gelmez.

Tekli ve paralel UPS mimarilerinde UIB, SSIB, UOB, MBB, SIB, BIB ve akü kesicilerinin bulunması modele göre değişir. Bu nedenle internetteki genel bir şalter sırası kopyalanmamalı; tek hat şeması, saha etiketleri ve üretici işletme kılavuzu aynı isimlendirme üzerinden eşleştirilmelidir.

- UPS’nin tekli veya paralel, tek girişli veya çift girişli mimarisini kaydedin.
- Statik bypass ile bakım bypassını ayrı fonksiyonlar olarak işaretleyin.
- Her şalterin saha etiketi ile tek hat şemasındaki karşılığını doğrulayın.
- Modelde bulunmayan şalter adımlarını genel prosedürden taşımayın.

_Kaynaklar: S1, S3_

## Normal işletmeden bakım bypassına kesintisiz transferin ön koşulları nelerdir?

Transfer öncesinde bypass kaynağının gerilim ve frekans aralığı, faz sırası ve inverterle senkron durumu doğrulanmalıdır. Yük statik bypassa alınmadan bakım bypass şalterinin kapatılması bazı mimarilerde paralel kaynak veya yanlış akım yolu oluşturabilir. Üretici prosedürü bu nedenle ekran durumu, mimic diyagramı ve kesici sırasını birlikte tanımlar.

Kabul testi yalnız boşta yapılmamalıdır. Kritik olmayan, temsilî bir yükle çıkış gerilimi ve frekansı trendlenmeli; transfer sırasında kesinti, gerilim çukuru, yük düşmesi, aşırı akım veya beklenmeyen alarm oluşup oluşmadığı kaydedilmelidir. Hassas yüklerin toleransı ayrıca doğrulanmalıdır.

- Bypass kaynağının faz sırası, gerilim ve frekansını doğrulayın.
- İnverter-bypass senkron durumunu ekran ve olay kaydından kaydedin.
- Temsilî yükte transfer öncesi, anı ve sonrası gerilim trendi alın.
- Beklenmeyen kaynak paralellemesini engelleyen koşulları test edin.

_Kaynaklar: S1, S3_

## Geri besleme koruması nasıl fonksiyonel olarak doğrulanır?

UPS’nin bypass veya giriş tarafına enerji geri verebilmesi, açık olduğu varsayılan bir upstream devrede ölümcül gerilim oluşturabilir. Üretici dokümanları bypass için geri besleme korumasını; UPS’ye bağlı şönt açtırmalı üst kesici, dahili geri besleme kiti veya koruma elemanı içeren bakım bypass kabini gibi model onaylı yöntemlerle kurmayı zorunlu tutabilir.

Kabul dosyası yalnız ekipman etiketini fotoğraflamakla yetinmemelidir. Koruma komutunun doğru kesiciyi açtırdığı, yardımcı kontak ve UPS alarmının doğru duruma geçtiği, kablo ve terminal tanımlarının tek hatla eşleştiği ve koruma devresi arızasında güvenli durumun oluştuğu yetkin ekipçe senaryolu test edilmelidir.

- Geri besleme korumasının hangi cihazla sağlandığını tek hatta işaretleyin.
- Şönt açtırma veya dahili kitin fonksiyon testini kaydedin.
- Kesici yardımcı kontağı, alarm ve olay zaman damgasını karşılaştırın.
- Koruma devresi veya haberleşme kaybındaki güvenli durumu doğrulayın.

_Kaynaklar: S1, S2_

## Mekanik, anahtarlı ve elektriksel kilitlemeler hangi hataları engellemelidir?

Kilitlemenin amacı, yalnız operatöre doğru sırayı hatırlatmak değil; tehlikeli şalter kombinasyonunu fiziksel veya mantıksal olarak mümkün olmaktan çıkarmaktır. Anahtarlı kilit, kapı kilidi, şalter mekanik kilidi ve kuru kontaklı elektriksel izin zinciri; tasarıma göre MBB ile çıkış veya sistem izolasyon şalterlerinin yanlış eşzamanlı durumunu engellemelidir.

Bakım izolasyonu tamamlandığında LOTO uygulanmalı ve UPS, bypass, çıkış, nötr ve DC terminallerinde gerilim yokluğu doğrudan uygun ölçüm cihazıyla doğrulanmalıdır. Ekranın kapanması veya tek bir şalterin açık görünmesi gerilimsizlik kanıtı değildir; kapasitör boşalma süresi ve alternatif besleme yolları hesaba katılmalıdır.

- Tehlikeli her şalter kombinasyonu için kilitleme matrisi oluşturun.
- Anahtarın yalnız güvenli durumda serbest kaldığını sahada deneyin.
- LOTO noktalarını AC giriş, bypass, çıkış ve DC kaynakları için ayrı tanımlayın.
- Çalışma başlamadan tüm ilgili terminallerde gerilimsizliği ölçün.

_Kaynaklar: S3, S4_

## UPS bakım bypassı hangi kanıt dosyasıyla teslim alınmalıdır?

Teslim dosyasında onaylı tek hat, şalter ve kablo etiketleri, şalter konum tablosu, üretici prosedürü, geri besleme koruma yöntemi, kilitleme matrisi, transfer trendleri, olay kayıtları, alarm listesi, gerilimsizlik ölçümü ve fotoğraflı son durum bulunmalıdır. Paralel sistemde her UPS kolu ve ortak bypass yolu ayrı izlenmelidir.

Sonuç geçti, şartlı geçti veya kaldı olarak sınıflandırılmalıdır. Yükte kesinti, beklenmeyen alarm, yanlış şalter geri bildirimi, geri besleme korumasının çalışmaması veya kilit bypassı varsa sistem kabul edilmemelidir. Mevcut bypass sistemi bütün senaryoları kanıtla geçiyorsa sırf yeni model olduğu için pano veya UPS değiştirmek gereksizdir.

- Her test adımını saat damgalı şalter durumu ve ölçümle eşleştirin.
- Tekli ve paralel çalışma senaryolarını ayrı raporlayın.
- Eksik kilitleme veya geri besleme korumasını kapanış maddesi yapın.
- Kanıt yeterliyse gereksiz pano veya UPS satın almayın.

_Kaynaklar: S1, S2, S3, S4_

## Sık sorulan sorular

### UPS statik bypassa geçtiğinde bakım yapmak güvenli midir?

Hayır. Statik bypass yükü inverterden bypass kaynağına aktarır ancak UPS’nin bütün giriş, çıkış ve DC bölümlerini fiziksel olarak izole etmez. Bakım için üretici prosedürüne göre mekanik bypass, izolasyon, LOTO ve gerilimsizlik doğrulaması gerekir.

_Kaynaklar: S1, S3_

### Bakım bypass şalterini doğrudan kapatmak neden tehlikeli olabilir?

İnverter ve bypass senkron değilse veya şalter sırası yanlışsa paralel kaynak, yüksek dolaşım akımı, yük kesintisi ya da ekipman hasarı oluşabilir. Doğru sıra modelin tek hat ve işletme kılavuzundan alınmalıdır.

_Kaynaklar: S3_

### UPS geri besleme koruması yalnız bir uyarı etiketiyle sağlanabilir mi?

Hayır. Etiket tehlikeyi bildirir; koruma için üreticinin kabul ettiği üst kesici-şönt açtırma, dahili backfeed kiti veya koruma cihazı içeren bakım bypass kabini gibi işlevsel bir ayırma yöntemi gerekir.

_Kaynaklar: S2_

### Ekran kapalıysa UPS terminalleri gerilimsiz kabul edilebilir mi?

Hayır. Alternatif bypass yolu, geri besleme, akü/DC kaynakları ve kapasitörlerde kalan enerji bulunabilir. LOTO sonrasında uygun ölçüm cihazıyla ilgili bütün terminallerde gerilim yokluğu doğrulanmalıdır.

_Kaynaklar: S4_

## İnsan onay komutu

PR sahibinin veya repository yetkilisinin yorumu:

```text
/cms approve ups-bakim-bypass-geri-besleme-kilitleme-kabul-testi
```

Onay iş akışı kalite puanı, kaynak güncelliği, iç linkler, kanibalizasyon ve risk sınırlarını yeniden çalıştırmadan canonical dosya üretmez.
