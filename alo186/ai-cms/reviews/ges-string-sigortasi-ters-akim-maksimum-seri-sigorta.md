# AI CMS inceleme paketi: GES String Sigortası

- **Sıra:** 2/3
- **Fırsat puanı:** 91/100
- **Durum:** `review`
- **Risk sınıfı:** `high`
- **Canonical adayı:** `/haberler/ges-string-sigortasi-ters-akim-maksimum-seri-sigorta`
- **Birincil sorgu:** `GES string sigortası`
- **Kaynak doğrulama tarihi:** 3 Ağustos 2026
- **İnsan onayı:** Zorunlu; AI veya otomasyon onay/publish yapamaz.

## Kullanıcı görevi

GES tasarımında paralel stringler için sigorta gerekip gerekmediğini, sigorta satın almadan önce ters akım yolu, modül maksimum seri sigorta sınırı, inverter reverse-current bilgisi ve kablo kapasitesiyle kanıtlamak.

## Neden seçildi?

PV string sigortası, GES tasarım ve bakım ekiplerinin doğrudan proje kararı verdiği yüksek değerli bir sorgudur. Mevcut GES içerikleri ark, izolasyon, clipping ve şebeke gerilimini kapsıyor; ters akım ile modül maksimum seri sigorta sınırı için ayrı canonical görev bulunmuyor.

## Mevcut içerikten ayrım

`/haberler/ges-inverter-afci-dc-ark-hatasi` ve izolasyon rehberleri arıza teşhisidir. Bu içerik yalnız paralel string geri akımı, modül maksimum seri sigorta sınırı ve gPV koruma koordinasyonu görevine odaklanır.

## Somut çıktı

MPPT bazlı string matrisi, ters akım ön hesabı, modül sınırı, gPV sigorta, DC kesme kapasitesi ve kablo koordinasyon tablosu.

## Kaynak kanıtı

- **S1 · IEC:** [IEC 62548-1:2023+A1:2025](https://webstore.iec.ch/en/publication/110893) — PV dizi tasarımında aşırı akım koruması, arıza akımı, kablo ve ayırma sınırlarını kapsar.
- **S2 · Fronius:** [String fuses](https://manuals.fronius.com/html/4204101909/en.html) — String sigortasının modül maksimum seri sigorta sınırı ve inverter yuvasıyla uyumunu açıklar.
- **S3 · SMA:** [Sunny Tripower CORE1 Technical Data](https://manuals.sma.de/STP50-40/en-US/43470603.html) — Model bazlı DC giriş, kısa devre ve reverse-current sınırlarını verir.

## AEO, schema ve dönüşüm

- İlk ekranda “hangi durumda gerekir?” sorusuna doğrudan cevap.
- Canonical derleyicide `Article`, `FAQPage`, `BreadcrumbList`.
- `Product` veya `Offer` yok; amper, marka veya ürün satın alma önerisi üretilmiyor.
- Yüksek risk nedeniyle affiliate CTA kapalı.
- Dönüşüm: yetkili GES tasarımcısından istenecek string koruma koordinasyon dosyası.

## Yayın kabul listesi

- [ ] Her teknik iddia ilgili `S#` kaynağıyla doğrulandı.
- [ ] AFCI, izolasyon izleme, SPD ve string sigortasının görevleri karıştırılmıyor.
- [ ] Mevcut canonical içerikle görev çakışması bulunmuyor.
- [ ] Enerjili DC konnektör veya sigorta müdahalesi kullanıcıya yaptırılmıyor.
- [ ] İç bağlantılar routing envanterinde çalışıyor.
- [ ] Canonical build, sitemap ve ChatGPT Sites önizleme kapıları başarılı.

## Onay komutu

```text
/cms approve ges-string-sigortasi-ters-akim-maksimum-seri-sigorta
```

Komut canonical HTML, routing overlay ve ChatGPT Sites önizleme artifactını üretir. Zorunlu kontroller başarılı olmadan PR birleştirilmemelidir.
