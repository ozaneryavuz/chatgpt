from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RECOVERY = ROOT / "alo186/hesaplama/elektrik-geldikten-sonra-guvenli-yeniden-baslatma/index.html"
READINESS = ROOT / "alo186/hesaplama/kesinti-hazirlik-kontrolu/index.html"
ROUTES = ROOT / "alo186/deployment/routing-overlays/growth-run6-v257.json"
SERP_CONFIG = ROOT / "alo186/growth/serpapi/intent-watch.json"
SERP_SCRIPT = ROOT / "alo186/growth/serpapi/serpapi_intent_gap.py"


def jsonld_blocks(source: str) -> list[dict]:
    blocks = []
    for raw in re.findall(
        r'<script\b[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
        source,
        flags=re.I | re.S,
    ):
        blocks.append(json.loads(raw))
    return blocks


def schema_types(value):
    found = set()
    if isinstance(value, dict):
        current = value.get("@type")
        if isinstance(current, str):
            found.add(current)
        elif isinstance(current, list):
            found.update(current)
        for child in value.values():
            found.update(schema_types(child))
    elif isinstance(value, list):
        for child in value:
            found.update(schema_types(child))
    return found


def assert_common_page_contract(path: Path, canonical: str) -> str:
    source = path.read_text(encoding="utf-8")
    assert f'<link rel="canonical" href="{canonical}">' in source
    assert "ALO186" in source
    assert "resmî kurum" in source or "kamu kurumu" in source
    assert "112" in source and "186" in source
    assert "Fiyat" in source and "stok" in source
    assert "yeni ürün almayın" in source
    assert "amazon.com.tr" not in source.casefold()
    assert 'type="application/ld+json"' in source
    blocks = jsonld_blocks(source)
    assert blocks
    types = set().union(*(schema_types(block) for block in blocks))
    assert "WebApplication" in types
    assert "FAQPage" in types
    assert "BreadcrumbList" in types
    assert "Offer" not in types
    assert "AggregateRating" not in types
    assert "Review" not in types
    return source


def main() -> None:
    recovery = assert_common_page_contract(
        RECOVERY,
        "https://alo186.com/hesaplama/elektrik-geldikten-sonra-guvenli-yeniden-baslatma/",
    )
    readiness = assert_common_page_contract(
        READINESS,
        "https://alo186.com/hesaplama/kesinti-hazirlik-kontrolu/",
    )

    recovery_types = set().union(*(schema_types(block) for block in jsonld_blocks(recovery)))
    assert "HowTo" in recovery_types
    assert recovery.count("HowToStep") >= 4
    assert '<section id="result" class="result" data-state="wait"' in recovery
    assert '<section id="result" class="result" data-state="danger"' not in recovery
    assert "Ticari ve ürün yolları bu durumda kapalıdır" in recovery
    assert "/hesaplama/modem-internet-yedekleme/" in recovery
    assert "/hesaplama/kombi-kesinti-yedek-guc-uygunluk/" in recovery
    assert "/hesaplama/gerilim-koruma-cozum-secici/" in recovery

    assert "localStorage" in readiness
    assert "text/calendar" in readiness
    assert "30 gün sonra hatırlat" in readiness
    assert "90 gün sonra hatırlat" in readiness
    assert "Hiçbir bilgi sunucuya gönderilmedi" in readiness
    assert "fetch(" not in readiness
    assert "XMLHttpRequest" not in readiness

    route_data = json.loads(ROUTES.read_text(encoding="utf-8"))
    assert route_data["version"] == 257
    route_paths = {item["canonicalPath"] for item in route_data["routes"]}
    assert route_paths == {
        "/hesaplama/elektrik-geldikten-sonra-guvenli-yeniden-baslatma/",
        "/hesaplama/kesinti-hazirlik-kontrolu/",
    }
    assert all(item["type"] == "tool" for item in route_data["routes"])

    config = json.loads(SERP_CONFIG.read_text(encoding="utf-8"))
    assert config["siteDomain"] == "alo186.com"
    assert config["gl"] == "tr" and config["hl"] == "tr"
    assert config["device"] == "mobile"
    assert len(config["queries"]) == 8
    assert len({item["query"] for item in config["queries"]}) == 8
    assert all(item["commercialMode"] in {"closed", "technical-gate"} for item in config["queries"])
    assert any(item["targetRoute"].endswith("elektrik-geldikten-sonra-guvenli-yeniden-baslatma/") for item in config["queries"])

    script = SERP_SCRIPT.read_text(encoding="utf-8")
    assert "SERPAPI_API_KEY" in script
    assert '"api_key": api_key' in script
    assert "Fiyat, stok, puan veya garanti üretme" in script
    assert "1 <= len(specs) <= 8" in script
    assert "https://serpapi.com/search.json" in script

    print(json.dumps({
        "ok": True,
        "routes": sorted(route_paths),
        "serpQueries": len(config["queries"]),
        "affiliateDirectLinks": 0,
        "localOnlyReadiness": True,
        "howTo": True,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
