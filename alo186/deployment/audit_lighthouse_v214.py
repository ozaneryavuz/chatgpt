from __future__ import annotations

import argparse
import json
from pathlib import Path

VERSION = 214
THRESHOLDS = {
    "mobile": {
        "performance": 0.75,
        "accessibility": 0.90,
        "best-practices": 0.90,
        "seo": 0.90,
        "largest-contentful-paint": 4000.0,
        "cumulative-layout-shift": 0.10,
        "total-blocking-time": 500.0,
    },
    "desktop": {
        "performance": 0.85,
        "accessibility": 0.90,
        "best-practices": 0.90,
        "seo": 0.90,
        "largest-contentful-paint": 3000.0,
        "cumulative-layout-shift": 0.10,
        "total-blocking-time": 300.0,
    },
}


def parse_spec(value: str) -> tuple[str, Path]:
    if "=" not in value:
        raise argparse.ArgumentTypeError("Rapor biçimi name=path olmalı")
    name, path = value.split("=", 1)
    if not name.strip() or not path.strip():
        raise argparse.ArgumentTypeError("Rapor adı ve yolu boş olamaz")
    return name.strip(), Path(path.strip())


def mode_for(name: str, payload: dict) -> str:
    if name.casefold().startswith("desktop"):
        return "desktop"
    config = payload.get("configSettings") or {}
    form_factor = str(config.get("formFactor") or "").casefold()
    return "desktop" if form_factor == "desktop" else "mobile"


def audit_value(payload: dict, audit_id: str) -> float | None:
    audit = (payload.get("audits") or {}).get(audit_id) or {}
    value = audit.get("numericValue")
    return float(value) if isinstance(value, (int, float)) else None


def category_score(payload: dict, category: str) -> float | None:
    score = ((payload.get("categories") or {}).get(category) or {}).get("score")
    return float(score) if isinstance(score, (int, float)) else None


def inspect_report(name: str, path: Path) -> tuple[dict, list[str]]:
    if not path.is_file():
        return {"name": name, "path": str(path), "missing": True}, [f"Lighthouse raporu eksik: {name} → {path}"]
    payload = json.loads(path.read_text(encoding="utf-8"))
    mode = mode_for(name, payload)
    thresholds = THRESHOLDS[mode]
    scores = {category: category_score(payload, category) for category in ("performance", "accessibility", "best-practices", "seo")}
    metrics = {
        "largest-contentful-paint": audit_value(payload, "largest-contentful-paint"),
        "cumulative-layout-shift": audit_value(payload, "cumulative-layout-shift"),
        "total-blocking-time": audit_value(payload, "total-blocking-time"),
        "first-contentful-paint": audit_value(payload, "first-contentful-paint"),
        "speed-index": audit_value(payload, "speed-index"),
    }
    failures: list[str] = []
    for category, minimum in ((key, value) for key, value in thresholds.items() if key in scores):
        actual = scores.get(category)
        if actual is None or actual < minimum:
            failures.append(f"{name}: {category} {actual}; minimum {minimum}")
    for metric in ("largest-contentful-paint", "cumulative-layout-shift", "total-blocking-time"):
        actual = metrics.get(metric)
        maximum = thresholds[metric]
        if actual is None or actual > maximum:
            failures.append(f"{name}: {metric} {actual}; maximum {maximum}")
    runtime_error = payload.get("runtimeError")
    if isinstance(runtime_error, dict) and runtime_error.get("code"):
        failures.append(f"{name}: Lighthouse runtime error → {runtime_error}")
    return {
        "name": name,
        "path": str(path),
        "mode": mode,
        "requestedUrl": payload.get("requestedUrl"),
        "finalUrl": payload.get("finalUrl"),
        "lighthouseVersion": payload.get("lighthouseVersion"),
        "scores": scores,
        "metrics": metrics,
        "thresholds": thresholds,
        "passed": not failures,
    }, failures


def run(specs: list[tuple[str, Path]]) -> dict:
    reports: list[dict] = []
    failures: list[str] = []
    for name, path in specs:
        report, report_failures = inspect_report(name, path)
        reports.append(report)
        failures.extend(report_failures)
    modes = {report.get("mode") for report in reports}
    if "mobile" not in modes or "desktop" not in modes:
        failures.append("Lighthouse bütçesi hem mobil hem masaüstü raporu gerektirir")
    receipt = {
        "ok": not failures,
        "version": VERSION,
        "reports": reports,
        "labMetrics": ["LCP", "CLS", "TBT"],
        "fieldInpAvailable": False,
        "fieldCoreWebVitalsClaimed": False,
        "failures": failures,
    }
    if failures:
        raise RuntimeError("ALO186 Lighthouse v214 bütçesi başarısız:\n- " + "\n- ".join(failures))
    return receipt


def main() -> None:
    parser = argparse.ArgumentParser(description="ALO186 mobil ve masaüstü Lighthouse raporlarını performans, erişilebilirlik, SEO, LCP, CLS ve TBT bütçeleriyle doğrular.")
    parser.add_argument("--report", action="append", type=parse_spec, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()
    result = run(args.report)
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    args.receipt.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
