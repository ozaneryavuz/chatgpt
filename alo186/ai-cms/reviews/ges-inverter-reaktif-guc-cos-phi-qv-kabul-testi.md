# ALO186 AI CMS inceleme paketi — ges-inverter-reaktif-guc-cos-phi-qv-kabul-testi

> Bu dosya canonical yayına dahil edilmez. PR incelemesi ve insan onayı için üretilmiştir.

## Durum

- State: **approved**
- Risk: **legal**
- Model: **gpt-5.6-thinking**
- Kalite: **88/100**
- Benzerlik: **0.46** — https://alo186.com/haberler/ges-inverter-reaktif-guc-q-u-cosphi-p-volt-var-ayari
- Kelime: **977**

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

- **S1 · IEC** — [IEC TS 62786-1:2023 — DER Grid Connection General Requirements](https://webstore.iec.ch/en/publication/62452) — erişim 2026-08-03 — birincil
- **S2 · IEC** — [IEC TS 62786-2:2026 — Additional Requirements for PV Generation Systems](https://webstore.iec.ch/en/publication/90029) — erişim 2026-08-03 — birincil
- **S3 · SMA** — [Reactive Power Control — Q, cos φ and Q(V)](https://manuals.sma.de/EDMM-10/en-US/13971373323.html) — erişim 2026-08-03 — birincil
- **S4 · TEİAŞ** — [Reaktif Güç Kontrolü Hizmeti](https://www.teias.gov.tr/reaktif-guc-kontrolu-hizmeti) — erişim 2026-08-03 — birincil
- **S5 · TEİAŞ** — [01 Ocak 2026 Sonrası Hibrit Santral RGK Veri Kayıt Formatları](https://www.teias.gov.tr/duyurular/01-ocak-2026-tarihinden-sonra-gecerli-olacak-yardimci-kaynakli-santrallerin-reaktif-guc-kontrolu-veri-kayit-dosyalarinin-formatlari-hakkinda-duyuru) — erişim 2026-08-03 — birincil
- **S6 · SMA** — [Q on Demand 24/7](https://manuals.sma.de/STPxxx70/en-US/10413884811.html) — erişim 2026-08-03 — birincil

## SEO

- Title: `GES İnverter Reaktif Güç Kabul Testi: cos φ ve Q(V)`
- H1: `GES inverterinde cos φ ve Q(V) reaktif güç ayarları nasıl kabul edilir?`
- Description: `GES inverter reaktif güç kabul testini bağlantı noktası ölçümü, cos φ, Q(V), işaret yönü, haberleşme ve kayıt kanıtlarıyla hazırlayın.`
- Canonical: `/haberler/ges-inverter-reaktif-guc-cos-phi-qv-kabul-testi`
- Birincil anahtar kelime: `GES inverter reaktif güç kabul testi`

## Doğrudan cevap

GES inverter reaktif güç kabul testi, yalnız ekranda seçili cos φ ya da Q(V) modunu görmekle tamamlanmaz. Kabul; bağlantı anlaşmasındaki referans noktasının belirlenmesi, bağlantı noktasında V-P-Q ölçen sayacın yön ve faz eşleşmesinin doğrulanması, şebeke işletmecisinin istediği sabit Q, sabit cos φ veya Q(V) karakteristiğinin farklı aktif güç ve gerilim koşullarında denenmesi, inverter ya da tesis kontrolörünün kVAr cevabı ile geri bildiriminin kaydedilmesi ve haberleşme kaybındaki fallback davranışının test edilmesiyle yapılır. Ayarlar tesise, bağlantı seviyesine ve resmî talebe özgüdür; başka bir santralden kopyalanmamalıdır.

## Reaktif güç talebi hangi noktada ve hangi belgeye göre doğrulanmalıdır?

İlk adım inverter menüsündeki parametreyi değil, yükümlülüğün uygulandığı referans noktasını belirlemektir. Şebeke bağlantı noktası, inverter AC terminali ve santral ortak barası aynı elektriksel nokta olmayabilir. Trafo, yardımcı tüketim, kablo ve başka üretim üniteleri nedeniyle inverterin verdiği Q ile bağlantı noktasında görülen Q farklılaşabilir.

Bağlantı anlaşması, proje onayı, dağıtım veya iletim işletmecisinin yazılı ayar talebi ve güncel test formatı tek kabul indeksi içinde tutulmalıdır. TEİAŞ'ın reaktif güç kontrolü hizmeti için yayımladığı rapor, tutanak ve veri kayıt formatları yalnız yükümlü tesisler için doğrudan uygulanmalı; küçük lisanssız bir GES'e evrensel zorunluluk gibi kopyalanmamalıdır.

- Bağlantı noktası, ölçüm noktası ve inverter terminalini tek hatta ayrı işaretleyin.
- İstenen çalışma modunu ve parametre kaynağını belge numarasıyla kaydedin.
- Dağıtım ve iletim seviyesindeki yükümlülükleri birbirine karıştırmayın.
- Geçerli test/tutanak formatının tarih ve sürümünü dosyaya ekleyin.

_Kaynaklar: S1, S2, S4, S5_

## Sayaç, CT yönü ve reaktif güç işaret sözleşmesi nasıl sınanır?

Q(V) veya cos φ kontrolü kapalı çevrim çalışacaksa yalnız gerilim ölçümü yeterli değildir; bağlantı noktasında V, P ve Q değerlerini doğru yönde ölçen uyumlu bir sayaç gerekir. CT yönünün, faz sırasının veya içe-dışa enerji işaretinin hatalı olması kontrolörün doğru komuta ters yönde tepki vermesine ve gerilim sorununu büyütmesine yol açabilir.

Kabul sırasında küçük ve güvenli bir reaktif güç komutu uygulanarak SCADA, kontrolör, inverter ve bağımsız analizörde Q işaretinin aynı anlamı taşıdığı doğrulanmalıdır. Faz bazlı akım ve gerilimler, toplam kW-kVAr, cos φ ve zaman damgaları birlikte kaydedilmeli; ölçüm sapması ve haberleşme gecikmesi ayrıca raporlanmalıdır.

- Sayaç ve CT faz/yön eşleşmesini tek hatla karşılaştırın.
- Endüktif ve kapasitif Q işaretini bütün cihazlarda aynı sözleşmeye bağlayın.
- Bağımsız analizör ile kontrolör ölçümünü eşzamanlı karşılaştırın.
- Ölçüm çözünürlüğü, gecikme ve zaman senkronunu kaydedin.

_Kaynaklar: S1, S3, S6_

## Sabit Q, cos φ ve Q(V) modları hangi senaryolarla kabul edilmelidir?

Sabit Q, sabit cos φ ve Q(V) birbirinin eş anlamlısı değildir. Sabit cos φ aktif güç değiştikçe gerekli kVAr değerini değiştirir; Q(V) ise bağlantı noktası gerilimine göre karakteristik eğri üzerinden cevap verir. Kontrol modu, eğri noktaları, deadband, rampa, öncelik ve sınırlar yalnız resmî talep ile üretici kabiliyeti birlikte değerlendirilerek ayarlanmalıdır.

Test; düşük, orta ve yüksek aktif güçte; eğri deadbandinin altında, içinde ve üstünde; komut artışı ve azalışında yapılmalıdır. Beklenen ve ölçülen Q, cevap süresi, kararlılık, salınım, aktif güç kısıtı ve inverter akım sınırı tek tabloda gösterilmelidir. İnverterin akım kapasitesi yetersizse aktif ve reaktif güç önceliği açıkça belgelenmelidir.

- Her çalışma modunu ayrı test senaryosu olarak tanımlayın.
- Q(V) eğrisinin kırılma noktaları, deadband ve rampasını doğrulayın.
- Aktif güç değişiminde cos φ hedefinin doğru kVAr ürettiğini karşılaştırın.
- Akım sınırında P-Q önceliği ve derating davranışını kaydedin.

_Kaynaklar: S1, S2, S3_

## Gece reaktif güç, uzak komut ve fallback davranışı nasıl test edilir?

Bazı inverterler sıfır aktif güçte veya gece çalışmasında reaktif güç sağlayabilir; bazı modlar ise birbirleriyle uyumsuz olabilir. Bu özellik bağlantı talebinde açıkça istenmemişse varsayılan olarak etkinleştirilmemeli, yardımcı tüketim ve termal etkileri ölçülmeden 24 saat reaktif güç desteği vaadi verilmemelidir.

Modbus, analog giriş, SCADA veya üst kontrolör komutu kesildiğinde sistemin son değerde kalma, güvenli varsayılana dönme ya da reaktif gücü sıfırlama davranışı test edilmelidir. Haberleşmenin geri gelmesi, kontrolör yeniden başlatması ve saat kayması sırasında yanlış veya çift komut oluşmadığı olay kayıtlarıyla kanıtlanmalıdır.

- Gece Q özelliğinin bağlantı talebi ve üretici uyumluluğunu doğrulayın.
- Haberleşme kesintisi ve bozuk ölçüm için fallback değerini test edin.
- Kontrolör ve inverter yeniden başlatma sırasını senaryolaştırın.
- Uzak komut, yerel ayar ve geri bildirim zaman damgalarını eşleştirin.

_Kaynaklar: S3, S6_

## GES reaktif güç kabul dosyasında hangi kanıtlar bulunmalıdır?

Teslim dosyasında bağlantı yükümlülüğü, tek hat, ölçüm noktaları, sayaç/CT yön kontrolü, firmware ve parametre yedeği, Q veya cos φ karakteristiği, test senaryoları, bağımsız analizör trendleri, SCADA komut/geri bildirim kayıtları, alarm listesi ve imzalı sonuç tablosu bulunmalıdır. Her ayar, hangi belge ve kaynak tarafından istendiğiyle ilişkilendirilmelidir.

Sonuç geçti, şartlı geçti veya kaldı olarak sınıflandırılmalıdır. Yanlış işaret, kararsız Q(V) cevabı, ölçüm kopması, açıklanmayan aktif güç kaybı veya güvenli olmayan fallback varsa tesis kabul edilmemelidir. Mevcut kontrolör ve sayaç bütün testleri kanıtla geçiyorsa sırf daha yeni model olduğu için inverter ya da enerji analizörü satın almak gereksizdir.

- Beklenen ve ölçülen V-P-Q-cos φ değerlerini tek zaman çizelgesinde verin.
- Parametre, firmware, eğri ve test dosyalarının hash/sürüm bilgisini saklayın.
- Sapmalar için sorumlu, kapanış kanıtı ve yeniden test tarihi tanımlayın.
- Kanıt yeterliyse gereksiz kontrolör veya inverter değişimi yapmayın.

_Kaynaklar: S1, S2, S3, S4, S5, S6_

## Sık sorulan sorular

### GES inverterinde cos φ değeri her tesiste aynı mı olmalıdır?

Hayır. Hedef değer bağlantı seviyesi, anlaşma, işletmeci talebi, tesis gücü ve çalışma moduna göre değişebilir. Başka bir santralden alınan cos φ ayarı, bağlantı noktasında yanlış reaktif güç üretimine yol açabilir.

_Kaynaklar: S1, S2_

### Q(V) kontrolü için yalnız gerilim ölçmek yeterli midir?

Kapalı çevrim tesis kontrolünde genellikle yeterli değildir. Bağlantı noktasında V, P ve Q değerlerini doğru yönde ölçen uygun sayaç gerekir; üretici dokümanı cos φ kontrol modunda da bağlantı noktası ölçümünü ister.

_Kaynaklar: S3, S6_

### İnverter gece reaktif güç verebilir mi?

Bazı modeller ve konfigürasyonlar sıfır aktif güçte reaktif güç sağlayabilir; ancak mod uyumluluğu, yardımcı tüketim, termal sınır ve işletmeci talebi model bazında doğrulanmalıdır. Bu özellik evrensel kabul edilmemelidir.

_Kaynaklar: S6_

### Reaktif güç testi yapılmadan yalnız parametre ekranı teslim için yeterli midir?

Hayır. Parametre ekranı niyeti gösterir; sayaç yönü, gerçek bağlantı noktası kVAr cevabı, zamanlama, kararlılık ve haberleşme kaybı davranışı yük altında ölçülmeden işlev kanıtlanmış olmaz.

_Kaynaklar: S1, S3, S4_

## İnsan onay komutu

PR sahibinin veya repository yetkilisinin yorumu:

```text
/cms approve ges-inverter-reaktif-guc-cos-phi-qv-kabul-testi
```

Onay iş akışı kalite puanı, kaynak güncelliği, iç linkler, kanibalizasyon ve risk sınırlarını yeniden çalıştırmadan canonical dosya üretmez.
