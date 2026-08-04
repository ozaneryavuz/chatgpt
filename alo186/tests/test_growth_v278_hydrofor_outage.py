from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTICLE = ROOT / "haberler/elektrik-kesilince-hidrofor-calisir-mi/index.html"
TOOL = ROOT / "hesaplama/hidrofor-elektrik-kesintisi-su-surekliligi-plani/index.html"
OVERLAY = ROOT / "deployment/routing-overlays/growth-v278-hydrofor-outage.json"
DECISION = ROOT / "deployment/affiliate-category-decisions/hydrofor-outage-v278.json"
POLICY = ROOT / "deployment/affiliate_route_risk_policy_v265.json"


def read(path: Path) -> str:
    assert path.is_file(), f"missing: {path}"
    return path.read_text(encoding="utf-8")


def main() -> None:
    article = read(ARTICLE)
    tool = read(TOOL)
    combined = article + "\n" + tool

    assert 'href="https://alo186.com/haberler/elektrik-kesilince-hidrofor-calisir-mi/"' in article
    assert 'href="https://alo186.com/hesaplama/hidrofor-elektrik-kesintisi-su-surekliligi-plani/"' in tool
    assert "bağımsız" in combined.lower()
    assert "kamu kurumu değildir" in combined.lower()
    assert "yeni ürün almayın" in combined.lower()
    assert "professional-only" in combined
    assert "yanıtlar sunucuya gönderilmez" in tool.lower()
    assert "BEGIN:VCALENDAR" in tool and "30 günlük" in tool and "90 günlük" in tool and "365" in tool

    assert "amazon." not in combined.lower()
    assert '"@type":"Offer"' not in combined
    assert '"@type":"AggregateRating"' not in combined
    assert '"@type":"Review"' not in combined
    assert re.search(r'<input[^>]+type="(?:text|email|tel)"', tool, re.I) is None
    assert "localStorage" not in tool and "sessionStorage" not in tool and "fetch(" not in tool

    overlay = json.loads(read(OVERLAY))
    routes = {item["canonicalPath"] for item in overlay["routes"]}
    assert routes == {
        "/haberler/elektrik-kesilince-hidrofor-calisir-mi/",
        "/hesaplama/hidrofor-elektrik-kesintisi-su-surekliligi-plani/",
    }

    decision = json.loads(read(DECISION))
    assert decision["decision"] == "professional-only-no-direct-affiliate"
    assert decision["conversionPolicy"]["directAffiliateLinksAllowed"] is False
    assert decision["conversionPolicy"]["noBuyOutcomeRequired"] is True
    assert decision["conversionPolicy"]["personalDataCollectionForbidden"] is True
    assert decision["conversionPolicy"]["noPriceStockRatingWarrantyClaims"] is True
    assert len(decision["repeatVisitReasons"]) == 3

    policy = json.loads(read(POLICY))
    professional = set(policy["professionalLeadOnlyRoutePatterns"])
    assert {"hidrofor", "pompa", "kuyu-pompasi", "yangin-pompasi"}.issubset(professional)

    print(json.dumps({
        "ok": True,
        "version": 278,
        "routes": sorted(routes),
        "directAffiliateLinks": 0,
        "personalDataFields": 0,
        "repeatVisitCycles": [30, 90, 365],
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
