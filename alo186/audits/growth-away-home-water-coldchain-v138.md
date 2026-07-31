# ALO186 sürdürülebilir büyüme denetimi v138

Tarih: 31 Temmuz 2026

## Bu çalıştırmada seçilen üç aksiyon

1. Su kaçağı sensörü ve otomatik vana uygunluk testi
2. Buzdolabı/dondurucu sıcaklık alarmı uygunluk testi
3. Tatil ve yazlık ev elektrik, su ve soğuk zincir güvenlik merkezi

## Seçim gerekçesi

Son içerik paketleri kesinti, yedek güç, klima, priz, alarm ve araç enerjisi niyetlerini güçlü biçimde kapsıyor. Bu çalıştırmada çakışma yaratmadan yüksek ticari niyet ile güçlü tekrar ziyaret nedenini birleştiren iki boşluk öne çıktı:

- `su kaçağı sensörü nereye konur`, `akıllı su baskını alarmı`, `otomatik su kesme vanası`, `yazlık ev su kaçağı önleme`
- `buzdolabı termometresi`, `dondurucu sıcaklık alarmı`, `elektrik kesintisinde buzdolabı kaç saat`, `uzaktan sıcaklık takibi`
- `tatile giderken elektrik ve su ne yapılır`, `yazlık kapatma kontrol listesi`, `uzun süre boş kalan ev güvenliği`

Bu niyetler yalnız ürün araştırması değildir. Kullanıcı; evden uzaktayken hasarı erken fark etme, gıdayı güvenli tutma, mevcut cihazı test etme ve dönüşte sistemi güvenli biçimde yeniden devreye alma görevi taşır.

## Aksiyon 1 — Su kaçağı sensörü ve otomatik vana uygunluğu

Yeni rota:

`/hesaplama/su-kacagi-sensoru-otomatik-vana-uygunluk/`

Araç şu görevleri ayırır:

- noktasal nem/su alarmı;
- kablo tipi geniş alan algılama;
- yerel sesli alarm;
- uzaktan bildirim;
- ana hat akış izleme;
- tesisatçı tarafından doğrulanmış otomatik kapatma.

Aktif su-elektrik teması, ıslak zeminde elektrikli ekipman, ortak/ticari/kritik tesis, uyumsuz vana ve başarısız kapatma testi ticari sonuca dönüştürülmez. Mevcut sensör kapsam, pil, yerleşim, alarm ve gerçek su testini karşılıyorsa açık satın almama sonucu verilir.

### Affiliate kategorileri

- noktasal su kaçağı alarmı;
- kablo tipi sensör;
- yerel alarmı bulunan akıllı su sensörü;
- yalnız tesisat uyumu profesyonelce doğrulanmışsa akış izleme/otomatik kapatma sınıfı.

### Kullanıcı faydası

Kullanıcı bulut bildirimini tek güvenlik katmanı sanmaz; suyun ilk birikeceği nokta, pil, yerel alarm, internet bağımlılığı ve manuel vana kullanımını birlikte doğrular.

### Beklenen gelir etkisi

Yazlık, ikinci ev, çamaşır/bulaşık makinesi ve lavabo niyetlerinde orta-yüksek potansiyel. Daha pahalı otomatik vana çözümü herkese önerilmediği için yanlış kurulum ve iade riski azalır.

## Aksiyon 2 — Buzdolabı/dondurucu sıcaklık alarmı

Yeni rota:

`/hesaplama/buzdolabi-dondurucu-sicaklik-alarmi-uygunluk/`

Araç şu görevleri ayırır:

- yalnız yerinde sıcaklık doğrulama;
- yüksek sıcaklıkta yerel alarm;
- min/max hafıza ve olay kaydı;
- ev dışındayken uzaktan bildirim;
- profesyonel ticari veya medikal soğuk zincir.

Aktif kesintide ürün teslimatı çözüm sayılmaz. Buzdolabında yaklaşık 4°C veya altı, dondurucuda yaklaşık -18°C veya altı ölçüm hedefi görünürdür. Ticari mutfak, ilaç, aşı ve laboratuvar yükleri tüketici cihazına yönlendirilmez. Mevcut termometre veya alarm bağımsız doğrulama, pil, yerleşim ve gerçek kullanım testini karşılıyorsa satın almama sonucu verilir.

### Affiliate kategorileri

- buzdolabı/dondurucu cihaz termometresi;
- yüksek sıcaklık alarmı ve min/max hafızalı termometre;
- yalnız gerçek ihtiyaçta yerel kayıt/alarmı da bulunan uzaktan sıcaklık izleme sınıfı.

### Kullanıcı faydası

