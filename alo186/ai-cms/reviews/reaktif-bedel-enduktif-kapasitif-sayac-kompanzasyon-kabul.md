# ALO186 AI CMS inceleme paketi — reaktif-bedel-enduktif-kapasitif-sayac-kompanzasyon-kabul

> Canonical yayına dahil edilmez; insan teknik incelemesi içindir.

## Durum

- State: **review**
- Risk: **legal**
- Kalite hedefi: **100/100**
- Tahmini benzerlik: **0.41** — `/haberler/kompanzasyon-panosu-reaktif-guc-neden-bozulur`
- Kelime: **826**

## SEO ve kullanıcı çıktısı

- Title: `Reaktif Bedel, Sayaç Endeksleri ve Kompanzasyon Kabulü`
- H1: `Reaktif bedel neden gelir, endüktif–kapasitif sayaç ve kompanzasyon nasıl kontrol edilir?`
- Canonical: `/haberler/reaktif-bedel-enduktif-kapasitif-sayac-kompanzasyon-kabul`
- Anahtar kelime: `reaktif bedel endüktif kapasitif sayaç`
- Doğrudan cevap: Önce güncel tarife kapsamı, aktif/reaktif endeksler, OBIS kodları, sayaç çarpanı ve CT/VT oranı doğrulanır; sonra P–Q–cos φ, kademe ve harmonik trendiyle teknik kök neden ayrılır.

## Bölümler

- **Reaktif bedel görüldüğünde ilk olarak ne doğrulanmalıdır?** — S1, S3, S4
- **Sayaçtaki RI/RC ve OBIS kodları nasıl eşleştirilir?** — S2, S3, S4
- **Endüktif veya kapasitif aşımın kök nedeni nasıl ayrılır?** — S1, S5
- **Kompanzasyon panosu onarım sonrası nasıl kabul edilir?** — S1, S2, S3, S5
- **Reaktif bedel itiraz ve kapanış dosyası neleri içermelidir?** — S1–S5

## Kaynaklar

- **S1 · EPDK** — [Elektrik Piyasası Tarifeleri Uygulama Usul ve Esasları](https://www.epdk.gov.tr/Detay/Icerik/3-17057/elektrik-piyasasi-tarifeleri-uygulama-usul-ve-esa)
- **S2 · IEC** — [IEC 62053-24:2020](https://webstore.iec.ch/en/publication/34533)
- **S3 · IEC** — [IEC 62056-6-1:2023](https://webstore.iec.ch/en/publication/67916)
- **S4 · Enerjisa** — [Reaktif Enerji / Bedel nedir?](https://www.enerjisa.com.tr/tr/sikca-sorulan-sorular/fatura-kalemleri/reaktif-enerji-bedel-nedir)
- **S5 · Schneider Electric** — [PowerLogic PFC Manual](https://www.se.com/us/en/download/document/BQT2027101/)

## İç bağlantılar

- [Kompanzasyon panosu arızaları](/haberler/kompanzasyon-panosu-reaktif-guc-neden-bozulur)
- [Harmonik ve THD](/haberler/harmonik-nedir-thd-cihazlari-nasil-etkiler)
- [Detuned reaktör ve aktif filtre](/haberler/detuned-reaktor-aktif-harmonik-filtre-farki)
- [Sayaç arızası ve fatura itirazı](/haberler/elektrik-sayaci-arizali-mi-fatura-itirazi)
- [Sayaç değişimi endeks kontrolü](/haberler/elektrik-sayaci-degisti-eski-yeni-endeks-fatura-kontrolu)
- [Fatura analizi](/fatura-analizi)
- [Elektrik Portalı](/elektrik-portali)

## Yapılandırılmış veri ve dönüşüm

- `Article`, `FAQPage`, `BreadcrumbList`; `Organization` yazarlığı.
- Kişisel verisiz fatura–sayaç–P/Q–kademe kabul matrisi CTA’sı.
- `Person`, `Product`, `Offer`, fiyat, stok ve affiliate kapalı.
- Güncel EPDK metni doğrulanmadan sabit tarife oranı ilan edilmez; mühürlü sayaç ve enerjili pano müdahalesi önerilmez.

## İnsan onay komutu

```text
/cms approve reaktif-bedel-enduktif-kapasitif-sayac-kompanzasyon-kabul
```

Onay akışı kaynak, link, kalite, kanibalizasyon ve güvenlik kapılarını yeniden çalıştırmalıdır.
