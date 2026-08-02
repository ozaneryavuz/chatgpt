# ALO186 güvenlik kamerası, NVR, PoE ve UPS büyüme denetimi v200

Tarih: 2 Ağustos 2026

## Arama niyeti ve içerik boşluğu

Canlı site; elektrik kesintisi, UPS, modem/ONT ve genel acil aydınlatma niyetlerini karşılıyor. Buna karşılık şu yüksek niyetli sorular için kamera kayıt zincirini birlikte ele alan özel bir kullanıcı yolculuğu bulunmuyordu:

- Güvenlik kamerası elektrik kesilince kayıt yapar mı?
- 4, 8 veya daha fazla IP kamera için UPS kaç saat çalışır?
- NVR ve PoE switch birlikte UPS'e bağlanmalı mı?
- PoE switch güç bütçesi kamera sayısına yeter mi?
- İnternet kesilince yerel kamera kaydı devam eder mi?
- Kamera sistemi UPS testi nasıl yapılır?

Genel UPS sayfası, kamera gece IR yükü, PoE toplam bütçesi, NVR/disk, yerel kayıt ile uzaktan erişim ayrımı ve düzenli kayıt provası için yeterince görev odaklı değildir. Bu paket yeni bir genel UPS makalesi üretmek yerine doğrulanmış bu içerik boşluğuna odaklanır.

## Seçilen üç aksiyon

1. **Kamera–PoE–NVR UPS çalışma süresi hesabı**
   - kamera adedi ve kamera başına W,
   - gece IR/ısıtıcı/hareket rezervi,
   - PoE switch veya PoE NVR taban yükü,
   - NVR/disk, NAS/ek yük ve gerekli router/ONT,
   - UPS kullanılabilir Wh, verim, batarya rezervi, hedef süre ve sürekli W sınırı,
   - mevcut gerçek test yeterliyse “yeni ürün almayın”.

2. **Üçlü güven kapılı ürün seçici**
   - model uyumlu AC UPS sınıfı,
   - belgeli toplam güç bütçesine sahip PoE switch sınıfı,
   - güvenli priz tipi enerji ölçer sınıfı,
   - en fazla üç sınıf; statik Amazon bağlantısı yok,
   - teknik uygunluk, gerçek ihtiyaç ve satış ortaklığı ilişkisi ayrı ayrı onaylanır.

3. **30/90 günlük kamera kesinti test merkezi**
   - mahremiyet ve yetki kontrolü,
   - tam model güç belgeleri ve PoE bütçesi,
   - gece modu, örnek kayıt, disk sağlığı ve tarih-saat,
   - internetsiz yerel kayıt ile uzaktan erişim ayrımı,
   - UPS fiziksel durum ve gerçek kesinti provası,
   - kişisel verisiz JSON, 30 günlük kısa kontrol ve 90 günlük tam prova ICS.

## Kullanıcı yolculuğu

Arama niyeti → ücretsiz tam-zincir yük hesabı → tam model/gerçek ölçüm → mevcut UPS provası → yalnız doğrulanmış eksik sınıf → üç affiliate onayı → Amazon seçenekleri.

Aşağıdaki durumlarda ticari yol kapanır:

- şişmiş, sızdıran veya aşırı ısınan batarya,
- yanık kokusu, su teması, gevşek priz veya hasarlı kablo,
- bina çapında profesyonel sistem,
- yangın algılama, acil çağrı, erişim kontrolü veya yaşam güvenliğiyle bütünleşik sistem,
- mevcut sistemin gerçek provada hedefi karşılaması.

## Affiliate ürün kategorileri

### Model uyumlu AC UPS

Yalnız bütün kayıt zincirinin toplam W/VA yükü ve hedef süresi doğrulandıktan sonra değerlendirilir. Marka veya model üstünlüğü, fiyat, stok, puan, garanti ya da çalışma süresi iddiası yayımlanmaz. Üreticinin tam model yük–süre tablosu önceliklidir.

### Belgeli PoE switch

Yalnız mevcut switch port standardı veya toplam PoE bütçesi yetersizse gösterilir. Kamera sayısı tek başına satın alma gerekçesi değildir; tam model kamera tüketimi, gece modu ve toplam bütçe doğrulanır.

### Priz tipi enerji ölçer

Yalnız toplam AC yük bilinmiyorsa ve ölçüm sağlam, kuru, topraklı kullanıcı prizinde güvenle yapılabiliyorsa gösterilir. Pano, sabit tesisat veya açılmış cihaz üzerinde ölçüm önerilmez.

## Dönüşüm noktaları

