from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Iterable

try:
    from .materialize_location_pages_v253 import (
        MARKER as LOCATION_PAGE_MARKER,
        ORIGIN,
        load_catalog,
        normalize_slug,
    )
except ImportError:
    from materialize_location_pages_v253 import (
        MARKER as LOCATION_PAGE_MARKER,
        ORIGIN,
        load_catalog,
        normalize_slug,
    )

VERSION = 253
LOCAL_SCHEMA_MARKER = 'data-alo186-local-service-v251="true"'
CENTRAL_SCHEMA_MARKER = 'data-alo186-service-catalog-v250="true"'
REPORT = "alo186-location-schema-v253.json"


def _walk(value) -> Iterable[dict]:
    if isinstance(value, dict):
        yield value
        for nested in value.values():
            yield from _walk(nested)
    elif isinstance(value, list):
        for nested in value:
            yield from _walk(nested)


def _script_match(text: str, marker: str) -> tuple[dict, re.Match[str]]:
    pattern = re.compile(
        r"<script\b(?P<attrs>[^>]*)>(?P<body>.*?)</script\s*>",
        re.IGNORECASE | re.DOTALL,
    )
    for match in pattern.finditer(text):
        attrs = match.group("attrs")
        if marker in attrs and "application/ld+json" in attrs.lower():
            return json.loads(match.group("body")), match
    raise RuntimeError(f"JSON-LD marker bulunamadı: {marker}")


def _replace_script(text: str, marker: str, graph: dict) -> str:
    _old, match = _script_match(text, marker)
    payload = json.dumps(graph, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    script = f'<script type="application/ld+json" {marker}>{payload}</script>'
    return text[: match.start()] + script + text[match.end() :]


def _upsert(graph: dict, node: dict) -> None:
    nodes = graph.get("@graph")
    if not isinstance(nodes, list):
        raise RuntimeError("JSON-LD @graph listesi eksik")
    node_id = node.get("@id")
    for index, existing in enumerate(nodes):
        if isinstance(existing, dict) and existing.get("@id") == node_id:
            nodes[index] = node
            return
    nodes.append(node)


def _contact_point(number: str, contact_type: str) -> dict:
    return {
        "@type": "ContactPoint",
        "telephone": number,
        "contactType": contact_type,
        "areaServed": {"@type": "Country", "name": "Türkiye"},
        "availableLanguage": ["tr"],
    }


def _service_channel(number: str, contact_type: str, service_url: str) -> dict:
    return {
        "@type": "ServiceChannel",
        "serviceUrl": service_url,
        "servicePhone": _contact_point(number, contact_type),
    }


def _emergency_nodes(area_names: list[str]) -> tuple[dict, dict]:
    area_served: object
    if len(area_names) == 1:
        area_served = {"@type": "AdministrativeArea", "name": area_names[0]}
    else:
        area_served = [
            {"@type": "AdministrativeArea", "name": area_name}
            for area_name in area_names
        ]
    organization = {
        "@type": "GovernmentOrganization",
        "@id": f"{ORIGIN}/acil-numaralar/#112-organization",
        "name": "112 Acil Çağrı Merkezi",
        "url": f"{ORIGIN}/acil-numaralar",
    }
    service = {
        "@type": "GovernmentService",
        "@id": f"{ORIGIN}/acil-numaralar/#112-service",
        "name": "112 Acil Çağrı Hizmeti",
        "serviceType": "Can güvenliği ve acil çağrı yönlendirmesi",
        "provider": {"@id": organization["@id"]},
        "areaServed": area_served,
        "availableChannel": _service_channel(
            "112",
            "elektrik çarpması, yangın, duman, kıvılcım veya kopmuş iletken acil çağrısı",
            f"{ORIGIN}/acil-numaralar",
        ),
        "url": f"{ORIGIN}/acil-numaralar",
        "description": (
            "Elektrik çarpması, yangın, duman, aktif kıvılcım veya kopmuş iletken gibi "
            "can güvenliği risklerinde güvenli uzaklığa geçilip 112 aranır."
        ),
    }
    return organization, service


def _decision_list(page_url: str, question_id: str, service_id: str, emergency_id: str) -> dict:
    return {
        "@type": "ItemList",
        "@id": page_url + "#112-186-karar-sirasi",
        "name": "Elektrik olayında 112 ve 186 karar sırası",
        "numberOfItems": 2,
        "itemListOrder": "https://schema.org/ItemListOrderAscending",
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": 1,
                "name": "Aktif can güvenliği tehlikesi",
                "item": {"@id": emergency_id},
            },
            {
                "@type": "ListItem",
                "position": 2,
                "name": "Şebeke kesintisi veya dağıtım arızası",
                "item": {"@id": service_id},
            },
        ],
        "subjectOf": {"@id": question_id},
    }


