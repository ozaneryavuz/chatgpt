from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import guard_commerce_routes_v2 as legacy

DIRECT_CATEGORY_CONTRACT = {
    "powerbank": {"risk": "consumer", "affiliatePolicy": "verified_direct"},
    "usb_c_charger": {"risk": "consumer", "affiliatePolicy": "verified_direct"},
    "usb_c_cable": {"risk": "consumer", "affiliatePolicy": "verified_direct"},
    "usb_c_hub": {"risk": "consumer", "affiliatePolicy": "verified_direct"},
    "display_cable": {"risk": "consumer", "affiliatePolicy": "verified_direct"},
}
LEGACY_DIRECT_ERROR_PREFIX = "catalog.js: yalnız powerbank doğrudan kategori olmalı;"
DIRECT_ID_PATTERN = re.compile(r"\{id:'([^']+)'[^{}]*?mode:'direct'")
DIRECT_CONTRACT_PATTERN = re.compile(
    r"\{id:'(?P<id>[^']+)',name:'[^']+',mode:'direct',risk:'(?P<risk>[^']+)',"
    r"affiliatePolicy:'(?P<policy>[^']+)'"
)
_ORIGINAL_VALIDATE_RUNTIME = legacy.validate_runtime


def catalog_file(site: Path) -> Path:
    path = site / "akilli-urun-secimi" / "catalog.js"
    if not path.is_file():
        path = site / "urun-eslestirme" / "catalog.js"
    return path


def validate_direct_categories(catalog: str) -> tuple[list[str], list[dict[str, str]]]:
    errors: list[str] = []
    direct_ids = DIRECT_ID_PATTERN.findall(catalog)
    records = [match.groupdict() for match in DIRECT_CONTRACT_PATTERN.finditer(catalog)]
    record_ids = [record["id"] for record in records]

    duplicates = sorted({category_id for category_id in direct_ids if direct_ids.count(category_id) > 1})
    if duplicates:
        errors.append(f"catalog.js: yinelenen doğrudan kategori kimliği var: {duplicates}")

    if len(records) != len(direct_ids):
        errors.append(
            "catalog.js: her doğrudan kategori risk ve affiliatePolicy alanlarını açıkça taşımalı; "
            f"kimlikler={direct_ids}, sözleşmeli={record_ids}"
        )

    expected_ids = set(DIRECT_CATEGORY_CONTRACT)
    actual_ids = set(direct_ids)
    missing = sorted(expected_ids - actual_ids)
    unexpected = sorted(actual_ids - expected_ids)
    if missing or unexpected:
        errors.append(
            "catalog.js: düşük riskli doğrudan kategori izin listesi değişti; "
            f"eksik={missing}, beklenmeyen={unexpected}, bulunan={direct_ids}"
        )

    for record in records:
        expected = DIRECT_CATEGORY_CONTRACT.get(record["id"])
        if expected is None:
            continue
        if record["risk"] != expected["risk"] or record["policy"] != expected["affiliatePolicy"]:
            errors.append(
                "catalog.js: doğrudan kategori yalnız consumer + verified_direct olabilir; "
                f"id={record['id']}, risk={record['risk']}, affiliatePolicy={record['policy']}"
            )

    return errors, records


def validate_runtime(site: Path) -> tuple[list[str], dict]:
    legacy_errors, metrics = _ORIGINAL_VALIDATE_RUNTIME(site)
    errors = [error for error in legacy_errors if not error.startswith(LEGACY_DIRECT_ERROR_PREFIX)]

    path = catalog_file(site)
    if not path.is_file():
        return errors, metrics

    catalog = path.read_text(encoding="utf-8", errors="ignore")
    contract_errors, records = validate_direct_categories(catalog)
    errors.extend(contract_errors)
    metrics.update(
        {
            "directCategoryCount": len(records),
            "directCategoryIds": [record["id"] for record in records],
            "directCategoryContract": DIRECT_CATEGORY_CONTRACT,
        }
    )
    return errors, metrics


def validate_site(site: Path) -> dict:
    original = legacy.validate_runtime
    legacy.validate_runtime = validate_runtime
    try:
        result = legacy.validate_site(site)
    finally:
        legacy.validate_runtime = original

    policy = result.setdefault("commercialPolicy", {})
    policy.pop("directCategory", None)
    policy.update(
        {
            "directCategories": list(DIRECT_CATEGORY_CONTRACT),
            "directCategoryRisk": "consumer",
            "directCategoryPolicy": "verified_direct",
        }
    )
    return result


def main() -> None:
    parser = argparse.ArgumentParser(
        description="ALO186 ticari rotalarını ve düşük riskli doğrudan affiliate kategori izin listesini fail-closed doğrular."
    )
    parser.add_argument("--site", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(validate_site(args.site), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
