# ALO186 Kullanıcı Fayda Araçları v1

Bu paket, ALO186 için fatura analizine benzer şekilde çalışan, mobil uyumlu ve kişisel veri istemeyen dört yeni araç ile bir hesaplama merkezi içerir.

## Rotalar

- `/hesaplama/` — araç merkezi
- `/hesaplama/ups-suresi/` — UPS / power station süre ve kapasite hesabı
- `/hesaplama/ev-sarj-suresi/` — EV şarj süresi, enerji, maliyet ve hat akımı
- `/hesaplama/kablo-gerilim-dusumu/` — DC, monofaze ve trifaze gerilim düşümü ön hesabı
- `/hesaplama/kesinti-hazirlik-plani/` — ev/site/işletme/otel kesinti planı
- `/fatura-analizi` — mevcut Elektrik Faturası Zekâ Merkezi

## Güvenlik sınırı

- Kablo aracı yalnız gerilim düşümü ön kontrolü yapar; akım taşıma, kısa devre, döşeme ve koruma hesabı yapmaz.
- EV aracı sabit şarj kurulumuna uygunluk onayı vermez.
- UPS aracı gerçek cihaz tüketimi, sıcaklık, batarya yaşı ve kalkış akımına göre değişebilen yaklaşık sonuç verir.
- Acil durumda 112, şebeke arızasında 186 kullanılmalıdır.

## Teknik yapı

- Haricî JavaScript bağımlılığı yoktur.
- Hesaplar kullanıcı tarayıcısında yapılır.
- Ortak hesap motoru `calc-core.js` içindedir.
- Ortak tasarım `styles.css`, olay izleme yardımcıları `common.js` içindedir.
- Sonuçlar kopyalanabilir ve tarayıcının yazdır/PDF özelliğiyle kaydedilebilir.

## Analytics

Araçlar `window.dataLayer` mevcutsa özel olayları otomatik yollar. Olay listesi `integration/analytics-events.md` dosyasındadır.

## Test

```bash
node alo186/tests/test_calc_core.js
```

## Yayın kontrolü

1. Canonical host kararını doğrulayın (`www` veya kök alan adı).
2. Sitemap girişlerini mevcut sitemap'e ekleyin.
3. Hesaplayıcılar menü bağlantısını yayınlayın.
4. Search Console üzerinden yeni rotaları denetleyin.
5. Profesyonel hizmet CTA rotalarının canlı sitede bulunduğunu doğrulayın.
