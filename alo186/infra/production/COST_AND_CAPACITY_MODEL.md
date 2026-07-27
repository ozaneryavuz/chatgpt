# ALO186 SaaS production cost and capacity model

Bu model sağlayıcı fiyatlarını sabit kabul etmez. Render, Postmark, Sentry, Grafana ve R2 panelindeki güncel fiyatlar aylık olarak girilir.

## Değişkenler

| Sembol | Açıklama |
|---|---|
| `C_web` | API web service aylık bedeli |
| `C_worker` | E-posta worker aylık bedeli |
| `C_cron` | cron servisleri aylık bedeli |
| `C_db` | PostgreSQL instance + depolama + PITR |
| `C_email` | gönderilen e-posta hacmi |
| `C_obs` | Sentry + Grafana |
| `C_backup` | R2 depolama ve istek |
| `C_domain` | DNS/domain/sertifika yan gideri |
| `C_total` | toplam aylık altyapı gideri |
| `N` | ücretli kuruluş sayısı |
| `ARPA` | kuruluş başına aylık ortalama gelir |
| `GM` | brüt marj |

```text
C_total = C_web + C_worker + C_cron + C_db + C_email + C_obs + C_backup + C_domain
MRR = N × ARPA
GM = (MRR - C_total - değişken destek maliyeti) / MRR
Başabaş kuruluş = ceil(C_total / ARPA)
```

## Başlangıç paket hipotezi

| Paket | Hedef müşteri | Aylık fiyat hipotezi | Limit odağı |
|---|---|---:|---|
| Site | apartman/site | ₺499–999 | 1–3 lokasyon, sınırlı ekip |
| Business | küçük işletme | ₺750–1.500 | kritik yük, test, olay |
| Hotel | otel/tesis | ₺1.500–4.000 | çoklu kritik sistem, ekip |
| Multi-location | zincir/çoklu tesis | özel | API, merkezi rapor, SLA |

Fiyat doğrulaması altyapı maliyetine değil müşterinin önlediği duruş, raporlama süresi ve denetim değerine göre yapılmalıdır.

## Kapasite eşikleri

### Aşama A — pilot

- 7 pilot kuruluş
- tek API process
- tek worker
- managed PostgreSQL
- 15 dakikalık synthetic
- düşük hacimli SMTP

Başarı kapısı:

- 30 günlük aktif kuruluş ≥ %70
- ilk planı 24 saatte oluşturma ≥ %60
- haftalık test kaydı ≥ %70
- ücretliye dönüşüm ≥ %25

### Aşama B — ilk 100 ücretli kuruluş

- DB connection ve slow query izlemesi
- e-posta worker retry/bounce dashboard
- Redis tabanlı paylaşımlı rate limit/idempotency
- API iki replica değerlendirmesi
- plan ve kullanım limitlerinin billing ile eşleşmesi
- destek self-service oranı ≥ %70

### Aşama C — 1.000 kuruluş

- PostgreSQL connection pooling
- read replica gereksinim analizi
- queue tabanlı background iş sistemi
- olay/rapor dosyaları için object storage
- merkezi feature flag ve rollout
- SLO ve error budget
- ayrı analytics warehouse

## Ölçek artırma tetikleri

| Tetik | Aksiyon |
|---|---|
| API p95 > 750 ms, 15 dakika | sorgu/profil; sonra compute scale |
| DB CPU > %70, 30 dakika | index/query/connection; sonra DB scale |
| connection kullanımı > %70 | pooling veya instance scale |
| outbox bekleme > 5 dakika | worker ve SMTP kapasitesi |
| 5xx > %1 | release/DB/entegrasyon incelemesi |
| backup > 60 dakika veya 24 saat yedeksiz | backup plan yükseltme |
| aylık altyapı / MRR > %20 | provider ve mimari maliyet optimizasyonu |

## Marj hedefi

Erken SaaS hedefi:

```text
Altyapı + transactional e-posta + observability ≤ MRR'nin %15'i
Brüt marj ≥ %80
Destek maliyeti hariç altyapı başabaş ≤ 10 ücretli kuruluş
```

Bu hedefler gerçekleşmiş finansal sonuç değil; pilot ölçümüyle doğrulanacak yönetim sınırlarıdır.

## Aylık maliyet toplantısı

Her ay şu tablo doldurulur:

```text
Ücretli kuruluş:
MRR:
Web:
Worker:
Cron:
PostgreSQL:
Email:
Observability:
Backup:
Toplam altyapı:
Altyapı / MRR:
Brüt marj:
Bir sonraki optimizasyon:
```

Altyapı maliyeti düşükken gereksiz mikroservis veya yüksek kullanılabilirlik katmanı eklenmez; müşteri riski ve gelir bunu doğruladığında ölçek artırılır.
