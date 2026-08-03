from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

MARKER = "data-alo186-pages-sw"
RECEIPT_KEY = "serviceWorkerRegistrationFinalization"


def normalize_base_path(value: str) -> str:
    cleaned = str(value or "").strip()
    if not cleaned or cleaned == "/":
        return ""
    return "/" + cleaned.strip("/")


def public_url(base_path: str, route: str) -> str:
    route = "/" + str(route or "").lstrip("/")
    if not base_path:
        return route
    if route == "/":
        return base_path + "/"
    return base_path + route


def registration_html(base_path: str) -> str:
    sw_url = public_url(base_path, "/sw.js")
    scope = public_url(base_path, "/")
    return (
        f'<script {MARKER}>'
        "if('serviceWorker'in navigator){addEventListener('load',()=>"
        f"navigator.serviceWorker.register({json.dumps(sw_url)},"
        f"{{scope:{json.dumps(scope)}}}).catch(()=>{{}}));}}"
        "</script>"
    )


def finalize(site: Path, base_path: str) -> dict:
    site = Path(site).resolve()
    normalized = normalize_base_path(base_path)
    registration = registration_html(normalized)
    injected = 0
    preserved = 0

    html_files = sorted(site.rglob("*.html"))
    if not html_files:
        raise RuntimeError("Service worker finalizasyonu için HTML sayfası bulunamadı")

    for path in html_files:
        text = path.read_text(encoding="utf-8")
        if MARKER in text:
            preserved += 1
            continue
        if "</body>" not in text:
            raise RuntimeError(
                f"Service worker finalizasyonu için geçersiz HTML: {path.relative_to(site)}"
            )
        path.write_text(
            text.replace("</body>", registration + "\n</body>", 1),
            encoding="utf-8",
        )
        injected += 1

    return {
        "ok": True,
        "basePath": normalized,
        "injectedPages": injected,
        "preservedPages": preserved,
        "checkedPages": len(html_files),
        "serviceWorker": public_url(normalized, "/sw.js"),
        "scope": public_url(normalized, "/"),
    }


def _merge_receipt(existing: object, report: dict) -> dict:
    if not isinstance(existing, dict) or existing.get("basePath") != report.get("basePath"):
        return report
    merged = dict(report)
    merged["injectedPages"] = int(existing.get("injectedPages") or 0) + int(
        report.get("injectedPages") or 0
    )
    merged["runs"] = int(existing.get("runs") or 1) + 1
    return merged


def record_receipt(site: Path, report: dict) -> None:
    for name in ("alo186-release.json", "pages-release.json"):
        path = site / name
        if not path.is_file():
            continue
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload[RECEIPT_KEY] = _merge_receipt(payload.get(RECEIPT_KEY), report)
        path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )


def recompute_checksums(site: Path) -> None:
    path = site / "checksums.sha256"
    if path.exists():
        path.unlink()
    files = sorted(item for item in site.rglob("*") if item.is_file())
    path.write_text(
        "\n".join(
            f"{hashlib.sha256(item.read_bytes()).hexdigest()}  {item.relative_to(site).as_posix()}"
            for item in files
        )
        + "\n",
        encoding="utf-8",
    )


def finalize_and_record(site: Path, base_path: str) -> dict:
    resolved = Path(site).resolve()
    report = finalize(resolved, base_path)
    record_receipt(resolved, report)
    recompute_checksums(resolved)
    return report


def main() -> None:
    parser = argparse.ArgumentParser(
        description="ALO186 final Pages artifact service worker kayıtlarını tamamla"
    )
    parser.add_argument("--site", type=Path, required=True)
    parser.add_argument("--base-path", default="")
    args = parser.parse_args()
    print(
        json.dumps(
            finalize_and_record(args.site, args.base_path),
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
