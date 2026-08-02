from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DEPLOYMENT = REPO_ROOT / "alo186/deployment"
sys.path.insert(0, str(DEPLOYMENT))

from build_static_site import build, load_effective_manifest  # noqa: E402
from canonical_aliases import CANONICAL_HOST, load_alias_map  # noqa: E402

EXPECTED_CANONICALS = {
    "/haberler/jenerator-reverse-power-ansi-32r-motoring-ct-polarite-teshis",
    "/haberler/ups-fan-failure-overtemperature-hava-akisi-filtre-teshis",
    "/haberler/jenerator-underfrequency-dusuk-frekans-governor-yuk-adimi-teshis",
}

EXPECTED_ALIASES = {
    "/haberler/jenerator-ters-guc-reverse-power-alarmi-ansi-32",
    "/haberler/jenerator-ters-guc-reverse-power-alarmi-ansi-32r",
    "/haberler/jenerator-reverse-power-ters-guc-ansi-32r-motoring-koruma",
    "/haberler/jenerator-reverse-power-ansi-32r-negatif-kw-ct-polarite-teshis",
    "/haberler/ups-fan-failure-overtemperature-yuksek-sicaklik-derating-teshis",
    "/haberler/jenerator-underfrequency-dusuk-frekans-governor-hunting-yuk-alma",
}


def test_alias_registry_is_complete_and_routes_exist() -> None:
    aliases = load_alias_map()
    manifest = load_effective_manifest(REPO_ROOT)
    paths = {route["canonicalPath"] for route in manifest["routes"]}

    assert manifest["version"] >= 208
    assert set(aliases) == EXPECTED_ALIASES
    assert set(aliases.values()) == EXPECTED_CANONICALS
    assert EXPECTED_ALIASES | EXPECTED_CANONICALS <= paths
    assert all(alias != target for alias, target in aliases.items())


def test_production_build_consolidates_intents(tmp_path: Path) -> None:
    aliases = load_alias_map()
    output = tmp_path / "site"
    release = build(REPO_ROOT, output, "intent-consolidation-v208-test")

    assert release["routingVersion"] >= 208
    sitemap = (output / "sitemap.xml").read_text(encoding="utf-8")

    for canonical in EXPECTED_CANONICALS:
        assert f"{CANONICAL_HOST}{canonical}" in sitemap
        canonical_html = (output / canonical.strip("/") / "index.html").read_text(encoding="utf-8")
        assert '<meta name="robots" content="index,follow,max-image-preview:large">' in canonical_html
        assert f'<link rel="canonical" href="{CANONICAL_HOST}{canonical}">' in canonical_html

    for alias, canonical in aliases.items():
        assert f"{CANONICAL_HOST}{alias}" not in sitemap
        alias_html = (output / alias.strip("/") / "index.html").read_text(encoding="utf-8")
        canonical_url = f"{CANONICAL_HOST}{canonical}"
        assert '<meta name="robots" content="noindex,follow">' in alias_html
        assert f'<link rel="canonical" href="{canonical_url}">' in alias_html
        assert f'<meta http-equiv="refresh" content="0; url={canonical_url}">' in alias_html
        assert "location.replace(" in alias_html
        assert "bağımsız bir bilgi platformudur" in alias_html
        assert "amazon." not in alias_html.casefold()
        assert '"Product"' not in alias_html and '"Offer"' not in alias_html


def test_internal_links_are_rewritten_to_canonical_targets(tmp_path: Path) -> None:
    aliases = load_alias_map()
    output = tmp_path / "site"
    build(REPO_ROOT, output, "intent-link-rewrite-v208-test")

    excluded = {"alo186-release.json", "checksums.sha256"}
    remaining: list[str] = []
    for path in output.rglob("*"):
        if not path.is_file() or path.name in excluded:
            continue
        if path.suffix.lower() not in {".html", ".xml", ".json", ".js", ".css", ".txt"}:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for alias in aliases:
            if alias in text:
                remaining.append(f"{path.relative_to(output)} -> {alias}")

    assert not remaining, "Eski içerik niyeti bağlantıları artifact'ta kaldı:\n" + "\n".join(remaining[:30])


def test_registry_has_no_commercial_claims() -> None:
    payload = json.loads(
        (DEPLOYMENT / "canonical-aliases.json").read_text(encoding="utf-8")
    )
    text = json.dumps(payload, ensure_ascii=False).casefold()
    forbidden = ("fiyat", "stokta", "puan", "garanti süresi", "amazon.com")
    assert not any(token in text for token in forbidden)
