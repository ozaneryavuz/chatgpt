# ALO186 kullanıcı odaklı site denetimi — 31 Temmuz 2026

## Kapsam

Canlı ana giriş, EDAŞ/kesinti karar akışı, elektrik portalı, hesaplayıcılar, ürün seçim rotası, sektör rehberleri, kurumsal hizmet ve yasal/güven sayfaları; ayrıca üretim artifactındaki bütün HTML sayfalarına uygulanan ortak kalite katmanı.

Denetim yalnız kaynak şablonlarını değil, canonical üretimden sonra oluşan custom-domain ve `/chatgpt` GitHub Pages paketlerini de kapsar. V117 kabulünde iki hedefte toplam 456 HTML sayfası incelenmiş, ortak UX katmanı bütün sayfalara uygulanmış ve H1 kapsamı yüzde 100 doğrulanmıştır.

## Öncelikli bulgular

### P1 — Ana girişte karar yoğunluğu

Ana sayfa güçlü ve güvenilir içerik taşıyor; ancak kesinti, güvenlik, ürün, teknik makale ve kurumsal hizmet rotaları aynı anda görünür olduğunda ilk kez gelen kullanıcı için seçenek yükü artıyor. Birincil başlangıç Elektrik Durum Merkezi olmalı; diğer rotalar ikincil keşif olarak kalmalı.

### P1 — Mobil okunabilirlik ve taşma dayanıklılığı

Kart, grid, form ve uzun teknik başlıklarda min-width, satır kırma ve dokunma hedefi sözleşmesi tüm ortak stillerde korunmalı. Hata gizlemek için `body overflow-x:hidden` kullanılmamalı.

### P1 — Project-path ve dil bağlamı

Ortak mobil hızlı erişimin yalnız alan adı kökünü varsayması, `/chatgpt` paketinde kullanıcıyı yanlış adrese götürebilir. Aynı Türkçe navigasyonun `/en/` sayfalarında görünmesi de dil bütünlüğünü bozar. Ortak navigasyon base-path ve belge dili üzerinden üretilmelidir.

### P2 — Uzun sayfalarda tarama maliyeti

Alt bölümlerdeki kart ve makale grupları ilk ekranda render edilmek zorunda değil. `content-visibility` ve güvenli intrinsic size kullanımı, özellikle düşük seviye mobil cihazlarda kaydırma ve ilk etkileşim maliyetini azaltabilir. Dört veya daha fazla ana bölümü bulunan uzun rehberlerde erişilebilir bir sayfa içi içerik listesi kullanıcıya tarama kolaylığı sağlar.

### P2 — İçerik sonrasında devam yolunun belirsizliği

Kullanıcı bir hesap, makale, mevzuat veya ürün sayfasını bitirdiğinde yeniden ana menüyü taramak zorunda kalmamalı. Sayfa türüne göre sonuç takibi, resmî kaynak, teknik arama, ürün uygunluğu veya güvenli sonraki adım gösterilmelidir.

### P2 — Ticari ve kamu yararı rotalarının ayrımı

Affiliate, ücretli hizmet ve sponsorlu iş birliği etiketleri görünür kalmalı; teknik güvenlik veya resmî yönlendirme akışından önce ticari CTA gösterilmemeli. Dinamik olarak oluşturulan Amazon bağlantıları da `sponsored nofollow noopener` sözleşmesine otomatik alınmalıdır.

### P2 — İçerik mimarisi

Benzer rehberlerin çoğalması halinde kullanıcının aynı konuda farklı sayfalara dağılması önlenmeli. Her niyet için bir ana sayfa, destekleyici sayfalar için açık breadcrumb, sayfa içi tarama ve geri dönüş rotası kullanılmalı.

## Uygulanan aksiyonlar

### V117 ortak kalite tabanı

- Grid çocuklarında `min-width:0`.
- Başlıklarda dengeli satır kırma.
- Metin bloklarında 72ch okunabilirlik sınırı.
- Etkileşimli öğelerde en az 44px dokunma yüksekliği.
- Form kontrollerinde taşma koruması ve kalıtılan yazı tipi.
- Kartlarda `content-visibility:auto` ve intrinsic render alanı.
- Mobilde uzun başlık/metin satır kırma ve marka kapsayıcı koruması.
- Geniş tablolar için klavye erişilebilir yatay kaydırma kapsayıcısı.
- Görsellerde taşma koruması, sonraki görsellerde lazy loading ve async decoding.
- Dış sekme bağlantılarında `noopener noreferrer`.
- İçerik atlama bağlantısı, aktif rota işareti ve erişilebilir başa dön düğmesi.
- `prefers-reduced-motion`, safe-area ve yazdırma davranışı.

### V118 bağlama duyarlı devam katmanı

- Mobil hızlı erişim custom-domain ve `/chatgpt` taban yoluna göre üretilir.
- İngilizce sayfalarda İngilizce etiketler ve yalnız İngilizce rotalar kullanılır.
- Eksik `lang` ve referrer metadata alanları yayın katmanında tamamlanır.
- Uzun teknik makale, sektör rehberi, mevzuat ve İngilizce içeriklerde erişilebilir sayfa içi içerik listesi oluşturulur.
- Hesaplayıcı, ürün, makale, kesinti ve yasal sayfalara bağlama göre üç güvenli devam rotası eklenir.
- Amazon bağlantıları ilk yüklemede ve sonradan DOM'a eklendiğinde affiliate ilişki ve dış bağlantı güven etiketleriyle güçlendirilir.
- `noindex` teknik köprülerde mobil navigasyon ve ticari devam modülü oluşturulmaz.
- Bütün yayın sayfaları için title, canonical, viewport, dil, referrer, H1, main, görsel alt metni ve form kontrol etiketi kapsamı ölçülür.

## Tasarım ilkesi

Ortak katman sayfa tasarımlarını tek tipe zorlamaz. Her sayfanın mevcut görsel kimliğini korurken yalnız şu çapraz sorunları çözer:

```text
bulunabilirlik
→ okunabilirlik
→ erişilebilirlik
→ güvenli devam
→ ticari şeffaflık
→ tekrar ziyaret
```

## Güven sınırı

Yeni iletişim formu, telefon/e-posta/açık adres/abonelik/T.C. kimlik alanı, konum erişimi, tarayıcı depolaması, resmî kurum izlenimi veya doğrulanmamış ticari yönlendirme eklenmemiştir. Mevcut ürün yeterliyse satın almama sonucu ve tehlike durumunda ticari yolun kapanması korunur.
