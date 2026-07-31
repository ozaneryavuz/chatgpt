# ALO186 yayın ve editoryal şeffaflık denetimi v150

**Doğrulama tarihi:** 31 Temmuz 2026  
**Kapsam:** Canlı yayın kimliği, rota bütünlüğü, makale yayın yöntemi, düzeltme kanalı ve dağıtım sonrası gözlemlenebilirlik.

## Öncelikli sorun

ALO186 içerik ve araç sayısı hızla büyürken kullanıcı şu üç soruya tek yerden cevap alamıyordu:

1. Canlı site hangi kaynak commitinden ve routing sürümünden üretildi?
2. Bir teknik makale hangi ortak yayın, kaynak ve düzeltme yöntemiyle sunuluyor?
3. GitHub Pages dağıtımı tamamlandıktan sonra kritik rotaların canlı alan adında gerçekten açıldığı nasıl kanıtlanıyor?

Tek tek sayfa eklemek yerine bu çalışmada bütün mevcut ve gelecekteki içeriklere uygulanan bir güven katmanı seçildi.

## Uygulanan çözüm

### 1. Yayın durumu sayfası

Yeni canonical rota:

`/yayin-durumu/`

Sayfa üretim sırasında otomatik olarak şu alanlarla doldurulur:

- kaynak commit,
- routing sürümü,
- canonical rota sayısı,
- teknik makale sayısı,
- cihaz hasarı başvuru süresi,
- paket oluşturma zamanı,
- kritik kullanıcı yollarının fiziksel varlığı,
- makine tarafından okunabilir `/release-status.json`,
- kaynak commit, yayın ilkeleri, kaynak yaklaşımı ve düzeltme kanalı.

Kayıt, resmî EDAŞ veya mevzuat doğrulaması gibi sunulmaz. Yalnız ALO186 yayın artifactının teknik kimliğini ve bütünlüğünü gösterir.

### 2. Bütün teknik makalelerde ortak güven bloğu

Routing manifestinde `article` türündeki bütün sayfalara otomatik olarak:

- birincil kaynak önceliği,
- son doğrulama tarihinin önemi,
- can güvenliği ve satın almama sınırı,
- saha ölçümü ve resmî karar yerine geçmeme açıklaması,
- yayın ilkeleri,
- kaynak yaklaşımı,
- yayın durumu,
- hata/düzeltme kanalı

bağlantıları eklenir.

Adı veya yeterliliği doğrulanmamış bir kişi “uzman” ya da “teknik hakem” olarak gösterilmez. Güven, görünür yöntem ve doğrulanabilir kaynak üzerinden kurulur.

### 3. Canlı dağıtım smoke kontrolü

GitHub Pages ana-dal dağıtımı başarıyla tamamlandığında yalnız herkese açık uç noktaları kullanan bir workflow:

- `/release-status.json`,
- `/yayin-durumu/`,
- ana sayfa,
- Elektrik Portalı,
- EDAŞ Bulucu,
- Elektrik Durum Merkezi,
- Teknik Makaleler,
- Hesaplama Merkezi

rotalarını kontrol eder.

Ayrıca canlı kayıtta:

- `status=ready`,
- canonical host,
- 30 günlük cihaz hasarı süresi,
- beklenen commit,
- bütün kritik rotaların HTTP 200 ve H1 sonucu

aranır. Sonuç JSON artifact olarak 45 gün saklanır. Workflow issue yazmaz, gizli anahtar istemez ve canlı sitede değişiklik yapmaz.

## AEO ve SEO katkısı

- Yayın durumu `WebPage`, `Dataset`, `FAQPage`, `BreadcrumbList` ve `DefinedTerm` ilişkileri taşır.
- Makale güven blokları kullanıcıya görünür ve her makaleden yayın yöntemi/düzeltme rotasına semantik bağlantı kurar.
- Yeni rota sitemap ve PWA shortcut zincirine girer.
- Routing sürümü 150’ye yükselir.
- Teknik yöntem, sürüm ve düzeltme izi arama motoru ile yapay zekâ yanıt sistemleri için açık hâle gelir.

## Güven sınırları

- Kişisel veri veya tarayıcı depolaması eklenmez.
- Resmî kurum, EDAŞ, test kuruluşu veya ürün satıcısı izlenimi oluşturulmaz.
- Fiyat, stok, puan, garanti, Product veya Offer şeması eklenmez.
- Cihaz hasarı başvuru süresi 30 gün olarak korunur.
- Canlı smoke kontrolü dış kurum verisinin güncelliğini değil, ALO186 artifactının yayınlandığını doğrular.
