# ALO186 portal satın alma kontrol noktası v213

Tarih: 2 Ağustos 2026

## Değerlendirme

Elektrik portalında doğrudan ürün karşılaştırma bağlantıları ve görünür satış ortaklığı açıklaması bulunuyor. En yüksek potansiyelli boşluk daha fazla ürün eklemek değil; ürün alanından hemen önce kullanıcının sürdürmek istediği görevi, ücretsiz doğrulama aracını ve satın almama sonucunu görünür hâle getirmekti.

## Seçilen üç aksiyon

### 1. Görev bazlı satın alma kontrol noktası

Ürün karşılaştırma bölümünden önce üç yüksek niyetli kullanıcı yolculuğu gösterilir:

- modem ve ONT ile internet sürekliliği,
- telefon şarjı ve güvenli kesinti aydınlatması,
- buzdolabı, dondurucu ve soğuk zincir.

Her yolculuk önce ücretsiz hesap veya rehbere, sonra ilgili teknik ürün seçiciye gider. Kontrol noktasının içinde doğrudan Amazon bağlantısı bulunmaz.

### 2. Satın almama ve risk devre kesicisi

Kontrol noktası şu sınırları görünür biçimde uygular:

- mevcut güvenli çözüm gerçek testte yeterliyse yeni ürün alınmaz,
- ıslak, hasarlı, şişmiş veya aşırı ısınan ekipmanda ürün seçimine ilerlenmez,
- fiyat, stok, puan, satıcı veya garanti bilgisi yayımlanmaz,
- ALO186'in ürün satıcısı, EDAŞ veya kamu kurumu olmadığı açıklanır,
- satış ortaklığı ilişkisi teknik seçiciden önce belirtilir.

### 3. Otuz günlük tekrar test nedeni

Her görev kartı kişisel veri istemeyen bir ICS takvim kaydı üretir. Hatırlatıcı, mevcut ekipmanın 30 gün sonra yeniden denenmesini ve yeterliyse yeni ürün alınmamasını söyler. Sunucuya kayıt gönderilmez ve kalıcı tarayıcı depolaması kullanılmaz.

## Dönüşüm ölçümü

Anonim görev ve bağlantı türü düzeyinde üç olay oluşturulur:

- `portal_purchase_checkpoint_view`
- `portal_purchase_checkpoint_click`
- `portal_purchase_retest_download`

Ham mağaza hedefi, ASIN, arama sorgusu veya kullanıcı kimliği olaylara eklenmez.

## Beklenen etki

Kullanıcı faydası; ürün listesine geçmeden önce gerçek ihtiyacı ayırmak, uyumsuz veya gereksiz alışverişi azaltmak ve ekipmanı düzenli yeniden test etmektir.

Gelir etkisi; genel ürün tıklaması yerine mini UPS, USB-C/aydınlatma ve soğuk zincir seçicilerine daha nitelikli trafik taşınmasıdır. Gelir veya dönüşüm garantisi verilmez.

## Yayın entegrasyonu

Yeni modül mevcut tek yetkili Pages artifactında commerce guard çalışırken eklenir. Guard, modülü ekledikten sonra tüm ticari sayfaları fail-closed biçimde doğrulamaya devam eder. Mevcut mağaza bağlantıları değiştirilmez; yeni kontrol noktası yalnız iç teknik rotalar kullanır.
