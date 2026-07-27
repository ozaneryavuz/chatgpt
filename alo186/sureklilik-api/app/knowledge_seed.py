from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from datetime import datetime, timezone
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from sqlalchemy import select

from .db import SessionLocal
from .kg_models import KnowledgeSource, KnowledgeVerificationRun
from .kg_service import GLOBAL_SCOPE, graph_health, upsert_assertion, upsert_entity, upsert_source
from .models import utcnow

PROVINCES_URL = "https://api.turkiyeapi.dev/v2/datasets/2025/provinces.json"
DISTRICTS_URL = "https://api.turkiyeapi.dev/v2/datasets/2025/districts.json"

COMPANIES = [
    {"id": "toroslar", "name": "Toroslar EDAŞ", "slug": "toroslar-edas", "province_ids": [1, 27, 31, 79, 33, 80]},
    {"id": "akedas", "name": "AKEDAŞ", "slug": "akedas", "province_ids": [2, 46]},
    {"id": "oedas", "name": "Osmangazi EDAŞ", "slug": "oedas", "province_ids": [3, 11, 26, 43, 64]},
    {"id": "aras", "name": "ARAS EDAŞ", "slug": "aras-edas", "province_ids": [4, 24, 25, 36, 69, 75, 76]},
    {"id": "medas", "name": "MEDAŞ", "slug": "medas", "province_ids": [68, 70, 40, 42, 50, 51]},
    {"id": "yedas", "name": "YEDAŞ", "slug": "yedas", "province_ids": [5, 19, 52, 55, 57]},
    {"id": "baskent", "name": "Başkent EDAŞ", "slug": "baskent-edas", "province_ids": [6, 18, 37, 71, 74, 78, 67]},
    {"id": "aedas", "name": "Akdeniz EDAŞ", "slug": "akdeniz-edas", "province_ids": [7, 15, 32]},
    {"id": "coruh", "name": "Çoruh EDAŞ", "slug": "coruh-edas", "province_ids": [8, 28, 29, 53, 61]},
    {"id": "adm", "name": "ADM Elektrik", "slug": "adm-elektrik", "province_ids": [9, 20, 48]},
    {"id": "uedas", "name": "UEDAŞ", "slug": "uedas", "province_ids": [10, 16, 17, 77]},
    {"id": "dicle", "name": "Dicle Elektrik", "slug": "dicle-elektrik", "province_ids": [72, 21, 47, 56, 63, 73]},
    {"id": "fedas", "name": "Fırat EDAŞ", "slug": "firat-edas", "province_ids": [12, 23, 44, 62]},
    {"id": "vedas", "name": "VEDAŞ", "slug": "vedas", "province_ids": [13, 30, 49, 65]},
    {"id": "sedas", "name": "SEDAŞ", "slug": "sedas", "province_ids": [14, 41, 54, 81]},
    {"id": "tredas", "name": "TREDAŞ", "slug": "tredas", "province_ids": [22, 39, 59]},
    {"id": "gdz", "name": "GDZ Elektrik", "slug": "gdz-elektrik", "province_ids": [35, 45]},
    {"id": "kcetas", "name": "KCETAŞ", "slug": "kcetas", "province_ids": [38]},
    {"id": "cedas", "name": "Çamlıbel EDAŞ", "slug": "cedas", "province_ids": [58, 60, 66]},
    {"id": "bedas", "name": "BEDAŞ", "slug": "bedas", "province_ids": [34], "district_mode": "europe"},
    {"id": "ayedas", "name": "AYEDAŞ", "slug": "ayedas", "province_ids": [34], "district_mode": "asia"},
]

