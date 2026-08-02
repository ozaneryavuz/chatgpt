#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path
from typing import Any

TOOL_DIR = Path(__file__).resolve().parent
if str(TOOL_DIR) not in sys.path:
    sys.path.insert(0, str(TOOL_DIR))

from core import DEFAULT_CONFIG, DEFAULT_QUEUE, Finding, read_json, write_json
from inventory import build_inventory
from planning import make_brief, make_report, make_sites_package, rank_ready, render_dashboard, render_sites_prompt
from validation import validate_draft, validate_queue, validate_receipt


def emit(value: Any) -> None:
    print(json.dumps(value, ensure_ascii=False, indent=2))


def resolve_today(raw: date | None) -> date:
    return raw or date.today()


def audit_state(args: argparse.Namespace) -> tuple[dict[str, Any], dict[str, Any], list[dict[str, Any]], list[Finding]]:
    repo = args.repo.resolve()
    config = read_json(args.config.resolve())
    queue = read_json(args.queue.resolve())
    inventory, inventory_findings = build_inventory(repo)
    findings, items = validate_queue(queue, config, inventory, inventory_findings, resolve_today(args.today))
    report = make_report(
        config=config,
        queue=queue,
        inventory_count=len(inventory),
        findings=findings,
        items=items,
        today=resolve_today(args.today),
    )
    return config, report, items, findings


def ensure_private_output(repo: Path, out_dir: Path) -> None:
    public_root = (repo / "alo186").resolve()
    target = out_dir.resolve()
    if target == public_root or public_root in target.parents:
        raise SystemExit("AI CMS artifactı public alo186/ ağacına yazılamaz")


def command_audit(args: argparse.Namespace) -> int:
    _, report, _, _ = audit_state(args)
    if args.output:
        write_json(args.output.resolve(), report)
    emit(report)
    return 0 if report["ok"] else 1


def command_plan(args: argparse.Namespace) -> int:
    config, report, items, findings = audit_state(args)
    out_dir = args.out_dir.resolve()
    ensure_private_output(args.repo.resolve(), out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    write_json(out_dir / "audit-report.json", report)

    if not report["ok"]:
        summary = {
            "ok": False,
            "cmsVersion": config["version"],
            "selectedCount": 0,
            "selected": [],
            "reason": "Fail-closed denetimde hata bulundu",
        }
        write_json(out_dir / "plan-summary.json", summary)
        emit(summary)
        return 1

    limit = min(int(args.limit), int(config["runPolicy"]["maximumSelections"]))
    selected = rank_ready(items, findings, config, limit)
    briefs = [make_brief(item, config, args.source_commit, resolve_today(args.today)) for item in selected]
    briefs_dir = out_dir / "briefs"
    briefs_dir.mkdir(parents=True, exist_ok=True)
    for brief in briefs:
        write_json(briefs_dir / f"{brief['contentId']}.json", brief)

    package = make_sites_package(briefs, config, args.source_commit)
    write_json(out_dir / "sites-package.json", package)
    (out_dir / "sites-publish-prompt.md").write_text(render_sites_prompt(package, briefs), encoding="utf-8")
    (out_dir / "dashboard.html").write_text(render_dashboard(report, selected, package), encoding="utf-8")

    summary = {
        "ok": True,
        "cmsVersion": config["version"],
        "generatedAt": resolve_today(args.today).isoformat(),
        "sourceCommit": args.source_commit,
        "selectedCount": len(selected),
        "selectionLimit": limit,
        "selected": [
            {
                "id": item["id"],
                "title": item["title"],
                "route": item["normalizedRoute"],
                "cluster": item["cluster"],
                "weightedScore": item["weightedScore"],
                "briefPath": f"briefs/{item['id']}.json",
            }
            for item in selected
        ],
        "sitesPackageHash": package["packageHash"],
        "automaticDeployAllowed": package["reviewPolicy"]["automaticDeployAllowed"],
    }
    write_json(out_dir / "plan-summary.json", summary)
    emit(summary)
    return 0


def validation_report(kind: str, path: Path, findings: list[Finding]) -> dict[str, Any]:
    errors = [finding for finding in findings if finding.level == "error"]
    return {
        "ok": not errors,
        "kind": kind,
        "path": str(path),
        "errorCount": len(errors),
        "warningCount": sum(finding.level == "warning" for finding in findings),
        "findings": [finding.__dict__ for finding in findings],
    }


def command_validate_draft(args: argparse.Namespace) -> int:
    config = read_json(args.config.resolve())
    findings = validate_draft(args.path.resolve(), config, args.repo.resolve(), resolve_today(args.today))
    report = validation_report("draft", args.path.resolve(), findings)
    if args.output:
        write_json(args.output.resolve(), report)
    emit(report)
    return 0 if report["ok"] else 1


def command_validate_receipt(args: argparse.Namespace) -> int:
    config = read_json(args.config.resolve())
    findings = validate_receipt(args.path.resolve(), config)
    report = validation_report("sites-receipt", args.path.resolve(), findings)
    if args.output:
        write_json(args.output.resolve(), report)
    emit(report)
    return 0 if report["ok"] else 1


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description="ALO186 AI CMS v220 — GitHub kaynaklı ChatGPT Sites yayın kontrol düzlemi")
    result.add_argument("--repo", type=Path, default=Path.cwd())
    result.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    result.add_argument("--queue", type=Path, default=DEFAULT_QUEUE)
    result.add_argument("--today", type=date.fromisoformat)
    commands = result.add_subparsers(dest="command", required=True)

    audit = commands.add_parser("audit", help="Rota, canonical, kuyruk, kaynak ve güven kapılarını denetle")
    audit.add_argument("--output", type=Path)
    audit.set_defaults(handler=command_audit)

    plan = commands.add_parser("plan", help="En yüksek potansiyelli en fazla üç brief ve Sites paketi üret")
    plan.add_argument("--out-dir", type=Path, required=True)
    plan.add_argument("--limit", type=int, choices=(1, 2, 3), default=3)
    plan.add_argument("--source-commit", default="working-tree")
    plan.set_defaults(handler=command_plan)

    draft = commands.add_parser("validate-draft", help="Üretilmiş içerik JSON'unu fail-closed doğrula")
    draft.add_argument("path", type=Path)
    draft.add_argument("--output", type=Path)
    draft.set_defaults(handler=command_validate_draft)

    receipt = commands.add_parser("validate-receipt", help="ChatGPT Sites yayın makbuzunu doğrula")
    receipt.add_argument("path", type=Path)
    receipt.add_argument("--output", type=Path)
    receipt.set_defaults(handler=command_validate_receipt)
    return result


def main() -> None:
    args = parser().parse_args()
    raise SystemExit(args.handler(args))


if __name__ == "__main__":
    main()
