#!/usr/bin/env python3
"""Regression contract for the production files that the deploy workflow actually uses."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def read(relative: str) -> str:
    path = ROOT / relative
    assert path.is_file(), f"Production contract file missing: {relative}"
    return path.read_text(encoding="utf-8")


def main() -> None:
    workflow = read(".github/workflows/alo186-production-deploy.yml")
    builder = read("alo186/deployment/build_static_site.py")
    apache = read("alo186/deployment/apache-production.htaccess")
    static_smoke = read("alo186/deployment/smoke_static_site.py")
    live_smoke = read("alo186/deployment/smoke_live_routes.py")

    # The production workflow must use the Python builder and the active Apache file.
    assert "python alo186/deployment/build_static_site.py" in workflow
    assert "apache-production.htaccess" in builder
    assert "build_static_site.sh" not in workflow

    # A controlled hotfix merge or explicit manual dispatch can run deploy even if the
    # repository-wide deploy variable is intentionally disabled.
    assert "[deploy alo186]" in workflow
    assert "force_deploy" in workflow
    assert "environment:" in workflow and "alo186-production" in workflow
    assert "mirror --reverse --overwrite" in workflow

    # The build must fail closed on the legal deadline, active production contract,
    # Python syntax and canonical bundle.
    assert "device_damage_deadline_guard.py" in workflow
    assert "test_active_production_contract.py" in workflow
    assert "smoke_static_site.py" in workflow
    assert "smoke_live_routes.py" in workflow

    required_headers = (
        "Strict-Transport-Security",
        "X-Content-Type-Options",
        "Content-Security-Policy",
        "Referrer-Policy",
        "Permissions-Policy",
    )
    for header in required_headers:
        assert header in apache, f"Active Apache production header missing: {header}"
        assert header in builder, f"Builder header validation missing: {header}"
        assert header.lower() in live_smoke, f"Live smoke header validation missing: {header}"

    # The live root still comes from an older/external template. The active Apache
    # output filter protects visible HTML and embedded JSON-LD until that source is
    # replaced, while source/artifact guards prevent new regressions.
    assert "AddOutputFilterByType SUBSTITUTE text/html application/xhtml+xml" in apache
    assert "zararın ortaya çıktığı tarihten itibaren 30 gün içinde" in apache
    assert "zararın ortaya çıktığı tarihten itibaren 10 iş günü içinde" in apache
    assert "30 gün içinde EDAŞ kaydı açın" in apache
    assert "10 iş günü içinde ilgili dağıtım şirketinin resmî kanalına başvurun" in apache
    assert "wrong_damage_deadline_contexts" in static_smoke
    assert "wrong_deadline_contexts" in live_smoke
    assert "10 iş günü" in live_smoke

    # The active builder must include the root operational files that the old shell
    # builder already carried, otherwise 404 and the Tailwind compatibility response
    # silently disappear from the real artifact.
    for token in ("404.html", "tailwindcss", "ROOT_STATIC_FILES", "normalize_canonical_host"):
        assert token in builder, f"Builder production asset/normalization missing: {token}"
    for token in ("404.html", "tailwindcss", "REQUIRED_ROOT_FILES"):
        assert token in static_smoke, f"Static smoke root-file check missing: {token}"

    # Canonical host policy is www everywhere and live smoke verifies apex redirect.
    assert "https://www.alo186.com" in apache
    assert "https://www.alo186.com" in builder
    assert "apex-redirect" in live_smoke
    assert "https://alo186.com" in builder

    print("PASS: active ALO186 production builder, Apache config, deploy gate and smoke tests are aligned.")


if __name__ == "__main__":
    main()
