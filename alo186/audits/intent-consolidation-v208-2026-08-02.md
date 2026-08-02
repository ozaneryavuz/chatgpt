# ALO186 içerik niyeti birleştirme ve sürdürülebilir büyüme denetimi v208

Tarih: 2 Ağustos 2026

## Bulgular

Teknik içerik envanteri ve yakın dönem PR geçmişi incelendi. Aynı arama görevini karşılayan üç belirgin küme bulundu:

1. Jeneratör Reverse Power / ANSI 32R / negatif kW / motoring: beş ayrı canonical rota.
2. UPS Fan Failure / Overtemperature: iki ayrı canonical rota.
3. Jeneratör Underfrequency / düşük frekans / governor / yük adımı: iki ayrı canonical rota.

Bu kümelerde yeni bir makale eklemek kullanıcıya ek fayda sağlamaktan çok hangi sayfanın güncel olduğu konusunda karar yükü, bölünmüş iç bağlantı sinyali ve dağınık teknik lead ölçümü oluşturabilirdi.

## Seçilen en yüksek potansiyelli 3 aksiyon

### 1. Reverse Power niyetini tek kanonik rehberde birleştirme

Tercih edilen rota:

`/haberler/jenerator-reverse-power-ansi-32r-motoring-ct-polarite-teshis`

Birleştirilen dört eski rota; üretim artifact'ında kullanıcıyı tercih edilen sayfaya yönlendiren, `rel=canonical` taşıyan, sitemap dışında kalan ve resmî kurum izlenimi oluşturmayan hafif geçiş sayfalarına çevrilir.

Kullanıcı faydası: negatif kW, CT/VT faz eşleşmesi, güç yönü ve prime mover tork kaybı aynı güncel teşhis zincirinde bulunur.

Beklenen lead etkisi: beş farklı CTA ve analitik rotası yerine tek teknik ön değerlendirme niyetinde daha temiz ölçüm ve daha güçlü uzmanlık sinyali. Gelir veya sıralama garantisi verilmez.

### 2. UPS fan ve termal alarm niyetini birleştirme

Tercih edilen rota:

`/haberler/ups-fan-failure-overtemperature-hava-akisi-filtre-teshis`

Eski `yüksek sıcaklık / derating` rotası; fan komutu ve tach geri bildirimi, filtre, hava yolu, ortam, yük, sensör ve iç ısı kaynağını birlikte ele alan güncel sayfaya yönlendirilir.

Kullanıcı faydası: fan değişimi, filtre temizliği veya plansız bypass gibi tek sebebe dayalı karar yerine kanıta dayalı ayrım korunur.

Beklenen lead etkisi: UPS bakım ve termal kabul talebi tek rotada ölçülür; affiliate ürün veya doğrulanmamış parça uygunluğu eklenmez.

### 3. Jeneratör düşük frekans niyetini birleştirme

Tercih edilen rota:

`/haberler/jenerator-underfrequency-dusuk-frekans-governor-yuk-adimi-teshis`

Eski `governor hunting / yük alma` rotası; gerçek frekans ölçümü, yük adımı, motor devri, governor/actuator, yakıt-hava yolu, derating ve toparlanma süresini bir arada doğrulayan güncel sayfaya yönlendirilir.

Kullanıcı faydası: düşük frekansın doğrudan governor ayarı veya parça değişimi olarak yorumlanması önlenir.

Beklenen lead etkisi: jeneratör test ve devreye alma niyeti tek kabul sayfasında toplanır; gereksiz ürün veya servis satın alma yönlendirmesi yapılmaz.

## Uygulanan teknik geliştirmeler

- `canonical-aliases.json`: üç arama niyeti kümesi, üç tercih edilen rota ve altı tarihsel alias için merkezi kayıt.
- Üretim derlemesinde alias rotaları için `rel=canonical`, `noindex,follow`, meta refresh ve JavaScript `location.replace` geçiş artifact'ı.
- Artifact içindeki tarihsel iç bağlantıların tercih edilen canonical rotalara otomatik çevrilmesi.
- Ana sitemap'ten yalnız alias rotalarının çıkarılması; tercih edilen canonical rotaların korunması.
- Dil alternatifi kayıtlarının mevcut manifest üzerinden doğrulanmaya devam etmesi.
- Fail-closed artifact doğrulaması: alias hedefi, canonical etiketi, yönlendirme, bağımsızlık açıklaması ve affiliate bağlantısı bulunmaması.
- Routing v208 ve özel GitHub Actions kalite işi.

Kaynak HTML dosyaları korunur; böylece tarihsel içerik ve test kanıtı silinmeden yalnız yayın artifact'ı konsolide edilir. Bu yaklaşım geri alınabilir ve merkezi alias kayıt dosyasıyla yönetilir.

## Ticari ve güven sınırları

- Yeni Amazon veya başka mağaza bağlantısı eklenmedi.
- Fiyat, stok, puan, satıcı, teslimat ve garanti bilgisi kullanılmadı.
- `Product`, `Offer` veya `AggregateRating` eklenmedi.
- Alias sayfaları ürün veya hizmet satın almaya yönlendirmez.
- ALO186'in EDAŞ, TEDAŞ, EMO veya kamu kurumu olmadığı geçiş sayfasında açıkça belirtilir.
- Teknik uygunluk, arıza çözümü, proje onayı veya kesintisiz çalışma garantisi verilmez.

## Doğrulanan yöntem kaynakları

2 Ağustos 2026 tarihinde Google Search Central kaynakları yeniden kontrol edildi:

- Canonicalization overview: https://developers.google.com/search/docs/crawling-indexing/canonicalization
- Canonical URL methods: https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls
- Sitemap overview: https://developers.google.com/search/docs/crawling-indexing/sitemaps/overview
- Sitemap building guidance: https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap

Google; redirect ve `rel=canonical` sinyallerini güçlü, sitemap katılımını daha zayıf bir canonical tercihi olarak açıklar. İç bağlantıların tercih edilen URL'ye verilmesini ve sitemap'te gösterilmek istenen canonical URL'lerin listelenmesini önerir. Canonical seçimi, tarama veya indeksleme sonucu garanti değildir.

## Tamamlanamayan kontroller

- Search Console URL Inspection ve sitemap yeniden gönderimi için bağlı Search Console yazma aracı bulunmuyor.
- GitHub Pages ve özel alan adı dağıtımının merge sonrasında tamamlandığı bağımsız canlı HTTP kontrolüyle doğrulanmalıdır.
- GitHub Pages sunucu tarafı 301 üretmediği için üretim artifact'ında HTML canonical + istemci yönlendirmesi kullanılır. Sunucu tarafı yönlendirme desteklenen barındırmada HTTP 301 tercih edilmelidir.
- Arama motorlarının canonical seçimi, yeniden tarama tarihi ve sıralama etkisi anlık değildir ve garanti edilemez.
