# ALO186 AI CMS insan inceleme paketi

## İçerik

- **Başlık:** Topraklamada Dokunma ve Adım Gerilimi Ölçüm Kabul Dosyası
- **H1:** Topraklama direnci düşük olsa bile dokunma ve adım gerilimi neden ölçülmelidir?
- **Canonical adayı:** `/haberler/topraklama-dokunma-adim-gerilimi-olcum-kabul-dosyasi`
- **Birincil anahtar ifade:** `dokunma gerilimi adım gerilimi ölçümü`
- **Risk sınıfı:** `high`
- **Fırsat puanı:** **92/100**
- **AI CMS kalite hedefi:** **100/100**
- **Durum:** `review` — canonical HTML veya routing overlay henüz yok

## Kullanıcı görevi

Trafo merkezi, jeneratör sahası, GES, EV şarj tesisi veya geniş işletmede topraklama direnci tek başına yeterli olmadığında dokunma ve adım gerilimi güvenliğini ölçüm ve proje verileriyle doğrulamak.

## Doğrudan cevap

Topraklama direncinin düşük çıkması, arıza anında her noktada güvenli dokunma ve adım gerilimi oluşacağını tek başına kanıtlamaz. Güvenlik; arıza akımının büyüklüğü ve süresi, akımın toprak ve metal yollar arasında bölünmesi, topraklama ağı geometrisi, yüzey özdirenci, eşpotansiyel bağlantılar ve kişinin aynı anda temas edebileceği noktalarla belirlenir. Kabul dosyası; toprak özdirenci, ağ empedansı, süreklilik, arıza süresi, dokunma-adım gerilimi ölçümü veya doğrulanmış hesap, yüzey tabakası ve kritik metal parçaların eşpotansiyel bağlantısını birlikte göstermelidir.

## Kaynak doğrulaması

| ID | Yayıncı | Kaynak | Birincil | Erişim |
|---|---|---|---|---|
| S1 | IEEE Standards Association | IEEE 81-2025 — Ground resistivity, ground impedance and earth surface potential measurements | Evet | 2026-08-03 |
| S2 | IEC | IEC 60364-4-41:2005+AMD1:2017 CSV — Protection against electric shock | Evet | 2026-08-03 |
| S3 | IEC | IEC 61936-1:2021 CMV — Power installations exceeding 1 kV AC | Evet | 2026-08-03 |
| S4 | IEEE Power & Energy Society | Testing and application of crushed aggregate for a resistive substation surface layer | Evet | 2026-08-03 |

Kaynak özetleri içerik kaydında tutulur; her bölüm ve SSS yalnız ilgili `S#` kimliklerine dayanır. Erişim tarihi **3 Ağustos 2026**’dır.

## İçerik yapısı

- **Neden yalnız topraklama direnci yeterli değildir?** — kaynaklar: S1, S2, S3
- **Dokunma ve adım gerilimi nasıl ölçülür veya hesaplanır?** — kaynaklar: S1, S3
- **Eşpotansiyel bağlantı ve süreklilik nasıl doğrulanır?** — kaynaklar: S1, S2, S4
- **Yüzey malzemesi ve saha geometrisi güvenliği nasıl etkiler?** — kaynaklar: S1, S3, S4
- **Kabul dosyası hangi belgeleri içermelidir?** — kaynaklar: S1, S2, S3, S4

## İç bağlantılar

- [Topraklama direnci kaç ohm olmalı?](/haberler/topraklama-direnci-kac-ohm-olmali) — Tek direnç değerinin bağlamını ve temel ölçüm kavramını açıklar.
- [Toprak direnci ve çevrim empedansı farkı](/haberler/topraklama-direnci-ariza-cevrim-empedansi-farki) — Elektrot ölçümü ile koruma açma yolunu ayırır.
- [Prizde topraklama var mı?](/haberler/prizde-topraklama-var-mi-priz-test-cihazi) — Konut düzeyindeki basit kontrol ile profesyonel saha ölçümünü ayırır.
- [Nötr-toprak gerilimi](/haberler/notr-toprak-arasi-gerilim-kac-volt-olmali) — N-PE potansiyel farkının ölçüm sınırlarını tamamlar.
- [Faz kaybı ve dengesizlik](/haberler/faz-dengesizligi-faz-kaybi-motoru-nasil-etkiler) — Topraklama dışındaki gerilim ve motor risklerini ayırır.
- [Elektrik panosunda termal kamera](/haberler/elektrik-panosunda-termal-kamera-kontrolu) — Bağlantı ve eşpotansiyel iletkenlerde termal bakım bağını destekler.
- [Kurumsal ön değerlendirme](/kurumsal-elektrik-surekliligi-on-degerlendirme) — Trafo, GES ve geniş tesislerde ölçüm kapsamını profesyonel çalışmaya taşır.

## AEO, SEO ve yapılandırılmış veri

- İlk ekranda bağımsız anlaşılabilen doğrudan cevap bulunur.
- Title, meta description, H1 ve canonical birbirinden tutarlı ve kullanıcı görevi odaklıdır.
- Dört görünür SSS bulunur.
- Canonical derleyici `Article`, `FAQPage` ve `BreadcrumbList` üretmelidir.
- Yazar/üretici kimliği kurumsal `Organization` olmalıdır.
- `Person`, `ProfilePage`, `Product` ve `Offer` kullanılmamalıdır.
- Tahmini en yüksek mevcut içerik benzerliği `0.43`; en yakın rota `/haberler/topraklama-direnci-kac-ohm-olmali`. Fail-closed eşik `0,78`’dir.

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
/cms approve topraklama-dokunma-adim-gerilimi-olcum-kabul-dosyasi
```

AI ve bot yorumları onay sayılmaz. Onay workflow’u canonical HTML, routing overlay ve ChatGPT Sites önizleme artifactını üretir; PR ayrıca insan merge’i olmadan canlıya çıkmaz.
