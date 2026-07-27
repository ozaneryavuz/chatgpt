from __future__ import annotations

import argparse
import base64
import json
import os
import re
import socket
import ssl
from dataclasses import dataclass
from urllib.parse import urlparse
from urllib.request import Request, urlopen


PLACEHOLDER_MARKERS = ("replace", "change-me", "example", "development-only", "replaceme")


@dataclass
class Check:
    name: str
    ok: bool
    detail: str
    critical: bool = True


def env(name: str) -> str:
    return os.getenv(name, "").strip()


def looks_placeholder(value: str) -> bool:
    lower = value.lower()
    return not value or any(marker in lower for marker in PLACEHOLDER_MARKERS)


def check_fernet(value: str) -> bool:
    try:
        decoded = base64.urlsafe_b64decode(value.encode("ascii"))
        return len(decoded) == 32
    except Exception:
        return False


def check_url(name: str, value: str, *, https: bool = False) -> Check:
    parsed = urlparse(value)
    valid = bool(parsed.scheme and parsed.netloc)
    if https:
        valid = valid and parsed.scheme == "https"
    return Check(name, valid, value or "boş")


def resolve_host(hostname: str) -> Check:
    try:
        addresses = sorted({item[4][0] for item in socket.getaddrinfo(hostname, 443, type=socket.SOCK_STREAM)})
        return Check(f"DNS {hostname}", bool(addresses), ", ".join(addresses))
    except Exception as exc:  # noqa: BLE001
        return Check(f"DNS {hostname}", False, str(exc))


def tls_check(hostname: str, timeout: float = 8.0) -> Check:
    try:
        context = ssl.create_default_context()
        with socket.create_connection((hostname, 443), timeout=timeout) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as tls_sock:
                cert = tls_sock.getpeercert()
        return Check(f"TLS {hostname}", bool(cert.get("notAfter")), cert.get("notAfter", "sertifika okunamadı"))
    except Exception as exc:  # noqa: BLE001
        return Check(f"TLS {hostname}", False, str(exc))


def http_check(url: str, expected_status: int = 200, timeout: float = 10.0) -> Check:
    try:
        request = Request(url, headers={"User-Agent": "ALO186-Production-Preflight/1.0"})
        with urlopen(request, timeout=timeout) as response:
            return Check(f"HTTP {url}", response.status == expected_status, f"{response.status} → {response.geturl()}")
    except Exception as exc:  # noqa: BLE001
        return Check(f"HTTP {url}", False, str(exc))


