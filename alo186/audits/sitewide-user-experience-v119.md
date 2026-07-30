# ALO186 site geneli kullanıcı deneyimi denetimi v119

Tarih: 31 Temmuz 2026

## Kapsam

Denetim; canonical üretim paketi, custom-domain hedefi ve `/chatgpt` proje-alt-yolu hedefini birlikte kapsar. Canonical artifact üzerinde 403 HTML sayfası, Pages hazırlığında üretilen köprü ve teknik sayfalarla birlikte 456 HTML sayfası incelenmiştir.

İncelenen başlıklar:

- mobil ve masaüstü navigasyon
- sayfa içi içerik mimarisi
- klavye ve ekran okuyucu erişilebilirliği
- form kontrolleri ve dinamik işlem bağlantıları
- tablo taşması
- sabit alt arayüzlerin çakışması
- görsel yükleme ve alt metin güvenliği
- custom-domain ve GitHub Pages proje-alt-yolu bütünlüğü
- kritik rota, canonical, metadata ve H1 kapsamı

## Güçlü yönler

- 403 canonical HTML sayfasının tamamında dil, başlık, viewport, tek H1 ve ana içerik alanı bulunuyor.
- Güvenlik önceliği, 112/186/EDAŞ/elektrikçi ayrımı ve bağımsız platform açıklaması güçlü.
- Kişisel veri istemeyen hesaplayıcılar ve kanıt üretme araçları belirgin bir ürün farklılaşması oluşturuyor.
- Uzun sayfalarda otomatik içerik haritası, mobil hızlı erişim, dış bağlantı güvenliği ve geri-dönüş düğmesi ortak katmana alınmış durumda.
- Kritik rota ve yayın metadata kontrolleri otomatik testlerle korunuyor.

## Tespit edilen sistemik sorunlar

### P0 — yayın bütünlüğü

Ortak UX JavaScript dosyasında doğrudan `/` kök rota sabiti bulunduğu için `/chatgpt` Pages hedefinin smoke testi duruyordu. Son taramada 456 sayfa ve 7.549 referans kontrol edilmiş, tek ortak asset hatası bütün GitHub Pages yayınını engellemişti.

### P1 — sabit mobil arayüz çakışmaları

Bazı gelişmiş araçlar kendi mobil alt menüsünü oluşturuyor. Ortak UX katmanı bunu algılamadığı için ikinci bir alt menü ekleyebiliyor. Çerez ayarları ve sayfa başına dön düğmesi de aynı sağ-alt alanı kullanabiliyordu.

### P1 — tablo klavye davranışı

357 tablonun 353’ünde görünür caption bulunmuyor. Eski ortak katman taşmayan tabloları da klavye sırasına alıyor ve hepsine genel “Kaydırılabilir tablo” adı veriyordu. Bu, gereksiz odak durakları ve bağlam kaybı oluşturuyordu.

### P1 — form ve dinamik bağlantı adları

Statik artifact taramasında sekiz form kontrolü açık label/ARIA adı olmadan, beş dinamik işlem bağlantısı ise ilk yüklemede boş metin ve `href="#"` ile bulundu. İlgili bileşenler çalışırken metin üretse de ilk erişilebilirlik ağacı ve otomatik kalite taraması zayıf kalıyordu.

### P2 — odak görünürlüğü

Ortak içerik haritası ve mobil navigasyonun bazı focus kuralları outline’ı kaldırıyordu. Sayfa bazlı stiller iyi olsa da site çapında tutarlı bir görünür klavye odağı garantisi yoktu.

### P2 — performans ve kritik görseller

İlk görsel dışındaki her görsel koşulsuz lazy işaretleniyordu. Hero veya `fetchpriority=high` olarak tanımlanmış kritik görsellerin korunması gerekiyordu. Scroll dinleyicisi de her olayda doğrudan çalışıyordu.

## Uygulanan aksiyonlar

1. Kök rota sabitleri çalışma anında güvenli biçimde oluşturuldu; ortak asset artık custom-domain ve proje-alt-yolunda aynı kodla çalışıyor.
2. Sitewide test, her iki hedefte gerçek `smoke_github_pages.py` kontrolünü çalıştıracak şekilde güçlendirildi.
3. Sayfanın kendi `.mobile-dock` bileşeni varsa ortak mobil menü eklenmiyor.
4. Çerez ayarları mobil alt menünün üstüne taşındı; görünür olduğunda başa-dön düğmesi karşı köşeye geçiyor.
5. Tablolar yalnız gerçekten yatay taştığında klavye odağı ve region rolü alıyor; erişilebilir ad caption, `aria-labelledby` veya yakın bölüm başlığından türetiliyor.
6. Açık label taşımayan form kontrollerine fieldset legend, bileşen başlığı veya güvenli alan kimliğinden çalışma anında erişilebilir ad atanıyor.
7. Boş dinamik işlem bağlantıları hedef ve metin oluşana kadar odak sırasından çıkarılıyor; güvenli bir geçici ad veriliyor ve içerik geldiğinde doğal ada dönüyor.
8. Tüm bağlantı, düğme, form alanı ve odaklanabilir bileşenler için görünür sarı focus halkası sağlandı.
9. Hero, eager veya yüksek öncelikli görseller lazy dönüşümünden hariç tutuldu.
10. Başa-dön görünürlüğü `requestAnimationFrame` ile sınırlandırıldı ve gizliyken klavye sırasından çıkarıldı.
11. Uzun sayfa içerik haritasında anchor kimliği çakışmalarına karşı benzersiz kimlik üretimi eklendi.

## Kabul kriterleri

- JavaScript sözdizimi geçerli.
- UX assetında proje-alt-yolu dışında çözümlenmemiş kök rota yok.
- Custom-domain ve `/chatgpt` hedeflerinin ikisi de GitHub Pages smoke testinden geçiyor.
- 456 final HTML sayfasının tamamında ortak UX CSS ve JS işaretçileri bulunuyor.
- Kritik kullanıcı rotaları fiziksel olarak mevcut ve H1 taşıyor.
- H1 kapsama oranı en az `%97`.
- Taşmayan tablolar klavye tab sırasına alınmıyor.
- CSS içinde `outline: 0` veya `outline: none` ile focus bastırılmıyor.
- İngilizce ve noindex sayfalarda Türkçe mobil hızlı erişim gösterilmiyor.
- Mevcut özel mobil dock bulunan sayfalarda ikinci dock üretilmiyor.

## Sonraki ölçüm

GA4 tarafında aşağıdaki olaylar sayfa grubu ve cihaz sınıfıyla izlenmelidir: `decision_engine_open`, `edas_finder_open`, `calculator_open`, `affiliate_click`, `outbound_click` ve `call_186_click`. UX kararları yalnız sayfa görüntülenmesine değil; doğru rotaya ulaşma, araç tamamlama, hatalı tıklama ve geri dönüş oranına göre değerlendirilecektir.
