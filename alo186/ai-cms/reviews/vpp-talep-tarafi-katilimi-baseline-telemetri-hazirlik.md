# ALO186 AI CMS insan inceleme paketi

## İçerik

- **Başlık:** VPP Talep Tarafı Katılımı Hazırlık Dosyası
- **H1:** VPP ve talep tarafı katılımı için baseline ve telemetri nasıl hazırlanır?
- **Canonical adayı:** `/haberler/vpp-talep-tarafi-katilimi-baseline-telemetri-hazirlik`
- **Birincil anahtar ifade:** `talep tarafı katılımı hazırlık`
- **Risk sınıfı:** `legal`
- **Fırsat puanı:** **94/100**
- **AI CMS kalite hedefi:** **100/100**
- **Durum:** `review` — canonical HTML veya routing overlay henüz yok

## Kullanıcı görevi

Bir tesisin veya portföyün VPP ve Talep Tarafı Katılımı hizmetine teknik ve operasyonel olarak hazır olup olmadığını, başvuru öncesi kanıt matrisiyle değerlendirmek.

## Doğrudan cevap

VPP veya Talep Tarafı Katılımı hazırlığı yalnız batarya kapasitesi hesabı değildir. Hazır bir dosya; yetkili piyasa katılımcısı ve anlaşma durumunu, TTK birimi sayaç/ölçüm sınırını, geçmiş tüketim verisinden baseline üretimini, telemetri ve CSV/API veri akışını, dispatch komutunun sahada güvenli karşılanmasını ve olay sonrası doğrulamayı birlikte kanıtlamalıdır. TEİAŞ’ın 2026 duyuruları anlaşma, başvuru CSV’si ve web servis kataloğunu fiilen kullanan bir süreç gösterdiği için, teknik entegrasyon ile mevzuat uygunluğu aynı hazırlık planında tutulmalıdır.

## Mevcut içerikten görev ayrımı

Mevcut VPP tanım ve batarya sözleşmesi içeriklerinden farklı olarak TTK birimi, baseline veri kalitesi, telemetri, CSV/API ve dispatch kabul zincirini hazırlar.

Tahmini en yüksek başlık/H1 benzerliği: **0.320** — en yakın rota: `/haberler/vpp-batarya-cevrim-rezerv-garanti-sozlesmesi`. Fail-closed AI CMS doğrulaması gerçek envanter üzerinde yeniden hesaplar; `0,78` veya üzeri benzerlikte onay durmalıdır.

## Bölümler ve kaynak bağı

- **VPP, toplayıcı ve talep tarafı katılımı rollerini nasıl ayırmalısınız?** — S1, S2, S5
- **TTK birimi, sayaç ve geçmiş veri sınırı nasıl tanımlanır?** — S3, S4
- **Baseline ve sunulabilir esneklik kapasitesi nasıl kanıtlanır?** — S1, S3, S5
- **Telemetri, CSV/API ve dispatch zinciri hangi testlerden geçmelidir?** — S3, S4
- **Canlı katılım öncesi kabul ve sözleşme dosyası ne içermelidir?** — S1, S2, S3, S4, S5

## Kaynak doğrulaması

| Ref | Yayıncı | Kaynak | Erişim | Birincil |
|---|---|---|---|---|
| S1 | TEİAŞ | Talep Tarafı Katılımı Hizmeti Hakkında — Temmuz–Eylül 2026 tedarik duyurusu | 2026-08-03 | Evet |
| S2 | TEİAŞ | Talep Tarafı Katılımı Anlaşması duyurusu | 2026-08-03 | Evet |
| S3 | TEİAŞ | Talep Tarafı Katılımı Hizmeti doküman merkezi | 2026-08-03 | Evet |
| S4 | TEİAŞ | Talep Tarafı Katılımı modülüne veri gönderme API dokümanı duyurusu | 2026-08-03 | Evet |
| S5 | EPDK | Elektrik piyasası yürürlükteki yönetmelikler | 2026-08-03 | Evet |

Bütün teknik ve hukukî iddialar yalnız içerik kaydındaki `factSummary` ve ilgili `S#` kaynak referanslarına dayanmalıdır. Evrensel eşik, garanti, fiyat, stok veya resmî onay iddiası eklenmemelidir.

## İç bağlantılar

- `/haberler/vpp-sanal-guc-santrali-nedir` — Temel VPP kavramını başvuru hazırlığından ayırır.
- `/haberler/vpp-batarya-cevrim-rezerv-garanti-sozlesmesi` — Batarya ticari ve garanti sınırını teknik katılım dosyasına bağlar.
- `/haberler/batarya-soc-soh-farki-kapasite-saglik-nasil-anlasilir` — Sunulabilir kapasitede şarj durumu ve sağlık ayrımını açıklar.
- `/haberler/batarya-c-rate-dod-kullanilabilir-kapasite` — Güç, süre ve kullanılabilir enerji sınırlarını destekler.
- `/hesaplama/elektrik-surekliligi-pasaportu` — Varlık ve test kayıtlarını düzenli kanıt dosyasına dönüştürür.
- `/kurumsal-elektrik-surekliligi-on-degerlendirme` — Çoklu tesis ve profesyonel ölçüm kapsamına geçiş sağlar.
- `/isletme-surekliligi` — Dispatch sırasında kritik yük ve proses sınırını tanımlar.

## AEO / SEO ve yapılandırılmış veri

- benzersiz title, meta description, H1 ve canonical adayı;
- ilk ekranda bağımsız doğrudan cevap;
- beş kaynak bağlı bölüm ve dört görünür SSS;
- kurumsal `Organization` yazarlığı;
- canonical derleyicide `Article`, `FAQPage` ve `BreadcrumbList`;
- `Product`, `Offer`, `Person` ve `ProfilePage` yasağı;
- kaynak erişim tarihi ve görünür atıf zinciri;
- kullanıcıya teslim edilebilir kontrol, kanıt veya kabul dosyası.

## Güvenlik ve dönüşüm sınırı

Bu içerik `legal` risk sınıfındadır. Affiliate ve ürün satın alma CTA’sı kapalıdır. Dönüşüm çağrısı; TTK hazırlık matrisi, veri sözlüğü, dispatch kabul planı ve kurumsal teknik ön değerlendirmedir. Güncel TEİAŞ/EPDK belgesi doğrulanmadan piyasa katılımı iddiası kurulamaz.

## İnsan onayı

Teknik içerik, kaynak, görev ayrımı, iç bağlantılar ve güvenlik sınırı kabul edilirse PR konuşmasına tam olarak şu yorum eklenmelidir:

```text
/cms approve vpp-talep-tarafi-katilimi-baseline-telemetri-hazirlik
```

AI veya otomasyon bu komutu veremez. Onay sonrasında canonical HTML, routing overlay ve ChatGPT Sites önizleme artifactı oluşur; zorunlu kontroller geçmeden merge edilmemelidir.
