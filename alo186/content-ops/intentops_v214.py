from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "content-ops" / "intent-opportunities-v214.json"


@dataclass(frozen=True)
class Finding:
    level: str
    code: str
    route: str
    detail: str


def weighted_score(item: dict, weights: dict[str, float]) -> float:
    scores = item.get("scores", {})
    return round(sum(float(scores.get(key, 0)) * weight for key, weight in weights.items()), 2)


def route_file(route: str) -> Path:
    clean = route.strip("/")
    return ROOT / clean / "index.html"


def extract_jsonld(text: str) -> list[dict]:
    blocks = re.findall(r'<script\b[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', text, re.I | re.S)
    values: list[dict] = []
    for block in blocks:
        try:
            payload = json.loads(block)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict):
            values.append(payload)
    return values


def schema_types(payloads: list[dict]) -> set[str]:
    result: set[str] = set()
    for payload in payloads:
        candidates = payload.get("@graph", []) if isinstance(payload.get("@graph"), list) else [payload]
        for candidate in candidates:
            if isinstance(candidate, dict):
                value = candidate.get("@type")
                if isinstance(value, str):
                    result.add(value)
                elif isinstance(value, list):
                    result.update(str(item) for item in value)
    return result


def visible_internal_links(text: str) -> set[str]:
    links: set[str] = set()
    for href in re.findall(r'<a\b[^>]*href=["\']([^"\']+)', text, re.I):
        if href.startswith("/") and not href.startswith("//"):
            links.add(href.split("#", 1)[0].split("?", 1)[0])
    return links


def external_domains(text: str) -> set[str]:
    domains: set[str] = set()
    for href in re.findall(r'<a\b[^>]*href=["\'](https?://[^"\']+)', text, re.I):
        domain = (urlparse(href).hostname or "").lower()
        if domain:
            domains.add(domain)
    return domains


def source_date(text: str) -> date | None:
    patterns = [
        r"Son kaynak doğrulama:\s*(\d{1,2})\s+([A-Za-zÇĞİÖŞÜçğıöşü]+)\s+(\d{4})",
        r"Son doğrulama:\s*(\d{1,2})\s+([A-Za-zÇĞİÖŞÜçğıöşü]+)\s+(\d{4})",
    ]
    months = {
        "ocak": 1, "şubat": 2, "mart": 3, "nisan": 4, "mayıs": 5, "haziran": 6,
        "temmuz": 7, "ağustos": 8, "eylül": 9, "ekim": 10, "kasım": 11, "aralık": 12,
    }
    for pattern in patterns:
        match = re.search(pattern, text, re.I)
        if match:
            month = months.get(match.group(2).casefold())
            if month:
                return date(int(match.group(3)), month, int(match.group(1)))
    for payload in extract_jsonld(text):
        candidates = payload.get("@graph", []) if isinstance(payload.get("@graph"), list) else [payload]
        for candidate in candidates:
            if isinstance(candidate, dict) and candidate.get("dateModified"):
                try:
                    return datetime.fromisoformat(str(candidate["dateModified"])).date()
                except ValueError:
                    pass
    return None


def event_contract(text: str, expected: list[str]) -> bool:
    return all(event in text for event in expected)


