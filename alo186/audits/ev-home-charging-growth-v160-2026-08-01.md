# ALO186 EV evde şarj büyüme denetimi — v160

Tarih: 1 Ağustos 2026

## Seçilen 3 yüksek potansiyelli aksiyon

1. Elektrikli araç evde şarj priz ve uzatma kablosu güvenlik aracı
2. Mode 2 taşınabilir şarj cihazı, IC-CPD ve Type 2 kablo uygunluk aracı
3. Elektrikli araç evde şarj güvenlik ve tekrar test merkezi

## Arama niyeti

- elektrikli araç normal prizden şarj edilir mi
- elektrikli araç uzatma kablosuyla şarj edilir mi
- elektrikli araç prizi neden ısınıyor
- taşınabilir elektrikli araç şarj cihazı nasıl seçilir
- Mode 2 şarj cihazı nedir
- IC-CPD nedir
- Type 2 kablo 16 A 32 A tek faz üç faz farkı
- 32 A Type 2 kablo her araçta hızlı şarj eder mi
- elektrikli araç şarj kablosu ne zaman değiştirilir

## İçerik boşluğu

ALO186'te apartman/site şarj altyapısı, open PEN, EV şarj ısınması ve proje içerikleri bulunuyordu. Buna karşın ev kullanıcısının üç ayrı görevini tek güvenli yolculukta çözen canonical araçlar yoktu:

- priz, uzatma, ayrı devre, topraklama ve ısınma için satın alma öncesi fail-closed güvenlik kararı,
- Mode 2 IC-CPD ile Mode 3 Type 2 kablonun görev ayrımı,
- yeni araç, yeni ekipman, hata veya tesisat değişikliği sonrası kişisel verisiz tekrar test planı.

## Kullanıcı yolculuğu

1. Duman, kıvılcım, su, erime ve elektrik çarpması riski ayrılır.
2. Ortak alan, kaldırım geçişi ve sabit wallbox profesyonel proje yoluna çıkarılır.
3. Ev tipi uzatma, çoklayıcı ve adaptör zinciri ticari çözüm olarak gösterilmez.
4. Ayrı devre, topraklama ve kaçak akım koruması ölçüm kanıtı aranır.
5. Mode 2 taşınabilir EVSE ile Mode 3 Type 2 kablo ayrılır.
6. Araç girişi, kaynak arayüzü, faz, akım, standardın güncel sürümü ve üretici onayı doğrulanır.
7. Mevcut ürün aynı zincirde güvenli çalışıyorsa yeni ürün almayın sonucu verilir.
8. Yalnız gerçek ürün sınıfı açığında üç ayrı onayla şeffaf affiliate geçişi açılır.
9. Kullanıcı 7, 30 ve 90 günlük tekrar kontrol kaydı oluşturabilir.

## Affiliate ürün kategorileri

- IEC 62752:2024 kapsamı, fiş sıcaklık gözetimi, araç ve priz uyumu üretici belgesiyle yeniden doğrulanacak Mode 2 taşınabilir şarj cihazı / IC-CPD sınıfı
- IEC 62196-2:2025 arayüzü, araç-istasyon Type 2 uyumu, faz, akım ve uzunluğu yeniden doğrulanacak Type 2 AC şarj kablosu sınıfı

Sabit wallbox, pano ürünü, uzatma kablosu, adaptör, koruma cihazı ve ortak otopark ekipmanı tüketici affiliate akışına alınmadı.

## Dönüşüm noktaları

- Affiliate yalnız tek konut, aktif tehlike bulunmaması, mevcut uygun ürünün olmaması ve teknik zincirin tamamlanması halinde görünür.
- Bağlantıdan önce Amazon satış ortaklığı açıklaması bulunur.
- `needConfirm`, `specConfirm` ve `adConfirm` tamamlanmadan mağaza URL'si açılmaz.
- Bağlantı `rel="sponsored nofollow noopener"` taşır.
- Fiyat, stok, puan, satıcı, teslimat ve garanti yayımlanmaz.
- Product, Offer, availability ve aggregateRating kullanılmaz.

## Tekrar ziyaret nedenleri

- yeni araç, yeni wallbox, yeni taşınabilir şarj cihazı veya Type 2 kablo
- priz, pano, sayaç, kolon hattı veya topraklama değişikliği
- şarj sırasında ısınma, hata, gerilim düşümü veya akım kısılması
- kablo, fiş, soket ve IC-CPD fiziksel hasarı
- yaz-kış sıcaklık ve dış ortam değişimi
- ortak otoparka veya farklı park yerine geçiş
- üretici servis bülteni, yazılım güncellemesi veya geri çağırma duyurusu

## Beklenen kullanıcı faydası

- Uzatma kablosu satın alarak tesisat sorununu gizleme riski azalır.
- Mode 2 şarj cihazı ile Type 2 kablo karıştırılmaz.
- Daha yüksek amperin otomatik olarak daha hızlı şarj anlamına gelmediği açıklanır.
- Mevcut güvenli ekipman yeterliyse Mevcut sistem yeterli — yeni ürün almayın sonucu öncelik kazanır.
- Adres, plaka, konum, araç kimliği ve kalıcı tarayıcı depolaması kullanılmaz.

## Beklenen gelir etkisi

- Type 2 kablo ve taşınabilir EVSE, açık satın alma niyeti ve görece yüksek sepet nedeniyle yüksek nitelikli gelir potansiyeline sahiptir.
- Fail-closed kapılar ham tıklamayı düşürebilir; yanlış ürün, iade, güven kaybı ve güvenlik şikâyeti riskini azaltır.
- Tekrar test merkezi doğrudan gelir üretmez; organik giriş, araçlar arası geçiş, geri dönüş ve ileride oluşan doğrulanmış ihtiyacı güçlendirir.

## Doğrulanan birincil kaynaklar

- IEC 61851-1:2017 — EV besleme ekipmanının genel çalışma ve elektriksel güvenlik çerçevesi.
- IEC 62752:2024 — Mode 2 IC-CPD; ikinci baskıda ev tipi fişin akım taşıyan bölümleri için sıcaklık kontrolü gereği.
- IEC 62196-2:2025 — Type 2 dahil AC pin ve kontak tüpü arayüzlerinin boyutsal uyumluluğu.
- U.S. DOE Alternative Fuels Data Center — ev tipi yavaş şarjda park alanına yakın ayrı branşman devresi yaklaşımı.
- Electrical Safety First — EV yavaş şarjının sürekli yüksek yük olması, ayrı devre ve uzatma kullanmama yaklaşımı.

## Güven sınırı

ALO186; EDAŞ, EPDK, IEC, araç üreticisi, şarj ağı, test laboratuvarı, servis veya satıcı değildir. Araç ya da tesisat uygunluğu, proje, kabul, garanti veya performans taahhüdü verilmez. Standart sürümü ve model belgeleri işlem öncesinde yeniden doğrulanır.