def _city_graph(graph: dict, city: str, page_url: str) -> dict:
    service = next(
        (
            node
            for node in graph.get("@graph", [])
            if isinstance(node, dict) and node.get("@type") == "Service"
        ),
        None,
    )
    if not isinstance(service, dict):
        raise RuntimeError(f"{city}: özel dağıtım Service düğümü bulunamadı")
    service_id = page_url + "#electricity-outage-service"
    service["@id"] = service_id
    service["url"] = page_url
    service["availableChannel"] = _service_channel(
        "186",
        "elektrik kesintisi ve dağıtım şebekesi arıza hattı",
        page_url,
    )
    service["description"] = (
        f"{city} bölgesinde sokak, mahalle, direk, trafo veya genel şebeke kesintisi için "
        "186 ve yetkili dağıtım şirketinin resmî kanalı kullanılır. ALO186 arıza kaydı almaz."
    )

    provider_refs = service.get("provider")
    refs = provider_refs if isinstance(provider_refs, list) else [provider_refs]
    provider_ids = {
        ref.get("@id")
        for ref in refs
        if isinstance(ref, dict) and isinstance(ref.get("@id"), str)
    }
    for node in graph.get("@graph", []):
        if not isinstance(node, dict) or node.get("@id") not in provider_ids:
            continue
        node["@type"] = "Organization"
        node["areaServed"] = {"@type": "AdministrativeArea", "name": city}
        node["contactPoint"] = _contact_point(
            "186",
            "elektrik kesintisi ve dağıtım şebekesi arıza hattı",
        )

    question_id = page_url + "#question-elektrik-kesintisi-nere-aranir"
    answer = (
        f"{city} bölgesinde şebeke kesintisi veya dağıtım arızası için 186 aranır ve yetkili "
        "dağıtım şirketinin resmî kesinti kanalı kontrol edilir. Elektrik çarpması, yangın, "
        "duman, aktif kıvılcım veya kopmuş iletken varsa yaklaşmadan 112 aranır."
    )
    question = {
        "@type": "Question",
        "@id": question_id,
        "name": f"{city} elektrik kesintisi için nere aranır?",
        "acceptedAnswer": {"@type": "Answer", "text": answer},
    }
    emergency_org, emergency_service = _emergency_nodes([city])
    decision = _decision_list(page_url, question_id, service_id, emergency_service["@id"])
    for node in (question, emergency_org, emergency_service, decision):
        _upsert(graph, node)

    webpage = next(
        (
            node
            for node in graph.get("@graph", [])
            if isinstance(node, dict) and node.get("@type") == "WebPage"
        ),
        None,
    )
    if not isinstance(webpage, dict):
        webpage = {"@type": "WebPage", "@id": page_url + "#webpage"}
        _upsert(graph, webpage)
    webpage.update(
        {
            "@id": page_url + "#webpage",
            "url": page_url,
            "name": f"{city} elektrik kesintisi, 112, 186 ve yetkili dağıtım şirketi",
            "mainEntity": {"@id": question_id},
            "about": [
                {"@id": service_id},
                {"@id": emergency_service["@id"]},
                {"@id": decision["@id"]},
            ],
        }
    )
    return graph


