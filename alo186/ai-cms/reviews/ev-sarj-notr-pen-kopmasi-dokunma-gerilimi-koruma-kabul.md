# ALO186 AI CMS inceleme paketi — ev-sarj-notr-pen-kopmasi-dokunma-gerilimi-koruma-kabul

> Canonical yayına dahil edilmez; insan teknik incelemesi içindir.

## Durum

- State: **review**
- Risk: **high**
- Kalite hedefi: **100/100**
- Tahmini benzerlik: **0.46** — `/haberler/notr-kopmasi-nasil-anlasilir`
- Kelime: **980**

## SEO ve kullanıcı çıktısı

- Title: `EV Şarjda Nötr/PEN Kopması ve Dokunma Gerilimi Koruması`
- H1: `EV şarj noktasında nötr veya PEN kopması riski nasıl kabul edilir?`
- Canonical: `/haberler/ev-sarj-notr-pen-kopmasi-dokunma-gerilimi-koruma-kabul`
- Anahtar kelime: `EV şarj PEN kopması koruması`
- Doğrudan cevap: EV şarj noktasında nötr veya PEN kopması koruması yalnız ürün etiketiyle kabul edilmez. Önce TT, TN-S veya TN-C-S/PEN besleme düzeni doğrulanır; cihazın tam modeli, algılama yöntemi, ayırdığı kutuplar, kontaktör geri bildirimi ve reset davranışı güvenli simülasyonla belgelenir. Birleşik PEN bulunmayan sistemlerde open PEN çözümü otomatik gereklilik değildir.

## Bölümler

- **Önce TT, TN-S ve TN-C-S/PEN sistemi nasıl ayrılır?** — kaynaklar: S1, S3, S4
- **Koruma cihazının hangi arızayı algıladığı nasıl doğrulanır?** — kaynaklar: S2, S4, S5
- **Nötr/PEN arızası fonksiyon testi hangi sınırlarla yapılmalıdır?** — kaynaklar: S1, S2, S4, S5
- **Gerilim düşümü veya şebeke dalgalanması yanlış PEN alarmı oluşturabilir mi?** — kaynaklar: S1, S4, S5
- **EV şarj nötr/PEN koruması hangi kabul dosyasıyla teslim alınmalıdır?** — kaynaklar: S1, S2, S3, S4, S5

## Kaynaklar

- **S1 · IEC** — [IEC 60364-7-722:2018 — Supplies for electric vehicles](https://webstore.iec.ch/en/publication/29958) — erişim 2026-08-03
- **S2 · IEC** — [IEC 61851-1:2017 — Electric vehicle conductive charging system](https://webstore.iec.ch/en/publication/33644) — erişim 2026-08-03
- **S3 · IEC** — [IEC 60364-4-41:2005+A1:2017 — Protection against electric shock](https://webstore.iec.ch/en/publication/60169) — erişim 2026-08-03
- **S4 · IET** — [Open combined protective and neutral conductor detection devices — IET 01:2024](https://electrical.theiet.org/guidance-and-codes-of-practice/publications-by-category/electric-vehicles/open-combined-protective-and-neutral-pen-conductor-detection-devices-opdds) — erişim 2026-08-03
- **S5 · IET** — [New standard to ensure safety for electric vehicle charging equipment](https://www.theiet.org/media/press-releases/press-releases-2024/press-releases-2024-october-december/1-october-2024-new-standard-to-ensure-safety-for-electric-vehicle-charging-equipment) — erişim 2026-08-03

## İç bağlantılar

- [EV şarj tesisat uygunluğu](/haberler/ev-sarj-cihazi-icin-ev-tesisati-uygun-mu)
- [EV şarj Tip B RCD ve RDC-DD kabulü](/haberler/ev-sarj-kacak-akim-rcd-tip-b-rdc-dd-6ma-kabul)
- [Nötr kopması nasıl anlaşılır?](/haberler/notr-kopmasi-nasil-anlasilir)
- [Nötr–toprak arası gerilim](/haberler/notr-toprak-arasi-gerilim-kac-volt-olmali)
- [Wallbox neden başlamıyor?](/haberler/elektrikli-arac-sarj-olmuyor-wallbox-neden-baslamiyor)
- [EV şarj uygunluk aracı](/hesaplama/ev-sarj-uygunluk/)
- [Kurumsal elektrik sürekliliği ön değerlendirmesi](/kurumsal-elektrik-surekliligi-on-degerlendirme)

## Yapılandırılmış veri ve dönüşüm

- `Article`, `FAQPage`, `BreadcrumbList`; kurumsal `Organization` yazarlığı.
- Kişisel verisiz şebeke sistemi–EVSE–ayırma–RCD kabul matrisi CTA’sı.
- `Person`, `Product`, `Offer`, fiyat, stok ve affiliate yolu kapalı.
- Gerçek nötr/PEN iletkenini açma, korumayı köprüleme veya enerjili EVSE müdahalesi önerilmez.

## İnsan onay komutu

```text
/cms approve ev-sarj-notr-pen-kopmasi-dokunma-gerilimi-koruma-kabul
```

Onay akışı kaynak, link, kalite, kanibalizasyon ve güvenlik kapılarını yeniden çalıştırmalıdır.
