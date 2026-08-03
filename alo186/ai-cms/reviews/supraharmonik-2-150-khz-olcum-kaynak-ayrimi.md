# ALO186 AI CMS insan inceleme paketi

## İçerik

- **Başlık:** Supraharmonik 2–150 kHz Ölçüm ve Kaynak Ayrımı
- **H1:** THD normalken cihazlar neden etkilenir? Supraharmonik kanıt planı
- **Canonical adayı:** `/haberler/supraharmonik-2-150-khz-olcum-kaynak-ayrimi`
- **Birincil anahtar ifade:** `supraharmonik 2 150 kHz`
- **Risk sınıfı:** `high`
- **Fırsat puanı:** **90/100**
- **AI CMS kalite hedefi:** **100/100**
- **Durum:** `review` — canonical HTML veya routing overlay henüz yok

## Kullanıcı görevi

THD normal görünürken iletişim, şarj veya elektronik cihaz sorunlarına yol açabilen 2–150 kHz iletilen bileşenleri doğru ölçüm zinciri ve kaynak ayrımıyla kanıtlamak.

## Doğrudan cevap

THD’nin normal görünmesi 2–150 kHz iletilen bozucuların bulunmadığını kanıtlamaz. EV şarj cihazı, GES inverteri, UPS, LED sürücü veya güç hattı haberleşmesi bu bantta zamanla değişen bileşenler oluşturabilir. Doğru teşhis; 2–9 kHz ve 9–150 kHz için doğrulanmış sensör/analizör, ortak saatli kaynak-mağdur kaydı ve kontrollü A/B işletme senaryolarıyla yapılır; tek spektrum görüntüsünden filtre satın alma kararı verilmez.

## Mevcut içerikten görev ayrımı

Klasik THD/TDD/PCC içeriklerinden farklı olarak 2–150 kHz iletilen bileşenlerin ölçüm bant genişliği, zaman-frekans davranışı ve kaynak-mağdur ayrımını ele alır.

Tahmini en yüksek başlık/H1 benzerliği: **0.350** — en yakın rota: `/haberler/harmonik-nedir-thd-cihazlari-nasil-etkiler`. Fail-closed AI CMS doğrulaması gerçek envanter üzerinde yeniden hesaplar; `0,78` veya üzeri benzerlikte onay durmalıdır.

## Bölümler ve kaynak bağı

- **THD normal görünürken neden 2–150 kHz bozucu bileşen olabilir?** — S1, S2, S3
- **Hangi belirtiler supraharmonik incelemesini haklı kılar?** — S1, S3, S4
- **2–150 kHz ölçüm zinciri nasıl tanımlanmalıdır?** — S1, S2, S3
- **Kaynak, yayılım yolu ve etkilenen cihaz nasıl ayrılır?** — S2, S3, S4
- **İyileştirme kararı hangi kanıtlarla kabul edilmelidir?** — S1, S2, S3, S4

## Kaynak doğrulaması

| Ref | Yayıncı | Kaynak | Erişim | Birincil |
|---|---|---|---|---|
| S1 | IEC | IEC 61000-4-30:2025 — Power quality measurement methods | 2026-08-03 | Evet |
| S2 | IEC | IEC 61000-4-19:2014 — Immunity to 2 kHz–150 kHz differential-mode disturbances | 2026-08-03 | Evet |
| S3 | CIGRE | Assessment of conducted disturbances above 2 kHz in MV and LV power systems | 2026-08-03 | Evet |
| S4 | IEC | IEC 61000-2-4:2024 — Compatibility levels in industrial power systems | 2026-08-03 | Evet |

Bütün teknik iddialar yalnız içerik kaydındaki `factSummary` ve ilgili `S#` kaynak referanslarına dayanmalıdır. Evrensel ürün eşiği, garanti, fiyat, stok veya resmî onay iddiası eklenmemelidir.

## İç bağlantılar

- `/haberler/harmonik-nedir-thd-cihazlari-nasil-etkiler` — Klasik harmonik temelini 2–150 kHz görev ayrımı öncesinde açıklar.
- `/haberler/notr-akimi-faz-akimindan-yuksek-neden-olur` — Düşük frekanslı harmonik ve nötr yüklenmesi görevini supraharmonikten ayırır.
- `/haberler/detuned-reaktor-aktif-harmonik-filtre-farki` — Ölçüm yapılmadan filtre seçimini engelleyen ürün görev ayrımını tamamlar.
- `/haberler/ev-sarj-gucu-neden-dusuk-yavas-sarj` — Şarj gücü sınırlamasıyla EMC ve haberleşme girişimini birbirinden ayırır.
- `/haberler/ges-inverter-sebeke-gerilimi-yuksek-hatasi` — 50 Hz gerilim yükselmesi ile 2–150 kHz iletilen bileşenleri ayırır.
- `/haberler/inverter-dusuk-voltaj-alarmi-neden-verir` — DC besleme ve düşük gerilim arızalarını yüksek frekans girişiminden ayırır.
- `/kurumsal-elektrik-surekliligi-on-degerlendirme` — Çok noktalı güç kalitesi ve EMC ölçüm planını profesyonel sürece bağlar.

## AEO / SEO ve yapılandırılmış veri

- benzersiz title, meta description, H1 ve canonical adayı;
- ilk ekranda bağımsız doğrudan cevap;
- beş kaynak bağlı bölüm ve dört görünür SSS;
- kurumsal `Organization` yazarlığı;
- canonical derleyicide `Article`, `FAQPage` ve `BreadcrumbList`;
- `Product`, `Offer`, `Person` ve `ProfilePage` yasağı;
- kaynak erişim tarihi ve görünür atıf zinciri;
- kullanıcıya teslim edilebilir ölçüm/kabul dosyası.

## Güvenlik ve dönüşüm sınırı

Bu içerik `high` risk sınıfındadır. Affiliate ve ürün satın alma CTA’sı kapalıdır. Enerjili pano, PV DC bağlantısı, makine güvenlik zinciri veya yüksek frekans ölçümü kullanıcı işlemi olarak sunulamaz. Dönüşüm çağrısı; kişisel verisiz kontrol listesi, teknik kanıt dosyası ve yetkili profesyonel ön değerlendirmedir. Mevcut sistem ölçüm ve kayıtlarla yeterliyse satın almama sonucu korunur.

## İnsan onayı

Teknik içerik, kaynak, görev ayrımı, iç bağlantılar ve güvenlik sınırı kabul edilirse PR konuşmasına tam olarak şu yorum eklenmelidir:

```text
/cms approve supraharmonik-2-150-khz-olcum-kaynak-ayrimi
```

AI veya otomasyon bu komutu veremez. Onay sonrasında canonical HTML, routing overlay ve ChatGPT Sites önizleme artifactı oluşur; zorunlu kontroller geçmeden merge edilmemelidir.
