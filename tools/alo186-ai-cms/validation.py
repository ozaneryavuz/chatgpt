from __future__ import annotations

import re
from datetime import date, datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from core import DRAFT_STATES, READY_STATES, Finding, InventoryItem, collect_schema_types, normalize_route, read_json, similarity, strip_markup
from inventory import build_inventory


def weighted_score(item: dict[str, Any], config: dict[str, Any]) -> float:
    return round(sum(float(item.get("scores", {}).get(key, 0)) * float(weight) for key, weight in config["scoringWeights"].items()), 2)


def age_days(value: str, today: date) -> int | None:
    try:
        return (today - date.fromisoformat(value)).days
    except (TypeError, ValueError):
        return None


def item_similarity(item: dict[str, Any], existing: InventoryItem) -> float:
    candidate = " ".join(str(item.get(k, "")) for k in ("title", "task", "intentBoundary", "proposedRoute"))
    current = " ".join((existing.title, existing.h1, existing.description, existing.route))
    return similarity(candidate, current)


def shape_findings(item: dict[str, Any], index: int, config: dict[str, Any]) -> list[Finding]:
    subject = str(item.get("id") or f"items[{index}]")
    required = {"id", "status", "topic", "cluster", "contentType", "title", "task", "intentBoundary", "proposedRoute", "scores", "sources", "internalLinks", "schemaTypes", "conversion", "safetyBoundary"}
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
    if len(str(item["task"])) < 60:
        out.append(Finding("error", "task_too_short", subject, "en az 60 karakter"))
    if len(str(item["intentBoundary"])) < 60:
        out.append(Finding("error", "intent_boundary_too_short", subject, "en az 60 karakter"))
    if len(str(item["safetyBoundary"])) < 30:
        out.append(Finding("error", "safety_boundary_too_short", subject, "en az 30 karakter"))
    expected = set(config["scoringWeights"])
    scores = item.get("scores")
    if not isinstance(scores, dict) or set(scores) != expected:
        out.append(Finding("error", "scores_invalid", subject, ", ".join(sorted(expected))))
    elif any(isinstance(v, bool) or not isinstance(v, (int, float)) or not 0 <= float(v) <= 100 for v in scores.values()):
        out.append(Finding("error", "score_out_of_range", subject, str(scores)))
    events = item.get("conversion", {}).get("events") if isinstance(item.get("conversion"), dict) else None
    if not isinstance(events, list) or not events or any(not re.fullmatch(r"[a-z0-9_]{5,80}", str(event)) for event in events):
        out.append(Finding("error", "conversion_events_invalid", subject, str(events)))
    return out


