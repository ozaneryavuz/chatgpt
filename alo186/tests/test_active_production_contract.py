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
    deadline_guard = read("alo186/tests/device_damage_deadline_guard.py")

    # The production workflow must use the Python builder and the active Apache file.
    assert "python alo186/deployment/build_static_site.py" in workflow
    assert "apache-production.htaccess" in builder
    assert "build_static_site.sh" not in workflow

    # A controlled hotfix merge or explicit manual dispatch can request deploy even if
    # the repository-wide deploy variable is intentionally disabled. A request must not
    # run a transfer with an undefined method: it becomes an explicit blocked state and
    # updates the P0 hosting issue instead of producing an opaque scheduled-task error.
    assert "[deploy alo186]" in workflow
    assert "force_deploy" in workflow
    assert "environment:" in workflow and "alo186-production" in workflow
    assert "mirror --reverse --overwrite" in workflow
    assert "deploy-config-blocked:" in workflow
    assert "Deploy yapılandırması eksik — yayın yapılmadı" in workflow
    assert "vars.ALO186_DEPLOY_METHOD == 'ssh'" in workflow
    assert "vars.ALO186_DEPLOY_METHOD == 'ftps'" in workflow
    assert "alo186-production-deploy-blocked" in workflow
    assert "alo186-production-deploy-failure" in workflow
    assert "issues: write" in workflow
    assert "Manuel zorunlu deploy isteğini başarısız say" in workflow
    assert "Deploy yöntemi doğrulaması" not in workflow

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

    # Binding Kalite Yönetmeliği Madde 26/1 uses a 30-day application period.
    # The response layer must not rewrite visible HTML or JSON-LD; builder and
    # smoke guards validate the canonical artifact and live pages instead.
    assert "Cihaz hasarı başvuru süresi HTML yanıt katmanında değiştirilmez" in apache
    assert "AddOutputFilterByType SUBSTITUTE text/html application/xhtml+xml" not in apache
    assert "<IfModule mod_substitute.c>" not in apache
    assert "Substitute \"s|" not in apache
    assert "deviceDamageDeadline\": CURRENT_DEADLINE" in builder
    assert "30 gün" in deadline_guard
    assert "stale_damage_application_contexts" in static_smoke
    assert "stale_deadline_contexts" in live_smoke
    assert "CURRENT_DEADLINE" in live_smoke
    assert "30 gün" in live_smoke

    # The active builder must include root operational files. Otherwise 404 and the
    # Tailwind compatibility response silently disappear from the real artifact.
    for token in ("404.html", "tailwindcss", "ROOT_STATIC_FILES", "normalize_canonical_host"):
        assert token in builder, f"Builder production asset/normalization missing: {token}"
    for token in ("404.html", "tailwindcss", "REQUIRED_ROOT_FILES"):
        assert token in static_smoke, f"Static smoke root-file check missing: {token}"

    # Public web root must not expose test files, README/internal notes, source maps,
    # package metadata, Python/shell scripts or deployment/infra trees.
    for token in (
        "FORBIDDEN_PUBLIC_DIRECTORIES",
        "FORBIDDEN_PUBLIC_FILE_PATTERNS",
        "public_copy_ignore",
        "find_forbidden_public_files",
        "publicArtifactPolicy",
    ):
        assert token in builder, f"Builder public-artifact hygiene missing: {token}"
    for token in (
        "FORBIDDEN_PUBLIC_DIRECTORIES",
        "FORBIDDEN_PUBLIC_FILE_PATTERNS",
        "is_forbidden_public_file",
        "forbiddenPublicFileCount",
        "sourceDocsExcluded",
        "testsExcluded",
        "packageMetadataExcluded",
    ):
        assert token in static_smoke, f"Static smoke public-artifact hygiene missing: {token}"

    # Canonical host policy is apex everywhere and live smoke verifies www redirect.
    assert "https://alo186.com" in apache
    assert "https://alo186.com" in builder
    assert "www-redirect" in live_smoke
    assert "https://www.alo186.com" in builder

    print(
        "PASS: active ALO186 production builder, 30-day legal deadline, public artifact "
        "hygiene, Apache config, deploy gates and smoke tests are aligned."
    )


if __name__ == "__main__":
    main()
