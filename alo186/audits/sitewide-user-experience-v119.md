# ALO186 site geneli kullanıcı deneyimi denetimi v120

Tarih: 31 Temmuz 2026

## Kapsam

Denetim; canonical üretim paketi, custom-domain hedefi ve `/chatgpt` proje-alt-yolu hedefini birlikte kapsar. Canonical artifact üzerinde 403 HTML sayfası, Pages hazırlığında üretilen köprü ve teknik sayfalarla birlikte 456+ HTML sayfası incelenmiştir.

İncelenen başlıklar:

- mobil ve masaüstü navigasyon
- Türkçe ve İngilizce görev tamamlama eşitliği
- sayfa içi içerik mimarisi ve sayfa sonu devam rotası
- klavye ve ekran okuyucu erişilebilirliği
- form kontrolleri ve dinamik işlem bağlantıları
- tablo taşması
- sabit alt arayüzlerin çakışması
- görsel yükleme ve alt metin güvenliği
- affiliate bağlantısı şeffaflığı
- custom-domain ve GitHub Pages proje-alt-yolu bütünlüğü
- kritik rota, canonical, metadata ve H1 kapsamı

## Güçlü yönler

- Canonical sayfaların tamamında dil, başlık, viewport, tek H1 ve ana içerik alanı bulunuyor.
- Güvenlik önceliği, 112/186/187/EDAŞ/elektrikçi ayrımı ve bağımsız platform açıklaması güçlü.
- Kişisel veri istemeyen hesaplayıcılar ve kanıt üretme araçları belirgin bir ürün farklılaşması oluşturuyor.
- Uzun sayfalarda otomatik içerik haritası, mobil hızlı erişim, dış bağlantı güvenliği ve geri-dönüş düğmesi ortak katmana alınmış durumda.
- Kritik rota ve yayın metadata kontrolleri otomatik testlerle korunuyor.
- Kullanıcıya görünmemesi gereken iç ticari jargon portal girişinden temizlenmiş; ücretsiz kaynaklar ticari seçeneklerden önce gösteriliyor.

## Tespit edilen sistemik sorunlar

### P0 — yayın bütünlüğü

Ortak UX JavaScript dosyasında doğrudan kök rota sabiti bulunduğu için `/chatgpt` Pages hedefinin smoke testi daha önce duruyordu. Son taramada 456 sayfa ve binlerce referans kontrol edilmiş, tek ortak asset hatasının bütün GitHub Pages yayınını engelleyebildiği görülmüştü.

### P1 — sayfa sonu çıkmazları

Kullanıcı bir hesaplayıcıyı, mevzuat kaydını, teknik rehberi veya ürün karşılaştırmasını tamamladıktan sonra yeniden üst menüyü taramak zorunda kalıyordu. Aynı aramayı baştan başlatmak yerine sayfanın bağlamına göre sonuç takibi, resmî kaynak, teknik arama veya uygunluk aracına ilerlemelidir.

### P1 — İngilizce mobil yolculuk eksikliği

Türkçe mobil hızlı erişim güçlüydü; ancak İngilizce sayfalarda ikinci bir Türkçe dock oluşturmamak için ortak mobil menü tamamen kapatılmıştı. Bu durum İngilizce kullanıcının dağıtım şirketi bulucu, kesinti ve acil numara rotalarına erişimini gereksiz yere zorlaştırıyordu.

### P1 — dinamik affiliate bağlantılarında şeffaflık

Kaynak HTML'deki çoğu Amazon bağlantısı doğru `rel` değerlerini taşısa da, kullanıcı etkileşimi sonrasında JavaScript tarafından oluşturulan bağlantılar için site-geneli bir güvenlik ve görünür etiket katmanı yoktu. Ticari ilişkinin CTA metninde görünmediği durumda kullanıcı bunun satış ortaklığı bağlantısı olduğunu ayrıca görebilmelidir.

### P1 — sabit mobil arayüz çakışmaları

Bazı gelişmiş araçlar kendi mobil alt menüsünü oluşturuyor. Ortak UX katmanı bunu algılamadığı durumda ikinci bir alt menü oluşabiliyordu. Çerez ayarları ve sayfa başına dön düğmesi de aynı sağ-alt alanı kullanabiliyordu.

Gerçek 390 × 844 px Chromium renderında iki ilave mobil regresyon belirlendi: teknik arama sayfasında ikinci bir atlama bağlantısı oluşuyor; kesinti kiti dönemsel kontrolündeki uzun `select` metni belgeyi 390 px yerine 440 px genişliğe taşıyordu. İlk ziyaret analitik tercih penceresi de sabit alt menü ve içerik haritasıyla aynı ekran alanını paylaşabiliyordu.

### P1 — tablo klavye davranışı

Tabloların çoğunda görünür caption bulunmuyor. Eski ortak katman taşmayan tabloları da klavye sırasına alıyor ve genel bir ad veriyordu. Bu, gereksiz odak durakları ve bağlam kaybı oluşturuyordu.

### P1 — form ve dinamik bağlantı adları

Bazı form kontrolleri açık label/ARIA adı olmadan, bazı dinamik işlem bağlantıları ise ilk yüklemede boş metin ve `href="#"` ile bulunuyordu. İlgili bileşenler çalışırken metin üretse de ilk erişilebilirlik ağacı zayıf kalıyordu.

### P2 — odak görünürlüğü ve yüksek karşıtlık

Ortak içerik haritası ve mobil navigasyonun bazı eski focus kuralları outline'ı kaldırıyordu. Windows High Contrast, `forced-colors` ve artırılmış kontrast tercihlerinde aktif rota ve odak durumunun sistem renkleriyle görünür kalması gerekiyor.

### P2 — performans ve kritik görseller

