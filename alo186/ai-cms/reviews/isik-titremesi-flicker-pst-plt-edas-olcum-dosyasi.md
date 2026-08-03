# ALO186 AI CMS insan inceleme paketi

## İçerik

- **Başlık:** Işık Titremesi: Pst, Plt ve EDAŞ Ölçüm Dosyası
- **H1:** Işık titremesinde Pst ve Plt nasıl ölçülür, EDAŞ’a hangi kanıtla başvurulur?
- **Canonical adayı:** `/haberler/isik-titremesi-flicker-pst-plt-edas-olcum-dosyasi`
- **Birincil anahtar ifade:** `ışık titremesi Pst Plt`
- **Risk sınıfı:** `legal`
- **Fırsat puanı:** **93/100**
- **AI CMS kalite hedefi:** **100/100**
- **Durum:** `review` — canonical HTML veya routing overlay henüz yok

## Kullanıcı görevi

Tekrarlayan ışık titremesinin bina içi yükten mi yoksa dağıtım şebekesi gerilim dalgalanmasından mı kaynaklandığını Pst, Plt ve zaman eşleştirmeli ölçümle kanıtlamak.

## Doğrudan cevap

Işık titremesi yaşanırken el tipi voltmetrenin 230 V göstermesi sorunu dışlamaz; insan gözünün algıladığı hızlı gerilim dalgalanmaları ortalama değerde kaybolabilir. Pst kısa dönem, Plt uzun dönem flicker şiddetini standartlaştırılmış flickermetre yöntemiyle değerlendirir. Güvenilir dosya; uygun güç kalitesi analizörüyle zaman damgalı gerilim ve akım kaydı, Pst/Plt trendi, faz bazlı karşılaştırma, büyük yerel yüklerin açma-kapama saatleri ve komşu/bina gözlemlerini birleştirmelidir. Şikâyet teknik kalite kapsamında dağıtım şirketine ölçüm talebiyle iletilir; kullanıcı ALO186’e abonelik veya adres verisi göndermemelidir.

## Mevcut içerikten görev ayrımı

Mevcut düşük/yüksek gerilim EDAŞ ölçüm rehberi kalıcı RMS seviye şikâyetini ele alır. Yeni içerik, anlık voltmetrede görünmeyen ışık titremesini Pst, Plt, faz/yük korelasyonu ve resmî teknik kalite ölçüm talebiyle ayrı bir göreve dönüştürür.

Tahmini en yüksek başlık/H1 benzerliği: **0.280** — en yakın rota: `/haberler/elektrik-gerilimi-dusuk-yuksek-edas-olcum-talebi`. Fail-closed AI CMS doğrulaması gerçek envanter üzerinde yeniden hesaplar; `0,78` veya üzeri benzerlikte onay durmalıdır.

## Bölümler ve kaynak bağı

- **Lamba titremesi neden anlık voltmetrede görünmeyebilir?** — S1, S2
- **Pst ve Plt hangi ölçüm zinciriyle kaydedilmelidir?** — S1, S2, S3
- **Yerel yük ile dağıtım şebekesi kaynağı nasıl ayrılır?** — S2, S3
- **EDAŞ teknik kalite ölçüm talebi nasıl hazırlanmalıdır?** — S4, S5
- **Düzeltme sonrası kabul ve izleme nasıl yapılmalıdır?** — S2, S3, S4, S5

## Kaynak doğrulaması

| Ref | Yayıncı | Kaynak | Erişim | Birincil |
|---|---|---|---|---|
| S1 | IEC | IEC 61000-4-15:2010 — Flickermetre işlevsel ve tasarım özellikleri | 2026-08-03 | Evet |
| S2 | Fluke | Fluke 1742, 1746 ve 1748 güç kalitesi kaydedicileri | 2026-08-03 | Evet |
| S3 | Fluke | Fluke 1760 üç fazlı güç kalitesi kaydedici teknik özellikleri | 2026-08-03 | Evet |
| S4 | EPDK | Teknik kaliteye ilişkin tüketici hak ve yükümlülükleri | 2026-08-03 | Evet |
| S5 | EPDK | Elektrik dağıtımı ve perakende satışına ilişkin hizmet kalitesi mevzuatı | 2026-08-03 | Evet |

Bütün teknik ve hukukî iddialar yalnız içerik kaydındaki `factSummary` ve ilgili `S#` kaynak referanslarına dayanmalıdır. Güncel mevzuat ve dağıtım şirketi başvuru şartları yayın öncesi tekrar doğrulanmalıdır.

## İç bağlantılar

- `/haberler/elektrik-gerilimi-dusuk-yuksek-edas-olcum-talebi` — Kalıcı gerilim seviyesi şikâyetini flicker görevinden ayırır.
- `/haberler/notr-kopmasi-nasil-anlasilir` — Titremeyle birlikte tehlikeli parlaklık ve faz gerilimi değişimini açıklar.
- `/haberler/faz-dengesizligi-faz-kaybi-motoru-nasil-etkiler` — Faz bazlı ölçüm ve motor yük etkisini destekler.
- `/haberler/kompanzasyon-panosu-reaktif-guc-neden-bozulur` — Anahtarlanan kapasitif yük ve tesis içi değişimleri bağlama alır.
- `/hesaplama/kesinti-gunlugu` — Tarih-saat ve gözlem kayıtlarını kişisel verisiz düzenler.
- `/edas-bul` — İl ve ilçeye göre resmî dağıtım şirketi kanalına yönlendirir.
- `/kurumsal-elektrik-surekliligi-on-degerlendirme` — Çok noktalı güç kalitesi ölçüm kapsamını profesyonel değerlendirmeye taşır.

## AEO / SEO ve yapılandırılmış veri

- benzersiz title, meta description, H1 ve canonical adayı;
- ilk ekranda bağımsız doğrudan cevap;
- beş kaynak bağlı bölüm ve dört görünür SSS;
- kurumsal `Organization` yazarlığı;
- canonical derleyicide `Article`, `FAQPage` ve `BreadcrumbList`;
- `Product`, `Offer`, `Person` ve `ProfilePage` yasağı;
- kaynak erişim tarihi ve görünür atıf zinciri;
- Pst/Plt, olay günlüğü ve resmî başvuru için somut kanıt dosyası.

## Güvenlik ve dönüşüm sınırı

Dönüşüm çağrısı; kişisel verisiz olay günlüğü, Pst/Plt ölçüm kapsamı, resmî EDAŞ bulma ve belge sıralı teknik kalite başvuru dosyasıdır. ALO186 başvuru veya abonelik verisi almaz. Enerjili panoda ölçüm yalnız yetkin personel sınırındadır; affiliate kapalıdır.

## İnsan onayı

Teknik içerik, kaynak, görev ayrımı, iç bağlantılar ve güvenlik sınırı kabul edilirse PR konuşmasına tam olarak şu yorum eklenmelidir:

```text
/cms approve isik-titremesi-flicker-pst-plt-edas-olcum-dosyasi
```

AI veya otomasyon bu komutu veremez. Onay sonrasında canonical HTML, routing overlay ve ChatGPT Sites önizleme artifactı oluşur; zorunlu kontroller geçmeden merge edilmemelidir.
