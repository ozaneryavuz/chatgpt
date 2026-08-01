# ALO186 duman alarmı ve yangın kaçış güvenliği büyüme denetimi v162

Doğrulama tarihi: 1 Ağustos 2026

## Seçilen en yüksek potansiyelli 3 aksiyon

1. Sürekli alarm, aralıklı bip, yemek/buhar kaynaklı alarm ve test başarısızlığını ayıran acil durum aracı.
2. Konut tipi duman alarmı kapsamı, yerleşim, batarya yedeği, bağlantı, test ve cihaz yaşı uygunluk aracı.
3. Kişisel verisiz JSON ve 7/30/90 günlük ICS çıktılı duman alarmı ile yangın kaçış planı tekrar test merkezi.

## Arama niyeti

- duman alarmı neden ötüyor
- duman alarmı aralıklı bip sesi
- duman alarmı düşük pil sesi
- yemek yaparken duman alarmı çalıyor
- duman alarmı test düğmesi çalışmıyor
- duman alarmı evde nereye takılır
- her odaya duman alarmı gerekli mi
- pilli duman alarmı mı kablolu alarm mı
- duman alarmı kaç yılda değiştirilir
- duman alarmı aylık test ve yangın kaçış planı

## İçerik boşluğu

ALO186’te karbonmonoksit alarmı ve jeneratör güvenliği içeriği bulunmasına rağmen duman alarmının gerçek yangın, aralıklı hata sesi, istenmeyen alarm, yatak odası/kat kapsamı, şebeke kesintisi yedeği, birbirine bağlı uyarı, cihaz yaşı ve ev kaçış planını aynı fail-closed kullanıcı yolculuğunda birleştiren canonical araç yoktu. Repo aramasında aynı görev başlığı bulunmadı.

## Kullanıcı yolculuğu

arama veya alarm olayı
→ duman, alev, yoğun ısı, yanık kokusu ve içeride kişi kontrolü
→ tahliye, 112 ve yeniden giriş yasağı
→ sürekli alarm / aralıklı bip / yemek-buhar / test başarısızlığı ayrımı
→ tam model ses ve ışık kodu
→ konut ile ortak-profesyonel sistem ayrımı
→ yatak odası, uyuma alanı ve kat kapsamı
→ test, üretim tarihi, yedek enerji ve birbirine bağlı uyarı
→ mevcut kapsam yeterliyse satın alma yok
→ yalnız kablolama gerektirmeyen doğrulanmış konut alarmı açığında açıklamalı affiliate bağlantısı
→ olay sonrası, aylık ve üç aylık tekrar test

## Affiliate ürün kategorileri

Yalnız aktif olay bulunmayan, tek konut kapsamındaki ve mevcut sistemin eksik, testte başarısız veya kullanım süresi dolmuş olduğu doğrulanan senaryoda:

- tam model etiketi ve üretici talimatı doğrulanacak konut tipi pilli duman alarmı
- birden fazla alarm bölgesi için üretici uyumluluğu ve birlikte uyarı testi doğrulanacak kablosuz bağlantılı pilli duman alarmı

Affiliate dışı / profesyonel kapalı alanlar:

- aktif duman, alev, yoğun ısı, yanık kokusu veya alarm olayı
- apartman, site, otel, okul, işyeri ve ortak yangın sistemi
- şebeke bağlantılı alarm, yangın paneli ve kablolama değişikliği
- işitme güçlüğü için strobe/titreşimli özel uyarı tasarımı
- etiketi, modeli, üretim tarihi veya test sonucu bilinmeyen cihaz
- çalışan, genç ve kapsama uygun mevcut alarm

## Dönüşüm noktaları

1. İlk araçta ürün gösterilmez; tahliye, 112, sinyal deseni ve tam model kılavuzu önceliklidir.
2. İkinci araçta kapsam, test, yaş, etiket ve yedek enerji yeterliyse “Mevcut duman alarmı kapsamı yeterli — yeni ürün almayın” sonucu verilir.
3. Ortak/profesyonel veya şebeke bağlantılı sistemlerde affiliate tamamen kapanır.
4. Yalnız gerçek konut alarmı açığı doğrulanırsa kategori paneli açılır.
5. Amazon bağlantısı; ihtiyaç, teknik yeniden doğrulama ve satış ortaklığı açıklaması için üç ayrı onaydan sonra etkinleşir.
6. Bağlantı `rel="sponsored nofollow noopener"` ve `alo186rehber-21` etiketi taşır.

