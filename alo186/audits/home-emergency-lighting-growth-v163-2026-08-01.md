# ALO186 ev acil aydınlatma büyüme denetimi v163

Tarih: 1 Ağustos 2026

## Seçim özeti

Bu çalıştırmada yeni bir yüksek riskli teknik ürün sınıfı eklemek yerine, ana sayfada zaten görünür olan “acil durum aydınlatması” ticari niyetini güvenli ve ölçülebilir bir kullanıcı yolculuğuna dönüştüren üç aksiyon seçildi. Konu; geniş kesinti arama niyeti, düşük teknik giriş eşiği, mevsimsel tekrar ihtiyacı, güvenli tak-çalıştır affiliate kategorileri ve mum kaynaklı yangın riskini azaltma potansiyeli nedeniyle önceliklendirildi.

## Arama niyeti

Birincil sorgular:

- elektrik kesintisinde mum kullanılır mı
- elektrik kesintisinde el feneri
- şarjlı fener kaç saat çalışır
- lümen ne demek, çalışma süresini gösterir mi
- kamp feneri mi el feneri mi
- kafa feneri mi şarjlı fener mi
- acil durum feneri nasıl seçilir
- şarjlı fener ısınıyor
- fener pili ne sıklıkla kontrol edilir
- elektrik kesintisi hazırlık çantası fener

Niyet katmanları:

1. **Acil güvenlik:** duman, gaz, açık alev, karanlıkta yön bulma.
2. **Bilgilendirici:** lümen, watt, Wh ve çalışma süresi farkı.
3. **Karşılaştırma:** el feneri, lantern ve kafa fenerinin görev ayrımı.
4. **Ticari:** gerçek aydınlatma açığı doğrulandıktan sonra kategori araştırması.
5. **Tekrar ziyaret:** şarj, batarya, geri çağırma ve gerçek süre testi.

## İçerik boşluğu

ALO186 ana sayfası acil aydınlatmayı ürün rehberi olarak gösteriyordu; fakat aşağıdaki görevleri aynı fail-closed zincirde çözen canonical araçlar bulunmuyordu:

- aktif tehlike ile sıradan kesintiyi ayırma,
- mumun açık alev riskini ürün satışından önce açıklama,
- lümeni çalışma süresi sanma hatasını önleme,
- Wh ve W kanıtı varsa temkinli süre hesabı yapma,
- mevcut çalışan fener yeterliyse “yeni ürün almayın” sonucu verme,
- geri çağırma, şişme, ısınma ve modifiye şarj durumunda affiliate'i kapatma,
- kişisel veri istemeden 7/30/90 günlük tekrar test planı oluşturma.

## Kullanıcı yolculuğu

### 1. Güvenlik ayrımı

`/hesaplama/elektrik-kesintisi-el-feneri-mum-guvenligi/`

Kullanıcı önce duman, alev, gaz, su, elektriksel hasar, içeride kişi ve hasarlı batarya durumunu ayırır. Aktif tehlikede 112 eşiği gösterilir; ürün ve affiliate yolu açılmaz. Güvenli mevcut fener varsa satın almama sonucu verilir.

### 2. Teknik uygunluk ve süre

`/hesaplama/sarjli-fener-acil-aydinlatma-lumen-wh-sure-uygunlugu/`

Kullanıcı görev türünü, mevcut ürünü, batarya Wh, kullanılan mod W, hedef süre, şarj kanıtı, geri çağırma ve çocuk erişimini değerlendirir. Yaklaşık süre yalnız `Wh × 0,75 ÷ W` ile hesaplanır; lümen çalışma süresi hesabına dönüştürülmez. Aktif kesinti, profesyonel alan, hasar, belirsiz teknik kanıt ve çalışan mevcut ürün affiliate'i kapatır.

### 3. Tekrar test merkezi

`/sektor-rehberi/ev-acil-aydinlatma-batarya-test-merkezi/`

Kullanıcı kişisel veri vermeden görev planı, JSON dosyası ve 7/30/90 günlük ICS kayıtları üretir. Merkez doğrudan affiliate bağlantısı içermez ve önce iki ücretsiz araca yönlendirir.

## Affiliate ürün kategorileri

Yalnız olay öncesi tek konut hazırlığında, güvenli mevcut ürünün bulunmadığı veya gerçek süreyi karşılamadığı doğrulanırsa:

- oda genel aydınlatması için taşınabilir LED lantern / şarjlı fener kategorisi,
- kısa yön bulma için kompakt LED el feneri kategorisi,
- eller serbest kısa kontrol için LED kafa feneri kategorisi.

Ticaret dışı kapsam:

- mum, kibrit ve açık alev,
- gevşek 18650 hücre veya modifiye batarya paketi,
- ortak alan ve profesyonel acil aydınlatma,
- aktif kesinti sırasında teslimata dayalı çözüm,
- hasarlı, şişmiş, sızıntılı, aşırı ısınan veya geri çağrılan ürün,
- yalnız satıcı açıklamasına dayanan teknik seçim.

