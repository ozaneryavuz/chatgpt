# AI CMS inceleme paketi: BESS Güvenlik Dosyası

- **Sıra:** 3/3
- **Fırsat puanı:** 90/100
- **Durum:** `review`
- **Risk sınıfı:** `high`
- **Canonical adayı:** `/haberler/bess-guvenlik-dosyasi-iec-62933-ul-9540a-kontrolu`
- **Birincil sorgu:** `BESS güvenlik dosyası`
- **Kaynak doğrulama tarihi:** 3 Ağustos 2026
- **İnsan onayı:** Zorunlu; AI veya otomasyon onay/publish yapamaz.

## Kullanıcı görevi

Ticari veya endüstriyel BESS için ürün sertifikasının ötesinde; sistem seviyesi tasarım, termal kaçak, gaz, elektriksel ayırma, acil durum, devreye alma, bakım ve yaşam döngüsü kanıtlarını tek dosyada doğrulamak.

## Neden seçildi?

BESS yatırımlarında yangın ve yaşam döngüsü güvenlik kanıtı 2025–2026 standart güncellemeleriyle daha kritik hâle geldi. Mevcut içerikler kapasite, SoC/SoH, VPP ve termal kaçak kavramlarını açıklıyor; kurulum öncesi bütün güvenlik dosyasını bir kanıt matrisinde toplayan görev eksik.

## Mevcut içerikten ayrım

`/hesaplama/bess-vpp-gelir-hazirligi/` ticari-operasyonel hazırlığı; LiFePO4 rehberi hücre ve termal kaçak kavramlarını ele alır. Bu içerik sistem seviyesi test, yerleşim, gaz, elektriksel ayırma, acil durum, bakım ve hizmet sonu kanıt dosyasını hedefler.

## Somut çıktı

Gereklilik, test edilen konfigürasyon, saha eşleşmesi, sorumlu taraf, uygunsuzluk ve kapanış kanıtını birleştiren BESS güvenlik matrisi.

## Kaynak kanıtı

- **S1 · IEC:** [IEC 62933-5-2:2025](https://webstore.iec.ch/en/publication/68297) — Şebekeye entegre EES sistemleri için yaşam döngüsü güvenliği.
- **S2 · IEC:** [IEC 62933-5-4:2026](https://webstore.iec.ch/en/publication/67442) — Şebekeden bağımsız EES uygulamalarında güvenlik yaklaşımı.
- **S3 · UL Solutions:** [UL 9540A Test Method](https://www.ul.com/services/ul-9540a-test-method) — Termal kaçak yangın yayılımının hücre, modül, ünite ve kurulum düzeylerinde test çerçevesi.
- **S4 · NFPA:** [NFPA 855 — 2023 edition](https://link.nfpa.org/all-publications/855/2023) — Sabit enerji depolama sistemlerinde yerleşim, yangın koruması ve acil durum planlaması.

## AEO, schema ve dönüşüm

- İlk ekranda güvenlik dosyasının zorunlu kanıt katmanlarını özetleyen doğrudan cevap.
- Canonical derleyicide `Article`, `FAQPage`, `BreadcrumbList`.
- Kurumsal `Organization` yazarlığı; kişi profili, ürün veya teklif şeması yok.
- Yüksek risk nedeniyle affiliate ve ürün satın alma CTA’sı kapalı.
- Dönüşüm: tesis ve yatırım ekibinin kurumsal teknik ön değerlendirme kapsamında kanıt matrisi hazırlaması.

## Yayın kabul listesi

- [ ] Her teknik iddia ilgili `S#` kaynağıyla doğrulandı.
- [ ] UL 9540A sonucu saha uygunluğu garantisi gibi sunulmuyor.
- [ ] IEC 62933-5-2 ve 5-4 kapsamları doğru ayrılıyor.
- [ ] Yerel yetkili merci ve itfaiye koordinasyon sınırı görünür.
- [ ] Kullanıcıya kabin, DC bara veya alarm eşiklerine müdahale önerilmiyor.
- [ ] Mevcut canonical içerikle görev çakışması bulunmuyor.
- [ ] Canonical build, sitemap ve ChatGPT Sites önizleme kapıları başarılı.

## Onay komutu

```text
/cms approve bess-guvenlik-dosyasi-iec-62933-ul-9540a-kontrolu
```

Komut canonical HTML, routing overlay ve ChatGPT Sites önizleme artifactını üretir. Zorunlu kontroller başarılı olmadan PR birleştirilmemelidir.
