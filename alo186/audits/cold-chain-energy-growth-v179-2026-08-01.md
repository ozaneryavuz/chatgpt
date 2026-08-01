# ALO186 soğuk zincir ve cihaz enerjisi büyüme denetimi v179

Tarih: 1 Ağustos 2026

## Seçilen 3 aksiyon

1. Elektrik kesintisinde buzdolabı/dondurucu için süre, kapak, sıcaklık ve buz kristali girdilerini ayıran gıda sıcaklık karar aracı.
2. Fiş-prizle bağlı düşük riskli cihazlarda ölçülmüş W veya kWh değerinden günlük/aylık tüketim planı çıkaran ve yalnız gerçek ölçüm açığında affiliate yolu açan cihaz tüketim aracı.
3. Soğuk zincir sıcaklığı, kesinti süresi ve cihaz kWh kayıtlarını kişisel veri istemeden tarayıcıda tutan; JSON, CSV ve 7/30/90 günlük ICS çıktısı üreten tekrar ziyaret merkezi.

## Arama niyeti ve içerik boşluğu

Karşılanan niyetler: “elektrik kesilince buzdolabındaki yiyecekler bozulur mu”, “dondurucu kaç saat dayanır”, “buzdolabı termometresi gerekli mi”, “bir cihaz kaç kWh yakar”, “priz tipi enerji ölçer nasıl kullanılır”, “watt değeri aylık faturaya nasıl çevrilir”, “evde enerji tüketimi nasıl takip edilir”.

Mevcut kesinti hazırlık sepeti, min/max buzdolabı termometresi kartını var olmayan `/sektor-rehberi/elektrik-kesintisinde-buzdolabi-gida-guvenligi/` rotasına bağlıyordu. Yeni karar aracı bu kırık kullanıcı yolculuğunu tamamlar ve ürün kartını gerçek güvenlik kararına bağlar. Site enerji verimliliği ve ürün merkezleri içerse de kullanıcı tarafından girilen gerçek kWh ölçümünü 30 günlük karşılaştırmaya bağlayan bütünleşik ev akışı bulunmuyordu.

## Kullanıcı yolculuğu

Aktif kesinti veya yeni biten olayda gıda güvenliği aracı mağaza bağlantısı göstermez. Süre, sıcaklık ve ürün sınıfı belirsizse fail-closed sonuç üretir. Kesinti öncesi hazırlıkta mevcut termometre, yalıtımlı soğutucu ve jel paket kontrol edilir; mevcut ekipman yeterliyse satın almama mesajı korunur.

Cihaz enerjisi aracında sabit bağlı, yüksek güçlü, motorlu, profesyonel veya hasarlı yük mağaza akışından çıkarılır. Yalnız sağlam fiş-prizle bağlı cihazda, ölçer sınırları doğrulanmışsa hesap yapılır. Mevcut ölçer varsa yeni ürün önerilmez.

Takip merkezi, tek ölçümü karar saymak yerine 7/30/90 günlük yeniden kontrol döngüsü kurar. Kayıtlar yalnız tarayıcıda tutulur; ad, açık adres, abonelik numarası veya iletişim bilgisi istenmez.

## Affiliate ürün kategorileri

Düşük riskli ve bağlama uygun kategoriler:

- Min/max buzdolabı ve dondurucu termometresi
- Yalıtımlı soğutucu çanta/kutu
- Yeniden kullanılabilir buz jel paketi
- Priz tipi enerji ölçer/wattmetre
- Enerji ölçümlü akıllı priz

Kuru buz, sabit tesisat ölçüm cihazları, pano sayaçları, akım trafoları, profesyonel logger, yüksek güçlü ara adaptörler, jeneratör ve soğuk oda ekipmanları tüketici affiliate akışına alınmadı.

## Dönüşüm noktaları

- Mevcut kesinti hazırlık sepetindeki termometre niyetinden yeni sıcaklık karar aracına geçiş.
- Kesinti öncesinde gerçek hazırlık açığı doğrulanırsa üçlü affiliate onayı.
- Cihaz kWh aracında “mevcut ölçer yok + sınırlar doğrulandı + yük fiş-prizle bağlı” koşuluyla mağaza geçişi.
- 30 günlük kayıtta sıcaklık veya tüketim eğilimi oluşursa ücretsiz karar araçlarına geri dönüş.
- Otel, restoran, market, soğuk oda veya ticari bina için `/iletisim/` üzerinden ölçüm kapsamı ön değerlendirmesi.

## Tekrar ziyaret nedenleri

