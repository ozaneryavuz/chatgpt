# ALO186 AI CMS inceleme paketi — vpp-temel-tuketim-baseline-uzlastirma-itiraz-dosyasi

> Bu dosya canonical yayına dahil edilmez. PR incelemesi ve insan onayı için üretilmiştir.

## Durum

- State: **approved**
- Risk: **legal**
- Model: **gpt-5.6-thinking**
- Kalite: **88/100**
- Benzerlik: **0.47** — https://www.alo186.com/haberler/vpp-temel-tuketim-baseline-performans-dogrulama
- Kelime: **878**

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

- **S1 · IEC** — [IEC SRD 63443-1:2026 — DER aggregation — Business architecture](https://webstore.iec.ch/en/publication/72787) — erişim 2026-08-03 — birincil
- **S2 · EPDK** — [Elektrik Piyasası Yan Hizmetler Yönetmeliği ve ilgili usul-esaslar](https://epdk.gov.tr/Detay/Icerik/3-6723/elektrik-piyasasi-yan-hizmetler-yonetmeligi) — erişim 2026-08-03 — birincil
- **S3 · Resmî Gazete / EPDK** — [Kurul Kararı 13529 — Talep Tarafı Katılımı Temel Tüketim Değeri Belirleme Metodolojisi](https://www.resmigazete.gov.tr/eskiler/2025/05/20250527-7.pdf) — erişim 2026-08-03 — birincil
- **S4 · TEİAŞ** — [Talep Tarafı Katılımı Hizmeti](https://www.teias.gov.tr/talep-tarafi-katilimi-hizmeti) — erişim 2026-08-03 — birincil
- **S5 · IEC** — [IEC 61850-7-420:2021 — DER information models](https://webstore.iec.ch/en/publication/34384) — erişim 2026-08-03 — birincil

## SEO

- Title: `VPP Temel Tüketim, Baseline ve Uzlaştırma İtiraz Dosyası`
- H1: `VPP ve talep tarafı katılımında baseline nasıl doğrulanır, sapmaya nasıl itiraz edilir?`
- Description: `VPP ve talep tarafı katılımında temel tüketim değerini; OSOS, saatlik program, aktivasyon ve uzlaştırma verileriyle doğrulayın.`
- Canonical: `/haberler/vpp-temel-tuketim-baseline-uzlastirma-itiraz-dosyasi`
- Birincil anahtar kelime: `VPP baseline temel tüketim değeri`

## Doğrudan cevap

VPP veya talep tarafı katılımında baseline, basit bir geçmiş tüketim ortalaması değildir. Saatlik program, OSOS gerçekleşmesi, aktivasyon zamanı, veri kalitesi ve işlem dönemindeki yöntem birlikte değerlendirilir. Kabul dosyası; sayaç/portföy eşleşmesi, zaman dilimi, program, gerçekleşme, talimat, eksik veya düzeltilmiş veri, yöntem sürümü ve hesaplanan sapmayı aynı çizelgede göstermelidir. Bu çalışma piyasa katılımı, ödeme veya gelir garantisi değildir; müşteri kimliği ve erişim sırları paylaşılmamalıdır.

## Baseline ile gerçek tüketim arasındaki fark nasıl tanımlanır?

Baseline veya temel tüketim değeri, aktivasyon olmasaydı tesisin ilgili saatte beklenen tüketimini temsil eder. Gerçek tüketimle arasındaki fark, esneklik performansının hesabında kullanılabilir; ancak hesap yöntemi piyasa ürünü, dönem, tesis türü ve yürürlükteki kurallara bağlıdır. Basit bir son yedi gün ortalaması, resmî yöntem yerine kullanılamaz.

IEC SRD 63443-1, dağıtık enerji kaynaklarının toplanması için iş rolleri ve veri akışlarını tanımlayan genel bir mimari sağlar. Türkiye'deki Talep Tarafı Katılımı için ise EPDK'nın yan hizmetler düzenlemeleri, kurul kararları ve TEİAŞ uygulama sayfaları esas alınmalıdır. Uluslararası VPP kavramı ile ulusal uzlaştırma formülü aynı şey değildir.

- Baseline yöntemini piyasa ürünü ve yürürlük tarihine göre sabitleyin.
- Basit geçmiş ortalamayı resmî yöntemmiş gibi kullanmayın.
- Program, gerçekleşme ve aktivasyon verisini ayrı katmanlarda tutun.
- Teknik VPP mimarisi ile ulusal ödeme ve uzlaştırma kuralını ayırın.

_Kaynaklar: S1, S2, S3, S4_

## OSOS ve sayaç verisinde hangi kalite kontrolleri yapılmalıdır?

Saatlik veya daha kısa aralıklı veride sayaç ve portföy eşleşmesi, sayaç değişimi, çarpan, ölçüm yönü, zaman dilimi, yaz-kış saati uygulaması, eksik profil, yinelenen kayıt, geç gelen veri ve kalite biti kontrol edilmelidir. Aynı tesisin farklı sayaçlarının yanlış toplanması veya üretim-tüketim işaretinin ters çevrilmesi baseline ve performansı doğrudan bozar.

Ham OSOS verisi, temizlenmiş analiz verisi ve uzlaştırmada kullanılan resmî veri birbirinden ayrılmalıdır. Eksik değerlerin hangi kural ve sürümle tamamlandığı; sonradan yapılan düzeltmenin hangi döneme yansıdığı kayıt altına alınmalıdır. Bir grafik üzerinde düzgün görünmesi, verinin resmî uzlaştırma katmanıyla aynı olduğunu kanıtlamaz.

- Sayaç seri numarasını raporda maskeleyip portföy eşleşmesini içeride doğrulayın.
- Zaman damgası, zaman dilimi ve saat kaymasını açıkça kaydedin.
- Eksik, yinelenen ve düzeltilmiş verileri ayrı kalite kodlarıyla işaretleyin.
- Ham, temizlenmiş ve resmî uzlaştırma veri katmanlarını karıştırmayın.

_Kaynaklar: S2, S3, S4, S5_

## Aktivasyon sırasında baseline ve gerçek tepki nasıl eşleştirilir?

Her olay için talimat kimliği, başlangıç ve bitiş zamanı, hedef güç veya enerji, katılan kaynaklar, ilgili baseline, gerçek tüketim ve ölçülen yük değişimi tek satırda izlenmelidir. VPP platformundaki komut kaydı, OSOS gerçekleşmesi ve tesis SCADA verisi farklı zaman tabanlarındaysa önce senkronizasyon yapılmalıdır.

TEİAŞ'ın Talep Tarafı Katılımı hizmet sayfası hizmetin güncel süreç ve dokümanlarını yayımlar. Performans eşiği, tolerans veya katsayılar geçmiş bir duyurudan kopyalanmamalıdır; sözleşme dönemi ve yürürlükteki kurul kararı esas alınmalıdır. Yerel yük arızası, üretim değişimi veya ölçüm boşluğu esneklik performansı gibi raporlanmamalıdır.

- Talimat, baseline, gerçekleşme ve ölçülen farkı aynı zaman ekseninde gösterin.
- Katılmayan veya haberleşme kaybındaki kaynağı emreamade kapasiteye eklemeyin.
- Eski tolerans ve katsayıları yeni uzlaştırma dönemine taşımayın.
- Üretim, yük arızası ve veri düzeltmesini gerçek talep tepkisinden ayırın.

_Kaynaklar: S2, S3, S4_

## Baseline veya uzlaştırma sapmasında itiraz dosyası nasıl hazırlanır?

İtiraz dosyası uzlaştırma veya fatura dönemini, ilgili TEİAŞ temel tüketim değerini, tesisin bildirilen saatlik programını, OSOS gerçekleşmesini, aktivasyon talimatını, kullanılan yöntem ve sürümü, veri kalite sorunlarını, yeniden hesaplanan sonucu ve istenen düzeltmeyi açıkça göstermelidir. Yalnız toplam tutar veya ekran görüntüsü, hatanın hangi saat ve veriden doğduğunu kanıtlamaz.

Temel tüketim metodolojisi ve katsayıları zaman içinde değişebilir. 27 Mayıs 2025 tarihli kurul kararıyla yayımlanan yöntem, daha sonra 17 Ekim 2025 tarihli değişiklikle bazı katsayılar bakımından güncellenmiştir. Bu nedenle dosyada işlem tarihindeki yürürlük sürümü ve kullanılan formül saklanmalıdır; ALO186 hukuki temsil veya ödeme sonucu garantisi vermez.

- Sapmayı saat ve veri kaynağı düzeyinde gösterin.
- İşlem dönemindeki yöntem ve katsayı sürümünü ekleyin.
- Resmî veriye karşı kullanılan alternatif verinin kaynağını açıklayın.
- Teknik yeniden hesaplama ile hukuki itiraz sürecini ayrı sorumlulara imzalatın.

_Kaynaklar: S2, S3, S4_

## VPP baseline kabul ve uzlaştırma teslim paketi neleri içermelidir?

Paket; portföy ve sayaç eşleştirme tablosu, veri sözlüğü, zaman ve kalite kuralları, ham-temiz-resmî veri katmanları, program ve aktivasyon kayıtları, yöntem ve formül sürümü, yeniden üretilebilir hesap adımları, saatlik fark tablosu, açık maddeler ve imzalı teknik-mevzuat sonuçlarını içermelidir. Müşteri ve sayaç kimlikleri dış paylaşımda takma kimlikle gösterilmelidir.

Aynı girdi ve sürümle hesap tekrarlandığında aynı sonucun üretilmesi kabulün temel şartıdır. Dosya yalnız teknik kanıt sağlar; toplayıcılık yetkisi, piyasa kaydı, ödeme, ceza veya gelir sonucunu tek başına belirlemez. CTA: kişisel verisiz VPP baseline–OSOS–aktivasyon–uzlaştırma matrisini enerji ve piyasa uzmanlarına iletin.

- Formül, katsayı ve veri temizleme kodunu sürümleyin.
- Portföy ve sayaç kimliklerini dış dosyada maskeleyin.
- Aynı hesap paketini bağımsız kişi tarafından tekrar çalıştırın.
- Canlı API anahtarı, parola veya müşteri verisini ALO186'e yüklemeyin.

_Kaynaklar: S1, S2, S3, S4, S5_

## Sık sorulan sorular

### VPP baseline son günlerin basit tüketim ortalaması mıdır?

Her zaman değil. Kullanılacak temel tüketim yöntemi ilgili piyasa ürünü, yürürlük tarihi ve TEİAŞ/EPDK düzenlemesine bağlıdır; basit ortalama resmî formülün yerine geçmez.

_Kaynaklar: S2, S3, S4_

### OSOS verisi eksikse baseline nasıl hesaplanır?

Eksik veri, yürürlükteki metodoloji ve veri kalite kuralına göre işlenmelidir. Hangi saatlerin hangi yöntemle tamamlandığı görünür olmalı; tahmini veri gerçek ölçüm gibi saklanmamalıdır.

_Kaynaklar: S2, S3, S4_

### Yanlış baseline veya uzlaştırma sonucuna itiraz edilebilir mi?

İlgili piyasa ve sözleşme sürecindeki itiraz kanalı kullanılabilir. Başvuru; saatlik program, OSOS, aktivasyon, yöntem sürümü ve yeniden hesaplama kanıtıyla hazırlanmalıdır.

_Kaynaklar: S2, S3, S4_

### Baseline kabul dosyası VPP gelirini garanti eder mi?

Hayır. Dosya hesap ve veri zincirinin izlenebilirliğini gösterir; piyasa fiyatı, aktivasyon sıklığı, performans, ceza ve sözleşme koşulları geliri ayrıca belirler.

_Kaynaklar: S1, S2, S4_

## İnsan onay komutu

PR sahibinin veya repository yetkilisinin yorumu:

```text
/cms approve vpp-temel-tuketim-baseline-uzlastirma-itiraz-dosyasi
```

Onay iş akışı kalite puanı, kaynak güncelliği, iç linkler, kanibalizasyon ve risk sınırlarını yeniden çalıştırmadan canonical dosya üretmez.
