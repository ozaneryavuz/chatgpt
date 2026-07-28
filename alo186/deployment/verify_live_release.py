from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path
from typing import Iterable
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import HTTPRedirectHandler, Request, build_opener

CANONICAL_HOST = "https://www.alo186.com"
DEFAULT_CRITICAL_PATHS = (
    "/elektrik-portali",
    "/edas-bul",
    "/karar-motoru",
    "/hesaplama/",
    "/akilli-urun-secimi",
    "/isletme-surekliligi",
    "/hesaplama/elektrik-surekliligi-pasaportu/",
    "/hesaplama/elektrik-kesintisi-tatbikati/",
)


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def parse_checksums(text: str) -> dict[str, str]:
    checksums: dict[str, str] = {}
    for line_number, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        if not line:
            continue
        try:
            digest, path = line.split("  ", 1)
        except ValueError as exc:
            raise ValueError(f"checksums.sha256 satır {line_number} geçersiz") from exc
        if len(digest) != 64 or any(char not in "0123456789abcdef" for char in digest.lower()):
            raise ValueError(f"checksums.sha256 satır {line_number} SHA-256 değil")
        normalized = path.strip().lstrip("./")
        if not normalized or normalized in checksums:
            raise ValueError(f"checksums.sha256 satır {line_number} yol geçersiz/tekrarlı")
        checksums[normalized] = digest.lower()
    if not checksums:
        raise ValueError("checksums.sha256 boş")
    return checksums


def route_bundle_path(path: str) -> str:
    normalized = "/" + path.strip("/")
    if normalized == "/":
        raise ValueError("Kök rota production bundle içinde canonical index değildir.")
    return normalized.strip("/") + "/index.html"


def fetch_bytes(url: str, *, timeout: int = 20) -> tuple[int, str, bytes, dict[str, str], float]:
    request = Request(
        url,
        headers={
            "User-Agent": "ALO186-Release-Drift-Guard/1.0",
            "Accept": "application/json,text/html,text/plain,*/*",
            "Accept-Encoding": "identity",
            "Cache-Control": "no-cache, no-store, max-age=0",
            "Pragma": "no-cache",
        },
    )
    started = time.perf_counter()
    with build_opener(HTTPRedirectHandler()).open(request, timeout=timeout) as response:
        payload = response.read()
        return (
            response.status,
            response.geturl(),
            payload,
            {key.lower(): value for key, value in response.headers.items()},
            time.perf_counter() - started,
        )


def _cache_busted(base_url: str, path: str, expected_commit: str) -> str:
    separator = "&" if "?" in path else "?"
    return f"{base_url.rstrip('/')}{path}{separator}{urlencode({'__alo186_release': expected_commit[:16]})}"


def _load_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON nesnesi bekleniyordu: {path}")
    return value


def validate_release_contract(local: dict, live: dict, expected_commit: str) -> list[str]:
    failures: list[str] = []
    required_equal = (
        "schemaVersion",
        "canonicalHost",
        "routeCount",
        "deviceDamageDeadline",
        "publicArtifactPolicy",
    )
    for key in required_equal:
        if live.get(key) != local.get(key):
            failures.append(f"release metadata farklı: {key} beklenen={local.get(key)!r} canlı={live.get(key)!r}")
    if live.get("commit") != expected_commit:
        failures.append(
            f"canlı release commit farklı: beklenen={expected_commit} canlı={live.get('commit')!r}"
        )
    if live.get("canonicalHost") != CANONICAL_HOST:
        failures.append(f"canlı release canonical host yanlış: {live.get('canonicalHost')!r}")
    if live.get("deviceDamageDeadline") != "10 iş günü":
        failures.append("canlı release cihaz hasarı süresi 10 iş günü değil")
    return failures