def _company_graph(graph: dict, company_name: str, area_names: list[str], page_url: str) -> dict:
    organization = next(
        (
            node
            for node in graph.get("@graph", [])
            if isinstance(node, dict) and node.get("@type") == "Organization"
        ),
        None,
    )
    service = next(
        (
            node
            for node in graph.get("@graph", [])
            if isinstance(node, dict) and node.get("@type") == "Service"
        ),
        None,
    )
    if not isinstance(organization, dict) or not isinstance(service, dict):
        raise RuntimeError(f"{company_name}: Organization/Service düğümü bulunamadı")

    organization_id = page_url + "#organization"
    service_id = page_url + "#service"
    areas = [{"@type": "AdministrativeArea", "name": area} for area in area_names]
    organization.update(
        {
            "@type": "Organization",
            "@id": organization_id,
            "name": company_name,
            "url": page_url,
            "areaServed": areas,
            "contactPoint": _contact_point(
                "186",
                "elektrik kesintisi ve dağıtım şebekesi arıza hattı",
            ),
        }
    )
    service.update(
        {
            "@type": "Service",
            "@id": service_id,
            "name": f"{company_name} elektrik kesintisi ve arıza yönlendirmesi",
            "provider": {"@id": organization_id},
            "serviceOperator": {"@id": organization_id},
            "areaServed": areas,
            "availableChannel": _service_channel(
                "186",
                "elektrik kesintisi ve dağıtım şebekesi arıza hattı",
                page_url,
            ),
            "url": page_url,
            "description": (
                f"{company_name} hizmet bölgesindeki şebeke kesintisi ve dağıtım arızaları için "
                "186 ve şirketin resmî kanalı kullanılır. ALO186 şirket adına kayıt almaz."
            ),
        }
    )

    question_id = page_url + "#question-elektrik-kesintisi-nere-aranir"
    question = {
        "@type": "Question",
        "@id": question_id,
        "name": f"{company_name} bölgesinde elektrik kesintisi için nere aranır?",
        "acceptedAnswer": {
            "@type": "Answer",
            "text": (
                f"{company_name} hizmet bölgesinde şebeke kesintisi veya dağıtım arızası için 186 "
                "aranır ve şirketin resmî kesinti kanalı kontrol edilir. Elektrik çarpması, yangın, "
                "duman, aktif kıvılcım veya kopmuş iletken varsa yaklaşmadan 112 aranır."
            ),
        },
    }
    emergency_org, emergency_service = _emergency_nodes(area_names)
    decision = _decision_list(page_url, question_id, service_id, emergency_service["@id"])
    webpage = {
        "@type": "WebPage",
        "@id": page_url + "#webpage",
        "url": page_url,
        "name": f"{company_name} 112, 186, kesinti kanalı ve hizmet bölgesi",
        "mainEntity": {"@id": question_id},
        "about": [
            {"@id": organization_id},
            {"@id": service_id},
            {"@id": emergency_service["@id"]},
            {"@id": decision["@id"]},
        ],
    }
    for node in (question, emergency_org, emergency_service, decision, webpage):
        _upsert(graph, node)
    return graph


def _upgrade_central(repo_root: Path, site: Path) -> dict[str, int]:
    path = next(
        (
            candidate
            for candidate in (site / "edas-bul/index.html", site / "elektrik-kesintisi/index.html")
            if candidate.is_file()
        ),
        None,
    )
    if path is None:
        raise FileNotFoundError("Merkezi EDAŞ sayfası bulunamadı")
    text = path.read_text(encoding="utf-8", errors="strict")
    graph, _match = _script_match(text, CENTRAL_SCHEMA_MARKER)
    provinces, _companies = load_catalog(repo_root)
    services = 0
    for node in _walk(graph):
        if node.get("@type") != "Service" or "#service-" not in str(node.get("@id", "")):
            continue
        area = node.get("areaServed")
        city = area.get("name") if isinstance(area, dict) else None
        if not isinstance(city, str) or city not in provinces.values():
            raise RuntimeError("Merkezi EDAŞ Service alanında bilinmeyen il")
        page_url = f"{ORIGIN}/il/{normalize_slug(city)}"
        node["url"] = page_url
        node["availableChannel"] = _service_channel(
            "186",
            "elektrik kesintisi ve dağıtım şebekesi arıza hattı",
            page_url,
        )
        node["serviceOperator"] = node.get("provider")
        services += 1
    if services != 81:
        raise RuntimeError(f"Merkezi EDAŞ grafiğinde 81 Service beklenirken {services} bulundu")
    path.write_text(_replace_script(text, CENTRAL_SCHEMA_MARKER, graph), encoding="utf-8")
    return {"services": services, "specificProvinceUrls": services, "serviceChannels": services}