ISTANBUL_EUROPE = {
    "Arnavutköy", "Avcılar", "Bağcılar", "Bahçelievler", "Bakırköy", "Başakşehir", "Bayrampaşa",
    "Beşiktaş", "Beylikdüzü", "Beyoğlu", "Büyükçekmece", "Çatalca", "Esenler", "Esenyurt",
    "Eyüpsultan", "Fatih", "Gaziosmanpaşa", "Güngören", "Kağıthane", "Küçükçekmece", "Sarıyer",
    "Silivri", "Sultangazi", "Şişli", "Zeytinburnu",
}
ISTANBUL_ASIA = {
    "Adalar", "Ataşehir", "Beykoz", "Çekmeköy", "Kadıköy", "Kartal", "Maltepe", "Pendik",
    "Sancaktepe", "Sultanbeyli", "Şile", "Tuzla", "Ümraniye", "Üsküdar",
}

PROBLEMS = [
    ("area_outage", "Bölgede elektrik yok", "outage", "route:186", "normal"),
    ("building_outage", "Yalnız binada veya ortak alanda elektrik yok", "outage", "route:building-management", "yellow"),
    ("unit_outage", "Yalnız dairede veya iş yerinde elektrik yok", "outage", "route:electrician", "yellow"),
    ("partial_outage", "Bazı odalar veya prizler çalışmıyor", "outage", "route:electrician", "yellow"),
    ("flicker", "Elektrik gelip gidiyor", "outage", "route:scope-check", "yellow"),
    ("bright_dim", "Lambalar aşırı parlak veya sönük", "outage", "route:scope-check", "yellow"),
    ("phase_loss", "Tek faz eksik veya üç fazlı cihaz çalışmıyor", "outage", "route:scope-check", "yellow"),
    ("neutral_suspect", "Nötr arızası şüphesi", "outage", "route:scope-check", "red"),
    ("rcd_trips", "Kaçak akım rölesi atıyor", "panel", "route:electrician", "yellow"),
    ("main_breaker_trips", "Ana sigorta veya şalter atıyor", "panel", "route:electrician", "yellow"),
    ("breaker_hot", "Sigorta veya şalter ısınıyor", "panel", "route:electrician", "red"),
    ("panel_noise", "Panodan uğultu, çıtırtı veya ark sesi geliyor", "panel", "route:electrician", "red"),
    ("burning_smell", "Yanık kokusu var", "panel", "route:112", "red"),
    ("socket_burn", "Prizde kararma, erime veya ısınma var", "panel", "route:electrician", "red"),
    ("touch_voltage", "Cihaz gövdesinde elektrik hissediliyor", "panel", "route:112", "red"),
    ("streetlight_off", "Sokak lambası yanmıyor", "external", "route:186", "normal"),
    ("pole_spark", "Direkten veya hattan kıvılcım çıkıyor", "external", "route:112", "red"),
    ("fallen_conductor", "Kablo yere düştü", "external", "route:112", "red"),
    ("transformer_noise", "Trafo olağandışı ses yapıyor", "external", "route:186", "yellow"),
    ("damaged_pole", "Direk eğilmiş veya hasarlı", "external", "route:112", "red"),
    ("meter_display_off", "Sayaç ekranı kapalı veya hata gösteriyor", "meter", "route:186", "normal"),
    ("meter_burned", "Sayaç yanmış, ısınmış veya kıvılcım var", "meter", "route:112", "red"),
    ("seal_issue", "Sayaç mührü veya bağlantı kapağı sorunu", "meter", "route:186", "normal"),
    ("illegal_electricity", "Kaçak elektrik şüphesi", "meter", "route:186", "normal"),
    ("subscription", "Abonelik, bağlantı veya tesisat işlemi", "meter", "route:edas-finder", "normal"),
]

TOOLS = [
    ("tool:edas-finder", "Türkiye EDAŞ Bulucu", "/edas-bul"),
    ("tool:decision-engine", "Elektrik Sorunu Karar Motoru", "/karar-motoru"),
    ("tool:calculator-hub", "Elektrik Hesaplama Merkezi", "/hesaplama/"),
    ("tool:product-matcher", "Akıllı Ürün Eşleştirme", "/akilli-urun-secimi"),
    ("tool:continuity-panel", "Elektrik Sürekliliği Paneli", "/isletme-surekliligi"),
    ("tool:invoice-intelligence", "Elektrik Faturası Zekâ Merkezi", "/fatura-analizi"),
]