def validate_queue(queue: dict[str, Any], config: dict[str, Any], inventory: list[InventoryItem], base_findings: list[Finding], today: date) -> tuple[list[Finding], list[dict[str, Any]]]:
    findings = list(base_findings)
    raw_items = queue.get("items")
    if not isinstance(raw_items, list):
        return findings + [Finding("error", "queue_items_invalid", "queue", "items dizi değil")], []
    items: list[dict[str, Any]] = []
    ids: set[str] = set(); routes: set[str] = set()
    inventory_routes = {normalize_route(x.route) for x in inventory} | {normalize_route(x.canonical) for x in inventory}
    policy = config["runPolicy"]
    allowed = set(config["sourcePolicy"]["allowedClasses"]); primary_classes = set(config["sourcePolicy"]["primaryClasses"])
    blocked_domains = set(config["sourcePolicy"]["blockedDomains"]); forbidden = set(config["schemaPolicy"]["forbiddenTypes"])
    for index, raw in enumerate(raw_items):
        if not isinstance(raw, dict):
            findings.append(Finding("error", "queue_item_invalid", f"items[{index}]", "nesne değil")); continue
        item = dict(raw); findings.extend(shape_findings(item, index, config))
        subject = str(item.get("id") or f"items[{index}]"); route = normalize_route(str(item.get("proposedRoute", "")))
        item["weightedScore"] = weighted_score(item, config); item["normalizedRoute"] = route
        if subject in ids: findings.append(Finding("error", "duplicate_id", subject, subject))
        if route in routes: findings.append(Finding("error", "duplicate_queue_route", subject, route))
        ids.add(subject); routes.add(route)
        status = item.get("status")
        if status in READY_STATES and item["weightedScore"] < float(policy["minimumPublishScore"]):
            findings.append(Finding("error", "score_below_publish_threshold", subject, f"{item['weightedScore']} < {policy['minimumPublishScore']}"))
        exists = route in inventory_routes
        if status == "published" and not exists: findings.append(Finding("error", "published_route_missing", subject, route))
        elif status != "published" and exists: findings.append(Finding("error", "route_collision", subject, route))

        if status != "published":
            nearest = sorted(((item_similarity(item, old), old) for old in inventory), key=lambda pair: (-pair[0], pair[1].canonical))
            if nearest and nearest[0][0] >= float(policy["warningCollisionThreshold"]):
                score, old = nearest[0]; old_route = normalize_route(old.canonical or old.route)
                item["nearestExisting"] = {"route": old_route, "source": old.source, "similarity": round(score, 3)}
                supporting = normalize_route(str(item.get("supportingOf") or ""))
                if score >= float(policy["collisionThreshold"]) and supporting != old_route:
                    findings.append(Finding("error", "intent_collision", subject, f"{old_route} similarity={score:.3f}"))
                elif score < float(policy["collisionThreshold"]):
                    findings.append(Finding("warning", "intent_similarity_review", subject, f"{old_route} similarity={score:.3f}"))

        if status in READY_STATES:
            sources = item.get("sources") if isinstance(item.get("sources"), list) else []
            if len(sources) < int(policy["minimumSources"]): findings.append(Finding("error", "sources_too_few", subject, str(len(sources))))
            primary = 0; urls: set[str] = set()
            for n, source in enumerate(sources):
                sub = f"{subject}.sources[{n}]"
                if not isinstance(source, dict): findings.append(Finding("error", "source_invalid", sub, "nesne değil")); continue
                url = str(source.get("url", "")); parsed = urlparse(url); domain = (parsed.hostname or "").casefold()
                if parsed.scheme != "https" or not domain: findings.append(Finding("error", "source_url_invalid", sub, url))
                if domain in blocked_domains: findings.append(Finding("error", "source_domain_blocked", sub, domain))
                if url in urls: findings.append(Finding("error", "source_duplicate", sub, url))
                urls.add(url); source_class = str(source.get("class", ""))
                if source_class not in allowed: findings.append(Finding("error", "source_class_invalid", sub, source_class))
                if source.get("primary") is True and source_class in primary_classes: primary += 1
                age = age_days(str(source.get("verifiedAt", "")), today)
                if age is None or age < 0: findings.append(Finding("error", "source_verified_date_invalid", sub, str(source.get("verifiedAt"))))
                elif age > int(policy["maximumSourceAgeDays"]): findings.append(Finding("error", "source_stale", sub, f"{age} gün"))
                claims = source.get("claims")
                if not isinstance(claims, list) or not claims or any(not str(x).strip() for x in claims): findings.append(Finding("error", "source_claims_missing", sub, "kanıtlanan iddia yok"))
            if primary < int(policy["minimumPrimarySources"]): findings.append(Finding("error", "primary_sources_too_few", subject, str(primary)))
            links = item.get("internalLinks") if isinstance(item.get("internalLinks"), list) else []
            normalized_links = {normalize_route(str(x)) for x in links}
            if len(normalized_links) < int(policy["minimumInternalLinks"]): findings.append(Finding("error", "internal_links_too_few", subject, str(len(normalized_links))))
            missing = sorted(normalized_links - inventory_routes)
            if missing: findings.append(Finding("error", "internal_link_missing", subject, ", ".join(missing)))
            required_types = set(config["schemaPolicy"].get(str(item.get("contentType")), [])); supplied = set(map(str, item.get("schemaTypes", [])))
            if not required_types <= supplied: findings.append(Finding("error", "schema_types_missing", subject, ", ".join(sorted(required_types - supplied))))
            if supplied & forbidden: findings.append(Finding("error", "forbidden_schema_type", subject, ", ".join(sorted(supplied & forbidden))))
            if item.get("cluster") in config["commercialPolicy"]["forbiddenAffiliateOnClusters"] and item.get("conversion", {}).get("affiliateAllowed") is True:
                findings.append(Finding("error", "affiliate_forbidden_for_cluster", subject, str(item.get("cluster"))))
        if status in DRAFT_STATES:
            draft = item.get("draft")
            if not isinstance(draft, dict): findings.append(Finding("error", "draft_missing_for_state", subject, str(status)))
            elif collect_schema_types(draft.get("jsonLd")) & forbidden:
                findings.append(Finding("error", "forbidden_schema_in_draft", subject, ", ".join(sorted(collect_schema_types(draft.get("jsonLd")) & forbidden))))
        items.append(item)
    return findings, items


