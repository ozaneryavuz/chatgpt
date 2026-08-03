# ALO186 AI CMS insan inceleme paketi

## İçerik

- **Başlık:** Elektrik Kesintisi Tazminatı Sorgulama Rehberi
- **H1:** Elektrik kesintisi tazminatı nasıl sorgulanır ve kanıtlanır?
- **Canonical adayı:** `/haberler/elektrik-kesintisi-tazminati-sorgulama-yillik-12-saat`
- **Birincil anahtar ifade:** `elektrik kesintisi tazminatı sorgulama`
- **Risk sınıfı:** `legal`
- **Fırsat puanı:** **96/100**
- **AI CMS kalite hedefi:** **100/100**
- **Durum:** `review` — canonical HTML veya routing overlay henüz yok

## Kullanıcı görevi

Kullanıcının yıllık veya 12 saati aşan elektrik kesintisi tazminatını cihaz hasarı talebiyle karıştırmadan sorgulaması, kayıtları doğrulaması ve eksik ödeme için kanıtlı başvuru yapması.

## Doğrudan cevap

Elektrik kesintisi tazminatı, cihaz hasarı başvurusundan farklı bir süreçtir. EPDK’nın yayımladığı çerçevede yıllık süre veya kesinti sayısı sınırları aşıldığında ödeme kural olarak başvuru aranmadan hesaplanır; ayrıca bildirimli ya da bildirimsiz 12 saati aşan kesintiler için uzun süreli kesinti tazminatı gündeme gelebilir. Kullanıcı önce kendi dağıtım şirketini, kesinti tarih-saatlerini ve ödeme/mahsup kaydını doğrulamalı; sonuç yoksa dağıtım şirketine yazılı başvuru yapıp yanıt ve belgelerle EPDK’ya ilerlemelidir.

## Mevcut içerikten görev ayrımı

Mevcut cihaz hasarı ve planlı kesinti içeriklerinden farklı olarak yıllık kalite tazminatı, 12 saat üzeri kesinti, otomatik ödeme/mahsup ve EPDK eskalasyon dosyasına odaklanır.

Tahmini en yüksek başlık/H1 benzerliği: **0.280** — en yakın rota: `/haberler/elektrik-kesintisi-cihaz-hasari-edas-basvurusu`. Fail-closed AI CMS doğrulaması gerçek envanter üzerinde yeniden hesaplar; `0,78` veya üzeri benzerlikte onay durmalıdır.

## Bölümler ve kaynak bağı

- **Yıllık tazminat, 12 saat tazminatı ve cihaz hasarı nasıl ayrılır?** — S1, S2
- **Başvurusuz hesaplanan ödeme nereden ve ne zaman kontrol edilir?** — S1, S3, S4
- **Kesinti kayıtları uyuşmuyorsa kanıt dosyası nasıl hazırlanır?** — S1, S2, S4
- **Dağıtım şirketine başvuru hangi sırayla yapılmalıdır?** — S1, S3
- **Dağıtım şirketi sonucu çözmezse EPDK dosyası nasıl kurulur?** — S1, S2

## Kaynak doğrulaması

| Ref | Yayıncı | Kaynak | Erişim | Birincil |
|---|---|---|---|---|
| S1 | EPDK | Elektrik tüketicileri için tedarik sürekliliği ve şikâyetler hakkında sık sorulan sorular | 2026-08-03 | Evet |
| S2 | EPDK | Elektrik piyasası yürürlükteki yönetmelikler | 2026-08-03 | Evet |
| S3 | Enerjisa Online | Başvuru işlemleri ve ticari kalite tazminatı sorgusu | 2026-08-03 | Evet |
| S4 | Enerjisa Online | Elektrik kesintileri sorgulama | 2026-08-03 | Evet |

Bütün teknik ve hukukî iddialar yalnız içerik kaydındaki `factSummary` ve ilgili `S#` kaynak referanslarına dayanmalıdır. Evrensel eşik, garanti, fiyat, stok veya resmî onay iddiası eklenmemelidir.

## İç bağlantılar

- `/edas-bul` — Faturadaki bölgeye göre doğru dağıtım şirketi ve resmî kanalı buldurur.
- `/haberler/planli-elektrik-kesintisi-ne-kadar-once-bildirilir` — Bildirimli ve bildirimsiz kesinti ayrımını açıklar.
- `/haberler/elektrik-kesintisi-cihaz-hasari-edas-basvurusu` — Cihaz zararını kalite tazminatından ayrı dosyada yönetir.
- `/haberler/elektrik-arizasinda-edas-mi-tedarikci-mi-aranir` — Dağıtım ve tedarik görev ayrımını netleştirir.
- `/hesaplama/kesinti-gunlugu` — Olay tarih ve sürelerini kişisel verisiz kaydetmeye yardım eder.
- `/hesaplama/kesinti-maliyeti` — Tazminattan bağımsız işletme etkisini ölçer.
- `/karar-motoru` — Acil tehlike, 186 ve teknik destek ayrımını yapar.

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

Bu içerik `legal` risk sınıfındadır. Affiliate ve ürün satın alma CTA’sı kapalıdır. Dönüşüm çağrısı; kişisel verisiz kesinti günlüğü, doğru EDAŞ bulma, resmî sorgu ve belge sıralı başvuru dosyasıdır. ALO186 hak sahipliği veya kesin ödeme tutarı garantisi vermez.

## İnsan onayı

Teknik içerik, kaynak, görev ayrımı, iç bağlantılar ve güvenlik sınırı kabul edilirse PR konuşmasına tam olarak şu yorum eklenmelidir:

```text
/cms approve elektrik-kesintisi-tazminati-sorgulama-yillik-12-saat
```

AI veya otomasyon bu komutu veremez. Onay sonrasında canonical HTML, routing overlay ve ChatGPT Sites önizleme artifactı oluşur; zorunlu kontroller geçmeden merge edilmemelidir.