def audit_page(item: dict, guardrails: dict, today: date) -> list[Finding]:
    route = item["route"]
    path = route_file(route)
    findings: list[Finding] = []
    if not path.is_file():
        findings.append(Finding("error", "missing_route", route, str(path.relative_to(ROOT))))
        return findings

    text = path.read_text(encoding="utf-8", errors="strict")
    payloads = extract_jsonld(text)
    types = schema_types(payloads)
    internal = visible_internal_links(text)
    domains = external_domains(text)

    if guardrails["requireDirectAnswer"] and "Doğrudan cevap" not in text:
        findings.append(Finding("error", "direct_answer_missing", route, "Görünür doğrudan cevap bölümü yok"))
    if "FAQPage" not in types:
        findings.append(Finding("error", "faq_schema_missing", route, "FAQPage yok"))
    if "BreadcrumbList" not in types:
        findings.append(Finding("error", "breadcrumb_schema_missing", route, "BreadcrumbList yok"))
    visible_faq = len(re.findall(r"<details\b", text, re.I))
    if visible_faq < guardrails["minimumVisibleFaq"]:
        findings.append(Finding("warning", "visible_faq_low", route, f"{visible_faq} görünür SSS"))
    if len(internal) < guardrails["minimumInternalLinks"]:
        findings.append(Finding("error", "internal_links_low", route, f"{len(internal)} benzersiz iç bağlantı"))
    if len(domains) < guardrails["primarySourcesRequired"]:
        findings.append(Finding("warning", "source_domains_low", route, f"{len(domains)} dış kaynak alan adı"))
    verified = source_date(text)
    if not verified:
        findings.append(Finding("error", "source_date_missing", route, "Kaynak doğrulama tarihi yok"))
    elif (today - verified).days > guardrails["freshnessDays"]:
        findings.append(Finding("error", "sources_stale", route, f"Kaynak yaşı {(today - verified).days} gün"))
    if guardrails["requireSafetyBoundary"] and not re.search(r"güven|tehlike|köprülemeyin|müdahale etmeyin|risk", text, re.I):
        findings.append(Finding("error", "safety_boundary_missing", route, "Güvenlik sınırı bulunamadı"))
    if guardrails["requireConversionEvent"] and not event_contract(text, item.get("conversionEvents", [])):
        findings.append(Finding("error", "conversion_event_missing", route, ", ".join(item.get("conversionEvents", []))))
    if re.search(r'"@type"\s*:\s*"(?:Product|Offer|AggregateRating)"', text):
        findings.append(Finding("error", "commercial_schema_forbidden", route, "Product/Offer/AggregateRating bulundu"))
    return findings


def token_set(value: str) -> set[str]:
    return {token for token in re.findall(r"[a-z0-9çğıöşü]+", value.casefold()) if len(token) > 2}


def jaccard(a: str, b: str) -> float:
    left, right = token_set(a), token_set(b)
    if not left or not right:
        return 0.0
    return len(left & right) / len(left | right)


def audit_registry(data: dict) -> list[Finding]:
    findings: list[Finding] = []
    opportunities = data["opportunities"]
    weights = data["scoringModel"]
    guardrails = data["guardrails"]
    keys: set[str] = set()
    routes: set[str] = set()
    for item in opportunities:
        key, route = item["intentKey"], item["route"]
        if key in keys:
            findings.append(Finding("error", "duplicate_intent_key", route, key))
        if route in routes:
            findings.append(Finding("error", "duplicate_route", route, key))
        keys.add(key); routes.add(route)
        score = weighted_score(item, weights)
        item["weightedScore"] = score
        if item["status"] in {"candidate", "published"} and score < guardrails["minimumPublishScore"]:
            findings.append(Finding("warning", "score_below_threshold", route, str(score)))
    for index, left in enumerate(opportunities):
        for right in opportunities[index + 1:]:
            similarity = jaccard(left["task"], right["task"])
            if similarity > guardrails["maximumIntentSimilarity"]:
                findings.append(Finding("error", "intent_collision", left["route"], f"{right['route']} similarity={similarity:.2f}"))
    return findings


def run(today: date | None = None) -> dict:
    today = today or date.today()
    data = json.loads(REGISTRY.read_text(encoding="utf-8"))
    findings = audit_registry(data)
    for item in data["opportunities"]:
        if item["status"] == "published":
            findings.extend(audit_page(item, data["guardrails"], today))
    ranked = sorted(data["opportunities"], key=lambda item: (-item["weightedScore"], item["intentKey"]))
    report = {
        "ok": not any(f.level == "error" for f in findings),
        "version": data["version"],
        "generatedAt": today.isoformat(),
        "publishedAudited": sum(item["status"] == "published" for item in ranked),
        "candidateCount": sum(item["status"] == "candidate" for item in ranked),
        "rankedOpportunities": [{"intentKey": item["intentKey"], "route": item["route"], "status": item["status"], "score": item["weightedScore"]} for item in ranked],
        "findings": [f.__dict__ for f in findings],
    }
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="ALO186 IntentOps fırsat, çakışma, kaynak ve dönüşüm kalite motoru")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--today", type=date.fromisoformat)
    args = parser.parse_args()
    report = run(args.today)
    encoded = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded, encoding="utf-8")
    print(encoded, end="")
    raise SystemExit(0 if report["ok"] else 1)


if __name__ == "__main__":
    main()
