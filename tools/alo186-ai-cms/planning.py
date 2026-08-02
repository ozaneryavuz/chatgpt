from __future__ import annotations

import html
from datetime import date
from typing import Any

from core import Finding, normalize_route, stable_hash


def errors_for_item(item: dict[str, Any], findings: list[Finding]) -> list[Finding]:
    item_id = str(item.get("id", ""))
    return [
        finding
        for finding in findings
        if finding.level == "error"
        and (finding.subject == item_id or finding.subject.startswith(item_id + "."))
    ]


def rank_ready(
    items: list[dict[str, Any]],
    findings: list[Finding],
    config: dict[str, Any],
    limit: int,
) -> list[dict[str, Any]]:
    policy = config["runPolicy"]
    maximum = int(policy["maximumSelections"])
    if isinstance(limit, bool) or not 0 <= int(limit) <= maximum:
        raise ValueError(f"limit 0-{maximum} arasında olmalı")

    candidates = [
        item
        for item in items
        if item.get("status") == "ready" and not errors_for_item(item, findings)
    ]
    candidates.sort(
        key=lambda item: (
            -float(item.get("weightedScore", 0)),
            -float(item.get("scores", {}).get("taskCompletionValue", 0)),
            -float(item.get("scores", {}).get("sourceConfidence", 0)),
            str(item.get("id", "")),
        )
    )

    selected: list[dict[str, Any]] = []
    per_cluster: dict[str, int] = {}
    cluster_cap = int(policy["maximumPerCluster"])
    for item in candidates:
        cluster = str(item.get("cluster", "unclassified"))
        if per_cluster.get(cluster, 0) >= cluster_cap:
            continue
        selected.append(item)
        per_cluster[cluster] = per_cluster.get(cluster, 0) + 1
        if len(selected) >= int(limit):
            break
    return selected


def make_brief(
    item: dict[str, Any],
    config: dict[str, Any],
    source_commit: str,
    today: date,
) -> dict[str, Any]:
    route = normalize_route(str(item["proposedRoute"]))
    brief: dict[str, Any] = {
        "cmsVersion": config["version"],
        "contentId": item["id"],
        "siteSlug": config["site"]["slug"],
        "sourceRepository": config["site"]["repository"],
        "sourceCommit": source_commit,
        "generatedAt": today.isoformat(),
        "route": route,
        "canonicalUrl": config["site"]["canonicalOrigin"] + route,
        "contentType": item["contentType"],
        "topic": item["topic"],
        "cluster": item["cluster"],
        "title": item["title"],
        "audience": item.get("audience", "ALO186 kullanıcıları"),
        "task": item["task"],
        "intentBoundary": item["intentBoundary"],
        "supportingOf": item.get("supportingOf"),
        "weightedScore": item["weightedScore"],
        "nearestExisting": item.get("nearestExisting"),
        "sources": item["sources"],
        "internalLinks": [normalize_route(str(route)) for route in item["internalLinks"]],
        "requiredSchemaTypes": item["schemaTypes"],
        "conversion": item["conversion"],
        "safetyBoundary": item["safetyBoundary"],
        "editorialRequirements": {
            "directAnswerRequired": True,
            "visibleFaqMinimum": 3,
            "sourceAttributionRequired": True,
            "existingContentSeparationRequired": True,
            "purchaseNotRequiredOutcome": config["commercialPolicy"]["purchaseNotRequiredOutcome"],
            "personalDataFieldsAllowed": config["privacyPolicy"]["personalDataFieldsAllowed"],
            "rawUserInputsToAnalyticsAllowed": config["privacyPolicy"]["analyticsMayReceiveRawUserInputs"],
            "forbiddenSchemaTypes": config["schemaPolicy"]["forbiddenTypes"],
            "forbiddenClaims": config["commercialPolicy"]["forbiddenClaims"],
        },
        "draftSchema": "tools/alo186-ai-cms/schemas/draft.schema.json",
        "validationCommand": (
            "python tools/alo186-ai-cms/cms.py --repo . validate-draft "
            f"drafts/{item['id']}.json"
        ),
    }
    brief["briefHash"] = stable_hash(brief)
    return brief


