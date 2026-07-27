# ALO186 Grafana Cloud Dashboard ve Alert Seti

## Temel paneller

1. API up/down
2. HTTP istek hızı
3. 2xx / 4xx / 5xx oranları
4. Ortalama istek süresi
5. In-flight istek
6. Process uptime
7. Alloy remote-write queue ve retry
8. Haricî GitHub sentetik kontrol sonucu
9. Backup heartbeat yaşı
10. Sentry hata sayısı ve yeni regression'lar

## Önerilen PromQL alertleri

### API scrape başarısız

```promql
up{job="alo186-continuity-api"} == 0
```

- For: 2 dakika
- Severity: critical

### 5xx oranı yüksek

```promql
sum(rate(alo186_http_requests_total{status=~"5.."}[5m]))
/
clamp_min(sum(rate(alo186_http_requests_total[5m])), 0.001)
> 0.02
```

- For: 5 dakika
- Severity: high

### Ortalama istek süresi yüksek

```promql
sum(rate(alo186_http_request_duration_seconds_sum[5m]))
/
clamp_min(sum(rate(alo186_http_requests_total[5m])), 0.001)
> 1
```

- For: 10 dakika
- Severity: warning

### Çok sayıda 429

```promql
sum(rate(alo186_http_requests_total{status="429"}[10m])) > 0.2
```

- For: 10 dakika
- Severity: warning
- Auth saldırısı veya yanlış istemci retry davranışı araştırılır.

### Process sık yeniden başlıyor

```promql
alo186_uptime_seconds < 600
```

- For: 5 dakika
- Severity: warning
- Deploy pencereleri için mute interval tanımlanır.

### Alloy remote write geride kalıyor

```promql
prometheus_remote_storage_samples_pending > 10000
```

- For: 10 dakika
- Severity: warning

## Bildirim rotası

- Critical: e-posta + mobil push / telefon escalation
- High: e-posta + ekip kanalı
- Warning: ekip kanalı veya günlük digest

İlk aşamada tek kişilik operasyon için alarm sayısı sınırlı tutulmalıdır. Her alarmın:

- sahibi,
- cevap süresi,
- runbook bağlantısı,
- yanlış pozitif geçmişi,
- son test tarihi

olmalıdır.

## Sentry politikası

- `send_default_pii=false`
- Üretim traces örnekleme: %5
- Worker traces örnekleme: %1
- E-posta, parola, token, açık adres ve tesisat numarası tag/breadcrumb olarak gönderilmez.
- Yeni issue ve regression için alert; tekrarlayan aynı hata için digest.

## Sentetik monitoring

GitHub workflow'u canlıya çıkıştan sonra şu variable ile etkinleştirilir:

```text
ALO186_PRODUCTION_MONITOR_ENABLED=true
```

Kontroller:

- DNS resolve
- TLS SAN ve en az 21 gün geçerlilik
- `/health/live`
- `/health/ready`
- güvenlik başlıkları
- tek SPF ve DMARC kaydı

Başarısızlıkta tek açık GitHub alert issue güncellenir; servis iyileştiğinde otomatik kapanır.
