from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RECOVERY = ROOT / "alo186/hesaplama/kesinti-sonrasi-guvenli-yeniden-baslatma-plani/index.html"
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


def assert_schema_contract(source: str) -> set[str]:
    blocks = jsonld_blocks(source)
    assert blocks
    types = set().union(*(schema_types(block) for block in blocks))
    assert "WebApplication" in types
    assert "FAQPage" in types
    assert "BreadcrumbList" in types
    assert "Offer" not in types
    assert "AggregateRating" not in types
    assert "Review" not in types
    return types


def main() -> None:
    recovery = RECOVERY.read_text(encoding="utf-8")
    assert "https://www.alo186.com/hesaplama/kesinti-sonrasi-guvenli-yeniden-baslatma-plani/" in recovery
    assert "ALO186 EDAŞ" in recovery
    assert "112" in recovery and "186" in recovery
    assert "fiyat, stok, puan" in recovery.casefold()
    assert "yeni ürün satın almayın" in recovery
    assert "amazon.com.tr" not in recovery.casefold()
    assert "Yeniden başlatmayı durdur" in recovery
    assert "Ticari yol kapalı" in recovery
    assert "/hesaplama/yedek-guc-cozum-secici/" in recovery
    assert "/hesaplama/kesinti-kiti-donemsel-kontrolu/" in recovery
    assert_schema_contract(recovery)

    readiness = READINESS.read_text(encoding="utf-8")
    assert '<link rel="canonical" href="https://alo186.com/hesaplama/kesinti-hazirlik-kontrolu/">' in readiness
    assert "ALO186" in readiness
    assert "resmî kurum" in readiness or "kamu kurumu" in readiness
    assert "112" in readiness and "186" in readiness
    assert "Fiyat" in readiness and "stok" in readiness
    assert "yeni ürün almayın" in readiness
    assert "amazon.com.tr" not in readiness.casefold()
    assert_schema_contract(readiness)
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
    assert route_paths == {"/hesaplama/kesinti-hazirlik-kontrolu/"}
    assert all(item["type"] == "tool" for item in route_data["routes"])

    config = json.loads(SERP_CONFIG.read_text(encoding="utf-8"))
    assert config["version"] == 2
    assert config["siteDomain"] == "alo186.com"
    assert config["gl"] == "tr" and config["hl"] == "tr"
    assert config["device"] == "mobile"
    assert len(config["queries"]) == 8
    assert len({item["query"] for item in config["queries"]}) == 8
    assert all(item["commercialMode"] in {"closed", "technical-gate"} for item in config["queries"])
    route_by_query = {item["query"]: item["targetRoute"] for item in config["queries"]}
    assert route_by_query["elektrik geldikten sonra cihazlar nasıl açılır"] == "/hesaplama/kesinti-sonrasi-guvenli-yeniden-baslatma-plani/"
    assert route_by_query["elektrik kesintisine nasıl hazırlanılır"] == "/hesaplama/kesinti-hazirlik-kontrolu/"
    assert "/hesaplama/elektrik-geldikten-sonra-guvenli-yeniden-baslatma/" not in set(route_by_query.values())

    script = SERP_SCRIPT.read_text(encoding="utf-8")
    assert "SERPAPI_API_KEY" in script
    assert '"api_key": api_key' in script
    assert "Fiyat, stok, puan veya garanti üretme" in script
    assert "1 <= len(specs) <= 8" in script
    assert "https://serpapi.com/search.json" in script

    print(json.dumps({
        "ok": True,
        "newCanonicalRoutes": sorted(route_paths),
        "existingRecoveryRouteReused": True,
        "serpQueries": len(config["queries"]),
        "affiliateDirectLinks": 0,
        "localOnlyReadiness": True,
        "intentCannibalizationPrevented": True,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