İlk görsel dışındaki her görselin koşulsuz lazy işaretlenmesi hero veya `fetchpriority=high` görsellerini geciktirebiliyordu. Scroll dinleyicisinin de her olayda doğrudan çalışması gereksiz maliyet oluşturuyordu.

## Uygulanan aksiyonlar

1. Kök rota sabitleri çalışma anında güvenli biçimde oluşturuldu; ortak asset custom-domain ve proje-alt-yolunda aynı kodla çalışıyor.
2. Site-geneli test, her iki hedefte gerçek `smoke_github_pages.py` kontrolünü çalıştırıyor.
3. Sayfanın kendi `.mobile-dock` bileşeni varsa ortak mobil menü eklenmiyor.
4. Türkçe sayfalarda Ana sayfa / EDAŞ bul / Arama / Acil; İngilizce sayfalarda Home / Distributor / Outage / Emergency hızlı erişimi gösteriliyor.
5. Çerez ayarları mobil alt menünün üstüne taşındı; görünür olduğunda başa-dön düğmesi karşı köşeye geçiyor.
6. Tablolar yalnız gerçekten yatay taştığında klavye odağı ve region rolü alıyor; erişilebilir ad yakın bağlamdan türetiliyor.
7. Açık label taşımayan form kontrollerine güvenli çalışma anı etiketi atanıyor.
8. Boş dinamik işlem bağlantıları hedef ve metin oluşana kadar odak sırasından çıkarılıyor.
9. Tüm odaklanabilir bileşenler için görünür focus halkası, `forced-colors` ve yüksek kontrast davranışı korunuyor.
10. Hero, eager veya yüksek öncelikli görseller lazy dönüşümünden hariç tutuluyor.
11. Başa-dön görünürlüğü `requestAnimationFrame` ile sınırlandırılıyor ve gizliyken klavye sırasından çıkarılıyor.
12. Uzun sayfa içerik haritasında anchor kimliği çakışmalarına karşı benzersiz kimlik üretiliyor; gizli sonuç bölümleri içerik haritasına alınmıyor.
13. Hesaplayıcı, ürün, makale, mevzuat, kesinti, yasal ve İngilizce sayfalara bağlama göre üç güvenli “Sonraki doğru adım” rotası ekleniyor.
14. CPAP/BiPAP, gaz ve yangın gibi hassas araçların devam rotalarında ürün seçimi yerine acil numaralar, kesinti planı ve teknik merkez gösteriliyor.
15. İlk yüklemede ve MutationObserver ile sonradan eklenen Amazon bağlantıları `sponsored nofollow noopener` alıyor.
16. CTA metni ticari ilişkiyi açıkça söylemiyorsa görünür `Satış ortaklığı / Affiliate` rozeti ekleniyor.
17. Ortak katman mevcut `.skip-link`, `.skip` veya benzer sayfa içi atlama bağlantısını algılıyor; ikinci bağlantı üretmiyor.
18. `.item`, `.field`, `.form-row`, `.control` ve `.input-group` içindeki uzun form kontrolleri `min-width:0`, `max-width:100%` ve doğrudan `select` için `width:100%` kurallarıyla mobil viewport içine alınıyor.
19. İlk ziyaret analitik tercih penceresi sabit bir örtü olmaktan çıkarılıp başlık ile ana içerik arasındaki normal belge akışına taşınıyor.
20. Analitik tercihi verilene kadar ortak ve sayfaya özel mobil dock'lar gizleniyor; seçimden sonra hızlı erişim kendiliğinden geri açılıyor.

## Kabul kriterleri

- JavaScript sözdizimi geçerli.
- UX assetında proje-alt-yolu dışında çözümlenmemiş kök rota yok.
- Custom-domain ve `/chatgpt` hedeflerinin ikisi de GitHub Pages smoke testinden geçiyor.
- Final HTML sayfalarının tamamında ortak UX CSS ve JS işaretçileri bulunuyor.
- Kritik Türkçe ve İngilizce kullanıcı rotaları fiziksel olarak mevcut ve H1 taşıyor.
- H1 kapsama oranı en az `%97`.
- Taşmayan tablolar klavye tab sırasına alınmıyor.
- CSS içinde `outline: 0` veya `outline: none` ile focus bastırılmıyor.
- İngilizce sayfalarda İngilizce mobil hızlı erişim gösteriliyor.
- `noindex` teknik köprülerde ortak mobil bar ve bağlamsal ticari devam oluşturulmuyor.
- Mevcut özel mobil dock bulunan sayfalarda ikinci dock üretilmiyor.
- Mevcut sayfa içi atlama bağlantısı bulunan sayfalarda ortak ikinci atlama bağlantısı üretilmiyor.
- Uzun seçenek metni taşıyan dar grid/form bileşenleri mobil viewport genişliğini aşmıyor.
- İlk analitik tercih ekranı sayfa içeriğinin veya mobil hızlı erişim bağlantılarının üstüne gelmiyor.
- Dinamik Amazon bağlantıları satış ortaklığı ve dış bağlantı güven sözleşmesine otomatik alınıyor.
- Sağlık, gaz ve yangın bağlamında ürün rotası öne çıkarılmıyor.

## Sonraki ölçüm

GA4 tarafında aşağıdaki olaylar sayfa grubu, dil ve cihaz sınıfıyla izlenmelidir: `decision_engine_open`, `edas_finder_open`, `calculator_open`, `affiliate_click`, `outbound_click`, `call_186_click`, `contextual_next_step_click` ve `language_route_click`. UX kararları yalnız sayfa görüntülenmesine değil; doğru rotaya ulaşma, araç tamamlama, hatalı tıklama, sayfa sonu çıkış ve geri dönüş oranına göre değerlendirilmelidir.
