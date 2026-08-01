# ALO186 kombi elektrik sürekliliği büyüme denetimi — v158

Tarih: 2026-08-01

## Seçilen üç yüksek potansiyelli aksiyon

1. `/hesaplama/kombi-elektrik-kesintisi-sonrasi-guvenli-yeniden-baslatma/`
2. `/hesaplama/kombi-ups-w-va-wh-saf-sinus-uygunluk/`
3. `/sektor-rehberi/kombi-elektrik-surekliligi-donma-koruma-merkezi/`

## Arama niyeti

Bu çalıştırmada aşağıdaki yüksek niyetli ve birbirini tamamlayan sorgular hedeflendi:

- elektrik kesintisinden sonra kombi nasıl açılır
- elektrik gelince kombi hata verdi
- kombi kaç kez resetlenir
- elektrik kesintisinde kombi donar mı
- kombi için UPS kaç watt olmalı
- kombi UPS saf sinüs gerekli mi
- 1000 VA UPS kombiyi kaç saat çalıştırır
- kombi UPS W VA Wh hesabı
- kombi donma koruması elektrik kesilince çalışır mı

Bu sorguların ortak kullanıcı görevi, kesinti sonrasında cihazı güvenle devreye almak ve yalnız gerçek ihtiyaç varsa yedek enerji kapasitesini teknik kanıtla seçmektir.

## İçerik boşluğu

Mevcut ALO186 envanterinde genel UPS, güç istasyonu, priz güvenliği ve elektrik kesintisi içerikleri vardı. Buna karşın doğal gazlı kombi için:

- gaz kokusu ile elektrik işlemini aynı fail-closed kapıda ayıran,
- kararsız şebeke, su kaçağı, basınç, hata kodu, reset sayısı ve donma belirtisini tek sırada değerlendiren,
- kombi üreticisi/yetkili servis haricî AC yedek besleme onayını zorunlu tutan,
- W, VA, Wh, tepe güç, saf sinüs, transfer, topraklama ve bağlantı tipini birlikte hesaplayan,
- mevcut sistem gerçek testi geçmişse satın almama sonucu veren,
- 7/30/90 günlük kişisel verisiz tekrar kontrol planı üreten

canonical kullanıcı yolculuğu bulunmuyordu.

## Kullanıcı yolculuğu

1. Gaz kokusu, su kaçağı, yanık izi, donma ve devam eden kesinti kontrol edilir.
2. Aktif gaz olayında elektrik düğmesine dokunmadan ortamdan uzaklaşma ve 187/112 yolu açılır; ticaret kapanır.
3. Elektrik geri geldiyse besleme kararlılığı, model basıncı, ekran/hata kodu ve reset sayısı değerlendirilir.
4. Güvenli koşullar sağlanırsa yalnız model kılavuzunun izin verdiği kontrollü yeniden başlatma uygulanır.
5. Kesinti öncesi hazırlıkta kombi üreticisi/yetkili servis haricî AC yedek besleme koşullarını doğrular.
6. Fişli bağlantı, topraklama ve koruma kanıtı yoksa tüketici UPS yolu kapanır.
7. Sürekli W, tepe W, VA ve Wh gereksinimleri hesaplanır.
8. Mevcut UPS aynı kombiyle geçiş ve süre testini geçmişse “Mevcut UPS yeterli — yeni ürün almayın” sonucu verilir.
9. Yalnız doğrulanmış kapasite açığında üç ayrı onaydan sonra açık Amazon satış ortaklığı bağlantısı etkinleşir.
10. Kullanıcı JSON ve ICS görevleriyle 7, 30 ve 90 günlük yeniden kontrol döngüsüne girer.

## Affiliate ürün kategorileri

Yalnız tek kombili ev kullanımı, kesinti öncesi hazırlık, fişli bağlantı, doğrulanmış topraklama, model onayı ve teknik kapasite açığında şu kategori açılabilir:

- kombi üreticisinin şartlarıyla uyumlu olduğu ayrıca doğrulanacak saf sinüs AC UPS sınıfı

Aşağıdaki kategoriler ve senaryolar affiliate dışıdır:

- kombi, termostat, pompa veya elektronik kart değişimi
- priz tipi gerilim koruyucu ile bütün arızaları çözme iddiası
- sabit tesisata veya bina prizine geri besleme
- otel, site, işyeri, ortak kazan ve kritik tesis
- gaz kokusu, su kaçağı, ıslaklık, yanık izi veya batarya hasarı
- model onayı, topraklama, dalga biçimi veya bağlantı tipi belirsizliği

Fiyat, stok, puan, satıcı, teslimat ve garanti bilgisi yayımlanmaz. Product, Offer, availability veya aggregateRating şeması kullanılmaz.

## Dönüşüm noktaları

