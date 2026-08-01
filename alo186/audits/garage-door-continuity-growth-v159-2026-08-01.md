# ALO186 garaj kapısı elektrik sürekliliği büyüme denetimi — v159

Tarih: 2026-08-01

## Seçilen 3 yüksek potansiyelli aksiyon

1. `/hesaplama/garaj-kapisi-elektrik-kesintisi-manuel-acma-guvenligi/`
2. `/hesaplama/garaj-kapisi-motoru-ups-batarya-w-wh-uygunluk/`
3. `/sektor-rehberi/garaj-kapisi-elektrik-kesintisi-guvenlik-test-merkezi/`

## Arama niyeti

- elektrik kesintisinde garaj kapısı nasıl açılır
- garaj kapısı acil ayırma ipi nasıl kullanılır
- otomatik garaj kapısı elle açılır mı
- garaj kapısı çok ağır neden
- garaj kapısı için UPS kaç watt olmalı
- garaj kapısı yedek aküsü nasıl seçilir
- elektrik kesintisinde otomatik kapı çalışır mı
- garaj kapısı otomatik geri dönüş testi

## İçerik boşluğu

Mevcut ALO186 kesinti, UPS, güç istasyonu ve acil hazırlık içerikleri genel elektrik sürekliliğini kapsıyordu. Ancak konut tipi dikey garaj kapısında:

- kapının tamamen kapalı olması,
- yay, halat ve ray durumu,
- acil ayırma mekanizmasının kapıyı kaldırmadığı,
- sıkışma önleme ve otomatik geri dönüş testi,
- üretici onaylı entegre batarya ile haricî UPS ayrımı,
- sürekli W, kalkış W, bekleme tüketimi ve Wh hesabı,
- gerçek kesinti çevrimi

aynı fail-closed kullanıcı yolculuğunda bulunmuyordu.

## Kullanıcı yolculuğu

1. Kullanıcı aktif kesinti veya hazırlık niyetiyle gelir.
2. Önce elektriksel tehlike, kapı düşmesi, yay/halat/yarı açık kapı ve ortak kullanım kapsamı ayrılır.
3. Aktif olayda affiliate tamamen kapanır; güvenli manuel açma veya servis yolu gösterilir.
4. Hazırlık aşamasında tam model üretici onayı ve manuel ayırma yöntemi doğrulanır.
5. Sürekli W, tepe W, çevrim Wh ve bekleme Wh hesaplanır.
6. Mevcut sistem gerçek testte yeterliyse `Mevcut sistem yeterli — yeni ürün almayın` sonucu verilir.
7. Yalnız doğrulanmış teknik açıkta, üç ayrı onaydan sonra açık Amazon satış ortaklığı bağlantısı etkinleşir.
8. Kullanıcı 7/30/90 günlük güvenlik ve yedekleme test merkezine yönlendirilir.

## Affiliate ürün kategorileri

Yalnız aşağıdaki koşullu kategoriler açılır:

- Tam model için üretici tarafından onaylanmış garaj kapısı yedek bataryası.
- Üretici haricî AC beslemeyi açıkça onaylıyorsa; sürekli W, tepe W, dalga biçimi, transfer ve Wh değerleri doğrulanacak UPS kategorisi.

Genel amaçlı akü, rastgele motor, uzaktan kumanda, fotosel, yay, halat veya kapı mekanizması affiliate akışına alınmaz. Mekanik güvenlik parçaları profesyonel servis alanıdır.

## Dönüşüm noktaları

- Manuel açma aracından kapasite aracına geçiş.
- Kapasite aracında üretici onayı ve gerçek teknik açık sonrası üçlü affiliate onayı.
- Sonuçtan 7/30/90 günlük test merkezine geçiş.
- Test merkezinden gerçek olay veya batarya zayıflaması sonrası kapasite aracına dönüş.

Affiliate bağlantıları görünür `Amazon satış ortaklığı bağlantısı` açıklaması taşır ve `rel="sponsored nofollow noopener"` kullanır. Fiyat, stok, puan, satıcı, teslimat veya garanti yayımlanmaz.

## Tekrar ziyaret nedenleri

- Gerçek elektrik kesintisi veya manuel açma kullanımı.
- Yeni motor, kapı, fotosel, kumanda veya yedek batarya.
- Batarya uyarısı veya azalan çevrim sayısı.
- Kapının ağırlaşması, açık kalmaması veya hızla düşmesi.
- Yay, halat, ray, denge veya servis işlemi.
- Yeni kullanıcı, çocuk, evcil hayvan veya garaja tek giriş düzeni.
- Üretici kılavuzu, servis bülteni veya geri çağırma değişikliği.

## Beklenen kullanıcı faydası

- Acil ayırma kolunun kapıyı kaldırmadığı anlaşılır.
- Kısmen açık veya mekanik hasarlı kapıda kontrolsüz düşme riski azaltılır.
- Kullanıcı VA değerini çalışma süresi sanmaz.
- Mekanik arıza daha büyük UPS veya yeni batarya ile maskelenmez.
- Çalışan mevcut sistem gereksiz yere değiştirilmez.
- Aylık sıkışma önleme ve dönemsel kesinti testi tekrar ziyaret nedeni olur.

## Beklenen gelir etkisi

- Manuel açma sayfası: doğrudan düşük gelir, yüksek güven ve organik giriş potansiyeli.
- Yedek batarya/UPS aracı: düşük-orta hacim, yüksek satın alma niyeti ve orta-yüksek nitelikli dönüşüm potansiyeli.
- Test merkezi: doğrudan düşük gelir, tekrar ziyaret ve ileride doğrulanmış batarya ihtiyacı üzerinde yüksek etki.

Ham tıklama sayısının teknik ve güvenlik kapıları nedeniyle düşük kalması beklenir; buna karşılık yanlış ürün, iade ve güven kaybı riski azalır.

## Güven sınırı

- Aktif kesinti, elektriksel hasar, yarı açık kapı, bozuk yay/halat/ray, sıkışma önleme arızası ve ortak kullanımda affiliate kapalıdır.
- Üretici onayı veya manuel ayırma yöntemi bilinmiyorsa mağaza geçişi açılmaz.
- `Product`, `Offer`, `availability` ve `aggregateRating` şemaları kullanılmaz.
- Kişisel veri, adres, konum, telefon, kapı seri numarası ve kalıcı tarayıcı depolaması kullanılmaz.
- ALO186; üretici, servis, CPSC, IEC, EDAŞ veya resmî kurum gibi gösterilmez.

## Doğrulanan birincil kaynaklar

- IEC 60335-2-95:2023 — konut tipi dikey hareketli garaj kapısı sürücülerinin güvenliği: https://webstore.iec.ch/en/publication/75496
- CPSC — otomatik geri dönüş ve aylık test yaklaşımı: https://www.cpsc.gov/Newsroom/News-Releases/1993/Safety-Commission-Publishes-Final-Rules-For-Automatic-Garage-Door-Openers
- Chamberlain Group — manuel açma/kapama ve düşme riski uyarıları: https://support.chamberlaingroup.com/s/article/How-to-Manually-Open-or-Close-a-Garage-Door
- LiftMaster — entegre yedek batarya yaklaşımı: https://www.liftmaster.com/builder-knowledge-center/offer-battery-backup

## Yayın kapsamı

- Routing overlay v159
- İki WebApplication ve bir WebPage
- FAQPage ve BreadcrumbList
- Mobil tek sütun davranışı
- JavaScript sözdizimi kontrolü
- Üçlü affiliate onayı ve satın almama sonucu
- JSON görev planı ve 7/30/90 günlük ICS kayıtları
