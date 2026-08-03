# ALO186 AI CMS inceleme paketi — dc-hizli-sarj-izolasyon-izleme-imd-ariza-kabul-testi

> Bu dosya canonical yayına dahil edilmez. PR incelemesi ve insan onayı için üretilmiştir.

## Durum

- State: **approved**
- Risk: **high**
- Model: **gpt-5.6-thinking**
- Kalite: **88/100**
- Benzerlik: **0.38** — https://alo186.com/haberler/dc-hizli-sarj-izolasyon-hatasi-imd-arac-istasyon-ayrimi
- Kelime: **887**

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

- **S1 · IEC** — [IEC 61851-23:2023 — DC electric vehicle supply equipment](https://webstore.iec.ch/en/publication/32973) — erişim 2026-08-03 — birincil
- **S2 · IEC** — [IEC 61557-8:2014 — Insulation monitoring devices for IT systems](https://webstore.iec.ch/en/publication/5582) — erişim 2026-08-03 — birincil
- **S3 · IEC** — [IEC 61851-24:2023 — Digital communication for DC charging](https://webstore.iec.ch/en/publication/32582) — erişim 2026-08-03 — birincil
- **S4 · ISO** — [ISO 6469-3:2021 — Electrically propelled road vehicles electrical safety](https://www.iso.org/standard/81746.html) — erişim 2026-08-03 — birincil
- **S5 · Bender** — [ISOMETER isoCHA425HV — insulation monitoring for DC fast charging](https://www.bender.de/en/products/insulation-monitoring/isometer-isocha425hv-with-agh420-1/) — erişim 2026-08-03 — birincil

## SEO

- Title: `DC Hızlı Şarj İzolasyon İzleme ve IMD Kabul Testi`
- H1: `DC hızlı şarj istasyonunda izolasyon hatası ve IMD nasıl test edilir?`
- Description: `DC hızlı şarjda IMD, izolasyon eşiği, kontaktör ve deşarj sırasını güvenli simülasyonla doğrulayın; araç–istasyon kök nedenini ayırın.`
- Canonical: `/haberler/dc-hizli-sarj-izolasyon-izleme-imd-ariza-kabul-testi`
- Birincil anahtar kelime: `DC hızlı şarj izolasyon hatası IMD`

## Doğrudan cevap

DC hızlı şarjda izolasyon izleme cihazı (IMD), toprağa göre yalıtılmış DC+ ve DC− devresinin izolasyon direncini sürekli izler; AC giriş RCD'sinin yerine geçmez. Kabul; IMD ve kuplaj cihazının tam modeli, gerilim ve kaçak kapasitesi sınırları, şarj öncesi öz-test, bilinen test direnciyle güvenli simülasyon, alarm–akım düşürme–kontaktör açma–deşarj sırası ve olay loguyla yapılır. Gerçek DC iletkenini toprağa bağlayarak veya araç bağlıyken rastgele megger kullanarak test yapılmaz.

## DC hızlı şarjda IMD neyi izler, RCD'den farkı nedir?

DC hızlı şarj güç devresi çoğu tasarımda şarj sırasında toprağa göre yalıtılmış bir DC sistem olarak yönetilir. İzolasyon izleme cihazı (IMD), DC+ ve DC− ile toprak arasındaki izolasyon direncini sürekli değerlendirerek ilk izolasyon bozulmasını şarj başlamadan veya şarj sırasında tespit etmeyi amaçlar. RCD ise AC besleme tarafındaki artık akım korumasıdır; aynı arızayı ve aynı devreyi izlemez.

Kabul dosyasında IMD'nin ölçüm noktası, kuplaj cihazı, anma gerilim aralığı, izin verilen sistem kaçak kapasitesi, alarm ve kesme eşikleri ile istasyonun tam güç modülü mimarisi gösterilmelidir. 'İzolasyon kontrolü var' şeklindeki genel satış ifadesi yeterli değildir.

- AC giriş RCD'si ile DC çıkış IMD'sini ayrı koruma katmanları olarak gösterin.
- IMD modelini, kuplaj modülünü ve anma DC gerilim aralığını kaydedin.
- DC+–PE ve DC−–PE ölçüm noktalarını tek hatta işaretleyin.
- Ürün ailesindeki başka varyantın eşik ve sürelerini kullanmayın.

_Kaynaklar: S1, S2, S5_

## Araç bağlanmadan önce izolasyon ön kontrolü nasıl kabul edilir?

DC enerji aktarımı başlamadan önce istasyon, kendi çıkış devresinin ve bağlantı yolunun güvenli durumda olduğunu doğrulamalıdır. Kablo, konnektör, kontaktör, güç modülü ve çıkış filtresinin oluşturduğu doğal kaçak kapasitesi IMD ölçümünü etkileyebilir. Sistem gerilimi yokken ve kontrollü test geriliminde yapılan aşamalar ayrı kaydedilmelidir.

Yetkin ekip, üretici tarafından izin verilen izolasyon test kutusu veya simülatörle bilinen dirençleri uygular; alarm eşiği, tepki süresi, kontaktörün kapama izni ve olay kodunu doğrular. Meger gibi yüksek test gerilimi üreten cihazlar, bağlı elektronik ve araç üzerinde üretici prosedürü olmadan kullanılmamalıdır.

- Şarj öncesi öz-test ve IMD hazır durumunu kaydedin.
- Bilinen test dirençlerini yalnız üretici onaylı simülatörle uygulayın.
- Kontaktör kapama izninin izolasyon sonucuna bağlı olduğunu doğrulayın.
- Araç veya güç elektroniği bağlıyken rastgele megger testi yapmayın.

_Kaynaklar: S1, S2, S5_

## Şarj sırasında izolasyon arızası oluşursa hangi sıra izlenmelidir?

Şarj sırasında asimetrik veya simetrik izolasyon bozulması oluşabilir. Kabul, yalnız alarm LED'inin yanmasını değil; araç-EVSE haberleşmesindeki hata bildirimi, akımın kontrollü düşürülmesi, DC kontaktörlerin açılması, deşarj süresi, konnektör kilidi ve kullanıcı mesajını birlikte kapsamalıdır. Kesme sırası yüksek DC gerilimin konnektörde kalmasını önlemelidir.

IMD'nin tepki süresi ve eşik değeri istasyon mimarisi, gerilim ve kaçak kapasitesine bağlıdır. Üretici örneğindeki süreler evrensel kabul limiti değildir. Gerçek geçti-kaldı sınırı istasyon standardı, uygunluk dosyası ve model dokümanından alınmalıdır.

- IMD alarmı, şarj kontrolü, akım, kontaktör ve DC gerilimi ortak zaman çizelgesinde kaydedin.
- Arıza sonrası konnektör geriliminin güvenli seviyeye düşüşünü doğrulayın.
- Simetrik ve asimetrik arıza senaryolarını ayrı test edin.
- Gerçek DC iletkenini toprağa kısa devre ederek test yapmayın.

_Kaynaklar: S1, S2, S3, S5_

## İzolasyon hatası araçtan mı istasyondan mı kaynaklanıyor?

Aynı hata şarj kablosu veya konnektör nemi, güç modülü, DC bara, filtre, soğutma sıvısı, araç yüksek gerilim sistemi ya da haberleşme/parametre uyumsuzluğundan kaynaklanabilir. Olay kaydı; araç kimliğini kişisel veri toplamadan tip/model düzeyinde, soket, hava koşulu, gerilim, şarj aşaması ve IMD ölçümüyle eşleştirmelidir.

Aynı aracın farklı doğrulanmış istasyonda veya aynı istasyonun üretici test aracıyla karşılaştırılması arıza katmanını daraltabilir; tek başına kesin teşhis değildir. Alarm eşiklerini büyütmek, IMD'yi köprülemek veya tekrar tekrar şarj başlatmak güvenli çözüm değildir.

- Kablo, konnektör, istasyon güç katı ve araç katmanını ayrı inceleyin.
- Nem ve soğutma sıvısı izlerini enerjisiz görsel kontrol planına alın.
- Hata kaydını araç sahibinin kişisel verisini toplamadan saklayın.
- Tekrarlayan izolasyon alarmında şarj noktasını servis dışı bırakın.

_Kaynaklar: S1, S3, S4, S5_

## DC hızlı şarj izolasyon izleme sistemi nasıl teslim alınmalıdır?

Teslim dosyası; tek hat, DC sistem topolojisi, EVSE ve IMD tam referansları, firmware, kuplaj modülü, eşik ve tepki süreleri, doğal kaçak kapasitesi, öz-test, şarj öncesi kontrol, şarj sırasında hata, kontaktör/deşarj sırası, olay logu ve yeniden başlatma koşullarını içermelidir. Her konnektör ve güç modülü ayrı sonuç satırıyla izlenmelidir.

Testler geçtiyse sırf daha yeni bir IMD modeli bulunduğu için değişim gerekmez; fakat yalnız alarmın silinmesi veya tek başarılı şarj kabul kanıtı değildir. CTA: kişisel verisiz DC EVSE–IMD–kontaktör–deşarj kabul matrisini yetkili şarj istasyonu servis ve devreye alma ekibine iletin.

- Her soket için IMD ve güç modülü ilişkisini tekilleştirin.
- Test ekipmanı, kalibrasyon, direnç ve tepki sürelerini rapora ekleyin.
- Firmware veya güç modülü değişiminden sonra kabul testini tekrarlayın.
- Kanıt yeterliyse gereksiz IMD veya komple şarj cihazı değişimi satın almayın.

_Kaynaklar: S1, S2, S3, S4, S5_

## Sık sorulan sorular

### DC hızlı şarj istasyonunda RCD varsa IMD gerekir mi?

RCD ve IMD farklı devre ve arızaları izler. AC giriş RCD'si, yalıtılmış DC çıkışın izolasyon direncini sürekli izleyen IMD'nin yerine geçmez; kesin mimari istasyon standardı ve uygunluk dosyasından doğrulanır.

_Kaynaklar: S1, S2_

### İzolasyon hatasında şarja tekrar başlanabilir mi?

Kök neden giderilmeden ve güvenli reset koşulu sağlanmadan tekrar denenmemelidir. İstasyon servis dışı bırakılmalı; olay logu ve ölçüm yetkili servisçe incelenmelidir.

_Kaynaklar: S1, S3, S5_

### IMD testi için DC kablo toprağa değdirilir mi?

Hayır. Gerçek DC iletkenini toprağa bağlamak tehlikelidir. Üreticinin izin verdiği test direnci ve simülatör, manevra planı ve yetkin ekip kullanılmalıdır.

_Kaynaklar: S1, S2, S5_

### İzolasyon hatası her zaman araç arızası mıdır?

Hayır. Kablo, konnektör, nem, istasyon güç modülü, DC bara, filtre veya araç yüksek gerilim sistemi kaynaklı olabilir. Karşılaştırmalı test kesin hüküm değil, kök neden ayrımı için kanıttır.

_Kaynaklar: S1, S3, S4_

## İnsan onay komutu

PR sahibinin veya repository yetkilisinin yorumu:

```text
/cms approve dc-hizli-sarj-izolasyon-izleme-imd-ariza-kabul-testi
```

Onay iş akışı kalite puanı, kaynak güncelliği, iç linkler, kanibalizasyon ve risk sınırlarını yeniden çalıştırmadan canonical dosya üretmez.
