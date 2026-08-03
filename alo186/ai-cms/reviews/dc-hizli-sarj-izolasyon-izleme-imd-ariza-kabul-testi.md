# ALO186 AI CMS inceleme paketi — dc-hizli-sarj-izolasyon-izleme-imd-ariza-kabul-testi

> Canonical yayına dahil edilmez; insan teknik incelemesi içindir.

## Durum

- State: **review**
- Risk: **high**
- Kalite hedefi: **100/100**
- Tahmini benzerlik: **0.36** — `/haberler/ges-inverter-izolasyon-direnci-dusuk-hatasi`
- Kelime: **792**

## SEO ve kullanıcı çıktısı

- Title: `DC Hızlı Şarj İzolasyon İzleme ve IMD Kabul Testi`
- H1: `DC hızlı şarj istasyonunda izolasyon hatası ve IMD nasıl test edilir?`
- Canonical: `/haberler/dc-hizli-sarj-izolasyon-izleme-imd-ariza-kabul-testi`
- Anahtar kelime: `DC hızlı şarj izolasyon hatası IMD`
- Doğrudan cevap: IMD, yalıtılmış DC çıkışın izolasyon direncini sürekli izler; AC giriş RCD'sinin yerine geçmez. Kabul; güvenli test direnci simülasyonu, alarm, kontaktör, deşarj ve olay kaydıyla yapılır.

## Bölümler

- **DC hızlı şarjda IMD neyi izler, RCD'den farkı nedir?** — S1, S2, S5
- **Araç bağlanmadan önce izolasyon ön kontrolü nasıl kabul edilir?** — S1, S2, S5
- **Şarj sırasında izolasyon arızası oluşursa hangi sıra izlenmelidir?** — S1, S2, S3, S5
- **İzolasyon hatası araçtan mı istasyondan mı kaynaklanıyor?** — S1, S3, S4, S5
- **DC hızlı şarj izolasyon izleme sistemi nasıl teslim alınmalıdır?** — S1–S5

## Kaynaklar

- **S1 · IEC** — [IEC 61851-23:2023](https://webstore.iec.ch/en/publication/32973)
- **S2 · IEC** — [IEC 61557-8:2014](https://webstore.iec.ch/en/publication/5582)
- **S3 · IEC** — [IEC 61851-24:2023](https://webstore.iec.ch/en/publication/32582)
- **S4 · ISO** — [ISO 6469-3:2021](https://www.iso.org/standard/81746.html)
- **S5 · Bender** — [ISOMETER isoCHA425HV](https://www.bender.de/en/products/insulation-monitoring/isometer-isocha425hv-with-agh420-1/)

## İç bağlantılar

- [EV şarj tesisat uygunluğu](/haberler/ev-sarj-cihazi-icin-ev-tesisati-uygun-mu)
- [EV şarj Tip B RCD ve RDC-DD kabulü](/haberler/ev-sarj-kacak-akim-rcd-tip-b-rdc-dd-6ma-kabul)
- [Wallbox neden başlamıyor?](/haberler/elektrikli-arac-sarj-olmuyor-wallbox-neden-baslamiyor)
- [EV şarj kablosu ısınıyor](/haberler/ev-sarj-kablosu-prizi-isiniyor-ne-yapilmali)
- [EV şarj gücü neden düşük?](/haberler/ev-sarj-gucu-neden-dusuk-yavas-sarj)
- [EV şarj uygunluk aracı](/hesaplama/ev-sarj-uygunluk/)
- [Elektrik Portalı](/elektrik-portali)

## Yapılandırılmış veri ve dönüşüm

- `Article`, `FAQPage`, `BreadcrumbList`; `Organization` yazarlığı.
- Kişisel verisiz DC EVSE–IMD–kontaktör–deşarj kabul matrisi CTA’sı.
- `Person`, `Product`, `Offer`, fiyat, stok ve affiliate kapalı.
- Gerçek DC iletkenini toprağa bağlama veya araç bağlıyken kontrolsüz megger testi önerilmez.

## İnsan onay komutu

```text
/cms approve dc-hizli-sarj-izolasyon-izleme-imd-ariza-kabul-testi
```

Onay akışı kaynak, link, kalite, kanibalizasyon ve güvenlik kapılarını yeniden çalıştırmalıdır.
