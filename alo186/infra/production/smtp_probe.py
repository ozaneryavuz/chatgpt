from __future__ import annotations

import argparse
import os
import smtplib
import ssl
from email.message import EmailMessage


def required(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise SystemExit(f"{name} zorunludur.")
    return value


def main() -> None:
    parser = argparse.ArgumentParser(description="ALO186 SMTP TLS/auth ve isteğe bağlı teslimat testi")
    parser.add_argument("--send", action="store_true", help="Gerçek test e-postası gönder.")
    args = parser.parse_args()

    host = required("ALO186_SMTP_HOST")
    port = int(os.getenv("ALO186_SMTP_PORT", "587"))
    username = required("ALO186_SMTP_USERNAME")
    password = required("ALO186_SMTP_PASSWORD")

    with smtplib.SMTP(host, port, timeout=20) as smtp:
        smtp.ehlo()
        smtp.starttls(context=ssl.create_default_context())
        smtp.ehlo()
        smtp.login(username, password)
        code, _message = smtp.noop()
        if code != 250:
            raise SystemExit(f"SMTP NOOP başarısız: {code}")

        if args.send:
            sender = required("ALO186_SMTP_FROM_EMAIL")
            recipient = required("ALO186_SMTP_TEST_RECIPIENT")
            message = EmailMessage()
            message["From"] = sender
            message["To"] = recipient
            message["Subject"] = "ALO186 production SMTP doğrulaması"
            message.set_content(
                "Bu mesaj ALO186 production SMTP, TLS ve gönderici alan adı doğrulaması için otomatik oluşturuldu."
            )
            smtp.send_message(message)
            print(f"Test mesajı gönderildi: {recipient}")
        else:
            print("SMTP TLS ve kimlik doğrulama başarılı; mesaj gönderilmedi.")


if __name__ == "__main__":
    main()
