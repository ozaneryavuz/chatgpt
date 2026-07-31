# ALO186 kaçak akım rölesi uygunluk modülü — v136

## Seçim gerekçesi

Kaçak akım rölesi aramaları; elektrik çarpması korkusu, sürekli açma problemi ve pano ürünü satın alma niyetini aynı anda taşır. Kullanıcılar 30 mA ile 40/63 A değerlerini, RCCB ile RCBO'yu ve Type AC/A/F/B sınıflarını sık karıştırır. Modül bu kavramları ürün kartından önce ayırır.

## Güvenlik sınırları

- Duman, erime, ısınma, su teması, TEST düğmesi başarısızlığı ve izolasyon testi hatasında bütün ticari yollar kapanır.
- Sürekli açmada daha yüksek mA önerilmez; izolasyon, nötr-toprak, toplam kaçak ve devre ayrımı teşhisine geçilir.
- EV, PV, enerji depolama, UPS, trifaze sürücü, ticari ve medikal kullanım profesyonel tasarıma yönlendirilir.
- Pano kapağı açma, canlı ölçüm, kablo veya sigorta boyutlandırma talimatı verilmez.

## Teknik karar

- Genel modern ev yükü: Type A muhafazakâr ön seçim.
- Tek faz frekans kontrollü yük: Type F ön seçim; üretici şartı üstündür.
- Düzgün DC ihtimali bulunan EV/PV/UPS/VFD: Type B veya üreticinin eşdeğer çözümü; profesyonel doğrulama.
- Tek devre veya gereksiz açma ayrımı: RCBO.
- Çoklu devre üst kademesi: RCCB + ayrı MCB veya devre başına RCBO.
- 100/300 mA üst kademe, 30 mA kişisel korumanın yerine geçmez.

## Kaynaklar

- IEC 61008-1:2024 — RCCB genel kuralları.
- IEC 62423 — Type F ve Type B RCD.
- Hager Selection of RCD Types — yük sınıfları.
- Schneider Electric CA9UG000E — rutin TEST düğmesi kontrolü.

## Ticari ve gizlilik ilkeleri

- Yalnız güvenli ev tipi planlama, gerçek teknik açık ve üç açık onay sonrası ürün sınıfı bağlantısı.
- `rel="sponsored nofollow noopener"`.
- Fiyat, stok, puan, satıcı, teslimat ve garanti iddiası yok.
- Kişisel veri, konum, tarayıcı depolaması ve haricî istek yok.
