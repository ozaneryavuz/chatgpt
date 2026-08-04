from __future__ import annotations

import json
import re
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
SITE = ROOT / "alo186"
POLICY_PATH = SITE / "deployment/affiliate_route_risk_policy_v265.json"
AFFILIATE_ROOT = SITE / "amazon-elektrik-urunleri"

AMAZON_HOST_TOKENS = ("amazon.com.tr", "amzn.to")
DISCLOSURE_TOKENS = (
    "satış ortaklığı",
    "satis ortakligi",
    "affiliate",
)
NO_BUY_TOKENS = (
    "yeni ürün almayacağım",
    "yeni urun almayacagim",
    "satın almayacağım",
    "satin almayacagim",
    "mevcut çözümüm yeterli",
    "mevcut cozumum yeterli",
    "satın almama",
    "satin almama",
    "satın alma yok",
    "satin alma yok",
)
HAZARD_TOKENS = (
    "112",
    "yangın",
    "yangin",
    "elektrik çarpması",
    "elektrik carpmasi",
    "duman",
    "kıvılcım",
    "kivilcim",
)


class AnchorParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.anchors: list[dict[str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.casefold() != "a":
            return
        self.anchors.append({key.casefold(): value or "" for key, value in attrs})


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def amazon_target(attrs: dict[str, str]) -> str:
    for key in ("href", "data-affiliate-href", "data-href", "data-url"):
        value = attrs.get(key, "")
        if any(token in value.casefold() for token in AMAZON_HOST_TOKENS):
            return value
    return ""


def jsonld_blocks(html: str, path: Path) -> list[Any]:
    blocks: list[Any] = []
    for raw in re.findall(
        r'<script\b[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
        html,
        flags=re.I | re.S,
    ):
        try:
            blocks.append(json.loads(raw.strip()))
        except json.JSONDecodeError as exc:
            raise AssertionError(f"Geçersiz JSON-LD: {path}: {exc}") from exc
    return blocks


def collect_keys(value: Any) -> set[str]:
    keys: set[str] = set()
    if isinstance(value, dict):
        for key, child in value.items():
            keys.add(str(key).casefold())
            keys.update(collect_keys(child))
    elif isinstance(value, list):
        for child in value:
            keys.update(collect_keys(child))
    return keys


def canonical_url(html: str) -> str:
    match = re.search(
        r'<link\b(?=[^>]*\brel=["\']canonical["\'])(?=[^>]*\bhref=["\']([^"\']+)["\'])[^>]*>',
        html,
        flags=re.I,
    )
    return match.group(1).strip() if match else ""


def route_for(path: Path) -> str:
    relative = path.relative_to(SITE).as_posix()
    assert relative.endswith("/index.html")
    return "/" + relative[: -len("index.html")]


def assert_governed_page(path: Path, policy: dict[str, Any]) -> dict[str, Any]:
    html = path.read_text(encoding="utf-8")
    lowered = html.casefold()
    route = route_for(path)

    parser = AnchorParser()
    parser.feed(html)
    amazon_anchors = [(attrs, amazon_target(attrs)) for attrs in parser.anchors]
    amazon_anchors = [(attrs, target) for attrs, target in amazon_anchors if target]
    assert amazon_anchors, f"Yönetilen affiliate sayfasında Amazon Türkiye hedefi yok: {route}"

    first_link_position = min(lowered.find(target.casefold()) for _, target in amazon_anchors)
    disclosure_positions = [lowered.find(token) for token in DISCLOSURE_TOKENS if token in lowered]
    assert disclosure_positions, f"Görünür satış ortaklığı açıklaması yok: {route}"
    assert min(disclosure_positions) < first_link_position, f"Affiliate açıklaması bağlantıdan önce değil: {route}"
    assert any(token in lowered for token in NO_BUY_TOKENS), f"Satın almama sonucu yok: {route}"
    assert any(token in lowered for token in HAZARD_TOKENS), f"Aktif tehlike/ticaret kapısı görünür değil: {route}"

    required_rel = {item.casefold() for item in policy["affiliateProgram"]["requiredRel"]}
    unsafe_links: list[str] = []
    for attrs, target in amazon_anchors:
        rel = {token.casefold() for token in attrs.get("rel", "").split()}
        if not required_rel.issubset(rel):
            unsafe_links.append(target)
    assert not unsafe_links, f"Affiliate rel sözleşmesi eksik: {route}: {unsafe_links}"

    canonical = canonical_url(html)
    expected = policy["canonicalHost"] + route
    assert canonical == expected, f"Canonical uyuşmuyor: {route}: {canonical!r} != {expected!r}"

    forbidden = {item.casefold() for item in policy["trustRules"]["unverifiedCommercialFieldsForbidden"]}
    schema_keys: set[str] = set()
    for block in jsonld_blocks(html, path):
        schema_keys.update(collect_keys(block))
    violations = sorted(forbidden.intersection(schema_keys))
    assert not violations, f"Doğrulanmamış ticari schema alanı: {route}: {violations}"

    return {
        "route": route,
        "amazonLinks": len(amazon_anchors),
        "schemaKeys": len(schema_keys),
    }


def assert_zero_affiliate_prefix(prefix: str) -> int:
    directory = SITE / prefix.strip("/")
    if not directory.is_dir():
        return 0
    checked = 0
    for path in directory.rglob("index.html"):
        html = path.read_text(encoding="utf-8").casefold()
        assert not any(token in html for token in AMAZON_HOST_TOKENS), (
            f"Resmî yönlendirme/acil rota altında affiliate hedefi bulundu: {route_for(path)}"
        )
        checked += 1
    return checked


def main() -> None:
    policy = load_json(POLICY_PATH)
    assert policy["version"] == 265
    assert policy["canonicalHost"] == "https://alo186.com"
    assert policy["affiliateProgram"]["merchant"] == "Amazon Türkiye"
    assert policy["trustRules"]["activeHazardCommerceClosed"] is True
    assert policy["trustRules"]["officialInstitutionImpressionForbidden"] is True

    all_pages = sorted(AFFILIATE_ROOT.rglob("index.html"))
    assert all_pages, "Affiliate rota kaynağı bulunamadı"

    governed: list[dict[str, Any]] = []
    allowed_patterns = [item.casefold() for item in policy["allowedAffiliateRoutePatterns"]]
    for path in all_pages:
        route = route_for(path).casefold()
        if any(pattern in route for pattern in allowed_patterns):
            governed.append(assert_governed_page(path, policy))
    assert len(governed) >= 4, f"Yeterli güvenlik kapılı rota doğrulanmadı: {len(governed)}"

    source_routes = {route_for(path) for path in all_pages}
    for blocked in policy["blockedCandidateRoutes"]:
        assert blocked not in source_routes, f"Riskli aday affiliate rotası kaynakta yayımlandı: {blocked}"

    professional_patterns = [item.casefold() for item in policy["professionalLeadOnlyRoutePatterns"]]
    professional_conflicts = [
        route for route in source_routes if any(pattern in route.casefold() for pattern in professional_patterns)
    ]
    assert not professional_conflicts, (
        "Profesyonel/sabit tesisat niyeti tüketici affiliate rotasında: "
        + ", ".join(sorted(professional_conflicts))
    )

    zero_affiliate_pages = sum(
        assert_zero_affiliate_prefix(prefix) for prefix in policy["zeroAffiliatePrefixes"]
    )

    smart_plug = AFFILIATE_ROOT / "akilli-priz-enerji-olcer-secimi/index.html"
    assert smart_plug.is_file(), "Akıllı priz canonical seçim rotası yok"
    smart_html = smart_plug.read_text(encoding="utf-8")
    assert 'data-commercial-scope="after_tool"' in smart_html
    assert "/hesaplama/akilli-priz-enerji-olcer-uygunluk/" in smart_html

    summary = {
        "ok": True,
        "policyVersion": policy["version"],
        "governedRoutes": len(governed),
        "governedAmazonLinks": sum(item["amazonLinks"] for item in governed),
        "zeroAffiliatePages": zero_affiliate_pages,
        "blockedCandidateRoutes": len(policy["blockedCandidateRoutes"]),
        "professionalAffiliateConflicts": 0,
        "unverifiedSchemaFields": 0,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
