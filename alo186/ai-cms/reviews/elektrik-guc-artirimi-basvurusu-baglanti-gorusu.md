# ALO186 AI CMS insan inceleme paketi

## İçerik

- **Başlık:** Elektrik Güç Artırımı Başvurusu ve Bağlantı Görüşü
- **H1:** Elektrik güç artırımı başvurusu nasıl hazırlanır, bağlantı görüşünde ne incelenir?
- **Canonical adayı:** `/haberler/elektrik-guc-artirimi-basvurusu-baglanti-gorusu`
- **Birincil anahtar ifade:** `elektrik güç artırımı başvurusu`
- **Risk sınıfı:** `legal`
- **Fırsat puanı:** **97/100**
- **AI CMS kalite hedefi:** **100/100**
- **Durum:** `review` — canonical HTML veya routing overlay henüz yok

## Kullanıcı görevi

Konut veya işletmede yeni cihazlar nedeniyle mevcut bağlantı gücü yetersiz kaldığında, dağıtım şirketine güç artırımı talebini teknik ve belgeye dayalı biçimde hazırlamak.

## Doğrudan cevap

Elektrik güç artırımı, yalnız ana sigortayı büyütmek değildir. Önce mevcut bağlantı ve sözleşme gücü, sayaç ve koruma düzeni, eşzamanlı yükler, kablo ve pano kapasitesi ile yeni talep gücü yetkili proje çalışmasıyla belirlenir. Ardından ilgili dağıtım şirketine güncel proje ve istenen belgelerle başvurulur; şebeke kapasitesi, bağlantı seviyesi, trafo veya hat yatırımı gerekip gerekmediği bağlantı görüşünde değerlendirilir. Kullanıcı, proje onayı ve dağıtım şirketi süreci tamamlanmadan sigorta veya kabloyu tek başına büyütmemelidir.

## Mevcut içerikten görev ayrımı

Mevcut EV tesisat uygunluğu ve dinamik yük yönetimi sayfaları cihaz/tesis uyumunu ele alır. Yeni içerik, dağıtım şirketine güç artırımı için yük cetveli, proje, bağlantı görüşü, şebeke kapasitesi ve kabul dosyasını ayrı bir resmî süreç olarak kurar.

Tahmini en yüksek başlık/H1 benzerliği: **0.310** — en yakın rota: `/haberler/ev-sarj-cihazi-icin-ev-tesisati-uygun-mu`. Fail-closed AI CMS doğrulaması gerçek envanter üzerinde yeniden hesaplar; `0,78` veya üzeri benzerlikte onay durmalıdır.

## Bölümler ve kaynak bağı

- **Güç artırımı gerekip gerekmediği nasıl anlaşılır?** — S1, S2, S3
- **Başvuru öncesinde hangi teknik dosya hazırlanmalıdır?** — S1, S2, S4
- **Dağıtım şirketi bağlantı görüşünde neyi değerlendirir?** — S1, S2
- **Onay sonrasında tesis tadili ve kabul nasıl yönetilir?** — S1, S3
- **Kullanıcı hangi sonuç dosyasını saklamalıdır?** — S2, S3, S4

## Kaynak doğrulaması

| Ref | Yayıncı | Kaynak | Erişim | Birincil |
|---|---|---|---|---|
| S1 | EPDK | Elektrik Piyasası Bağlantı ve Sistem Kullanım Yönetmeliği | 2026-08-03 | Evet |
| S2 | EPDK | Elektrik bağlantı talepleri ve tüketici bilgilendirmesi | 2026-08-03 | Evet |
| S3 | EPDK | Elektrikli araç şarj ünitesi kurulum süreci | 2026-08-03 | Evet |
| S4 | EPDK | Elektrik piyasası güncel yönetmelikler listesi | 2026-08-03 | Evet |

Bütün teknik ve hukukî iddialar yalnız içerik kaydındaki `factSummary` ve ilgili `S#` kaynak referanslarına dayanmalıdır. Güncel mevzuat, üretici sürümü ve dağıtım şirketi şartları yayın öncesi tekrar doğrulanmalıdır.

## İç bağlantılar

- `/edas-bul` — Güç artırımı için bölgedeki resmî dağıtım şirketi kanalını doğrular.
- `/haberler/elektrik-arizasinda-edas-mi-tedarikci-mi-aranir` — Teknik bağlantı süreci ile enerji satış sözleşmesini ayırır.
- `/haberler/ev-sarj-cihazi-icin-ev-tesisati-uygun-mu` — Yeni şarj yükünün mevcut tesis ve güç kapasitesine etkisini bağlama alır.
- `/haberler/ev-sarjinda-dinamik-yuk-yonetimi` — Güç artışına alternatif olabilecek kontrollü yük paylaşımını açıklar.
- `/hesaplama/kablo-gerilim-dusumu/` — Yeni güçte besleme hattının gerilim düşümü ön kontrolünü destekler.
- `/haberler/faz-dengesizligi-faz-kaybi-motoru-nasil-etkiler` — Talep gücünün fazlara dengeli dağıtılması gereğini tamamlar.
- `/kurumsal-elektrik-surekliligi-on-degerlendirme` — İşletme ve otellerde yük envanteri ile teknik kapsamı profesyonel değerlendirmeye taşır.

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

Dönüşüm çağrısı; kişisel verisiz yük cetveli, mevcut-yeni güç matrisi, EDAŞ bulma ve yetkili proje/ön değerlendirme akışıdır. ALO186 başvuru almaz. Enerjili pano ve tesis tadili yalnız yetkin personel sınırındadır; affiliate kapalıdır.

## İnsan onayı

Teknik içerik, kaynak, görev ayrımı, iç bağlantılar ve güvenlik sınırı kabul edilirse PR konuşmasına tam olarak şu yorum eklenmelidir:

```text
/cms approve elektrik-guc-artirimi-basvurusu-baglanti-gorusu
```

AI veya otomasyon bu komutu veremez. Onay sonrasında canonical HTML, routing overlay ve ChatGPT Sites önizleme artifactı oluşur; zorunlu kontroller geçmeden merge edilmemelidir.
