# ALO186 affiliate karar hunisi v215

**Tarih:** 2 Ağustos 2026  
**Üst çalışma:** GitHub issue #672  
**İlgili görevler:** #676, #677, #678, #679, #685, #686, #687, #688, #689

## Amaç

ALO186 üzerindeki üç yüksek satın alma niyetli kullanıcı yolunu yalnız ürün listesine yönlendirmek yerine aynı karar sözleşmesine bağlamak:

1. Modem / ONT mini UPS uyumluluğu,
2. UPS çalışma süresi ve kapasite sınıfı,
3. Power station kapasite, EPS ve güvenlik uygunluğu.

Yeni akışın sırası:

> hesap veya kapalı teknik seçim → güvenlik kapısı → satın almama kontrolü → en fazla üç teknik sınıf → ilgili ürün seçici

## Uygulanan kullanıcı deneyimi

Her akışta üç seçenek bulunur:

- **Temel:** düşük güç veya kısa süre,
- **Dengeli:** birden fazla küçük yük veya orta süre,
- **Uzun süre:** daha yüksek Wh rezervi ve uzun kesinti.

Her kartta üç karar alanı zorunludur:

- **Kimler için?**
- **Uygun değil**
- **Önce kontrol et**

Ürün CTA’sı varsayılan olarak gizlidir. Yalnız teknik ve güvenlik koşulları sağlandığında ilgili sınıfın CTA’sı açılır.

## Mini UPS güvenlik kapısı

Mini UPS sayfasında kişisel veri istemeyen dört kapalı seçim kullanılır:

- adaptör geriliminin okunması,
- jak ve polaritenin doğrulanması,
- cihaz zinciri,
- hedef süre.

Gerilim, jak veya polarite belirsizse ürün yolu `insufficient_evidence` nedeniyle kapanır. Serbest metin, e-posta, telefon, adres, dosya veya konum alanı yoktur.

## UPS runtime sınıflandırması

Mevcut hesaplayıcı girdilerinden sürekli yük, kalkış katsayısı, Wh, verim, kullanılabilir deşarj, yaş/sıcaklık katsayısı, hedef süre ve rezerv okunur. VA çalışma süresi olarak sunulmaz. 2 kW üzeri veya yüksek kalkışlı yükte tüketici ürün yolu kapanır ve profesyonel koordinasyon açılır.

## Power station güvenlik kapısı

Kapasiteye ek olarak şu kontroller uygulanır:

- hasarsız ekipman,
- kuru ve havalandırılan ortam,
- doğrudan ve güvenli bağlantı,
- doğrulanmış teknik etiket,
- yük türüne göre saf sinüs,
- motor/kompresör için üretici onayı,
- gerekiyorsa PE düzeni,
- gerekiyorsa EPS geçiş süresi,
- gözetimsiz rezistif yük yasağı.

Tıbbi/yaşam güvenliği, sunucu için sıfır milisaniye ihtiyacı, sabit tesisat, bina geri beslemesi ve EV şarjı ticari tüketici yoluna ilerlemez.

## Satın almama sonucu

`no_buy_result`, başarısızlık değildir. Mevcut güvenli çözüm gerçek testte yeterliyse yeni ürün önerilmez. Sahip olunan power station gerekli enerji ve güç sınırlarını karşılıyorsa sistem bu sonucu otomatik üretebilir; diğer akışlarda kullanıcı açıkça satın almama sonucunu seçebilir.

## Ölçüm sözleşmesi

Sürümlü olay sözleşmesi: `alo186/audits/affiliate-event-contract-v215.json`

Olaylar:

- `affiliate_decision_view`
- `affiliate_decision_result`
- `affiliate_decision_select`
- `no_buy_result`
- `commerce_blocked`

İzin verilen boyutlar yalnız kontrollü enum değerleridir: akış, yerleşim, teknik sınıf, uygunluk durumu, kapanış nedeni ve sözleşme sürümü.

## Gizlilik sınırı

GA4 ölçümü yalnız açık analitik onayından sonra çalışır. Ham mağaza URL’si, Amazon arama sorgusu, ASIN, serbest metin, watt/Wh/gerilim/süre gibi sayısal elektrik girdileri ve kullanıcı veya cihaz kimliği analitiğe gönderilmez.

## Ticari ve hukuki sınır

- Yeni modül doğrudan Amazon bağlantısı eklemez.
- Fiyat, stok, puan, satıcı, teslimat ve garanti yayımlamaz.
- Affiliate açıklaması teknik seçiciden önce görünür.
- Yüksek riskli veya profesyonel kapsamda mağaza CTA’sı açılmaz.
- Mevcut çözüm yeterliyse satın almama sonucu korunur.

## Yayın mimarisi

`inject_affiliate_decision_funnel_v215.py`, tek yetkili Pages artifactında `guard_commerce_routes_v3.py` tarafından çalıştırılır. Custom domain, `/chatgpt` project path ve önizleme base path’leri aynı kurala uyar. Modül idempotenttir; ikinci çalıştırmada sayfa bölümleri çoğalmaz.

## Kalite kapıları

- üç base-path senaryosu,
- idempotency,
- eksik hedefte fail-closed davranış,
- harici JS sözdizimi,
- sürümlü olay sözleşmesi eşleşmesi,
- kişisel veri içermeyen kapalı seçimler,
- iki Pages artifactında tam build ve commerce guard,
- doğrudan Amazon linki eklenmemesi

otomatik test edilir.