def make_sites_package(
    briefs: list[dict[str, Any]],
    config: dict[str, Any],
    source_commit: str,
) -> dict[str, Any]:
    operations: list[dict[str, Any]] = []
    for brief in briefs:
        route = normalize_route(str(brief["route"]))
        canonical_url = str(brief.get("canonicalUrl") or config["site"]["canonicalOrigin"] + route)
        brief_hash = str(brief.get("briefHash") or stable_hash(brief))
        required_schema_types = list(brief.get("requiredSchemaTypes", []))
        conversion = brief.get("conversion") if isinstance(brief.get("conversion"), dict) else {}
        events = list(conversion.get("events", []))
        operation = {
            "operationId": f"cms-{config['version']}-{brief['contentId']}",
            "action": "create-or-update-route",
            "siteSlug": config["site"]["slug"],
            "route": route,
            "canonicalUrl": canonical_url,
            "contentId": brief["contentId"],
            "briefPath": f"briefs/{brief['contentId']}.json",
            "briefHash": brief_hash,
            "requirePreview": True,
            "publish": False,
            "acceptance": {
                "canonicalMustMatch": True,
                "singleH1": True,
                "structuredDataTypes": required_schema_types,
                "forbiddenSchemaTypes": config["schemaPolicy"]["forbiddenTypes"],
                "minimumInternalLinks": config["runPolicy"]["minimumInternalLinks"],
                "sourceVerificationRequired": True,
                "safetyBoundaryRequired": True,
                "conversionEvents": events,
            },
        }
        operations.append(operation)

    package: dict[str, Any] = {
        "cmsVersion": config["version"],
        "target": "chatgpt-sites",
        "siteSlug": config["site"]["slug"],
        "sourceRepository": config["site"]["repository"],
        "sourceCommit": source_commit,
        "reviewPolicy": {
            "humanPreviewRequired": bool(config["runPolicy"]["requireHumanPreviewBeforeSitesDeploy"]),
            "automaticDeployAllowed": bool(config["runPolicy"]["allowAutomaticSitesDeploy"]),
            "undocumentedApiUseAllowed": False,
        },
        "operations": operations,
        "receiptSchema": "tools/alo186-ai-cms/schemas/sites-receipt.schema.json",
    }
    package["packageHash"] = stable_hash(package)
    return package


def render_sites_prompt(package: dict[str, Any], briefs: list[dict[str, Any]]) -> str:
    lines = [
        "Use @Sites to edit the site with the slug alo186, with:",
        "",
        "ALO186 AI CMS paketindeki aşağıdaki rotaları önizleme olarak uygula.",
        "Henüz yayınlama; her rota için canonical, tek H1, görünür doğrudan cevap, kaynaklar,",
        "iç bağlantılar, yapılandırılmış veri, güvenlik sınırı ve dönüşüm olaylarını doğrula.",
        "Product, Offer, AggregateOffer, AggregateRating, Person ve ProfilePage kullanma.",
        "ALO186'i resmî kurum, EDAŞ, EPDK, TEDAŞ, üretici veya satıcı gibi gösterme.",
        "Kişisel veri toplama ve kullanıcı girdilerini analitiğe gönderme.",
        "",
        f"Kaynak commit: {package['sourceCommit']}",
        f"Paket hash: {package['packageHash']}",
        "",
    ]
    if not briefs:
        lines.append("Bu çalıştırmada yayına uygun yeni brief seçilmedi; sitede değişiklik yapma.")
        return "\n".join(lines) + "\n"

    for index, brief in enumerate(briefs, start=1):
        lines.extend([
            f"## {index}. {brief['title']}",
            f"Rota: {brief['route']}",
            f"Canonical: {brief['canonicalUrl']}",
            f"Kullanıcı görevi: {brief['task']}",
            f"Mevcut içerikten ayrım: {brief['intentBoundary']}",
            f"Güvenlik sınırı: {brief['safetyBoundary']}",
            "Zorunlu şema: " + ", ".join(brief["requiredSchemaTypes"]),
            "İç bağlantılar: " + ", ".join(brief["internalLinks"]),
            "Dönüşüm olayları: " + ", ".join(brief["conversion"]["events"]),
            "Kaynaklar:",
        ])
        for source in brief["sources"]:
            claims = "; ".join(str(claim) for claim in source.get("claims", []))
            lines.append(f"- {source.get('publisher')}: {source.get('url')} — {claims}")
        lines.append("")
    lines.extend([
        "Önizleme sonunda her rota için kabul özeti üret. Kullanıcı açıkça yayın onayı vermeden publish etme.",
    ])
    return "\n".join(lines) + "\n"


