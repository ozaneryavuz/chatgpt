# ALO186 kullanıcı odaklı site denetimi — 31 Temmuz 2026

## Kapsam

Canlı ana giriş, EDAŞ/kesinti karar akışı, elektrik portalı, hesaplayıcılar, ürün seçim rotası, sektör rehberleri, kurumsal hizmet ve yasal/güven sayfaları; ayrıca üretim artifactındaki bütün HTML sayfalarına uygulanan ortak kalite katmanı.

## Öncelikli bulgular

### P1 — Ana girişte karar yoğunluğu
Ana sayfa güçlü ve güvenilir içerik taşıyor; ancak kesinti, güvenlik, ürün, teknik makale ve kurumsal hizmet rotaları aynı anda görünür olduğunda ilk kez gelen kullanıcı için seçenek yükü artıyor. Birincil başlangıç Elektrik Durum Merkezi olmalı; diğer rotalar ikincil keşif olarak kalmalı.

### P1 — Mobil okunabilirlik ve taşma dayanıklılığı
Kart, grid, form ve uzun teknik başlıklarda min-width, satır kırma ve dokunma hedefi sözleşmesi tüm ortak stillerde korunmalı. Hata gizlemek için body overflow-x:hidden kullanılmamalı.

### P2 — Uzun sayfalarda tarama maliyeti
Alt bölümlerdeki kart ve makale grupları ilk ekranda render edilmek zorunda değil. content-visibility ve güvenli intrinsic size kullanımı, özellikle düşük seviye mobil cihazlarda kaydırma ve ilk etkileşim maliyetini azaltabilir.

### P2 — Ticari ve kamu yararı rotalarının ayrımı
Affiliate, ücretli hizmet ve sponsorlu iş birliği etiketleri görünür kalmalı; teknik güvenlik veya resmî yönlendirme akışından önce ticari CTA gösterilmemeli.

### P2 — İçerik mimarisi
Benzer rehberlerin çoğalması halinde kullanıcının aynı konuda farklı sayfalara dağılması önlenmeli. Her niyet için bir ana sayfa, destekleyici sayfalar için açık breadcrumb ve geri dönüş rotası kullanılmalı.

## Uygulanan aksiyon

- Grid çocuklarında min-width:0.
- Başlıklarda dengeli satır kırma.
- Metin bloklarında 72ch okunabilirlik sınırı.
- Etkileşimli öğelerde en az 44px dokunma yüksekliği.
- Form kontrollerinde taşma koruması ve kalıtılan yazı tipi.
- Kartlarda content-visibility:auto ve intrinsic render alanı.
- Mobilde uzun başlık/metin satır kırma ve marka kapsayıcı koruması.
- Reduced-motion davranışı korunmuştur.
- body overflow-x:hidden, outline:none veya outline:0 eklenmemiştir.

## Güven sınırı

Yeni iletişim formu, telefon/e-posta/açık adres/abonelik/T.C. kimlik alanı, resmî kurum izlenimi veya doğrulanmamış ticari yönlendirme eklenmemiştir.
