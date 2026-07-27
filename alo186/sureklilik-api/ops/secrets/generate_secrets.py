#!/usr/bin/env python3
from __future__ import annotations

import argparse
import base64
import json
import os
import secrets
import stat
from pathlib import Path


def token_urlsafe_bytes(size: int) -> str:
    return base64.urlsafe_b64encode(os.urandom(size)).decode("ascii")


def write_secret(path: Path, value: str) -> None:
    path.write_text(value + "\n", encoding="utf-8")
    path.chmod(stat.S_IRUSR | stat.S_IWUSR)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="ALO186 production secret bootstrap dosyalarını yerel olarak üretir."
    )
    parser.add_argument("--output-dir", default="./generated-secrets")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    output = Path(args.output_dir).resolve()
    if output.exists() and any(output.iterdir()) and not args.force:
        raise SystemExit(f"{output} dolu. Yeniden yazmak için --force kullanın.")
    output.mkdir(parents=True, exist_ok=True)
    output.chmod(stat.S_IRWXU)

    values = {
        "ALO186_TOKEN_SECRET": secrets.token_urlsafe(48),
        "ALO186_DATA_ENCRYPTION_KEY": token_urlsafe_bytes(32),
        "ALO186_METRICS_TOKEN": secrets.token_urlsafe(32),
        "RESTIC_PASSWORD": secrets.token_urlsafe(48),
        "CADDY_ACME_EMAIL": "ops@alo186.com",
        "ALO186_SMTP_USERNAME": "POSTMARK_SERVER_TOKEN",
        "ALO186_SMTP_PASSWORD": "POSTMARK_SERVER_TOKEN",
        "ALO186_SENTRY_DSN": "SET_IN_PROVIDER_DASHBOARD",
        "RESTIC_REPOSITORY": "s3:https://<CLOUDFLARE_ACCOUNT_ID>.r2.cloudflarestorage.com/alo186-backups",
        "AWS_ACCESS_KEY_ID": "SET_R2_ACCESS_KEY_ID",
        "AWS_SECRET_ACCESS_KEY": "SET_R2_SECRET_ACCESS_KEY",
    }

    for name, value in values.items():
        write_secret(output / f"{name}.txt", value)

    manifest = {
        "generated_at": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(),
        "rotation": {
            "ALO186_TOKEN_SECRET": "180 days; rotation invalidates existing sessions",
            "ALO186_DATA_ENCRYPTION_KEY": "manual envelope-key migration required",
            "ALO186_METRICS_TOKEN": "90 days",
            "RESTIC_PASSWORD": "annual; keep old password during repository migration",
            "ALO186_SMTP_PASSWORD": "90 days or provider incident",
            "AWS_SECRET_ACCESS_KEY": "90 days",
        },
        "external_values_required": [
            "Postmark server token and verified sender",
            "Sentry DSN",
            "Cloudflare account ID and bucket-scoped R2 credentials",
        ],
    }
    (output / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (output / "README.txt").write_text(
        "Bu klasörü Git'e eklemeyin. Değerleri secret manager'a taşıdıktan sonra güvenli biçimde silin.\n",
        encoding="utf-8",
    )
    (output / "README.txt").chmod(stat.S_IRUSR | stat.S_IWUSR)

    print(f"Secret bootstrap dosyaları oluşturuldu: {output}")
    print("Secret değerleri terminale yazdırılmadı.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
