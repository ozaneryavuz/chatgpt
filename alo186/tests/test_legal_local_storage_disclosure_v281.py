from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BRIDGE = ROOT / "alo186/hesaplama/outcome-bridge.js"
PRIVACY = ROOT / "alo186/gizlilik/index.html"
COOKIE = ROOT / "alo186/yasal/cerez/index.html"
ENGLISH_OVERLAY = ROOT / "alo186/deployment/routing-overlays/english-core-run1.json"
LEGAL_OVERLAY = ROOT / "alo186/deployment/routing-overlays/107-ga4-legal-pages.json"
BUILD = ROOT / "alo186/deployment/build_static_site.py"
MARKER = 'data-alo186-outcome-storage-disclosure-v281="true"'


def integer_constant(source: str, name: str) -> int:
    match = re.search(rf"\bconst\s+{re.escape(name)}\s*=\s*(\d+)\s*;", source)
    assert match, f"{name} sabiti bulunamadı"
    return int(match.group(1))


def route_source(overlay: Path, canonical: str) -> str:
    payload = json.loads(overlay.read_text(encoding="utf-8"))
    matches = [item["source"] for item in payload["routes"] if item["canonicalPath"] == canonical]
    assert len(matches) == 1, (overlay, canonical, matches)
    return matches[0]


def assert_disclosure(html: str, label: str) -> None:
    assert html.count(MARKER) == 1, label
    for required in (
        "en fazla 45 gün",
        "rastgele yerel kayıt kimliği",
        "kaynak sınıfı",
        "teknik kategori",
        "eylem türü",
        "başlangıç ve öneri rotaları",
        "Ham Amazon URL",
        "Amazon arama sorgusu",
        "ASIN",
        "ALO186 sunucusuna gönderilmez",
        "tarayıcı site verileri",
    ):
        assert required in html, (label, required)
    for stale in (
        "en fazla 7 gün",
        "kalıcı depolama kullanmaz",
        "yalnız sayfa açıkken bellekte",
        "geçici işaret okunmaz veya yazılmaz",
    ):
        assert stale not in html, (label, stale)


def main() -> None:
    bridge = BRIDGE.read_text(encoding="utf-8")
    assert integer_constant(bridge, "TTL_DAYS") == 45
    assert "alo186:pending-solutions:v1" in bridge
    assert "root.localStorage.getItem(STORAGE_KEY)" in bridge
    assert "root.localStorage.setItem(STORAGE_KEY" in bridge
    for field in (
        "source",
        "category",
        "action",
        "originPath",
        "recommendedPath",
        "createdAt",
        "askAfter",
        "expiresAt",
    ):
        assert field in bridge, field
    for forbidden in (
        "asin",
        "orderId",
        "email",
        "phone",
        "address",
        "subscriptionNumber",
    ):
        assert forbidden not in bridge.casefold(), forbidden

    privacy = PRIVACY.read_text(encoding="utf-8")
    cookie = COOKIE.read_text(encoding="utf-8")
    assert_disclosure(privacy, "gizlilik")
    assert_disclosure(cookie, "çerez")
    assert '"lastReviewed":"2026-08-04"' in privacy
    assert "Son gözden geçirme: 4 Ağustos 2026" in privacy
    assert '"dateModified":"2026-08-04"' in cookie
    assert "Son güncelleme: 4 Ağustos 2026" in cookie

    assert route_source(ENGLISH_OVERLAY, "/gizlilik") == "alo186/gizlilik/index.html"
    assert route_source(LEGAL_OVERLAY, "/yasal/cerez") == "alo186/yasal/cerez/index.html"

    with tempfile.TemporaryDirectory(prefix="alo186-v281-") as directory:
        output = Path(directory)
        subprocess.run(
            [sys.executable, str(BUILD), "--output", str(output), "--commit", "v281-test"],
            cwd=ROOT,
            check=True,
        )
        built_privacy = (output / "gizlilik/index.html").read_text(encoding="utf-8")
        built_cookie = (output / "yasal/cerez/index.html").read_text(encoding="utf-8")
        assert_disclosure(built_privacy, "build/gizlilik")
        assert_disclosure(built_cookie, "build/yasal/cerez")
        assert "https://www.alo186.com" not in built_privacy
        assert '<link rel="canonical" href="https://alo186.com/gizlilik">' in built_privacy
        assert '<link rel="canonical" href="https://alo186.com/yasal/cerez">' in built_cookie

    print(
        json.dumps(
            {
                "ok": True,
                "version": 281,
                "ttlDays": 45,
                "storageKey": "alo186:pending-solutions:v1",
                "legalRoutes": ["/gizlilik", "/yasal/cerez"],
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
