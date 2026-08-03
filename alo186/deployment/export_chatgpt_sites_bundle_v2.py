from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
from typing import Any

try:
    from .export_chatgpt_sites_bundle import (
        DEPLOYMENT,
        REPO_ROOT,
        affiliate_contract,
        build_site_brief,
        export_bundle as export_core_bundle,
        extract_h1,
        extract_meta_description,
        extract_text,
        extract_title,
        markdown_document,
        read_json,
        safe_filename,
        write_json,
    )
    from .materialize_location_pages_v253 import (
        ORIGIN,
        company_page,
        city_page,
        load_catalog,
        normalize_slug,
    )
except ImportError:
    from export_chatgpt_sites_bundle import (
        DEPLOYMENT,
        REPO_ROOT,
        affiliate_contract,
        build_site_brief,
        export_bundle as export_core_bundle,
        extract_h1,
        extract_meta_description,
        extract_text,
        extract_title,
        markdown_document,
        read_json,
        safe_filename,
        write_json,
    )
    from materialize_location_pages_v253 import (
        ORIGIN,
        company_page,
        city_page,
        load_catalog,
        normalize_slug,
    )

VERSION = 2
POLICY_PATH = DEPLOYMENT / "chatgpt-sites-export-policy.json"


def _province_schema(city: str, slug: str, companies: list[Any]) -> dict[str, Any]:
    page = f"{ORIGIN}/il/{slug}"
    provider_nodes = [
        {
            "@type": "Organization",
            "@id": f"{ORIGIN}/dagitim-sirketleri/{company.slug}#organization",
            "name": company.name,
            "url": f"{ORIGIN}/dagitim-sirketleri/{company.slug}",
        }
        for company in companies
    ]
    return {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "WebPage",
                "@id": f"{page}#webpage",
                "url": page,
                "name": f"{city} elektrik kesintisi, 186 ve yetkili dağıtım şirketi",
                "about": {"@type": "AdministrativeArea", "name": city},
            },
            {
                "@type": "Question",
                "@id": f"{page}#question",
                "name": f"{city} elektrik kesintisi için nere aranır?",
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": "Aktif tehlikede 112; şebeke kesintisi veya dağıtım arızasında 186 ve yetkili dağıtım şirketinin resmî kanalı kullanılır. ALO186 bağımsız yönlendirme platformudur.",
                },
            },
            {
                "@type": "Service",
                "@id": f"{page}#service-186",
                "name": f"{city} elektrik dağıtım arıza yönlendirmesi",
                "areaServed": {"@type": "AdministrativeArea", "name": city},
                "provider": [{"@id": node["@id"]} for node in provider_nodes],
                "availableChannel": {
                    "@type": "ServiceChannel",
                    "servicePhone": {
                        "@type": "ContactPoint",
                        "telephone": "186",
                        "contactType": "electricity distribution fault",
                    },
                },
            },
            {
                "@type": "GovernmentService",
                "@id": f"{page}#government-service-112",
                "name": "112 Acil Çağrı Hizmeti",
                "serviceType": "Emergency service",
                "availableChannel": {
                    "@type": "ServiceChannel",
                    "servicePhone": {
                        "@type": "ContactPoint",
                        "telephone": "112",
                        "contactType": "emergency",
                    },
                },
            },
            *provider_nodes,
        ],
    }


def _company_schema(company: Any, provinces: dict[int, str]) -> dict[str, Any]:
    page = f"{ORIGIN}/dagitim-sirketleri/{company.slug}"
    areas = [provinces[province_id] for province_id in company.province_ids]
    return {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "WebPage",
                "@id": f"{page}#webpage",
                "url": page,
                "name": f"{company.name} arıza telefonu, kesinti kanalı ve hizmet bölgesi",
            },
            {
                "@type": "Organization",
                "@id": f"{page}#organization",
                "name": company.name,
                "url": page,
                "areaServed": [{"@type": "AdministrativeArea", "name": city} for city in areas],
            },
            {
                "@type": "Service",
                "@id": f"{page}#service-186",
                "name": f"{company.name} elektrik dağıtım arıza yönlendirmesi",
                "provider": {"@id": f"{page}#organization"},
                "areaServed": [{"@type": "AdministrativeArea", "name": city} for city in areas],
                "availableChannel": {
                    "@type": "ServiceChannel",
                    "servicePhone": {
                        "@type": "ContactPoint",
                        "telephone": "186",
                        "contactType": "electricity distribution fault",
                    },
                },
            },
            {
                "@type": "Question",
                "@id": f"{page}#question",
                "name": f"{company.name} elektrik kesintisi için nere aranır?",
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": "Şebeke kesintisi veya dağıtım arızasında 186 ve şirketin resmî kanalı kullanılır. Aktif can güvenliği riskinde 112 aranır. ALO186 resmî kurum değildir.",
                },
            },
            {
                "@type": "GovernmentService",
                "@id": f"{page}#government-service-112",
                "name": "112 Acil Çağrı Hizmeti",
                "serviceType": "Emergency service",
                "availableChannel": {
                    "@type": "ServiceChannel",
                    "servicePhone": {
                        "@type": "ContactPoint",
                        "telephone": "112",
                        "contactType": "emergency",
                    },
                },
            },
        ],
    }


