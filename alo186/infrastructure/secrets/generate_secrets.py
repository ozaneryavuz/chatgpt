#!/usr/bin/env python3
from __future__ import annotations

import argparse
import base64
import os
import secrets
from pathlib import Path


def values() -> dict[str, str]:
    return {
        "ALO186_TOKEN_SECRET": secrets.token_urlsafe(48),
        "ALO186_DATA_ENCRYPTION_KEY": base64.urlsafe_b64encode(os.urandom(32)).decode("ascii"),
        "ALO186_METRICS_TOKEN": secrets.token_urlsafe(32),
        "RESTIC_PASSWORD": secrets.token_urlsafe(48),
        "ALO186_VAULT_ENCRYPTION_KEY": secrets.token_urlsafe(48),
        "ALO186_WEBHOOK_SECRET": secrets.token_urlsafe(40),
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="ALO186 üretim için yerel secret başlangıç paketi üretir; değerleri ekrana yazmaz."
    )
    parser.add_argument(
        "--output",
        default="generated/alo186-production-secrets.env",
        help="Repository dışında veya gitignore altında tutulacak çıktı dosyası.",
    )
    parser.add_argument("--force", action="store_true", help="Var olan dosyanın üzerine yaz.")
    args = parser.parse_args()

    target = Path(args.output).expanduser().resolve()
    if target.exists() and not args.force:
        raise SystemExit(f"Dosya zaten var: {target}. Üzerine yazmak için --force kullanın.")
    target.parent.mkdir(parents=True, exist_ok=True)

    payload = values()
    lines = [
        "# ALO186 production bootstrap secrets",
        "# Bu dosyayı Git'e eklemeyin. Değerleri sağlayıcı secret manager'a taşıdıktan sonra güvenli kasada saklayın.",
        *(f"{key}={value}" for key, value in payload.items()),
        "",
    ]
    target.write_text("\n".join(lines), encoding="utf-8")
    os.chmod(target, 0o600)

    print(f"Secret paketi oluşturuldu: {target}")
    print("Üretilen anahtarlar: " + ", ".join(payload))
    print("Secret değerleri güvenlik nedeniyle stdout'a yazılmadı.")


if __name__ == "__main__":
    main()