- `camera_ups_calculated`: toplam W, tahmini süre ve doğrulama durumu.
- `camera_ups_no_buy`: mevcut sistem yeterli sonucu.
- `affiliate_gate_viewed`: seçilen doğrulanmış sınıflar.
- `affiliate_gate_passed`: üç güven onayının tamamlanması.
- `affiliate_no_buy_selected`: satın almama seçimi.
- `affiliate_product_clicked`: yalnız kapı sonrası Amazon geçişi.
- `camera_test_assessed`: tamamlanan test görevi sayısı.
- `camera_test_no_buy`: bütün testler başarılı sonucu.
- JSON ve ICS dışa aktarma olayları.

Bu olaylar kişisel veri, kamera görüntüsü, adres, IP, parola, seri numarası veya konum içermez.

## Tekrar ziyaret nedenleri

- kamera, PoE switch, NVR, disk, router/ONT veya UPS değişikliği,
- kamera gece modu, çözünürlük, kare hızı veya firmware değişikliği,
- UPS batarya yaşlanması ve gerçek sürenin düşmesi,
- kayıt doluluk ve disk sağlık uyarısı,
- internet sağlayıcısı veya uzaktan erişim düzeni değişikliği,
- gerçek kesinti, bakım veya cihaz arızası,
- kullanıcı yetkisi ve mahremiyet kapsamı değişikliği,
- 30/90 günlük tekrar kontrol tarihleri.

## Beklenen kullanıcı faydası

- “8 kamera için kaç VA?” gibi eksik soruyu bütün güç zinciri ve hedef süre hesabına dönüştürür.
- Yalnız NVR'yi yedekleyip PoE switchi enerjisiz bırakma hatasını azaltır.
- İnternet, yerel kayıt, uzaktan erişim ve bildirim işlevlerini ayırır.
- Kamera ışığının yanmasını kayıt kanıtı saymak yerine örnek dosya ve tarih-saat kontrolü ister.
- Mevcut sistem yeterliyse görünür satın almama sonucu sunar.
- Profesyonel ve yaşam güvenliği sistemlerini tüketici affiliate yolundan çıkarır.

## Beklenen gelir etkisi

UPS ve PoE switch kategorileri genel kesinti ürünlerine göre daha yüksek sepet değerine sahip olabilir; ancak bu paket gelir veya sipariş garantisi vermez. Beklenen etki, rastgele ürün tıklamasını artırmak değil:

- açık teknik ihtiyeti bulunan kullanıcıyı mağazaya taşımak,
- yanlış ürün ve iade riskini azaltmak,
- ölçüm → test → bakım döngüsüyle tekrar ziyaret oluşturmak,
- güven kapısından geçen tıklamaların niteliğini yükseltmektir.

Başarılı test satış oluşturmaz. Gelir etkisi, `affiliate_gate_passed / affiliate_gate_viewed`, `affiliate_product_clicked / affiliate_gate_passed` ve no-buy oranlarıyla zaman içinde ölçülmelidir.

## Korunan ticari sözleşme

- Doğrulanmamış fiyat, stok, satıcı, puan, yorum, teslimat veya garanti yayımlanmaz.
- Statik Amazon bağlantısı bulunmaz.
- Affiliate ilişkisi bağlantı açılmadan önce görünürdür.
- Amazon bağlantısı `alo186rehber-21` etiketi ve `rel="sponsored nofollow noopener"` ile yalnız üç onaydan sonra oluşturulur.
- Gösterilen ürün sınıfı en fazla üçtür.
- Mevcut sistem yeterliyse yeni ürün alınmaz.
- Tehlike, profesyonel sistem ve yaşam güvenliği kullanımında ticari yol kapanır.
- Product, Offer ve AggregateRating şeması kullanılmaz.
- Kamera görüntüsü, adres, konum, IP, kullanıcı adı, parola, seri numarası veya başka kişisel veri istenmez.
- ALO186 resmî kurum, güvenlik şirketi, kamera üreticisi veya satıcı gibi sunulmaz.
- Hukuka aykırı veya mahremiyeti ihlal eden kamera kullanımı desteklenmez.

## Birincil kaynaklar

- Cisco — Power over Ethernet: aynı Ethernet kablosunda veri ve DC güç, PSE/PD ilişkisi.
- Axis — PoE güç yönetimi: toplam bütçe, cihaz sınıfı ve gerçek tüketim ayrımı.
- APC — UPS seçim rehberi: W ve VA sınırları, kapasite payı ve yük–süre ilişkisi.
- Eaton — UPS yük ve çalışma süresi araçları: çalışma süresinin bağlı watt yüküne ve batarya koşullarına bağlı olduğu sınırı.

Kaynak kontrolü 2 Ağustos 2026 tarihinde yapıldı. Tam model üretici belgesi ve yetkili sistem tasarımı her zaman önceliklidir.
