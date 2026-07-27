from __future__ import annotations

import argparse
import json
import os
import secrets
from pathlib import Path

from cryptography.fernet import Fernet


def generate() -> dict[str, str]:
    return {
        "ALO186_TOKEN_SECRET": secrets.token_urlsafe(64),
        "ALO186_DATA_ENCRYPTION_KEY": Fernet.generate_key().decode("ascii"),
        "ALO186_METRICS_TOKEN": secrets.token_urlsafe(48),
        "RESTIC_PASSWORD": secrets.token_urlsafe(48),
    }


def shell_format(values: dict[str, str]) -> str:
    return "\n".join(f"{key}={json.dumps(value)}" for key, value in values.items()) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="ALO186 production secret seti üretir.")
    parser.add_argument("--format", choices=("json", "shell"), default="json")
    parser.add_argument("--output", type=Path, help="Secret değerlerini 0600 izinli dosyaya yazar.")
    args = parser.parse_args()

    values = generate()
    payload = json.dumps(values, ensure_ascii=False, indent=2) + "\n" if args.format == "json" else shell_format(values)
    if args.output:
        output = args.output.expanduser().resolve()
        output.parent.mkdir(parents=True, exist_ok=True)
        fd = os.open(output, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(payload)
        os.chmod(output, 0o600)
        print(f"Secret dosyası oluşturuldu: {output} (izin 0600)")
        return

    print("UYARI: Çıktı secret içerir; CI loguna veya issue yorumuna kopyalamayın.", file=os.sys.stderr)
    print(payload, end="")


if __name__ == "__main__":
    main()
