from __future__ import annotations

import re
from datetime import date, datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from core import (
    DRAFT_STATES,
    READY_STATES,
    Finding,
    InventoryItem,
    collect_schema_types,
    normalize_route,
    read_json,
    similarity,
    strip_markup,
)
from inventory import build_inventory


def weighted_score(item: dict[str, Any], config: dict[str, Any]) -> float:
    scores = item.get("scores")
    if not isinstance(scores, dict):
        return 0.0
    try:
        return round(
            sum(float(scores.get(key, 0)) * float(weight) for key, weight in config["scoringWeights"].items()),
            2,
        )
    except (TypeError, ValueError):
        return 0.0


def age_days(value: str, today: date) -> int | None:
    try:
        return (today - date.fromisoformat(value)).days
    except (TypeError, ValueError):
        return None


def valid_https_url(value: Any) -> bool:
    if not isinstance(value, str) or not value.strip():
        return False
    parsed = urlparse(value.strip())
    return parsed.scheme == "https" and bool(parsed.hostname) and not parsed.username and not parsed.password


def valid_text(value: Any, minimum: int, maximum: int | None = None) -> bool:
    if not isinstance(value, str):
        return False
    length = len(value.strip())
    return length >= minimum and (maximum is None or length <= maximum)


def item_similarity(item: dict[str, Any], existing: InventoryItem) -> float:
    candidate = " ".join(str(item.get(key, "")) for key in ("title", "task", "intentBoundary", "proposedRoute"))
    current = " ".join((existing.title, existing.h1, existing.description, existing.route))
    return similarity(candidate, current)


def shape_findings(item: dict[str, Any], index: int, config: dict[str, Any]) -> list[Finding]:
    subject = str(item.get("id") or f"items[{index}]")
    required = {
        "id", "status", "topic", "cluster", "contentType", "title", "task",
        "intentBoundary", "proposedRoute", "scores", "sources", "internalLinks",
        "schemaTypes", "conversion", "safetyBoundary",
    }
    missing = sorted(required - set(item))
    if missing:
        return [Finding("error", "required_fields_missing", subject, ", ".join(missing))]

    out: list[Finding] = []
    if item["status"] not in config["states"]:
        out.append(Finding("error", "status_invalid", subject, str(item["status"])))
    if item["topic"] not in config["topics"]:
        out.append(Finding("error", "topic_invalid", subject, str(item["topic"])))
    if item["contentType"] not in {"article", "tool", "business-tool"}:
        out.append(Finding("error", "content_type_invalid", subject, str(item["contentType"])))
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{4,80}", str(item["id"])):
        out.append(Finding("error", "id_invalid", subject, "küçük harf, sayı ve tire"))

    route = normalize_route(str(item["proposedRoute"]))
    if not route or not re.fullmatch(r"/[a-z0-9/-]+", route):
        out.append(Finding("error", "route_invalid", subject, str(item["proposedRoute"])))
    if not valid_text(item["task"], 60):
        out.append(Finding("error", "task_too_short", subject, "en az 60 karakter"))
    if not valid_text(item["intentBoundary"], 60):
        out.append(Finding("error", "intent_boundary_too_short", subject, "en az 60 karakter"))
    if not valid_text(item["safetyBoundary"], 30):
        out.append(Finding("error", "safety_boundary_too_short", subject, "en az 30 karakter"))

    expected = set(config["scoringWeights"])
    scores = item.get("scores")
    if not isinstance(scores, dict) or set(scores) != expected:
        out.append(Finding("error", "scores_invalid", subject, ", ".join(sorted(expected))))
    elif any(
        isinstance(value, bool)
        or not isinstance(value, (int, float))
        or not 0 <= float(value) <= 100
        for value in scores.values()
    ):
        out.append(Finding("error", "score_out_of_range", subject, str(scores)))

    conversion = item.get("conversion")
    events = conversion.get("events") if isinstance(conversion, dict) else None
    if (
        not isinstance(events, list)
        or not events
        or len(set(map(str, events))) != len(events)
        or any(not isinstance(event, str) or not re.fullmatch(r"[a-z0-9_]{5,80}", event) for event in events)
    ):
        out.append(Finding("error", "conversion_events_invalid", subject, str(events)))
    return out