def run(*, network: bool, api_base: str) -> dict[str, object]:
    checks: list[Check] = []
    environment = env("ALO186_ENV")
    database_url = env("ALO186_DATABASE_URL")
    token_secret = env("ALO186_TOKEN_SECRET")
    encryption_key = env("ALO186_DATA_ENCRYPTION_KEY")
    metrics_token = env("ALO186_METRICS_TOKEN")
    allowed_origins = env("ALO186_ALLOWED_ORIGINS")
    allowed_hosts = env("ALO186_ALLOWED_HOSTS")
    public_base_url = env("ALO186_PUBLIC_BASE_URL")
    email_backend = env("ALO186_EMAIL_BACKEND")

    checks.extend(
        [
            Check("ALO186_ENV", environment == "production", environment or "boş"),
            Check(
                "PostgreSQL URL",
                database_url.startswith(("postgresql://", "postgres://", "postgresql+psycopg://")),
                re.sub(r"://([^:@/]+):[^@/]+@", r"://\1:***@", database_url) if database_url else "boş",
            ),
            Check("Token secret", len(token_secret) >= 43 and not looks_placeholder(token_secret), f"uzunluk={len(token_secret)}"),
            Check("Fernet key", check_fernet(encryption_key), "geçerli" if check_fernet(encryption_key) else "geçersiz"),
            Check("Metrics token", len(metrics_token) >= 32 and not looks_placeholder(metrics_token), f"uzunluk={len(metrics_token)}"),
            Check("Allowed origins", allowed_origins == "https://www.alo186.com", allowed_origins or "boş"),
            Check("Allowed hosts", "api.alo186.com" in {x.strip() for x in allowed_hosts.split(",")}, allowed_hosts or "boş"),
            check_url("Public base URL", public_base_url, https=True),
            Check("Auto schema kapalı", env("ALO186_AUTO_CREATE_SCHEMA").lower() in {"false", "0", "no"}, env("ALO186_AUTO_CREATE_SCHEMA") or "boş"),
            Check("Test token kapalı", env("ALO186_EXPOSE_TEST_TOKENS").lower() in {"false", "0", "no"}, env("ALO186_EXPOSE_TEST_TOKENS") or "boş"),
            Check("Email verification açık", env("ALO186_EMAIL_VERIFICATION_REQUIRED").lower() in {"true", "1", "yes"}, env("ALO186_EMAIL_VERIFICATION_REQUIRED") or "boş"),
            Check("SMTP backend", email_backend == "smtp", email_backend or "boş"),
            Check("SMTP host", bool(env("ALO186_SMTP_HOST")), env("ALO186_SMTP_HOST") or "boş"),
            Check("SMTP username", bool(env("ALO186_SMTP_USERNAME")), "tanımlı" if env("ALO186_SMTP_USERNAME") else "boş"),
            Check("SMTP password", bool(env("ALO186_SMTP_PASSWORD")), "tanımlı" if env("ALO186_SMTP_PASSWORD") else "boş"),
            Check("SMTP from", bool(re.fullmatch(r"[^@\s]+@alo186\.com", env("ALO186_SMTP_FROM_EMAIL"))), env("ALO186_SMTP_FROM_EMAIL") or "boş"),
            Check("Sentry DSN", bool(env("ALO186_SENTRY_DSN")), "tanımlı" if env("ALO186_SENTRY_DSN") else "kapalı", critical=False),
            Check("Restic repository", bool(env("RESTIC_REPOSITORY")), "tanımlı" if env("RESTIC_REPOSITORY") else "boş"),
            Check("Restic password", bool(env("RESTIC_PASSWORD")), "tanımlı" if env("RESTIC_PASSWORD") else "boş"),
            Check("R2 access key", bool(env("AWS_ACCESS_KEY_ID")), "tanımlı" if env("AWS_ACCESS_KEY_ID") else "boş"),
            Check("R2 secret key", bool(env("AWS_SECRET_ACCESS_KEY")), "tanımlı" if env("AWS_SECRET_ACCESS_KEY") else "boş"),
        ]
    )

    if token_secret and encryption_key:
        checks.append(Check("Token/Fernet ayrımı", token_secret != encryption_key, "ayrı" if token_secret != encryption_key else "aynı değer"))

    if network:
        api_host = urlparse(api_base).hostname or "api.alo186.com"
        checks.extend(
            [
                resolve_host("www.alo186.com"),
                resolve_host(api_host),
                tls_check("www.alo186.com"),
                tls_check(api_host),
                http_check("https://www.alo186.com/robots.txt"),
                http_check(f"{api_base.rstrip('/')}/health/live"),
                http_check(f"{api_base.rstrip('/')}/health/ready"),
            ]
        )

    critical_failures = [check for check in checks if check.critical and not check.ok]
    warnings = [check for check in checks if not check.critical and not check.ok]
    return {
        "ok": not critical_failures,
        "checks": [check.__dict__ for check in checks],
        "criticalFailureCount": len(critical_failures),
        "warningCount": len(warnings),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="ALO186 production ortam preflight doğrulaması")
    parser.add_argument("--network", action="store_true", help="DNS/TLS/HTTP kontrollerini de çalıştırır.")
    parser.add_argument("--api-base", default="https://api.alo186.com")
    parser.add_argument("--output", default="")
    args = parser.parse_args()
    result = run(network=args.network, api_base=args.api_base)
    payload = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as handle:
            handle.write(payload + "\n")
    print(payload)
    raise SystemExit(0 if result["ok"] else 1)


if __name__ == "__main__":
    main()
