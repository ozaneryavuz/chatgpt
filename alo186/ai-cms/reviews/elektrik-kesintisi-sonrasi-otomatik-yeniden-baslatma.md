# ALO186 AI CMS insan inceleme paketi

## İçerik

- **Başlık:** Kesinti Sonrası Otomatik Yeniden Başlatma Güvenliği
- **H1:** Elektrik gelince makine neden kendiliğinden başlamamalı? Kabul planı
- **Canonical adayı:** `/haberler/elektrik-kesintisi-sonrasi-otomatik-yeniden-baslatma`
- **Birincil anahtar ifade:** `kesinti sonrası otomatik yeniden başlatma`
- **Risk sınıfı:** `high`
- **Fırsat puanı:** **92/100**
- **AI CMS kalite hedefi:** **100/100**
- **Durum:** `review` — canonical HTML veya routing overlay henüz yok

## Kullanıcı görevi

Elektrik kesintisi sonrasında makine ve proseslerin beklenmedik hareketini önlemek için güç, kontrol, interlock ve depolanmış enerji zincirini ölçümlü kabul dosyasına dönüştürmek.

## Doğrudan cevap

Elektriğin geri gelmesi makine için tek başına start komutu olmamalıdır. PLC’de kalıcı talep, sürücü auto-restart ayarı, iki telli kumanda, uzaktan otomasyon, farklı kontrol beslemeleri veya depolanmış mekanik enerji beklenmedik hareket oluşturabilir. Güvenli sonuç; risk değerlendirmesi, interlock matrisi, manuel reset/start ayrımı ve şebeke-jeneratör-UPS senaryolarında ölçümlü yeniden başlatma testiyle kanıtlanır.

## Mevcut içerikten görev ayrımı

Kesinti hazırlığı ve jeneratör transferinden farklı olarak makine kontrol devresi, kalıcı PLC talebi, interlock ve depolanmış enerji nedeniyle beklenmedik yeniden çalışmayı hedefler.

Tahmini en yüksek başlık/H1 benzerliği: **0.280** — en yakın rota: `/hesaplama/elektrik-kesintisi-tatbikati/`. Fail-closed AI CMS doğrulaması gerçek envanter üzerinde yeniden hesaplar; `0,78` veya üzeri benzerlikte onay durmalıdır.

## Bölümler ve kaynak bağı

- **Elektriğin geri gelmesi neden otomatik çalışma komutu değildir?** — S1, S2
- **Kontrol devresi, kontaktör ve PLC hafızası nasıl incelenir?** — S1, S2, S3
- **Koruyucu kapı ve interlocklar yeniden başlatmada hangi görevi yapar?** — S1, S3
- **Tesis genelinde kademeli yeniden başlatma planı nasıl kurulur?** — S1, S2
- **Yeniden başlatma kabul dosyasında neler bulunmalıdır?** — S1, S2, S3

## Kaynak doğrulaması

| Ref | Yayıncı | Kaynak | Erişim | Birincil |
|---|---|---|---|---|
| S1 | ISO | ISO 14118:2017 — Safety of machinery, prevention of unexpected start-up | 2026-08-03 | Evet |
| S2 | IEC | IEC 60204-1:2016+A1:2021 — Electrical equipment of machines | 2026-08-03 | Evet |
| S3 | ISO | ISO 14119:2024 — Interlocking devices associated with guards | 2026-08-03 | Evet |

Bütün teknik iddialar yalnız içerik kaydındaki `factSummary` ve ilgili `S#` kaynak referanslarına dayanmalıdır. Evrensel ürün eşiği, garanti, fiyat, stok veya resmî onay iddiası eklenmemelidir.

## İç bağlantılar

- `/hesaplama/elektrik-kesintisi-tatbikati/` — Yeniden başlatma senaryolarını kişisel verisiz tatbikat planına dönüştürür.
- `/hesaplama/ekipman-bakim-plani/` — Interlock, kontaktör ve kontrol sistemlerinin dönemsel test görevlerini planlar.
- `/hesaplama/kesinti-hazirlik-plani/` — Şebeke kaybı öncesi operasyon ve sorumluluk hazırlığını tamamlar.
- `/isletme-surekliligi` — Kritik yük ve proses sıralamasını işletme ölçeğinde ele alır.
- `/haberler/jenerator-transfer-salteri-neden-gerekir` — Kaynak transferinin geri besleme ve ayırma temelini açıklar.
- `/haberler/ups-bypass-modu-nedir-neden-gecer` — UPS normal, batarya ve bypass modlarında kontrol beslemesi ayrımını destekler.
- `/kurumsal-elektrik-surekliligi-on-degerlendirme` — Makine restart matrisi ve saha kabul kapsamını profesyonel değerlendirmeye bağlar.

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
/cms approve elektrik-kesintisi-sonrasi-otomatik-yeniden-baslatma
```

AI veya otomasyon bu komutu veremez. Onay sonrasında canonical HTML, routing overlay ve ChatGPT Sites önizleme artifactı oluşur; zorunlu kontroller geçmeden merge edilmemelidir.
