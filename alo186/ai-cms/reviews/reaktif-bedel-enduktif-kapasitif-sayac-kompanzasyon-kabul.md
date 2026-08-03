# ALO186 AI CMS inceleme paketi — reaktif-bedel-enduktif-kapasitif-sayac-kompanzasyon-kabul

> Bu dosya canonical yayına dahil edilmez. PR incelemesi ve insan onayı için üretilmiştir.

## Durum

- State: **approved**
- Risk: **legal**
- Model: **gpt-5.6-thinking**
- Kalite: **88/100**
- Benzerlik: **0.20** — https://alo186.com/haberler/elektrik-faturasi-reaktif-enerji-enduktif-kapasitif-bedel
- Kelime: **909**

## Kalite kapıları

- ❌ metadata
- ✅ directAnswer
- ✅ contentDepth
- ✅ sources
- ✅ safety
- ✅ internalLinks
- ✅ uniqueness
- ✅ structuredData

### Hatalar

- Yok

### Uyarılar

- Yok

## AI risk notları

- AI ek risk notu üretmedi.

## Kaynaklar

- **S1 · EPDK** — [Elektrik Piyasası Tarifeleri Uygulama Usul ve Esasları](https://www.epdk.gov.tr/Detay/Icerik/3-17057/elektrik-piyasasi-tarifeleri-uygulama-usul-ve-esa) — erişim 2026-08-03 — birincil
- **S2 · IEC** — [IEC 62053-24:2020 — Static meters for reactive energy](https://webstore.iec.ch/en/publication/34533) — erişim 2026-08-03 — birincil
- **S3 · IEC** — [IEC 62056-6-1:2023 — OBIS object identification system](https://webstore.iec.ch/en/publication/67916) — erişim 2026-08-03 — birincil
- **S4 · Enerjisa** — [Reaktif Enerji / Bedel nedir?](https://www.enerjisa.com.tr/tr/sikca-sorulan-sorular/fatura-kalemleri/reaktif-enerji-bedel-nedir) — erişim 2026-08-03 — birincil
- **S5 · Schneider Electric** — [PowerLogic PFC Capacitor Bank — Installation and Operation Manual](https://www.se.com/us/en/download/document/BQT2027101/) — erişim 2026-08-03 — birincil

## SEO

- Title: `Reaktif Bedel, Sayaç Endeksleri ve Kompanzasyon Kabulü`
- H1: `Reaktif bedel neden gelir, endüktif–kapasitif sayaç ve kompanzasyon nasıl kontrol edilir?`
- Description: `Reaktif bedeli; tarife kapsamı, RI/RC–OBIS endeksleri, CT oranı, P/Q trendi ve kompanzasyon kademeleriyle kanıta dayalı doğrulayın.`
- Canonical: `/haberler/reaktif-bedel-enduktif-kapasitif-sayac-kompanzasyon-kabul`
- Birincil anahtar kelime: `reaktif bedel endüktif kapasitif sayaç`

## Doğrudan cevap

Reaktif bedel görüldüğünde doğrudan kondansatör eklenmemelidir. Önce güncel EPDK tarife kapsamı, fatura dönemi, aktif–endüktif–kapasitif başlangıç ve son endeksleri, OBIS kodları, sayaç çarpanı ile CT/VT oranı doğrulanır. Ardından faz bazlı P, Q, cos φ, kademe durumu ve harmonik trendiyle kompanzasyon arızası ayrılır. Anlık cos φ veya tek fatura satırı kök nedeni kanıtlamaz; mühürlü sayaç ve enerjili pano işlemleri yalnız yetkin ekipçe yapılmalıdır.

## Reaktif bedel görüldüğünde ilk olarak ne doğrulanmalıdır?

İlk adım yeni kondansatör satın almak değil, faturadaki abone grubu, kurulu güç, aktif enerji, endüktif ve kapasitif reaktif enerji değerleri ile okuma dönemini doğrulamaktır. Reaktif tarife kapsamı ve oranları EPDK'nın güncel tarife uygulama usul ve esaslarına bağlıdır; eski internet tabloları veya başka tesisin sınırı doğrudan kullanılmamalıdır.

Fatura, sayaç ekranı veya uzaktan okuma raporundaki başlangıç-son endekslerle eşleştirilmelidir. Sayaç değişimi, eksik okuma, çarpan, akım/gerilim trafosu oranı ya da döneme ait gün sayısı farklıysa yalnız yüzde hesabı yanıltıcı olabilir. Kişisel ve sözleşmesel bilgiler kamuya açık araçlara yüklenmemelidir.

- Fatura dönemi, abone grubu, kurulu güç ve tarife kapsamını kaydedin.
- Aktif, endüktif ve kapasitif başlangıç-son endeksleri ayrı doğrulayın.
- CT/VT oranı ve sayaç çarpanını tek hat ve sözleşmeyle eşleştirin.
- Güncel EPDK metnini görmeden sabit oran veya muafiyet ilan etmeyin.

_Kaynaklar: S1, S3, S4_

## Sayaçtaki RI/RC ve OBIS kodları nasıl eşleştirilir?

Farklı sayaç üreticileri ekranda RI, RC veya OBIS kodları gösterebilir. OBIS ölçüm nesnelerini benzersiz tanımlayan bir sistemdir; ancak ekrandaki kodun endüktif veya kapasitif yönü sayaç kılavuzu, enerji akış yönü ve tesis bağlantısıyla doğrulanmalıdır. Yaygın kod örnekleri faydalı ipucudur, fakat üretici ekran menüsü ve dört kadran işareti esastır.

Sayaç fotoğrafı alınırken tarih-saat, kod, değer, birim ve çarpan aynı kayıt setinde tutulmalıdır. Aktif enerji ile reaktif endeksler farklı zamanlarda okunursa oran yanlış çıkar. Ters akım trafosu polaritesi veya yanlış faz eşleşmesi, gerçek kompanzasyon durumundan farklı kayıt üretebilir.

- OBIS kodu, değer, birim ve zaman damgasını birlikte kaydedin.
- Sayaç kılavuzunda enerji yönü ve kadran tanımını doğrulayın.
- Aktif ve reaktif endeksleri aynı zaman sınırında karşılaştırın.
- Mühürlü sayaç ve CT devresine kullanıcı müdahalesi yapmayın.

_Kaynaklar: S2, S3, S4_

## Endüktif veya kapasitif aşımın kök nedeni nasıl ayrılır?

Endüktif aşım; kondansatör kademesinin devreye girmemesi, sigorta veya kontaktör arızası, düşük kapasitans, yanlış akım trafosu yönü, kontrol rölesi ayarı ya da artan motor ve trafo yükünden kaynaklanabilir. Kapasitif aşım ise düşük yükte fazla kademenin devrede kalması, sabit kondansatör, hatalı röle ölçümü, hızlı yük değişimi veya GES/inverter ve kablo etkileriyle görülebilir.

Kök neden için faz bazlı P, Q, cos φ, akım, gerilim, kademe durumu ve THD zaman serisi gerekir. Tek anlık cos φ veya yalnız fatura toplamı hangi kademenin arızalı olduğunu kanıtlamaz. Harmonikli tesiste kondansatör eklemek rezonans ve aşırı akım riskini büyütebileceğinden harmonik spektrum ve mevcut reaktör düzeni değerlendirilmelidir.

- Faz bazlı P–Q–cos φ ve kademe durumunu ortak zamanlı kaydedin.
- Endüktif ve kapasitif aşımı ayrı kök neden ağaçlarıyla inceleyin.
- CT yönü, röle faz seçimi, sigorta, kontaktör ve kapasitansı kontrol planına alın.
- Harmonik ölçmeden rastgele kondansatör kademesi eklemeyin.

_Kaynaklar: S1, S5_

## Kompanzasyon panosu onarım sonrası nasıl kabul edilir?

Onarım sonrası kabul, panonun yalnız hedef cos φ değerini kısa süre göstermesiyle tamamlanmaz. Düşük, tipik ve yüksek yükte kademe sırası, devreye girme-çıkma gecikmesi, kapasitif tarafa taşma, faz akımları, kondansatör ve reaktör sıcaklıkları, kontaktör davranışı ve kontrol rölesi alarmı kaydedilmelidir.

Bir fatura dönemini beklemeden sayaç endeks trendi ve güç analizörü verisiyle erken doğrulama yapılabilir; nihai finansal kapanış ise dağıtım veya tedarik faturası ve aynı dönem endeksleriyle yapılmalıdır. Sayaç verisi ile analizör farklıysa ölçüm noktası, zaman senkronu, CT oranı ve işaret sözleşmesi kontrol edilmelidir.

- Düşük, tipik ve yüksek yükte kademe geçişlerini test edin.
- Kapasitif taşma ve gece veya düşük yük davranışını ayrıca izleyin.
- Termal kontrolü akım ve kademe durumuyla eşleştirin.
- Onarım öncesi-sonrası sayaç endeksi ve analizör trendini karşılaştırın.

_Kaynaklar: S1, S2, S3, S5_

## Reaktif bedel itiraz ve kapanış dosyası neleri içermelidir?

Dosyada fatura ve sözleşme dönemi, kişisel verileri maskelenmiş endeksler, sayaç/OBIS kodları, CT/VT oranları, tek hat, kompanzasyon rölesi ayar yedeği, kademe testleri, güç kalitesi trendi, yapılan onarım ve yeniden kabul sonucu bulunmalıdır. Fatura hatası şüphesinde önce tedarik veya dağıtım şirketinin yazılı başvuru kanalı ve kayıt numarası kullanılmalıdır.

Teknik ölçüm uygun olduğu hâlde tarife veya endeks eşleşmesi yanlışsa ekipman değişimi çözüm değildir. Teknik arıza doğrulanırsa da bütün panoyu yenilemeden önce arızalı kademe, kontaktör, sigorta, kondansatör, reaktör veya ölçüm zinciri kanıtlanmalıdır. CTA: kişisel verisiz fatura–sayaç–P/Q–kademe kabul matrisini enerji yöneticisi ve yetkin elektrik mühendisine iletin.

- Faturadaki tekil kod, adres ve müşteri bilgilerini paylaşmadan önce maskeleyin.
- Başvuru numarası ve yazılı yanıtı teknik raporla aynı dosyada tutun.
- Tarife uyuşmazlığı ile pano arızasını ayrı sorumluluk alanları olarak gösterin.
- Kanıt yeterliyse gereksiz komple kompanzasyon panosu veya kondansatör satın almayın.

_Kaynaklar: S1, S2, S3, S4, S5_

## Sık sorulan sorular

### Reaktif bedel gelince hemen kondansatör eklenir mi?

Hayır. Önce tarife kapsamı, sayaç endeksleri, CT/VT oranı ve endüktif-kapasitif yön doğrulanır; sonra faz bazlı ölçümle kök neden bulunur. Harmonikli sistemde rastgele kademe eklemek riskli olabilir.

_Kaynaklar: S1, S4, S5_

### Sayaçta 3.8.0 ve 4.8.0 ne anlama gelir?

Yaygın uygulamada endüktif ve kapasitif reaktif enerjiyle ilişkilendirilir; kesin anlam sayaç kılavuzu, OBIS tanımı ve enerji akış yönüyle doğrulanmalıdır.

_Kaynaklar: S3, S4_

### Cos φ normal görünürken reaktif bedel gelebilir mi?

Evet. Anlık cos φ, bütün fatura döneminin endüktif ve kapasitif enerji oranını göstermez. Düşük yük, gece çalışması, hızlı yük değişimi veya geçmiş arıza dönem toplamını etkileyebilir.

_Kaynaklar: S1, S5_

### Reaktif bedel için EDAŞ mı tedarikçi mi aranır?

Fatura ve sözleşme tarafı için faturayı düzenleyen tedarikçi; sayaç, ölçüm veya dağıtım bağlantısı şüphesinde dağıtım şirketi devreye girer. Yazılı kayıt ve numara alınmalıdır.

_Kaynaklar: S1, S4_

## İnsan onay komutu

PR sahibinin veya repository yetkilisinin yorumu:

```text
/cms approve reaktif-bedel-enduktif-kapasitif-sayac-kompanzasyon-kabul
```

Onay iş akışı kalite puanı, kaynak güncelliği, iç linkler, kanibalizasyon ve risk sınırlarını yeniden çalıştırmadan canonical dosya üretmez.
