#!/usr/bin/env python3
from __future__ import annotations

import argparse
import base64
import json
import os
import re
import socket
import ssl
import sys
import urllib.parse
from dataclasses import dataclass, asdict
from datetime import datetime, timezone


@dataclass
class Check:
    name: str
    ok: bool
    detail: str
    severity: str = "error"


def secret(name: str) -> str:
    direct = os.getenv(name)
    file_path = os.getenv(f"{name}_FILE")
    if direct and file_path:
        return ""
    if file_path:
        try:
            return open(file_path, encoding="utf-8").read().strip()
        except OSError:
            return ""
    return direct or ""


def check_env() -> list[Check]:
    checks: list[Check] = []
    required = [
        "ALO186_DATABASE_URL",
        "ALO186_TOKEN_SECRET",
        "ALO186_DATA_ENCRYPTION_KEY",
        "ALO186_SMTP_HOST",
        "ALO186_SMTP_USERNAME",
        "ALO186_SMTP_PASSWORD",
        "ALO186_SMTP_FROM_EMAIL",
        "ALO186_ALLOWED_ORIGINS",
        "ALO186_ALLOWED_HOSTS",
        "ALO186_PUBLIC_BASE_URL",
    ]
    for name in required:
        value = secret(name) if name in {"ALO186_DATABASE_URL", "ALO186_TOKEN_SECRET", "ALO186_DATA_ENCRYPTION_KEY", "ALO186_SMTP_PASSWORD"} else os.getenv(name, "")
        checks.append(Check(f"env:{name}", bool(value), "tanımlı" if value else "eksik"))

    db = secret("ALO186_DATABASE_URL")
    checks.append(Check("database:postgres", db.startswith(("postgresql://", "postgresql+psycopg://", "postgres://")), "PostgreSQL URL" if db else "eksik"))

    token = secret("ALO186_TOKEN_SECRET")
    checks.append(Check("secret:token-entropy", len(token) >= 43, f"uzunluk={len(token)}"))

    key = secret("ALO186_DATA_ENCRYPTION_KEY")
    try:
        raw = base64.urlsafe_b64decode(key.encode("ascii"))
        valid_key = len(raw) == 32
    except Exception:
        valid_key = False
    checks.append(Check("secret:fernet-key", valid_key, "32 byte urlsafe base64" if valid_key else "geçersiz"))

    public = os.getenv("ALO186_PUBLIC_BASE_URL", "")
    parsed = urllib.parse.urlparse(public)
    checks.append(Check("url:public-https", parsed.scheme == "https" and bool(parsed.netloc), public or "eksik"))

    origins = [x.strip() for x in os.getenv("ALO186_ALLOWED_ORIGINS", "").split(",") if x.strip()]
    checks.append(Check("cors:no-wildcard", bool(origins) and "*" not in origins, ",".join(origins) or "eksik"))

    hosts = [x.strip() for x in os.getenv("ALO186_ALLOWED_HOSTS", "").split(",") if x.strip()]
    checks.append(Check("hosts:no-wildcard", bool(hosts) and "*" not in hosts, ",".join(hosts) or "eksik"))

    email = os.getenv("ALO186_SMTP_FROM_EMAIL", "")
    checks.append(Check("smtp:from-email", bool(re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email)), email or "eksik"))

    backup_vars = ["RESTIC_REPOSITORY", "RESTIC_PASSWORD", "AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY"]
    for name in backup_vars:
        checks.append(Check(f"backup:{name}", bool(os.getenv(name)), "tanımlı" if os.getenv(name) else "eksik", severity="warning"))

    checks.append(Check("sentry:dsn", bool(secret("ALO186_SENTRY_DSN")), "tanımlı" if secret("ALO186_SENTRY_DSN") else "opsiyonel/eksik", severity="warning"))
    return checks


def online_checks(api_url: str, min_tls_days: int = 21) -> list[Check]:
    parsed = urllib.parse.urlparse(api_url)
    host = parsed.hostname or ""
    checks: list[Check] = []
    try:
        addresses = sorted({item[4][0] for item in socket.getaddrinfo(host, 443, type=socket.SOCK_STREAM)})
        checks.append(Check("online:dns", bool(addresses), ", ".join(addresses)))
    except Exception as exc:
        checks.append(Check("online:dns", False, str(exc)))

    try:
        context = ssl.create_default_context()
        with socket.create_connection((host, parsed.port or 443), timeout=10) as raw:
            with context.wrap_socket(raw, server_hostname=host) as tls:
                cert = tls.getpeercert()
        expires = datetime.strptime(cert["notAfter"], "%b %d %H:%M:%S %Y %Z").replace(tzinfo=timezone.utc)
        days = (expires - datetime.now(timezone.utc)).total_seconds() / 86400
        checks.append(Check("online:tls-expiry", days >= min_tls_days, f"{days:.1f} gün"))
    except Exception as exc:
        checks.append(Check("online:tls-expiry", False, str(exc)))
    return checks


def main() -> int:
    parser = argparse.ArgumentParser(description="ALO186 production readiness doğrulaması")
    parser.add_argument("--online", action="store_true")
    parser.add_argument("--api-url", default="https://api.alo186.com")
    parser.add_argument("--json-output")
    args = parser.parse_args()

    checks = check_env()
    if args.online:
        checks.extend(online_checks(args.api_url))

    hard_failures = [item for item in checks if not item.ok and item.severity == "error"]
    result = {
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "ready": not hard_failures,
        "checks": [asdict(item) for item in checks],
    }
    rendered = json.dumps(result, ensure_ascii=False, indent=2)
    print(rendered)
    if args.json_output:
        with open(args.json_output, "w", encoding="utf-8") as handle:
            handle.write(rendered + "\n")
    return 0 if result["ready"] else 1


if __name__ == "__main__":
    sys.exit(main())