Kullanıcı cihaz ekranını veya Wi-Fi bildirimini gıda güvenliği garantisi saymaz. Kesinti süresi, bağımsız sıcaklık kanıtı, pil, hafıza ve bağlantı kaybı davranışı birlikte değerlendirilir.

### Beklenen gelir etkisi

Ev ve yazlık kullanıcısında orta-yüksek potansiyel. Ürün sınıfı basit termometreden uzaktan alarma doğru yalnız gerçek görev ihtiyacı kadar genişletilir.

## Aksiyon 3 — Tatil ve yazlık ev tekrar ziyaret merkezi

Yeni rota:

`/sektor-rehberi/tatil-yazlik-ev-elektrik-su-guvenlik-merkezi/`

Merkez doğrudan affiliate bağlantısı göstermez. Kullanıcının planını şu sıraya koyar:

```text
aktif tehlike
→ resmî/profesyonel kanal
→ açık kalacak elektrik ve su görevleri
→ sıcaklık, duman ve CO kanıtı
→ modem/bulut bağımlılığı
→ fiziksel kontrol
→ 7/30/90 günlük tekrar test
```

Kullanıcı kişisel veri vermeden JSON görev planı ve `.ics` takvimi oluşturabilir.

### Tekrar ziyaret nedenleri

- her tatil veya uzun seyahat öncesi;
- yazlığı sezonluk kapatma ve yeniden açma;
- elektrik kesintisi veya su kaçağı sonrası;
- yeni buzdolabı, modem, alarm, sensör veya tesisat değişikliği;
- düşük pil, bildirim kaybı veya başarısız gerçek test;
- 7 günlük olay sonrası, 30 günlük hazırlık veya 90 günlük bakım kontrolü.

### Kullanıcı faydası

Kullanıcı evi tek bir “ana şalteri kapat” tavsiyesiyle yönetmez. Açık kalması gereken yükler, gıda, alarm, su ve uzaktan izleme bağımlılıkları ayrı görevler hâline gelir.

### Beklenen gelir etkisi

Doğrudan affiliate etkisi düşük; yeni iki hesaplayıcıya geçiş, tekrar ziyaret, marka güveni ve daha sonra oluşan nitelikli ürün ihtiyacı etkisi yüksektir.

## Dönüşüm sözleşmesi

```text
arama niyeti
→ ücretsiz kişisel verisiz teknik test
→ aktif tehlike ve profesyonel kapsam ayrımı
→ mevcut ekipmanın gerçek testi
→ yeterliyse satın almama
→ gerçek görev açığında üç ayrı kullanıcı onayı
→ açıkça belirtilen Amazon satış ortaklığı ürün sınıfı
→ periyodik yeniden test
```

Affiliate bağlantıları `rel="sponsored nofollow noopener"` taşır. Doğrudan Amazon URL'si eklenmez. Fiyat, stok, puan, yorum, satıcı, teslimat veya garanti yayımlanmaz. Product, Offer, availability veya aggregateRating şeması kullanılmaz.

## Güven ve gizlilik sınırları

- ALO186; EDAŞ, su idaresi, itfaiye, sağlık/gıda otoritesi, sigorta şirketi, tesisatçı, üretici, servis veya satıcı gibi gösterilmez.
- Ad, telefon, e-posta, adres, konum, seyahat tarihi, sağlık kaydı, gıda listesi veya seri numarası istenmez.
- `localStorage`, `sessionStorage`, geolocation ve haricî veri isteği kullanılmaz.
- Aktif su-elektrik tehlikesi, aktif kesinti, ticari/medikal soğuk zincir ve profesyonel tesisat senaryolarında ticari yol kapalıdır.
- Mevcut cihaz yeterliyse yeni ürün önerilmez.

## Birincil kaynak yaklaşımı

- EPA WaterSense: nem algılayan sensör ve akış izleme cihazı ayrımı, kurulum ve bakım.
- USDA FSIS: cihaz termometresi; buzdolabında yaklaşık 4°C, dondurucuda yaklaşık -18°C hedefi; kesinti sırasında kapıların kapalı tutulması ve sıcaklık kanıtı.
- CDC: su basmış alanda su içinde dururken elektrikli anahtar, cihaz ve ekipman kullanılmaması.

Bu kaynaklar Türkiye’de tesisat, gıda güvenliği, sigorta veya ürün uygunluk onayı olarak sunulmaz; güncel yerel resmî rehber, tam model üretici belgesi ve yetkili uzman önceliklidir.

## Yayın kabulü

- Routing overlay v138 ile üç canonical rota ve sitemap entegrasyonu.
- İki modül testi ve 25 karar/yayın senaryosu.
- Custom-domain ve `/chatgpt` Pages build/smoke kabulü.
- Kişisel verisiz Teknik Arama entegrasyonu.
- Mevcut release, portal ve cihaz hasarı süresi regresyonları.