def _record(*, route: str, html: str, category: str, source_copy: str, schema: dict[str, Any], policy: dict[str, Any]) -> dict[str, Any]:
    title = extract_title(html)
    description = extract_meta_description(html)
    h1 = extract_h1(html)
    if not (title and description and h1):
        raise RuntimeError(f"Konum sayfası metadata eksik: {route}")
    affiliate = affiliate_contract(html, policy)
    if affiliate["hasAffiliateLinks"]:
        raise RuntimeError(f"Konum sayfasında affiliate bağlantısı olmamalı: {route}")
    return {
        "canonicalPath": route,
        "canonicalUrl": ORIGIN + route,
        "sourceCanonical": ORIGIN + route,
        "source": f"generated:v253{route}/index.html",
        "sourceCopy": source_copy,
        "routeType": "structured-location-page",
        "category": category,
        "importMode": "sites-structured-page",
        "priority": 1,
        "title": title,
        "description": description,
        "h1": h1,
        "language": "tr-TR",
        "schemaTypes": sorted({"WebPage", "Question", "Answer", "Organization", "Service", "ServiceChannel", "ContactPoint", "GovernmentService", "AdministrativeArea"}),
        "jsonLd": [schema],
        "interactive": False,
        "affiliate": affiliate,
        "professionalLead": False,
        "importReady": True,
        "reviewReasons": [],
    }


def _write_generated_source(output: Path, route: str, html: str) -> str:
    destination = output / "source" / route.strip("/") / "index.html"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(html, encoding="utf-8")
    return destination.relative_to(output).as_posix()


def _rebuild_checksums(output: Path) -> None:
    checksum = output / "checksums.sha256"
    if checksum.exists():
        checksum.unlink()
    lines: list[str] = []
    for path in sorted(item for item in output.rglob("*") if item.is_file()):
        lines.append(f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.relative_to(output).as_posix()}")
    checksum.write_text("\n".join(lines) + "\n", encoding="utf-8")


def export_bundle(output: Path, source_commit: str) -> dict[str, Any]:
    manifest = export_core_bundle(output, source_commit)
    policy = read_json(POLICY_PATH, {})
    provinces, companies = load_catalog(REPO_ROOT)
    companies_by_province = {
        province_id: [company for company in companies if province_id in company.province_ids]
        for province_id in provinces
    }

    generated: list[dict[str, Any]] = []
    for province_id, city in sorted(provinces.items()):
        slug = normalize_slug(city)
        route = f"/il/{slug}"
        html = city_page(city, companies_by_province[province_id])
        schema = _province_schema(city, slug, companies_by_province[province_id])
        source_copy = _write_generated_source(output, route, html)
        record = _record(route=route, html=html, category="location-province", source_copy=source_copy, schema=schema, policy=policy)
        generated.append(record)
        (output / "content/pages" / (safe_filename(route) + ".md")).write_text(
            markdown_document(record, extract_text(html)), encoding="utf-8"
        )

    for company in companies:
        route = f"/dagitim-sirketleri/{company.slug}"
        html = company_page(company, provinces)
        schema = _company_schema(company, provinces)
        source_copy = _write_generated_source(output, route, html)
        record = _record(route=route, html=html, category="location-company", source_copy=source_copy, schema=schema, policy=policy)
        generated.append(record)
        (output / "content/pages" / (safe_filename(route) + ".md")).write_text(
            markdown_document(record, extract_text(html)), encoding="utf-8"
        )

    existing_paths = {item["canonicalPath"] for item in manifest["pages"]}
    duplicate = existing_paths.intersection(item["canonicalPath"] for item in generated)
    if duplicate:
        raise RuntimeError("Konum rotası mevcut export ile çakıştı: " + ", ".join(sorted(duplicate)))

    manifest["pages"].extend(generated)
    manifest["pages"] = sorted(manifest["pages"], key=lambda item: (item["priority"], item["canonicalPath"]))
    stats = manifest["stats"]
    stats["effectiveRoutes"] += len(generated)
    stats["importReady"] += len(generated)
    stats["provincePages"] = len(provinces)
    stats["companyPages"] = len(companies)
    manifest["exporterVersion"] = VERSION

    navigation_path = output / "data/navigation.json"
    navigation = json.loads(navigation_path.read_text(encoding="utf-8"))
    navigation["location-province"] = [
        {
            "canonicalPath": item["canonicalPath"],
            "title": item["title"],
            "description": item["description"],
            "priority": 1,
            "importMode": "sites-structured-page",
        }
        for item in generated
        if item["category"] == "location-province"
    ]
    navigation["location-company"] = [
        {
            "canonicalPath": item["canonicalPath"],
            "title": item["title"],
            "description": item["description"],
            "priority": 1,
            "importMode": "sites-structured-page",
        }
        for item in generated
        if item["category"] == "location-company"
    ]
    write_json(navigation_path, navigation)

    location_records = [
        {
            "canonicalPath": item["canonicalPath"],
            "title": item["title"],
            "description": item["description"],
            "category": item["category"],
            "jsonLd": item["jsonLd"],
            "sourceCopy": item["sourceCopy"],
        }
        for item in generated
    ]
    write_json(output / "data/location-services.json", location_records)
    write_json(output / "data/export-stats.json", stats)
    write_json(output / "sites-import.json", manifest)
    (output / "SITE_BRIEF.md").write_text(build_site_brief(policy, stats, source_commit), encoding="utf-8")
    _rebuild_checksums(output)
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description="ALO186 ChatGPT Sites aktarım paketi v2")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--commit", default=os.environ.get("GITHUB_SHA", "unknown"))
    args = parser.parse_args()
    manifest = export_bundle(args.output.resolve(), args.commit)
    print(json.dumps({"ok": True, "exporterVersion": VERSION, "stats": manifest["stats"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
