# ALO186 AI CMS inceleme paketi — ups-giris-thdi-jenerator-uyumluluk-kabul-testi

> Bu dosya canonical yayına dahil edilmez. PR incelemesi ve insan onayı için üretilmiştir.

## Durum

- State: **approved**
- Risk: **high**
- Model: **GPT-5.6 Thinking**
- Kalite: **100/100**
- Benzerlik: **0.17** — https://www.alo186.com/haberler/ups-jenerator-boyutlandirma-thdi-guc-faktoru
- Kelime: **984**

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

- **S1 · IEC** — [IEC 62040-3:2021 — UPS performans ve test gerekleri](https://webstore.iec.ch/en/publication/60140) — erişim 2026-08-03 — birincil
- **S2 · Schneider Electric** — [Easy UPS 3L 250–400 kVA giriş ve bypass özellikleri](https://productinfo.se.com/easyups3l/990-6289_master-easy-ups-3l-technical-specifications/English/990-6289%20Easy%20UPS%203L%20Technical%20Specifications_0000415605.xml/%24/FacilityPlanningfor250-400kVAUPSsforExternalBatteriesREF_0000493856) — erişim 2026-08-03 — birincil
- **S3 · Schneider Electric** — [Easy UPS 3S 380/400/415 V teknik özellikleri](https://productinfo.se.com/easyups3s/viewer?docidentity=REF_Specifications-B929255A&extension=xml&lang=en&manualidentity=InstallationEasyUPS3SWithInternalBa-984B85A2) — erişim 2026-08-03 — birincil
- **S4 · Schneider Electric** — [Easy UPS 3L normal mod başlatma ve doğrultucu rampası](https://productinfo.se.com/easyups3l/viewer?docidentity=StartUpASingleUPSInNormalModeWithSi-DD8CE505&extension=xml&lang=en&manualidentity=OperationEasyUPS3L500-600KVAInsertP-C1133F8E) — erişim 2026-08-03 — birincil

## SEO

- Title: `UPS Giriş THDi ve Jeneratör Uyumluluk Kabulü`
- H1: `UPS giriş THDi değeri jeneratör seçimini ve kararlı çalışmayı nasıl etkiler?`
- Description: `UPS, jeneratör, akü şarjı, ramp-in, giriş THDi ve güç faktörünü gerçek yük testinde doğrulayarak kVA tahmini yerine kabul dosyası oluşturun.`
- Canonical: `/haberler/ups-giris-thdi-jenerator-uyumluluk-kabul-testi`
- Birincil anahtar kelime: `UPS giriş THDi`

## Doğrudan cevap

UPS ile jeneratör uyumu yalnız UPS çıkış kVA’sını bir katsayıyla büyütmek değildir. Jeneratör, UPS’nin gerçek maksimum giriş akımını, akü yeniden şarj gücünü, ramp-in süresini, giriş güç faktörünü ve THDi kaynaklı akım dalga biçimini; aynı baradaki motor ve diğer yüklerle birlikte kararlı taşımalıdır. Kabul testi jeneratör boşta çalışmadan başlayıp UPS doğrultucusunun devreye girmesi, yük basamakları, akü şarjı, transfer, bypass senkronu ve geri dönüş boyunca gerilim, frekans, akım, THDi ve olay loglarını kaydetmelidir. Evrensel bir aşırı boyutlandırma oranı yerine UPS ve jeneratör üretici verileri ile gerçek saha testi kullanılmalıdır.

## Nominal kVA dışında hangi UPS giriş verileri gerekir?

UPS çıkış gücü, jeneratör hesabının yalnız bir parçasıdır. Teknik dosyada nominal ve maksimum giriş akımı, doğrultucu akım limiti, akü şarj gücü, giriş güç faktörü, THDi, ramp-in süresi, bypass giriş şartları ve üreticinin jeneratör modu bulunmalıdır. IEC 62040-3, tamamlanmış UPS sisteminin performans ve test gereklerini tanımlayan temel çerçeveyi verir.

Üretici verileri model ve yük koşuluna göre değişebilir. Schneider Easy UPS örneklerinde düşük giriş THDi, yüksek giriş güç faktörü ve belirli ramp-in süreleri ayrı ayrı yayınlanır. Bu değerler, aynı kVA etiketi taşıyan iki UPS’nin jeneratöre aynı dinamik yükü uygulayacağı varsayımını geçersiz kılar.

- UPS nominal ve maksimum giriş akımını ayrı kaydedin.
- Akü şarj gücü ve doğrultucu akım limitini dosyaya ekleyin.
- Giriş THDi, güç faktörü ve ramp-in süresini model belgesinden alın.
- Normal giriş ile bypass girişinin bağlantı ve senkron şartlarını ayırın.

_Kaynaklar: S1, S2, S3_

## Giriş THDi jeneratör gerilimini ve AVR davranışını nasıl etkileyebilir?

Doğrusal olmayan doğrultucu akımı sinüs biçiminden sapar ve jeneratörün iç empedansı üzerinde harmonik gerilim düşümleri oluşturabilir. Sonuç, yalnız akım THDi değeri değil; terminal gerilimi dalga biçimi, AVR tepkisi, ısınma, nötr akımı ve UPS’nin giriş toleransı içinde kalıp kalmadığıdır. Modern PFC girişli UPS’ler düşük THDi sağlayabilir, ancak gerçek değer yük oranı ve işletme moduyla doğrulanmalıdır.

Aynı baradaki motor yol verme, asansör, soğutma kompresörü veya VFD gibi yükler jeneratör gerilim ve frekansını ayrıca zorlar. Bu nedenle UPS’yi tek başına test etmek yeterli olmayabilir. Jeneratör alternatörü, AVR, motor governor, kısa devre gücü ve yük sıralaması ortak kabul senaryosunda değerlendirilmelidir.

- Gerilim ve akım dalga biçimini jeneratör terminali ve UPS girişinde kaydedin.
- THDi ile birlikte THDv, faz dengesizliği ve nötr akımını izleyin.
- Motor yol verme ve büyük yük basamaklarını aynı senaryoya ekleyin.
- AVR ve governor ayarlarını yetkisiz biçimde değiştirmeyin; üretici kabul sınırını kullanın.

_Kaynaklar: S2, S3, S4_

## Akü şarjı, ramp-in ve yük sıralaması neden kritik olur?

Kesinti sonrasında jeneratör devreye girdiğinde UPS hem kritik yükü besler hem de boşalmış aküyü şarj etmeye çalışabilir. Maksimum şarj gücü sınırlandırılmamışsa jeneratör üzerindeki yük, yalnız çıkış yükünden belirgin biçimde yüksek olabilir. Ramp-in özelliği doğrultucunun giriş akımını zamana yayarak ani basamağı azaltır; ancak süre ve limit model ayarına bağlıdır.

Yük sıralaması jeneratör kararlı gerilim ve frekansa ulaştıktan sonra UPS doğrultucusunu, ardından diğer büyük yükleri kontrollü devreye almalıdır. Akü şarj limiti, kritik yük önceliği ve jeneratör modu üretici prosedürüyle belirlenmelidir. Yalnız UPS hassasiyetini gevşetmek veya geniş frekans penceresi seçmek kararsız jeneratörü güvenli hâle getirmez.

- En kötü akü SoC durumunda şarj gücünü hesaba katın.
- Ramp-in süresi ve giriş akım limitini test senaryosuna yazın.
- UPS, motor ve HVAC yüklarını kademeli sıraya bağlayın.
- Geniş tolerans ayarını ölçüm ve üretici onayı olmadan çözüm saymayın.

_Kaynaklar: S2, S3, S4_

## UPS–jeneratör saha kabul testi hangi adımları içermelidir?

Test; jeneratörün boşta gerilim ve frekans kararlılığı, UPS girişinin kapanması, doğrultucu rampası, yüzde 25–50–75–100 yük basamakları, akü şarjı, ortak büyük yükler, UPS’nin jeneratör kaynağını kabulü, bypass senkronu ve şebekeye geri dönüş adımlarını kapsamalıdır. Her adımda RMS değerlerin yanında dalga biçimi ve olay logu tutulmalıdır.

UPS’nin sık bataryaya geçmesi, jeneratör alarmı, frekans avlanması, bypass senkron olamaması veya gerilim dalga biçimi bozulması fail kriteridir. Sorunun kaynağı UPS girişi, jeneratör kapasitesi, AVR/governor dinamiği, kablo/trafo empedansı veya yük sırası olabilir. Düzeltme sonrası aynı senaryo tekrarlanmalıdır.

- Boşta, yük basamaklı ve akü şarjlı testleri ayrı kaydedin.
- Gerilim, frekans, akım, THDi, THDv ve olay loglarını eşzamanlayın.
- Bypass senkronu ile normal mod kabulünü ayrı doğrulayın.
- Fail kriteri oluşursa ayar değişikliğinden önce kök nedeni belgeleyin.

_Kaynaklar: S1, S2, S3, S4_

## Boyutlandırma dosyası hangi kararı üretmelidir?

Dosya; UPS giriş tablosu, akü şarj profili, gerçek kritik yük, eşzamanlı motorlar, jeneratör alternatör ve motor verileri, ortam/irtifa deratingi, kablo-trafo empedansı, yük sırası ve saha ölçümlerini içerir. Böylece “UPS kVA × sabit oran” yaklaşımı yerine, üretici verisine bağlı izlenebilir kapasite ve kontrol kararı çıkar.

Mevcut jeneratör; şarj limiti, ramp-in ve güvenli yük sırasıyla tüm kabul kriterlerini sağlıyorsa daha büyük jeneratör veya UPS satın almak gerekmeyebilir. Kapasite veya dinamik performans yetersizse seçenekler yalnız jeneratörü büyütmek değildir; akü şarj yönetimi, yük önceliği, alternatör/AVR seçimi ve kontrollü sekans da değerlendirilir. Güvenlik ve garantiyi etkileyen ayarlar yetkili servis sınırındadır.

- Nominal kVA yerine maksimum gerçek giriş ve dinamik yük dosyası hazırlayın.
- Ortam, irtifa, kablo, trafo ve ortak yük etkilerini ekleyin.
- Kabul sağlanıyorsa gereksiz jeneratör veya UPS değişimini önleyin.
- Ayar ve ekipman kararlarını üretici onayı ve tekrar testine bağlayın.

_Kaynaklar: S1, S2, S3, S4_

## Sık sorulan sorular

### UPS için jeneratör gücü kaç kat büyük olmalıdır?

Her sistem için geçerli tek bir katsayı yoktur. UPS’nin maksimum giriş akımı, akü şarj gücü, ramp-in, THDi, güç faktörü, jeneratör empedansı, ortak motor yükleri, ortam ve üretici şartları birlikte hesaplanıp saha testinde doğrulanmalıdır.

_Kaynaklar: S1, S2, S3_

### Düşük UPS giriş THDi değeri küçük jeneratörün yeterli olduğunu kanıtlar mı?

Hayır. Düşük THDi yararlı bir özelliktir; ancak maksimum giriş akımı, akü şarjı, dinamik yük basamağı, AVR/governor tepkisi, kısa devre gücü ve diğer yükler de kararlılığı belirler.

_Kaynaklar: S2, S3_

### UPS jeneratörde sürekli bataryaya geçiyorsa hassasiyeti düşürmeli miyim?

Önce jeneratör gerilim ve frekans kararlılığı, dalga biçimi, yük basamakları, ramp-in, şarj limiti ve kablo/trafo empedansı ölçülmelidir. Tolerans ayarını genişletmek kök nedeni gizleyebilir ve bypass veya yük uyumluluğunu etkileyebilir.

_Kaynaklar: S1, S4_

### Akü doluyken yapılan test yeterli midir?

Hayır. Akü doluyken şarj talebi düşük olabilir. En kötü makul SoC durumunda akü şarjı, kritik yük ve eşzamanlı büyük yüklerle kontrollü kabul testi yapılmalı; üretici sınırları aşılmamalıdır.

_Kaynaklar: S2, S3_

## İnsan onay komutu

PR sahibinin veya repository yetkilisinin yorumu:

```text
/cms approve ups-giris-thdi-jenerator-uyumluluk-kabul-testi
```

Onay iş akışı kalite puanı, kaynak güncelliği, iç linkler, kanibalizasyon ve risk sınırlarını yeniden çalıştırmadan canonical dosya üretmez.
