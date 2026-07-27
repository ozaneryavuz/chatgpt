# ALO186 Yedek Güç Hesaplayıcısı

Tarayıcı içinde çalışan UPS, power station ve batarya ön değerlendirme aracı.

## İşlevler

- Cihaz bazlı sürekli yük hesabı
- Motorlu yükler için kalkış gücü kontrolü
- Hedef süreye göre gerekli nominal Wh kapasitesi
- Mevcut ürünün tahmini çalışma süresi
- LiFePO4, lityum, AGM/GEL ve kurşun-asit varsayımları
- Dönüşüm verimi, güvenli deşarj, yaşlanma ve kapasite rezervi
- Saf sinüs ve profesyonel projelendirme uyarıları
- Yerel taslak kaydı, kopyalama ve yazdırma/PDF
- İsteğe bağlı GA4 olayları

## Hesap yaklaşımı

Gerekli nominal enerji:

```text
nominal_Wh = (toplam_W × hedef_saat) / (verim × DoD × sağlık_katsayısı) × (1 + rezerv)
```

Tahmini çalışma süresi:

```text
saat = nominal_Wh × verim × DoD × sağlık_katsayısı × (1 - rezerv) / toplam_W
```

Kalkış gücü, toplam sürekli yüke en büyük tek cihazın ilave kalkış yükü eklenerek ön değerlendirilir. Eşzamanlı motor kalkışı, üç fazlı sistemler ve sabit tesisat profesyonel hesap gerektirir.

## Yayın hedefi

- Canlı rota: `https://www.alo186.com/hesaplama/yedek-guc`
- GitHub Pages: depo içindeki `alo186/` dizini yayımlandığında `/yedek-guc-hesaplayici/`
