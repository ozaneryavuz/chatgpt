# ALO186 AI CMS inceleme paketi — ev-sarj-istasyonu-internet-kesintisi-ocpp-offline-islem-kabul

> Bu dosya canonical yayına dahil edilmez. PR incelemesi ve insan onayı için üretilmiştir.

## Durum

- State: **approved**
- Risk: **high**
- Model: **gpt-5.6-thinking**
- Kalite: **88/100**
- Benzerlik: **0.40** — https://alo186.com/haberler/ev-sarj-ocpp-internet-kesilirse-offline-calismasi
- Kelime: **869**

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

- **S1 · Open Charge Alliance** — [Download OCPP — OCPP 2.1, 2.0.1 ve 1.6 resmî paketleri](https://openchargealliance.org/my-oca/ocpp/) — erişim 2026-08-03 — birincil
- **S2 · Open Charge Alliance** — [OCPP 2.0.1 Certification](https://openchargealliance.org/certificationocpp/certification-ocpp-2-0-1/) — erişim 2026-08-03 — birincil
- **S3 · Open Charge Alliance** — [Open Charge Point Protocol](https://openchargealliance.org/protocols/open-charge-point-protocol/) — erişim 2026-08-03 — birincil
- **S4 · Open Charge Alliance** — [What is new in OCPP 2.0.1?](https://openchargealliance.org/ocpp-info-whitepapers/what-is-new-in-ocpp-2-0-1/) — erişim 2026-08-03 — birincil

## SEO

- Title: `EV Şarj İstasyonu İnternet Kesintisi: OCPP Offline İşlem Kabulü`
- H1: `İnternet kesilince EV şarj istasyonu çalışır mı, OCPP offline işlemler nasıl test edilir?`
- Description: `OCPP şarj istasyonunda internet kesintisi, yerel yetkilendirme, saat kayması, işlem kaydı ve bağlantı dönüşü mutabakatını test edin.`
- Canonical: `/haberler/ev-sarj-istasyonu-internet-kesintisi-ocpp-offline-islem-kabul`
- Birincil anahtar kelime: `EV şarj istasyonu internet kesintisi OCPP`

## Doğrudan cevap

İnternet kesildiğinde bir EV şarj istasyonunun çalışıp çalışmayacağı yalnız OCPP sürümüne bağlı değildir; cihazın yerel yetkilendirme, çevrimdışı işlem saklama, sayaç örnekleme, saat senkronizasyonu ve yeniden bağlantıda kayıt gönderme ayarlarına bağlıdır. Kabul testi; bağlantı kopmadan önce aktif işlem, yeni çevrimdışı başlatma, yetkisiz kart, cihaz yeniden başlatma, uzun kesinti, saat sapması ve bağlantı geri geldiğinde işlem mutabakatı senaryolarını ayrı ayrı kapsamalıdır. Şarj enerjisi, işlem kimliği, başlangıç-bitiş zamanları ve ücretlendirme verisi kayboluyor veya yineleniyorsa sistem canlı işletmeye kabul edilmemelidir.

## İnternet kesintisinde hangi işlevlerin devam edeceği nasıl belirlenir?

OCPP, şarj istasyonu ile merkezi yönetim sistemi arasındaki iletişimi standardize eder; ancak çevrimdışı yetkilendirme ve işlem davranışı cihazın desteklediği özellikler, yerel liste veya önbellek, operatör politikası ve yazılım ayarlarıyla belirlenir. Bu nedenle 'OCPP uyumlu' etiketi tek başına internet yokken her kartın kabul edileceği veya her işlemin doğru fiyatlandırılacağı anlamına gelmez.

OCA'nın OCPP 2.0.1 sertifikasyonunda temel profil; açılış, yetkilendirme, yapılandırma, işlemler ve uzaktan kontrol gibi çekirdek işlevleri kapsar; yerel liste yönetimi ise ayrı bir seçenek olabilir. Kabul planı, istasyonun sertifika kapsamı ile sahada etkinleştirilen özellikleri aynı tabloda karşılaştırmalıdır.

- OCPP sürümü, sertifika profili ve firmware sürümünü kaydedin.
- Yerel yetkilendirme önbelleği veya yerel listenin etkin olup olmadığını doğrulayın.
- Çevrimdışı dönemde hangi kullanıcıların kabul veya reddedileceğini yazılı politika haline getirin.
- 'İnternet yoksa herkes şarj eder' gibi varsayımları test etmeden kabul etmeyin.

_Kaynaklar: S1, S2, S3_

## Çevrimdışı işlem ve sayaç verisi nasıl kanıtlanmalıdır?

Bağlantı kesilmeden önce başlayan işlem, bağlantı kesildikten sonra başlayan işlem ve kesinti sırasında biten işlem ayrı senaryolardır. Her senaryoda istasyonun yerel işlem kimliği, enerji başlangıç ve bitiş değerleri, periyodik sayaç örnekleri, konektör durumu ve durdurma nedeni kaydedilmelidir.

OCPP 2.0.1 işlem modeli, işlem başlangıç ve bitiş koşullarını daha esnek hale getirir. OCPP 1.6 ile 2.0.1 geriye dönük uyumlu olmadığından, merkezi sistemin beklediği mesaj sırası ve mutabakat mantığı sürüme göre test edilmelidir. Kayıp veya çift gönderim, fatura ve kullanıcı itirazı riski doğurur.

- Bağlantı öncesi, kesinti sırası ve bağlantı sonrası sayaç değerlerini karşılaştırın.
- Aynı işlemin iki kez oluşmadığını işlem kimliği ve enerji toplamıyla doğrulayın.
- Uzun kesintide yerel belleğin dolma davranışını test edin.
- Elektrik sayacı ile OCPP enerji toplamı arasındaki farkı kabul kriterine bağlayın.

_Kaynaklar: S1, S3, S4_

## Saat senkronizasyonu ve zaman damgası hatası nasıl test edilir?

İnternet kesintisi sırasında istasyonun gerçek zaman saati sapabilir; yeniden bağlantıda geçmiş olaylar yanlış sırada veya gelecekte görünür. Bu durum tarife dilimi, rezervasyon, işlem süresi, SLA ve kullanıcı itirazlarında kritik hale gelir. Kabul testinde istasyon saatinin kesinti öncesi, uzun kesinti sonrası ve yeniden senkronizasyon sonrasındaki farkı kaydedilmelidir.

Merkezi sistem, gecikmeli gelen olayları yalnız alındığı saate göre değil olay zamanına ve işlem bağlamına göre işlemelidir. Saat aniden geri veya ileri alındığında aynı işlemde negatif süre, çakışan oturum veya yanlış fiyatlandırma oluşmaması doğrulanmalıdır.

- Kesinti başlangıcında ve sonunda istasyon saatini bağımsız referansla karşılaştırın.
- Saat sapması için alarm ve bakım eşiği belirleyin.
- Yeniden bağlantıda geçmiş olayların kronolojik sırasını doğrulayın.
- Tarife ve faturalama sisteminin gecikmeli kayıtlara verdiği sonucu test edin.

_Kaynaklar: S1, S3_

## Bağlantı geri geldiğinde mutabakat nasıl yapılmalıdır?

Bağlantı geri geldiğinde istasyon bekleyen mesajları gönderebilir, merkezi sistem yapılandırma veya uzaktan komutları yeniden uygulayabilir ve cihaz durumu değişebilir. Bu aşamada yalnız 'online' göstergesinin yeşile dönmesi yeterli değildir; bekleyen işlemlerin tam sayısı, sayaç toplamı, hata kayıtları ve kullanıcı hesapları karşılaştırılmalıdır.

Tekrarlı mesaj, sıra dışı zaman damgası veya cihaz yeniden başlatma sonrasında merkezi sistemin idempotent davranması gerekir. Mutabakat raporu; istasyon kaydı, CSMS kaydı, ödeme/faturalama kaydı ve ana sayaç verisini tek olay çizelgesinde birleştirmelidir.

- Bekleyen mesaj sayısını bağlantı öncesi ve sonrası kaydedin.
- İstasyon, CSMS ve ödeme kayıtlarını işlem kimliğiyle eşleştirin.
- Yinelenen veya eksik işlem için otomatik alarm üretildiğini doğrulayın.
- Uzaktan durdurma ve yeniden başlatma komutlarını bağlantı dönüşünde kontrollü test edin.

_Kaynaklar: S1, S2, S3_

## Canlı işletme öncesi hangi kabul dosyası hazırlanmalıdır?

Kabul dosyasında cihaz modeli, firmware, OCPP sürümü ve sertifika profili; yerel yetkilendirme ayarları; çevrimdışı bellek kapasitesi; saat kayması; test kartları; her senaryonun enerji ve işlem kayıtları; bağlantı dönüşü mutabakatı ve hata ekranları bulunmalıdır. Testler gerçek kullanıcı verisi yerine kontrollü test kimlikleriyle yapılmalıdır.

İstasyon tüm senaryolarda kayıt kaybetmeden ve güvenli yetkilendirme politikasıyla çalışıyorsa yeni modem, SIM veya şarj cihazı satın almak gerekmeyebilir. Sorun yalnız mobil kapsama ise önce ağ ve anten yerleşimi; işlem bütünlüğü sorunu ise firmware, CSMS ve protokol uyumu birlikte ele alınmalıdır.

- En az yedi çevrimdışı senaryoyu tarih ve sonuçla imzalayın.
- Gerçek kart, telefon, plaka veya ödeme verisini ALO186'e yüklemeyin.
- Başarısız senaryoyu cihaz, ağ, CSMS veya ödeme katmanına ayırın.
- Mevcut sistem yeterliyse gereksiz donanım değişiminden kaçının.

_Kaynaklar: S1, S2, S3, S4_

## Sık sorulan sorular

### İnternet kesilince şarj devam eder mi?

Aktif işlemin devamı ve yeni işlemin başlatılması cihazın yerel politika ve ayarlarına bağlıdır. Kabul testi, aktif işlem ile yeni çevrimdışı işlemi ayrı ayrı doğrulamalıdır.

_Kaynaklar: S1, S2_

### OCPP uyumlu her istasyon çevrimdışı kart kabul eder mi?

Hayır. Yerel yetkilendirme önbelleği veya yerel liste desteği ve bunun sahada etkinleştirilmesi gerekir. Sertifika profili ve cihaz ayarı birlikte incelenmelidir.

_Kaynaklar: S2, S3_

### Bağlantı gelince işlemler iki kez faturalandırılabilir mi?

Yanlış entegrasyon veya yinelenen kayıt işleme hatası varsa olabilir. İşlem kimliği, sayaç toplamı ve ödeme kaydıyla idempotent mutabakat testi yapılmalıdır.

_Kaynaklar: S1, S3_

### OCPP 1.6 ile 2.0.1 aynı şekilde test edilir mi?

Hayır. Sürümler geriye dönük uyumlu değildir ve işlem modeli farklıdır. Test senaryosu kullanılan sürümün resmî spesifikasyonu ve cihaz sertifika kapsamına göre hazırlanmalıdır.

_Kaynaklar: S1, S4_

## İnsan onay komutu

PR sahibinin veya repository yetkilisinin yorumu:

```text
/cms approve ev-sarj-istasyonu-internet-kesintisi-ocpp-offline-islem-kabul
```

Onay iş akışı kalite puanı, kaynak güncelliği, iç linkler, kanibalizasyon ve risk sınırlarını yeniden çalıştırmadan canonical dosya üretmez.
