from __future__ import annotations

import argparse
import json
import socket
import ssl
import time
from datetime import datetime, timezone
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


STATIC_PATHS = (
    "/elektrik-portali",
    "/edas-bul",
    "/karar-motoru",
    "/hesaplama/",
    "/akilli-urun-secimi",
    "/isletme-surekliligi",
)
API_PATHS = ("/health/live", "/health/ready", "/api/v1/kg/public/health")


def fetch(url: str, timeout: float) -> dict[str, object]:
    started = time.perf_counter()
    request = Request(url, headers={"User-Agent": "ALO186-Synthetic/1.1", "Accept": "application/json,text/html,*/*"})
    try:
        with urlopen(request, timeout=timeout) as response:
            body = response.read(64_000)
            result: dict[str, object] = {
                "ok": response.status == 200,
                "status": response.status,
                "finalUrl": response.geturl(),
                "contentType": response.headers.get("content-type"),
                "durationMs": round((time.perf_counter() - started) * 1000, 1),
                "bytesRead": len(body),
            }
            if url.endswith("/api/v1/kg/public/health") and response.status == 200:
                try:
                    payload = json.loads(body.decode("utf-8"))
                    score = float(payload.get("score", 0))
                    result["knowledgeGraphScore"] = score
                    result["knowledgeGraphEntities"] = int(payload.get("entities", 0))
                    result["knowledgeGraphAssertions"] = int(payload.get("assertions", 0))
                    result["ok"] = score >= 70 and int(payload.get("entities", 0)) > 0
                    if not result["ok"]:
                        result["error"] = "Knowledge Graph boş veya health skoru 70 altında."
                except (ValueError, TypeError, json.JSONDecodeError) as exc:
                    result["ok"] = False
                    result["error"] = f"Knowledge Graph health cevabı okunamadı: {exc}"
            return result
    except (HTTPError, URLError, TimeoutError) as exc:
        return {
            "ok": False,
            "error": str(exc),
            "durationMs": round((time.perf_counter() - started) * 1000, 1),
        }


def tls_expiry(hostname: str, port: int = 443, timeout: float = 10.0) -> dict[str, object]:
    context = ssl.create_default_context()
    with socket.create_connection((hostname, port), timeout=timeout) as sock:
        with context.wrap_socket(sock, server_hostname=hostname) as tls_sock:
            certificate = tls_sock.getpeercert()
    expires = datetime.strptime(certificate["notAfter"], "%b %d %H:%M:%S %Y %Z").replace(tzinfo=timezone.utc)
    remaining = expires - datetime.now(timezone.utc)
    return {
        "ok": remaining.days >= 21,
        "hostname": hostname,
        "expiresAt": expires.isoformat(),
        "daysRemaining": remaining.days,
        "issuer": dict(item[0] for item in certificate.get("issuer", [])),
    }


def run(web_base: str, api_base: str, timeout: float) -> dict[str, object]:
    checks: list[dict[str, object]] = []
    for path in STATIC_PATHS:
        result = fetch(f"{web_base.rstrip('/')}{path}", timeout)
        result.update({"kind": "web", "path": path})
        checks.append(result)
    for path in API_PATHS:
        result = fetch(f"{api_base.rstrip('/')}{path}", timeout)
        result.update({"kind": "api", "path": path})
        checks.append(result)

    tls_checks = []
    for hostname in {web_base.split("//", 1)[-1].split("/", 1)[0], api_base.split("//", 1)[-1].split("/", 1)[0]}:
        try:
            tls_checks.append(tls_expiry(hostname, timeout=timeout))
        except Exception as exc:  # noqa: BLE001
            tls_checks.append({"ok": False, "hostname": hostname, "error": str(exc)})

    failures = [item for item in checks + tls_checks if not item.get("ok")]
    return {
        "ok": not failures,
        "checkedAt": datetime.now(timezone.utc).isoformat(),
        "webBase": web_base,
        "apiBase": api_base,
        "checks": checks,
        "tls": tls_checks,
        "failureCount": len(failures),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="ALO186 web/API/TLS/Knowledge Graph synthetic kontrolü")
    parser.add_argument("--web-base", default="https://www.alo186.com")
    parser.add_argument("--api-base", default="https://api.alo186.com")
    parser.add_argument("--timeout", type=float, default=15.0)
    parser.add_argument("--output", default="")
    args = parser.parse_args()
    result = run(args.web_base, args.api_base, args.timeout)
    payload = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as handle:
            handle.write(payload + "\n")
    print(payload)
    raise SystemExit(0 if result["ok"] else 1)


if __name__ == "__main__":
    main()