def validate_queue(
    queue: dict[str, Any],
    config: dict[str, Any],
    inventory: list[InventoryItem],
    base_findings: list[Finding],
    today: date,
) -> tuple[list[Finding], list[dict[str, Any]]]:
    findings = list(base_findings)
    raw_items = queue.get("items")
    if not isinstance(raw_items, list):
        return findings + [Finding("error", "queue_items_invalid", "queue", "items dizi değil")], []

    items: list[dict[str, Any]] = []
    ids: set[str] = set()
    routes: set[str] = set()
    inventory_routes = {normalize_route(item.route) for item in inventory} | {
        normalize_route(item.canonical) for item in inventory
    }
    policy = config["runPolicy"]
    allowed_classes = set(config["sourcePolicy"]["allowedClasses"])
    primary_classes = set(config["sourcePolicy"]["primaryClasses"])
    blocked_domains = set(config["sourcePolicy"]["blockedDomains"])
    forbidden_types = set(config["schemaPolicy"]["forbiddenTypes"])

    for index, raw in enumerate(raw_items):
        if not isinstance(raw, dict):
            findings.append(Finding("error", "queue_item_invalid", f"items[{index}]", "nesne değil"))
            continue
        item = dict(raw)
        item_findings = shape_findings(item, index, config)
        findings.extend(item_findings)
        subject = str(item.get("id") or f"items[{index}]")
        route = normalize_route(str(item.get("proposedRoute", "")))
        item["weightedScore"] = weighted_score(item, config)
        item["normalizedRoute"] = route

        if subject in ids:
            findings.append(Finding("error", "duplicate_id", subject, subject))
        if route and route in routes:
            findings.append(Finding("error", "duplicate_queue_route", subject, route))
        ids.add(subject)
        if route:
            routes.add(route)

        status = item.get("status")
        if status in READY_STATES and item["weightedScore"] < float(policy["minimumPublishScore"]):
            findings.append(
                Finding(
                    "error",
                    "score_below_publish_threshold",
                    subject,
                    f"{item['weightedScore']} < {policy['minimumPublishScore']}",
                )
            )
        exists = bool(route) and route in inventory_routes
        if status == "published" and not exists:
            findings.append(Finding("error", "published_route_missing", subject, route))
        elif status != "published" and exists:
            findings.append(Finding("error", "route_collision", subject, route))

        if status != "published" and inventory:
            nearest = min(
                ((item_similarity(item, existing), existing) for existing in inventory),
                key=lambda pair: (-pair[0], pair[1].canonical),
            )
            score, existing = nearest
            if score >= float(policy["warningCollisionThreshold"]):
                existing_route = normalize_route(existing.canonical or existing.route)
                item["nearestExisting"] = {
                    "route": existing_route,
                    "source": existing.source,
                    "similarity": round(score, 3),
                }
                supporting = normalize_route(str(item.get("supportingOf") or ""))
                if score >= float(policy["collisionThreshold"]) and supporting != existing_route:
                    findings.append(
                        Finding("error", "intent_collision", subject, f"{existing_route} similarity={score:.3f}")
                    )
                elif score < float(policy["collisionThreshold"]):
                    findings.append(
                        Finding("warning", "intent_similarity_review", subject, f"{existing_route} similarity={score:.3f}")
                    )

        if status in READY_STATES:
            sources = item.get("sources") if isinstance(item.get("sources"), list) else []
            if len(sources) < int(policy["minimumSources"]):
                findings.append(Finding("error", "sources_too_few", subject, str(len(sources))))
            primary_count = 0
            urls: set[str] = set()
            for source_index, source in enumerate(sources):
                source_subject = f"{subject}.sources[{source_index}]"
                if not isinstance(source, dict):
                    findings.append(Finding("error", "source_invalid", source_subject, "nesne değil"))
                    continue
                url = source.get("url")
                parsed = urlparse(url) if isinstance(url, str) else urlparse("")
                domain = (parsed.hostname or "").casefold()
                if not valid_https_url(url):
                    findings.append(Finding("error", "source_url_invalid", source_subject, str(url)))
                if domain in blocked_domains:
                    findings.append(Finding("error", "source_domain_blocked", source_subject, domain))
                if isinstance(url, str) and url in urls:
                    findings.append(Finding("error", "source_duplicate", source_subject, url))
                if isinstance(url, str):
                    urls.add(url)

                source_class = str(source.get("class", ""))
                if source_class not in allowed_classes:
                    findings.append(Finding("error", "source_class_invalid", source_subject, source_class))
                if source.get("primary") is True and source_class in primary_classes:
                    primary_count += 1
                source_age = age_days(str(source.get("verifiedAt", "")), today)
                if source_age is None or source_age < 0:
                    findings.append(
                        Finding("error", "source_verified_date_invalid", source_subject, str(source.get("verifiedAt")))
                    )
                elif source_age > int(policy["maximumSourceAgeDays"]):
                    findings.append(Finding("error", "source_stale", source_subject, f"{source_age} gün"))
                claims = source.get("claims")
                if not isinstance(claims, list) or not claims or any(not valid_text(claim, 1) for claim in claims):
                    findings.append(Finding("error", "source_claims_missing", source_subject, "kanıtlanan iddia yok"))

            if primary_count < int(policy["minimumPrimarySources"]):
                findings.append(Finding("error", "primary_sources_too_few", subject, str(primary_count)))

            raw_links = item.get("internalLinks") if isinstance(item.get("internalLinks"), list) else []
            normalized_links = {normalize_route(str(link)) for link in raw_links if normalize_route(str(link))}
            if len(normalized_links) < int(policy["minimumInternalLinks"]):
                findings.append(Finding("error", "internal_links_too_few", subject, str(len(normalized_links))))
            missing_links = sorted(normalized_links - inventory_routes)
            if missing_links:
                findings.append(Finding("error", "internal_link_missing", subject, ", ".join(missing_links)))

            required_types = set(config["schemaPolicy"].get(str(item.get("contentType")), []))
            supplied_types = set(map(str, item.get("schemaTypes", []))) if isinstance(item.get("schemaTypes"), list) else set()
            if not required_types <= supplied_types:
                findings.append(
                    Finding("error", "schema_types_missing", subject, ", ".join(sorted(required_types - supplied_types)))
                )
            blocked_types = supplied_types & forbidden_types
            if blocked_types:
                findings.append(
                    Finding("error", "forbidden_schema_type", subject, ", ".join(sorted(blocked_types)))
                )
            if (
                item.get("cluster") in config["commercialPolicy"]["forbiddenAffiliateOnClusters"]
                and isinstance(item.get("conversion"), dict)
                and item["conversion"].get("affiliateAllowed") is True
            ):
                findings.append(
                    Finding("error", "affiliate_forbidden_for_cluster", subject, str(item.get("cluster")))
                )

        if status in DRAFT_STATES:
            draft = item.get("draft")
            if not isinstance(draft, dict):
                findings.append(Finding("error", "draft_missing_for_state", subject, str(status)))
            else:
                blocked = collect_schema_types(draft.get("jsonLd")) & forbidden_types
                if blocked:
                    findings.append(
                        Finding("error", "forbidden_schema_in_draft", subject, ", ".join(sorted(blocked)))
                    )
        items.append(item)
    return findings, items


