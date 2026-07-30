from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from statistics import median
from urllib.parse import urlsplit

CATEGORY_MINIMUMS = {
    "accessibility": 0.90,
    "best-practices": 0.85,
    "seo": 0.90,
}
PERFORMANCE_MINIMUMS = {"mobile": 0.75, "desktop": 0.85}
METRIC_LIMITS = {
    "mobile": {"largest-contentful-paint": 4000, "cumulative-layout-shift": 0.10, "total-blocking-time": 500},
    "desktop": {"largest-contentful-paint": 3500, "cumulative-layout-shift": 0.10, "total-blocking-time": 300},
}
METRIC_KEYS = (
    "largest-contentful-paint",
    "cumulative-layout-shift",
    "total-blocking-time",
    "first-contentful-paint",
    "speed-index",
)


def number(value, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def page_key(mode: str, requested_url: str, fallback: str) -> str:
    path = urlsplit(requested_url).path.rstrip("/") or "/"
    return f"{mode}:{path or fallback}"


def read_report(path: Path) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    mode = "desktop" if path.stem.startswith("desktop-") else "mobile"
    categories = payload.get("categories", {})
    audits = payload.get("audits", {})
    scores = {key: number(value.get("score")) for key, value in categories.items() if isinstance(value, dict)}
    metrics = {key: number(audits.get(key, {}).get("numericValue")) for key in METRIC_KEYS}
    return {
        "report": path.name,
        "mode": mode,
        "requestedUrl": str(payload.get("requestedUrl") or ""),
        "finalUrl": str(payload.get("finalUrl") or ""),
        "scores": scores,
        "metrics": metrics,
    }


def median_page(group: list[dict]) -> dict:
    first = group[0]
    score_keys = sorted({key for report in group for key in report["scores"]})
    scores = {key: median([report["scores"].get(key, 0.0) for report in group]) for key in score_keys}
    metrics = {key: median([report["metrics"][key] for report in group]) for key in METRIC_KEYS}
    return {
        "reports": [report["report"] for report in group],
        "runCount": len(group),
        "mode": first["mode"],
        "requestedUrl": first["requestedUrl"],
        "finalUrl": first["finalUrl"],
        "scores": scores,
        "metrics": metrics,
        "aggregation": "median" if len(group) > 1 else "single-run",
    }


def audit(directory: Path) -> dict:
    failures: list[str] = []
    files = sorted(directory.glob("*.json"))
    if not files:
        raise SystemExit("Lighthouse JSON raporu bulunamadı")

    raw_reports = [read_report(path) for path in files]
    grouped: dict[str, list[dict]] = defaultdict(list)
    for report in raw_reports:
        grouped[page_key(report["mode"], report["requestedUrl"], report["report"])].append(report)
        final_url = report["finalUrl"]
        if final_url and not (final_url.startswith("http://127.0.0.1:") or final_url.startswith("http://localhost:")):
            failures.append(f"{report['report']}: beklenmeyen final URL {final_url}")

    pages: list[dict] = []
    for key in sorted(grouped):
        page = median_page(grouped[key])
        pages.append(page)
        mode = page["mode"]
        label = ",".join(page["reports"])
        performance = page["scores"].get("performance", 0)
        if performance < PERFORMANCE_MINIMUMS[mode]:
            failures.append(f"{label}: median performance {performance:.2f} < {PERFORMANCE_MINIMUMS[mode]:.2f}")
        for category, minimum in CATEGORY_MINIMUMS.items():
            score = page["scores"].get(category, 0)
            if score < minimum:
                failures.append(f"{label}: median {category} {score:.2f} < {minimum:.2f}")
        for metric, maximum in METRIC_LIMITS[mode].items():
            measured = page["metrics"][metric]
            if measured > maximum:
                unit = "" if metric == "cumulative-layout-shift" else " ms"
                failures.append(f"{label}: median {metric} {measured:.2f}{unit} > {maximum}{unit}")

    summary = {
        "ok": not failures,
        "reportCount": len(files),
        "pageGroupCount": len(pages),
        "aggregation": "median-by-mode-and-requested-url",
        "performanceMinimums": PERFORMANCE_MINIMUMS,
        "categoryMinimums": CATEGORY_MINIMUMS,
        "metricLimits": METRIC_LIMITS,
        "failureCount": len(failures),
        "failures": failures,
        "pages": pages,
        "rawRuns": raw_reports,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if failures:
        raise SystemExit(1)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="ALO186 Lighthouse kategori ve Core Web Vitals bütçeleri")
    parser.add_argument("--directory", type=Path, required=True)
    args = parser.parse_args()
    audit(args.directory)


if __name__ == "__main__":
    main()
