# ALO186 AI CMS inceleme paketi — ups-aku-kapasite-testi-ic-direnc-runtime-kabul

> Bu dosya canonical yayına dahil edilmez. PR incelemesi ve insan onayı için üretilmiştir.

## Durum

- State: **approved**
- Risk: **high**
- Model: **gpt-5.6-thinking**
- Kalite: **88/100**
- Benzerlik: **0.47** — https://alo186.com/haberler/ups-aku-kapasite-testi-self-test-desarj-farki
- Kelime: **969**

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

- **S1 · IEEE Standards Association** — [IEEE 1188-2025 — VRLA Batteries for Stationary Applications](https://standards.ieee.org/ieee/1188/11656/) — erişim 2026-08-03 — birincil
- **S2 · Schneider Electric** — [Perform a Manual Self-Test on an Easy UPS](https://www.se.com/us/en/faqs/FAQ000265292/) — erişim 2026-08-03 — birincil
- **S3 · Schneider Electric** — [How to perform self-test on Back-UPS products?](https://www.se.com/us/en/faqs/FAQ000281733/) — erişim 2026-08-03 — birincil
- **S4 · Schneider Electric** — [Runtime Test on UPS SRT Series](https://www.se.com/id/id/faqs/FAQ000223475/) — erişim 2026-08-03 — birincil

## SEO

- Title: `UPS Akü Kapasite Testi: Self-Test, İç Direnç ve Runtime`
- H1: `UPS aküsünün gerçek kapasitesi self-test, iç direnç ve runtime testiyle nasıl doğrulanır?`
- Description: `UPS aküsünün gerçek kapasitesini kısa self-test, iç direnç trendi ve kontrollü runtime testiyle ayırın; değişim kararını kanıt dosyasına bağlayın.`
- Canonical: `/haberler/ups-aku-kapasite-testi-ic-direnc-runtime-kabul`
- Birincil anahtar kelime: `UPS akü kapasite testi runtime iç direnç`

## Doğrudan cevap

UPS’nin 10 saniyelik self-testi veya tek seferlik iç direnç ölçümü akünün gerçek kullanılabilir kapasitesini tek başına kanıtlamaz. Self-test hızlı bir tarama, iç direnç ve blok gerilimleri ise eğilim göstergesidir; hedef yükü belirtilen son gerilime kadar güvenle taşıyıp taşıyamadığını doğrulayan esas kanıt kontrollü runtime veya kapasite testidir. Test öncesinde tam şarj, gerçekçi yük, yedekleme planı ve kesintisiz yük güvenliği sağlanmalı; süre, akım, sıcaklık, toplam ve blok gerilimleri aynı zaman çizelgesinde kaydedilmelidir.

## Self-test, iç direnç ve kapasite testi aynı şeyi mi ölçer?

UPS self-testi cihazın kısa süreli olarak bataryaya geçip iç devreleri ve akü davranışını taramasını sağlar. Schneider Electric’in Easy UPS ve Back-UPS açıklamalarında testin yaklaşık 10 saniye sürdüğü, tam şarj ve uygun yük koşulunun sonucu etkilediği belirtilir. Bu test kötü bağlantı, belirgin zayıflık veya yetersiz tahmini runtime için yararlı olsa da uzun süreli yük taşıma kapasitesini doğrudan ölçmez.

İç direnç, blok gerilimi, ripple ve sıcaklık ölçümleri zayıf hücre veya blokları erken bulmak için değerlidir. Ancak cihaz markası, ölçüm yöntemi, sıcaklık ve geçmiş değerler bilinmeden tek bir evrensel iç direnç sınırı kullanmak hatalı değişim kararına yol açabilir. IEEE 1188 yaklaşımı bakım, test ve değişim kararını bir test programı içinde ele alır.

- Kısa self-testi hızlı tarama olarak sınıflandırın.
- İç direnci aynı cihaz ve benzer sıcaklıkta geçmiş trendle karşılaştırın.
- Blok gerilim farkını yük öncesi ve yük altında ayrı kaydedin.
- Gerçek kapasite iddiasını kontrollü deşarj veya runtime kanıtına bağlayın.

_Kaynaklar: S1, S2, S3_

## Runtime veya kapasite testi öncesinde hangi güvenlik koşulları sağlanmalıdır?

Akü testi, UPS’nin kritik yükü kaybetme riskini artırabilir. Testten önce şebeke, bypass, ikinci UPS, jeneratör veya planlı bakım penceresi gibi yedekleme katmanı doğrulanmalıdır. UPS’nin alarm geçmişi, akü bağlantıları, sigorta ve kesicileri, kabin sıcaklığı, şarj durumu ve bağlı yük yüzdesi kayıt altına alınmadan test başlatılmamalıdır.

Üretici self-test ve runtime talimatları tam şarjı ve asgari yükü ön koşul olarak gösterebilir. Bununla birlikte yük oranı ve test yöntemi model bazında değişir; genel bir yüzdeyi bütün UPS’lere uygulamak yerine cihaz kılavuzu esas alınmalıdır. Akü arkı, yüksek kısa devre akımı ve ağır blok riski nedeniyle fiziksel bağlantı ve deşarj düzeni yetkin kişilerce kurulmalıdır.

- Kritik yük için geri dönüş ve bypass planını yazılı hale getirin.
- UPS modeli, firmware, akü tipi, yaş, sıcaklık ve son şarj süresini kaydedin.
- Test yükünü ve hedef son gerilimi üretici verisinden belirleyin.
- Enerjili DC bağlantılarına kullanıcı müdahalesi yaptırmayın.

_Kaynaklar: S1, S2, S4_

## Kontrollü deşarj ve runtime kabul planı nasıl hazırlanır?

Test planı hedef yükü, beklenen süreyi, akü üreticisinin son gerilim şartını, ölçüm aralığını ve durdurma kriterlerini önceden tanımlar. Gerçek işletme yükü güvenli değilse kalibre edilmiş yük bankası veya üreticinin desteklediği runtime testi kullanılabilir. Test boyunca UPS çıkış gücü, DC akımı, toplam akü gerilimi, her blok gerilimi ve sıcaklık eş zamanlı kaydedilmelidir.

Yalnız toplam string gerilimi sağlıklı görünürken bir blok hızla çökebilir. Bu nedenle başlangıç, ara noktalar, alarm anı ve test sonundaki blok dağılımı önemlidir. Test sonucu üreticinin beklenen süre veya kapasite eğrisiyle aynı yük ve sıcaklık varsayımları altında karşılaştırılmalı; farklı koşullardaki katalog süresi doğrudan kabul değeri yapılmamalıdır.

- Yük, süre, ölçüm aralığı ve durdurma kriterini testten önce sabitleyin.
- Toplam gerilimin yanında her blok veya modülün gerilimini trendleyin.
- Sıcaklık ve yük değişimini sonuç raporunda görünür tutun.
- Kritik blok son gerilime yaklaşırsa testi güvenli biçimde sonlandırın.

_Kaynaklar: S1, S4_

## İç direnç, süre ve blok dağılımı birlikte nasıl yorumlanır?

Yüksek veya hızla artan iç direnç, yük altında erken gerilim çökmesi, komşu bloklardan belirgin sıcaklık farkı ve hedef runtime’ın karşılanmaması aynı yönde kanıt oluşturur. Buna karşılık tek yüksek ölçüm; gevşek bağlantı, yüzey oksidi, farklı sıcaklık veya ölçüm tekniğinden kaynaklanabilir. Önce bağlantı ve ölçüm tekrarıyla yanlış pozitif olasılığı azaltılmalıdır.

Self-test başarılıyken kontrollü runtime kısa kalabilir; çünkü kısa test yalnız başlangıç davranışını görür. Tersi durumda düşük yükle yapılan self-test hatalı runtime tahmini verebilir. Sonuç, UPS olay kaydı, yük profili, iç direnç trendi ve deşarj eğrisi bir araya getirilerek sınıflandırılmalıdır.

- Tek ölçüm yerine en az iki tarihli trend kullanın.
- Zayıf görünen bloğu bağlantı ve sıcaklık etkisinden ayırın.
- Runtime sonucunu gerçek yük profiliyle karşılaştırın.
- Alarm yokluğunu kapasite garantisi olarak kabul etmeyin.

_Kaynaklar: S1, S2, S3_

## Akü değişim veya kullanıma devam kararı hangi dosyayla verilmelidir?

Kabul dosyası; UPS ve akü kimliği, test öncesi durum, ölçüm cihazı, kalibrasyon bilgisi, yük profili, başlangıç şarjı, ortam sıcaklığı, toplam ve blok gerilim grafikleri, iç direnç trendi, test süresi, durdurma nedeni ve üretici eğrisi karşılaştırmasını içermelidir. Böylece karar yalnız yaş veya alarm yerine izlenebilir kanıta dayanır.

String içinde eski ve yeni blok karıştırmak veya yalnız tek zayıf bloğu değiştirmek bazı sistemlerde dengesizliği büyütebilir; değişim kapsamı üretici talimatı ve sistem mimarisine göre belirlenmelidir. Mevcut akü grubu hedef süreyi güvenli marjla sağlıyorsa sırf takvim yaşı nedeniyle gereksiz değişim yapılmaması da geçerli bir sonuçtur.

- Kararı geçti, şartlı geçti veya kaldı olarak sınıflandırın.
- Bir sonraki test tarihini sonuç ve risk seviyesine göre planlayın.
- Değişim kapsamını UPS ve akü üreticisiyle doğrulayın.
- Yeterli kapasite kanıtlandıysa gereksiz akü satın almayın.

_Kaynaklar: S1, S2, S4_

## Sık sorulan sorular

### UPS self-test başarılıysa aküler kesin olarak sağlam mıdır?

Hayır. Yaklaşık 10 saniyelik self-test belirgin zayıflıkları ve kısa süreli davranışı tarar; hedef yük altında gerçek kullanılabilir kapasiteyi kanıtlamak için kontrollü runtime veya kapasite testi gerekebilir.

_Kaynaklar: S2, S3_

### İç direnç kaç miliohm olunca UPS aküsü değiştirilmelidir?

Bütün marka ve aküler için geçerli tek bir miliohm sınırı yoktur. Aynı cihazla alınmış geçmiş trend, bloklar arası dağılım, sıcaklık, bağlantı durumu ve yük altındaki gerilim davranışı birlikte değerlendirilmelidir.

_Kaynaklar: S1_

### Runtime testi kritik yükü düşürebilir mi?

Yanlış yük, düşük şarj, zayıf blok veya yetersiz geri dönüş planı varsa düşürebilir. Bu nedenle test bakım penceresinde, üretici prosedürü ve doğrulanmış bypass veya yedekleme planıyla yetkin ekip tarafından yürütülmelidir.

_Kaynaklar: S2, S4_

### Bir stringde yalnız zayıf aküyü değiştirmek doğru mudur?

Her zaman değil. Yaş, kapasite ve iç direnç farkı yeni ve eski bloklar arasında dengesizlik oluşturabilir. Değişim kapsamı UPS ve akü üreticisinin kurallarıyla, test kanıtıyla belirlenmelidir.

_Kaynaklar: S1, S2_

## İnsan onay komutu

PR sahibinin veya repository yetkilisinin yorumu:

```text
/cms approve ups-aku-kapasite-testi-ic-direnc-runtime-kabul
```

Onay iş akışı kalite puanı, kaynak güncelliği, iç linkler, kanibalizasyon ve risk sınırlarını yeniden çalıştırmadan canonical dosya üretmez.
