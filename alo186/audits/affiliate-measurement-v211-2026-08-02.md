# ALO186 affiliate measurement v211 — uygulama makbuzu

**Tarih:** 2 Ağustos 2026  
**Bağlı büyüme programı:** #672  
**Kapsam:** görev 01, 02, 03, 04, 09, 10, 11 ve 40

## Problem

ALO186 içinde ana sayfa vitrini, görev bazlı ürün seçiciler, teknik uygunluk kapıları ve Amazon satış ortaklığı açıklamaları bulunuyor. Ancak farklı sayfalarda oluşan doğrudan mağaza tıklamalarını aynı veri sözleşmesiyle ölçen; link türünü, içerik kümesini ve yerleşimi kişisel veri toplamadan ayıran merkezi bir katman yoktu.

Ayrıca sonradan eklenen affiliate paketlerinin ayrı Pages yayıncıları oluşturması, aynı canlı ortam için yarışan artifactlar üretme ve daha yeni bir paketin sonraki sıradan yayında kaybolması riskini doğurabilirdi.

Bu eksiklikler şu soruların güvenilir biçimde yanıtlanmasını zorlaştırıyordu:

- Hangi karar sayfası nitelikli Amazon tıklaması üretiyor?
- Belirli ürün bağlantısı mı, dar arama bağlantısı mı daha verimli?
- Karşılaştırma tablosu, sonuç kartı veya içerik içi CTA’dan hangisi çalışıyor?
- Hangi sayfada affiliate link politikası veya `rel` niteliği eksik?
- Üretim artifactında kaç statik affiliate bağlantısı bulunuyor?
- Canlı sitede v209, v210 ve v211 aynı sürümde kalıcı olarak bulunuyor mu?

## Uygulanan çözüm

### 1. Merkezi ve açık rızaya bağlı ölçüm

Bütün HTML sayfalarına tek bir harici runtime asseti eklenir:

```text
/assets/affiliate-measurement-v211.js
```

Asset yalnız ALO186 analitik tercihi `granted` olduğunda ve GA4 yükleyicisi etkinleştiğinde olay gönderir. Rıza yoksa Google ağına affiliate ölçüm olayı gönderilmez.

Standart olaylar:

- `affiliate_page_view`
- `affiliate_click`

`affiliate_click` alanları:

- `affiliate_network`
- `page_path`
- `content_cluster`
- `link_placement`
- `link_type`
- `product_key`
- `measurement_version`

Ham hedef URL, Amazon arama sorgusu, ASIN, e-posta, telefon, açık adres, kullanıcı veya cihaz kimliği analitik olayına eklenmez. `product_key`, yalnız bağlantıyı raporlarda tekilleştiren, ham hedefi içermeyen kısa özet anahtarıdır.

### 2. Mevcut GA4 affiliate olayında çift sayımı önleme

GA4 açık rıza katmanındaki genel `affiliate_click` olayı korunur. v211 runtime, ayrıntılı olay gönderdiğinde aynı tıklama için oluşabilecek genel olayı yalnız o event döngüsünde bastırır. Normal dış bağlantı, 186, EDAŞ, hesaplayıcı ve diğer analitik olaylarına dokunmaz.

GA4 katmanı çalışma anında daha sonra oluşsa bile `installGtagGuard()` gönderimden hemen önce korumayı yeniden bağlar. Böylece script yükleme sırası veya kullanıcının sonradan onay vermesi çift sayım üretmez.

### 3. Link politika normalizasyonu

Final üretim HTML’sinde bulunan Amazon bağlantılarına eksikse şu nitelikler eklenir:

```html
rel="sponsored nofollow noopener"
```

Ayrıca düşük riskli makine okunur alanlar eklenir:

- ağ
- içerik kümesi
- link türü
- anonim ürün anahtarı
- ölçüm sürümü

CTA yerleşimi anchor üzerinde açıkça tanımlıysa veya anchor sınıfından güvenilir biçimde çıkarılabiliyorsa statik olarak yazılır. Link bir `<article class="card">`, tablo veya sonuç kapsayıcısının içindeyse fakat anchor’ın kendisi bunu belirtmiyorsa yanlışlıkla `content` değeri yazılmaz; çalışma anında en yakın gerçek üst kapsayıcıdan `card`, `comparison` veya `result` belirlenir.

Amazon dışındaki `target="_blank"` harici bağlantılarda `noopener` zorunlu hâle getirilir. Script ve stil bloklarının içindeki HTML şablonları değiştirilmez.

### 4. Keyfî Pages alt-yolu desteği

Runtime yalnız `/chatgpt` adına bağlı değildir. Enjektöre verilen normalize edilmiş `--base-path` asset içine gömülür ve tarayıcı tarafında segment bazında kaldırılır.

Aşağıdaki modlar test kapsamındadır:

- apex/custom domain: boş base path
- standart proje yolu: `/chatgpt`
- keyfî iç içe yol: `/preview/alo186`

