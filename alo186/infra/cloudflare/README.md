# ALO186 Cloudflare DNS Terraform v5

Bu modül yalnız ALO186 üretim API ve Postmark doğrulama kayıtlarını yönetir. Mevcut `www`, MX veya web hosting kayıtlarını otomatik olarak devralmaz.

## Önkoşullar

- `alo186.com` zone Cloudflare üzerinde etkin olmalı.
- API token yalnız ilgili zone için `DNS Read` ve `DNS Write` yetkisine sahip olmalı.
- Render üzerinde `api.alo186.com` custom domain eklenmiş olmalı.
- Postmark DKIM/Return-Path adları sağlayıcı panelinden alınmalı.

## Kullanım

```bash
cd alo186/infra/cloudflare
terraform init
terraform validate
terraform plan \
  -var='cloudflare_api_token=***' \
  -var='zone_id=***' \
  -var='render_api_hostname=alo186-continuity-api.onrender.com'
```

İlk Render domain doğrulaması sırasında:

```hcl
api_proxied = false
```

TLS sertifikası ve Render custom domain doğrulaması tamamlandıktan sonra Cloudflare proxy ayrı bir planla etkinleştirilmelidir.

## Postmark

Postmark panelindeki gerçek değerleri kullanın:

```hcl
postmark_dkim_name                = "..."
postmark_dkim_content             = "..."
postmark_return_path_name         = "..."
postmark_return_path_content      = "..."
```

Mevcut SPF kaydını bu modül değiştirmez. Aynı alan adında ikinci SPF TXT kaydı oluşturmayın. DMARC kaydı henüz yoksa `manage_dmarc=true` ile önce `p=none` gözlem politikası uygulanabilir.

## Natro manuel alternatif

Nameserver Cloudflare'a taşınmayacaksa Natro DNS panelinde:

1. `api` için CNAME → Render hostname
2. Postmark DKIM CNAME
3. Postmark Return-Path CNAME
4. Mevcut SPF kaydını koruyarak Postmark doğrulaması
5. `_dmarc` TXT

kayıtları manuel girilir. Render sertifika durumu **verified** olmadan Cloudflare proxy veya farklı CDN katmanı etkinleştirilmez.

## State güvenliği

Terraform state içinde DNS hedefleri ve bazı metadata bulunur. Remote state kullanılacaksa şifreli backend, erişim kontrolü ve state locking uygulanmalıdır. API token hiçbir `.tfvars` dosyasıyla repoya yazılmamalıdır.