PRODUCT_CATEGORIES = [
    ("product-category:powerbank", "Powerbank"),
    ("product-category:surge-strip", "Akım korumalı grup priz"),
    ("product-category:mini-ups", "Modem ve ONT mini UPS"),
    ("product-category:emergency-light", "Şarjlı acil aydınlatma"),
    ("product-category:smoke-alarm", "Fotoelektrik duman alarmı"),
    ("product-category:power-station", "Taşınabilir güç istasyonu"),
    ("product-category:outlet-tester", "Priz ve RCD test cihazı"),
]

PRODUCTS = [
    ("product:amazon:B0BYNZXFM2", "Anker Prime A1336 20.000 mAh 200 W", "product-category:powerbank"),
    ("product:amazon:B09TWRHGWV", "Xiaomi 10 W Wireless Power Bank 10.000", "product-category:powerbank"),
    ("product:amazon:B0CVGVG7NW", "Samsung EB-U2510X 10.000 mAh", "product-category:powerbank"),
    ("product:amazon:B07CST4766", "Tunçmatik TSK6136 PowerSurge 5 Priz 1050 J", "product-category:surge-strip"),
    ("product:amazon:B08L9KVRP1", "Viko Multilet Şok Korumalı 6'lı Grup Priz", "product-category:surge-strip"),
    ("product:amazon:B08KW6X13Y", "Tunçmatik PowerSurge 5 Priz + USB TSK5015", "product-category:surge-strip"),
    ("product:amazon:B09YTYTZ4J", "Cata CT-9186 Tekli Akım Korumalı Priz 918 J", "product-category:surge-strip"),
]

ROUTES = [
    ("route:112", "112 Acil Çağrı", "EmergencyNumber", {"telephone": "112", "revenueAllowed": False}),
    ("route:186", "186 Elektrik Arıza Hattı", "EmergencyNumber", {"telephone": "186"}),
    ("route:electrician", "Yetkili Elektrikçi", "SafetyRoute", {}),
    ("route:building-management", "Bina Yönetimi veya Teknik Servis", "SafetyRoute", {}),
    ("route:scope-check", "Şebeke ve İç Tesisat Kapsam Kontrolü", "SafetyRoute", {}),
    ("route:edas-finder", "ALO186 EDAŞ Bulucu", "Tool", {"url": "/edas-bul"}),
]


