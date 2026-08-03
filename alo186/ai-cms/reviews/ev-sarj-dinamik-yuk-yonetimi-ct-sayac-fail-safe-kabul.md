# Teknik inceleme paketi — EV şarj dinamik yük yönetimi CT yönü ve fail-safe nasıl test edilir?

## Karar özeti

- **Fırsat puanı:** 98/100
- **Risk sınıfı:** `high`
- **Canonical adayı:** `/haberler/ev-sarj-dinamik-yuk-yonetimi-ct-sayac-fail-safe-kabul`
- **En yakın mevcut içerik:** `/haberler/ev-sarjinda-dinamik-yuk-yonetimi`
- **Tahmini en yüksek benzerlik:** `0.49`
- **Çakışma eşiği:** `0.78`
- **Ticari durum:** Affiliate, Product, Offer, fiyat, stok ve garanti kapalıdır.

## Kullanıcı niyeti

Bir veya çoklu wallbox tesisinde dinamik yük yönetiminin ana bağlantı gücünü aşmadan çalıştığını; CT/sayaç faz-yön eşleşmesi, güç sınırı, iletişim kaybı ve güvenli fallback senaryolarıyla kanıtlamak.

## Mevcut içerikten ayrışma

Mevcut dinamik yük yönetimi rehberi kavramı ve faydayı açıklar. Bu kayıt yalnızca CT faz-yön eşleşmesi, sayaç sınırı, setpoint–gerçek güç, yük adımı ve haberleşme kaybı fail-safe kabulünü kanıtlar.

## Kaynak doğrulaması

IEC EV tesis ve şarj ekipmanı standartları ile OCA’nın OSCP/OCPP ve OCPP 1.6 sertifikasyon sayfaları kullanıldı. OCPP desteği saha performansı yerine geçmez; bu ayrım metinde korunmuştur.

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

CT sekonderinin açık devre bırakılması, enerjili panoya kullanıcı müdahalesi ve koruma sınırının kanıtsız büyütülmesi yasaklanmıştır.

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
/cms approve ev-sarj-dinamik-yuk-yonetimi-ct-sayac-fail-safe-kabul
```

Onay; canonical HTML, routing overlay ve ChatGPT Sites önizleme paketini üretmelidir. Zorunlu kalite kontrolleri geçmeden merge veya canlı yayın yapılmamalıdır.
