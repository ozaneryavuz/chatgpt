# ALO186 yaz serinleme büyüme ve güven denetimi v135

Tarih: 31 Temmuz 2026

## Seçilen üç yüksek potansiyelli aksiyon

### 1. Vantilatör, hava soğutucu veya klima karar testi

Yeni rota:

`/hesaplama/vantilator-hava-sogutucu-klima-karar/`

Arama niyetleri:

- vantilatör mü klima mı daha az elektrik harcar
- hava soğutucu işe yarar mı
- sulu vantilatör nemli yerde kullanılır mı
- vantilatör odayı soğutur mu
- klima yerine hava soğutucu alınır mı

Araç sıcaklık, bağıl nem, dış hava kalitesi, kişisel serinleme/oda soğutma hedefi, mevcut cihaz ve gerçek etiket wattlarını birlikte değerlendirir. Kullanıcının girdiği W × saat × gün değerlerini kWh'a çevirir; TL, tarife veya tasarruf garantisi yayımlamaz.

Sağlık kapıları:

- bilinç değişikliği, nöbet veya bayılmada 112;
- 40°C ve üzerindeki iç ortamda fanı tek güvenlik çözümü saymama;
- bebek, ileri yaş, gebelik veya kronik hastalıkta serin alan ve sağlık planını ürün karşılaştırmasından önce gösterme;
- kötü dış hava kalitesinde pencere havalandırmasını önermeme.

Ticari geçiş yalnız mevcut güvenli çözüm yetersiz, ortam düşük riskli ve üç açık onay tamamlanmışsa açılır. Mevcut çözüm gerçek sıcak gün testini geçmişse açık satın almama sonucu verilir.

Affiliate sınıfları:

- vantilatör / hava dolaştırıcı;
- yalnız sıcak-kuru ve havalandırılabilen ortamda evaporatif hava soğutucu;
- teknik kanıt tamamlanmadan doğrudan klima ürünü değil, ücretsiz BTU ve altyapı testi.

### 2. Portatif klima egzoz, pencere ve priz uygunluk testi

Yeni rota:

`/hesaplama/portatif-klima-egzoz-pencere-priz-uygunluk/`

Arama niyetleri:

- portatif klima hortumsuz çalışır mı
- portatif klima pencere kiti gerekli mi
- klima egzoz hortumu uzatılır mı
- portatif klima uzatma kablosuna takılır mı
- portatif klima kaç amper çeker
- portatif klima su tahliyesi nasıl yapılır

Araç sıcak egzozun dışarı atılması, pencere güvenliği, üretici uyumlu hortum, sızdırmazlık kiti, yoğuşma suyu, gerçek giriş W/A, doğrudan topraklı priz, RCD, priz ve sigorta sınırını birlikte kontrol eder.

Ticari kapılar:

- aynı odaya egzoz, kaçış penceresini engelleme, uzatılmış/ezilmiş hortum, uzatma/grup priz, doğrulanmamış RCD, aşırı akım veya su riski durumunda kapanır;
- mevcut cihaz yalnız pencere kiti eksikse yeni klima yerine aksesuar sınıfı açılabilir;
- mevcut cihaz bütün gerçek testleri geçiyorsa yeni ürün alınmaması belirtilir;
- çok odalı, ticari, medikal ve server alanları profesyonel kapsama ayrılır.

Affiliate sınıfları:

- portatif klima;
- tam model hortum çapı ve pencere tipiyle uyumlu sökülebilir pencere/egzoz kiti;
- fiyat, stok, puan, teslimat ve garanti bilgisi ALO186 üzerinde yayımlanmaz.

### 3. Yaz serinleme, elektrik ve tekrar test merkezi

Yeni rota:

`/sektor-rehberi/yaz-serinleme-elektrik-ve-tekrar-test-merkezi/`

Merkez doğrudan ürün bağlantısı göstermez. Kullanıcı durumunu şu rotalara bağlar:

