# ALO186 ana sayfa affiliate banner ve ürün vitrini v209

Tarih: 2 Ağustos 2026

## Amaç

Ana sayfada kullanıcı güvenini bozmadan affiliate gelir potansiyelini artırmak; ticari alanı güvenlik ve resmî yönlendirmelerin önüne geçirmeden daha görünür hâle getirmek.

## Seçilen 3 aksiyon

1. Görev kartlarından hemen sonra, açık satış ortaklığı açıklamalı ve mevcut ürün yeterliyse satın almama mesajı taşıyan ana banner.
2. Modem mini UPS, powerbank/USB-C, kesinti aydınlatması, soğuk zincir, enerji ölçümü ve kamp/araç enerjisi için altı bağlamsal ürün seçici kartı.
3. Banner görüntülenmesi, ana CTA ve ürün kartı tıklamalarını ayrı ölçen kişisel verisiz GA4 olayları.

## Kullanıcı yolculuğu

Aktif tehlike ve resmî işlem görevleri ana sayfanın üst kısmında korunur. Ticari vitrin doğrudan Amazon bağlantısı içermez. Kullanıcı önce konuya göre ürün haritasına veya ilgili teknik seçiciye gider; mağaza bağlantısı ilgili sayfadaki üçlü güven kapısından sonra açılır.

## Ticari kapsam

- Modem ve ONT mini UPS
- Powerbank ve USB-C şarj ekipmanı
- Şarjlı fener ve acil aydınlatma
- Buzdolabı/dondurucu termometresi ve pasif soğutma
- Priz tipi enerji ölçer ve düşük riskli koruma ürünleri
- Kamp/araç taşınabilir enerji ve solar ürünleri

## Güven sınırları

- Ana sayfada doğrudan Amazon URL'si yoktur.
- Fiyat, stok, puan, satıcı, teslimat ve garanti bilgisi yayımlanmaz.
- Mevcut güvenli ürün yeterliyse yenisinin alınmaması açıkça söylenir.
- Sabit tesisat, aktif tehlike ve profesyonel sistemler bu vitrinde ürünleştirilmez.
- ALO186'in ürün satıcısı veya resmî kurum olmadığı görünür biçimde belirtilir.
- Product, Offer ve AggregateRating yapılandırılmış verileri eklenmez.

## Ölçüm olayları

- `home_affiliate_showcase_view`
- `home_affiliate_banner_click`
- `home_affiliate_product_click`

## Beklenen etki

Banner, ana sayfadan ürün merkezine geçişi artırabilir. Altı görev kartı genel ürün araması yerine yüksek niyetli kategori seçicilerine trafik taşır. Doğrudan mağaza tıklaması yerine güven kapılı kullanıcı yolculuğu korunduğu için ham tıklama değil nitelikli dönüşüm artışı hedeflenir.

## Yayın kontrolü

Custom-domain ve `/chatgpt` artifactları için idempotent enjeksiyon, altı kart, açık affiliate açıklaması, doğrudan Amazon bağlantısı bulunmaması, mobil 3/2/1 düzeni ve commerce guard doğrulanır.
