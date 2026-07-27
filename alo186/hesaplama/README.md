# ALO186 Elektrik Hesaplama Merkezi

Bu dizin, kişisel veri istemeden tarayıcı içinde çalışan kullanıcı fayda araçlarını içerir.

## Araçlar

- `/hesaplama/ups-suresi/` — UPS ve power station süre/kapasite hesabı
- `/hesaplama/ev-sarj-suresi/` — EV şarj süresi, enerji, maliyet ve akım
- `/hesaplama/kablo-gerilim-dusumu/` — monofaze/trifaze gerilim düşümü ön hesabı
- `/hesaplama/kesinti-hazirlik-plani/` — ev/site/işletme/otel kontrol listesi

## Ortak dosyalar

- `styles.css` — responsive tasarım
- `calc-core.js` — deterministik hesap fonksiyonları
- `common.js` — analytics, formatlama, kopyalama ve yazdırma yardımcıları
- `tests/test_calc_core.js` — Node.js birim testleri

## Test

```bash
node alo186/hesaplama/tests/test_calc_core.js
```

## Canlı entegrasyon

1. `hesaplama` dizinini site kökünde `/hesaplama/` rotasına yayınlayın.
2. Üst menü ve ana sayfadan `/hesaplama/` bağlantısı verin.
3. Sitemap'e aşağıdaki URL'leri ekleyin:
   - `https://www.alo186.com/hesaplama/`
   - `https://www.alo186.com/hesaplama/ups-suresi/`
   - `https://www.alo186.com/hesaplama/ev-sarj-suresi/`
   - `https://www.alo186.com/hesaplama/kablo-gerilim-dusumu/`
   - `https://www.alo186.com/hesaplama/kesinti-hazirlik-plani/`
4. Canonical host kök alan adı olacaksa dosyalardaki `www` adreslerini topluca güncelleyin.
5. GA4'te şu olayları izleyin: `ups_calculation_completed`, `ev_calculation_completed`, `voltage_drop_completed`, `outage_plan_generated`, `outage_plan_saved`.

## Güvenlik sınırları

- Kablo aracı yalnız gerilim düşümü ön kontrolü yapar; akım taşıma, kısa devre, döşeme ve koruma hesabı yapmaz.
- EV aracı sabit şarj kurulumuna uygunluk onayı vermez.
- UPS aracı gerçek tüketim, sıcaklık, batarya yaşı ve kalkış akımına bağlı yaklaşık sonuç verir.
- Can güvenliği tehlikesinde 112; şebeke arızasında 186 kullanılmalıdır.
