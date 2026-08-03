# AI CMS inceleme paketi: Jeneratör ATS Nötr Transferi

- **Sıra:** 1/3
- **Fırsat puanı:** 93/100
- **Durum:** `review`
- **Risk sınıfı:** `high`
- **Canonical adayı:** `/haberler/jenerator-ats-notr-transferi-3p-4p-kanit-dosyasi`
- **Birincil sorgu:** `jeneratör ATS nötr transferi`
- **Kaynak doğrulama tarihi:** 3 Ağustos 2026
- **İnsan onayı:** Zorunlu; AI veya otomasyon onay/publish yapamaz.

## Kullanıcı görevi

Jeneratör ve ATS projesinde nötrün anahtarlanıp anahtarlanmayacağını kullanıcı müdahalesi olmadan; tek hat şeması, N–PE bağları, kontak sırası, RCD ölçümü ve saha kabul testleriyle kanıtlamak.

## Neden seçildi?

Jeneratör nötr anahtarlama araması yüksek güvenlik ve proje niyeti taşır. Mevcut içerik RCD’nin neden açtığını açıklıyor; yeni rehber kullanıcının 3P/4P kararını bağlantı değiştirmeden bir kabul dosyasına dönüştürür.

## Mevcut içerikten ayrım

`/haberler/jenerator-devreye-girince-kacak-akim-rolesi-neden-atar` arıza belirtisini teşhis eder. Bu içerik teşhisi tekrar etmez; proje ve kabul ekibinin 3P/4P nötr transfer kararını hangi belgeler ve testlerle doğrulayacağını tanımlar.

## Somut çıktı

Tek hat, N–PE bağ noktaları, ATS nötr kontak sırası, RCD testleri ve gerçek yük transfer kaydından oluşan kabul dosyası.

## Kaynak kanıtı

- **S1 · IEC:** [IEC 60364-5-55](https://webstore.iec.ch/en/publication/25534) — Jeneratör setlerinin koruma, ayırma, nötr ve topraklama koşullarını sistem bütünlüğü içinde ele alır.
- **S2 · Schneider Electric ASCO:** [Neutral Configurations in Transfer Switches](https://www.se.com/us/en/download/document/ASC-DB-NCTS/) — Solid neutral, switched neutral ve ayrı türetilmiş kaynak ilişkisini açıklar.
- **S3 · Schneider Electric:** [Comparison of Neutral Wire Distribution Options for Data Centers](https://www.se.com/us/en/download/document/SPD_WP41_EN/) — Hassas yüklerde nötr dağıtımı ve transfer seçeneklerini karşılaştırır.

## AEO, schema ve dönüşüm

- İlk ekranda bağımsız doğrudan cevap.
- Canonical derleyicide `Article`, `FAQPage`, `BreadcrumbList`.
- Kurumsal `Organization` yazarlığı; `Person`, `ProfilePage`, `Product`, `Offer` yok.
- Yüksek risk nedeniyle affiliate ve doğrudan satın alma CTA’sı kapalı.
- Dönüşüm: kullanıcının servis talebine ekleyebileceği ölçümlü kabul dosyası kapsamı.

## Yayın kabul listesi

- [ ] Teknik iddialar ilgili `S#` kaynağıyla doğrulandı.
- [ ] Mevcut canonical içerikle görev çakışması bulunmuyor.
- [ ] Elektriksel müdahale kullanıcıya yaptırılmıyor.
- [ ] İç bağlantılar routing envanterinde çalışıyor.
- [ ] Canonical üretim, sitemap ve final artifact kalite kapıları başarılı.
- [ ] ChatGPT Sites önizlemesi kaynak commit ve paket hash ile doğrulandı.

## Onay komutu

```text
/cms approve jenerator-ats-notr-transferi-3p-4p-kanit-dosyasi
```

Komut canonical HTML, routing overlay ve ChatGPT Sites önizleme artifactını üretir. Zorunlu kontroller başarılı olmadan PR birleştirilmemelidir.
