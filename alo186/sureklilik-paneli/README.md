# ALO186 Elektrik Sürekliliği Paneli — Pilot v1

Otel, apartman/site ve küçük işletmelerin elektrik kesintisi hazırlığını, kritik yüklerini, jeneratör/UPS testlerini ve olay kayıtlarını tek local-first panelde yönetmesi için hazırlanmıştır.

## Pilot kapsamı

- Kuruluş profili
- Çoklu lokasyon
- Kritik yük envanteri
- P1/P2/P3 öncelik ve yedek kaynak
- Jeneratör, UPS ve batarya/inverter varlıkları
- Test periyodu ve test kaydı
- Açık/kapalı kesinti olayı
- Profile ve P1 yüklere göre otomatik görev listesi
- Olay zaman çizelgesi
- Olay maliyeti
- P1 görevleri tamamlanmadan kapanış uyarısı
- Yönetici tablosu
- JSON yedekleme/geri yükleme
- Yazdırma/PDF
- Audit log

## Veri mimarisi

Bütün veriler tarayıcı `localStorage` alanında tutulur. Sunucuya veri gönderilmez.

Bu nedenle pilot sürüm:

- kullanıcı hesabı içermez,
- çoklu kullanıcı senkronizasyonu yapmaz,
- bulut yedekleme sunmaz,
- rol bazlı gerçek erişim kontrolü sağlamaz,
- resmî bakım, denetim veya uygunluk belgesi oluşturmaz.

JSON yedeği olmadan tarayıcı verisi silinirse kayıtlar kaybolabilir.

## Dosyalar

- `store.js` — şema, lokasyon, yük, varlık, test, olay, görev, maliyet ve audit motoru
- `app.js` — localStorage, form ve dashboard akışları
- `index.html` — pilot kullanıcı arayüzü
- `styles.css` — responsive dashboard ve yazdırma tasarımı
- `../tests/test_continuity_store.js` — veri/olay motoru testleri

## Test

```bash
node alo186/tests/test_continuity_store.js
```

## Yayın rotası

```text
/isletme-surekliligi
```

## Pilot kullanım sırası

1. Kuruluş profilini oluşturun.
2. Lokasyonları ekleyin.
3. P1/P2/P3 kritik yükleri tanımlayın.
4. Jeneratör/UPS varlıklarını ve test periyodunu kaydedin.
5. Gerçek olay veya masa başı tatbikat başlatın.
6. Görevleri ve zaman çizelgesini tamamlayın.
7. Maliyet ve kapanış notunu kaydedin.
8. JSON yedeği ve PDF yönetici çıktısı alın.

## Analytics

- `continuity_organization_saved`
- `continuity_location_added`
- `continuity_critical_load_added`
- `continuity_asset_added`
- `continuity_asset_test_added`
- `continuity_incident_started`
- `continuity_task_updated`
- `continuity_incident_event_added`
- `continuity_incident_cost_added`
- `continuity_incident_closed`
- `continuity_exported`
- `continuity_imported`
- `continuity_sample_loaded`

## Sonraki SaaS fazı

Issue #6 tamamlanmadan önce:

- kullanıcı hesabı ve güvenli oturum,
- kuruluş/tenant izolasyonu,
- yönetici, teknik ekip ve görüntüleyici rolleri,
- merkezi PostgreSQL veri tabanı,
- e-posta/web bildirimleri,
- bakım takvimi,
- offline sync ve conflict handling,
- veri şifreleme ve audit dışa aktarımı,
- abonelik ve kullanım limitleri

geliştirilmelidir.
