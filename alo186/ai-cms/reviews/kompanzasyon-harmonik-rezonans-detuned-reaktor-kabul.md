# ALO186 AI CMS insan inceleme paketi

## İçerik

- **Başlık:** Kompanzasyonda Harmonik Rezonans ve Detuned Reaktör Kabulü
- **H1:** Kompanzasyon panosunda harmonik rezonans nasıl anlaşılır, detuned reaktör nasıl doğrulanır?
- **Canonical adayı:** `/haberler/kompanzasyon-harmonik-rezonans-detuned-reaktor-kabul`
- **Birincil anahtar ifade:** `kompanzasyon harmonik rezonans detuned reaktör`
- **Risk sınıfı:** `high`
- **Fırsat puanı:** **94/100**
- **AI CMS kalite hedefi:** **100/100**
- **Durum:** `review` — canonical HTML veya routing overlay henüz yok

## Kullanıcı görevi

Kompanzasyon panosunda tekrarlayan kondansatör, sigorta veya kontaktör arızalarının harmonik rezonans ve yanlış detuned reaktör koordinasyonundan kaynaklanıp kaynaklanmadığını ölçümle kanıtlamak.

## Doğrudan cevap

Kompanzasyon panosunda kondansatörlerin sık arızalanması, kademe sigortalarının açması veya reaktörlerin aşırı ısınması yalnız 'kondansatör kalitesi' sorunu değildir; şebeke kısa devre gücü, mevcut harmonikler, kondansatör kVAr'ı ve reaktör-kondansatör ayar frekansı paralel veya seri rezonans oluşturabilir. Kabul çalışması; kompanzasyon kapalı ve açıkken faz bazlı harmonik spektrum, kondansatör ve reaktör akımı, gerilim, sıcaklık, kademe geçişleri ve reaktif güç davranışını karşılaştırmalıdır. Detuned reaktör yüzdesi katalogdan tahmin edilmemeli; sistem empedansı ve üretici kombinasyonu ile doğrulanmalıdır.

## Kaynak doğrulaması

| ID | Yayıncı | Kaynak | Birincil | Erişim |
|---|---|---|---|---|
| S1 | IEC | IEC 61642:1997 — Harmoniklerden etkilenen endüstriyel AC şebekelerde filtre ve şönt kondansatör uygulaması | Evet | 2026-08-03 |
| S2 | IEC | IEC 63497:2026 — Shunt-connected active correction devices | Evet | 2026-08-03 |
| S3 | Schneider Electric | PowerLogic Harmonics Overview | Evet | 2026-08-03 |
| S4 | Schneider Electric | PowerLogic ION9000 — Harmonics | Evet | 2026-08-03 |

Kaynak özetleri içerik kaydında tutulur; her bölüm ve SSS yalnız ilgili `S#` kimliklerine dayanır. Erişim tarihi **3 Ağustos 2026**’dır.

## İçerik yapısı

- **Harmonik rezonans hangi belirtilerle kendini gösterir?** — kaynaklar: S1, S3, S4
- **Rezonans ölçüm planı nasıl kurulmalıdır?** — kaynaklar: S3, S4
- **Detuned reaktör ve kondansatör uyumu nasıl doğrulanır?** — kaynaklar: S1, S2
- **Detuned reaktör mü aktif harmonik filtre mi gerekir?** — kaynaklar: S1, S2
- **Kabul ve bakım dosyasında hangi kanıtlar bulunmalıdır?** — kaynaklar: S1, S2, S3, S4

## İç bağlantılar

- [Harmonik nedir?](/haberler/harmonik-nedir-thd-cihazlari-nasil-etkiler) — Temel harmonik ve THD kavramlarını açıklar.
- [Detuned reaktör ve aktif filtre farkı](/haberler/detuned-reaktor-aktif-harmonik-filtre-farki) — İki çözüm sınıfının görev ayrımını tamamlar.
- [Kompanzasyon panosu neden bozulur?](/haberler/kompanzasyon-panosu-reaktif-guc-neden-bozulur) — Genel arıza nedenlerini rezonans kabul çalışmasına bağlar.
- [Nötr akımı neden yüksek olur?](/haberler/notr-akimi-faz-akimindan-yuksek-neden-olur) — Üçüncü harmonikler ve dengesizlik etkisini tamamlar.
- [Faz dengesizliği](/haberler/faz-dengesizligi-faz-kaybi-motoru-nasil-etkiler) — Harmonik dışındaki faz bazlı ısınma ve koruma sorunlarını ayırır.
- [Elektrik panosunda termal kamera](/haberler/elektrik-panosunda-termal-kamera-kontrolu) — Kondansatör, reaktör, kontaktör ve bağlantı sıcaklıklarının kabulünü destekler.
- [Kurumsal ön değerlendirme](/kurumsal-elektrik-surekliligi-on-degerlendirme) — İşletme kompanzasyon ve harmonik ölçüm kapsamını profesyonel çalışmaya taşır.

## AEO, SEO ve yapılandırılmış veri

- İlk ekranda bağımsız anlaşılabilen doğrudan cevap bulunur.
- Title, meta description, H1 ve canonical birbirinden tutarlı ve kullanıcı görevi odaklıdır.
- Dört görünür SSS bulunur.
- Canonical derleyici `Article`, `FAQPage` ve `BreadcrumbList` üretmelidir.
- Yazar/üretici kimliği kurumsal `Organization` olmalıdır.
- `Person`, `ProfilePage`, `Product` ve `Offer` kullanılmamalıdır.
- Tahmini en yüksek mevcut içerik benzerliği `0.47`; en yakın rota `/haberler/detuned-reaktor-aktif-harmonik-filtre-farki`. Fail-closed eşik `0,78`’dir.

## Kullanıcı faydası ve dönüşüm

- **Birincil CTA:** Kişisel verisiz teknik kabul/kanıt dosyası hazırlama.
- **İkincil CTA:** İlgili ücretsiz ALO186 araçları ve resmî/kurumsal teknik değerlendirme.
- **Affiliate:** kapalıdır.
- Mevcut sistem ölçüm ve belgeyle yeterliyse satın almama sonucu korunur.

## Güvenlik sınırı

Bu içerik enerjili pano, sayaç, akım trafosu, şarj ünitesi, kompanzasyon kademesi veya topraklama tesisatına kullanıcı müdahalesi önermez. Ölçüm, ayar, devreye alma ve kabul işlemleri yetkin kişilerce; üretici talimatları, güncel standartlar ve saha risk değerlendirmesiyle yapılmalıdır. ALO186 bağımsız bilgilendirme platformudur; resmî kurum, EDAŞ, test laboratuvarı veya kabul mercii değildir.

## İnsan onayı

Teknik ve editoryal inceleme tamamlandıktan sonra PR konuşmasına yalnız yetkili repository kullanıcısı şu komutu eklemelidir:

```text
/cms approve kompanzasyon-harmonik-rezonans-detuned-reaktor-kabul
```

AI ve bot yorumları onay sayılmaz. Onay workflow’u canonical HTML, routing overlay ve ChatGPT Sites önizleme artifactını üretir; PR ayrıca insan merge’i olmadan canlıya çıkmaz.
