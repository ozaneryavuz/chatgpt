# ALO186 AI CMS inceleme paketi — aktif-harmonik-filtre-ct-yonu-kompanzasyon-kabul-testi

> Bu dosya canonical yayına dahil edilmez. PR incelemesi ve insan onayı için üretilmiştir.

## Durum

- State: **approved**
- Risk: **high**
- Model: **gpt-5.6-thinking**
- Kalite: **100/100**
- Benzerlik: **0.42** — https://alo186.com/haberler/aktif-harmonik-filtre-ct-yonu-faz-eslesmesi-devreye-alma
- Kelime: **977**

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

- **S1 · IEC** — [IEC 61000-4-7:2002+A1:2008 — Harmonics and interharmonics measurement](https://webstore.iec.ch/en/publication/4228) — erişim 2026-08-03 — birincil
- **S2 · IEC** — [IEC 61000-4-30:2025 — Power quality measurement methods](https://webstore.iec.ch/en/publication/71611) — erişim 2026-08-03 — birincil
- **S3 · Schneider Electric** — [PowerLogic AccuSine PCS+, PFV+, and PCSn User Manual](https://www.se.com/uk/en/download/document/JYT20814EN/) — erişim 2026-08-03 — birincil
- **S4 · Schneider Electric** — [PowerLogic AccuSine Firmware User Manual](https://www.se.com/us/en/download/document/PKR30257EN/) — erişim 2026-08-03 — birincil
- **S5 · Schneider Electric** — [AccuSine+ User Manual](https://www.se.com/us/en/download/document/13172409/) — erişim 2026-08-03 — birincil
- **S6 · Schneider Electric** — [Load required to commission an AccuSine unit](https://www.se.com/us/en/faqs/FA361328/) — erişim 2026-08-03 — birincil

## SEO

- Title: `Aktif Harmonik Filtre CT Yönü Testi ve Kabulü`
- H1: `Aktif harmonik filtre CT yönü testi ve kompanzasyon performansı nasıl doğrulanır?`
- Description: `AHF devreye almada CT yönü, faz eşleşmesi, PCC ölçümü, filtre akımı ve harmonik iyileşmesini yük seviyelerine göre kanıtlayın.`
- Canonical: `/haberler/aktif-harmonik-filtre-ct-yonu-kompanzasyon-kabul-testi`
- Birincil anahtar kelime: `aktif harmonik filtre CT yönü testi`

## Doğrudan cevap

Aktif harmonik filtre yalnız HMI'da çalışıyor görünmesiyle kabul edilmez. CT'ler doğru faz, yön, oran ve ölçüm noktasında olmalı; filtre kapalı ve açık durumda aynı yük koşulunda tekil harmonikler, THDi/THDv, nötr akımı, güç faktörü ve filtre çıkış akımı karşılaştırılmalıdır. Haberleşme, paralel modül ve termal sınırlar da test edilmelidir. Enerjili CT ve pano bağlantıları yalnız yetkin ekipçe, üretici şeması ve ölçüm planıyla doğrulanmalıdır.

## Aktif harmonik filtre için CT ölçüm sınırı nasıl seçilmelidir?

Aktif harmonik filtre, CT'lerin gördüğü yük akımındaki hedef bileşenleri ölçüp ters fazlı kompanzasyon akımı üretir. CT ana bağlantı noktasında, yalnız belirli bir yük grubunda veya filtrenin kaynak tarafında olabilir; her yerleşim farklı yükleri kapsar. Tek hat üzerinde CT konumu, yük tarafı, kaynak tarafı, filtre bağlantı noktası ve paralel kondansatör bankları açıkça işaretlenmeden performans kabulü yapılamaz.

Üretici devreye alma kılavuzları CT seçimi, bağlantısı, otomatik veya manuel CT yapılandırması ve sistem bütünlük testini temel adımlar olarak tanımlar. CT'lerin filtre akımını yanlışlıkla yeniden ölçmesi kontrol döngüsü oluşturabilir; filtre dışında kalan yük ise telafi edilmez. Bu nedenle ölçüm sınırı, hedef PCC ve raporlanan harmonik kriteri aynı noktayı temsil etmelidir.

- Tek hatta CT, AHF, yükler, kondansatör bankı ve PCC konumlarını gösterin.
- Source-side ve load-side CT seçimini üretici şemasına göre doğrulayın.
- Filtre çıkış akımının CT tarafından yanlış geri beslenmediğini kontrol edin.
- CT sekonderine enerjili durumda kullanıcı müdahalesi önermeyin.

_Kaynaklar: S3, S4, S5_

## CT yönü, faz eşleşmesi ve oran hatası nasıl anlaşılır?

Ters CT yönü veya yanlış faz eşleşmesi, filtrenin azaltması gereken harmonik akımı büyütmesine, reaktif gücü yanlış yönde sürmesine veya aşırı akım alarmı vermesine neden olabilir. Her CT'nin P1/P2 yönü, faz etiketi, sekonder oranı ve HMI kanal eşleşmesi kontrollü faz yükü ve analizör kaydıyla doğrulanmalıdır. Yalnız toplam THDi ekranına bakmak hatalı fazı gizleyebilir.

Otomatik CT algılama işlevi varsa sonuç fiziksel etiket ve bağımsız ölçümle karşılaştırılmalıdır. İthalat-ihracat işareti, kapasitif-endüktif yön ve nötr akımı dört iletkenli sistemlerde ayrıca kontrol edilir. CT oranı çok yüksek seçilirse düşük yükte çözünürlük yetersiz kalabilir; çok düşük seçilirse beklenen yükte doygunluk veya ölçüm sınırı sorunu oluşabilir.

- Her CT için faz, yön, oran ve terminal numarasını kabul tablosuna yazın.
- Tek fazlı kontrollü yük değişimiyle doğru kanalın beklenen yönde tepki verdiğini doğrulayın.
- Otomatik CT tanımasını fiziksel bağlantı ve bağımsız analizörle karşılaştırın.
- Yanlış yönü yazılım işaretiyle örtmeden önce üretici prosedürünü izleyin.

_Kaynaklar: S3, S4, S5_

## AHF öncesi ve sonrası harmonik performans nasıl ölçülmelidir?

Filtre kabulü yalnız THDi yüzdesinin bir an için düşmesiyle verilmez. Aynı yük ve işletme koşulunda filtre kapalı ve açık kayıtları; faz akımları, THDi, tekil harmonikler, THDv, güç faktörü, kW, kVAr, nötr akımı ve filtre çıkış akımıyla birlikte karşılaştırılmalıdır. Yük profili değişiyorsa sonuçlar eşdeğer zaman dilimleri veya kontrollü yük senaryolarıyla normalleştirilmelidir.

IEC 61000-4-7 harmonik ve interharmonik ölçüm cihazı ve gruplama yaklaşımını, IEC 61000-4-30:2025 ise saha güç kalitesi parametrelerinin tekrarlanabilir ölçüm yöntemlerini tanımlar. Bu standartlar tek başına tesis için kabul sınırı vermez; ölçüm yöntemini standardize eder. Geçti-kaldı hedefi proje, bağlantı noktası, ekipman dayanımı ve uygulanabilir şebeke şartlarıyla önceden yazılmalıdır.

- Filtre kapalı/açık kayıtlarını aynı yük koşulunda alın.
- THDi yanında tekil harmonikler, THDv, nötr akımı ve güç faktörünü izleyin.
- Ölçüm sınıfı, CT oranı, örnekleme ve agregasyon aralığını rapora ekleyin.
- Standart ölçüm yöntemini evrensel emisyon limiti gibi sunmayın.

_Kaynaklar: S1, S2, S3_

## Düşük yükte iyi görünen filtre tam yükte neden yetersiz kalabilir?

AHF'nin gerekli kompanzasyon akımı yük seviyesine ve harmonik spektruma bağlıdır. Düşük yükte filtre akımı küçükken THDi yüzdesi değişken olabilir; tam üretim veya yoğun işletmede cihaz akım limitine ulaşabilir, bazı harmonikleri önceliklendirebilir veya termal derating yaşayabilir. Bu nedenle yalnız gece ya da kısmi yük devreye alma sonucu bütün tesis için yeterli değildir.

Schneider Electric devreye alma açıklaması, mümkünse beklenen yükün en az yarısının bulunmasını ve tam sistem entegrasyonu için desteklenen yüklerin çalıştırılmasını önerir; filtre çıkış akımının da anlamlı bir seviyeye ulaşması gerekir. Bu üretici örneği evrensel yüzde değildir, fakat kabul testinin gerçek yük spektrumunu temsil etmesi gerektiğini gösterir. Paralel AHF modüllerinde akım paylaşımı ayrıca izlenmelidir.

- Düşük, tipik ve en yüksek makul yük seviyelerinde test yapın.
- Filtre çıkış akımı, kapasite yüzdesi ve termal derating olaylarını kaydedin.
- Paralel modüllerde akım paylaşımı ve bir modül kaybı davranışını doğrulayın.
- Kısmi yük sonucunu tam yük performans garantisi saymayın.

_Kaynaklar: S3, S4, S6_

## Aktif harmonik filtre kabul dosyası hangi verileri içermelidir?

Teslim dosyasında tek hat, PCC ve CT konumu, CT faz-yön-oran matrisi, AHF tam model ve firmware, kompanzasyon modları, hedef harmonikler, akım limiti, paralel modül ayarları, filtre kapalı/açık güç kalitesi trendleri, termal kayıtlar, olay günlüğü ve geçti-kaldı kriterleri bulunmalıdır. Ölçüm cihazı ve CT kalibrasyon bilgileri de saklanmalıdır.

Geçti sonucu; doğru CT geri bildirimi, kararlı kontrol, tanımlı yük aralığında hedef harmonik ve güç faktörü iyileşmesi, filtre akımının kapasite/termal sınır içinde kalması ve kompanzasyon panosuyla rezonans oluşturmamasıyla verilmelidir. CTA: kişisel verisiz CT–PCC–harmonik–filtre akımı–termal kabul matrisi hazırlayın; kanıt yeterliyse gereksiz ek AHF kapasitesi veya kondansatör değişimi satın almayın.

- CT ve AHF parametre yedeğini teslim dosyasına ekleyin.
- Öncesi-sonrası ölçümü ortak yük ve zaman koşuluyla karşılaştırın.
- Alarm, kapasite sınırı ve termal sonuçları ayrı geçti-kaldı satırlarında gösterin.
- Sistem hedefi sağlıyorsa yalnız THDi korkusuyla cihaz büyütmeyin.

_Kaynaklar: S1, S2, S3, S4, S5, S6_

## Sık sorulan sorular

### Aktif harmonik filtre açılınca THDi neden düşmeyebilir?

Yanlış CT yönü/fazı, hatalı ölçüm noktası, yetersiz yük, filtre akım limiti, yanlış hedef harmonikler veya rezonans etkisi olabilir. Filtre kapalı-açık kayıtları aynı yükte karşılaştırılmalıdır.

_Kaynaklar: S3, S4, S5_

### CT yönü tersse filtre zarar verir mi?

Yanlış geri bildirim kompanzasyonu yanlış yönde sürerek harmonikleri veya reaktif akımı artırabilir ve alarm oluşturabilir. Cihaz üretici prosedürüne göre güvenli biçimde durdurulup bağlantı doğrulanmalıdır.

_Kaynaklar: S3, S4, S5_

### AHF kabulünde yalnız THDi yeterli midir?

Hayır. Tekil harmonikler, THDv, nötr akımı, güç faktörü, yük seviyesi, filtre çıkış akımı, termal durum ve PCC hedefi birlikte değerlendirilmelidir.

_Kaynaklar: S1, S2, S3_

### Aktif filtre varsa detuned reaktör kaldırılır mı?

Otomatik olarak hayır. Kondansatör bankı, rezonans, reaktif güç ihtiyacı ve AHF kontrol modu birlikte mühendislik analizi gerektirir; mevcut koruma ve reaktörler kanıtsız sökülmemelidir.

_Kaynaklar: S3, S4, S5_

## İnsan onay komutu

PR sahibinin veya repository yetkilisinin yorumu:

```text
/cms approve aktif-harmonik-filtre-ct-yonu-kompanzasyon-kabul-testi
```

Onay iş akışı kalite puanı, kaynak güncelliği, iç linkler, kanibalizasyon ve risk sınırlarını yeniden çalıştırmadan canonical dosya üretmez.
