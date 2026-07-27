# ALO186 Tam Türkiye EDAŞ Arama Motoru

81 il, 973 ilçe, 21 elektrik dağıtım şirketi ve temel işlem/güvenlik niyetlerini tek arama kutusunda birleştirir.

## Özellikler

- İl, ilçe ve şirket adıyla arama
- Türkçe karakter kullanmadan arama (`mugla`, `umraniye`)
- Şirket kısaltmaları ve eski/yaygın adlar
- İstanbul Avrupa/Anadolu yakası ilçe ayrımı
- 112, 186 ve iç tesisat niyetlerinin ayrıştırılması
- Yazım hatası toleransı
- Klavye ile sonuç seçimi
- Sıfır sonuç ve eksik bölge bildirme akışı
- Kişisel veri toplamadan tarayıcı içi arama
- İlçe verisi alınamazsa 81 il ve 21 şirket için yerel yedek çalışma

## İdari veri kaynağı

İl ve ilçe adları TurkiyeAPI v2 sürümlenmiş statik veri setinden alınır:

- `https://api.turkiyeapi.dev/v2/datasets/2025/provinces.json`
- `https://api.turkiyeapi.dev/v2/datasets/2025/districts.json`

TurkiyeAPI açık kaynak ve MIT lisanslıdır. Veri tarayıcıda 30 gün önbelleğe alınır; yüksek frekanslı polling yapılmaz.

Elektrik dağıtım bölgesi eşleştirmeleri `companies.js` içindeki ALO186 editoryal kataloğunda sürümlenir. İstanbul için ilçe bazlı BEDAŞ/AYEDAŞ ayrımı uygulanır.

## Yayın rotası

Önerilen canlı rota:

```text
/edas-bul
```

Mevcut `/elektrik-kesintisi` sayfasındaki sınırlı statik arama, doğrulama sonrasında bu motorla değiştirilebilir veya bu modüle yönlendirilebilir.

## Test

```bash
node alo186/tests/test_turkiye_search.js
```

Testler:

- 81 ilin dağıtım kapsamı
- ADM/GDZ gibi il eşleştirmeleri
- İstanbul ilçe/yaka ayrımı
- Türkçe normalizasyon
- şirket alias eşleştirmesi
- güvenlik niyeti
- bulanık arama

## GA4 olayları

- `location_dataset_loaded`
- `location_dataset_failed`
- `location_search_results_shown`
- `location_search_zero_result`
- `location_quick_query_clicked`
- `location_result_action_clicked`

## Güvenlik

- Elektrik çarpması, yangın, duman, kıvılcım ve düşmüş kablo sorguları 112 öncelikli sonuç verir.
- Araç arıza kaydı almaz ve resmî kurum gibi davranmaz.
- Kullanıcıdan açık adres, abonelik veya kimlik bilgisi istemez.
