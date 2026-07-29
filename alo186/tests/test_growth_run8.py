from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

FOLLOWUP = ROOT / "alo186/hesaplama/kesinti-sonrasi-takip-dosyasi/index.html"
RECEIPTS = ROOT / "alo186/karar-makbuzlari/index.html"
INJECTOR = ROOT / "alo186/deployment/inject_growth_run8.py"
SHORTLIST = ROOT / "alo186/deployment/inject_shortlist_growth.py"
OVERLAY = ROOT / "alo186/deployment/routing-overlays/growth-outage-receipts-contextual-run8.json"


def require(text: str, tokens: list[str], label: str) -> None:
    missing = [token for token in tokens if token not in text]
    assert not missing, f"{label} eksik sözleşmeler: {missing}"


def main() -> None:
    followup = FOLLOWUP.read_text(encoding="utf-8")
    receipts = RECEIPTS.read_text(encoding="utf-8")
    injector = INJECTOR.read_text(encoding="utf-8")
    shortlist = SHORTLIST.read_text(encoding="utf-8")
    overlay = json.loads(OVERLAY.read_text(encoding="utf-8"))

    require(
        followup,
        [
            "https://www.alo186.com/hesaplama/kesinti-sonrasi-takip-dosyasi/",
            '"@type":"WebApplication"',
            '"@type":"FAQPage"',
            '"@type":"BreadcrumbList"',
            "10 iş günü içinde",
            "Bu araç arıza kaydı, EDAŞ başvurusu",
            "Ticari yol kapalı",
            "affiliateEligible:false",
            "noBuyOutcome:true",
            "60*86400000",
            "/haberler/elektrik-kesintisi-cihaz-hasari-edas-basvurusu/",
        ],
        "kesinti takip dosyası",
    )
    assert "amazon.com" not in followup.lower() and "amzn." not in followup.lower()
    assert 'type="text"' not in followup and "textarea" not in followup.lower()

    require(
        receipts,
        [
            "https://www.alo186.com/karar-makbuzlari/",
            '"@type":"WebApplication"',
            '"@type":"FAQPage"',
            '"@type":"BreadcrumbList"',
            'type="file"',
            "candidate.personalData!==false",
            "Tanınmayan alanlar atılır",
            "TTL=180*86400000",
            "affiliateEligible",
            "noBuyOutcome",
            "Hizmet satın almak zorunlu değildir",
        ],
        "karar makbuzları",
    )
    assert "amazon.com" not in receipts.lower() and "amzn." not in receipts.lower()
    assert "fetch(" not in receipts and "XMLHttpRequest" not in receipts

    require(
        injector,
        [
            'CONTEXT_MARKER = \'data-alo186-growth-run8-context="true"\'',
            'return "product"',
            'return "outage"',
            'return "technical"',
            '"directAffiliateLinksAdded": 0',
            '"unverifiedCommercialFieldsUsed": []',
            '"noBuyOutcomePreserved": True',
            '"officialAffiliationClaimed": False',
        ],
        "growth run8 injector",
    )
    require(shortlist, ["inject_growth_run8", "run_growth_run8", '"growthRun8"'], "shortlist pipeline")

    assert overlay["version"] == 49
    routes = {item["canonicalPath"]: item for item in overlay["routes"]}
    assert routes["/hesaplama/kesinti-sonrasi-takip-dosyasi/"]["type"] == "calculator"
    assert routes["/karar-makbuzlari/"]["type"] == "retention-tool"
    assert len(routes) == 2
    print(json.dumps({"ok": True, "routes": sorted(routes)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