def validate_draft(path: Path, config: dict[str, Any], repo: Path, today: date) -> list[Finding]:
    draft = read_json(path)
    subject = str(draft.get("id") or path.name)
    out: list[Finding] = []
    required = {
        "id", "route", "title", "description", "h1", "directAnswer", "bodyHtml",
        "faqs", "jsonLd", "internalLinks", "sourceCitations", "cta",
        "analyticsEvents", "intentBoundary", "safetyBoundary", "verifiedAt",
    }
    missing = sorted(required - set(draft))
    if missing:
        return [Finding("error", "draft_required_fields_missing", subject, ", ".join(missing))]
    extra = sorted(set(draft) - required)
    if extra:
        out.append(Finding("error", "draft_unexpected_fields", subject, ", ".join(extra)))

    if not valid_text(draft.get("id"), 1, 100):
        out.append(Finding("error", "draft_id_invalid", subject, str(draft.get("id"))))
    route = draft.get("route")
    normalized_route = normalize_route(route) if isinstance(route, str) else ""
    if not normalized_route or not re.fullmatch(r"/[a-z0-9/-]+", normalized_route):
        out.append(Finding("error", "draft_route_invalid", subject, str(route)))
    if not valid_text(draft.get("title"), 20, 140):
        out.append(Finding("error", "draft_title_length", subject, str(len(str(draft.get("title", ""))))))
    if not valid_text(draft.get("description"), 70, 190):
        out.append(Finding("error", "draft_description_length", subject, str(len(str(draft.get("description", ""))))))
    if not valid_text(draft.get("h1"), 15, 150):
        out.append(Finding("error", "draft_h1_length", subject, str(len(str(draft.get("h1", ""))))))
    if not valid_text(draft.get("directAnswer"), 120, 1200):
        out.append(
            Finding("error", "draft_direct_answer_length", subject, str(len(str(draft.get("directAnswer", "")))))
        )
    body_html = draft.get("bodyHtml")
    if not isinstance(body_html, str) or len(body_html) < 800:
        out.append(Finding("error", "draft_body_html_length", subject, str(len(str(body_html or "")))))
    visible_body_length = len(strip_markup(body_html if isinstance(body_html, str) else ""))
    if visible_body_length < 700:
        out.append(Finding("error", "draft_body_visible_short", subject, str(visible_body_length)))

    faqs = draft.get("faqs")
    if not isinstance(faqs, list) or len(faqs) < 3:
        out.append(Finding("error", "draft_faq_low", subject, str(len(faqs) if isinstance(faqs, list) else 0)))
    else:
        for index, faq in enumerate(faqs):
            faq_subject = f"{subject}.faqs[{index}]"
            if not isinstance(faq, dict) or set(faq) != {"question", "answer"}:
                out.append(Finding("error", "draft_faq_contract_invalid", faq_subject, str(faq)))
                continue
            if not valid_text(faq.get("question"), 10):
                out.append(Finding("error", "draft_faq_question_short", faq_subject, str(faq.get("question"))))
            if not valid_text(faq.get("answer"), 40):
                out.append(Finding("error", "draft_faq_answer_short", faq_subject, str(faq.get("answer"))))

    jsonld = draft.get("jsonLd")
    if not isinstance(jsonld, (dict, list)) or not jsonld:
        out.append(Finding("error", "draft_jsonld_empty", subject, str(jsonld)))
        schema_types: set[str] = set()
    else:
        schema_types = collect_schema_types(jsonld)
        support_types = {"FAQPage", "BreadcrumbList"}
        if not support_types <= schema_types:
            out.append(
                Finding(
                    "error",
                    "draft_jsonld_support_types_missing",
                    subject,
                    ", ".join(sorted(support_types - schema_types)),
                )
            )
        if not schema_types.intersection({"Article", "WebApplication"}):
            out.append(
                Finding("error", "draft_jsonld_primary_type_missing", subject, ", ".join(sorted(schema_types)))
            )
    blocked_schema = schema_types & set(config["schemaPolicy"]["forbiddenTypes"])
    if blocked_schema:
        out.append(Finding("error", "draft_forbidden_schema", subject, ", ".join(sorted(blocked_schema))))

    inventory, inventory_findings = build_inventory(repo)
    out.extend(finding for finding in inventory_findings if finding.level == "error")
    inventory_routes = {normalize_route(item.route) for item in inventory} | {
        normalize_route(item.canonical) for item in inventory
    }
    internal_links = draft.get("internalLinks")
    if not isinstance(internal_links, list) or any(not isinstance(link, str) for link in internal_links):
        out.append(Finding("error", "draft_internal_links_invalid", subject, str(internal_links)))
        normalized_links: set[str] = set()
    else:
        normalized_links = {normalize_route(link) for link in internal_links if normalize_route(link)}
        if len(normalized_links) != len(internal_links):
            out.append(
                Finding("error", "draft_internal_links_duplicate_or_empty", subject, str(internal_links))
            )
    missing_links = normalized_links - inventory_routes
    if missing_links:
        out.append(Finding("error", "draft_internal_link_missing", subject, ", ".join(sorted(missing_links))))
    if len(normalized_links) < int(config["runPolicy"]["minimumInternalLinks"]):
        out.append(Finding("error", "draft_internal_links_low", subject, str(len(normalized_links))))

    citations = draft.get("sourceCitations")
    if not isinstance(citations, list) or len(citations) < int(config["runPolicy"]["minimumSources"]):
        out.append(
            Finding(
                "error",
                "draft_source_citations_low",
                subject,
                str(len(citations) if isinstance(citations, list) else 0),
            )
        )
    elif any(not valid_https_url(citation) for citation in citations):
        out.append(Finding("error", "draft_source_citation_invalid", subject, str(citations)))
    elif len(set(citations)) != len(citations):
        out.append(Finding("error", "draft_source_citation_duplicate", subject, str(citations)))

    cta = draft.get("cta")
    if not isinstance(cta, dict) or set(cta) != {"primary", "secondary"}:
        out.append(Finding("error", "draft_cta_invalid", subject, str(cta)))
    else:
        if not valid_text(cta.get("primary"), 5):
            out.append(Finding("error", "draft_primary_cta_invalid", subject, str(cta.get("primary"))))
        if not valid_text(cta.get("secondary"), 5):
            out.append(Finding("error", "draft_secondary_cta_invalid", subject, str(cta.get("secondary"))))

    events = draft.get("analyticsEvents")
    if (
        not isinstance(events, list)
        or not events
        or len(set(map(str, events))) != len(events)
        or any(not isinstance(event, str) or not re.fullmatch(r"[a-z0-9_]{5,80}", event) for event in events)
    ):
        out.append(Finding("error", "draft_analytics_events_invalid", subject, str(events)))
    if not valid_text(draft.get("intentBoundary"), 60):
        out.append(
            Finding("error", "draft_intent_boundary_short", subject, str(len(str(draft.get("intentBoundary", "")))))
        )
    if not valid_text(draft.get("safetyBoundary"), 30):
        out.append(
            Finding("error", "draft_safety_boundary_short", subject, str(len(str(draft.get("safetyBoundary", "")))))
        )

    verified_age = age_days(draft.get("verifiedAt") if isinstance(draft.get("verifiedAt"), str) else "", today)
    if (
        verified_age is None
        or verified_age < 0
        or verified_age > int(config["runPolicy"]["maximumSourceAgeDays"])
    ):
        out.append(Finding("error", "draft_verified_date_invalid", subject, str(draft.get("verifiedAt"))))
    text = " ".join(
        str(draft.get(key, "")) for key in ("title", "description", "directAnswer", "bodyHtml")
    ).casefold()
    for claim in config["commercialPolicy"]["forbiddenClaims"]:
        if claim.casefold() in text:
            out.append(Finding("error", "draft_forbidden_claim", subject, claim))
    return out


