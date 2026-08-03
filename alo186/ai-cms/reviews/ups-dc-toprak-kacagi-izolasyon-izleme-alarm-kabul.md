# Teknik inceleme paketi — UPS akü DC toprak kaçağı alarmı nasıl doğrulanır ve kabul edilir?

## Karar özeti

- **Fırsat puanı:** 96/100
- **Risk sınıfı:** `high`
- **Canonical adayı:** `/haberler/ups-dc-toprak-kacagi-izolasyon-izleme-alarm-kabul`
- **En yakın mevcut içerik:** `/haberler/ups-akusu-ne-zaman-degisir`
- **Tahmini en yüksek benzerlik:** `0.38`
- **Çakışma eşiği:** `0.78`
- **Ticari durum:** Affiliate, Product, Offer, fiyat, stok ve garanti kapalıdır.

## Kullanıcı niyeti

UPS veya haricî akü sisteminde DC ground fault/toprak kaçağı alarmının gerçek izolasyon bozulmasını mı, ölçüm/bağlantı hatasını mı gösterdiğini; IMD ayarı, alarm zinciri ve kontrollü kaynak ayrımıyla kanıtlamak.

## Mevcut içerikten ayrışma

Mevcut UPS akü değişim ve çalışma süresi sayfaları kapasite/yaş kararını ele alır. Bu kayıt DC sistem mimarisi, IMD seçimi, alarm zinciri, kutup yönü, kontrollü test ve izolasyon arızası kök neden kabulüne odaklanır.

## Kaynak doğrulaması

IEC 62040-1 ve IEC 61557-8 ile Bender IMD ve Schneider Galaxy UPS alarm giriş dokümanları kullanıldı. Üretici ürünleri evrensel seçim önerisi değil, uygulama sınırı ve alarm mimarisi örneği olarak işlendi.

Kaynaklara erişim tarihi: **3 Ağustos 2026**. İçerikte yalnız `S1–S5` kaynaklarının kayıtlı factSummary kapsamı kullanılmıştır. Kaynaklar yayımdan önce URL, yayın/sürüm ve ürün kapsamı bakımından yeniden kontrol edilmelidir.

## Somut kullanıcı çıktısı

Kullanıcı, teknik ekibe aktarılabilir bir kabul matrisi ve geçti-kaldı kaydı oluşturabilir. CTA; kişisel veri, canlı erişim anahtarı, fiyat teklifi veya otomatik satın alma toplamaz.

## AEO / SEO sözleşmesi

- İlk ekranda bağımsız doğrudan cevap
- 5 teknik bölüm ve 4 görünür SSS
- 7 doğrulanmış iç bağlantı
- Benzersiz title, description, H1 ve canonical
- `Article`, `FAQPage`, `BreadcrumbList`
- `Organization` yazarlığı
- Tarihli kaynak–iddia zinciri
- `index,follow,max-image-preview:large`
- Sistem yeterliyse satın almama sonucu

## Güvenlik incelemesi

Canlı DC baranın kısa devre edilmesi, rastgele akü stringi ayırma ve bilinmeyen kutbun toprağa bağlanması yasaklanmıştır; test yalnız kontrollü direnç/öz-test ve yetkin ekip ile yapılır.

## İnsan inceleme kontrolü

- [ ] Teknik ifadeler proje ve ürün kapsamına uygun.
- [ ] Her iddia doğru `S#` kaynağına bağlı.
- [ ] İç bağlantıların tamamı routing envanterinde mevcut.
- [ ] Başlık ve doğrudan cevap mevcut içerikle aynı görevi tekrar etmiyor.
- [ ] Enerjili ekipman üzerinde kullanıcı müdahalesi önerilmiyor.
- [ ] Ülke/mevzuat zorunluluğu kanıtsız genellenmiyor.
- [ ] CTA kişisel verisiz ve ticari baskısız.
- [ ] Canonical, yapılandırılmış veri ve mobil önizleme doğrulandı.

## Onay komutu

```text
/cms approve ups-dc-toprak-kacagi-izolasyon-izleme-alarm-kabul
```

Onay; canonical HTML, routing overlay ve ChatGPT Sites önizleme paketini üretmelidir. Zorunlu kalite kontrolleri geçmeden merge veya canlı yayın yapılmamalıdır.
