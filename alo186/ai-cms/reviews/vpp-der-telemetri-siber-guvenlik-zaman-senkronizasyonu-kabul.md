# ALO186 AI CMS inceleme paketi — vpp-der-telemetri-siber-guvenlik-zaman-senkronizasyonu-kabul

> Bu dosya canonical yayına dahil edilmez. PR incelemesi ve insan onayı için üretilmiştir.

## Durum

- State: **approved**
- Risk: **legal**
- Model: **gpt-5.6-thinking**
- Kalite: **88/100**
- Benzerlik: **0.12** — https://alo186.com/haberler/vpp-telemetri-stale-data-zaman-damgasi-sayac-mutabakat-teshis
- Kelime: **943**

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

- **S1 · IEC** — [IEC 62351-3:2023 — TCP/IP Security Profiles Including TLS](https://webstore.iec.ch/en/publication/68410) — erişim 2026-08-03 — birincil
- **S2 · IEC** — [IEC 62351-8:2020 — Role-Based Access Control for Power System Management](https://webstore.iec.ch/en/publication/61822) — erişim 2026-08-03 — birincil
- **S3 · IEC / IEEE** — [IEC/IEEE 61850-9-3:2016 — Precision Time Protocol Profile](https://webstore.iec.ch/en/publication/24998) — erişim 2026-08-03 — birincil
- **S4 · IEC** — [IEC 62351-7:2025 — Network and System Management Data Object Models](https://webstore.iec.ch/en/publication/76108) — erişim 2026-08-03 — birincil
- **S5 · NIST** — [NIST SP 800-82 Rev. 3 — Guide to Operational Technology Security](https://csrc.nist.gov/pubs/sp/800/82/r3/final) — erişim 2026-08-03 — birincil

## SEO

- Title: `VPP Telemetri Siber Güvenliği: TLS, RBAC ve Zaman Senkronu`
- H1: `VPP ve DER telemetrisi TLS, rol tabanlı erişim ve zaman senkronuyla nasıl kabul edilir?`
- Description: `VPP ve DER telemetrisini TLS, sertifika yönetimi, RBAC, olay izleme, PTP/NTP zaman senkronu ve güvenli arıza senaryolarıyla kabul edin.`
- Canonical: `/haberler/vpp-der-telemetri-siber-guvenlik-zaman-senkronizasyonu-kabul`
- Birincil anahtar kelime: `VPP DER telemetri siber güvenlik zaman senkronizasyonu`

## Doğrudan cevap

VPP veya DER telemetrisi, merkez ekranında değer görünmesiyle güvenli kabul edilmiş olmaz. Kabul dosyası; cihazdan toplayıcıya kadar veri akışını, TLS 1.2/1.3 profilini ve sertifika doğrulamasını, rol tabanlı en az ayrıcalıklı erişimi, ortak zaman kaynağını ve saat sapması alarmlarını, güvenlik olaylarını, yedekleme-geri yükleme sürecini ve iletişim kaybında yerel güvenli kontrolü kanıtlamalıdır. Komut, ölçüm ve olay kayıtları aynı güvenilir zaman tabanında eşleştirilmeli; başarısız kimlik doğrulama, süresi dolmuş sertifika, yetkisiz rol, zaman kaybı ve bağlantı kesintisi senaryoları canlı işletmeden önce test edilmelidir.

## VPP siber güvenlik kabulü hangi varlık ve veri akışı envanteriyle başlamalıdır?

İlk adım; sayaç, inverter, BMS, EVSE, RTU, gateway, VPN, bulut servisleri, toplayıcı platformu ve piyasa/şebeke arayüzlerini tek veri akışı üzerinde göstermektir. Her bağlantıda protokol, yön, port, veri sınıfı, komut yetkisi, güven sınırı, sahiplik ve hizmet sağlayıcı sorumluluğu kaydedilmelidir.

Yalnız IP listesi yeterli değildir. Hangi veri noktasının ölçüm, alarm, ayar veya kontrol komutu olduğu; komutun fiziksel tesiste ne değiştirdiği ve iletişim kesildiğinde yerel kontrolün hangi güvenli değeri koruyacağı açıkça tanımlanmalıdır. NIST OT yaklaşımı güvenlik önlemlerinin performans, güvenilirlik ve emniyet gereksinimleriyle birlikte ele alınmasını ister.

- Cihazdan toplayıcıya bütün ağ ve güven sınırlarını çizin.
- Her veri noktasını ölçüm, olay, ayar veya kontrol olarak sınıflandırın.
- Üçüncü taraf bulut ve uzaktan bakım bağlantılarını ayrı gösterin.
- İletişim kaybında yerel emniyet ve işletme önceliğini tanımlayın.

_Kaynaklar: S4, S5_

## TLS ve sertifika yaşam döngüsü nasıl doğrulanmalıdır?

IEC 62351-3, TCP/IP kullanan güç sistemi protokollerinde gizlilik, bütünlük ve mesaj düzeyi kimlik doğrulaması için TLS 1.2 ve TLS 1.3 profilleri tanımlar. Kabulde yalnız trafik şifreli mi sorusu değil; sunucu ve gerekiyorsa istemci kimliği, sertifika zinciri, güven kökü, izin verilen protokol/suite, oturum davranışı ve güvenlik olayı kaydı doğrulanmalıdır.

Sertifika süresi dolması, iptal listesi veya OCSP erişilememesi, yanlış cihaz kimliği ve güven kökü değişimi senaryoları planlı test edilmelidir. Anahtar ve sertifika yenilemesi üretim kesintisine yol açmadan yapılabilmeli; özel anahtarlar log, yedek veya destek dosyalarına düz metin olarak girmemelidir.

- TLS sürümü ve kimlik doğrulama yönünü arayüz bazında kaydedin.
- Sertifika zinciri, ad eşleşmesi ve iptal kontrolünü test edin.
- Süre dolumu yaklaşırken alarm ve kontrollü yenileme senaryosu uygulayın.
- Özel anahtarın dışa aktarım ve yedekleme politikasını doğrulayın.

_Kaynaklar: S1_

## Rol tabanlı erişim hangi yetki matrisiyle kabul edilmelidir?

IEC 62351-8, insan kullanıcılar, otomatik sistemler ve yazılım uygulamaları için rol tabanlı erişimi ve en az ayrıcalık ilkesini ele alır. VPP’de izleme, dispatch onayı, setpoint gönderme, firmware, sertifika, kullanıcı yönetimi ve acil durum işlemleri aynı süper kullanıcı hesabında toplanmamalıdır.

Kabul testi her rol için izin verilen ve reddedilen işlemleri içermelidir. Ortak hesap, varsayılan parola, süresiz servis hesabı ve ayrılan personelin açık yetkisi kapanış maddesi olmalıdır. Kritik komutlarda iki kişi onayı, süreli yetki veya ayrı kontrol kanalı risk değerlendirmesine göre uygulanabilir.

- İzleme, işletme, mühendislik, siber güvenlik ve yönetici rollerini ayırın.
- Her rol için okuma, yazma, kontrol ve yönetim izinlerini test edin.
- Ortak ve varsayılan hesapları kapatın veya belgeli istisnaya bağlayın.
- Yetki verme, gözden geçirme ve geri alma kayıtlarını saklayın.

_Kaynaklar: S2, S5_

## Zaman senkronizasyonu neden dispatch ve olay kanıtının parçasıdır?

VPP’de setpoint, ölçüm, sayaç, piyasa olayı ve cihaz alarmı farklı saatlerdeyse gerçek tepki süresi ve baseline sapması yanlış yorumlanabilir. IEC/IEEE 61850-9-3, güç otomasyonu için PTP profilini ve yüksek senkronizasyon sınıflarını tanımlar. Her tesis aynı hassasiyeti gerektirmese de ihtiyaç duyulan zaman doğruluğu işlev ve sözleşmeye göre belirlenmelidir.

Birincil zaman kaynağı, yedek kaynak, holdover davranışı, saat sapması alarmı, zaman dilimi ve yaz/kış saati işleme kuralları test edilmelidir. Zaman kaynağı kaybolduğunda eski veya gelecekteki zaman damgasıyla komut kabul edilmemeli; olay kayıtları monoton ve değiştirilemez bir sıra sunmalıdır.

- Her arayüz için gerekli zaman doğruluğu ve toleransı tanımlayın.
- PTP/NTP kaynağı, yedek ve holdover davranışını test edin.
- Saat sıçraması ve zaman kaybında alarm/komut politikasını doğrulayın.
- Dispatch, ölçüm ve olay kaydını ortak zaman çizelgesinde karşılaştırın.

_Kaynaklar: S3, S4_

## Güvenlik izleme ve güvenli arıza senaryosu nasıl teslim alınmalıdır?

IEC 62351-7; IED, RTU ve DER sistemlerinin sağlık, performans ve olası güvenlik ihlallerini izlemek için NSM veri nesneleri tanımlar. Kabul dosyasında başarısız giriş, sertifika hatası, bağlantı kesintisi, beklenmeyen konfigürasyon değişikliği, zaman senkron kaybı, servis yeniden başlatma ve komut reddi gibi olayların merkezi izleme sistemine doğru önem ve zamanla ulaştığı gösterilmelidir.

İletişim veya merkez platformu kaybolduğunda tesis güvenli yerel moda geçmeli; son komutu sınırsız süre körü körüne sürdürmemelidir. Yedekleme ve geri yükleme testi, temiz konfigürasyon, sertifika ve rol bilgilerini geri getirmeli; canlı dispatch öncesi izole ortamda test edilmelidir. Mevcut sistem bütün kapıları kanıtla geçiyorsa yalnız moda olduğu için yeni siber güvenlik ürünü alınmamalıdır.

- NSM ve güvenlik olaylarını merkezi alarm listesine eşleyin.
- Bağlantı, kimlik, zaman ve konfigürasyon arızalarını senaryolu test edin.
- Yerel fail-safe/fail-operational davranışı süre ve sınırlarıyla doğrulayın.
- Yedekleme-geri yükleme ve rollback testini canlıdan önce tamamlayın.

_Kaynaklar: S4, S5_

## Sık sorulan sorular

### VPP bağlantısında VPN varsa TLS yine gerekli midir?

VPN ağ katmanında koruma sağlar ancak uygulama uçlarının kimliği, sertifika yaşam döngüsü, mesaj bütünlüğü ve güvenlik olayları ayrıca yönetilmelidir. Gereksinim, protokol ve güven sınırına göre katmanlı biçimde belirlenir.

_Kaynaklar: S1, S5_

### VPP’de tek yönetici hesabı kullanmak neden risklidir?

Ortak süper kullanıcı hesabı yetkinin kime ait olduğunu ve hangi işlemin kim tarafından yapıldığını belirsizleştirir. RBAC, kullanıcı ve otomatik ajanları yalnız görevleri için gerekli izinlerle sınırlar.

_Kaynaklar: S2_

### Saat birkaç saniye saparsa ne olur?

İzin verilen sapma kullanım amacına bağlıdır. Dispatch tepki süresi, sayaç mutabakatı, olay sırası ve arıza kök neden analizi etkilenebilir. Bu nedenle tolerans, zaman kaynağı ve kayıp alarmı sözleşmede açık olmalıdır.

_Kaynaklar: S3_

### İletişim kesilince DER son setpointte kalmalı mı?

Her tesis için tek cevap yoktur. Güvenli yerel davranış; ekipman sınırları, şebeke gereksinimleri, sözleşme ve emniyet analizine göre zaman sınırlı hold, yerel kontrol veya güvenli setpoint olabilir ve kabul testinde doğrulanmalıdır.

_Kaynaklar: S4, S5_

## İnsan onay komutu

PR sahibinin veya repository yetkilisinin yorumu:

```text
/cms approve vpp-der-telemetri-siber-guvenlik-zaman-senkronizasyonu-kabul
```

Onay iş akışı kalite puanı, kaynak güncelliği, iç linkler, kanibalizasyon ve risk sınırlarını yeniden çalıştırmadan canonical dosya üretmez.
