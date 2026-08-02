from __future__ import annotations

import json
import re
import sys
import tempfile
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[2]
DEPLOYMENT = ROOT / "alo186/deployment"
sys.path.insert(0, str(DEPLOYMENT))

from build_static_site import build  # noqa: E402
from guard_commerce_routes_v2 import COMMERCIAL_ROUTES, SERVICE_ROUTES  # noqa: E402

CANONICAL_ORIGIN = "https://alo186.com"
LEGACY_ORIGIN = "https://www.alo186.com"
CANONICAL_LINK = re.compile(r'<link\s+rel=["\']canonical["\']\s+href=["\']([^"\']+)["\']', re.I)
MALFORMED_HUB_URL = re.compile(r"https://alo186\.com/amazon-elektrik-urunleri(?=[a-z0-9])", re.I)
UX_MARKER = 'data-alo186-user-experience="true"'


def normalized_path(value: str) -> str:
    return (urlsplit(value).path or "/").rstrip("/") or "/"


def source_canonical_path(route: str) -> None:
    page = ROOT / "alo186" / route.strip("/") / "index.html"
    assert page.is_file(), page
    html = page.read_text(encoding="utf-8")
    match = CANONICAL_LINK.search(html)
    assert match, route
    parsed = urlsplit(match.group(1))
    assert parsed.scheme == "https", (route, match.group(1))
    assert parsed.hostname in {"alo186.com", "www.alo186.com"}, (route, match.group(1))
    assert normalized_path(match.group(1)) == normalized_path(route), (route, match.group(1))


def artifact_contract() -> dict:
    with tempfile.TemporaryDirectory() as directory:
        site = Path(directory) / "site"
        release = build(ROOT, site, "commerce-canonical-v217-test")
        report = release["commercialCanonicalV217"]
        ux_report = release["userExperiencePreflightV217"]
        assert report["version"] == 217
        assert report["canonicalOrigin"] == CANONICAL_ORIGIN
        assert report["artifactLegacyWwwRejected"] is True
        assert ux_report["version"] == 217
        assert ux_report["caseInsensitiveHeadInsertion"] is True
        assert ux_report["formsResponsive"] is True
        assert ux_report["injectedPages"] > 0

        for route in (*COMMERCIAL_ROUTES, *SERVICE_ROUTES):
            page = site / route.strip("/") / "index.html"
            assert page.is_file(), page
            html = page.read_text(encoding="utf-8")
            expected = f'rel="canonical" href="{CANONICAL_ORIGIN}{route}"'
            legacy = f'rel="canonical" href="{LEGACY_ORIGIN}{route}"'
            assert expected in html, (route, expected)
            assert legacy not in html, (route, legacy)
            assert UX_MARKER in html, route

        power_station = site / "hesaplama/power-station-kapasite-eps-uygunluk/index.html"
        assert power_station.is_file()
        assert UX_MARKER in power_station.read_text(encoding="utf-8")

        hub = (site / "amazon-elektrik-urunleri/index.html").read_text(encoding="utf-8")
        assert not MALFORMED_HUB_URL.search(hub)
        assert "https://alo186.com/amazon-elektrik-urunleri/modem-ont-mini-ups-yedekleme-secici/" in hub
        assert "https://alo186.com/amazon-elektrik-urunleri/nas-ups-usb-snmp-uygunluk-secici/" in hub
        release_file = json.loads((site / "alo186-release.json").read_text(encoding="utf-8"))
        assert release_file["commercialCanonicalV217"] == report
        assert release_file["userExperiencePreflightV217"] == ux_report
        return {**report, "userExperiencePreflight": ux_report}


def main() -> None:
    for route in (*COMMERCIAL_ROUTES, *SERVICE_ROUTES):
        source_canonical_path(route)
    report = artifact_contract()
    print(json.dumps({"ok": True, **report}, ensure_ascii=False))


if __name__ == "__main__":
    main()
