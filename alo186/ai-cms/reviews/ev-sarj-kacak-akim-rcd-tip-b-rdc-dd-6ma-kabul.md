# ALO186 AI CMS insan inceleme paketi

## İçerik

- **Başlık:** EV Şarj Kaçak Akım Koruması: Tip B veya 6 mA RDC-DD
- **Canonical adayı:** `/haberler/ev-sarj-kacak-akim-rcd-tip-b-rdc-dd-6ma-kabul`
- **Birincil anahtar ifade:** `EV şarj kaçak akım rölesi Tip B`
- **Risk sınıfı:** `high`
- **Fırsat puanı:** **98/100**
- **AI CMS kalite hedefi:** **100/100**
- **Durum:** `review`

## Kullanıcı görevi

Mode 3 AC EV şarj noktasında düzgün DC artık akıma karşı korumanın Tip B RCD veya IEC 62955 RDC-DD ile doğru kurulduğunu ve saha testleriyle çalıştığını doğrulamak.

## Kaynak doğrulaması

| ID | Yayıncı | Kaynak | Erişim |
|---|---|---|---|
| S1 | IEC | IEC 60364-7-722:2018 — Supplies for electric vehicles | 2026-08-03 |
| S2 | IEC | IEC 62955:2018 — RDC-DD for mode 3 EV charging | 2026-08-03 |
| S3 | IEC | IEC 62423:2009 — Type F and Type B RCDs | 2026-08-03 |
| S4 | Schneider Electric Türkiye | EVlink Home dahili 6 mA RDC-DD ve haricî RCD gereği | 2026-08-03 |
| S5 | Schneider Electric Türkiye | EVlink Pro AC dahili 6 mA RDC-DD davranışı | 2026-08-03 |

## AEO, SEO ve kullanıcı faydası

- İlk ekranda bağımsız ve alıntılanabilir doğrudan cevap bulunur.
- 5 kaynak bağlı teknik bölüm ve 4 görünür SSS hazırlanmıştır.
- 7 doğrulanmış bağlamsal iç bağlantı eklenmiştir.
- Canonical derleyici `Article`, `FAQPage` ve `BreadcrumbList` üretmelidir.
- Kurumsal yazar `Organization` olmalıdır; `Person`, `Product` ve `Offer` kullanılmamalıdır.
- Birincil CTA kişisel verisiz kabul/ölçüm matrisi ve yetkin teknik ekibe teslim edilebilir kanıt dosyasıdır.
- Mevcut sistem bütün sınırları kanıtla geçiyorsa gereksiz ekipman veya yazılım satın alınmamalıdır.
- Tahmini en yüksek benzerlik `0.48`; en yakın rota `/haberler/kacak-akim-toplam-kacak-butcesi-istenmeyen-acma-teshisi`; fail-closed eşik `0,78`’dir.

## Güvenlik ve mevzuat sınırı

İçerik kullanıcıya enerjili pano, RCD, kontaktör veya EVSE iç devresinde müdahale yaptırmaz. Düzgün DC artık akım, açma süresi ve RDC-DD fonksiyon testleri yalnız uygun cihaz, üretici prosedürü ve yetkin ekip ile yapılmalıdır. Ürün serisi veya marka adına dayanarak koruma özelliği varsayılmaz; tam ürün referansı doğrulanır. Affiliate kapalıdır.

## İnsan onayı

```text
/cms approve ev-sarj-kacak-akim-rcd-tip-b-rdc-dd-6ma-kabul
```

AI ve bot yorumları onay sayılmaz. Onay sonrası canonical HTML, routing overlay ve ChatGPT Sites önizleme artifactı hazırlanır; ayrıca insan merge'i gerekir.
