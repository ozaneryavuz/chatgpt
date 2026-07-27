# ALO186 Production Stack

Bu klasör, Elektrik Sürekliliği SaaS API'yi tek kişinin yönetebileceği fakat sağlayıcı kilidine karşı taşınabilir bir üretim mimarisine dönüştürür.

## Mimari: Managed Core + Portable Escape Hatch

```text
www.alo186.com
      │
      ├── statik kullanıcı araçları
      │
      └── api.alo186.com
              │
        Render managed TLS edge
              │
        FastAPI web service ───── Sentry
              │
      Render private network
        ┌─────┼────────────┐
        │     │            │
   PostgreSQL email worker Grafana Alloy
   paid + PITR             │
        │                  └── Grafana Cloud
        │
   daily pg_dump
        │
   Restic encrypted R2 ─── monthly locked vault
```

Taşınabilir fallback:

```text
Caddy + Docker Compose + PostgreSQL + API + workers + Restic
```

## Klasörler

- `render/production.yaml` — Frankfurt Render Blueprint
- `dns/` — Cloudflare idempotent DNS reconciler ve Natro alternatifi
- `smtp/` — Postmark/DKIM/SPF/DMARC ve SMTP probe
- `secrets/` — secret envanteri, üretim ve rotasyon politikası
- `backups/` — R2/PITR/vault ve restore tatbikatı
- `monitoring/` — sentetik probe, Grafana/Sentry alertleri
- `../sureklilik-api/infra/backup/` — yedek container ve restore scripti
- `../sureklilik-api/infra/monitoring/` — Grafana Alloy image/config
- `../sureklilik-api/infra/caddy/` — portable TLS reverse proxy

## Neden bu model?

- FastAPI ve PostgreSQL aynı Frankfurt bölgesinde düşük gecikmeyle çalışır.
- TLS, deploy, health check ve PITR operasyon yükü yönetilen sağlayıcıda kalır.
- Günlük şifreli R2 yedeği sağlayıcı bağımlılığını azaltır.
- Caddy fallback'i Render dışına çıkışı mümkün kılar.
- DNS, monitoring ve secret süreçleri GitHub'da denetlenebilir; gerçek değerler Git'e girmez.
- Sağlayıcı kimlik bilgileri eklenene kadar workflow'lar dry-run veya kapalı modda kalır.

## Uygulama sırası

1. `secrets/generate_secrets.py` ile başlangıç secret'larını üretin.
2. Postmark Sender Domain ve DNS kayıtlarını hazırlayın.
3. Cloudflare R2'de Restic ve monthly-vault bucket'larını oluşturun.
4. Sentry ve Grafana Cloud projelerini oluşturun.
5. Render Blueprint'i `render/production.yaml` özel yolundan oluşturun.
6. `sync: false` alanlarına secret değerlerini girin.
7. Render deploy ve Alembic migration sonucunu doğrulayın.
8. Render servis custom domain'ine `api.alo186.com` ekleyin.
9. DNS dry-run, ardından korumalı apply çalıştırın.
10. TLS ve health doğrulandıktan sonra sentetik monitoring'i etkinleştirin.
11. İlk günlük yedeği ve izole restore tatbikatını tamamlayın.
12. Pilot tenant oluşturun; ilk yönetici MFA'yı etkinleştirsin.

Ayrıntılı uygulama ve rollback adımları `PRODUCTION_RUNBOOK.md` dosyasındadır.
