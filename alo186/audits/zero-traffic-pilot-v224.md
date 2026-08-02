# ALO186 sıfır trafik aktivasyon pilotu v224

Tarih: 3 Ağustos 2026

## Amaç

ALO186 için arama motoru trafiğini beklemeden ilk tekrar kullanılabilir kullanıcı davranışını doğrulamak. Pilotun giriş ürünü `/elektrik-dayaniklilik-karti/` rotasıdır.

Bu sürüm yeni içerik veya ürün kataloğu büyütmez. Kullanıcıya iki dakikada değer üretir; sonucu birlikte hareket edeceği kişiyle paylaşmasını ve işletme/site bağlamında mevcut Elektrik Sürekliliği Pasaportuna geçmesini sağlar.

## İlk 10 pilot konum

- 4 otel veya konaklama tesisi
- 2 apartman / site yönetimi
- 2 villa / yazlık
- 1 ofis
- 1 restoran, market veya soğuk zincir noktası

Her konumda en az iki kişi kartı birlikte değerlendirmelidir: konumu kullanan/yöneten kişi ve teknik ya da operasyon sorumlusu.

## Pilot uygulama sırası

1. Kart bağlantısını doğrudan karar vericiye gönder.
2. Kişinin kartı kendi başına tamamlamasını iste; cevapları görüşme sırasında yönlendirme.
3. Sonuç ekranındaki ilk üç aksiyonu birlikte gözden geçir.
4. “Kartı paylaş” adımının ikinci kişiye ulaşıp ulaşmadığını doğrula.
5. Site/işletme sonuçlarında Elektrik Sürekliliği Pasaportu handoff'unu göster.
6. Yedi gün sonra ilk aksiyonlardan en az birinin tamamlanıp tamamlanmadığını sor.
7. Otuz gün içinde kartın yeniden açılması veya başka bir konum için kullanılması davranışını ölç.

## Başarı kapıları

| Kapı | Ölçüm | İlk eşik |
|---|---|---:|
| Aktivasyon | Kartı başlatanların tamamlaması | >= %60 |
| Davet | Tamamlayanların paylaşım yapması | >= %25 |
| Ortak kullanım | Paylaşılan kartın ikinci kişi tarafından açılması | >= %40 |
| Aksiyon | Yedi günde ilk üç aksiyondan en az birinin kapanması | >= %35 |
| Tekrar kullanım | Otuz günde ikinci kart veya geri dönüş | >= %30 |
| B2B sinyali | Site/işletme kullanıcısının Pasaport handoff'una geçmesi | >= %20 |
| Ödeme doğrulaması | Gerçek ücretli pilot | ilk 10 konumdan >= 3 |

## Yalnız anonim olaylar

- `resilience_card_start`
- `resilience_card_complete`
- `resilience_card_share`
- `resilience_card_relative_restart`
- `resilience_card_restore`
- `resilience_card_official_channel`
- `resilience_card_business_handoff`

Analitiğe form yanıtları, açık adres, telefon, e-posta, abonelik numarası, serbest metin veya paylaşım bağlantısının hash içeriği gönderilmez.

## Tarayıcı depolama dayanıklılığı

Sonuç saklama kullanıcının açık seçimine bağlıdır. Tarayıcı gizlilik modu, gömülü web görünümü veya kurumsal politika `localStorage` erişimini engellerse araç puanlama, aksiyon üretme ve paylaşım işlevlerini bellekte sürdürür; yalnız 90 günlük geri yükleme özelliği kapanır. Depolama hatası kullanıcı akışını veya 112 / 186 güvenlik yönünü kesemez.

## Görüşme soruları

1. Kartı neden tamamladınız veya neden yarıda bıraktınız?
2. Sonuçta sizi şaşırtan tek şey neydi?
3. İlk üç aksiyondan hangisini gerçekten yaparsınız?
4. Bu kartı kiminle paylaşmanız gerekir?
5. Kesinti olduğunda tekrar açar mısınız; hangi bilgi eksik?
6. İşletme/site için olay kaydı, test takvimi ve sorumlu yönetimi sunulsa hangi koşulda ödeme yaparsınız?

“Faydalı mı?” yerine davranış ve ödeme soruları sorulmalıdır.

## Pilot dışı bırakılan işler

- Saatlik ürün veya ASIN ekleme
- Yeni şehir/ilçe içerik varyasyonları
- Toplu İngilizce çeviri
- Boş canlı kesinti haritası
- Kullanım doğrulanmadan mobil uygulama
- Puan tamamlanmadan affiliate CTA
- Kişisel veri veya serbest metin toplama

## Sonraki ürün kapısı

Bu pilot aktivasyon, paylaşım ve tekrar kullanım eşiklerini geçerse ikinci paket şu sırayla açılır:

1. Konum sahipliği ve davet modeli
2. Kesinti Olay Odası
3. Pano için yerel üretilen QR kartı
4. Jeneratör / UPS test takvimi
5. Partner elektrikçi paneli
6. Ücretli ALO186 Pro pilotu

Eşikler geçilmeden sensör ağı, topluluk haritası veya geniş SaaS geliştirmesine başlanmaz.
