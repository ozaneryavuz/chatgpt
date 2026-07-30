from __future__ import annotations

import argparse
import json
from pathlib import Path

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


def number(value, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def audit(directory: Path) -> dict:
    failures: list[str] = []
    pages: list[dict] = []
    files = sorted(directory.glob("*.json"))
    if not files:
        raise SystemExit("Lighthouse JSON raporu bulunamadı")

    for path in files:
        payload = json.loads(path.read_text(encoding="utf-8"))
        mode = "desktop" if "desktop" in path.stem else "mobile"
        categories = payload.get("categories", {})
        audits = payload.get("audits", {})
        scores = {key: number(value.get("score")) for key, value in categories.items() if isinstance(value, dict)}
        metrics = {
            key: number(audits.get(key, {}).get("numericValue"))
            for key in ("largest-contentful-paint", "cumulative-layout-shift", "total-blocking-time", "first-contentful-paint", "speed-index")
        }
        page = {
            "report": path.name,
            "mode": mode,
            "requestedUrl": payload.get("requestedUrl"),
            "finalUrl": payload.get("finalUrl"),
            "scores": scores,
            "metrics": metrics,
        }
        pages.append(page)

        performance = scores.get("performance", 0)
        if performance < PERFORMANCE_MINIMUMS[mode]:
            failures.append(f"{path.name}: performance {performance:.2f} < {PERFORMANCE_MINIMUMS[mode]:.2f}")
        for category, minimum in CATEGORY_MINIMUMS.items():
            score = scores.get(category, 0)
            if score < minimum:
                failures.append(f"{path.name}: {category} {score:.2f} < {minimum:.2f}")
        for metric, maximum in METRIC_LIMITS[mode].items():
            measured = metrics[metric]
            if measured > maximum:
                unit = "" if metric == "cumulative-layout-shift" else " ms"
                failures.append(f"{path.name}: {metric} {measured:.2f}{unit} > {maximum}{unit}")

        final_url = str(payload.get("finalUrl") or "")
        if final_url and not (final_url.startswith("http://127.0.0.1:") or final_url.startswith("http://localhost:")):
            failures.append(f"{path.name}: beklenmeyen final URL {final_url}")

    summary = {
        "ok": not failures,
        "reportCount": len(files),
        "performanceMinimums": PERFORMANCE_MINIMUMS,
        "categoryMinimums": CATEGORY_MINIMUMS,
        "metricLimits": METRIC_LIMITS,
        "failureCount": len(failures),
        "failures": failures,
        "pages": pages,
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