## Tekrar ziyaret nedenleri

- gerçek alarm, duman veya yangın olayı sonrası kontrol
- aralıklı bip, düşük pil, hata veya kullanım sonu göstergesi
- aylık test düğmesi veya bağlı alarm testinin başarısız olması
- yeni ev, kat planı, yatak odası veya oda kullanım değişikliği
- yeni kiracı, çocuk, yaşlı veya erişilebilirlik ihtiyacı
- tadilat, boya, toz, mutfak düzeni veya alarm yerinin değişmesi
- üretim tarihinin 10 yıla yaklaşması
- geri çağırma, servis bülteni veya yerel kural değişikliği

Merkez doğrudan affiliate bağlantısı içermez. Kişisel veri toplamadan `application/json` görev planı ve `text/calendar` biçiminde 7, 30 ve 90 günlük ICS kayıtları oluşturur.

## Beklenen kullanıcı faydası

- Sürekli alarm veya belirsiz sinyal düşük pil sayılmaz; tahliye ve 112 gecikmez.
- Yemek/buhar alarmında pil çıkarma davranışı önlenir.
- Şebeke bağlantılı ve ortak sistemler tüketici alarmıyla ikame edilmez.
- Her yatak odası, uyuma alanı ve kat kapsamı görünür hâle gelir.
- Çalışan ve uygun mevcut alarm gereksiz yere değiştirilmez.
- Aylık test, cihaz yaşı, yedek enerji ve kaçış planı tek görev döngüsünde izlenir.

## Beklenen gelir etkisi

Duman alarmı kategorisi düşük-orta sepetli ancak güvenlik ihtiyacı açık ve tekrar testi güçlü bir ürün sınıfıdır. Fail-closed güvenlik kapıları ham affiliate tıklamasını azaltabilir; buna karşılık mağazaya geçen ziyaretçinin gerçek kapsam açığı, ürün görevi ve bağlantı türü daha nettir. Beklenen doğrudan gelir etkisi orta, organik arama ve tekrar ziyaret etkisi yüksek, güven ve yanlış satın alma/iade azaltma etkisi yüksektir.

## Kaynak doğrulaması

- T.C. İçişleri Bakanlığı 112 Acil Çağrı Merkezi: yangın dahil acil çağrıların tek numara 112 altında toplanması.
- USFA, 1 Mayıs 2026 gözden geçirmesi: her yatak odası, her ayrı uyuma alanının dışı ve her kat; en az ayda bir test; üretim tarihinden 10 yıl sonra değişim.
- USFA duman alarmı rehberi: alarm türleri, birbirine bağlantı, üretici montaj talimatı ve yemek/buharda pili çıkarmama yaklaşımı.
- CPSC, 23 Ocak 2026: bataryalı veya batarya yedekli alarm, birbirine bağlı uyarı ve aylık test.

Genel rehberler belirli ürün veya Türkiye’deki bina için otomatik uygunluk belgesi değildir. Kesin montaj yüksekliği, mutfak/banyo mesafesi, algılama teknolojisi, kablolama ve bakım için üretici talimatı ile yerel kurallar korunur.

## Güven ve ticaret sözleşmesi

- Doğrulanmamış fiyat, stok, puan, satıcı, teslimat veya garanti kullanılmaz.
- `Product`, `Offer`, `availability` ve `aggregateRating` şeması oluşturulmaz.
- Aktif yangın/alarm, profesyonel sistem, şebeke bağlantısı, erişilebilirlik tasarımı, belirsiz model ve çalışan mevcut sistemde affiliate kapalıdır.
- İlk acil durum sayfası ve tekrar test merkezi affiliate içermez.
- Mevcut sistem yeterli — yeni ürün almayın sonucu korunur.
- ALO186; 112, itfaiye, üretici, sertifikasyon kuruluşu, test laboratuvarı, servis, satıcı veya resmî kurum gibi gösterilmez.
- Ad, adres, telefon, e-posta, konum, bina planı veya seri numarası istenmez.
- `localStorage`, `sessionStorage`, geolocation veya haricî form gönderimi kullanılmaz.
