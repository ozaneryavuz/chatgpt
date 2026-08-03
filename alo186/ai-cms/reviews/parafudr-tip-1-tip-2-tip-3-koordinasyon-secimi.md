# ALO186 AI CMS insan inceleme paketi

## İçerik

- **Başlık:** Parafudr Tip 1, Tip 2, Tip 3 Farkı ve Koordinasyonu
- **H1:** Tip 1, Tip 2 ve Tip 3 parafudr nerede kullanılır, birlikte nasıl koordine edilir?
- **Canonical adayı:** `/haberler/parafudr-tip-1-tip-2-tip-3-koordinasyon-secimi`
- **Birincil anahtar ifade:** `Tip 1 Tip 2 Tip 3 parafudr farkı`
- **Risk sınıfı:** `high`
- **Fırsat puanı:** **93/100**
- **AI CMS kalite hedefi:** **100/100**
- **Durum:** `review` — canonical HTML veya routing overlay henüz yok

## Kullanıcı görevi

Bir yapıda yıldırım ve anahtarlama kaynaklı geçici aşırı gerilim riskine göre Tip 1, Tip 2 ve Tip 3 SPD katmanlarını, yerleşim ve enerji koordinasyonuyla doğru planlamak.

## Doğrudan cevap

Tip 1, yıldırım akımının bir bölümünü bina girişinde yönetmek için; Tip 2, ana ve tali panolarda kalan geçici aşırı gerilimi sınırlamak için; Tip 3 ise hassas cihaza yakın son koruma katmanı olarak kullanılır. Bunlar birbirinin rastgele alternatifi değildir: dış yıldırımlık, havai hat, bina beslemesi, pano mesafeleri, topraklama sistemi, kısa devre dayanımı, Uc-Up-Iimp-In değerleri ve üreticinin enerji koordinasyon tabloları birlikte değerlendirilmelidir. Tip 3 tek başına yüksek enerjili darbeye karşı bina koruması sağlamaz; Tip 1 bulunan tesiste de aşağı akış Tip 2 veya birleşik çözüm gerekebilir.

## Mevcut içerikten görev ayrımı

Mevcut SPD etiket değerleri, bağlantı uzunluğu, yedek sigorta ve gösterge içerikleri tekil seçim ayrıntılarını açıklar. Yeni içerik, Tip 1, Tip 2 ve Tip 3 katmanlarının bina boyunca yerleşim ve enerji koordinasyonunu tek karar matrisi olarak kurar.

Tahmini en yüksek başlık/H1 benzerliği: **0.460** — en yakın rota: `/haberler/parafudr-uc-up-in-imax-iimp-ne-demek`. Fail-closed AI CMS doğrulaması gerçek envanter üzerinde yeniden hesaplar; `0,78` veya üzeri benzerlikte onay durmalıdır.

## Bölümler ve kaynak bağı

- **Tip 1, Tip 2 ve Tip 3 SPD’nin görevleri nelerdir?** — S1, S3, S4
- **Hangi binada hangi koruma katmanı gerekir?** — S2, S3, S4
- **Uc, Up, Iimp, In ve Imax nasıl birlikte okunur?** — S1, S2, S5
- **Katmanlar arasındaki enerji koordinasyonu nasıl doğrulanır?** — S2, S4, S5
- **Devreye alma ve bakım kabul dosyasında neler bulunmalıdır?** — S1, S3, S4, S5

## Kaynak doğrulaması

| Ref | Yayıncı | Kaynak | Erişim | Birincil |
|---|---|---|---|---|
| S1 | IEC | IEC 61643-11:2025 — AC alçak gerilim sistemleri için SPD gerekleri | 2026-08-03 | Evet |
| S2 | IEC | IEC 60364-5-53:2019+A1:2020+A2:2024 | 2026-08-03 | Evet |
| S3 | Schneider Electric | What is a surge protection device and how does it work? | 2026-08-03 | Evet |
| S4 | DEHN | Surge protection for industrial buildings — three-stage protection principle | 2026-08-03 | Evet |
| S5 | Schneider Electric | How to select an SPD for an entire installation? | 2026-08-03 | Evet |

Bütün teknik ve hukukî iddialar yalnız içerik kaydındaki `factSummary` ve ilgili `S#` kaynak referanslarına dayanmalıdır. Güncel mevzuat, üretici sürümü ve dağıtım şirketi şartları yayın öncesi tekrar doğrulanmalıdır.

## İç bağlantılar

- `/hesaplama/parafudr-risk-testi/` — Yapı ve besleme koşullarına göre ilk risk sınıflandırmasını sağlar.
- `/haberler/parafudr-gerilim-koruma-rolesi-farki` — Geçici darbe korumasını sürekli düşük-yüksek gerilim korumasından ayırır.
- `/haberler/parafudr-uc-up-in-imax-iimp-ne-demek` — SPD etiket değerlerini ayrıntılı okumayı destekler.
- `/haberler/parafudr-baglanti-kablosu-neden-kisa-olmali` — Gerçek koruma seviyesini etkileyen bağlantı endüktansını açıklar.
- `/haberler/parafudr-yedek-sigorta-scpd-nasil-secilir` — Kısa devre ve üretici SCPD koordinasyonunu tamamlar.
- `/haberler/parafudr-gostergesi-kirmizi-ne-demek` — Bakım ve modül değişim kararını destekler.
- `/hesaplama/gerilim-koruma-cozum-secici/` — Darbe, sürekli gerilim ve kesinti sorunlarını doğru çözüm sınıfına ayırır.

## AEO / SEO ve yapılandırılmış veri

- benzersiz title, meta description, H1 ve canonical adayı;
- ilk ekranda bağımsız doğrudan cevap;
- beş kaynak bağlı bölüm ve dört görünür SSS;
- kurumsal `Organization` yazarlığı;
- canonical derleyicide `Article`, `FAQPage` ve `BreadcrumbList`;
- `Product`, `Offer`, `Person` ve `ProfilePage` yasağı;
- kaynak erişim tarihi ve görünür atıf zinciri;
- kullanıcıya teslim edilebilir kontrol, başvuru veya kabul dosyası.

## Güvenlik ve dönüşüm sınırı

Dönüşüm çağrısı; SPD risk testi, Tip 1-2-3 yerleşim matrisi, üretici koordinasyon tablosu ve profesyonel pano değerlendirmesidir. Enerjili sabit tesisata kullanıcı müdahalesi önerilmez; fiyat, stok ve ürün garantisi yayımlanmaz; affiliate kapalıdır.

## İnsan onayı

Teknik içerik, kaynak, görev ayrımı, iç bağlantılar ve güvenlik sınırı kabul edilirse PR konuşmasına tam olarak şu yorum eklenmelidir:

```text
/cms approve parafudr-tip-1-tip-2-tip-3-koordinasyon-secimi
```

AI veya otomasyon bu komutu veremez. Onay sonrasında canonical HTML, routing overlay ve ChatGPT Sites önizleme artifactı oluşur; zorunlu kontroller geçmeden merge edilmemelidir.
