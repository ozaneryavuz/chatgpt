# ALO186 AI CMS insan inceleme paketi

## İçerik

- **Başlık:** EV Şarj İstasyonu İnternet Kesintisi: OCPP Offline İşlem Kabulü
- **H1:** İnternet kesilince EV şarj istasyonu çalışır mı, OCPP offline işlemler nasıl test edilir?
- **Canonical adayı:** `/haberler/ev-sarj-istasyonu-internet-kesintisi-ocpp-offline-islem-kabul`
- **Birincil anahtar ifade:** `EV şarj istasyonu internet kesintisi OCPP`
- **Risk sınıfı:** `high`
- **Fırsat puanı:** **96/100**
- **AI CMS kalite hedefi:** **100/100**
- **Durum:** `review` — canonical HTML veya routing overlay henüz yok

## Kullanıcı görevi

OCPP bağlı bir EV şarj istasyonunun internet veya CSMS bağlantısı kesildiğinde güvenli şarj, yetkilendirme, sayaç verisi, zaman damgası ve işlem mutabakatını kayıpsız sürdürebildiğini kanıtlamak.

## Doğrudan cevap

İnternet kesildiğinde bir EV şarj istasyonunun çalışıp çalışmayacağı yalnız OCPP sürümüne bağlı değildir; cihazın yerel yetkilendirme, çevrimdışı işlem saklama, sayaç örnekleme, saat senkronizasyonu ve yeniden bağlantıda kayıt gönderme ayarlarına bağlıdır. Kabul testi; bağlantı kopmadan önce aktif işlem, yeni çevrimdışı başlatma, yetkisiz kart, cihaz yeniden başlatma, uzun kesinti, saat sapması ve bağlantı geri geldiğinde işlem mutabakatı senaryolarını ayrı ayrı kapsamalıdır. Şarj enerjisi, işlem kimliği, başlangıç-bitiş zamanları ve ücretlendirme verisi kayboluyor veya yineleniyorsa sistem canlı işletmeye kabul edilmemelidir.

## Kaynak doğrulaması

| ID | Yayıncı | Kaynak | Birincil | Erişim |
|---|---|---|---|---|
| S1 | Open Charge Alliance | Download OCPP — OCPP 2.1, 2.0.1 ve 1.6 resmî paketleri | Evet | 2026-08-03 |
| S2 | Open Charge Alliance | OCPP 2.0.1 Certification | Evet | 2026-08-03 |
| S3 | Open Charge Alliance | Open Charge Point Protocol | Evet | 2026-08-03 |
| S4 | Open Charge Alliance | What is new in OCPP 2.0.1? | Evet | 2026-08-03 |

Kaynak özetleri içerik kaydında tutulur; her bölüm ve SSS yalnız ilgili `S#` kimliklerine dayanır. Erişim tarihi **3 Ağustos 2026**’dır.

## İçerik yapısı

- **İnternet kesintisinde hangi işlevlerin devam edeceği nasıl belirlenir?** — kaynaklar: S1, S2, S3
- **Çevrimdışı işlem ve sayaç verisi nasıl kanıtlanmalıdır?** — kaynaklar: S1, S3, S4
- **Saat senkronizasyonu ve zaman damgası hatası nasıl test edilir?** — kaynaklar: S1, S3
- **Bağlantı geri geldiğinde mutabakat nasıl yapılmalıdır?** — kaynaklar: S1, S2, S3
- **Canlı işletme öncesi hangi kabul dosyası hazırlanmalıdır?** — kaynaklar: S1, S2, S3, S4

## İç bağlantılar

- [EV şarj tesisat uygunluğu](/haberler/ev-sarj-cihazi-icin-ev-tesisati-uygun-mu) — İletişim testinden önce elektrik altyapısı ve koruma uygunluğunu doğrular.
- [Dinamik yük yönetimi](/haberler/ev-sarjinda-dinamik-yuk-yonetimi) — OCPP Smart Charging ve yerel güç sınırı bağlamını tamamlar.
- [EV şarj süresi hesabı](/hesaplama/ev-sarj-suresi/) — İşlem enerjisi ve beklenen şarj süresi için kullanıcıya referans verir.
- [EV şarj gücü neden düşük?](/haberler/ev-sarj-gucu-neden-dusuk-yavas-sarj) — İletişim kopmasını gerçek güç sınırlaması veya araç davranışından ayırır.
- [Wallbox neden başlamıyor?](/haberler/elektrikli-arac-sarj-olmuyor-wallbox-neden-baslamiyor) — Yerel elektrik ve yetkilendirme sorunlarını ilk arıza sınıflandırmasına bağlar.
- [V2L, V2H ve V2G farkı](/haberler/v2l-v2h-v2g-farki-cift-yonlu-sarj) — İleri şarj ve enerji yönetimi mesajlaşması için kavramsal bağ kurar.
- [Kurumsal ön değerlendirme](/kurumsal-elektrik-surekliligi-on-degerlendirme) — Çoklu istasyon ve işletme ağlarında saha kabul kapsamını profesyonel çalışmaya taşır.

## AEO, SEO ve yapılandırılmış veri

- İlk ekranda bağımsız anlaşılabilen doğrudan cevap bulunur.
- Title, meta description, H1 ve canonical birbirinden tutarlı ve kullanıcı görevi odaklıdır.
- Dört görünür SSS bulunur.
- Canonical derleyici `Article`, `FAQPage` ve `BreadcrumbList` üretmelidir.
- Yazar/üretici kimliği kurumsal `Organization` olmalıdır.
- `Person`, `ProfilePage`, `Product` ve `Offer` kullanılmamalıdır.
- Tahmini en yüksek mevcut içerik benzerliği `0.28`; en yakın rota `/haberler/elektrikli-arac-sarj-olmuyor-wallbox-neden-baslamiyor`. Fail-closed eşik `0,78`’dir.

## Kullanıcı faydası ve dönüşüm

- **Birincil CTA:** Kişisel verisiz teknik kabul/kanıt dosyası hazırlama.
- **İkincil CTA:** İlgili ücretsiz ALO186 araçları ve resmî/kurumsal teknik değerlendirme.
- **Affiliate:** kapalıdır.
- Mevcut sistem ölçüm ve belgeyle yeterliyse satın almama sonucu korunur.

## Güvenlik sınırı

Bu içerik enerjili pano, sayaç, akım trafosu, şarj ünitesi, kompanzasyon kademesi veya topraklama tesisatına kullanıcı müdahalesi önermez. Ölçüm, ayar, devreye alma ve kabul işlemleri yetkin kişilerce; üretici talimatları, güncel standartlar ve saha risk değerlendirmesiyle yapılmalıdır. ALO186 bağımsız bilgilendirme platformudur; resmî kurum, EDAŞ, test laboratuvarı veya kabul mercii değildir.

## İnsan onayı

Teknik ve editoryal inceleme tamamlandıktan sonra PR konuşmasına yalnız yetkili repository kullanıcısı şu komutu eklemelidir:

```text
/cms approve ev-sarj-istasyonu-internet-kesintisi-ocpp-offline-islem-kabul
```

AI ve bot yorumları onay sayılmaz. Onay workflow’u canonical HTML, routing overlay ve ChatGPT Sites önizleme artifactını üretir; PR ayrıca insan merge’i olmadan canlıya çıkmaz.