Bağlantılar görünür Amazon satış ortaklığı açıklamasından ve üç ayrı onaydan sonra açılır; `rel="sponsored nofollow noopener"` ve `tag=alo186rehber-21` kullanılır. Doğrulanmamış fiyat, stok, puan, satıcı, teslimat veya garanti yayımlanmaz.

## Dönüşüm noktaları

1. Güvenlik aracından teknik uygunluk aracına geçiş: yalnız çalışan ışık yoksa veya telefon flaşı geçici çözümse.
2. Teknik uygunluk sonucundan kategori araştırmasına geçiş: yalnız hazırlık zamanı, tek konut, doğrulanmış güvenlik/etiket ve gerçek ihtiyaç açığında.
3. Mevcut ürün yeterliyse test merkezine geçiş: satın alma yerine bakım ve tekrar ziyaret.
4. Test merkezinden 30 ve 90 günlük geri dönüş: şarj/işlev ve gerçek süre kontrolü.

## Tekrar ziyaret nedenleri

- gerçek elektrik kesintisi veya tahliye olayı,
- yeni fener, pil, batarya veya şarj kablosu,
- azalan çalışma süresi,
- şişme, koku, sızıntı, düşme veya su teması,
- üretici geri çağırması,
- yeni çocuk, evcil hayvan veya erişilebilirlik ihtiyacı,
- fırtına, seyahat ve araç acil çantası hazırlığı,
- ev düzeni veya güvenli çıkış yolunun değişmesi.

## Kaynak doğrulaması

- U.S. Fire Administration: elektrik kesintisinde mum yerine el feneri kullanılması; açık alevin devrilme ve yangın riski.
- CPSC, 15 Ocak 2026: belirli bir şarjlı lantern modelinde lityum iyon bataryanın aşırı ısınma riski ve tam model/tarih kodu geri çağırma yaklaşımı.
- Ready.gov, 26 Ağustos 2025 güncellemesi: kesinti hazırlığında el feneri, yedek pil ve düzenli batarya/fener kontrolü.
- IEC 62133-2:2017+A1:2021: taşınabilir kapalı lityum hücre ve batarya güvenlik kapsamı.
- IEC 60598-2-22:2014+A1:2017: acil aydınlatma armatürlerinin özel gerekleri.

Standart veya resmî rehber adı, belirli ürünün uygunluk sertifikası ya da Türkiye'deki profesyonel acil aydınlatma projesi için otomatik kabul anlamına gelmez.

## Beklenen kullanıcı faydası

### Aksiyon 1 — kesinti, fener ve mum güvenliği

- Açık alev yerine güvenli taşınabilir ışık önceliği oluşturur.
- Aktif duman, gaz, su ve hasarlı bataryada ürüne yönlendirme yapmaz.
- Çalışan mevcut fener varsa yeni ürün almayı engeller.

Beklenen fayda: **yüksek güvenlik ve güven etkisi**.

### Aksiyon 2 — lümen–Wh–süre uygunluğu

- Lümen, watt ve Wh kavramlarını ayırır.
- Desteksiz çalışma süresi vaadi yerine kanıta dayalı temkinli hesap ve gerçek test ister.
- Yanlış ürün sınıfı ve gereksiz yüksek lümen satın alımını azaltır.

Beklenen fayda: **yüksek karar kalitesi**.

### Aksiyon 3 — tekrar test merkezi

- Ürün alışverişini düzenli şarj, fiziksel kontrol ve gerçek süre testine dönüştürür.
- Kişisel veri istemeden tekrar ziyaret mekanizması kurar.

Beklenen fayda: **orta-yüksek hazırlık ve sadakat etkisi**.

## Beklenen gelir etkisi

- Güvenlik aracı: doğrudan düşük; geniş organik giriş ve güven etkisi yüksek.
- Uygunluk aracı: düşük-orta sepetli fakat geniş arama niyeti nedeniyle **orta-yüksek nitelikli affiliate potansiyeli**.
- Test merkezi: doğrudan düşük; 30/90 günlük tekrar ziyaret ve gelecekteki doğrulanmış ihtiyaç nedeniyle **yüksek yaşam boyu değer etkisi**.

Gelir, ham tıklama sayısı yerine gerçek ihtiyaç, düşük iade riski, açık ticari açıklama ve kullanıcı güveninin korunması üzerinden hedeflenir.

## Güven sözleşmesi

- Mevcut sistem yeterli — yeni ürün almayın.
- Aktif tehlike ve aktif kesintide affiliate kapalı.
- Profesyonel ve ortak alanlarda tüketici ürünü ikamesi yok.
- Fiyat, stok, puan, satıcı, teslimat ve garanti yok.
- `Product`, `Offer`, `availability` ve `aggregateRating` yok.
- Kişisel veri, konum ve kalıcı tarayıcı depolaması yok.
- ALO186 resmî kurum, üretici, servis veya test laboratuvarı gibi gösterilmez.
