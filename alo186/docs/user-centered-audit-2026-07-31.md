# ALO186 kullanıcı odaklı site denetimi — 31 Temmuz 2026

## Kapsam

Canlı ana giriş, EDAŞ/kesinti karar akışı, elektrik portalı, hesaplayıcılar, ürün seçim rotası, sektör rehberleri, mevzuat, İngilizce çekirdek, kurumsal hizmet ve yasal/güven sayfaları; ayrıca canonical üretimden sonra oluşan custom-domain ve `/chatgpt` paketlerindeki bütün HTML sayfaları.

V118b kalite kabulünde iki yayın hedefinin her birinde 456 HTML sayfası incelenmiş, ortak UX katmanı bütün sayfalara uygulanmış ve H1 kapsamı yüzde 100 doğrulanmıştır.

## Öncelikli bulgular

### P1 — Ana girişte karar yoğunluğu

Ana sayfa güçlü ve güvenilir içerik taşıyor; ancak kesinti, güvenlik, ürün, teknik makale ve kurumsal hizmet rotaları aynı anda görünür olduğunda ilk kez gelen kullanıcı için seçenek yükü artıyor. Birincil başlangıç Elektrik Durum Merkezi olmalı; diğer rotalar ikincil keşif olarak kalmalı.

### P1 — Sayfa sonlarında devam yolu eksikliği

Bir hesap, rehber, mevzuat veya ürün sayfasını tamamlayan kullanıcı yeniden menü taramak zorunda kalıyor. Sayfanın türüne göre sonuç takibi, resmî kaynak, teknik arama, ürün uygunluğu veya güvenli sonraki adım görünür olmalı.

### P1 — İngilizce mobil yolculuk eksikliği

Project-path sorunu giderilmiş olsa da İngilizce sayfalarda mobil hızlı erişim tamamen kapalı kalıyordu. İngilizce kullanıcıların dağıtım şirketi bulucu, kesinti ve acil numara rotalarına aynı erişilebilirlikle ulaşması gerekir.

### P2 — Mobil okunabilirlik ve taşma dayanıklılığı

Kart, grid, form ve uzun teknik başlıklarda min-width, satır kırma ve dokunma hedefi sözleşmesi tüm ortak stillerde korunmalı. Hata gizlemek için `body overflow-x:hidden` kullanılmamalı.

### P2 — Uzun sayfalarda tarama maliyeti

Uzun teknik içeriklerde erişilebilir içerik haritası korunmalı; düşük seviye mobil cihazlarda alt bölüm render maliyeti `content-visibility` ve güvenli intrinsic size ile azaltılmalı.

### P2 — Ticari şeffaflığın dinamik bağlantılarda korunması

Kaynak HTML'de doğru etiketlenen affiliate bağlantılarına ek olarak, kullanıcı etkileşimi sonrasında oluşturulan Amazon bağlantıları da `sponsored nofollow noopener` sözleşmesine alınmalı ve genel CTA metinlerinde görünür satış ortaklığı etiketi bulunmalıdır.

## Uygulanan site geneli aksiyonlar

### Ortak kalite tabanı

- 44 px dokunma hedefi, taşma dayanıklılığı ve mobil satır kırma.
- Klavye erişilebilir yatay tablo kapsayıcısı.
- Görsel taşma koruması, lazy loading, async decoding ve eksik alt metin fallback'i.
- Atla bağlantısı, aktif rota işareti ve erişilebilir başa dön düğmesi.
- Uzun içeriklerde Türkçe/İngilizce sayfa içi içerik haritası.
- `prefers-reduced-motion`, safe-area ve yazdırma davranışı.

### V119 kullanıcı yolculuğu katmanı

- Türkçe ve İngilizce mobil hızlı erişim, custom-domain ve `/chatgpt` taban yoluna göre üretilir.
- İngilizce menü yalnız İngilizce ana sayfa, dağıtım şirketi bulucu, kesinti ve acil numara rotalarını kullanır.
- Hesaplayıcı, ürün, makale, mevzuat, kesinti ve yasal sayfalara bağlama göre üç güvenli devam rotası eklenir.
- Dinamik Amazon bağlantıları MutationObserver ile de yakalanır; affiliate ve dış bağlantı güven etiketleri otomatik uygulanır.
- Genel Amazon CTA'sı gerekli olduğunda görünür `Satış ortaklığı / Affiliate` rozeti alır.
- Eksik veya yanlış `lang` ile referrer metadata alanları yayın katmanında düzeltilir.
- `noindex` teknik köprülerde mobil navigasyon ve devam modülü oluşturulmaz.
- Bütün yayın sayfalarında title, canonical, viewport, dil, referrer, H1, main, görsel alt metni, form etiketi ve affiliate rel kapsamı ölçülür.

## Kullanıcı ve gelir etkisi

```text
bulunabilirlik
→ okunabilirlik
→ doğru devam rotası
→ güvenli teknik doğrulama
→ şeffaf ticari ilişki
→ tekrar ziyaret
```

Kullanıcı aynı araştırmaya baştan başlamaz; tamamladığı sayfanın bağlamına uygun araca, resmî kaynağa veya sonuç takibine geçer. Affiliate dönüşümü daha görünür ve güvenli hâle gelir; ancak tehlike, resmî işlem veya mevcut ürünün yeterli olduğu durumda ticari yol açılmaz.

## Güven sınırı

Yeni iletişim formu, telefon/e-posta/açık adres/abonelik/T.C. kimlik alanı, konum erişimi, tarayıcı depolaması, resmî kurum izlenimi veya doğrulanmamış fiyat, stok, puan ve garanti iddiası eklenmemiştir.
