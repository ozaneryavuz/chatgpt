# ALO186 AI CMS inceleme paketi — ups-aku-runtime-kalibrasyon-desarj-kapasite-kabul-testi

> Bu dosya canonical yayına dahil edilmez. PR incelemesi ve insan onayı için üretilmiştir.

## Durum

- State: **approved**
- Risk: **high**
- Model: **gpt-5.6-thinking**
- Kalite: **88/100**
- Benzerlik: **0.33** — https://alo186.com/haberler/ups-aku-ic-direnc-conductance-kapasite-runtime-testi
- Kelime: **1003**

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

- **S1 · IEC** — [IEC 62040-3:2021 — UPS performance and test requirements](https://webstore.iec.ch/en/publication/60140) — erişim 2026-08-03 — birincil
- **S2 · IEEE** — [IEEE 1188-2025 — Maintenance, Testing, and Replacement of VRLA Batteries](https://standards.ieee.org/ieee/1188/11656/) — erişim 2026-08-03 — birincil
- **S3 · IEEE** — [IEEE 450-2020 — Maintenance, Testing, and Replacement of Vented Lead-Acid Batteries](https://standards.ieee.org/ieee/450/6772/) — erişim 2026-08-03 — birincil
- **S4 · IEEE** — [IEEE 2962-2025 — Stationary Lithium-ion Battery Installation, Operation, Maintenance and Testing](https://standards.ieee.org/ieee/2962/10402) — erişim 2026-08-03 — birincil
- **S5 · Schneider Electric** — [Galaxy VS — Start a Runtime Calibration Test](https://www.productinfo.schneider-electric.com/galaxyvs_ul/990-5910_master-galaxy-vs-operation/990-5910B%20Galaxy%20VS%20Operation/English/990-5910%20Operation%20manual%20Galaxy%20VS_0000153852.xml/%24/StartaRuntimeCalibrationTestTSK_0000153868) — erişim 2026-08-03 — birincil

## SEO

- Title: `UPS Akü Runtime Kalibrasyonu ve Deşarj Kapasite Kabul Testi`
- H1: `UPS akü çalışma süresi gerçek mi, runtime kalibrasyonu nasıl kabul edilir?`
- Description: `UPS akü çalışma süresini kısa öz-testten ayırın; kontrollü deşarj, yük, sıcaklık, hücre gerilimi ve yeniden şarj kanıtıyla kabul edin.`
- Canonical: `/haberler/ups-aku-runtime-kalibrasyon-desarj-kapasite-kabul-testi`
- Birincil anahtar kelime: `UPS akü runtime kalibrasyon testi`

## Doğrudan cevap

UPS'nin 'akü testi geçti' mesajı gerçek çalışma süresini tek başına kanıtlamaz. Kısa öz-test bağlantı, sigorta ve belirgin zayıflıkları arayabilir; runtime kalibrasyonu veya kapasite testi ise tanımlı ve kararlı yük altında aküyü üreticinin belirlediği son gerilim ya da düşük DC uyarı seviyesine kadar kontrollü deşarj ederek geçen süreyi hesaplar. Test öncesinde tam şarj, bypass ve alternatif güç, alarm durumu, yük kararlılığı, sıcaklık ve acil durdurma planı doğrulanmalı; test sonrasında yeniden şarj tamamlanana kadar yedekleme riski açıkça yönetilmelidir. Enerjili DC barası ve akü bağlantılarında işlem yalnız yetkin ekipçe yapılmalıdır.

## Kısa akü testi, runtime kalibrasyonu ve kapasite testi aynı mıdır?

Hayır. UPS'nin kısa otomatik testi çoğu modelde akü bağlantısını, sigorta durumunu veya belirgin zayıf aküyü sınırlı bir deşarjla kontrol eder. Bu testin başarılı olması, tesisin hedeflenen dakika boyunca gerçek yükü taşıyacağını göstermez. Runtime kalibrasyonu, yük bilgisi ve geçen süreyle UPS'nin kalan süre tahminini düzeltmeyi amaçlar; tam kapasite testi ise akü kimyasına, üretici prosedürüne ve kabul standardına göre daha kapsamlıdır.

IEC 62040-3 bütün UPS'nin performans ve test çerçevesini tanımlar. Sabit VRLA, sulu kurşun-asit ve lityum sistemlerin bakım ve kapasite testleri aynı prosedür değildir; IEEE 1188, IEEE 450 ve IEEE 2962 ilgili kimyalar için ayrı kapsamlar sunar. Kabul dosyasında akü tipi, blok/hücre sayısı, yaş, nominal Ah, tasarım süresi ve uygulanacak test yöntemi açıkça belirtilmelidir.

- Öz-test sonucunu dakika cinsinden kapasite kanıtı saymayın.
- Akü kimyasını ve üretici prosedürünü testten önce doğrulayın.
- Kalibrasyon ile resmi kapasite testinin amacını ayrı yazın.
- Hedef runtime ve geçti-kaldı sınırını test başlamadan belirleyin.

_Kaynaklar: S1, S2, S3, S4, S5_

## Runtime kalibrasyonu öncesinde hangi güvenlik koşulları sağlanmalıdır?

Test akü enerjisini bilinçli olarak azaltır. Şebeke aynı anda kesilirse UPS kritik yükü beklenen süre taşımayabilir. Bu nedenle bypass kaynağı veya bağımsız alternatif besleme, jeneratör hazır oluşu, bakım penceresi, kritik alarm bulunmaması, akülerin tam şarjı ve yükün kararlı kalacağı doğrulanır. Schneider'in model dokümanı örneğinde tam şarj, bypass kullanılabilirliği, asgari yük ve sınırlı yük değişimi ön koşuldur; bu değerler başka modele kopyalanmamalıdır.

Testten önce blok sıcaklıkları, şişme-sızıntı, gevşek bağlantı, DC kesici, sigorta ve string gerilimleri kontrol edilir. Aşırı sıcak, hasarlı veya dengesiz string kontrollü deşarja alınmaz. Testin durdurma koşulları; minimum blok gerilimi, sıcaklık, alarm, ani kapasite düşüşü, yük değişimi ve alternatif kaynak kaybı olarak yazılı hale getirilir.

- Şebeke kesintisi olasılığına karşı alternatif güç planı hazırlayın.
- Tam şarj ve kararlı yük koşulunu model kılavuzuyla doğrulayın.
- Hasarlı veya sıcak aküde kapasite testi başlatmayın.
- Durdurma ve kritik yük geri dönüş adımlarını önceden onaylayın.

_Kaynaklar: S2, S3, S4, S5_

## Deşarj sırasında hangi ölçümler ve süre hesabı tutulmalıdır?

Başlangıçta UPS çıkış kW/kVA, güç faktörü, akü DC gerilimi ve akımı, blok/hücre sıcaklıkları, SoC tahmini ve ortam kaydedilir. Deşarj boyunca ortak zaman tabanında UPS yükü, toplam DC gerilim-akım, her string ve mümkünse blok gerilimleri, sıcaklık, alarm ve düşük gerilim olayları izlenir. Yük değişirse runtime karşılaştırması yanıltıcı olur; değişim toleransı ve testin geçerlilik kuralı önceden tanımlanmalıdır.

Geçen süre doğrudan etiket Ah ile karşılaştırılmaz. Deşarj oranı, son gerilim, sıcaklık düzeltmesi, yaş ve üretici eğrileri dikkate alınır. Tek bir zayıf blok toplam string gerilimi normal görünürken erken çökmeye neden olabilir. Sonuçta hem gerçek dakika hem de kapasite yüzdesi yöntemi, kullanılan referans ve ölçüm belirsizliğiyle birlikte raporlanmalıdır.

- UPS yükü ve DC ölçümlerini aynı zaman damgasıyla kaydedin.
- String ve blok davranışını yalnız toplam gerilime indirgemeyin.
- Sıcaklık ve deşarj oranı düzeltmesini kaynakla belirtin.
- Test geçerliliğini bozan yük değişimini rapordan gizlemeyin.

_Kaynaklar: S2, S3, S4, S5_

## Test bittikten sonra UPS ne zaman yeniden tam yedeklemeye hazır sayılır?

Kalibrasyon tamamlandığında aküler düşük kapasitede olabilir. UPS normal moda dönse bile hedef runtime hemen geri gelmez. Şarj akımı, DC gerilimi, sıcaklık, şarj limiti ve tahmini tam dolum süresi izlenir; kritik yük için risk penceresi işletmeye bildirilir. Jeneratör veya ikinci UPS modülü bulunması, akülerin yeniden şarj olduğunu varsaymak için yeterli değildir.

Tekrarlanan derin kalibrasyonlar akü ömrünü etkileyebilir. Schneider, runtime kalibrasyonunu devreye alma, akü değişimi veya batarya çözümü değişikliği gibi belirli durumlarda önerir ve tekrarlı testlerin ömrü etkileyebileceğini belirtir. Periyot, UPS ekranının varsayılan takviminden değil üretici, akü standardı, tesis kritiklik sınıfı ve geçmiş sonuçlardan belirlenmelidir.

- Test sonrası düşük rezerv süresini operasyon ekibine bildirin.
- Tam şarj kriterini yalnız SoC yüzdesine bağlamayın.
- Şarj akımı, sıcaklık ve alarm trendini kapanışa ekleyin.
- Gereksiz sık derin deşarj kalibrasyonu yapmayın.

_Kaynaklar: S2, S3, S4, S5_

## UPS akü runtime testi hangi kabul dosyasıyla kapatılmalıdır?

Dosyada UPS modeli ve firmware, akü kimyası, üretici/model, string-blok sayısı, yaş, nominal kapasite, tasarım runtime, tek hat, DC koruma, bakım bulguları, test yöntemi, başlangıç şarjı ve sıcaklık, yük profili, deşarj trendi, sonlandırma nedeni, minimum blok değerleri, gerçek süre, düzeltilmiş kapasite, alarm kaydı ve yeniden şarj tamamlanma zamanı bulunmalıdır. Ham CSV veya olay logu özet sonuçla birlikte saklanmalıdır.

Kısa test başarılı fakat runtime yetersizse yalnız tüm aküleri topluca değiştirmeden önce zayıf blok, bağlantı, şarj, sıcaklık, yanlış yük tahmini ve kapasite yaşlanması ayrılmalıdır. Runtime hedefi karşılanıyor ve string dengesi uygunsa sırf yaş takvimi nedeniyle gereksiz değişim yapılmamalıdır; ancak üretici ve güvenlik sınırları korunur. CTA: kişisel verisiz UPS yük–DC akım–blok gerilimi–sıcaklık–runtime kabul matrisini yetkin UPS/akü ekibine iletin.

- Öz-test, kalibrasyon ve kapasite sonucu için ayrı geçti-kaldı satırı açın.
- Minimum blok gerilimi ve erken çöken stringi görünür kılın.
- Yeniden şarj tamamlanmadan bakım kapanışı vermeyin.
- Kanıt yeterliyse gereksiz toplu akü değişimi satın almayın.

_Kaynaklar: S1, S2, S3, S4, S5_

## Sık sorulan sorular

### UPS akü testi geçtiyse çalışma süresi kesin yeterli midir?

Hayır. Kısa öz-test bağlantı ve belirgin zayıflıkları kontrol edebilir; gerçek dakika için kararlı yük altında runtime kalibrasyonu veya uygun kapasite testi gerekir.

_Kaynaklar: S1, S5_

### Runtime kalibrasyonu sırasında elektrik kesilirse ne olur?

Aküler test nedeniyle düşük seviyeye inebilir ve yükü hedef süre taşıyamayabilir. Bu yüzden bypass/alternatif güç, bakım penceresi ve acil durdurma planı ön koşuldur.

_Kaynaklar: S5_

### UPS aküsü yüzde kaç kapasitede değiştirilir?

Tek bir evrensel yüzde tüm kimya ve kritik tesisler için geçerli değildir. İlgili IEEE/üretici kriteri, hedef runtime, zayıf bloklar, güvenlik ve işletme riski birlikte değerlendirilir.

_Kaynaklar: S2, S3, S4_

### Runtime kalibrasyonu ne sıklıkla yapılmalıdır?

Model, akü kimyası, kritiklik ve geçmiş sonuçlara göre belirlenir. Derin kalibrasyonu gereksiz sık yapmak akü ömrünü etkileyebilir; üretici ve bakım standardı esas alınmalıdır.

_Kaynaklar: S2, S3, S4, S5_

## İnsan onay komutu

PR sahibinin veya repository yetkilisinin yorumu:

```text
/cms approve ups-aku-runtime-kalibrasyon-desarj-kapasite-kabul-testi
```

Onay iş akışı kalite puanı, kaynak güncelliği, iç linkler, kanibalizasyon ve risk sınırlarını yeniden çalıştırmadan canonical dosya üretmez.
