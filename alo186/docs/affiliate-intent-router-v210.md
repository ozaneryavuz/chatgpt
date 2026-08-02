# ALO186 affiliate ihtiyaç yönlendiricisi v210

Tarih: 2 Ağustos 2026

## Amaç

Ürün merkezindeki çok sayıdaki teknik rota arasında karar yükünü azaltmak; kullanıcıyı doğrudan mağazaya değil, kendi görevine uygun ücretsiz teknik araca ve yalnız doğrulanmış ihtiyaçta güven kapılı ürün seçiciye taşımak.

## Seçilen 3 aksiyon

1. **30 saniyelik ihtiyaç yönlendiricisi**
   - Kullanıcı yalnız kapalı seçeneklerle görev, hedef süre ve mevcut çözüm durumunu seçer.
   - Sekiz görev desteklenir: internet, USB-C iletişim, aydınlatma, soğuk zincir, enerji ölçümü, kamp/araç enerjisi, teknik karşılaştırma ve sabit/profesyonel sistem.
   - Sonuç önce ücretsiz teknik aracı gösterir.

2. **Satın almama ve uzmanlık devre kesicisi**
   - Mevcut güvenli çözüm gerçek testte yeterliyse yeni ürün bağlantısı gösterilmez.
   - Hasarlı, ıslak, şişmiş, aşırı ısınan veya yanık kokulu ekipmanda ticari yol kapatılır.
   - Sabit tesisat, yüksek güç, üç faz ve profesyonel sistemlerde tüketici affiliate yolu kapalıdır.
   - Ürün seçici yalnız mevcut çözümün yok veya yetersiz olduğu düşük riskli görevlerde görünür.

3. **Kişisel verisiz kaldığın yerden devam ve ölçüm**
   - Yalnız üç kapalı seçim cihazda 14 gün tutulur.
   - Ad, telefon, e-posta, adres, konum, marka, model, fiyat veya seri numarası kaydedilmez.
   - Kullanıcı önceki seçimine dönebilir veya kaydı temizleyebilir.
   - Kişisel veri taşımayan olaylar no-buy, risk engeli, profesyonel yönlendirme, devam ve CTA tıklamalarını ayrı ölçer.

## Kullanıcı yolculuğu

```text
ürün merkezi
→ görev + süre + mevcut çözüm durumu
→ ücretsiz hesap / test / karşılaştırma
→ mevcut sistem yeterliyse satın almama
→ risk veya sabit sistemde ticaret kapalı
→ yalnız gerçek düşük riskli açıkta ürün seçici
```

## Affiliate ve güven sınırları

- Yönlendiricide doğrudan Amazon URL'si yoktur.
- Affiliate etiketi veya ASIN depolanmaz.
- Fiyat, stok, puan, satıcı, teslimat ve garanti bilgisi yayımlanmaz.
- Product, Offer veya AggregateRating eklenmez.
- ALO186 ürün satıcısı, EDAŞ veya kamu kurumu gibi gösterilmez.
- Uzun süre hedefi otomatik ürün veya kapasite seçimi sayılmaz; gerçek yük, enerji kapasitesi ve kurulum sınırı ayrıca doğrulanır.

## Ölçüm olayları

- `affiliate_intent_router_view`
- `affiliate_intent_result`
- `affiliate_intent_no_buy`
- `affiliate_intent_blocked`
- `affiliate_intent_professional`
- `affiliate_intent_resume_available`
- `affiliate_intent_resume`
- `affiliate_intent_cta_click`
- `affiliate_intent_reset`

## Beklenen kullanıcı ve gelir etkisi

Kullanıcı, uzun ürün listesini taramak yerine kendi görevi için doğru başlangıç aracına ulaşır. Satın almama ve risk engelleri güven kaybını azaltır. Ürün seçiciye yalnız teknik açığı daha belirgin kullanıcıların geçmesi, ham mağaza tıklamasından çok daha nitelikli affiliate trafiği hedefler. 14 günlük devam kaydı, kişisel veri toplamadan tekrar ziyaret nedeni oluşturur.

## Yayın kontrolü

- Custom-domain ve `/chatgpt` base path desteği
- İdempotent enjeksiyon
- Sekiz görev ve üç soru
- 14 günlük kapalı seçim kaydı
- Doğrudan Amazon URL'si bulunmaması
- no-buy, risk ve profesyonel kapanışları
- commerce guard ve GitHub Pages smoke kontrolü