def verify(
    *,
    base_url: str,
    bundle: Path,
    expected_commit: str | None = None,
    critical_paths: Iterable[str] = DEFAULT_CRITICAL_PATHS,
    allow_content_drift: bool = False,
    timeout: int = 20,
) -> dict:
    bundle = bundle.resolve()
    local_release_path = bundle / "alo186-release.json"
    local_checksums_path = bundle / "checksums.sha256"
    if not local_release_path.is_file() or not local_checksums_path.is_file():
        raise FileNotFoundError("Bundle içinde alo186-release.json ve checksums.sha256 zorunludur.")

    local_release = _load_json(local_release_path)
    expected_commit = expected_commit or str(local_release.get("commit") or "")
    if not expected_commit or expected_commit == "local":
        raise ValueError("Beklenen production commit SHA açıkça verilmelidir.")
    local_checksums = parse_checksums(local_checksums_path.read_text(encoding="utf-8"))

    failures: list[str] = []
    results: list[dict] = []

    try:
        status, final_url, payload, headers, duration = fetch_bytes(
            _cache_busted(base_url, "/alo186-release.json", expected_commit), timeout=timeout
        )
        live_release = json.loads(payload.decode("utf-8"))
        if not isinstance(live_release, dict):
            raise ValueError("release JSON nesne değil")
        results.append(
            {
                "path": "/alo186-release.json",
                "status": status,
                "finalUrl": final_url,
                "contentType": headers.get("content-type"),
                "durationMs": round(duration * 1000, 1),
                "commit": live_release.get("commit"),
            }
        )
        failures.extend(validate_release_contract(local_release, live_release, expected_commit))
    except (HTTPError, URLError, TimeoutError, ValueError, json.JSONDecodeError) as exc:
        live_release = None
        failures.append(
            "production GitHub artifact'ını sunmuyor veya release metadata okunamadı: " + str(exc)
        )
        results.append({"path": "/alo186-release.json", "error": str(exc)})

    try:
        status, final_url, payload, headers, duration = fetch_bytes(
            _cache_busted(base_url, "/checksums.sha256", expected_commit), timeout=timeout
        )
        live_checksums = parse_checksums(payload.decode("utf-8"))
        results.append(
            {
                "path": "/checksums.sha256",
                "status": status,
                "finalUrl": final_url,
                "contentType": headers.get("content-type"),
                "durationMs": round(duration * 1000, 1),
                "entries": len(live_checksums),
            }
        )
    except (HTTPError, URLError, TimeoutError, UnicodeDecodeError, ValueError) as exc:
        live_checksums = {}
        failures.append("canlı checksums.sha256 yok veya geçersiz: " + str(exc))
        results.append({"path": "/checksums.sha256", "error": str(exc)})

    for path in critical_paths:
        bundle_path = route_bundle_path(path)
        expected_hash = local_checksums.get(bundle_path)
        if not expected_hash:
            failures.append(f"local checksum kritik rota için eksik: {bundle_path}")
            continue
        manifest_hash = live_checksums.get(bundle_path)
        if manifest_hash != expected_hash:
            failures.append(
                f"canlı checksum manifest drift: {bundle_path} beklenen={expected_hash} canlı={manifest_hash!r}"
            )
        try:
            status, final_url, payload, headers, duration = fetch_bytes(
                _cache_busted(base_url, path, expected_commit), timeout=timeout
            )
            live_hash = sha256_bytes(payload)
            matched = live_hash == expected_hash
            results.append(
                {
                    "path": path,
                    "bundlePath": bundle_path,
                    "status": status,
                    "finalUrl": final_url,
                    "contentType": headers.get("content-type"),
                    "durationMs": round(duration * 1000, 1),
                    "expectedSha256": expected_hash,
                    "liveSha256": live_hash,
                    "matched": matched,
                }
            )
            if status != 200:
                failures.append(f"{path}: HTTP {status}")
            if not matched and not allow_content_drift:
                failures.append(
                    f"canlı route byte drift: {path} beklenen={expected_hash} canlı={live_hash}"
                )
        except (HTTPError, URLError, TimeoutError) as exc:
            failures.append(f"{path}: canlı route okunamadı: {exc}")
            results.append({"path": path, "bundlePath": bundle_path, "error": str(exc)})

    return {
        "ok": not failures,
        "baseUrl": base_url.rstrip("/"),
        "expectedCommit": expected_commit,
        "localRouteCount": local_release.get("routeCount"),
        "allowContentDrift": allow_content_drift,
        "results": results,
        "failures": failures,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="GitHub production bundle ile canlı ALO186 release/checksum drift denetimi."
    )
    parser.add_argument("--base-url", default=CANONICAL_HOST)
    parser.add_argument("--bundle", type=Path, required=True)
    parser.add_argument("--expected-commit", required=True)
    parser.add_argument("--path", action="append", dest="paths")
    parser.add_argument("--allow-content-drift", action="store_true")
    parser.add_argument("--timeout", type=int, default=20)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()

    report = verify(
        base_url=args.base_url,
        bundle=args.bundle,
        expected_commit=args.expected_commit,
        critical_paths=args.paths or DEFAULT_CRITICAL_PATHS,
        allow_content_drift=args.allow_content_drift,
        timeout=max(3, args.timeout),
    )
    text = json.dumps(report, ensure_ascii=False, indent=2)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(text + "\n", encoding="utf-8")
    print(text)
    raise SystemExit(0 if report["ok"] else 1)


if __name__ == "__main__":
    main()
