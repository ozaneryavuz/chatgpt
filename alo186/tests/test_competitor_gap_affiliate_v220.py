from __future__ import annotations

import json
import re
import shutil
import sys
import tempfile
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

REPO_ROOT = Path(__file__).resolve().parents[2]
DEPLOYMENT_DIR = REPO_ROOT / "alo186/deployment"
if str(DEPLOYMENT_DIR) not in sys.path:
    sys.path.insert(0, str(DEPLOYMENT_DIR))

import install_competitor_gap_v220 as module  # noqa: E402


class AnchorParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.anchors: dict[str, dict[str, str]] = {}

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.casefold() != "a":
            return
        values = {name.casefold(): value or "" for name, value in attrs}
        anchor_id = values.get("id")
        if anchor_id:
            if anchor_id in self.anchors:
                raise AssertionError(f"Yinelenen anchor id: {anchor_id}")
            self.anchors[anchor_id] = values


def script_payload(source: str, script_id: str) -> dict[str, object]:
    pattern = re.compile(
        rf'<script\b(?=[^>]*\bid=["\']{re.escape(script_id)}["\'])(?=[^>]*\btype=["\']application/ld\+json["\'])[^>]*>(?P<body>.*?)</script>',
        re.IGNORECASE | re.DOTALL,
    )
    matches = list(pattern.finditer(source))
    if len(matches) != 1:
        raise AssertionError(f"JSON-LD script sayısı yanlış ({script_id}): {len(matches)}")
    return json.loads(matches[0].group("body"))


def has_type(node: dict[str, object], expected: str) -> bool:
    value = node.get("@type")
    if isinstance(value, str):
        return value == expected
    if isinstance(value, list):
        return expected in value
    return False


def validate_edas(source: str) -> dict[str, object]:
    payload = script_payload(source, module.EDAS_SCHEMA_ID)
    graph = payload.get("@graph")
    assert isinstance(graph, list), "EDAŞ @graph eksik"
    organizations = [node for node in graph if isinstance(node, dict) and has_type(node, "Organization")]
    services = [node for node in graph if isinstance(node, dict) and has_type(node, "GovernmentService")]
    assert len(organizations) == 21, len(organizations)
    assert len(services) == 81, len(services)
    org_ids = {node.get("@id") for node in organizations}
    assert len(org_ids) == 21 and None not in org_ids
    provinces: set[str] = set()
    for service in services:
        area = service.get("areaServed")
        assert isinstance(area, dict) and area.get("@type") == "AdministrativeArea"
        province = area.get("name")
        assert isinstance(province, str) and province
        provinces.add(province)
        provider = service.get("provider")
        refs = provider if isinstance(provider, list) else [provider]
        assert refs and all(isinstance(ref, dict) and ref.get("@id") in org_ids for ref in refs)
        channel = service.get("availableChannel")
        assert isinstance(channel, dict)
        phone = channel.get("servicePhone")
        assert isinstance(phone, dict) and phone.get("telephone") == "186"
        assert service.get("url")
        assert "ALO186 bağımsız" in str(service.get("description"))
    assert provinces == set(module.PROVINCE_ORDER)
    assert source.count(f'id="{module.EDAS_SSR_ID}"') == 1
    assert source.count('data-alo186-ssr="true"') >= 1
    assert all(f">{province}</a>" in source for province in module.PROVINCE_ORDER)
    assert "tel:186" in source
    assert "JavaScript gerektirir" not in source
    return {"organizations": len(organizations), "governmentServices": len(services), "provinces": len(provinces)}


