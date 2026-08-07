from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ALO = ROOT / "alo186"


def main() -> None:
    consolidations = json.loads((ALO / "deployment/content-consolidations.json").read_text(encoding="utf-8"))
    item = next(
        row for row in consolidations["consolidations"]
        if row["intentKey"] == "pv-grid-outage-behavior"
    )
    assert item["aliasPath"].rstrip("/") == "/haberler/ges-elektrik-kesintisinde-calisir-mi"
    assert item["canonicalPath"].rstrip("/") == "/haberler/elektrik-kesilince-gunes-paneli-calisir-mi"

    canonical = ALO / "haberler/elektrik-kesilince-gunes-paneli-calisir-mi/index.html"
    tool = ALO / "hesaplama/ges-elektrik-kesintisi-yedek-guc-uygunluk-kontrolu/index.html"
    assert canonical.is_file(), canonical
    assert tool.is_file(), tool

    workshop = (ALO / "kesinti-hazirlik-atolyesi/index.html").read_text(encoding="utf-8")
    app = (ALO / "kesinti-hazirlik-atolyesi/app.js").read_text(encoding="utf-8")
    assert 'value="solar_backup"' in workshop
    assert '/haberler/elektrik-kesilince-gunes-paneli-calisir-mi/' in workshop
    assert "'solar_backup'" in app
    assert "/hesaplama/ges-elektrik-kesintisi-yedek-guc-uygunluk-kontrolu/" in app
    assert "priority === 'solar_backup'" in app

    solar_block_start = app.index("solar_backup: {")
    solar_block_end = app.index("long_outage: {", solar_block_start)
    solar_block = app[solar_block_start:solar_block_end]
    assert "affiliateEligible: false" in solar_block
    assert "product: null" in solar_block
    assert "professional: true" in solar_block
    assert "yeni ürün almayın" in solar_block

    decision = json.loads(
        (ALO / "deployment/affiliate-category-decisions/solar-outage-governance-v343.json").read_text(encoding="utf-8")
    )
    assert decision["newAffiliateClasses"] == 0
    assert decision["newMerchantLinks"] == 0
    assert decision["decision"] == "professional-only-no-new-affiliate-class"
    assert "unverified-price" in decision["mustNotClaim"]
    assert "unverified-stock" in decision["mustNotClaim"]
    assert "unverified-rating" in decision["mustNotClaim"]
    assert "unverified-warranty" in decision["mustNotClaim"]

    assert "amazon.com.tr" not in workshop.lower()
    assert "amazon.com.tr" not in app.lower()

    print({
        "ok": True,
        "intent": "pv-grid-outage-behavior",
        "newAffiliateClasses": 0,
        "newMerchantLinks": 0,
        "workshopPriority": "solar_backup",
    })


if __name__ == "__main__":
    main()
