# ALO186 AI CMS inceleme paketi — inverter-eps-backup-notr-toprak-rcd-kabul-testi

> Canonical yayına dahil edilmez; insan teknik incelemesi içindir.

## Durum

- State: **review**
- Risk: **high**
- Kalite hedefi: **100/100**
- Tahmini benzerlik: **0.44** — `/haberler/jenerator-devreye-girince-kacak-akim-rolesi-neden-atar`
- Kelime: **1000**

## SEO ve kullanıcı çıktısı

- Title: `İnverter EPS Çıkışında Nötr–Toprak ve RCD Kabulü`
- H1: `İnverter EPS veya backup çıkışında nötr–toprak bağı ve RCD nasıl doğrulanır?`
- Canonical: `/haberler/inverter-eps-backup-notr-toprak-rcd-kabul-testi`
- Anahtar kelime: `EPS çıkışında`
- Doğrudan cevap: EPS veya backup çıkışının enerji vermesi, elektrik çarpmasına karşı korumanın her modda doğru çalıştığını kanıtlamaz. Şebeke modunda N–PE bağı çoğunlukla gelen kaynaktan sağlanırken ada modunda inverterin toprak rölesi veya haricî anahtarlama düzeni yeni bir referans oluşturabilir. Kabul; tek hat ve ürün kılavuzu, faz ve nötr anahtarlama matrisi, şebeke–ada geçiş sırası, N–PE süreklilik durumu, RCD açma akımı–süresi ve tekrar şebekeye bağlanma testiyle yapılmalıdır. Enerjili terminal ve koruma testleri yalnız yetkin ekipçe gerçekleştirilmelidir.

## Bölümler

- **Şebeke ve ada modunda kaynak ile topraklama sistemi neden değişir?** — kaynaklar: S1, S2, S4, S5
- **Nötr–toprak bağı RCD çalışması için nasıl değerlendirilir?** — kaynaklar: S2, S3
- **Nötr anahtarlaması ve geçiş sırası hangi kanıtlarla kabul edilir?** — kaynaklar: S1, S4, S5
- **RCD fonksiyon testi şebeke ve ada modunda nasıl kaydedilir?** — kaynaklar: S2, S3, S4
- **EPS nötr–toprak ve RCD kabul dosyasında neler bulunmalıdır?** — kaynaklar: S1, S2, S3, S4, S5

## Kaynaklar

- **S1 · IEC** — [IEC 60364-8-82:2022+A1:2026 — Prosumer low-voltage electrical installations](https://webstore.iec.ch/en/publication/113148) — erişim 2026-08-03
- **S2 · Victron Energy** — [Wiring Unlimited — Ground, earth and electrical safety](https://www.victronenergy.com/media/pg/The_Wiring_Unlimited_book/en/ground%2C-earth-and-electrical-safety.html) — erişim 2026-08-03
- **S3 · Victron Energy** — [VEConfigure Manual — Inverter ground relay setting](https://www.victronenergy.com/media/pg/VEConfigure_Manual/en/inverter-settings.html) — erişim 2026-08-03
- **S4 · SMA Solar Technology** — [Backup Unit intended use and three-pole/four-pole versions](https://manuals.sma.de/BU-STPH-xP63x/en-US/16824414475.html) — erişim 2026-08-03
- **S5 · SMA Solar Technology** — [Secure power supply output neutral and grounding conductor](https://manuals.sma.de/SBSxx-10/en-US/1642621195.html) — erişim 2026-08-03

## İç bağlantılar

- [GES elektrik kesintisinde çalışır mı?](/haberler/ges-elektrik-kesintisinde-calisir-mi) — On-grid çalışma ile gerçek backup/EPS ada beslemesini temel düzeyde ayırır.
- [Nötr–toprak arası gerilim](/haberler/notr-toprak-arasi-gerilim-kac-volt-olmali) — N–PE ölçümünün tek başına koruma kanıtı olmadığını ve olası nedenleri tamamlar.
- [Kaçak akım rölesi Tip A ve Tip AC farkı](/haberler/kacak-akim-rolesi-tip-a-tip-ac-farki) — Backup yüklerinin RCD tip seçimini nötr anahtarlamasından ayrı değerlendirmeyi sağlar.
- [Kaçak akım rölesi Tip S selektivite](/haberler/kacak-akim-rolesi-tip-s-selektivite-nedir) — Ana ve tali RCD koordinasyonunu mod değişimi kabulüne bağlar.
- [Jeneratör devreye girince RCD neden atar?](/haberler/jenerator-devreye-girince-kacak-akim-rolesi-neden-atar) — Alternatif kaynaklarda nötr ve topraklama değişiminin benzer kök nedenlerini gösterir.
- [İnverter uygunluk aracı](/hesaplama/inverter-uygunluk/) — Yük, güç ve dalga biçimi uygunluğunu koruma düzeninden ayrı ön kontrolde ele alır.
- [Kurumsal elektrik sürekliliği ön değerlendirme](/kurumsal-elektrik-surekliligi-on-degerlendirme) — Çok kaynaklı tesislerde tek hat, koruma ve devreye alma kapsamını profesyonel çalışmaya taşır.

## Yapılandırılmış veri ve dönüşüm

- `Article`, `FAQPage`, `BreadcrumbList`; kurumsal `Organization` yazarlığı.
- Kişisel verisiz kabul/kanıt dosyası CTA’sı.
- `Person`, `Product`, `Offer`, fiyat, stok ve affiliate yolu kapalı.
- Enerjili ekipmana kullanıcı müdahalesi önerilmez; kanıt yeterliyse satın almama sonucu korunur.

## İnsan onay komutu

```text
/cms approve inverter-eps-backup-notr-toprak-rcd-kabul-testi
```

Onay akışı kaynak, link, kalite, kanibalizasyon ve güvenlik kapılarını yeniden çalıştırmalıdır.
