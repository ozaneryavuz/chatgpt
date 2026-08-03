# Teknik inceleme paketi — GES rapid shutdown ve itfaiyeci acil ayırma sistemi nasıl kabul edilir?

## Karar özeti

- **Fırsat puanı:** 97/100
- **Risk sınıfı:** `high`
- **Canonical adayı:** `/haberler/ges-rapid-shutdown-acil-ayirma-itfaiyeci-kabul-testi`
- **En yakın mevcut içerik:** `/haberler/ges-elektrik-kesintisinde-calisir-mi`
- **Tahmini en yüksek benzerlik:** `0.40`
- **Çakışma eşiği:** `0.78`
- **Ticari durum:** Affiliate, Product, Offer, fiyat, stok ve garanti kapalıdır.

## Kullanıcı niyeti

Rapid shutdown veya itfaiyeci acil ayırma işlevi bulunan PV sisteminde tetikleyiciden modül seviyesine kadar bütün zincirin çalıştığını, DC iletken gerilimi ve durum geri bildirimiyle güvenli biçimde doğrulamak.

## Mevcut içerikten ayrışma

Mevcut GES kesintide çalışma, inverter gerilim hatası ve clipping sayfaları şebeke/üretim davranışını açıklar. Bu kayıt tetikleyiciden modül anahtarına kadar rapid shutdown zinciri, DC gerilim-zaman kanıtı, iletişim kaybı, etiket ve yeniden başlatma kabulüne odaklanır.

## Kaynak doğrulaması

IEC 62548-1, IEC 60364-7-712 ve 6 Mayıs 2026 tarihli IEC 63257 ile SMA ve SolarEdge üretici güvenlik dokümanları kullanıldı. Rapid shutdown Türkiye’de tüm tesisler için evrensel zorunluluk olarak sunulmamıştır.

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

Yüksek DC gerilim ölçümü yalnız yetkin ekip, uygun cihaz ve üretici prosedürüyle yapılır. AC ayırma veya inverter kapanması gerilimsizlik kanıtı sayılmaz.

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
/cms approve ges-rapid-shutdown-acil-ayirma-itfaiyeci-kabul-testi
```

Onay; canonical HTML, routing overlay ve ChatGPT Sites önizleme paketini üretmelidir. Zorunlu kalite kontrolleri geçmeden merge veya canlı yayın yapılmamalıdır.
