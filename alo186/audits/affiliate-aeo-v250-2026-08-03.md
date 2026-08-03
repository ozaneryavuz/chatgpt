# ALO186 AEO ve affiliate conversion doğrulama raporu v250

**Tarih:** 3 Ağustos 2026  
**Kapsam:** Structured data, deep linking, `llms.txt`, FAQ çözüm bağlantıları, SSR ürün önerileri ve AI crawler erişimi

## Uygulanan teknik katman

### 1. Product, Recommendation, ItemList ve koşullu Offer

Sekiz yüksek niyetli ürün/hesaplama sayfasına görünür HTML ile eşleşen JSON-LD grafiği eklenir:

- `Guide`
- `Product`
- `Recommendation`
- `ItemList`
- ilgili sayfada `FAQPage`

UPS–power station karar sayfasında görünür karşılaştırma tablosu ve aynı satırları temsil eden ayrı `ItemList` bulunur.

`Offer` üreticisi kod seviyesinde aktiftir; ancak yalnız şu alanların tamamı mevcutsa çıktı verir:

- Amazon Türkiye HTTPS merchant URL’si,
- pozitif ve doğrulanmış fiyat,
- `TRY` para birimi,
- Schema.org availability URL’si,
- geçerli `priceValidUntil`,
- en fazla 24 saatlik `verifiedAt`.

Mevcut içerik verisinde bu taze merchant sözleşmesi bulunmadığından üretimde `Offer` sayısı **0**’dır. Sahte fiyat, stok, satıcı, puan veya garanti yayımlanmaz. Böylece Schema.org ürün sınıfları açıklanırken Google merchant/product zengin sonucu için yanıltıcı uygunluk iddiası üretilmez.

### 2. Deep-link kimlikleri

Her görünür teknik çözüm ve SSR kartı benzersiz `id` taşır. Örnekler:

- `rehber-buzdolabi-icin-power-station-secimi`
- `rehber-ups-calisma-suresi-secimi`
- `rehber-ups-mi-power-station-mi`
- `rehber-gerilim-dalgalanmasinda-cihaz-koruma`
- `urun-sinifi-akim-korumali-priz-yuksek-joule`
- `urun-secim-kartlari-ssr`

Kimlik çakışması yayını fail-closed durdurur.

### 3. Kök llms.txt

`/llms.txt` aşağıdaki hiyerarşiyi yayımlar:

1. Resmî ve acil kanallar: 112, 186, EDAŞ,
2. Ev/ofis kesinti hazırlığı: UPS, mini UPS, power station,
3. Cihaz/pano koruması: korumalı priz, gerilim rölesi, SPD,
4. GES ve yedek enerji sistemleri,
5. Yayın politikası, kaynaklar ve affiliate açıklaması.

Bağlantılar yalnız `https://alo186.com` canonical originini kullanır ve mümkün olduğunda doğrudan bölüm kimliğine gider.

### 4. FAQ ve decision-tree çözüm bağlantıları

Gerilim koruma akışında şu iki görünür cevap, güvenlik açıklamasından sonra semantik iç bağlantıyla devam eder:

- “Evde elektrik var ama bazı prizler çalışmıyorsa ne yapılmalı?”
- “Voltaj dalgalanmasında cihazlar nasıl korunur?”

Bağlantı metni: **İlgili Koruma Ekipmanını İnceleyin**.

Aktif tehlike, topraksız/hasarlı priz veya pano müdahalesinde ürün yolu değil yetkili müdahale önceliklidir.

### 5. SSR ürün karşılaştırma katmanı

Dinamik filtre ve hesap sonuçlarından bağımsız olarak temel HTML’de toplam sekiz akış ve 24 teknik öneri kartı yayımlanır. Her kart:

- kimler için,
- uygun değil,
- önce kontrol et,
- ilgili statik teknik rehber

alanlarını taşır. Kartlar doğrudan Amazon bağlantısı içermez ve JavaScript olmadan okunur.

### 6. Robots ve AI crawler erişimi

`robots.txt` içinde aşağıdaki ajanlar için `/`, `/rehber/`, `/urunler/`, `/haberler/`, `/hesaplama/`, `/amazon-elektrik-urunleri/` ve `/akilli-urun-secimi` açıkça izinlidir:

- OAI-SearchBot,
- GPTBot,
- PerplexityBot,
- ClaudeBot,
- Bytespider,
- Google-Extended.

Sitemap apex canonical URL’si korunur.

## Otomatik doğrulama

`validate_affiliate_aeo_v250.py` aşağıdaki kontrolleri uygular:

- JSON-LD sözdizimi,
- gerekli Schema.org tipleri,
- görünür içerik–structured data eşleşmesi,
- Product ve Recommendation sayıları,
- karşılaştırma ItemList’i,
- benzersiz deep-link kimlikleri,
- SSR kartları,
- FAQ çözüm iç linkleri,
- site genelinde `rel="sponsored nofollow noopener"`,
- robots crawler blokları,
- llms.txt hiyerarşisi,
- release makbuzu,
- koşullu Offer güvenlik kapısı,
- custom-domain ve `/chatgpt` base-path uyumu.

## Google Rich Results ve Schema.org rapor durumu

CI raporunda iki ayrı durum üretilir:

- **Schema.org yerel semantik doğrulama:** JSON-LD parse, tip, görünür içerik ve bağlantı bütünlüğü.
- **Google Rich Results hazırlığı:** Product işaretlemesi mevcut; merchant Offer uygunluğu yalnız taze doğrulanmış fiyat/stok verisi oluştuğunda açılır.

Bu yerel rapor, Google veya Schema.org’un uzaktan çalışan resmî servisinin yerine geçtiği iddiasını taşımaz. Resmî URL tabanlı testler yalnız değişiklik canlı `https://alo186.com` origininde yayımlandıktan sonra çalıştırılmalı; araç ekranındaki sonuç ayrıca canlı yayın makbuzuna eklenmelidir.
