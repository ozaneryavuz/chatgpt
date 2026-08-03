# ALO186 AI CMS insan inceleme paketi

## İçerik

- **Başlık:** UPS Giriş THDi ve Jeneratör Uyumluluk Kabulü
- **H1:** UPS giriş THDi değeri jeneratör seçimini ve kararlı çalışmayı nasıl etkiler?
- **Canonical adayı:** `/haberler/ups-giris-thdi-jenerator-uyumluluk-kabul-testi`
- **Birincil anahtar ifade:** `UPS giriş THDi`
- **Risk sınıfı:** `high`
- **Fırsat puanı:** **91/100**
- **AI CMS kalite hedefi:** **100/100**
- **Durum:** `review` — canonical HTML veya routing overlay henüz yok

## Kullanıcı görevi

Bir UPS ile jeneratörün yalnız nominal kVA üzerinden değil, giriş THDi, maksimum giriş akımı, akü şarjı, ramp-in, AVR ve frekans davranışıyla uyumlu olup olmadığını sahada kanıtlamak.

## Doğrudan cevap

UPS ile jeneratör uyumu yalnız UPS çıkış kVA’sını bir katsayıyla büyütmek değildir. Jeneratör, UPS’nin gerçek maksimum giriş akımını, akü yeniden şarj gücünü, ramp-in süresini, giriş güç faktörünü ve THDi kaynaklı akım dalga biçimini; aynı baradaki motor ve diğer yüklerle birlikte kararlı taşımalıdır. Kabul testi jeneratör boşta çalışmadan başlayıp UPS doğrultucusunun devreye girmesi, yük basamakları, akü şarjı, transfer, bypass senkronu ve geri dönüş boyunca gerilim, frekans, akım, THDi ve olay loglarını kaydetmelidir. Evrensel bir aşırı boyutlandırma oranı yerine UPS ve jeneratör üretici verileri ile gerçek saha testi kullanılmalıdır.

## Mevcut içerikten görev ayrımı

Mevcut “jeneratör ve UPS birlikte çalışır mı?” içeriği temel uyumluluğu açıklar. Yeni içerik, UPS maksimum giriş akımı, THDi, akü şarjı, ramp-in, AVR/governor davranışı ve ortak yükleri içeren ölçümlü devreye alma kabulüne odaklanır.

Tahmini en yüksek başlık/H1 benzerliği: **0.340** — en yakın rota: `/haberler/jenerator-ups-birlikte-calisir-mi`. Fail-closed AI CMS doğrulaması gerçek envanter üzerinde yeniden hesaplar; `0,78` veya üzeri benzerlikte onay durmalıdır.

## Bölümler ve kaynak bağı

- **Nominal kVA dışında hangi UPS giriş verileri gerekir?** — S1, S2, S3
- **Giriş THDi jeneratör gerilimini ve AVR davranışını nasıl etkileyebilir?** — S2, S3, S4
- **Akü şarjı, ramp-in ve yük sıralaması neden kritik olur?** — S2, S3, S4
- **UPS–jeneratör saha kabul testi hangi adımları içermelidir?** — S1, S2, S3, S4
- **Boyutlandırma dosyası hangi kararı üretmelidir?** — S1, S2, S3, S4

## Kaynak doğrulaması

| Ref | Yayıncı | Kaynak | Erişim | Birincil |
|---|---|---|---|---|
| S1 | IEC | IEC 62040-3:2021 — UPS performans ve test gerekleri | 2026-08-03 | Evet |
| S2 | Schneider Electric | Easy UPS 3L 250–400 kVA giriş ve bypass özellikleri | 2026-08-03 | Evet |
| S3 | Schneider Electric | Easy UPS 3S 380/400/415 V teknik özellikleri | 2026-08-03 | Evet |
| S4 | Schneider Electric | Easy UPS 3L normal mod başlatma ve doğrultucu rampası | 2026-08-03 | Evet |

Bütün teknik iddialar yalnız içerik kaydındaki `factSummary` ve ilgili `S#` kaynak referanslarına dayanmalıdır. Tek bir evrensel jeneratör büyütme katsayısı veya marka bağımsız ayar eşiği yayımlanmamalıdır.

## İç bağlantılar

- `/haberler/jenerator-ups-birlikte-calisir-mi` — Temel topoloji ve uyumluluk kavramını ayrıntılı kabul görevine bağlar.
- `/haberler/jenerator-voltaj-frekans-dalgalanmasi-neden-olur` — AVR, governor ve yük basamağı belirtilerini açıklar.
- `/haberler/ups-sebeke-varken-bataryaya-geciyor` — Giriş toleransı ve olay logu teşhisine bağlar.
- `/haberler/ups-online-line-interactive-offline-farki` — UPS topolojisinin jeneratör davranışına etkisini temellendirir.
- `/haberler/ups-overload-asiri-yuk-alarmi-neden-verir` — Çıkış yükü ile giriş/jeneratör kapasitesini ayırır.
- `/hesaplama/jenerator-gucu-secimi` — Ön boyutlandırmayı teknik kabul dosyasına bağlar.
- `/kurumsal-elektrik-surekliligi-on-degerlendirme` — UPS ve jeneratör saha kabul kapsamını profesyonel çalışmaya taşır.

## AEO / SEO ve yapılandırılmış veri

- benzersiz title, meta description, H1 ve canonical adayı;
- ilk ekranda bağımsız doğrudan cevap;
- beş kaynak bağlı bölüm ve dört görünür SSS;
- kurumsal `Organization` yazarlığı;
- canonical derleyicide `Article`, `FAQPage` ve `BreadcrumbList`;
- `Product`, `Offer`, `Person` ve `ProfilePage` yasağı;
- kaynak erişim tarihi ve görünür atıf zinciri;
- UPS giriş verisi, yük sırası ve gerçek saha kabul dosyası.

## Güvenlik ve dönüşüm sınırı

Dönüşüm çağrısı; UPS–jeneratör giriş veri matrisi, yük sıralama senaryosu ve sahada yetkili kabul testidir. Affiliate ve doğrudan ekipman satın alma çağrısı kapalıdır. UPS, ATS, jeneratör, bypass ve enerjili pano ayarları kullanıcı işlemi olarak sunulmaz.

## İnsan onayı

Teknik içerik, kaynak, görev ayrımı, iç bağlantılar ve güvenlik sınırı kabul edilirse PR konuşmasına tam olarak şu yorum eklenmelidir:

```text
/cms approve ups-giris-thdi-jenerator-uyumluluk-kabul-testi
```

AI veya otomasyon bu komutu veremez. Onay sonrasında canonical HTML, routing overlay ve ChatGPT Sites önizleme artifactı oluşur; zorunlu kontroller geçmeden merge edilmemelidir.