Bu sayede `content_cluster`, depo adı yerine gerçek içerik kümesini raporlar.

### 5. Gizlilik korumalı üretim envanteri

Her artifactta aşağıdaki rapor oluşturulur:

```text
/affiliate-measurement-v211.json
```

Rapor; taranan ve enstrümante edilen sayfa sayısını, statik affiliate bağlantı sayısını, doğrudan ürün/arama/kısa link dağılımını, yerleşim türlerini ve anonim ürün anahtarlarını içerir. Ham Amazon URL’si veya satış ortaklığı etiketi rapora yazılmaz.

Üst kapsayıcıdan çalışma anında çözülecek bağlantılar envanterde `runtime_ancestor` olarak işaretlenir; böylece bilinmeyen yerleşim yanlış bir kesin değerle doldurulmaz.

### 6. Tek yetkili canlı yayıncı

v211’e özel workflow yalnız doğrulama yapar:

- `permissions: contents: read`
- Pages yazma yetkisi yoktur
- Pages artifactı yüklemez
- `deploy-pages` çalıştırmaz

v209 ana sayfa vitrini, v210 ihtiyaç yönlendiricisi, GA4 açık rıza katmanı ve v211 ölçüm/enventer katmanı tek yetkili `.github/workflows/alo186-github-pages.yml` artifactına bağlanmıştır.

Canonical yayın akışı hem custom-domain hem `/chatgpt` modunda şu zinciri doğrular:

```text
canonical build
→ Pages hazırlığı
→ sonuç runtime
→ bağlamsal affiliate
→ canlı kalite
→ ana sayfa v209
→ ihtiyaç yönlendiricisi v210
→ GA4 açık rıza
→ ölçüm ve link envanteri v211
→ Node sözdizimi
→ Pages smoke
→ commerce guard
```

Canlı dağıtımdan sonra `pages-release.json`, v211 envanteri ve JavaScript asseti apex origin üzerinden tekrar okunur. Sürüm, olay sözleşmesi ve gizlilik bayrakları doğrulanmadan yayın başarılı sayılmaz.

### 7. Yayın makbuzu ve bütünlük

`pages-release.json` içine `affiliateMeasurement` sürüm makbuzu eklenir. Asset, envanter ve değiştirilen HTML dosyaları `checksums.sha256` manifestine yeniden işlenir.

## Güven ve ticari sınırlar

- Yeni Amazon ürünü veya doğrudan mağaza URL’si eklenmedi.
- Ürün sıralaması, fiyat, stok, puan, yorum, satıcı, teslimat veya garanti verisi değiştirilmedi.
- `Product`, `Offer` veya `AggregateRating` şeması eklenmedi.
- Teknik uygunluk, satın almama sonucu ve profesyonel kategori kapıları korunur.
- Can güvenliği ve resmî yönlendirme sırası değiştirilmez.
- Script/style içindeki runtime şablonları sunucu tarafında yeniden yazılmaz.
- Ayrı ve yarışan yeni bir canlı Pages yayıncısı oluşturulmaz.

## Test kapsamı

- Python sözdizimi
- Node.js JavaScript sözdizimi
- Custom-domain yolu
- `/chatgpt` proje yolu
- Keyfî `/preview/alo186` alt-yolu
- İdempotent ikinci çalıştırma
- Statik Amazon ürün ve arama linki sınıflandırması
- Anchor sınıfından kesin yerleşim çıkarımı
- Kart üst-kapsayıcısında `runtime_ancestor` ve tarayıcı tarafı çözümleme
- `rel="sponsored nofollow noopener"` sözleşmesi
- Harici `_blank` bağlantı güvenliği
- Dahili bağlantının affiliate olarak yanlış sınıflandırılmaması
- Script içi HTML şablonunun değiştirilmemesi
- Envanterde ham URL/affiliate etiketi bulunmaması
- `pages-release.json` ve checksum bütünlüğü
- Tam site build, Pages smoke ve commerce guard
- v209 ana sayfa vitrini, v210 ihtiyaç yönlendiricisi ve v211 ölçümünün aynı canonical artifactta korunması
- Bağımsız v211 workflow’unda Pages yazma/deploy yetkisinin bulunmaması
- Canlı apex origin üzerinde v211 sürüm, envanter ve asset doğrulaması

## İlk başarı ölçütleri

- Enstrümante HTML sayfası / taranan HTML sayfası: **%100**
- Statik affiliate link politika kapsaması: **%100**
- Ham hedef URL veya kişisel kimlik gönderimi: **0**
- Envanter ile statik HTML link sayımı farkı: **0**
- Acil/güvenlik rotasında yeni ticari yol: **0**
- Yeni v211 bağımsız production publisher sayısı: **0**
- Canonical canlı artifactta v209 + v210 + v211 sürüm sürekliliği: **zorunlu**
