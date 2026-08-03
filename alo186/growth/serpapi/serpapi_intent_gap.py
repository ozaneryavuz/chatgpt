#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlparse
from urllib.request import Request, urlopen

ENDPOINT = "https://serpapi.com/search.json"
USER_AGENT = "ALO186-SerpIntentGap/1.0 (+https://alo186.com/yayin-ilkeleri/)"


class MonitorError(RuntimeError):
    pass


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def normalize_domain(url: str) -> str:
    try:
        host = urlparse(url).netloc.casefold().split(":", 1)[0]
    except ValueError:
        return ""
    return host[4:] if host.startswith("www.") else host


def is_own_domain(url: str, site_domain: str) -> bool:
    host = normalize_domain(url)
    site = site_domain.casefold().removeprefix("www.")
    return host == site or host.endswith("." + site)


def fetch_search(api_key: str, config: dict[str, Any], query: str, timeout: int) -> dict[str, Any]:
    params = {
        "engine": config.get("engine", "google"),
        "q": query,
        "api_key": api_key,
        "google_domain": config.get("googleDomain", "google.com.tr"),
        "location": config.get("location", "Istanbul, Turkey"),
        "gl": config.get("gl", "tr"),
        "hl": config.get("hl", "tr"),
        "device": config.get("device", "mobile"),
        "num": int(config.get("num", 10)),
        "output": "json",
        "no_cache": "false",
    }
    request = Request(ENDPOINT + "?" + urlencode(params), headers={"User-Agent": USER_AGENT})
    try:
        with urlopen(request, timeout=timeout) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")[:500]
        raise MonitorError(f"SerpApi HTTP {exc.code}: {body}") from exc
    except (URLError, TimeoutError) as exc:
        raise MonitorError(f"SerpApi bağlantı hatası: {exc}") from exc
    if payload.get("error"):
        raise MonitorError(str(payload["error"]))
    status = str(payload.get("search_metadata", {}).get("status") or "")
    if status and status.casefold() not in {"success", "cached"}:
        raise MonitorError(f"SerpApi arama durumu başarısız: {status}")
    return payload


def compact_result(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "position": item.get("position"),
        "title": item.get("title"),
        "link": item.get("link"),
        "domain": normalize_domain(str(item.get("link") or "")),
        "snippet": item.get("snippet"),
        "date": item.get("date"),
        "resultType": item.get("type"),
    }


def related_questions(payload: dict[str, Any]) -> list[str]:
    questions: list[str] = []
    for item in payload.get("related_questions") or []:
        value = str(item.get("question") or "").strip()
        if value and value not in questions:
            questions.append(value)
    return questions[:12]


def related_searches(payload: dict[str, Any]) -> list[str]:
    values: list[str] = []
    for item in payload.get("related_searches") or []:
        value = str(item.get("query") or item.get("text") or "").strip()
        if value and value not in values:
            values.append(value)
    return values[:12]


def analyze_query(spec: dict[str, Any], payload: dict[str, Any], site_domain: str) -> dict[str, Any]:
    organic = [compact_result(item) for item in (payload.get("organic_results") or [])]
    own = [item for item in organic if is_own_domain(str(item.get("link") or ""), site_domain)]
    own_position = min((int(item["position"]) for item in own if isinstance(item.get("position"), int)), default=None)
    competitors = [item for item in organic if item["domain"] and not is_own_domain(str(item.get("link") or ""), site_domain)]
    answer_box = payload.get("answer_box") or {}
    answer_source = normalize_domain(str(answer_box.get("link") or answer_box.get("displayed_link") or ""))
    gap_score = 0
    reasons: list[str] = []
    if own_position is None:
        gap_score += 50
        reasons.append("ALO186 ilk sayfada görünmüyor")
    elif own_position > 5:
        gap_score += 25
        reasons.append(f"ALO186 konumu {own_position}; ilk 5 dışında")
    if related_questions(payload):
        gap_score += 15
        reasons.append("People Also Ask soruları yeni alt başlık fırsatı veriyor")
    if related_searches(payload):
        gap_score += 10
        reasons.append("İlgili aramalar yeni iç bağlantı veya rota fırsatı veriyor")
    if answer_source and answer_source != site_domain:
        gap_score += 15
        reasons.append(f"Öne çıkan cevap başka kaynakta: {answer_source}")
    if spec.get("commercialMode") == "technical-gate":
        gap_score += 5
    return {
        "query": spec["query"],
        "intent": spec.get("intent"),
        "targetRoute": spec.get("targetRoute"),
        "commercialMode": spec.get("commercialMode"),
        "ownBestPosition": own_position,
        "ownResults": own,
        "topOrganic": organic[:10],
        "topCompetitors": competitors[:5],
        "answerBoxSource": answer_source or None,
        "relatedQuestions": related_questions(payload),
        "relatedSearches": related_searches(payload),
        "gapScore": min(gap_score, 100),
        "gapReasons": reasons,
        "searchId": payload.get("search_metadata", {}).get("id"),
        "searchStatus": payload.get("search_metadata", {}).get("status"),
    }


