# ALO186 AI CMS insan inceleme paketi

## İçerik

- **Başlık:** GES Zero Export: İhracat Sınırlama Kabul Testi
- **H1:** GES zero export nasıl çalışır, sayaç ve haberleşme arızasında nasıl test edilir?
- **Canonical adayı:** `/haberler/ges-zero-export-ihrac-sinirlama-kabul-testi`
- **Birincil anahtar ifade:** `GES zero export kabul testi`
- **Risk sınıfı:** `high`
- **Fırsat puanı:** **95/100**
- **AI CMS kalite hedefi:** **100/100**
- **Durum:** `review` — canonical HTML veya routing overlay henüz yok

## Kullanıcı görevi

Şebekeye aktif güç ihracının sınırlandırıldığı GES’te zero export fonksiyonunun bağlantı noktasında, faz bazında ve arıza senaryolarında gerçekten çalıştığını doğrulamak.

## Doğrudan cevap

Zero export, inverter gücünü sabit bir yüzdeye kısmak değil; bağlantı noktasındaki çift yönlü sayaç veya güç sensörü verisine göre üretimi kapalı çevrim düzenleyerek şebekeye verilen aktif gücü hedef sınırda tutmaktır. Kabul testi; sayaç yönü ve faz eşlemesi, toplam veya faz bazlı kontrol modu, yükün ani düşmesi, kontrol gecikmesi, haberleşme kopması, cihaz yeniden başlaması ve varsa batarya şarj-deşarjını kapsamalıdır. Üretici dokümanları kontrol çevrimi nedeniyle kısa süreli artık ihracın oluşabileceğini belirttiğinden, “0 kW” sonucu yalnız tek ekran görüntüsüyle değil zaman damgalı yüksek çözünürlüklü kayıtla doğrulanmalıdır.

## Mevcut içerikten görev ayrımı

Mevcut lisanssız GES mahsuplaşma, clipping, anti-islanding ve yüksek şebeke gerilimi içerikleri hukuki enerji akışı veya inverter işletme belirtilerini ele alır. Yeni içerik, bağlantı noktasında zero export kontrolünün sayaç, faz, yük basamağı ve haberleşme arızasıyla kabulünü ayrı göreve dönüştürür.

Tahmini en yüksek başlık/H1 benzerliği: **0.340** — en yakın rota: `/haberler/lisanssiz-ges-mahsuplasma-ihtiyac-fazlasi`. Fail-closed AI CMS doğrulaması gerçek envanter üzerinde yeniden hesaplar; `0,78` veya üzeri benzerlikte onay durmalıdır.

## Bölümler ve kaynak bağı

- **Zero export ile sabit güç sınırı arasındaki fark nedir?** — S1, S2, S3
- **Sayaç yönü ve faz eşlemesi nasıl doğrulanmalıdır?** — S3, S4
- **Ani yük değişiminde kontrol performansı nasıl test edilir?** — S2, S3, S4
- **Sayaç veya haberleşme arızasında sistem ne yapmalıdır?** — S3, S4
- **Teknik kabul ile lisanssız üretim süreci nasıl ayrılır?** — S1, S2, S3, S4

## Kaynak doğrulaması

| Ref | Yayıncı | Kaynak | Erişim | Birincil |
|---|---|---|---|---|
| S1 | EPDK | Elektrik piyasasında lisanssız elektrik üretimi | 2026-08-03 | Evet |
| S2 | SMA Solar Technology | Configuring Limitation of Active Power Feed-In | 2026-08-03 | Evet |
| S3 | SMA Solar Technology | Active power limitation with the SMA Data Manager M | 2026-08-03 | Evet |
| S4 | Huawei | Setting Limited Feed-in Parameters | 2026-08-03 | Evet |

Bütün teknik ve hukukî iddialar yalnız içerik kaydındaki `factSummary` ve ilgili `S#` kaynak referanslarına dayanmalıdır. Güncel mevzuat, üretici sürümü ve dağıtım şirketi şartları yayın öncesi tekrar doğrulanmalıdır.

## İç bağlantılar

- `/haberler/lisanssiz-ges-mahsuplasma-ihtiyac-fazlasi` — İhracat sınırlamasını ihtiyaç fazlası enerji ve mahsuplaşma sürecinden ayırır.
- `/haberler/ges-fazlasi-ile-elektrikli-arac-sarji` — İhracat yerine öz tüketimi artıran kontrollü yük kullanımını açıklar.
- `/haberler/ges-inverter-sebeke-gerilimi-yuksek-hatasi` — İhracat ve bağlantı noktası gerilimi arasındaki işletme bağını tamamlar.
- `/haberler/gunes-paneli-inverter-clipping-dc-ac-orani` — Üretim kısıtlamasını inverter clipping olgusundan ayırır.
- `/haberler/ges-elektrik-kesintisinde-calisir-mi` — Zero export ile anti-islanding ve yedekleme işlevlerini karıştırmayı önler.
- `/haberler/vpp-sanal-guc-santrali-nedir` — Harici aktif güç komutu ve enerji yönetimi bağlamını genişletir.
- `/kurumsal-elektrik-surekliligi-on-degerlendirme` — Çok inverterli tesislerde ölçüm ve kabul kapsamını profesyonel çalışmaya taşır.

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

Dönüşüm çağrısı; zero export kabul matrisi, faz bazlı trend, haberleşme arızası testi ve kurumsal teknik ön değerlendirmedir. ALO186 bağlantı izni vermez. Canlı sayaç, CT, inverter ve pano bağlantıları yalnız yetkin personel sınırındadır; affiliate kapalıdır.

## İnsan onayı

Teknik içerik, kaynak, görev ayrımı, iç bağlantılar ve güvenlik sınırı kabul edilirse PR konuşmasına tam olarak şu yorum eklenmelidir:

```text
/cms approve ges-zero-export-ihrac-sinirlama-kabul-testi
```

AI veya otomasyon bu komutu veremez. Onay sonrasında canonical HTML, routing overlay ve ChatGPT Sites önizleme artifactı oluşur; zorunlu kontroller geçmeden merge edilmemelidir.