def validate_receipt(path: Path, config: dict[str, Any]) -> list[Finding]:
    receipt = read_json(path)
    subject = str(receipt.get("contentId") or path.name)
    out: list[Finding] = []
    required = {
        "siteSlug", "sourceCommit", "contentId", "contentHash", "canonicalUrl",
        "deploymentUrl", "publishedAt", "liveVerified",
    }
    allowed = required | {"verification"}
    missing = sorted(required - set(receipt))
    if missing:
        return [Finding("error", "receipt_fields_missing", subject, ", ".join(missing))]
    extra = sorted(set(receipt) - allowed)
    if extra:
        out.append(Finding("error", "receipt_unexpected_fields", subject, ", ".join(extra)))

    if receipt["siteSlug"] != config["site"]["slug"]:
        out.append(Finding("error", "receipt_site_slug_mismatch", subject, str(receipt["siteSlug"])))
    if not re.fullmatch(r"[0-9a-f]{7,40}", str(receipt["sourceCommit"])):
        out.append(Finding("error", "receipt_commit_invalid", subject, str(receipt["sourceCommit"])))
    if not valid_text(receipt.get("contentId"), 1, 100):
        out.append(Finding("error", "receipt_content_id_invalid", subject, str(receipt.get("contentId"))))
    if not re.fullmatch(r"[0-9a-f]{64}", str(receipt["contentHash"])):
        out.append(Finding("error", "receipt_hash_invalid", subject, str(receipt["contentHash"])))

    canonical = urlparse(str(receipt["canonicalUrl"]))
    origin = urlparse(config["site"]["canonicalOrigin"])
    if canonical.scheme != "https" or canonical.hostname != origin.hostname or not canonical.path.startswith("/"):
        out.append(Finding("error", "receipt_canonical_invalid", subject, str(receipt["canonicalUrl"])))
    if not valid_https_url(receipt.get("deploymentUrl")):
        out.append(
            Finding("error", "receipt_deployment_url_invalid", subject, str(receipt.get("deploymentUrl")))
        )
    if receipt["liveVerified"] is not True:
        out.append(Finding("error", "receipt_live_not_verified", subject, "liveVerified true olmalı"))
    try:
        published = datetime.fromisoformat(str(receipt["publishedAt"]).replace("Z", "+00:00"))
        if published.tzinfo is None:
            raise ValueError("timezone gerekli")
    except (TypeError, ValueError):
        out.append(Finding("error", "receipt_published_at_invalid", subject, str(receipt["publishedAt"])))

    verification = receipt.get("verification")
    if verification is not None:
        allowed_verification = {
            "httpStatus", "canonicalMatched", "titleMatched", "structuredDataPresent",
        }
        if not isinstance(verification, dict) or set(verification) - allowed_verification:
            out.append(Finding("error", "receipt_verification_invalid", subject, str(verification)))
        else:
            http_status = verification.get("httpStatus")
            if (
                http_status is not None
                and (
                    isinstance(http_status, bool)
                    or not isinstance(http_status, int)
                    or not 100 <= http_status <= 599
                )
            ):
                out.append(Finding("error", "receipt_http_status_invalid", subject, str(http_status)))
            for key in ("canonicalMatched", "titleMatched", "structuredDataPresent"):
                if key in verification and not isinstance(verification[key], bool):
                    out.append(
                        Finding(
                            "error",
                            "receipt_verification_boolean_invalid",
                            subject,
                            f"{key}={verification[key]}",
                        )
                    )
    return out
