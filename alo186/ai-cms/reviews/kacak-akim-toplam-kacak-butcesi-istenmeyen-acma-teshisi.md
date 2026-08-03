# ALO186 AI CMS insan inceleme paketi

## İçerik

- **Başlık:** Toplam Kaçak Akım Bütçesi ve RCD Açma Teşhisi
- **H1:** Toplam kaçak akım bütçesi nasıl çıkarılır ve RCD neden gereksiz açar?
- **Canonical adayı:** `/haberler/kacak-akim-toplam-kacak-butcesi-istenmeyen-acma-teshisi`
- **Birincil anahtar ifade:** `toplam kaçak akım bütçesi`
- **Risk sınıfı:** `high`
- **Fırsat puanı:** **95/100**
- **AI CMS kalite hedefi:** **100/100**
- **Durum:** `review` — canonical HTML veya routing overlay henüz yok

## Kullanıcı görevi

Bir tesiste tekrarlayan kaçak akım rölesi açmalarının gerçek izolasyon arızasından mı, biriken normal kaçak akımlardan mı veya anahtarlama darbelerinden mi kaynaklandığını kanıt dosyasıyla ayırmak.

## Doğrudan cevap

RCD’nin sık açması her zaman tek bir arızalı cihaz olduğu anlamına gelmez. UPS, inverter, EVSE, LED sürücüler ve IT güç kaynaklarının EMI filtreleri koruma iletkenine normal çalışma akımı taşıyabilir; aynı koruma cihazı altındaki yükler arttıkça bu akımlar toplanır ve anahtarlama anındaki kısa darbelerle açma eşiğine yaklaşabilir. Güvenli teşhis; devre topolojisi, RCD tipi, nötr karışması, sürekli ve olay anı kaçak akım ölçümü ile yüklerin kontrollü ayrılmasını birlikte kaydetmelidir. Koruma cihazını büyütmek, köprülemek veya iptal etmek ölçüm yerine geçmez.

## Mevcut içerikten görev ayrımı

Mevcut “kaçak akım rölesi neden sürekli atar?” rehberinden farklı olarak tek cihaz arızası belirtilerini değil; çoklu elektronik yüklerin sürekli ve geçici artık akımlarını devre bazında toplayan ölçüm bütçesi, nötr karışması ve öncesi–sonrası kabul dosyasını hedefler.

Tahmini en yüksek başlık/H1 benzerliği: **0.320** — en yakın rota: `/haberler/kacak-akim-rolesi-neden-surekli-atar`. Fail-closed AI CMS doğrulaması gerçek envanter üzerinde yeniden hesaplar; `0,78` veya üzeri benzerlikte onay durmalıdır.

## Bölümler ve kaynak bağı

- **Gerçek izolasyon arızası ile toplam normal kaçak akımı nasıl ayırırsınız?** — S1, S2, S3
- **Kaçak akım bütçesi hangi ölçümlerle hazırlanmalıdır?** — S2, S3, S4
- **RCD tipi, hassasiyet ve selektivite kararı nasıl verilmelidir?** — S1, S2, S3
- **Kontrollü yük ayırma ve onarım sonrası kabul nasıl yapılır?** — S1, S2, S4
- **Teknik kanıt dosyası hangi sonucu üretmelidir?** — S1, S2, S3, S4

## Kaynak doğrulaması

| Ref | Yayıncı | Kaynak | Erişim | Birincil |
|---|---|---|---|---|
| S1 | IEC | IEC 60364-5-53:2019+A1:2020+A2:2024 — Koruma ve anahtarlama cihazlarının seçimi | 2026-08-03 | Evet |
| S2 | Schneider Electric | UPS tesislerinde RCD, toprak kaçağı ve istenmeyen açma | 2026-08-03 | Evet |
| S3 | Schneider Electric | UPS giriş tarafında RCD ve kümülatif kaçak akım | 2026-08-03 | Evet |
| S4 | Schneider Electric | Arıza olmadan toprak kaçağı korumasının açma nedenleri | 2026-08-03 | Evet |

Bütün teknik iddialar yalnız içerik kaydındaki `factSummary` ve ilgili `S#` kaynak referanslarına dayanmalıdır. Evrensel eşik, garanti, fiyat, stok veya resmî onay iddiası eklenmemelidir.

## İç bağlantılar

- `/haberler/kacak-akim-rolesi-neden-surekli-atar` — Genel arıza belirtilerini ölçüm bütçesi görevinden ayırır.
- `/haberler/kacak-akim-rolesi-tip-a-tip-ac-farki` — Artık akım dalga biçimi ve koruma tipi temelini açıklar.
- `/haberler/kacak-akim-rolesi-tip-s-selektivite-nedir` — Üst ve alt kademe zaman koordinasyonuna bağlar.
- `/haberler/kacak-akim-rolesi-tip-f-nedir-inverterli-cihazlar` — Frekans bileşenli yüklerin koruma gereğini destekler.
- `/haberler/ev-sarj-istasyonu-tip-b-rcd-rdc-dd-secimi` — EVSE kaynaklı DC artık akım görevini ayırır.
- `/haberler/ups-sebeke-varken-bataryaya-geciyor` — Transfer olayları ve şebeke kalitesi loglarına bağlar.
- `/kurumsal-elektrik-surekliligi-on-degerlendirme` — Çok devreli tesislerde yetkili ölçüm ve kabul kapsamına geçiş sağlar.

## AEO / SEO ve yapılandırılmış veri

- benzersiz title, meta description, H1 ve canonical adayı;
- ilk ekranda bağımsız doğrudan cevap;
- beş kaynak bağlı bölüm ve dört görünür SSS;
- kurumsal `Organization` yazarlığı;
- canonical derleyicide `Article`, `FAQPage` ve `BreadcrumbList`;
- `Product`, `Offer`, `Person` ve `ProfilePage` yasağı;
- kaynak erişim tarihi ve görünür atıf zinciri;
- kullanıcıya teslim edilebilir kaçak bütçesi ve kabul dosyası.

## Güvenlik ve dönüşüm sınırı

Dönüşüm çağrısı; kişisel verisiz kaçak akım bütçesi şablonu, devre/olay ölçüm matrisi ve kurumsal teknik ön değerlendirmedir. Affiliate ve ürün satın alma yolu kapalıdır. Enerjili pano, RCD, nötr veya koruma iletkeni üzerinde kullanıcı müdahalesi önerilmez.

## İnsan onayı

Teknik içerik, kaynak, görev ayrımı, iç bağlantılar ve güvenlik sınırı kabul edilirse PR konuşmasına tam olarak şu yorum eklenmelidir:

```text
/cms approve kacak-akim-toplam-kacak-butcesi-istenmeyen-acma-teshisi
```

AI veya otomasyon bu komutu veremez. Onay sonrasında canonical HTML, routing overlay ve ChatGPT Sites önizleme artifactı oluşur; zorunlu kontroller geçmeden merge edilmemelidir.
