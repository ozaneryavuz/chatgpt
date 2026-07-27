# ALO186 SaaS v0.4 — Davet tabanlı ekip onboarding'i

Kuruluş yöneticisinin admin, technician veya viewer rolüyle ekip üyesi davet etmesini sağlar. Davet edilen kişi mevcut hesabını kullanabilir veya davette sabitlenen e-posta adresiyle yeni hesap oluşturabilir.

## Güvenlik modeli

- Raw davet tokenı veri tabanında tutulmaz; HMAC-SHA256 hash saklanır.
- Token 32 byte yüksek entropili ve tek kullanımlıdır.
- Varsayılan geçerlilik 7 gündür (`ALO186_INVITATION_TTL_SECONDS`).
- Kabul e-postası token üzerinden sabittir; istek gövdesinden e-posta alınmaz.
- Süresi dolmuş, iptal edilmiş veya kabul edilmiş davet yeniden kullanılamaz.
- Aynı kuruluş/e-posta için aktif davet yeniden oluşturulursa eski token geçersizleşir.
- Davet yaratma, yeniden gönderme, iptal ve kabul işlemleri tenant audit loguna yazılır.
- Admin dışındaki roller davet oluşturamaz.
- Plan üye limiti, mevcut üyeler ile aktif bekleyen davetlerin toplamına uygulanır.
- Token API cevaplarında yalnız `ALO186_EXPOSE_TEST_TOKENS=true` olduğunda görünür.
- E-posta outbox payloadı Fernet ile şifrelenir.

## Endpointler

```text
GET    /api/v1/organizations/{organization_id}/invitations
POST   /api/v1/organizations/{organization_id}/invitations
POST   /api/v1/organizations/{organization_id}/invitations/{invitation_id}/resend
DELETE /api/v1/organizations/{organization_id}/invitations/{invitation_id}
POST   /api/v1/invitations/preview
POST   /api/v1/invitations/accept-new
POST   /api/v1/invitations/accept-existing
```

Kuruluş kapsamındaki yönetim endpointlerinde:

```http
Authorization: Bearer <admin-token>
X-Organization-ID: <organization-uuid>
```

başlıkları zorunludur.

## Davet oluşturma

```http
POST /api/v1/organizations/{organization_id}/invitations
Content-Type: application/json

{
  "email": "teknik@example.com",
  "role": "technician",
  "notify_incidents": true
}
```

Üretimde token yalnız şifreli e-posta outboxına yazılır. Test ortamında `test_token` alanı dönebilir.

## Ön izleme

Kimlik doğrulama gerektirmez ve tam e-posta adresini göstermez:

```http
POST /api/v1/invitations/preview

{"token":"<raw-token>"}
```

Yanıt kuruluş adı, maskelenmiş e-posta, rol, bildirim tercihi, süre ve mevcut hesap bilgisi içerir.

## Yeni kullanıcı kabulü

```http
POST /api/v1/invitations/accept-new

{
  "token": "<raw-token>",
  "password": "en-az-10-karakter"
}
```

Kullanıcı davet e-postasıyla oluşturulur, e-posta doğrulanmış kabul edilir, üyelik atanır ve süreli bearer oturumu döner.

## Mevcut kullanıcı kabulü

```http
POST /api/v1/invitations/accept-existing
Authorization: Bearer <user-token>

{"token":"<raw-token>"}
```

Oturumdaki kullanıcının e-postası davet e-postasıyla birebir eşleşmelidir.

## Migration

```bash
cd alo186/sureklilik-api
export PYTHONPATH=.
alembic upgrade head
```

Yeni tablo:

```text
organization_invitations
```

Migration sürümü:

```text
20260728_0003
```

## Test

```bash
pytest -q tests/test_invitations.py
pytest -q
alembic check
```

Test kapsamı:

- admin ve admin dışı yetki
- yeni ve mevcut kullanıcı kabulü
- e-posta sabitleme
- token hash, tek kullanım, süre ve revoke
- yeniden gönderme ve token rotasyonu
- duplicate aktif davet
- pending davet dahil plan limiti
- şifreli e-posta outboxı
- tenant audit logu
- SQLite ve PostgreSQL migration/entegrasyon
