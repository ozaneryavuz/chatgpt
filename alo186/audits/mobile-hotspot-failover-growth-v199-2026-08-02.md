# ALO186 mobil hotspot ve yedek internet büyüme denetimi v199

Tarih: 2 Ağustos 2026

## Arama niyeti ve içerik boşluğu

Ana dal envanteri; modem–ONT elektrik yedeği, evden çalışma güç seti ve internet arızası ayrımını kapsıyor. Buna karşılık “internet kesilince telefon hotspotu”, “4G/5G mobil router”, “video toplantısı kaç GB yer”, “hotspot kaç saat çalışır”, “çift WAN failover” ve “mobil bağlantıyı yedek internet olarak test etme” niyetlerini tek zincirde karşılayan canonical rota bulunmadı.

Aynı ihtiyeti karşılayan ikinci evden çalışma sayfası oluşturulması içerik çoğalması yaratacağından PR #647 birleştirilmeden kapatıldı. Büyüme odağı doğrulanmış boşluğa taşındı.

## Seçilen üç aksiyon

1. **Mobil hotspot veri ve batarya süre hesabı**
   - indirme + yükleme Mbps, çalışma süresi, toplantı dışı veri ve rezerv ile GB tahmini;
   - cihaz W, harici batarya Wh, verim ve rezerv ile çalışma süresi;
   - uygulama gereksinimi/gerçek ölçüm ve gerçek konum testi zorunlu;
   - veri ve enerji hedefi mevcut sistemle karşılanıyorsa “yeni ürün almayın”.

2. **Üçlü güven kapılı mobil internet ürün seçici**
   - taşınabilir 4G/5G mobil hotspot/router sınıfı;
   - çift WAN/failover router sınıfı;
   - USB-C powerbank sınıfı;
   - en fazla üç sınıf; statik Amazon bağlantısı yok;
   - operatör politikası, SIM/bant/model uyumluluğu ve affiliate ilişkisi ayrı ayrı doğrulanır.

3. **30/90 günlük mobil internet failover test merkezi**
   - gerçek konum kapsaması, operatör koşulu, parola, tarifeli bağlantı, veri, batarya, sıcaklık, failover ve alternatif iletişim;
   - kişisel verisiz JSON;
   - 30 günlük kısa kontrol ve 90 günlük tam failover ICS çıktısı;
   - tüm görevler geçerse satın almama sonucu.

## Kullanıcı yolculuğu

Sabit internet kesintisi veya hazırlık niyeti → mevcut telefon hotspotunun gerçek konum testi → ücretsiz GB/Wh hesabı → veri kotası ve enerji yeterlilik sonucu → yalnız gerçek cihaz/enerji/failover açığında ürün sınıfı → üç ayrı affiliate onayı → Amazon seçenekleri → 30/90 günlük tekrar test.

Riskli batarya, yaşam güvenliği kullanımı ve test edilmemiş kapsamada ticari yol fail-closed kapanır. Tarife veya SIM hizmeti satılmaz.

## Affiliate ürün kategorileri

- Taşınabilir 4G/5G mobil hotspot/router: telefon hotspotu gerçek provada yetersizse ve tam operatör/model uyumu doğrulanabiliyorsa.
- Çift WAN/failover router: sabit ve ikinci bağlantı arasında kontrollü geçiş gereken ev/küçük ofis senaryosunda.
- USB-C powerbank: mevcut telefon/hotspot görev olarak yeterli, yalnız enerji açığı belgelenmişse.

Fiyat, stok, satıcı, puan, yorum, teslimat veya garanti yayımlanmaz. 5G etiketi uyumluluk veya hız garantisi olarak kullanılmaz.

## Dönüşüm noktaları

- `mobile_failover_calculated`: veri ve enerji yeterlilik sonucu;
- `mobile_failover_no_buy`: mevcut sistem hedefi karşılıyor;
- `affiliate_gate_viewed`: gerçek ihtiyaca göre sınıflar açıldı;
- `affiliate_gate_passed`: satın almama, teknik uygunluk ve affiliate ilişkisi doğrulandı;
- `affiliate_product_clicked`: güven kapısı sonrası nitelikli mağaza geçişi;
- `mobile_failover_test_passed` / `mobile_failover_test_incomplete`: tekrar ziyaret ve gerçek eksik ayrımı.

Olaylarda adres, konum, SIM, telefon, hesap, parola veya ürün fiyatı bulunmaz.

## Tekrar ziyaret nedenleri

Operatör veya tarife değişikliği; yeni telefon/router; işletim sistemi, VPN veya firmware güncellemesi; taşınma/seyahat; batarya kapasite kaybı; gerçek internet kesintisi; mevsimsel şebeke yoğunluğu; 30/90 günlük hatırlatmalar.

## Beklenen kullanıcı faydası

- Telefon hotspotu yeterliyken ayrı mobil router alınması önlenir.
- Mobil veri tüketimi yalnız “saat” ile değil iki yönlü bit hızı ve rezervle planlanır.
- Kapsama haritası yerine gerçek konum ve benzer saat provası öne alınır.
- Operatör politikası, SIM ve ağ bantları cihaz satın almadan önce kontrol edilir.
- Tarifeli bağlantı ve arka plan eşitlemesi veri sürprizini azaltır.
- Riskli batarya ve yaşam güvenliği kullanımında mağaza yolu kapanır.

## Beklenen gelir etkisi

Mobil hotspot/router ve çift WAN router açık satın alma niyetine; powerbank ise daha geniş fakat daha düşük nitelikli niyete sahiptir. Seçici yalnız gerçek açığı göstererek rastgele tıklamayı azaltır. Beklenen sonuç daha düşük fakat daha nitelikli mağaza trafiği, internet kesintisi dönemlerinde bağlamsal dönüşüm ve 30/90 günlük testlerden doğan güvene dayalı yenileme talebidir.

Doğrulanmış arama hacmi, dönüşüm oranı veya gelir verisi bulunmadığından sayısal artış iddiası yapılmaz.

## Korunan ticari sözleşme

- Affiliate ilişkisi mağaza bağlantısından önce görünür.
- Bağlantılar üç onaydan sonra `alo186rehber-21` ve `rel="sponsored nofollow noopener"` ile açılır.
- Mevcut sistem hedefi karşılıyorsa satın almama sonucu görünürdür.
- Product, Offer ve AggregateRating şeması kullanılmaz.
- ALO186 resmî kurum, operatör, internet sağlayıcısı, üretici veya satıcı gibi sunulmaz.
- Kişisel veri ve kalıcı tarayıcı depolaması kullanılmaz.
- Yaşam güvenliği kullanımında tüketici affiliate yolu kapalıdır.