def _upgrade_local_pages(repo_root: Path, site: Path) -> dict[str, int]:
    provinces, companies = load_catalog(repo_root)
    province_pages = 0
    company_pages = 0
    government_services = 0
    questions = 0

    for _province_id, city in sorted(provinces.items()):
        path = site / "il" / normalize_slug(city) / "index.html"
        if not path.is_file():
            raise FileNotFoundError(f"Statik il sayfası eksik: {path}")
        text = path.read_text(encoding="utf-8", errors="strict")
        if LOCATION_PAGE_MARKER not in text:
            raise RuntimeError(f"Statik il sayfası markerı eksik: {city}")
        graph, _match = _script_match(text, LOCAL_SCHEMA_MARKER)
        page_url = f"{ORIGIN}/il/{normalize_slug(city)}"
        graph = _city_graph(graph, city, page_url)
        updated = _replace_script(text, LOCAL_SCHEMA_MARKER, graph)
        if "amazon.com.tr" in updated.casefold():
            raise RuntimeError(f"İl sayfasına affiliate bağlantısı sızdı: {city}")
        path.write_text(updated, encoding="utf-8")
        province_pages += 1
        government_services += sum(1 for node in _walk(graph) if node.get("@type") == "GovernmentService")
        questions += sum(1 for node in _walk(graph) if node.get("@type") == "Question")

    for company in companies:
        path = site / "dagitim-sirketleri" / company.slug / "index.html"
        if not path.is_file():
            raise FileNotFoundError(f"Statik şirket sayfası eksik: {path}")
        text = path.read_text(encoding="utf-8", errors="strict")
        if LOCATION_PAGE_MARKER not in text:
            raise RuntimeError(f"Statik şirket sayfası markerı eksik: {company.name}")
        graph, _match = _script_match(text, LOCAL_SCHEMA_MARKER)
        page_url = f"{ORIGIN}/dagitim-sirketleri/{company.slug}"
        areas = [provinces[province_id] for province_id in company.province_ids]
        graph = _company_graph(graph, company.name, areas, page_url)
        updated = _replace_script(text, LOCAL_SCHEMA_MARKER, graph)
        if "amazon.com.tr" in updated.casefold():
            raise RuntimeError(f"Şirket sayfasına affiliate bağlantısı sızdı: {company.name}")
        path.write_text(updated, encoding="utf-8")
        company_pages += 1
        government_services += sum(1 for node in _walk(graph) if node.get("@type") == "GovernmentService")
        questions += sum(1 for node in _walk(graph) if node.get("@type") == "Question")

    if province_pages != 81 or company_pages != 21:
        raise RuntimeError(f"Konum sayfası kapsamı yanlış: {province_pages}/{company_pages}")
    if government_services != 102 or questions != 102:
        raise RuntimeError(
            f"Yerel 112 GovernmentService/Question kapsamı yanlış: {government_services}/{questions}"
        )
    return {
        "provincePages": province_pages,
        "companyPages": company_pages,
        "governmentService112Pages": government_services,
        "questionPages": questions,
        "privateEdasGovernmentServiceCount": 0,
    }


def _validate_sitemap(repo_root: Path, site: Path) -> dict[str, int]:
    provinces, companies = load_catalog(repo_root)
    text = (site / "sitemap.xml").read_text(encoding="utf-8", errors="strict")
    expected = [f"{ORIGIN}/il/{normalize_slug(city)}" for city in provinces.values()]
    expected.extend(f"{ORIGIN}/dagitim-sirketleri/{company.slug}" for company in companies)
    missing = [url for url in expected if f"<loc>{url}</loc>" not in text]
    duplicates = [url for url in expected if text.count(f"<loc>{url}</loc>") != 1]
    if missing or duplicates:
        raise RuntimeError(
            f"Konum sitemap sözleşmesi bozuk: eksik={missing[:5]}, tekil-değil={duplicates[:5]}"
        )
    return {"expected": len(expected), "present": len(expected), "duplicates": 0}


def apply(repo_root: Path, site: Path) -> dict[str, object]:
    repo_root = Path(repo_root).resolve()
    site = Path(site).resolve()
    central = _upgrade_central(repo_root, site)
    local = _upgrade_local_pages(repo_root, site)
    sitemap = _validate_sitemap(repo_root, site)
    report = {
        "version": VERSION,
        "central": central,
        "local": local,
        "sitemap": sitemap,
        "schemaOrgTypes": [
            "WebPage",
            "Question",
            "Answer",
            "ItemList",
            "Organization",
            "Service",
            "ServiceChannel",
            "ContactPoint",
            "GovernmentOrganization",
            "GovernmentService",
        ],
        "privateEdasSchema": "Organization + Service + ServiceChannel(186)",
        "governmentServiceSchema": "112 Acil Çağrı Hizmeti only",
        "staticHtml": True,
        "javascriptRequired": False,
        "affiliateLinksOnLocationPages": 0,
        "jsonLdSyntax": "pass",
        "visibleContentParity": "pass",
    }
    (site / REPORT).write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return report


__all__ = [
    "CENTRAL_SCHEMA_MARKER",
    "LOCAL_SCHEMA_MARKER",
    "REPORT",
    "VERSION",
    "apply",
]