def render_dashboard(
    report: dict[str, Any],
    selected: list[dict[str, Any]],
    package: dict[str, Any],
) -> str:
    cards: list[str] = []
    for item in selected:
        nearest = item.get("nearestExisting") or {}
        nearest_text = (
            f"En yakın içerik: {nearest.get('route')} ({nearest.get('similarity')})"
            if nearest else "Belirgin canonical çakışması yok"
        )
        cards.append(
            "<article class=\"card\">"
            f"<p class=\"score\">{html.escape(str(item['weightedScore']))}</p>"
            f"<h2>{html.escape(str(item['title']))}</h2>"
            f"<p><strong>Rota:</strong> {html.escape(str(item['normalizedRoute']))}</p>"
            f"<p>{html.escape(str(item['task']))}</p>"
            f"<p class=\"muted\">{html.escape(nearest_text)}</p>"
            "</article>"
        )
    if not cards:
        cards.append("<article class=\"card\"><h2>Hazır brief yok</h2><p>Kuyruk temiz; bu çalıştırmada site değişikliği önerilmedi.</p></article>")

    return f'''<!doctype html>
<html lang="tr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>ALO186 AI CMS v220</title>
<style>body{{margin:0;background:#f5f7fb;color:#11213b;font:16px/1.55 system-ui,sans-serif}}main{{max-width:1100px;margin:auto;padding:28px}}.hero,.card{{background:white;border:1px solid #dbe3ef;border-radius:16px;padding:20px;box-shadow:0 8px 30px #10213b0d}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:16px;margin-top:18px}}.score{{font-size:2rem;font-weight:800;margin:0;color:#0757c7}}.muted{{color:#52627a}}code{{word-break:break-all}}.ok{{color:#147a45}}.bad{{color:#b42318}}</style></head><body><main>
<section class="hero"><p>ALO186 · GitHub kaynaklı · ChatGPT Sites hedefli</p><h1>AI CMS v220 çalışma özeti</h1><p class="{'ok' if report['ok'] else 'bad'}"><strong>{'Yayın kapıları geçti' if report['ok'] else 'Yayın durduruldu'}</strong></p><p>Envanter: {report['metrics']['inventoryCount']} · Kuyruk: {report['metrics']['queueCount']} · Hata: {report['metrics']['errorCount']} · Uyarı: {report['metrics']['warningCount']}</p><p>Sites paketi: <code>{html.escape(package['packageHash'])}</code></p></section>
<section class="grid">{''.join(cards)}</section>
</main></body></html>'''


def make_report(
    *,
    config: dict[str, Any],
    queue: dict[str, Any],
    inventory_count: int,
    findings: list[Finding],
    items: list[dict[str, Any]],
    today: date,
) -> dict[str, Any]:
    errors = [finding for finding in findings if finding.level == "error"]
    warnings = [finding for finding in findings if finding.level == "warning"]
    return {
        "ok": not errors,
        "cmsVersion": config["version"],
        "generatedAt": today.isoformat(),
        "siteSlug": config["site"]["slug"],
        "livePlatform": config["site"]["livePlatform"],
        "metrics": {
            "inventoryCount": inventory_count,
            "queueCount": len(queue.get("items", [])) if isinstance(queue.get("items"), list) else 0,
            "readyCount": sum(item.get("status") == "ready" for item in items),
            "publishedCount": sum(item.get("status") == "published" for item in items),
            "errorCount": len(errors),
            "warningCount": len(warnings),
        },
        "findings": [finding.__dict__ for finding in findings],
        "queue": [
            {
                "id": item.get("id"),
                "status": item.get("status"),
                "cluster": item.get("cluster"),
                "route": item.get("normalizedRoute"),
                "weightedScore": item.get("weightedScore"),
                "nearestExisting": item.get("nearestExisting"),
            }
            for item in items
        ],
        "queueHash": stable_hash(queue),
    }
