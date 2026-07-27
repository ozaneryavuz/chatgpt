# ALO186 Elektrik Faturası Zekâ Merkezi

Bu klasör, `alo186.com/fatura-analizi` için yayınlanmaya hazır bağımsız bir ön yüz MVP’sidir.

## İçerik

- `index.html`: SEO, AEO, resmî kaynaklar ve kullanıcı arayüzü
- `styles.css`: responsive, mobil öncelikli tasarım
- `app.js`: tarayıcı içi tüketim analizi ve 2026 SKTT risk motoru

## Doğrulanmış 2026 kuralları

- Mesken SKTT limiti: **4.000 kWh/yıl**
- Kamu/özel hizmetler, sanayi ve aydınlatma: **15.000 kWh/yıl**
- Tarımsal faaliyetler: **150.000.000 kWh/yıl**
- Serbest tüketici limiti: **500 kWh/yıl**
- Limit aşımından sonra uygulama: aşım ayını takip eden üçüncü ayın ilk günü

Kaynaklar sayfanın altındaki resmî EPDK bağlantılarında gösterilir.

## Güvenlik ve gizlilik

- Girdiler yalnız tarayıcıda işlenir.
- T.C. kimlik, adres, tesisat veya sözleşme hesap numarası istenmez.
- Araç kesin TL fatura hesabı veya resmî tarife kararı vermez.
- Kesin hesap için EPDK’nın resmî hesaplama modülüne yönlendirir.

## Entegrasyon

Mevcut siteye aşağıdaki URL ile eklenmesi önerilir:

`/fatura-analizi`

Dosyalar aynı klasörde sunulduğunda ek derleme bağımlılığı olmadan çalışır.
