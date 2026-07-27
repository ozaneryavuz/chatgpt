# chatgpt

## ALO186 geliştirmeleri

- [ALO186 ücretsiz araçlar ve yayın merkezi](./alo186/)
- [Tam Türkiye EDAŞ Arama Motoru](./alo186/turkiye-arama/)
- [25 sorunlu 186 / 112 / elektrikçi karar motoru](./alo186/karar-motoru/)
- [Elektrik Hesaplama Merkezi](./alo186/hesaplama/)
- [Akıllı Ürün Eşleştirme ve Affiliate Katalog](./alo186/urun-eslestirme/)
- [Otel, Site ve İşletme Elektrik Sürekliliği Paneli](./alo186/sureklilik-paneli/)
- [Elektrik Sürekliliği SaaS API v0.2](./alo186/sureklilik-api/)
- [Elektrik Faturası Zekâ Merkezi](./alo186/fatura-analizi/)
- [UPS ve Power Station süre hesabı](./alo186/hesaplama/ups-suresi/)
- [EV şarj süresi ve maliyet hesabı](./alo186/hesaplama/ev-sarj-suresi/)
- [Kablo gerilim düşümü ön hesabı](./alo186/hesaplama/kablo-gerilim-dusumu/)
- [Kesinti hazırlık planı](./alo186/hesaplama/kesinti-hazirlik-plani/)
- [Detaylı Yedek Güç Hesaplayıcısı](./alo186/yedek-guc-hesaplayici/)
- [Elektrik Kesintisi Maliyet Hesaplayıcısı](./alo186/kesinti-maliyet-hesaplayici/)

### Tam Türkiye EDAŞ Arama Motoru

81 il, 973 ilçe, 21 dağıtım şirketi, İstanbul Avrupa/Anadolu yakası ayrımı, Türkçe karakter toleransı, şirket alias'ları ve 112/186/elektrikçi işlem niyetlerini tek arama kutusunda birleştirir. İlçe verisi alınamazsa il ve şirket araması yerel yedek katalogla çalışmaya devam eder.

### 25 sorunlu karar motoru

Kesinti, faz, nötr, pano, kaçak akım, sayaç, sokak aydınlatması, direk, trafo ve dış hat problemlerini dört ana kategoride sınıflandırır. Elektrik çarpması, yangın, kıvılcım ve düşmüş iletkende 112 önceliği ve ticari CTA yasağı uygulanır.

### Akıllı Ürün Eşleştirme

Powerbank ve akım korumalı grup priz kategorilerinde teknik minimumları karşılayan doğrulanmış ASIN kartları sunar. Mini UPS, acil aydınlatma, duman alarmı, power station ve priz test cihazında doğrudan uygunluk iddiası yerine rehberli seçim ve profesyonel guardrail üretir. Statik fiyat ve stok göstermez.

### Elektrik Sürekliliği Paneli

Otel, apartman/site ve küçük işletmeler için local-first pilot panelidir. Çoklu lokasyon, kritik yük, jeneratör/UPS testleri, kesinti olayı, görev, zaman çizelgesi, maliyet, audit log, JSON yedek ve PDF çıktısı sunar.

### Elektrik Sürekliliği SaaS API v0.2

Local-first paneli çok kullanıcılı ürüne taşıyan FastAPI/PostgreSQL temelidir. Scrypt parola güvenliği, süreli imzalı oturum, kuruluş/tenant izolasyonu, admin-teknik ekip-görüntüleyici rolleri, kritik yükler, varlık testleri, P1 yüklere göre otomatik olay görevleri, zorunlu görev kapanış koruması ve kuruluş bazlı audit log sağlar. Docker Compose, SQLite test ortamı ve GitHub Actions kalite kontrolü içerir.

### Elektrik Faturası Zekâ Merkezi

2026 SKTT limiti, yıl sonu tüketim tahmini, anomali analizi ve serbest tüketici ön kontrolünü kişisel veri toplamadan tarayıcı içinde gerçekleştirir.

### Elektrik Hesaplama Merkezi

UPS/power station süresi, EV şarj süresi ve maliyeti, kablo gerilim düşümü ve kişiselleştirilmiş kesinti hazırlık planını ortak mobil arayüzde toplar. Hesaplamalar kullanıcı tarayıcısında yapılır; varsayımlar ve güvenlik sınırları görünür biçimde sunulur.

### Detaylı Yedek Güç Hesaplayıcısı

Cihazların sürekli ve kalkış gücünü birlikte değerlendirir; hedef süreye göre gerekli Wh kapasitesini veya mevcut UPS/power station ürününün tahmini çalışma süresini hesaplar. LiFePO4, lityum ve kurşun-asit batarya varsayımlarını, dönüşüm kayıplarını, yaşlanma payını ve kapasite rezervini açıkça gösterir.

### Kesinti Maliyet Hesaplayıcısı

Ev, site, otel ve işletmeler için ciro kaybı, personel bekleme, stok/gıda kaybı, jeneratör yakıtı, yeniden başlatma ve cihaz hasarı kalemlerini olay başı ve yıllık toplamda hesaplar; süreklilik yatırımı için öncelikli aksiyonlar üretir.

## Geliştirme programı

GitHub görevleri:

- #2 ALO186 büyüme programı epic
- #3 Tam Türkiye il–ilçe–EDAŞ arama motoru — tamamlandı
- #4 25 elektrik sorunu karar motoru — tamamlandı
- #5 Doğrulanmış ürün eşleştirme ve affiliate — v1 yayımlandı, katalog genişlemesi sürüyor
- #6 Otel/site/işletme sürekliliği paneli — local-first pilot ve SaaS API v0.2 yayımlandı; üretim sertleştirmesi sürüyor
- #7 Kullanıcı fayda hesaplayıcıları v1 — tamamlandı

## Yayın

`.github/workflows/alo186-fatura-pages.yml` ana daldaki `alo186/**` değişikliklerinde bütün statik ALO186 modüllerini GitHub Pages artifact'ına paketler.

Canlı `alo186.com` entegrasyonunda kaynak klasörler ile canonical rotalar `alo186/deployment/routing-manifest.json` üzerinden eşleştirilmelidir.
