# ALO186 AI CMS insan inceleme paketi

## İçerik

- **Başlık:** UPS Çıkışı Kısa Devre Akımı ve Kesici Selektivite Kabulü
- **Canonical adayı:** `/haberler/ups-cikis-kisa-devre-akimi-selektivite-kesici-kabul`
- **Birincil anahtar ifade:** `UPS kısa devre selektivite testi`
- **Risk sınıfı:** `high`
- **Fırsat puanı:** **97/100**
- **AI CMS kalite hedefi:** **100/100**
- **Durum:** `review`

## Kullanıcı görevi

UPS çıkışındaki alt devre arızasında doğru kesicinin, UPS kapanmadan veya sağlıklı kritik yükleri kesmeden arızayı temizleyebildiğini bütün çalışma modlarında kanıtlamak.

## Kaynak doğrulaması

| ID | Yayıncı | Kaynak | Erişim |
|---|---|---|---|
| S1 | IEC | IEC 62040-3:2021 — UPS performance and test requirements | 2026-08-03 |
| S2 | Schneider Electric | Galaxy PW 60 kVA UPS technical specifications | 2026-08-03 |
| S3 | Schneider Electric | Galaxy VS 400 V technical specifications — short-circuit capability | 2026-08-03 |
| S4 | Schneider Electric | Selectivity, Cascading and Coordination Guide 2025 | 2026-08-03 |
| S5 | Eaton | Low-voltage switchgear fundamentals — selective coordination | 2026-08-03 |

## AEO, SEO ve kullanıcı faydası

- İlk ekranda bağımsız ve alıntılanabilir doğrudan cevap bulunur.
- 5 kaynak bağlı teknik bölüm ve 4 görünür SSS hazırlanmıştır.
- 7 doğrulanmış bağlamsal iç bağlantı eklenmiştir.
- Canonical derleyici `Article`, `FAQPage` ve `BreadcrumbList` üretmelidir.
- Kurumsal yazar `Organization` olmalıdır; `Person`, `Product` ve `Offer` kullanılmamalıdır.
- Birincil CTA kişisel verisiz kabul/ölçüm matrisi ve yetkin teknik ekibe teslim edilebilir kanıt dosyasıdır.
- Mevcut sistem bütün sınırları kanıtla geçiyorsa gereksiz ekipman veya yazılım satın alınmamalıdır.
- Tahmini en yüksek benzerlik `0.52`; en yakın rota `/haberler/ups-bakim-bypass-geri-besleme-kilitleme-kabul-testi`; fail-closed eşik `0,78`’dir.

## Güvenlik ve mevzuat sınırı

İçerik kullanıcıya canlı UPS çıkışında kısa devre oluşturmayı, korumayı köprülemeyi veya kesici ayarını deneme-yanılmayla değiştirmeyi önermez. Hesap, üretici koordinasyon tablosu ve ikincil enjeksiyon önceliklidir; gerekiyorsa kontrollü saha testi risk analizi, kritik yük geri dönüş planı ve yetkin ekiple yapılmalıdır. Affiliate kapalıdır.

## İnsan onayı

```text
/cms approve ups-cikis-kisa-devre-akimi-selektivite-kesici-kabul
```

AI ve bot yorumları onay sayılmaz. Onay sonrası canonical HTML, routing overlay ve ChatGPT Sites önizleme artifactı hazırlanır; ayrıca insan merge'i gerekir.
