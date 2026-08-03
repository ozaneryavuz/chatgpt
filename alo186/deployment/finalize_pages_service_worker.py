from __future__ import annotations

import json
from pathlib import Path

MARKER = "data-alo186-pages-sw"


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
