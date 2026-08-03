# ALO186 AI CMS inceleme paketi — vpp-talep-tarafi-katilimi-baseline-telemetri-hazirlik

> Bu dosya canonical yayına dahil edilmez. PR incelemesi ve insan onayı için üretilmiştir.

## Durum

- State: **approved**
- Risk: **legal**
- Model: **gpt-5.6-thinking**
- Kalite: **100/100**
- Benzerlik: **0.42** — https://www.alo186.com/haberler/vpp-talep-tarafi-katilimi-toplayici-2026
- Kelime: **974**

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

- **S1 · TEİAŞ** — [Talep Tarafı Katılımı Hizmeti Hakkında — Temmuz–Eylül 2026 tedarik duyurusu](https://www.teias.gov.tr/haberler/talep-tarafi-katilimi-hizmeti-hakkinda-bkh2) — erişim 2026-08-03 — birincil
- **S2 · TEİAŞ** — [Talep Tarafı Katılımı Anlaşması duyurusu](https://www.teias.gov.tr/haberler/talep-tarafi-katilimi-anlasmasi) — erişim 2026-08-03 — birincil
- **S3 · TEİAŞ** — [Talep Tarafı Katılımı Hizmeti doküman merkezi](https://www.teias.gov.tr/talep-tarafi-katilimi-hizmeti) — erişim 2026-08-03 — birincil
- **S4 · TEİAŞ** — [Talep Tarafı Katılımı modülüne veri gönderme API dokümanı duyurusu](https://www.teias.gov.tr/duyurular/talep-tarafi-katilimi-modulune-veri-gonderebilmesine-dair-api-dokumani-duyurusu) — erişim 2026-08-03 — birincil
- **S5 · EPDK** — [Elektrik piyasası yürürlükteki yönetmelikler](https://www.epdk.gov.tr/Detay/Icerik/3-0-159/yonetmelikler) — erişim 2026-08-03 — birincil

## SEO

- Title: `VPP Talep Tarafı Katılımı Hazırlık Dosyası`
- H1: `VPP ve talep tarafı katılımı için baseline ve telemetri nasıl hazırlanır?`
- Description: `Toplayıcı ve tesis ekipleri için baseline, sayaç, telemetri, CSV/API, dispatch yanıtı ve kabul testlerini tek VPP hazırlık dosyasında doğrulayın.`
- Canonical: `/haberler/vpp-talep-tarafi-katilimi-baseline-telemetri-hazirlik`
- Birincil anahtar kelime: `talep tarafı katılımı hazırlık`

## Doğrudan cevap

VPP veya Talep Tarafı Katılımı hazırlığı yalnız batarya kapasitesi hesabı değildir. Hazır bir dosya; yetkili piyasa katılımcısı ve anlaşma durumunu, TTK birimi sayaç/ölçüm sınırını, geçmiş tüketim verisinden baseline üretimini, telemetri ve CSV/API veri akışını, dispatch komutunun sahada güvenli karşılanmasını ve olay sonrası doğrulamayı birlikte kanıtlamalıdır. TEİAŞ’ın 2026 duyuruları anlaşma, başvuru CSV’si ve web servis kataloğunu fiilen kullanan bir süreç gösterdiği için, teknik entegrasyon ile mevzuat uygunluğu aynı hazırlık planında tutulmalıdır.

## VPP, toplayıcı ve talep tarafı katılımı rollerini nasıl ayırmalısınız?

VPP, dağınık tüketim, üretim ve depolama esnekliğini ortak bir kontrol ve ticari karar katmanında birleştiren daha geniş bir işletim yaklaşımıdır. Türkiye’de Talep Tarafı Katılımı Hizmeti ise TEİAŞ’ın yan hizmet tedarik sürecine, toplayıcıların anlaşma ve teknik başvuru yükümlülükleriyle katıldığı belirli bir piyasa sürecidir. Bir tesisin VPP yazılımına bağlanması, tek başına TTK hizmetine kabul edildiği anlamına gelmez.

İlk matriste lisans ve toplayıcı sorumluluğu, tesis sahibi sorumluluğu, ölçüm noktası, portföy içi komut yetkisi, veri işleyen taraflar ve sözleşmesel performans yükümlülükleri ayrı yazılmalıdır. TEİAŞ 2026 duyurularında tedarik dönemine katılacak toplayıcılardan yan hizmet anlaşmasının belirli tarihe kadar imzalanmasını istemiş, ayrıca anlaşma başvurusunda lisans ve ticaret sicil belgelerini saymıştır.

- VPP yazılım hizmeti ile resmî TTK piyasa katılımını ayrı satırlarda gösterin.
- Toplayıcı, tesis, ölçüm sorumlusu ve yazılım sağlayıcının rollerini yazın.
- Güncel tedarik dönemi ve anlaşma son tarihlerini yalnız TEİAŞ duyurusundan doğrulayın.
- Bir tesisi yalnız teknik bağlantı kuruldu diye piyasa katılımcısı ilan etmeyin.

_Kaynaklar: S1, S2, S5_

## TTK birimi, sayaç ve geçmiş veri sınırı nasıl tanımlanır?

Başvuru dosyası, hangi sayaçların ve yüklerin tek TTK birimi olarak ele alınacağını açıkça göstermelidir. Sayaç kimliği, ölçüm periyodu, zaman dilimi, veri eksikliği, sayaç değişimi, üretim ve depolamanın net yükü nasıl etkilediği kayıt altına alınmalıdır. TEİAŞ hizmet sayfası EPDK onaylı anlaşma metni, web servis kataloğu ve başvuru için CSV örneğini aynı klasörde yayımlayarak veri modelinin başvurunun parçası olduğunu gösterir.

CSV veya API alanlarını son anda doldurmak yerine, geçmiş veride boşluk, tekrar, saat kayması ve birim dönüşümü kontrol edilmelidir. GES, BESS, EV şarj, jeneratör testi veya üretim vardiyası gibi olaylar baseline’ı bozabilir. Bu olaylar etiketlenmezse portföyün gerçek azaltma veya artırma performansı yanlış yorumlanabilir.

- Tek hat şemasıyla TTK birimine dahil ölçüm noktalarını eşleştirin.
- Sayaç zaman damgası, periyot ve birim sözlüğü oluşturun.
- Eksik ve değiştirilen sayaç dönemlerini işaretleyin.
- GES, BESS, EV ve üretim planı etkilerini olay etiketi olarak tutun.

_Kaynaklar: S3, S4_

## Baseline ve sunulabilir esneklik kapasitesi nasıl kanıtlanır?

Baseline, dispatch olmasaydı tesisin ne tüketeceğine ilişkin karşılaştırma çizgisidir; yalnız son gün ortalaması kullanmak çoğu tesis için yeterli kanıt değildir. Hafta içi/hafta sonu, mevsim, vardiya, sıcaklık, doluluk, üretim siparişi ve kendi üretim etkileri ayrılmalıdır. Yöntem, sözleşme ve güncel TEİAŞ prosedürleriyle uyumlu olmalı; tesis içi planlama için alternatif yöntemler hata ölçütleriyle karşılaştırılmalıdır.

Sunulabilir kapasite, teorik cihaz gücü değil; proses, konfor, can güvenliği, ürün kalitesi, minimum çalışma süresi, rebound ve batarya SoC rezervi sonrasında güvenle sürdürülebilen net değişimdir. Her kaynak için minimum/azami güç, rampalama, sürdürülebilir süre, toparlanma süresi ve o anda kullanılabilirliği hesaplayan veri tanımlanmalıdır. Aşırı taahhüt, hem proses riskini hem performans sapmasını büyütür.

- Baseline yöntemini veri penceresi ve dışlama kurallarıyla belgeleyin.
- Tahmin hatasını normal günler ve olay günleri için ayrı ölçün.
- Esneklik kapasitesinden proses, güvenlik ve SoC rezervlerini düşün.
- Rebound ve sonraki saatlerde oluşacak ek tüketimi hesaba katın.

_Kaynaklar: S1, S3, S5_

## Telemetri, CSV/API ve dispatch zinciri hangi testlerden geçmelidir?

TEİAŞ, toplayıcıların Talep Tarafı Katılımı modülüne veri göndermesi için web servis kataloğu yayımlamış; 20 Mayıs 2026 duyurusunda dağıtımdan başvuruda kullanılacak CSV örneğini ayrıca paylaşmıştır. Bu nedenle hazırlık yalnız dosya formatı değil; kimlik doğrulama, alan eşleştirme, zaman damgası, yeniden deneme, hata kodu ve veri bütünlüğü testlerini kapsamalıdır.

Dispatch komutu; piyasa sisteminden toplayıcıya, oradan tesis kontrol katmanına ve gerçek yüke kadar izlenebilmelidir. Komutun alındığı, kabul/red nedeni, hedef güç, başlangıç zamanı, gerçekleşen değer, bağlantı kaybı ve manuel geri dönüş aynı olay kimliğiyle kaydedilmelidir. Kritik yüklerde bağlantı kesilmesi veya yanlış komut, fail-safe yerel kontrolü geçersiz kılamaz.

- API ve CSV alanlarını tek veri sözlüğünde eşleştirin.
- Saat senkronu, tekrar kayıt ve eksik veri senaryolarını test edin.
- Dispatch komutuna uçtan uca olay kimliği verin.
- İletişim kaybında güvenli yerel işletme ve manuel geri alma planı yazın.

_Kaynaklar: S3, S4_

## Canlı katılım öncesi kabul ve sözleşme dosyası ne içermelidir?

Canlı kabul, masa başı API testinden daha geniştir. Temsili bir dispatch senaryosunda komut gecikmesi, ölçüm doğruluğu, gerçek güç değişimi, sürdürülebilir süre, rebound, veri teslimi ve olay raporu birlikte doğrulanmalıdır. GES üretim tahmini, BESS SoC sınırı ve tesis üretim planı değiştiğinde sunulabilir kapasitenin otomatik güncellendiği gösterilmelidir.

Sözleşme dosyasında performans ölçümü, sapma sorumluluğu, veri erişimi, siber güvenlik, kişisel veri, bakım penceresi, cihaz garanti sınırı ve portföyden çıkış koşulları bulunmalıdır. TEİAŞ duyuru ve belgeleri dönemsel olarak güncellenebileceğinden, başvuru günündeki resmî anlaşma ve teknik katalog sürümü kayda alınmalıdır. Mevcut ölçüm ve kontrol altyapısı şartları karşılıyorsa gereksiz yeni cihaz satın almak doğru sonuç değildir.

- Uçtan uca dispatch kabul tutanağı hazırlayın.
- Kapasite güncellemesini SoC, üretim ve bakım durumuna bağlayın.
- Veri, siber güvenlik ve sorumluluk maddelerini teknik ekle eşleştirin.
- Başvuru günündeki TEİAŞ belge sürümlerini arşivleyin.

_Kaynaklar: S1, S2, S3, S4, S5_

## Sık sorulan sorular

### VPP’ye bağlanan her tesis Talep Tarafı Katılımı hizmetine katılabilir mi?

Hayır. Teknik VPP bağlantısı, toplayıcı lisansı, yan hizmet anlaşması, TTK birimi başvurusu ve güncel tedarik koşullarının yerine geçtiği anlamına gelmez. Resmî süreç TEİAŞ ve EPDK belgeleriyle doğrulanmalıdır.

_Kaynaklar: S1, S2, S5_

### Baseline yalnız geçmiş tüketim ortalamasıyla kurulabilir mi?

Her tesis için tek bir ortalama yeterli değildir. Vardiya, mevsim, hava, üretim, GES, BESS ve olay günleri ayrılmalı; kullanılan yöntem güncel piyasa kurallarıyla uyumlu ve hata ölçütleriyle izlenebilir olmalıdır.

_Kaynaklar: S1, S3_

### TEİAŞ başvurusunda CSV yeterli midir?

CSV örneği başvuru veri yapısının bir parçasıdır; ayrıca yan hizmet anlaşması, lisans ve ilgili belgeler ile web servis/API entegrasyonu ve teknik performans gerekleri bulunabilir. Güncel resmî paket birlikte kontrol edilmelidir.

_Kaynaklar: S2, S3, S4_

### BESS’in nominal gücü VPP’ye sunulabilir kapasite midir?

Hayır. SoC rezervi, enerji kapasitesi, sıcaklık, garanti, inverter sınırı, tesis yükü, sürdürülebilir süre ve rebound dikkate alınmadan nominal güç taahhüt edilmemelidir.

_Kaynaklar: S1, S3_

## İnsan onay komutu

PR sahibinin veya repository yetkilisinin yorumu:

```text
/cms approve vpp-talep-tarafi-katilimi-baseline-telemetri-hazirlik
```

Onay iş akışı kalite puanı, kaynak güncelliği, iç linkler, kanibalizasyon ve risk sınırlarını yeniden çalıştırmadan canonical dosya üretmez.
