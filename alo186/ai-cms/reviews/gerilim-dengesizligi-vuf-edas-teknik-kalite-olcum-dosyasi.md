# ALO186 AI CMS inceleme paketi — gerilim-dengesizligi-vuf-edas-teknik-kalite-olcum-dosyasi

> Bu dosya canonical yayına dahil edilmez. PR incelemesi ve insan onayı için üretilmiştir.

## Durum

- State: **approved**
- Risk: **legal**
- Model: **gpt-5.6-thinking**
- Kalite: **88/100**
- Benzerlik: **0.33** — https://alo186.com/haberler/edas-gerilim-kalitesi-olcum-talebi-dusuk-yuksek-voltaj-sikayet-dosyasi
- Kelime: **989**

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

- **S1 · IEC** — [IEC 61000-4-30:2025 — Power Quality Measurement Methods](https://webstore.iec.ch/en/publication/71611) — erişim 2026-08-03 — birincil
- **S2 · IEC** — [IEC 60034-26:2026 — Effects of Unbalanced Voltages on Three-Phase Cage Induction Motors](https://webstore.iec.ch/en/publication/95874) — erişim 2026-08-03 — birincil
- **S3 · Schneider Electric** — [Symmetrical Components Module](https://product-help.se.com/docs/ION-Reference/content/ion%20reference/symmetrical-components-module.htm?TocPath=ION+modules%7C_____104) — erişim 2026-08-03 — birincil
- **S4 · Schneider Electric** — [Learning About Voltage Unbalance](https://meterinsights.schneider-electric.com/help/learning-about-voltage-unbalance) — erişim 2026-08-03 — birincil
- **S5 · EPDK** — [Elektrik Tüketicisi Sıkça Sorulan Sorular — Teknik Kalite Hakları](https://epdk.gov.tr/Detay/Icerik/12-3/1-elektrik-aboneligini-kendi-adima-almak-zorunda) — erişim 2026-08-03 — birincil
- **S6 · EPDK** — [Elektrik Piyasası Güncel Yönetmelikler ve Teknik Kalite Usul ve Esasları](https://www.epdk.gov.tr/Detay/Icerik/3-0-159/yonetmelikler) — erişim 2026-08-03 — birincil

## SEO

- Title: `Gerilim Dengesizliği VUF ve EDAŞ Ölçüm Dosyası`
- H1: `Gerilim dengesizliği VUF nasıl ölçülür ve EDAŞ dosyası nasıl hazırlanır?`
- Description: `Gerilim dengesizliğini VUF, negatif sıra, faz akımı, motor sıcaklığı ve bir haftalık Class A kayıtla kanıtlayıp EDAŞ teknik kalite dosyası hazırlayın.`
- Canonical: `/haberler/gerilim-dengesizligi-vuf-edas-teknik-kalite-olcum-dosyasi`
- Birincil anahtar kelime: `gerilim dengesizliği VUF EDAŞ ölçüm`

## Doğrudan cevap

Gerilim dengesizliği yalnız üç faz gerilimi arasındaki en büyük farkı volt cinsinden görmekle güvenilir biçimde değerlendirilmez. Kabul dosyasında IEC 61000-4-30'a uygun yöntemle pozitif ve negatif sıra bileşenleri, VUF, faz-faz ve faz-nötr gerilimleri, olay zamanları kaydedilmeli; aynı anda motor akımları, yük girişleri ve sıcaklıklar izlenmelidir. Servis girişindeki bir haftalık kayıt ile yük noktasındaki kayıt karşılaştırılarak sorun şebeke, iç tesisat, yük dağılımı, gevşek bağlantı veya motor kaynaklı olarak ayrılmalıdır. Teknik kalite şikâyeti için dağıtım şirketinden ölçüm istenebilir; güncel sınırlar resmî mevzuattan doğrulanmalıdır.

## VUF ve negatif sıra gerilimi neden basit faz farkından daha anlamlıdır?

Üç faz gerilimlerinin büyüklükleri birbirine yakın olsa bile faz açıları veya sıra bileşenleri nedeniyle motor açısından zararlı bir dengesizlik oluşabilir. VUF, negatif sıra geriliminin pozitif sıra gerilimine oranını ifade eden bir göstergedir ve üç fazlı motorların ters yönde dönen manyetik alan etkisini değerlendirmede basit maksimum-minimum yüzde hesabından daha açıklayıcıdır.

Ölçüm cihazının hangi dengesizlik tanımını kullandığı raporda açıkça yazılmalıdır. Faz-faz gerilimleri, faz-nötr gerilimleri, pozitif/negatif/varsa sıfır sıra büyüklükleri, VUF ve zaman birleştirme yöntemi aynı cihaz konfigürasyonundan alınmalı; farklı üretici yüzdeleri eşdeğer kabul edilmemelidir.

- Faz-faz ve faz-nötr gerilimleri ayrı kaydedin.
- VUF hesap yöntemini ve pozitif-negatif sıra değerlerini rapora yazın.
- Cihaz ölçüm sınıfı, bağlantı tipi ve zaman birleştirmesini belirtin.
- Basit gerilim farkı yüzdesini VUF ile karıştırmayın.

_Kaynaklar: S1, S2, S3_

## Gerilim dengesizliği motor akımı ve sıcaklığıyla nasıl ilişkilendirilir?

Negatif sıra gerilimi üç fazlı asenkron motorda akım dengesizliğini ve ek ısınmayı büyütebilir. Bu nedenle yalnız şebeke gerilimi trendi değil; motorun her faz akımı, yük oranı, sargı veya gövde sıcaklığı, koruma açma zamanı ve proses durumu aynı zaman ekseninde kaydedilmelidir. Motor üreticisinin izin verdiği işletme sınırı ve derating şartı ayrıca kontrol edilmelidir.

Kontaktör, sigorta, terminal, kablo ve pano bağlantılarındaki yüksek direnç de yük altında faz bazlı gerilim düşümü yaratabilir. Servis girişinde VUF düşükken motor terminalinde yükseliyorsa iç tesisat ve bağlantılar; girişte de yüksekse şebeke veya ortak yük etkisi öncelikli incelenmelidir. Termal kamera bulgusu tek başına dengesizlik nedeni sayılmamalı, elektriksel ölçümle eşleştirilmelidir.

- Motor faz akımları ve sıcaklıklarını VUF ile aynı anda kaydedin.
- Yük oranı ve motor devreye giriş saatlerini trend üzerine işaretleyin.
- Servis girişi ile motor terminalini eşzamanlı karşılaştırın.
- Bağlantı ısınmasını gerilim düşümü ve direnç kanıtıyla doğrulayın.

_Kaynaklar: S2, S3, S4_

## Şebeke, iç tesisat ve yük kaynaklı dengesizlik nasıl ayrılır?

Ölçüm planı bağlantı noktasından yüke doğru ilerlemelidir. Ana girişte, ana pano çıkışında ve şüpheli motor veya sürücü girişinde mümkün olduğunca ortak saatli kayıt alınmalıdır. Tek fazlı büyük yükler, fazlara eşit dağılmayan EV şarjı, kaynak makineleri, asansörler, gevşek nötr veya faz bağlantıları ve jeneratör işletmesi olay günlüğünde ayrı etiketlenmelidir.

Şebeke ile iç tesisatı ayırmak için farklı yük durumlarında karşılaştırma yapılır: tesis yükü düşükken, şüpheli yük devredeyken, jeneratör veya UPS kaynağında ve şebeke beslemesinde. VUF yalnız belirli bir cihaz çalıştığında yükseliyorsa yerel etki; farklı tüketicilerde ve servis girişinde süreklilik gösteriyorsa dağıtım tarafı ihtimali güçlenir. Sonuç kesin neden değil, kanıt ağırlığı olarak raporlanmalıdır.

- Ana giriş, ana pano ve yük noktasında ortak saatli kayıt planlayın.
- Tek fazlı büyük yükleri ve faz dağılımını olay günlüğüne ekleyin.
- Şebeke, jeneratör ve UPS çalışma modlarını ayrı etiketleyin.
- Yerel yük kapalı/açık A-B karşılaştırması yapın.

_Kaynaklar: S1, S3, S4_

## EDAŞ teknik kalite ölçüm talebi için bir haftalık dosya nasıl hazırlanır?

EPDK tüketici bilgilendirmesi, teknik kalite şikâyetlerinin değerlendirilmesi için kullanıcıların dağıtım şirketinden ölçüm talep edebileceğini belirtir. Kullanıcı soruna neden olmuyorsa veya bir haftalık ölçüm sonucunda ilgili teknik kalite sınırları aşılıyorsa ölçüm bedeli talep edilemeyeceği açıklanmıştır. Güncel başvuru kanalı, ölçüm noktası ve yürürlükteki sınırlar başvuru tarihinde resmî kaynaklardan yeniden doğrulanmalıdır.

Başvuruda açık adres veya abonelik verisi ALO186'e girilmez; bunlar yalnız resmî dağıtım şirketi kanalına verilir. Dosya; tarih-saatli belirti günlüğü, etkilenen ekipman listesi, ana giriş tek hattı, mevcut analizörün Class A/S bilgisi, VUF ve gerilim trendleri, yük olayları, motor akım-sıcaklık korelasyonu ve daha önceki başvuru numaralarını içermelidir. ALO186 dağıtım şirketi değildir ve ölçüm sonucu vermez.

- Resmî EDAŞ kanalından teknik kalite ölçümü talep edin.
- Bir haftalık kayıt aralığını ve analizör sınıfını başvuruda belirtin.
- Belirti, yük ve VUF zaman damgalarını aynı dosyada birleştirin.
- Abonelik ve adres bilgilerini yalnız resmî kanala iletin.

_Kaynaklar: S1, S5, S6_

## Ölçüm sonucu hangi aksiyon ve kapanış kanıtına dönüştürülmelidir?

Sonuç; şebeke kaynaklı olası dengesizlik, iç tesisat faz dağılımı, yüksek dirençli bağlantı, ekipman kaynaklı akım dengesizliği veya yetersiz kanıt olarak sınıflandırılmalıdır. Dağıtım şirketi ölçümü ile özel analizör kaydı farklıysa ölçüm sınıfı, bağlantı noktası, saat senkronu, veri aralığı ve hesap yöntemi karşılaştırılmalıdır. Evrensel tek bir VUF eşiği yayımlamak yerine proje, motor üreticisi ve güncel mevzuat sınırları birlikte kullanılmalıdır.

Düzeltme sonrası aynı yük ve ölçüm koşullarında yeniden kayıt alınmalı; VUF, faz akımları, sıcaklık ve koruma olayları öncesi-sonrası karşılaştırılmalıdır. Faz yükleri dengelenip bağlantılar sağlam ve giriş ölçümü sınırlar içindeyse sırf daha yeni bir güç kalitesi analizörü, motor veya koruma rölesi satın almak gerekmez.

- Sonucu kaynak sınıfı ve kanıt gücüyle raporlayın.
- Özel ve EDAŞ ölçümlerinde cihaz sınıfı ve zamanı karşılaştırın.
- Düzeltme sonrası aynı yük senaryosunu yeniden çalıştırın.
- Kanıt yeterliyse gereksiz motor, röle veya analizör değişimi yapmayın.

_Kaynaklar: S1, S2, S3, S5, S6_

## Sık sorulan sorular

### Gerilim dengesizliği ile faz kaybı aynı şey midir?

Hayır. Faz kaybı bir fazın tamamen veya etkili biçimde yok olmasıdır; gerilim dengesizliğinde üç faz mevcut olabilir ancak büyüklük veya faz açıları eşit değildir. VUF negatif ve pozitif sıra bileşenleri üzerinden dengesizliği nicelendirir.

_Kaynaklar: S1, S3_

### Üç faz gerilimleri yakınsa motor neden yine ısınabilir?

Basit voltaj farkı faz açısı ve negatif sıra bileşenini tam göstermez. Negatif sıra alanı motor akımlarında daha büyük dengesizlik ve ek ısınma oluşturabilir; motor akımı, yük ve sıcaklık birlikte ölçülmelidir.

_Kaynaklar: S2, S3_

### EDAŞ'tan teknik kalite ölçümü isteyebilir miyim?

EPDK tüketici bilgilendirmesine göre teknik kalite şikâyetleri için dağıtım şirketinden ölçüm talep edilebilir. Başvuru, güncel resmî kanal ve yürürlükteki mevzuata göre yapılmalı; ALO186 abonelik veya adres verisi almaz.

_Kaynaklar: S5, S6_

### VUF için tek bir evrensel kabul sınırı var mıdır?

Cihaz ölçüm standardı, ulusal teknik kalite düzenlemesi, bağlantı seviyesi ve motor üreticisi sınırları birlikte değerlendirilmelidir. ALO186 proje ve mevzuat bağlamı olmadan tek bir evrensel yüzdeyi güvenli kabul sınırı olarak yayımlamaz.

_Kaynaklar: S1, S2, S5_

## İnsan onay komutu

PR sahibinin veya repository yetkilisinin yorumu:

```text
/cms approve gerilim-dengesizligi-vuf-edas-teknik-kalite-olcum-dosyasi
```

Onay iş akışı kalite puanı, kaynak güncelliği, iç linkler, kanibalizasyon ve risk sınırlarını yeniden çalıştırmadan canonical dosya üretmez.
