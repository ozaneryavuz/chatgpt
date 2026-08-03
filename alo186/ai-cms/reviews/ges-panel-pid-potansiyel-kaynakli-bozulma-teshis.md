# ALO186 AI CMS inceleme paketi — ges-panel-pid-potansiyel-kaynakli-bozulma-teshis

> Bu dosya canonical yayına dahil edilmez. PR incelemesi ve insan onayı için üretilmiştir.

## Durum

- State: **approved**
- Risk: **high**
- Model: **gpt-5.6-thinking**
- Kalite: **88/100**
- Benzerlik: **0.30** — https://alo186.com/haberler/ges-panel-pid-lid-letid-guc-kaybi-teshisi
- Kelime: **888**

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

- **S1 · IEC** — [IEC TS 62804-1:2025 — Test Methods for Detection of PID](https://webstore.iec.ch/en/publication/71747) — erişim 2026-08-03 — birincil
- **S2 · IEC** — [IEC 61215-1-1:2021 — Crystalline Silicon PV Module Qualification](https://webstore.iec.ch/en/publication/61346) — erişim 2026-08-03 — birincil
- **S3 · National Renewable Energy Laboratory** — [Potential-Induced Degradation in Photovoltaic Modules: A Critical Review](https://research-hub.nrel.gov/en/publications/potential-induced-degradation-in-photovoltaic-modules-a-critical--2) — erişim 2026-08-03 — birincil
- **S4 · National Renewable Energy Laboratory** — [From Modules to Atoms: PV Degradation Characterization Techniques](https://research-hub.nrel.gov/en/publications/from-modules-to-atoms-techniques-and-characterization-for-identif/) — erişim 2026-08-03 — birincil

## SEO

- Title: `GES Panelinde PID Teşhisi: I-V, EL ve Sistem Gerilimi`
- H1: `GES panelinde PID kaybı nasıl anlaşılır ve diğer güç kayıplarından nasıl ayrılır?`
- Description: `GES panelindeki PID şüphesini gölgelenme, kirlenme, clipping ve izolasyon hatasından ayırın; I-V, EL, termal ve sistem gerilimi kanıtı oluşturun.`
- Canonical: `/haberler/ges-panel-pid-potansiyel-kaynakli-bozulma-teshis`
- Birincil anahtar kelime: `GES panel PID teşhisi potansiyel kaynaklı bozulma`

## Doğrudan cevap

GES’te üretim kaybı tek başına PID kanıtı değildir. PID şüphesi; benzer ışınım ve sıcaklıkta karşılaştırılan string performansı, I-V eğrisi, elektrolüminesans veya uygun görüntüleme bulguları, izolasyon ve kaçak akım davranışı, modül teknolojisi ve hücrelerin toprağa göre sistem gerilimi birlikte değerlendirilerek doğrulanmalıdır. IEC testleri modülün PID hassasiyetini laboratuvar stresinde ölçer; sahadaki arızanın kesin nedeni için kirlenme, gölgelenme, mismatch, sıcaklık derating, clipping ve bağlantı kusurları ayrıca elenmelidir.

## PID nedir ve her üretim düşüşü neden PID sayılmaz?

Potansiyel kaynaklı bozulma, PV modül hücreleri ile topraklanmış çerçeve veya çevre arasındaki yüksek sistem gerilimi ve kaçak yollarıyla ilişkili performans kaybı mekanizmalarını kapsar. IEC TS 62804-1:2025, kristal silisyum modüllerde PID-shunting, PID-polarization ve recovery davranışlarını ayrı test yöntemleriyle ele alır; gerçek dayanımın çevre ve modülün toprağa göre gerilimine bağlı olduğunu vurgular.

Aynı üretim kaybını kirlenme, gölgelenme, kablo veya konektör direnci, bypass diyot arızası, sıcaklık kaynaklı güç düşümü, inverter clipping ve MPPT mismatch de oluşturabilir. Bu nedenle yalnız aylık kWh düşüşü veya tek termal görüntüyle PID teşhisi konulmamalıdır.

- Modül teknolojisi, string polaritesi ve toprağa göre gerilim konumunu kaydedin.
- Kayıp başlangıcını hava, temizlik ve sistem değişiklikleriyle eşleştirin.
- Benzer stringleri aynı ışınım ve sıcaklık koşulunda karşılaştırın.
- Önce kirlenme, gölgelenme ve bağlantı arızası gibi yaygın nedenleri eleyin.

_Kaynaklar: S1, S3_

## Sahada PID şüphesi için hangi karşılaştırmalı veriler toplanmalıdır?

İlk aşamada inverter ve string izleme verileri ışınım, modül sıcaklığı, çalışma gerilimi ve temizlik durumu ile normalize edilmelidir. Aynı modül ve yönelimdeki referans stringlerle akım, gerilim, günlük özgül üretim ve gece izolasyon davranışı karşılaştırılmalıdır. Sorunun negatif veya pozitif kutba yakın modüllerde yoğunlaşıp yoğunlaşmadığı sistem gerilimi etkisini anlamaya yardım eder.

İzolasyon alarmı PID ile aynı şey değildir; yalıtım kusuru ayrı bir güvenlik arızasıdır ve öncelikle üretici prosedürüyle ele alınmalıdır. PID bazı mekanizmalarda görünür hasar bırakmadan güç kaybı oluşturabilir. Saha kanıtı zaman serisi ve konumsal desen içermelidir.

- String akım ve gerilimlerini aynı MPPT ve çevre koşulunda karşılaştırın.
- Işınım ve modül sıcaklığını üretim verisine ekleyin.
- Kayıp desenini string boyunca modül konumuyla eşleştirin.
- İzolasyon alarmını ayrı ve öncelikli güvenlik olayı olarak yönetin.

_Kaynaklar: S1, S3_

## I-V, elektrolüminesans ve termal ölçümler nasıl birlikte kullanılır?

I-V eğrisi kısa devre akımı, açık devre gerilimi, doluluk faktörü ve maksimum güçteki değişimin şeklini gösterir; fakat tek başına bütün bozunma mekanizmalarını ayıramaz. NREL’in modül bozulması karakterizasyonu çalışmaları elektrolüminesans, fotolüminesans ve lock-in termografi gibi görüntüleme yöntemlerinin modül içindeki konumsal kusurları ortaya çıkarmada tamamlayıcı olduğunu gösterir.

PID mekanizmasına göre EL kararması, şönt benzeri davranış veya polarizasyon etkileri farklı görünebilir. Ölçüm koşulları, cihaz kalibrasyonu, modül sıcaklığı ve ışınım kaydedilmeden önce-sonra kıyaslaması güvenilir olmaz. Laboratuvar PID stres testi saha modülüne doğrudan uygulanacak kullanıcı testi değildir.

- I-V eğrisini kalibre edilmiş ışınım ve sıcaklık verisiyle alın.
- EL veya uygun görüntülemeyi string performans verisiyle eşleştirin.
- Termal bulguyu konektör, diyot ve gölgelenme arızalarından ayırın.
- Yüksek DC gerilimli ölçümleri yalnız yetkin ekip ve uygun cihazla yapın.

_Kaynaklar: S1, S4_

## Modül sertifikası ve sistem topolojisi PID riskini nasıl etkiler?

IEC 61215-1-1:2021 kristal silisyum modüller için PID tespit testini MQT 21 olarak tasarım yeterlilik paketine ekler; ancak test sonucunun nicel bir saha ömrü tahmini olmadığını da belirtir. Sertifikadaki modül varyantı, BOM ve test kapsamı sahadaki gerçek ürünle eşleştirilmelidir.

İnverter topolojisi, galvanik izolasyon, sistemin topraklama yaklaşımı, maksimum DC gerilim, modül teknolojisi, sıcaklık ve nem PID stresini etkileyebilir. Sisteme anti-PID cihazı veya gece ters gerilim uygulaması eklemeden önce modül ve inverter üreticisinin izinleri, güvenlik ve garanti koşulları doğrulanmalıdır.

- Sertifika raporundaki modül varyantını sahadaki etiketle eşleştirin.
- Toprağa göre en olumsuz modül gerilimini tek hat üzerinden belirleyin.
- İnverter ve modül üreticisinin PID azaltma veya recovery talimatını doğrulayın.
- Uyumsuz anti-PID cihazını yalnız satış iddiasına dayanarak eklemeyin.

_Kaynaklar: S1, S2, S3_

## PID onarımı veya iyileştirmesi sonrasında hangi kabul dosyası hazırlanmalıdır?

Kabul dosyası başlangıç semptomu, referans ve şüpheli string karşılaştırması, temizlik ve gölgelenme kontrolü, I-V ve görüntüleme sonuçları, izolasyon ölçümü, sistem gerilimi-toprak ilişkisi, modül sertifikası, üretici görüşü ve uygulanan düzeltmeyi içermelidir. Düzeltme sonrası sonuç aynı mevsim ve ölçüm koşullarına mümkün olduğunca yakın biçimde tekrar ölçülmelidir.

Bazı PID mekanizmalarında recovery mümkün olsa da her güç kaybı tamamen geri dönmez ve aynı çözüm tüm teknolojilere uygulanamaz. Kanıt PID olmadığını gösterirse anti-PID cihazı veya toplu modül değişimi yapılmaması geçerli sonuçtur. Sorun doğrulanırsa iyileştirme sonrası uzun dönem string trendiyle tekrarlama riski izlenmelidir.

- Önce-sonra I-V ve özgül üretimi aynı koşullara normalize edin.
- Uygulanan cihaz veya ayarın üretici onayını dosyalayın.
- İzolasyon ve koruma fonksiyonlarını düzeltme sonrası yeniden test edin.
- PID kanıtlanmadıysa gereksiz modül veya anti-PID cihazı satın almayın.

_Kaynaklar: S1, S2, S3, S4_

## Sık sorulan sorular

### PID gözle bakarak anlaşılır mı?

Çoğu durumda hayır. Görünür bir iz olmayabilir; string performansı, I-V eğrisi, EL veya uygun görüntüleme, sistem gerilimi ve diğer kayıp nedenlerinin elenmesi birlikte gerekir.

_Kaynaklar: S1, S4_

### İnverter izolasyon hatası PID olduğu anlamına gelir mi?

Hayır. İzolasyon hatası ayrı bir elektrik güvenliği problemidir ve öncelikle üretici prosedürüyle giderilmelidir. PID şüphesi ancak ek performans ve karakterizasyon kanıtlarıyla değerlendirilir.

_Kaynaklar: S1, S3_

### PID hasarı tamamen geri döndürülebilir mi?

Mekanizmaya, modül teknolojisine ve hasarın seviyesine bağlıdır. IEC 62804-1 bazı polarizasyon türleri için recovery testi içerir; bu, her saha modülünün tamamen iyileşeceği garantisi değildir.

_Kaynaklar: S1, S3_

### Anti-PID cihazı her GES için gerekli midir?

Hayır. Önce PID kanıtlanmalı, modül ve inverter uyumu ile sistem topolojisi doğrulanmalıdır. Mevcut sistemde sorun yoksa veya kaybın nedeni başka ise cihaz eklemek gereksiz ve riskli olabilir.

_Kaynaklar: S1, S2, S3_

## İnsan onay komutu

PR sahibinin veya repository yetkilisinin yorumu:

```text
/cms approve ges-panel-pid-potansiyel-kaynakli-bozulma-teshis
```

Onay iş akışı kalite puanı, kaynak güncelliği, iç linkler, kanibalizasyon ve risk sınırlarını yeniden çalıştırmadan canonical dosya üretmez.
