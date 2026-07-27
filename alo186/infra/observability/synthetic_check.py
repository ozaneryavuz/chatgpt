from __future__ import annotations

import argparse
import json
import socket
import ssl
import subprocess
import time
from datetime import datetime, timezone
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen


STATIC_PATHS = (
    "/elektrik-portali",
    "/edas-bul",
    "/karar-motoru",
    "/hesaplama/",
    "/akilli-urun-secimi",
    "/isletme-surekliligi",
)
API_PATHS = ("/health/live", "/health/ready")
REQUIRED_API_HEADERS = (
    "x-request-id",
    "x-content-type-options",
    "x-frame-options",
    "referrer-policy",
)


def resolve(hostname: str) -> dict[str, object]:
    started = time.perf_counter()
    try:
        addresses = sorted(
            {item[4][0] for item in socket.getaddrinfo(hostname, 443, type=socket.SOCK_STREAM)}
        )
        return {
            "ok": bool(addresses),
            "hostname": hostname,
            "addresses": addresses,
            "durationMs": round((time.perf_counter() - started) * 1000, 1),
        }
    except OSError as exc:
        return {
            "ok": False,
            "hostname": hostname,
            "error": str(exc),
            "durationMs": round((time.perf_counter() - started) * 1000, 1),
        }


def fetch(url: str, timeout: float, *, api_health: bool = False) -> dict[str, object]:
    started = time.perf_counter()
    request = Request(
        url,
        headers={"User-Agent": "ALO186-Synthetic/2.0", "Accept": "application/json,text/html,*/*"},
    )
    try:
        with urlopen(request, timeout=timeout) as response:
            body = response.read(64_000)
            headers = {key.lower(): value for key, value in response.headers.items()}
            result: dict[str, object] = {
                "ok": response.status == 200,
                "status": response.status,
                "finalUrl": response.geturl(),
                "contentType": headers.get("content-type"),
                "durationMs": round((time.perf_counter() - started) * 1000, 1),
                "bytesRead": len(body),
            }
            if api_health:
                try:
                    payload = json.loads(body.decode("utf-8"))
                except (UnicodeDecodeError, json.JSONDecodeError):
                    payload = None
                missing_headers = [name for name in REQUIRED_API_HEADERS if not headers.get(name)]
                status_value = payload.get("status") if isinstance(payload, dict) else None
                result.update(
                    {
                        "jsonStatus": status_value,
                        "missingSecurityHeaders": missing_headers,
                        "ok": response.status == 200
                        and status_value in {"ok", "ready"}
                        and not missing_headers,
                    }
                )
            else:
                result["ok"] = response.status == 200 and len(body) >= 200
            return result
    except (HTTPError, URLError, TimeoutError, OSError) as exc:
        return {
            "ok": False,
            "error": str(exc),
            "durationMs": round((time.perf_counter() - started) * 1000, 1),
        }


def tls_expiry(hostname: str, port: int = 443, timeout: float = 10.0) -> dict[str, object]:
    # create_default_context + server_hostname, exact ve wildcard SAN eşleşmesini
    # TLS handshake sırasında zaten doğrular; burada tekrar exact string karşılaştırması yapılmaz.
    context = ssl.create_default_context()
    with socket.create_connection((hostname, port), timeout=timeout) as sock:
        with context.wrap_socket(sock, server_hostname=hostname) as tls_sock:
            certificate = tls_sock.getpeercert()
    expires = datetime.strptime(certificate["notAfter"], "%b %d %H:%M:%S %Y %Z").replace(
        tzinfo=timezone.utc
    )
    remaining = expires - datetime.now(timezone.utc)
    sans = [value for kind, value in certificate.get("subjectAltName", []) if kind == "DNS"]
    return {
        "ok": remaining.days >= 21,
        "hostname": hostname,
        "expiresAt": expires.isoformat(),
        "daysRemaining": remaining.days,
        "hostnameVerifiedByTlsContext": True,
        "subjectAltNames": sans,
        "issuer": dict(item[0] for item in certificate.get("issuer", [])),
    }


def dig_txt(name: str) -> list[str]:
    try:
        process = subprocess.run(
            ["dig", "+short", "TXT", name],
            check=False,
            capture_output=True,
            text=True,
            timeout=15,
        )
    except (OSError, subprocess.TimeoutExpired):
        return []
    return [line.strip().replace('"', "") for line in process.stdout.splitlines() if line.strip()]


def email_dns(domain: str) -> list[dict[str, object]]:
    spf = [value for value in dig_txt(domain) if "v=spf1" in value.lower()]
    dmarc = dig_txt(f"_dmarc.{domain}")
    return [
        {"ok": len(spf) == 1, "kind": "email-dns", "name": "spf", "recordCount": len(spf)},
        {
            "ok": any("V=DMARC1" in value.upper() for value in dmarc),
            "kind": "email-dns",
            "name": "dmarc",
            "recordCount": len(dmarc),
        },
    ]


def hostname(base_url: str) -> str:
    parsed = urlparse(base_url)
    if parsed.scheme != "https" or not parsed.hostname:
        raise ValueError(f"HTTPS base URL bekleniyor: {base_url}")
    return parsed.hostname


def run(
    web_base: str,
    api_base: str,
    timeout: float,
    *,
    check_email_dns: bool = False,
    email_domain: str = "alo186.com",
) -> dict[str, object]:
    web_host, api_host = hostname(web_base), hostname(api_base)
    dns_checks = [resolve(web_host), resolve(api_host)]
    checks: list[dict[str, object]] = []
    for path in STATIC_PATHS:
        result = fetch(f"{web_base.rstrip('/')}{path}", timeout)
        result.update({"kind": "web", "path": path})
        checks.append(result)
    for path in API_PATHS:
        result = fetch(f"{api_base.rstrip('/')}{path}", timeout, api_health=True)
        result.update({"kind": "api", "path": path})
        checks.append(result)

    tls_checks = []
    for host in {web_host, api_host}:
        try:
            tls_checks.append(tls_expiry(host, timeout=timeout))
        except Exception as exc:  # noqa: BLE001
            tls_checks.append({"ok": False, "hostname": host, "error": str(exc)})

    email_checks = email_dns(email_domain) if check_email_dns else []
    all_checks = [*dns_checks, *checks, *tls_checks, *email_checks]
    failures = [item for item in all_checks if not item.get("ok")]
    return {
        "ok": not failures,
        "checkedAt": datetime.now(timezone.utc).isoformat(),
        "webBase": web_base,
        "apiBase": api_base,
        "dns": dns_checks,
        "checks": checks,
        "tls": tls_checks,
        "emailDns": email_checks,
        "failureCount": len(failures),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="ALO186 web/API/DNS/TLS sentetik kontrolü")
    parser.add_argument("--web-base", default="https://www.alo186.com")
    parser.add_argument("--api-base", default="https://api.alo186.com")
    parser.add_argument("--timeout", type=float, default=15.0)
    parser.add_argument("--output", default="")
    parser.add_argument("--check-email-dns", action="store_true")
    parser.add_argument("--email-domain", default="alo186.com")
    args = parser.parse_args()
    result = run(
        args.web_base,
        args.api_base,
        args.timeout,
        check_email_dns=args.check_email_dns,
        email_domain=args.email_domain,
    )
    payload = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as handle:
            handle.write(payload + "\n")
    print(payload)
    raise SystemExit(0 if result["ok"] else 1)


if __name__ == "__main__":
    main()
