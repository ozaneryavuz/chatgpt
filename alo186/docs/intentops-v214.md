# ALO186 IntentOps v214

Tarih: 2 Ağustos 2026

## Amaç

ALO186 içerik büyümesini yalnız yeni sayfa sayısıyla değil; kullanıcı görevi, kaynak güveni, çakışma riski, iç bağlantı gücü, ölçülebilir dönüşüm ve ticari uygunlukla yönetmek.

## İşletim zinciri

```text
fırsat kaydı
→ ağırlıklı potansiyel skoru
→ intent çakışma kontrolü
→ yayın eşiği
→ kaynak tarihi ve şema denetimi
→ iç bağlantı ve güvenlik sınırı
→ dönüşüm olayı
→ yayın sonrası rapor
```

## Puanlama modeli

- Arama talebi: %24
- Görev aciliyeti: %18
- Ticari uyum: %16
- ALO186 uzmanlık uyumu: %16
- Net cevaplanabilirlik: %14
- İç bağlantı uyumu: %12

Yayın eşiği 72 puandır. Aynı görevi hedefleyen içeriklerde Jaccard benzerliği 0,78 üzerine çıkarsa yeni canonical rota fail-closed durur.

## Kalite kapıları

Yayımlanmış araçlarda aşağıdaki sözleşmeler denetlenir:

- doğrudan cevap,
- `FAQPage` ve `BreadcrumbList`,
- kaynak doğrulama tarihi,
- en az beş benzersiz iç bağlantı,
- görünür güvenlik sınırı,
- tanımlı dönüşüm olayları,
- `Product`, `Offer` ve `AggregateRating` yasağı.

Eksik dönüşüm olayı ve görünür SSS, raporda iyileştirme borcu olarak yüzeye çıkar. Canonical, kaynak tarihi, güvenlik sınırı, çakışma veya ticari şema ihlali yayın engelidir.

## İlk öncelik sırası

1. Ev enerji depolama kritik yük planı
2. Otel güç kalitesi kayıp hesaplayıcısı
3. BESS ve VPP gelir hazırlığı kontrolü

Bu üç aday; ALO186 uzmanlık avantajı, yüksek ticari değer ve mevcut içerik kümelerine güçlü iç bağlantı potansiyeli nedeniyle sıradaki üretim kuyruğudur.

## Beklenen etki

- içerik kanibalizasyonunun azalması,
- mevzuat ve standart kaynaklarının eskimesinin görünür olması,
- her yeni sayfanın ölçülebilir kullanıcı işi tamamlaması,
- affiliate ve kurumsal hizmet yollarının konuya göre ayrılması,
- yeni içerik üretiminde karar kalitesinin kişiye bağlı olmaktan çıkması.