def validate_draft(path: Path, config: dict[str, Any], repo: Path, today: date) -> list[Finding]:
    draft = read_json(path); subject = str(draft.get("id") or path.name); out: list[Finding] = []
    required = {"id", "route", "title", "description", "h1", "directAnswer", "bodyHtml", "faqs", "jsonLd", "internalLinks", "sourceCitations", "cta", "analyticsEvents", "intentBoundary", "safetyBoundary", "verifiedAt"}
    missing = sorted(required - set(draft))
    if missing: return [Finding("error", "draft_required_fields_missing", subject, ", ".join(missing))]
    if not 70 <= len(str(draft["description"])) <= 190: out.append(Finding("error", "draft_description_length", subject, str(len(str(draft["description"])))))
    if len(str(draft["directAnswer"])) < 120: out.append(Finding("error", "draft_direct_answer_short", subject, str(len(str(draft["directAnswer"])))))
    body_length = len(strip_markup(str(draft["bodyHtml"])))
    if body_length < 700:
        out.append(Finding("error", "draft_body_short", subject, str(body_length)))
    if not isinstance(draft.get("faqs"), list) or len(draft["faqs"]) < 3: out.append(Finding("error", "draft_faq_low", subject, str(len(draft.get("faqs", [])))))
    blocked = collect_schema_types(draft.get("jsonLd")) & set(config["schemaPolicy"]["forbiddenTypes"])
    if blocked: out.append(Finding("error", "draft_forbidden_schema", subject, ", ".join(sorted(blocked))))
    inventory, inv_findings = build_inventory(repo); out.extend(x for x in inv_findings if x.level == "error")
    routes = {normalize_route(x.route) for x in inventory} | {normalize_route(x.canonical) for x in inventory}
    links = {normalize_route(str(x)) for x in draft.get("internalLinks", [])}
    if links - routes: out.append(Finding("error", "draft_internal_link_missing", subject, ", ".join(sorted(links - routes))))
    if len(links) < int(config["runPolicy"]["minimumInternalLinks"]): out.append(Finding("error", "draft_internal_links_low", subject, str(len(links))))
    age = age_days(str(draft.get("verifiedAt", "")), today)
    if age is None or age < 0 or age > int(config["runPolicy"]["maximumSourceAgeDays"]): out.append(Finding("error", "draft_verified_date_invalid", subject, str(draft.get("verifiedAt"))))
    text = " ".join(str(draft.get(k, "")) for k in ("title", "description", "directAnswer", "bodyHtml")).casefold()
    for claim in config["commercialPolicy"]["forbiddenClaims"]:
        if claim.casefold() in text: out.append(Finding("error", "draft_forbidden_claim", subject, claim))
    return out


def validate_receipt(path: Path, config: dict[str, Any]) -> list[Finding]:
    receipt = read_json(path); subject = str(receipt.get("contentId") or path.name); out: list[Finding] = []
    required = {"siteSlug", "sourceCommit", "contentId", "contentHash", "canonicalUrl", "deploymentUrl", "publishedAt", "liveVerified"}
    missing = sorted(required - set(receipt))
    if missing: return [Finding("error", "receipt_fields_missing", subject, ", ".join(missing))]
    if receipt["siteSlug"] != config["site"]["slug"]: out.append(Finding("error", "receipt_site_slug_mismatch", subject, str(receipt["siteSlug"])))
    if not re.fullmatch(r"[0-9a-f]{7,40}", str(receipt["sourceCommit"])): out.append(Finding("error", "receipt_commit_invalid", subject, str(receipt["sourceCommit"])))
    if not re.fullmatch(r"[0-9a-f]{64}", str(receipt["contentHash"])): out.append(Finding("error", "receipt_hash_invalid", subject, str(receipt["contentHash"])))
    if not str(receipt["canonicalUrl"]).startswith(config["site"]["canonicalOrigin"] + "/"): out.append(Finding("error", "receipt_canonical_invalid", subject, str(receipt["canonicalUrl"])))
    if receipt["liveVerified"] is not True: out.append(Finding("error", "receipt_live_not_verified", subject, "liveVerified true olmalı"))
    try: datetime.fromisoformat(str(receipt["publishedAt"]).replace("Z", "+00:00"))
    except ValueError: out.append(Finding("error", "receipt_published_at_invalid", subject, str(receipt["publishedAt"])))
    return out