def validate_matcher(source: str) -> dict[str, object]:
    payload = script_payload(source, module.MATCHER_SCHEMA_ID)
    graph = payload.get("@graph")
    assert isinstance(graph, list), "Matcher @graph eksik"
    type_counts = {
        type_name: sum(1 for node in graph if isinstance(node, dict) and has_type(node, type_name))
        for type_name in ("Question", "DefinedTerm", "HowTo", "Product", "ItemList")
    }
    assert type_counts == {"Question": 1, "DefinedTerm": 1, "HowTo": 1, "Product": 1, "ItemList": 1}, type_counts
    question = next(node for node in graph if isinstance(node, dict) and has_type(node, "Question"))
    assert question.get("name") == "Kesintide kombi nasıl korunur?"
    howto = next(node for node in graph if isinstance(node, dict) and has_type(node, "HowTo"))
    steps = howto.get("step")
    assert isinstance(steps, list) and len(steps) == 5
    assert all(isinstance(step, dict) and step.get("@type") == "HowToStep" for step in steps)
    product = next(node for node in graph if isinstance(node, dict) and has_type(node, "Product"))
    assert product.get("category") == "Kombi UPS"
    forbidden_commerce_fields = {"offers", "aggregateRating", "review", "price", "priceCurrency", "availability"}
    assert forbidden_commerce_fields.isdisjoint(product), product
    item_list = next(node for node in graph if isinstance(node, dict) and has_type(node, "ItemList"))
    elements = item_list.get("itemListElement")
    assert isinstance(elements, list) and len(elements) == 4
    assert [element.get("name") for element in elements if isinstance(element, dict)] == ["Soru", "Sorun", "Çözüm", "Ürün sınıfı"]

    assert source.count(f'id="{module.SMART_PATH_ID}"') == 1
    assert source.count(f'id="{module.PREPAREDNESS_ID}"') == 1
    assert "Akıllı Yol: Soru → Sorun → Çözüm → Ürün" in source
    assert "Kişisel Hazırlık Kontrolü" in source
    assert "JavaScript gerektirir" not in source

    parser = AnchorParser()
    parser.feed(source)
    required_ids = {
        "urun-ups-3000va",
        "urun-kesintisiz-guc-kaynagi",
        "urun-asiri-gerilim-korumasi",
    }
    assert required_ids.issubset(parser.anchors), sorted(required_ids - set(parser.anchors))
    required_rel = {"sponsored", "nofollow", "noopener", "noreferrer"}
    for anchor_id in required_ids:
        attrs = parser.anchors[anchor_id]
        href = attrs.get("href", "")
        parsed = urlsplit(href)
        assert parsed.scheme == "https" and parsed.hostname == "www.amazon.com.tr", (anchor_id, href)
        assert parse_qs(parsed.query).get("tag") == [module.AFFILIATE_TAG]
        rel = {token.casefold() for token in attrs.get("rel", "").split()}
        assert required_rel.issubset(rel), (anchor_id, rel)
        assert attrs.get("target") == "_blank"
    assert "Nitelikli satın alımlardan komisyon" in source
    assert "Mevcut ürün yeterliyse satın almamak geçerli sonuçtur" in source
    return {**type_counts, "affiliateAnchors": len(required_ids), "howToSteps": len(steps)}


def validate_robots(path: Path) -> list[str]:
    verified = module.verify_ai_crawlers(path)
    assert tuple(verified) == module.REQUESTED_AI_BOTS
    return verified


def fixture_site(root: Path) -> Path:
    site = root / "site"
    (site / "edas-bul").mkdir(parents=True)
    (site / "akilli-urun-secimi").mkdir(parents=True)
    shutil.copy2(REPO_ROOT / "alo186/turkiye-arama/index.html", site / "edas-bul/index.html")
    shutil.copy2(REPO_ROOT / "alo186/urun-eslestirme/index.html", site / "akilli-urun-secimi/index.html")
    shutil.copy2(REPO_ROOT / "alo186/robots.txt", site / "robots.txt")
    return site


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="alo186-v220-") as temp_dir:
        root = Path(temp_dir)
        site = fixture_site(root)
        first = module.install(REPO_ROOT, site)
        second = module.install(REPO_ROOT, site)
        assert first["edasState"] == "injected"
        assert first["matcherState"] == "injected"
        assert second["edasState"] == "already-present"
        assert second["matcherState"] == "already-present"
        edas_source = (site / "edas-bul/index.html").read_text(encoding="utf-8")
        matcher_source = (site / "akilli-urun-secimi/index.html").read_text(encoding="utf-8")
        report = {
            "ok": True,
            "version": module.VERSION,
            "edas": validate_edas(edas_source),
            "matcher": validate_matcher(matcher_source),
            "robots": validate_robots(site / "robots.txt"),
            "idempotent": True,
            "javascriptRequiredForCoreAnswer": False,
            "googleSpecificEligibilityClaimed": False,
        }
        print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
