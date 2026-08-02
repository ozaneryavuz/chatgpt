# ALO186 affiliate measurement v211 — uygulama makbuzu

**Tarih:** 2 Ağustos 2026  
**Bağlı büyüme programı:** #672  
**Kapsam:** görev 01, 02, 03, 04, 09, 10, 11 ve 40

## Problem

ALO186 içinde ana sayfa vitrini, görev bazlı ürün seçiciler, teknik uygunluk kapıları ve Amazon satış ortaklığı açıklamaları bulunuyor. Ancak farklı sayfalarda oluşan doğrudan mağaza tıklamalarını aynı veri sözleşmesiyle ölçen; link türünü, içerik kümesini ve yerleşimi kişisel veri toplamadan ayıran merkezi bir katman yoktu.

Bu eksiklik şu soruların güvenilir biçimde yanıtlanmasını zorlaştırıyordu:

- Hangi karar sayfası nitelikli Amazon tıklaması üretiyor?
- Belirli ürün bağlantısı mı, dar arama bağlantısı mı daha verimli?
- Karşılaştırma tablosu, sonuç kartı veya içerik içi CTA’dan hangisi çalışıyor?
- Hangi sayfada affiliate link politikası veya `rel` niteliği eksik?
- Üretim artifactında kaç statik affiliate bağlantısı bulunuyor?

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

### 3. Link politika normalizasyonu

Final üretim HTML’sinde bulunan Amazon bağlantılarına eksikse şu nitelikler eklenir:

```html
rel="sponsored nofollow noopener"
```

Ayrıca düşük riskli makine okunur alanlar eklenir:

- ağ
- içerik kümesi
- CTA yerleşimi
- link türü
- anonim ürün anahtarı
- ölçüm sürümü

Amazon dışındaki `target="_blank"` harici bağlantılarda `noopener` zorunlu hâle getirilir. Script ve stil bloklarının içindeki HTML şablonları değiştirilmez.

### 4. Gizlilik korumalı üretim envanteri

Her artifactta aşağıdaki rapor oluşturulur:

```text
/affiliate-measurement-v211.json
```

Rapor; taranan ve enstrümante edilen sayfa sayısını, statik affiliate bağlantı sayısını, doğrudan ürün/arama/kısa link dağılımını, yerleşim türlerini ve anonim ürün anahtarlarını içerir. Ham Amazon URL’si veya satış ortaklığı etiketi rapora yazılmaz.

### 5. Yayın makbuzu ve bütünlük

`pages-release.json` içine `affiliateMeasurement` sürüm makbuzu eklenir. Asset, envanter ve değiştirilen HTML dosyaları `checksums.sha256` manifestine yeniden işlenir.

## Güven ve ticari sınırlar

- Yeni Amazon ürünü veya doğrudan mağaza URL’si eklenmedi.
- Ürün sıralaması, fiyat, stok, puan, yorum, satıcı, teslimat veya garanti verisi değiştirilmedi.
- `Product`, `Offer` veya `AggregateRating` şeması eklenmedi.
- Teknik uygunluk, satın almama sonucu ve profesyonel kategori kapıları korunur.
- Can güvenliği ve resmî yönlendirme sırası değiştirilmez.
- Script/style içindeki runtime şablonları sunucu tarafında yeniden yazılmaz.

## Test kapsamı

- Python sözdizimi
- Node.js JavaScript sözdizimi
- Custom-domain yolu
- `/chatgpt` proje yolu
- İdempotent ikinci çalıştırma
- Statik Amazon ürün ve arama linki sınıflandırması
- `rel="sponsored nofollow noopener"` sözleşmesi
- Harici `_blank` bağlantı güvenliği
- Dahili bağlantının affiliate olarak yanlış sınıflandırılmaması
- Script içi HTML şablonunun değiştirilmemesi
- Envanterde ham URL/affiliate etiketi bulunmaması
- `pages-release.json` ve checksum bütünlüğü
- Tam site build, Pages smoke ve commerce guard
- v209 ana sayfa vitrini ile v210 ihtiyaç yönlendiricisinin aynı artifactta korunması

## İlk başarı ölçütleri

- Enstrümante HTML sayfası / taranan HTML sayfası: **%100**
- Statik affiliate link politika kapsaması: **%100**
- Ham hedef URL veya kişisel kimlik gönderimi: **0**
- Envanter ile statik HTML link sayımı farkı: **0**
- Acil/güvenlik rotasında yeni ticari yol: **0**