def _dataset_array(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    if isinstance(payload, dict) and isinstance(payload.get("data"), list):
        return [item for item in payload["data"] if isinstance(item, dict)]
    raise ValueError("Beklenmeyen TurkiyeAPI veri biçimi.")


def _fetch_json(url: str, timeout: int) -> tuple[list[dict[str, Any]], str, int]:
    started = time.perf_counter()
    request = Request(url, headers={"Accept": "application/json", "User-Agent": "ALO186-KnowledgeGraph/1.0"})
    with urlopen(request, timeout=timeout) as response:  # noqa: S310 - allowlisted sabit URL
        body = response.read()
    payload = json.loads(body.decode("utf-8"))
    duration_ms = int((time.perf_counter() - started) * 1000)
    return _dataset_array(payload), hashlib.sha256(body).hexdigest(), duration_ms


def _province_id(item: dict[str, Any]) -> int:
    return int(item.get("provinceId") or item.get("province_id") or (item.get("province") or {}).get("id") or 0)


def _company_for_province(province_id: int, district_name: str | None = None) -> dict[str, Any] | None:
    if province_id == 34 and district_name:
        if district_name in ISTANBUL_EUROPE:
            return next(item for item in COMPANIES if item["id"] == "bedas")
        if district_name in ISTANBUL_ASIA:
            return next(item for item in COMPANIES if item["id"] == "ayedas")
        return None
    return next((item for item in COMPANIES if province_id in item["province_ids"] and not item.get("district_mode")), None)


def _verification(db, *, source: KnowledgeSource, status: str, duration_ms: int | None, content_hash: str | None, details: dict[str, Any]) -> None:
    db.add(
        KnowledgeVerificationRun(
            scope_key=GLOBAL_SCOPE,
            source_id=source.id,
            status=status,
            checked_at=utcnow(),
            duration_ms=duration_ms,
            content_hash=content_hash,
            details_json=json.dumps(details, ensure_ascii=False, sort_keys=True),
        )
    )


def sync_public_graph(*, timeout: int = 30, strict: bool = False) -> dict[str, Any]:
    db = SessionLocal()
    now = utcnow()
    counts = {"entities_created": 0, "entities_updated": 0, "assertions_created": 0, "assertions_updated": 0, "sources_created": 0, "sources_updated": 0}
    try:
        turkiye_source, created = upsert_source(
            db,
            scope_key=GLOBAL_SCOPE,
            organization_id=None,
            canonical_key="source:turkiyeapi:2025",
            name="TurkiyeAPI 2025 Administrative Dataset",
            source_type="dataset",
            url="https://docs.turkiyeapi.dev/en/v2/guide/datasets",
            authority_score=0.8,
            license_name="MIT",
            status="active",
        )
        counts["sources_created" if created else "sources_updated"] += 1
        distribution_source, created = upsert_source(
            db,
            scope_key=GLOBAL_SCOPE,
            organization_id=None,
            canonical_key="source:alo186:distribution-catalog",
            name="ALO186 Elektrik Dağıtım Bölgesi Kataloğu",
            source_type="repository",
            url="https://github.com/ozaneryavuz/chatgpt/tree/main/alo186/turkiye-arama",
            authority_score=0.9,
            license_name="ALO186 editorial",
            status="active",
            last_checked_at=now,
        )
        counts["sources_created" if created else "sources_updated"] += 1
        decision_source, created = upsert_source(
            db,
            scope_key=GLOBAL_SCOPE,
            organization_id=None,
            canonical_key="source:alo186:decision-rules",
            name="ALO186 25 Sorunlu Elektrik Karar Kuralları",
            source_type="repository",
            url="https://github.com/ozaneryavuz/chatgpt/tree/main/alo186/karar-motoru",
            authority_score=0.9,
            license_name="ALO186 editorial",
            status="active",
            last_checked_at=now,
        )
        counts["sources_created" if created else "sources_updated"] += 1
        product_source, created = upsert_source(
            db,
            scope_key=GLOBAL_SCOPE,
            organization_id=None,
            canonical_key="source:alo186:product-catalog",
            name="ALO186 Doğrulanmış Ürün Kataloğu",
            source_type="repository",
            url="https://github.com/ozaneryavuz/chatgpt/tree/main/alo186/urun-eslestirme",
            authority_score=0.7,
            license_name="ALO186 editorial",
            status="active",
            last_checked_at=now,
        )
        counts["sources_created" if created else "sources_updated"] += 1
        tool_source, created = upsert_source(
            db,
            scope_key=GLOBAL_SCOPE,
            organization_id=None,
            canonical_key="source:alo186:tool-registry",
            name="ALO186 Araç ve URL Kataloğu",
            source_type="repository",
            url="https://github.com/ozaneryavuz/chatgpt/tree/main/alo186",
            authority_score=0.85,
            license_name="ALO186 editorial",
            status="active",
            last_checked_at=now,
        )
        counts["sources_created" if created else "sources_updated"] += 1

        provinces: list[dict[str, Any]] = []
        districts: list[dict[str, Any]] = []
        remote_error: str | None = None
        try:
            provinces, province_hash, province_duration = _fetch_json(PROVINCES_URL, timeout)
            districts, district_hash, district_duration = _fetch_json(DISTRICTS_URL, timeout)
            turkiye_source.content_hash = hashlib.sha256(f"{province_hash}:{district_hash}".encode()).hexdigest()
            turkiye_source.last_checked_at = now
            turkiye_source.status = "active"
            _verification(
                db,
                source=turkiye_source,
                status="verified",
                duration_ms=province_duration + district_duration,
                content_hash=turkiye_source.content_hash,
                details={"provinces": len(provinces), "districts": len(districts), "dataset_version": "2025"},
            )
            if strict and (len(provinces) != 81 or len(districts) < 950):
                raise RuntimeError("TurkiyeAPI kapsamı beklenen 81 il / 950+ ilçe sınırının altında.")
        except (HTTPError, URLError, TimeoutError, ValueError, RuntimeError) as exc:
            remote_error = str(exc)
            turkiye_source.status = "unreachable"
            turkiye_source.last_checked_at = now
            _verification(
                db,
                source=turkiye_source,
                status="unreachable",
                duration_ms=None,
                content_hash=None,
                details={"error": remote_error},
            )
            if strict:
                raise

        entity_by_key: dict[str, Any] = {}

        def entity(canonical_key: str, kind: str, name: str, description: str | None = None, properties: dict[str, Any] | None = None):
            row, was_created = upsert_entity(
                db,
                scope_key=GLOBAL_SCOPE,
                organization_id=None,
                canonical_key=canonical_key,
                kind=kind,
                name=name,
                description=description,
                properties=properties,
                is_public=True,
                status="active",
            )
            entity_by_key[canonical_key] = row
            counts["entities_created" if was_created else "entities_updated"] += 1
            return row

        def assertion(subject_key: str, predicate: str, source: KnowledgeSource, *, object_key: str | None = None, literal: Any = None, confidence: float = 1.0, properties: dict[str, Any] | None = None):
            row, was_created = upsert_assertion(
                db,
                scope_key=GLOBAL_SCOPE,
                organization_id=None,
                subject_entity_id=entity_by_key[subject_key].id,
                predicate=predicate,
                object_entity_id=entity_by_key[object_key].id if object_key else None,
                literal_value=literal,
                source_id=source.id,
                confidence=confidence,
                status="active",
                is_public=True,
                verified_at=now,
                evidence={"subject": subject_key, "predicate": predicate, "object": object_key, "literal": literal},
                properties=properties,
            )
            counts["assertions_created" if was_created else "assertions_updated"] += 1
            return row

        for route_key, route_name, kind, props in ROUTES:
            entity(route_key, kind, route_name, properties=props)

        for company in COMPANIES:
            entity(
                f"distribution-company:{company['id']}",
                "DistributionCompany",
                company["name"],
                properties={
                    "slug": company["slug"],
                    "url": f"https://www.alo186.com/dagitim-sirketleri/{company['slug']}",
                    "provinceIds": company["province_ids"],
                    "districtMode": company.get("district_mode"),
                },
            )
            assertion(
                f"distribution-company:{company['id']}",
                "hasOfficialChannel",
                distribution_source,
                object_key="route:186",
                confidence=1.0,
            )

        province_names: dict[int, str] = {}
        for item in provinces:
            province_id = int(item.get("id") or 0)
            name = str(item.get("name") or "").strip()
            if not province_id or not name:
                continue
            province_names[province_id] = name
            entity(
                f"province:{province_id}",
                "Province",
                name,
                properties={"provinceId": province_id, "datasetVersion": "2025"},
            )
            if province_id == 34:
                for company_id, coverage in (("bedas", "europe"), ("ayedas", "asia")):
                    assertion(
                        f"province:{province_id}",
                        "servedBy",
                        distribution_source,
                        object_key=f"distribution-company:{company_id}",
                        confidence=0.8,
                        properties={"coverage": coverage, "requiresDistrict": True},
                    )
            else:
                company = _company_for_province(province_id)
                if company:
                    assertion(
                        f"province:{province_id}",
                        "servedBy",
                        distribution_source,
                        object_key=f"distribution-company:{company['id']}",
                        confidence=1.0,
                    )

        for item in districts:
            district_id = int(item.get("id") or 0)
            province_id = _province_id(item)
            name = str(item.get("name") or "").strip()
            if not district_id or not province_id or not name or province_id not in province_names:
                continue
            entity(
                f"district:{district_id}",
                "District",
                name,
                properties={"districtId": district_id, "provinceId": province_id, "datasetVersion": "2025"},
            )
            assertion(
                f"district:{district_id}",
                "partOf",
                turkiye_source,
                object_key=f"province:{province_id}",
                confidence=1.0,
            )
            company = _company_for_province(province_id, name)
            if company:
                assertion(
                    f"district:{district_id}",
                    "servedBy",
                    distribution_source,
                    object_key=f"distribution-company:{company['id']}",
                    confidence=1.0,
                )

        for problem_id, label, category, route_key, risk in PROBLEMS:
            entity(
                f"problem:{problem_id}",
                "Problem",
                label,
                properties={"category": category, "riskLevel": risk},
            )
            assertion(
                f"problem:{problem_id}",
                "routesTo",
                decision_source,
                object_key=route_key,
                confidence=1.0,
                properties={"riskLevel": risk},
            )
            assertion(
                f"problem:{problem_id}",
                "hasRiskLevel",
                decision_source,
                literal=risk,
                confidence=1.0,
            )

        for tool_key, name, path in TOOLS:
            entity(
                tool_key,
                "Tool",
                name,
                properties={"url": f"https://www.alo186.com{path}"},
            )

        for category_key, name in PRODUCT_CATEGORIES:
            entity(category_key, "ProductCategory", name)
            assertion(
                "tool:product-matcher",
                "supports",
                tool_source,
                object_key=category_key,
                confidence=1.0,
            )

        for product_key, name, category_key in PRODUCTS:
            asin = product_key.rsplit(":", 1)[-1]
            entity(
                product_key,
                "Product",
                name,
                properties={
                    "asin": asin,
                    "marketplace": "amazon.com.tr",
                    "affiliateDisclosure": True,
                    "priceStored": False,
                    "stockStored": False,
                },
            )
            assertion(
                product_key,
                "partOf",
                product_source,
                object_key=category_key,
                confidence=0.8,
            )
            assertion(
                product_key,
                "derivedFrom",
                product_source,
                literal=f"https://www.amazon.com.tr/dp/{asin}",
                confidence=0.7,
            )

        if "tool:edas-finder" in entity_by_key:
            for company in COMPANIES:
                assertion(
                    "tool:edas-finder",
                    "supports",
                    tool_source,
                    object_key=f"distribution-company:{company['id']}",
                    confidence=1.0,
                )
        if "tool:decision-engine" in entity_by_key:
            for problem_id, *_rest in PROBLEMS:
                assertion(
                    "tool:decision-engine",
                    "supports",
                    tool_source,
                    object_key=f"problem:{problem_id}",
                    confidence=1.0,
                )

        db.commit()
        health = graph_health(db, public_only=True, stale_days=30)
        return {
            **counts,
            "provinces": len(provinces),
            "districts": len(districts),
            "remote_error": remote_error,
            "health": health,
        }
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="ALO186 public Knowledge Graph seed/sync")
    parser.add_argument("command", choices=["sync-public"])
    parser.add_argument("--timeout", type=int, default=30)
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args(argv)
    result = sync_public_graph(timeout=max(5, args.timeout), strict=args.strict)
    print(json.dumps(result, ensure_ascii=False, default=str, indent=2))
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
