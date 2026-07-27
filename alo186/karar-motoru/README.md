# ALO186 Elektrik Sorunu Karar Motoru v2

Elektrik sorununu güvenlik, belirti ve etkilenen alan bakımından ayırarak kullanıcıyı 112, 186, EDAŞ, bina yönetimi veya yetkili elektrikçi kanallarından doğru olana yönlendirir.

## Kapsam

Dört kategoride 25 problem:

- Kesinti ve şebeke: 8
- Pano ve koruma: 7
- Dış şebeke: 5
- Sayaç ve abonelik: 5

Kural kataloğu `rules.js` içinde sürümlenebilir veri olarak tutulur. Arayüz mantığı ile güvenlik/karar içeriği birbirinden ayrılmıştır.

## Akış

```text
Acil tehlike kontrolü
→ Problem kategorisi
→ Tam belirti
→ Gerekiyorsa etkilenen alan
→ Güvenli sonuç ve resmî/teknik kanal
```

## Güvenlik ilkeleri

- Elektrik çarpması, yangın, duman, kıvılcım, düşmüş iletken, hasarlı direk ve yanmış sayaç doğrudan acil güvenlik rotasına gider.
- Acil sonuçlarda `revenueAllowed=false` olur; affiliate veya ticari CTA gösterilmemelidir.
- Pano açma, enerjili iletkene dokunma, gerilim ölçme veya şalteri tekrar tekrar kaldırma talimatı verilmez.
- Sonuçlar kesin teşhis, uygunluk belgesi veya resmî başvuru değildir.
- Kurallar serbest metin üreten AI yerine deterministik katalogdan çözülür.

## Dosyalar

- `rules.js`: 25 problem, route template'leri ve resolver
- `app.js`: ekran akışı, state ve sonuç üretimi
- `index.html`: mobil kullanıcı arayüzü ve SEO
- `styles.css`: responsive ve güvenlik durum tasarımı
- `../tests/test_decision_rules.js`: güvenlik regresyon testleri

## Test

```bash
node alo186/tests/test_decision_rules.js
```

Testler:

- tam 25 problem ve benzersiz kimlik
- bütün kategorilerin dolu olması
- her problemde güvenli adım ve başvuru hazırlığı
- acil problemlerde 112 ve gelir yasağı
- kapsam bazlı resmî/elektrikçi/mixed rotaları
- abonelik işleminin EDAŞ bulucuya bağlanması

## Analytics

- `electrical_decision_answered`
- `electrical_decision_completed`
- `electrical_decision_action_clicked`

Kritik KPI'lar:

- karar akışı tamamlama
- doğru kanala geçiş
- problem ve route dağılımı
- acil sonuçlarda ticari tıklama sayısının sıfır olması
- kullanıcı yanlış yönlendirme geri bildirimi