- sağlık belirtisi ve acil numaralar;
- resmî elektrik kesintisi kanalı;
- serinleme cihazı görev ayrımı;
- portatif klima kurulum testi;
- klima BTU ve elektrik altyapısı testi;
- klima yedek güç testi;
- elektrik faturası kWh/gün karşılaştırması.

Tekrar ziyaret nedenleri:

- 7 gün: riskli kişi veya sıcak sağlık olayı sonrası plan kontrolü;
- 30 gün: yeni klima, portatif kurulum, bakım, yüksek tüketim, aktif kesinti veya oda değişikliği sonrası gerçek görev testi;
- 90 gün: filtre, hortum, pencere kiti, priz sıcaklığı, RCD, etiket W ve gerçek konfor testi.

Kişisel veri olmadan JSON görev planı ve `.ics` takvimi oluşturulur.

## Kaynak yaklaşımı

- WHO, `Heat and health`, 13 Temmuz 2026.
- WHO Europe, sıcak hava sağlık önerileri, Mayıs–Haziran 2026.
- T.C. Sağlık Bakanlığı bağlantılı il sağlık müdürlüğü, aşırı sıcakların sağlık etkileri, 9 Temmuz 2026.
- U.S. Department of Energy, Home Cooling ve Portable Air Conditioners.
- ENERGY STAR, oda kliması kapasite seçimi.

Yabancı kaynaklar Türkiye'de ürün, elektrik tesisatı, bina cephesi veya sağlık tedavisi onayı olarak sunulmaz. Tam model üretici belgesi, yetkili sağlık kaynağı ve yerel uzman değerlendirmesi önceliklidir.

## Güven ve ticari sözleşme

- Doğrulanmamış fiyat, stok, puan, satıcı, teslimat ve garanti kullanılmaz.
- `Product`, `Offer`, `aggregateRating` ve `availability` şemaları eklenmez.
- Affiliate bağlantısı açıkça belirtilir ve `rel="sponsored nofollow noopener"` taşır.
- ALO186 sağlık kuruluşu, EDAŞ, kamu kurumu, klima üreticisi, servis veya ürün satıcısı gibi gösterilmez.
- Aktif tehlike, sağlık belirtisi, elektrik hasarı, kaçış engeli ve profesyonel kapsam ticari sonuca dönüştürülmez.
- Mevcut güvenli cihaz yeterliyse satın almama sonucu verilir.
- Ad, telefon, e-posta, adres, konum, abonelik veya seri numarası istenmez.
- `localStorage`, `sessionStorage`, geolocation ve haricî ağ isteği kullanılmaz.

## Beklenen etki

| Aksiyon | Kullanıcı faydası | Gelir etkisi |
|---|---|---|
| Serinleme cihazı karar testi | Fan, hava soğutucu ve klimanın görevini; nem, sağlık ve gerçek kWh ile ayırır | Yüksek mevsimsel trafik, orta-yüksek nitelikli affiliate potansiyeli |
| Portatif klima kurulum testi | Yanlış egzoz, pencere kiti, hortum ve priz kullanımını satın almadan önce yakalar | Yüksek satın alma niyeti; cihaz veya yalnız aksesuar düzeyinde daha doğru dönüşüm |
| Yaz tekrar test merkezi | Tek seferlik aramayı 7/30/90 günlük görev ve bakım döngüsüne bağlar | Doğrudan gelir düşük; tekrar ziyaret, araçlar arası geçiş ve güven etkisi yüksek |

## Kabul

- İki hesaplayıcının modül ve karar testleri.
- Sağlık, aktif kesinti, elektrik tehlikesi ve profesyonel kapsam kapanışları.
- Satın almama ve üçlü affiliate onayı.
- Canonical rota, sitemap, custom-domain ve `/chatgpt` Pages build/smoke.
- Mevcut yayın, portal ve cihaz hasarı süre regresyonları.