Gerçek elektrik kesintisi; buzdolabı/dondurucu sıcaklık değişimi; kapı contası veya termostat bakımı; yeni enerji ölçer; cihaz değişimi; kWh artışı; mevsim geçişi; gıda hazırlık testi; 7 günlük olay kapanışı; 30 günlük tüketim karşılaştırması; 90 günlük ekipman testi.

## Beklenen kullanıcı faydası

- Kullanıcı gıda güvenliğini koku veya tada göre değerlendirmez.
- Dondurucu ile buzdolabı için farklı süre ve sıcaklık eşikleri ayrılır.
- Etiket watt değeri, gerçek kWh tüketimi ve fatura toplamı birbirine karıştırılmaz.
- Sabit ve yüksek güçlü yüklerde tüketici ölçer kullanılmasının önüne geçilir.
- Mevcut termometre veya ölçer yeterliyse gereksiz satın alma engellenir.
- Tek ölçüm yerine eğilim kaydı oluşturulur.

## Beklenen gelir / lead etkisi

Soğuk zincir hazırlık ürünlerinde affiliate potansiyeli orta-yüksek; priz tipi enerji ölçer ve enerji ölçümlü akıllı prizlerde yüksek satın alma niyeti nedeniyle affiliate potansiyeli yüksektir. Takip merkezi ilk ziyarette satın alma baskısı oluşturmaz; gerçek ihtiyaç oluştuğunda geri dönüş ve güvene dayalı dönüşüm potansiyeli orta-yüksektir. Ticari soğuk zincir ve enerji ölçüm taleplerinde B2B lead potansiyeli yüksektir. Gerçek trafik, tıklama ve gelir artışı henüz ölçülmemiştir.

## Doğrulanan kaynaklar

- USDA FSIS, `How can I keep refrigerated and frozen food safe during a power outage?`, son güncelleme 18 Kasım 2024: buzdolabı yaklaşık 4 saat; dolu dondurucu yaklaşık 48 saat, yarı dolu dondurucu 24 saat; 4,4 °C ve altı hedef.
- FDA, `Power Outages: Key Tips for Consumers About Food Safety`, 1 Ağustos 2026 tarihinde erişildi: cihaz termometresi, kapakların kapalı tutulması ve enerji geri geldiğinde sıcaklık kontrolü.
- T.C. Enerji ve Tabii Kaynaklar Bakanlığı, `Enerji Verimliliği`, 1 Ağustos 2026 tarihinde erişildi: hizmet kalitesini azaltmadan birim başına enerji tüketiminin azaltılması yaklaşımı.
- U.S. Department of Energy, `Measuring Standby Power`, 1 Ağustos 2026 tarihinde erişildi: kararsız yükte enerjiyi zaman boyunca ölçerek ortalama güç değerlendirmesi ve ölçüm çözünürlüğü gereksinimi.

Kaynaklar belirli ürün için uygunluk, kalibrasyon veya resmî onay kanıtı olarak sunulmadı.

## Güven ve ticari sınırlar

- Affiliate açıklaması bağlantıdan önce görünür.
- Tüm mağaza bağlantıları `rel="sponsored nofollow noopener"` ve `alo186rehber-21` etiketi taşır.
- Fiyat, stok, puan, yorum, satıcı, teslimat ve garanti verisi yayımlanmaz.
- Product, Offer, availability ve aggregateRating şeması kullanılmaz.
- Aktif kesintide gıda aracı affiliate açmaz.
- Hasarlı priz, kablo veya cihazda affiliate açılmaz.
- Sabit, yüksek güçlü ve profesyonel yükler tüketici mağaza yoluna alınmaz.
- Mevcut güvenli ürün yeterliyse yeni ürün alınmaması istenir.
- ALO186’in EDAŞ, kamu kurumu, sağlık/gıda otoritesi, enerji tedarikçisi, Amazon, üretici veya satıcı olmadığı görünürdür.

## Teknik ve yayın kapsamı

- 3 benzersiz canonical rota
- WebApplication, FAQPage ve BreadcrumbList yapılandırılmış verileri
- Mobil tek sütun davranışı ve taşmayan tablo
- Karşılıklı iç bağlantılar
- Routing overlay v179 ve sitemap üretim girdisi
- Üçlü affiliate güven kapısı
- JSON, CSV ve ICS çıktıları
- Yerel kayıt temizleme kontrolü
- Fail-closed Python regresyon testi ve GitHub Actions kalite kapısı

## Tamamlanamayan bağımsız kontroller

GitHub Pages dağıtımının canlı alan adına tamamen yansıması, önbellek yenilenmesi, canlı sitemap çıktısı, Search Console keşfi, arama motoru indekslenmesi, gerçek kullanıcı davranışı ve affiliate dönüşüm verileri bu çalıştırmada bağımsız olarak doğrulanamadı.
