# Postmark SMTP ve E-posta Kimlik Doğrulama Runbook'u

## Neden ayrı transactional SMTP?

Doğrulama, parola sıfırlama, davet ve olay bildirimleri pazarlama e-postasından ayrı tutulur. Gönderici itibarı ve hata ayıklama kolaylaşır.

## Kurulum

1. Postmark'ta production server oluşturun.
2. Sender Domain olarak `alo186.com` ekleyin.
3. Gönderici adresi: `noreply@alo186.com`.
4. Postmark'ın verdiği DKIM TXT ve Return-Path CNAME kayıtlarını DNS sağlayıcısına ekleyin.
5. Mevcut SPF kaydını **ikinci bir SPF TXT oluşturmadan** Postmark talimatına göre birleştirin.
6. Önce DMARC izleme politikası kullanın:

```text
_dmarc.alo186.com TXT "v=DMARC1; p=none; pct=100; rua=mailto:dmarc@alo186.com; adkim=r; aspf=r"
```

7. En az iki hafta raporları inceleyin; bütün meşru kaynaklar hizalandıktan sonra `quarantine`, ardından `reject` politikasına geçin.

## Render secret değerleri

```text
ALO186_EMAIL_BACKEND=smtp
ALO186_SMTP_HOST=smtp.postmarkapp.com
ALO186_SMTP_PORT=587
ALO186_SMTP_USERNAME=<Postmark server token>
ALO186_SMTP_PASSWORD=<Postmark server token>
ALO186_SMTP_FROM_EMAIL=noreply@alo186.com
ALO186_SMTP_USE_TLS=true
```

Token repository'ye yazılmaz; Render'da `sync: false` secret olarak girilir.

## Gönderim öncesi test

Yalnız TLS ve kimlik doğrulama:

```bash
export ALO186_SMTP_HOST=smtp.postmarkapp.com
export ALO186_SMTP_PORT=587
export ALO186_SMTP_USERNAME='...'
export ALO186_SMTP_PASSWORD='...'
python alo186/infrastructure/smtp/smtp_probe.py
```

Gerçek test mesajı:

```bash
export ALO186_SMTP_FROM_EMAIL=noreply@alo186.com
export ALO186_SMTP_TEST_RECIPIENT='kontrol-edilen-adres@example.com'
python alo186/infrastructure/smtp/smtp_probe.py --send
```

## DNS kontrolü

```bash
bash alo186/infrastructure/smtp/check_email_dns.sh alo186.com
```

Script SPF ve DMARC varlığını doğrular. DKIM selector ve Return-Path değerleri Postmark hesabına özgü olduğundan aşağıdaki environment değerleriyle ayrıca kontrol edilir:

```bash
export POSTMARK_DKIM_HOST='selector._domainkey.alo186.com'
export POSTMARK_RETURN_PATH_HOST='pm-bounces.alo186.com'
bash alo186/infrastructure/smtp/check_email_dns.sh alo186.com
```

## Üretim kabul kriterleri

- Postmark Sender Domain `Verified`.
- DKIM doğrulandı.
- SPF tek TXT kaydında ve geçerli.
- DMARC kaydı mevcut.
- Verification/reset/invitation şablonları spam klasörüne düşmeden teslim edildi.
- Hard bounce ve spam complaint webhook'ları ileriki fazda kullanıcı durumuna işlenmek üzere ayrı issue olarak kaydedildi.
- `noreply@alo186.com` yanıtları ya izlenen bir adrese yönleniyor ya da e-postada açık destek kanalı bulunuyor.
