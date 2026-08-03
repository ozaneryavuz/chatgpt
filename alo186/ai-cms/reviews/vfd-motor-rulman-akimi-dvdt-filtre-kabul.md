# ALO186 AI CMS insan inceleme paketi

## İçerik

- **Başlık:** VFD Motor Rulman Akımı ve dv/dt Kabul Rehberi
- **H1:** İnverter motorunda rulman akımı ve dv/dt riski nasıl kanıtlanır?
- **Canonical adayı:** `/haberler/vfd-motor-rulman-akimi-dvdt-filtre-kabul`
- **Birincil anahtar ifade:** `VFD motor rulman akımı dv dt filtre`
- **Risk sınıfı:** `high`
- **Fırsat puanı:** **92/100**
- **AI CMS kalite hedefi:** **100/100**
- **Durum:** `review` — canonical HTML veya routing overlay henüz yok

## Kullanıcı görevi

VFD ile çalışan motorda rulman hasarı, izolasyon stresi veya EMC belirtisinin kaynağını ölçerek; kablo, bonding, filtre ve yatak koruması kararını kanıtlamak.

## Doğrudan cevap

VFD’li motorda rulman arızası görüldüğünde yalnız rulman markasını veya sürücüyü değiştirmek yeterli teşhis değildir. Doğru kabul dosyası; sürücü modeli ve anahtarlama ayarını, motorun converter-duty uygunluğunu, kablo tipi ve uzunluğunu, ekranın 360 derece sonlandırılmasını, eşpotansiyel bonding’i, motor terminalindeki gerilim kenarlarını ve şaft/rulman akımı belirtilerini birlikte kaydeder. Ölçüm ve üretici sınırları kök nedeni doğruluyorsa dv/dt veya sinüs filtre, common-mode çözümü, yalıtılmış yatak ya da şaft topraklama elemanı seçilir; mevcut kurulum yeterliyse gereksiz ekipman eklenmez.

## Mevcut içerikten görev ayrımı

Mevcut inverter alarmı ve klasik harmonik içeriklerinden farklı olarak motor terminali dv/dt, common-mode dönüş yolu, şaft/rulman akımı ve çıkış çözümü kabulüne odaklanır.

Tahmini en yüksek başlık/H1 benzerliği: **0.240** — en yakın rota: `/haberler/harmonik-nedir-thd-cihazlari-nasil-etkiler`. Fail-closed AI CMS doğrulaması gerçek envanter üzerinde yeniden hesaplar; `0,78` veya üzeri benzerlikte onay durmalıdır.

## Bölümler ve kaynak bağı

- **Rulman izi, motor sesi veya sürücü alarmı tek başına neden yeterli değildir?** — S1, S4, S5
- **VFD–motor–kablo uyum matrisi hangi alanları içermelidir?** — S1, S3
- **Bonding ve motor kablosu ekranı neden rulman akımı kararından önce kontrol edilir?** — S2, S3, S5
- **Şaft gerilimi, rulman akımı ve motor terminali nasıl ölçülür?** — S1, S4, S5
- **dv/dt filtresi, sinüs filtresi, yalıtılmış yatak veya şaft topraklama nasıl seçilir?** — S1, S2, S3, S4, S5

## Kaynak doğrulaması

| Ref | Yayıncı | Kaynak | Erişim | Birincil |
|---|---|---|---|---|
| S1 | IEC | IEC TS 60034-25:2022 — AC electrical machines used in power drive systems | 2026-08-03 | Evet |
| S2 | IEC | IEC 61800-3:2022 — EMC requirements for power drive systems | 2026-08-03 | Evet |
| S3 | IEC | IEC 61800-5-1:2022 — Safety requirements for power drive systems | 2026-08-03 | Evet |
| S4 | ABB | Baldor-Reliance shaft grounded motors | 2026-08-03 | Evet |
| S5 | ABB | RPM AC Inverter Duty motors | 2026-08-03 | Evet |

Bütün teknik ve hukukî iddialar yalnız içerik kaydındaki `factSummary` ve ilgili `S#` kaynak referanslarına dayanmalıdır. Evrensel eşik, garanti, fiyat, stok veya resmî onay iddiası eklenmemelidir.

## İç bağlantılar

- `/haberler/inverter-dusuk-voltaj-alarmi-neden-verir` — DC besleme ve düşük gerilim sorununu motor çıkış etkilerinden ayırır.
- `/haberler/faz-dengesizligi-faz-kaybi-motoru-nasil-etkiler` — Şebeke tarafı motor ısınma nedenlerini VFD çıkışından ayırır.
- `/haberler/harmonik-nedir-thd-cihazlari-nasil-etkiler` — Giriş harmonikleri ile motor terminali dv/dt/common-mode görevini ayırır.
- `/haberler/detuned-reaktor-aktif-harmonik-filtre-farki` — Şebeke harmonik filtresi ile VFD çıkış filtresi karışıklığını önler.
- `/haberler/notr-akimi-faz-akimindan-yuksek-neden-olur` — Tesis nötr harmonik problemini motor çıkış akımından ayırır.
- `/haberler/elektrik-panosunda-termal-kamera-kontrolu` — Sürücü ve bağlantı ısınmasının güvenli bakım kanıtını tamamlar.
- `/kurumsal-elektrik-surekliligi-on-degerlendirme` — Motor, VFD ve güç kalitesi için profesyonel ölçüm kapsamına geçiş sağlar.

## AEO / SEO ve yapılandırılmış veri

- benzersiz title, meta description, H1 ve canonical adayı;
- ilk ekranda bağımsız doğrudan cevap;
- beş kaynak bağlı bölüm ve dört görünür SSS;
- kurumsal `Organization` yazarlığı;
- canonical derleyicide `Article`, `FAQPage` ve `BreadcrumbList`;
- `Product`, `Offer`, `Person` ve `ProfilePage` yasağı;
- kaynak erişim tarihi ve görünür atıf zinciri;
- kullanıcıya teslim edilebilir kontrol, kanıt veya kabul dosyası.

## Güvenlik ve dönüşüm sınırı

Bu içerik `high` risk sınıfındadır. Affiliate ve ürün satın alma CTA’sı kapalıdır. Enerjili sürücü/motor terminallerinde osiloskop, şaft gerilimi veya common-mode ölçümü kullanıcı işlemi olarak sunulamaz. Dönüşüm çağrısı; VFD–motor–kablo matrisi, ölçüm/kabul dosyası ve yetkili profesyonel ön değerlendirmedir.

## İnsan onayı

Teknik içerik, kaynak, görev ayrımı, iç bağlantılar ve güvenlik sınırı kabul edilirse PR konuşmasına tam olarak şu yorum eklenmelidir:

```text
/cms approve vfd-motor-rulman-akimi-dvdt-filtre-kabul
```

AI veya otomasyon bu komutu veremez. Onay sonrasında canonical HTML, routing overlay ve ChatGPT Sites önizleme artifactı oluşur; zorunlu kontroller geçmeden merge edilmemelidir.
