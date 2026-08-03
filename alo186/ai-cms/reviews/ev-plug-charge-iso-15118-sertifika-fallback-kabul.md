# ALO186 AI CMS inceleme paketi — ev-plug-charge-iso-15118-sertifika-fallback-kabul

> Bu dosya canonical yayına dahil edilmez. PR incelemesi ve insan onayı için üretilmiştir.

## Durum

- State: **approved**
- Risk: **legal**
- Model: **gpt-5.6-thinking**
- Kalite: **88/100**
- Benzerlik: **0.36** — https://www.alo186.com/haberler/ev-sarj-plug-and-charge-iso-15118-sertifika-hatasi
- Kelime: **955**

## Kalite kapıları

- ❌ metadata
- ✅ directAnswer
- ✅ contentDepth
- ✅ sources
- ✅ safety
- ✅ internalLinks
- ✅ uniqueness
- ✅ structuredData

### Hatalar

- Yok

### Uyarılar

- Yok

## AI risk notları

- AI ek risk notu üretmedi.

## Kaynaklar

- **S1 · ISO** — [ISO 15118-20:2022 — Second Generation Network and Application Layer Requirements](https://www.iso.org/standard/77845.html) — erişim 2026-08-03 — birincil
- **S2 · ISO** — [ISO 15118-20:2022/Amd 1:2026 — AC DER, MCS and Improved Security Concept](https://www.iso.org/standard/87920.html) — erişim 2026-08-03 — birincil
- **S3 · Hubject** — [Plug&Charge Ecosystem](https://support.hubject.com/hc/en-us/articles/9205932782621-1-3-Plug-Charge-Ecosystem) — erişim 2026-08-03 — birincil
- **S4 · Hubject** — [Signing a CSR and Obtaining an EVSE Leaf Certificate](https://support.hubject.com/hc/en-us/articles/8922829951133-3-1-Signing-of-a-Certificate-Signing-Request-CSR-and-obtaining-an-EVSE-Leaf-Certificate-and-its-corresponding-Sub-Certificate-Chain) — erişim 2026-08-03 — birincil
- **S5 · Hubject** — [Requirements for CPMS](https://support.hubject.com/hc/en-us/articles/9174328536221-3-6-Requirements-for-CPMS) — erişim 2026-08-03 — birincil
- **S6 · CharIN** — [Certificate Policy Guideline for an ISO 15118 V2G PKI](https://www.charin.global/news/charin-e-v-publishes-certificate-policy-guideline-for-an-iso-15118-v2g-pki/) — erişim 2026-08-03 — birincil

## SEO

- Title: `EV Plug & Charge ISO 15118 Sertifika Kabul Testi`
- H1: `ISO 15118 Plug & Charge sertifika ve fallback akışı nasıl test edilir?`
- Description: `Plug & Charge kabulünü ISO 15118 sürümü, EVSE sertifika zinciri, sözleşme sertifikası, OCSP, saat, backend ve RFID fallback kanıtlarıyla hazırlayın.`
- Canonical: `/haberler/ev-plug-charge-iso-15118-sertifika-fallback-kabul`
- Birincil anahtar kelime: `ISO 15118 Plug Charge kabul testi`

## Doğrudan cevap

ISO 15118 Plug & Charge kabulü, aracın bir kez kablo takıldığında şarja başlamasıyla tamamlanmaz. Kabul; araç, EVSE, CPMS, e-mobilite hizmet sağlayıcısı ve V2G PKI rollerinin ayrılması; EVSE yaprak sertifikası ile alt ve kök sertifika zincirinin doğrulanması; sözleşme sertifikasının kurulması ve yetkilendirilmesi; sertifika süresi, iptal durumu, saat doğruluğu ve ağ kesintisinin denenmesi; başarısız Plug & Charge durumunda RFID, uygulama veya başka onaylı yönteme güvenli fallback yapılmasıyla kanıtlanır. Gerçek müşteri sertifikaları, özel anahtarlar veya sözleşme kimlikleri ALO186'e yüklenmemelidir.

## Plug & Charge kabulünde hangi roller ve protokol sürümleri ayrılmalıdır?

Plug & Charge tek bir şarj cihazı özelliği değildir. Araçtaki iletişim denetleyicisi, EVSE/SECC, şarj noktası yönetim sistemi, CPO, e-mobilite hizmet sağlayıcısı, sertifika sağlama hizmeti ve V2G PKI güven zinciri birlikte çalışır. Aracın ve istasyonun ISO 15118 desteği olsa bile backend veya sertifika ekosistemi eksikse otomatik sözleşme yetkilendirmesi tamamlanmayabilir.

Kabul dosyasında ISO 15118-2 ve ISO 15118-20 kapsamı, AC/DC kullanım senaryosu, OCPP sürümü, CPMS entegrasyon yöntemi ve desteklenen Plug & Charge fonksiyonları sürüm numarasıyla yazılmalıdır. ISO 15118-20'nin 2026 güvenlik değişikliği gibi yeni yayınlar, mevcut cihazın otomatik olarak o sürümü desteklediği anlamına gelmez; firmware, sertifika ve uygunluk kapsamı ayrı doğrulanmalıdır.

- EV, EVSE, CPMS, CPO, eMSP ve PKI rollerini tek RACI tablosunda gösterin.
- ISO 15118 ve OCPP sürümlerini cihaz/firmware bazında kaydedin.
- AC, DC, V2G ve çoklu sözleşme kabiliyetlerini ayrı işlevler olarak sınayın.
- Uyumlu etiketi yerine desteklenen gerçek mesaj ve sertifika akışını belgeleyin.

_Kaynaklar: S1, S2, S3, S6_

## EVSE yaprak sertifikası ve güven zinciri nasıl doğrulanmalıdır?

EVSE'nin özel anahtarını cihaz içinde oluşturması, sertifika imzalama isteğini güvenli biçimde CPMS'ye iletmesi, uygun sertifika otoritesinden imzalı yaprak sertifikası ve alt CA zinciri alması ve doğru sırayla kurması gerekir. Common Name, SECC ID, sertifika uzantıları, algoritma, geçerlilik süresi ve güven kökü kabul sırasında kontrol edilmelidir.

Sertifika yenileme yalnız son gün manuel işlem olarak bırakılmamalıdır. CPMS'nin CSR üretimini tetikleme, yeni zinciri dağıtma, başarısız kurulumu geri alma ve eski sertifika ile çakışmadan geçiş yapma davranışı test edilmelidir. Özel anahtarın dışa aktarılması veya ekran görüntüsüyle paylaşılması kabul kanıtı değildir ve güvenlik riski yaratır.

- CSR'nin EVSE içinde üretildiğini ve özel anahtarın dışarı çıkmadığını doğrulayın.
- Yaprak, Sub-CA ve güven kökü zincir sırasını kaydedin.
- SECC ID, ad alanı, uzantı ve geçerlilik tarihlerini kontrol edin.
- Planlı yenileme ve başarısız yenilemede rollback senaryosu çalıştırın.

_Kaynaklar: S3, S4, S5_

## Sözleşme sertifikası ve otomatik yetkilendirme uçtan uca nasıl sınanır?

Plug & Charge işleminde aracın sözleşme sertifikası güven zinciri üzerinden doğrulanır ve ilgili eMSP sözleşmesiyle eşleştirilir. Başarılı test yalnız EVSE ekranında 'authorized' görülmesi değildir; araç kimliklendirme mesajı, sertifika doğrulama sonucu, backend yetkilendirmesi, işlem kimliği, sayaç başlangıcı ve faturalama tarafındaki sözleşme eşleşmesi ortak zaman çizelgesinde görülmelidir.

Geçerli sertifika, süresi dolmuş sertifika, iptal edilmiş sertifika, bilinmeyen güven kökü, yanlış sözleşme ve backend gecikmesi ayrı negatif senaryolardır. OCSP veya eşdeğer durum kontrolü destekleniyorsa geri çekilmiş hakların hâlâ kabul edilmediği doğrulanmalıdır. Gerçek kullanıcı EMAID, sözleşme sertifikası veya kişisel ödeme verileri yerine test kimlikleri kullanılmalıdır.

- Başarılı yetkilendirmede EVSE, CPMS ve eMSP kayıtlarını eşleştirin.
- Süresi dolmuş, iptal edilmiş ve güvenilmeyen sertifika senaryolarını test edin.
- OCSP/durum kontrolünün hata ve timeout davranışını kaydedin.
- Gerçek müşteri sertifikası yerine ayrılmış test sözleşmesi kullanın.

_Kaynaklar: S3, S5, S6_

## Saat sapması, ağ kesintisi ve alternatif yetkilendirme fallback'i nasıl test edilir?

Sertifika doğrulaması geçerlilik tarihleri ve zaman damgalarına bağlı olduğundan EVSE, CPMS ve test aracının saat kaynağı ile zaman dilimi kontrol edilmelidir. NTP kaybı, belirlenmiş saat sapması, CPMS bağlantı kesintisi ve sertifika durum servisinin erişilememesi halinde sistemin güvenli ve izlenebilir davranışı ölçülmelidir.

Plug & Charge başarısız olduğunda sürücünün kilitli kalmaması için işletmecinin onayladığı RFID, uygulama, ödeme terminali veya çağrı merkezi akışı denenmelidir. Fallback, geçersiz sertifikayı sessizce yetkili saymamalı; ayrı bir kimlik doğrulama işlemi başlatmalı ve faturalama kaydında hangi yöntemin kullanıldığı açık görünmelidir.

- EVSE, CPMS ve backend saatlerini ortak referansla karşılaştırın.
- Ağ, DNS, PKI ve sertifika durum servisi kesintilerini ayrı test edin.
- Plug & Charge reddinden RFID/uygulamaya kontrollü fallback'i doğrulayın.
- Fallback işleminin kimlik ve faturalama yöntemini olay kaydında görünür tutun.

_Kaynaklar: S2, S3, S5, S6_

## Plug & Charge kabul dosyasında hangi kanıtlar bulunmalıdır?

Teslim dosyasında rol ve sürüm matrisi, EVSE modeli ve firmware, SECC ID, kullanılan test PKI ortamı, güven kökü listesi, sertifika zinciri özeti, geçerlilik ve yenileme planı, OCPP mesaj izleri, başarılı ve negatif senaryolar, işlem-sayaç-faturalama mutabakatı, saat kaydı ve fallback sonuçları bulunmalıdır. Sertifika veya log örnekleri özel anahtar, gerçek EMAID, token ve kişisel veri içermeyecek biçimde maskelenmelidir.

Sonuç geçti, şartlı geçti veya kaldı olarak sınıflandırılmalıdır. Zincir doğrulama hatası, süresi dolan sertifikada kabul, yenileme kesintisi, saat kaynaklı rastgele başarısızlık veya fallback'te yanlış faturalama varsa canlı kullanım açılmamalıdır. Mevcut sistem tüm senaryoları geçiyorsa yalnız pazarlama amacıyla yeni EVSE ya da backend modülü satın almak gerekmez.

- Sürüm, sertifika, işlem ve faturalama kanıtlarını aynı test kimliğiyle bağlayın.
- Özel anahtar ve gerçek sözleşme verilerini dosyaya koymayın.
- Sertifika yenileme tarihi ve sorumlusunu operasyon takvimine ekleyin.
- Kanıt yeterliyse gereksiz EVSE, modem veya CPMS değişimi yapmayın.

_Kaynaklar: S1, S2, S3, S4, S5, S6_

## Sık sorulan sorular

### Plug & Charge için yalnız ISO 15118 destekli araç ve istasyon yeterli midir?

Hayır. EVSE sertifikası, güven kökleri, sözleşme sertifikası, CPMS/OCPP mesajları, eMSP yetkilendirmesi ve PKI hizmetleri de uyumlu çalışmalıdır. Uçtan uca ekosistem olmadan otomatik kimliklendirme tamamlanmayabilir.

_Kaynaklar: S1, S3, S6_

### EVSE sertifikasının süresi dolarsa şarj tamamen durur mu?

Davranış ürün ve işletme politikasına bağlıdır; Plug & Charge reddedilebilirken RFID veya uygulama gibi ayrı yetkilendirme yöntemleri çalışabilir. Kabul testinde yenileme, expiry ve güvenli fallback birlikte sınanmalıdır.

_Kaynaklar: S3, S5_

### Plug & Charge testi için gerçek müşteri sertifikası kullanılmalı mı?

Hayır. Ayrılmış test ortamı ve test sözleşmesi kullanılmalı; özel anahtar, gerçek EMAID, sözleşme kimliği ve ödeme verileri rapora veya ALO186'e yüklenmemelidir.

_Kaynaklar: S3, S4_

### OCPP 1.6 kullanan istasyonda Plug & Charge mümkün müdür?

Bazı uygulamalar ISO 15118 mesajlarını OCPP 1.6J DataTransfer üzerinden taşıyabilir; OCPP 2.0.1 ise ilgili mesajları yerel olarak destekler. Gerçek kapsam CPMS ve EVSE uygulamasıyla test edilmelidir.

_Kaynaklar: S5_

## İnsan onay komutu

PR sahibinin veya repository yetkilisinin yorumu:

```text
/cms approve ev-plug-charge-iso-15118-sertifika-fallback-kabul
```

Onay iş akışı kalite puanı, kaynak güncelliği, iç linkler, kanibalizasyon ve risk sınırlarını yeniden çalıştırmadan canonical dosya üretmez.