def action_candidates(results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    for item in sorted(results, key=lambda row: (-int(row["gapScore"]), str(row["query"]))):
        questions = item.get("relatedQuestions") or []
        searches = item.get("relatedSearches") or []
        if item["ownBestPosition"] is None:
            action = "Hedef rotayı kısa cevap, görünür güven sınırı ve sorguyla aynı H1/meta yapısıyla güçlendir"
        elif item["ownBestPosition"] > 5:
            action = "Mevcut rotayı PAA soruları, kanıt kaynakları ve bağlamsal iç bağlantılarla derinleştir"
        else:
            action = "Mevcut görünürlüğü koru; snippet ve tekrar ziyaret dönüşümünü iyileştir"
        candidates.append(
            {
                "priority": len(candidates) + 1,
                "query": item["query"],
                "targetRoute": item["targetRoute"],
                "gapScore": item["gapScore"],
                "recommendedAction": action,
                "questionIdeas": questions[:4],
                "relatedSearchIdeas": searches[:4],
                "commercialMode": item["commercialMode"],
                "guardrail": "Fiyat, stok, puan veya garanti üretme; resmî kurum izlenimi yaratma; mevcut çözüm yeterliyse satın almama sonucu göster.",
            }
        )
        if len(candidates) == 3:
            break
    return candidates


def markdown_report(report: dict[str, Any]) -> str:
    lines = [
        "# ALO186 SerpApi arama niyeti ve içerik boşluğu raporu",
        "",
        f"Üretim zamanı: `{report['generatedAt']}`  ",
        f"Konum/dil: `{report['searchContext']['location']}` · `{report['searchContext']['hl']}-{report['searchContext']['gl']}` · `{report['searchContext']['device']}`  ",
        f"Kullanılan sorgu: **{report['queryCount']}**",
        "",
        "## En yüksek potansiyelli üç aksiyon",
        "",
    ]
    for action in report["topActions"]:
        lines.extend(
            [
                f"### {action['priority']}. {action['query']}",
                f"- Hedef rota: `{action['targetRoute']}`",
                f"- Gap skoru: **{action['gapScore']}/100**",
                f"- Aksiyon: {action['recommendedAction']}",
                f"- Ticari mod: `{action['commercialMode']}`",
                f"- Güven sınırı: {action['guardrail']}",
            ]
        )
        if action["questionIdeas"]:
            lines.append("- PAA fikirleri: " + " | ".join(action["questionIdeas"]))
        if action["relatedSearchIdeas"]:
            lines.append("- İlgili aramalar: " + " | ".join(action["relatedSearchIdeas"]))
        lines.append("")
    lines.extend(["## Sorgu görünürlüğü", "", "| Sorgu | ALO186 konumu | Gap | Hedef |", "|---|---:|---:|---|"])
    for item in report["queries"]:
        position = item["ownBestPosition"] if item["ownBestPosition"] is not None else "İlk 10 yok"
        lines.append(f"| {item['query']} | {position} | {item['gapScore']} | `{item['targetRoute']}` |")
    lines.extend(
        [
            "",
            "## Yönetişim",
            "",
            "Bu rapor sıralama ve sorgu boşluklarını izler; otomatik ürün yayımlamaz. Affiliate bağlantıları yalnız teknik ihtiyaç doğrulandıktan ve ticari ilişki açıkça belirtildikten sonra kullanılabilir. ALO186 EDAŞ veya kamu kurumu değildir.",
            "",
        ]
    )
    return "\n".join(lines)


def run(config_path: Path, output_dir: Path, api_key: str, timeout: int, delay: float) -> dict[str, Any]:
    config = read_json(config_path)
    specs = config.get("queries") or []
    if not api_key:
        raise MonitorError("SERPAPI_API_KEY tanımlı değil")
    if not 1 <= len(specs) <= 8:
        raise MonitorError("Günlük bütçe koruması: sorgu sayısı 1–8 arasında olmalı")
    results: list[dict[str, Any]] = []
    errors: list[dict[str, str]] = []
    for index, spec in enumerate(specs):
        try:
            payload = fetch_search(api_key, config, str(spec["query"]), timeout)
            results.append(analyze_query(spec, payload, str(config["siteDomain"])))
        except MonitorError as exc:
            errors.append({"query": str(spec.get("query")), "error": str(exc)})
        if index < len(specs) - 1 and delay > 0:
            time.sleep(delay)
    if not results:
        raise MonitorError("Hiçbir SerpApi sorgusu başarıyla tamamlanmadı")
    domains = Counter()
    for result in results:
        domains.update(item["domain"] for item in result["topCompetitors"] if item["domain"])
    report = {
        "schemaVersion": 1,
        "generatedAt": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "siteDomain": config["siteDomain"],
        "queryCount": len(results),
        "configuredQueryCount": len(specs),
        "errors": errors,
        "searchContext": {
            "engine": config.get("engine"),
            "googleDomain": config.get("googleDomain"),
            "location": config.get("location"),
            "gl": config.get("gl"),
            "hl": config.get("hl"),
            "device": config.get("device"),
            "num": config.get("num"),
        },
        "topCompetitorDomains": [{"domain": domain, "appearances": count} for domain, count in domains.most_common(15)],
        "queries": results,
        "topActions": action_candidates(results),
        "guardrails": {
            "officialInstitutionImpression": False,
            "unverifiedPriceStockRatingWarranty": False,
            "affiliateDisclosureRequired": True,
            "noBuyOutcomeRequired": True,
        },
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    write_json(output_dir / "serpapi-growth-report.json", report)
    (output_dir / "serpapi-growth-report.md").write_text(markdown_report(report), encoding="utf-8")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="ALO186 için bütçe korumalı SerpApi arama niyeti ve içerik boşluğu radarı")
    parser.add_argument("--config", type=Path, default=Path(__file__).with_name("intent-watch.json"))
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--timeout", type=int, default=30)
    parser.add_argument("--delay", type=float, default=0.4)
    parser.add_argument("--api-key", default=os.environ.get("SERPAPI_API_KEY", ""))
    args = parser.parse_args()
    try:
        report = run(args.config, args.output, args.api_key, args.timeout, args.delay)
    except MonitorError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
    print(json.dumps({"ok": True, "queryCount": report["queryCount"], "topActions": report["topActions"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