- Güvenlik aracı, olay anındaki kullanıcıyı alışverişten resmî acil ve servis yoluna taşır.
- UPS aracı, ürün sayfasına geçmeden önce model onayı ve altı teknik kanıtı zorunlu tutar.
- Hesap sonucu mevcut ekipmanın yeterli olduğunu gösteriyorsa dönüşüm bilinçli olarak satın almama sonucuna çevrilir.
- Gerçek kapasite açığında kullanıcı; ihtiyaç, teknik doğrulama ve reklam ilişkisini ayrı ayrı onaylar.
- Merkez sayfasında doğrudan affiliate bağlantısı yoktur; araçlar arası güvenli geçiş vardır.

## Tekrar ziyaret nedenleri

- gerçek elektrik veya doğal gaz kesintisi
- yeni hata kodu veya reset ihtiyacı
- yeni kombi, termostat, pompa veya UPS
- batarya süresinin azalması, aşırı ısınma veya şişme
- açık balkon, kombi dolabı, boru yalıtımı veya yoğuşma gideri değişikliği
- soğuk hava ve uzun süre evden uzak kalma
- yetkili servis bakımı veya elektrik tesisatı değişikliği
- üretici kılavuzu, teknik şart veya geri çağırma değişikliği

Merkez kişisel veri istemeden JSON görev dosyası ve 7/30/90 günlük ICS kayıtları üretir. localStorage ve sessionStorage kullanılmaz.

## Beklenen kullanıcı faydası

- Gaz kokusunda elektrik anahtarı kullanma gibi yüksek sonuçlu hata önlenir.
- Kesinti sonrası art arda reset ve donmuş sistemi çalıştırma davranışı azaltılır.
- VA değeri çalışma süresi sanılmaz; W, VA, Wh ve tepe güç ayrı sınırlar olarak anlaşılır.
- Saf sinüs ifadesinin tek başına kombi uyumluluğu kanıtı olmadığı görünür olur.
- Çalışan mevcut UPS gereksiz yere değiştirilmez.
- Profesyonel ve sabit tesisler tüketici ürünü akışından ayrılır.

## Beklenen gelir etkisi

- Güvenlik aracı: doğrudan gelir düşük, yüksek arama erişimi ve ikinci araca nitelikli geçiş yüksek.
- UPS uygunluk aracı: orta-yüksek sepet ve açık satın alma niyeti nedeniyle nitelikli gelir potansiyeli yüksek; fail-closed kapılar ham tıklamayı azaltabilir ancak yanlış ürün ve iade riskini düşürür.
- Süreklilik merkezi: doğrudan gelir düşük, tekrar ziyaret, iç bağlantı ve gelecekte oluşan doğrulanmış ihtiyaç etkisi yüksek.

## Güven ve resmî kurum ayrımı

- ALO186; EPDK, EDAŞ, doğal gaz dağıtım şirketi, 186, 187, 112, kombi/UPS üreticisi, yetkili servis, test laboratuvarı veya satıcı değildir.
- Aktif olayda affiliate açılmaz.
- Kullanıcıya güvenlik, uygunluk, çalışma süresi, tasarruf veya garanti vaadi verilmez.
- Kişisel veri, adres, abonelik, seri numarası ve kalıcı tarayıcı depolaması kullanılmaz.
- Affiliate açıklaması bağlantıdan önce görünür; bağlantı `rel="sponsored nofollow noopener"` taşır.

## Doğrulanan birincil kaynaklar

- EPDK doğal gaz piyasası tüketici bilgisi: acil durum ihbarları için 187.
- Aksa Doğalgaz acil durum rehberi: gaz kokusunda elektrik düğmelerine dokunmama ve güvenli yerden 187’yi arama.
- Bosch Home Comfort Türkiye: kombinin elektrikle çalışan parçaları, doğrudan topraklı priz, hata/servis sınırı ve kontrollü yeniden başlatma yaklaşımı.
- Bosch Home Comfort Türkiye: donma korumasının devrede kalması için elektrik ve doğal gaz koşulu.
- IEC 62040-3:2021: UPS performansının belirtilmesi ve test çerçevesi.
- IEC 62040-1 konsolide sürüm: UPS güvenlik gerekleri.

## Yayın ve kalite kapsamı

- routing overlay v158
- üç benzersiz canonical rota
- WebApplication/WebPage, FAQPage ve BreadcrumbList
- mobil tek sütun davranışı
- JavaScript sözdizimi kontrolü
- aktif olay, profesyonel kapsam, sabit bağlantı, geri besleme, topraklama ve model onayı için fail-closed kapılar
- üçlü affiliate onayı ve satın almama sonucu
- JSON/ICS tekrar kontrol merkezi
- fiyat, stok, puan, garanti ve kişisel veri yasağı

Canlı alan adı önbelleğine yansıma ve arama motoru indekslenmesi kod birleştirmesinden ayrı süreçlerdir; bu denetimde bağımsız olarak doğrulanmamıştır.
