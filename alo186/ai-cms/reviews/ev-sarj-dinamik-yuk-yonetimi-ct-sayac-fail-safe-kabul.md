# ALO186 AI CMS inceleme paketi — ev-sarj-dinamik-yuk-yonetimi-ct-sayac-fail-safe-kabul

> Bu dosya canonical yayına dahil edilmez. PR incelemesi ve insan onayı için üretilmiştir.

## Durum

- State: **approved**
- Risk: **high**
- Model: **gpt-5.6-thinking**
- Kalite: **88/100**
- Benzerlik: **0.33** — https://alo186.com/haberler/ev-sarj-dinamik-yuk-yonetimi-ct-sayac-faz-eslesmesi
- Kelime: **974**

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

- **S1 · IEC** — [IEC 60364-7-722:2018 — Supplies for electric vehicles](https://webstore.iec.ch/en/publication/29958) — erişim 2026-08-03 — birincil
- **S2 · IEC** — [IEC 61851-1:2017 — Electric vehicle conductive charging system, general requirements](https://webstore.iec.ch/en/publication/33644) — erişim 2026-08-03 — birincil
- **S3 · Open Charge Alliance** — [OSCP — Open Smart Charging Protocol](https://openchargealliance.org/protocols/open-smart-charging-protocol/) — erişim 2026-08-03 — birincil
- **S4 · Open Charge Alliance** — [OCPP — Open Charge Point Protocol](https://openchargealliance.org/protocols/open-charge-point-protocol/) — erişim 2026-08-03 — birincil
- **S5 · Open Charge Alliance** — [Certification OCPP 1.6](https://openchargealliance.org/certificationocpp/certification-ocpp-1-6/) — erişim 2026-08-03 — birincil

## SEO

- Title: `EV Şarj Dinamik Yük Yönetimi: CT ve Fail-Safe Kabulü`
- H1: `EV şarj dinamik yük yönetimi CT yönü ve fail-safe nasıl test edilir?`
- Description: `EV şarj yük yönetiminde CT yönü, faz eşleşmesi, haberleşme kaybı ve güç sınırını gerçek yük adımlarıyla doğrulayan kabul rehberi.`
- Canonical: `/haberler/ev-sarj-dinamik-yuk-yonetimi-ct-sayac-fail-safe-kabul`
- Birincil anahtar kelime: `EV şarj dinamik yük yönetimi CT testi`

## Doğrudan cevap

Dinamik yük yönetimi yalnız ekranda bir amper sınırı görünmesiyle kabul edilmez. Ana giriş CT’leri veya sayacı doğru faz ve yönde okumalı, şarj gücü gerçek bina yüküyle birlikte tanımlı bağlantı sınırını aşmamalı ve ölçüm ya da haberleşme kaybında sistem güvenli bir yerel sınıra dönmelidir. Kabul; faz bazlı P/I, CT yönü, sayaç çarpanı, setpoint–gerçek güç, yük adımı tepkisi ve fail-safe olay kaydıyla yapılır. Enerjili CT ve pano testleri yalnız yetkin ekipçe yürütülmelidir.

## Dinamik yük yönetiminde hangi ölçüm noktası esas alınmalıdır?

Dinamik yük yönetiminin amacı yalnız wallbox akımını azaltmak değil, tesisin bağlantı noktasındaki toplam yükü tanımlı kapasite içinde tutmaktır. Bu nedenle ana giriş, alt dağıtım veya yalnız şarj panosu ölçümü birbirinin yerine kullanılamaz. Ölçüm sınırı tek hat üzerinde işaretlenmeli; bina yükleri, GES üretimi, batarya, jeneratör ve tüm şarj noktalarının hangi tarafta kaldığı açıkça gösterilmelidir.

IEC 60364-7-722 EV besleme devrelerinin tesis gereklerini, IEC 61851-1 ise iletken şarj ekipmanının genel güvenlik ve çalışma çerçevesini tanımlar. OSCP, fiziksel şebeke kapasitesinin işletmeci arka ofisine bildirilip şarj profillerinin bu sınırlar içinde oluşturulması yaklaşımını açıklar. Saha kabulünde protokol adı kadar ölçüm noktasının gerçekten bağlantı sınırını temsil etmesi önemlidir.

- Ana bağlantı gücünü, sözleşme/koruma sınırını ve ölçüm noktasını tek hatta gösterin.
- Ana giriş ile şarj panosu ölçümünü ayrı isimlendirin.
- GES, BESS ve jeneratörün ölçüm sınırına göre işaretini doğrulayın.
- Etiket gücünü gerçek kullanılabilir kapasite sanmayın.

_Kaynaklar: S1, S2, S3_

## CT yönü, faz sırası ve sayaç çarpanı nasıl doğrulanır?

Ters takılmış bir CT, yanlış faz eşleştirmesi veya hatalı sayaç çarpanı tüketimi üretim gibi gösterebilir ve algoritmanın şarj gücünü artırması gereken anda azaltmasına ya da sınırı aşmasına neden olabilir. Her CT’nin P1/P2 veya ok yönü, bağlı olduğu faz, sekonder oranı ve sayaç kanal eşleşmesi fiziksel etiket ve kontrollü yük değişimiyle doğrulanmalıdır.

Doğrulama yalnız toplam üç faz kW değerine bakılarak yapılmamalıdır. Tek fazlı kontrollü bir yük adımı uygulandığında doğru fazın aktif gücü ve akımı beklenen yönde değişmeli; diğer fazlar yanlış tepki vermemelidir. İhracat/ithalat işareti, GES üretimi ve EV şarjı aynı anda varken ayrıca kontrol edilmelidir. CT sekonderine enerjili durumda gelişigüzel müdahale edilmez.

- Her CT’nin oranını, yönünü, fazını ve sayaç kanalını kaydedin.
- Faz bazlı kontrollü yük adımıyla P ve I değişimini karşılaştırın.
- İthalat ve ihracat işaretini GES açık ve kapalı senaryoda doğrulayın.
- CT sekonderini açık devre bırakmayın veya kullanıcı işlemi olarak sunmayın.

_Kaynaklar: S1, S2, S3_

## Setpoint ile gerçek şarj gücü hangi testlerle karşılaştırılmalıdır?

Kabul testi düşük, tipik ve yüksek bina yükünde yapılmalıdır. Bir klima grubu, pompa veya başka büyük yük devreye girdiğinde kontrolörün yeni kullanılabilir kapasiteyi hesaplama süresi, wallboxlara gönderdiği setpoint ve bağlantı noktasındaki gerçek P/I ortak zaman tabanında izlenmelidir. Sadece uygulamadaki komut değeri, aracın gerçekten o güçte şarj ettiğini kanıtlamaz.

OCPP 1.6 akıllı şarj profilleriyle yük dengeleme desteği sunar; OCPP 2.0.1 ve 2.1 daha gelişmiş akıllı şarj ve DER işlevleri sağlar. Ancak protokol desteği, saha limitinin doğru uygulandığı anlamına gelmez. Araç kabul sınırı, faz sayısı, minimum şarj akımı ve CPMS gecikmesi nedeniyle gerçek güç setpointten farklı olabilir; geçti-kaldı kriteri bağlantı noktası sınırına göre kurulmalıdır.

- En az üç bina yük düzeyinde test yapın.
- Setpoint, wallbox ölçümü ve ana sayaç P/I değerlerini aynı zaman çizelgesine alın.
- Tek ve çoklu araç senaryolarını ayrı sınayın.
- Kısa süreli aşım, salınım ve kararlı hata için proje kriteri tanımlayın.

_Kaynaklar: S3, S4, S5_

## Sayaç veya haberleşme kaybında fail-safe nasıl çalışmalıdır?

Sayaç verisi donarsa, CT haberleşmesi kesilirse, CPMS erişilemez olursa veya zaman damgası bayatlarsa sistem son yüksek setpointte kontrolsüz kalmamalıdır. Tasarım, yerel güvenli akım sınırı, şarjın kontrollü durdurulması veya önceden doğrulanmış başka bir fallback davranışı tanımlamalıdır. Hangi davranışın doğru olduğu tesis kapasitesine ve ürün mimarisine bağlıdır.

OSCP 2.0 tüketim, üretim ve fallback tahminleri ile hata mesajlarını kapsayan daha genel bir kapasite iletişimi tanımlar. OCPP tarafında da cihaz yönetimi, izleme ve akıllı şarj işlevleri bulunur. Kabulde fiziksel haberleşme kablosu, ağ, sayaç beslemesi ve arka ofis ayrı ayrı kesinti senaryosuna alınmalı; alarm, yerel limit, yeniden bağlantı ve setpoint toparlanması kaydedilmelidir.

- Sayaç verisi bayatlık eşiğini ve alarmını doğrulayın.
- Yerel fail-safe akımını proje kapasitesiyle eşleştirin.
- CPMS, sayaç ve ağ kaybını ayrı senaryolarda sınayın.
- Haberleşme geri geldiğinde ani güç sıçramasını engelleyin.

_Kaynaklar: S3, S4, S5_

## Dinamik yük yönetimi hangi kabul dosyasıyla teslim alınmalıdır?

Teslim paketi; tek hat, bağlantı gücü ve koruma sınırı, CT/sayaç ürün kodu ve oranı, faz-yön matrisi, GES/BESS işaret mantığı, wallbox ve CPMS sürümleri, setpoint kayıtları, ana sayaç P/I trendi, yük adımı sonuçları, haberleşme kaybı ve fallback senaryoları ile geçti-kaldı kararını içermelidir. Her şarj noktası ve yazılım revizyonu ayrı izlenmelidir.

Ölçüm ve kontrol kanıtla doğru çalışıyorsa sırf daha yüksek akımlı wallbox veya daha büyük ana sigorta düşüncesiyle yatırım yapmak gerekmez. Buna karşılık yalnız toplam kW ekranı bulunan fakat CT yönü ve fail-safe davranışı kanıtlanmamış sistem kabul edilmemelidir. CTA: kişisel verisiz CT–sayaç–setpoint–yük adımı–fallback kabul matrisini yetkin elektrik mühendisine iletin.

- Tek hat ve yazılım parametrelerini aynı revizyon numarasıyla saklayın.
- Test cihazı, sayaç oranı ve ortak zaman kaynağını rapora ekleyin.
- Her araç/EVSE için gerçek güç ile komut farkını gösterin.
- Kanıt yeterliyse gereksiz güç artırımı veya wallbox değişimi satın almayın.

_Kaynaklar: S1, S2, S3, S4, S5_

## Sık sorulan sorular

### Dinamik yük yönetimi varsa ana sigorta hiç açmaz mı?

Hayır. Doğru ölçüm, ayar ve fail-safe riski azaltır; ancak yanlış CT yönü, gecikme, haberleşme kaybı veya koruma koordinasyonu eksikliği yine açmaya yol açabilir.

_Kaynaklar: S1, S3, S4_

### CT oku ters takılırsa ne olur?

Sistem tüketimi yanlış yönde okuyabilir ve kullanılabilir kapasiteyi hatalı hesaplayabilir. Faz-yön eşleşmesi kontrollü yük adımı ve ana sayaçla doğrulanmalıdır.

_Kaynaklar: S1, S2, S3_

### OCPP desteği dinamik yük yönetiminin çalıştığını kanıtlar mı?

Hayır. OCPP akıllı şarj işlevleri sağlar; gerçek CT/sayaç verisi, setpoint uygulaması ve bağlantı noktası sınırı saha testinde ayrıca doğrulanmalıdır.

_Kaynaklar: S4, S5_

### İnternet kesilirse EV şarj tamamen durmalı mı?

Evrensel tek cevap yoktur. Tesis kapasitesine göre güvenli yerel limit, kontrollü duruş veya başka bir fallback tanımlanmalı ve test edilmelidir.

_Kaynaklar: S3, S4_

## İnsan onay komutu

PR sahibinin veya repository yetkilisinin yorumu:

```text
/cms approve ev-sarj-dinamik-yuk-yonetimi-ct-sayac-fail-safe-kabul
```

Onay iş akışı kalite puanı, kaynak güncelliği, iç linkler, kanibalizasyon ve risk sınırlarını yeniden çalıştırmadan canonical dosya üretmez.
