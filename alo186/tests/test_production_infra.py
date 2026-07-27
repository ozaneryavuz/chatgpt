from __future__ import annotations

import json
import os
import stat
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
BLUEPRINT = ROOT / "alo186/infrastructure/render/production.yaml"


def service(data: dict, name: str) -> dict:
    return next(item for item in data["services"] if item["name"] == name)


def env_map(item: dict) -> dict[str, dict]:
    return {row["key"]: row for row in item.get("envVars", [])}


def test_render_blueprint_contract() -> None:
    data = yaml.safe_load(BLUEPRINT.read_text(encoding="utf-8"))
    expected = {
        "alo186-continuity-api",
        "alo186-email-worker",
        "alo186-retention-cron",
        "alo186-r2-backup-cron",
        "alo186-grafana-alloy",
    }
    assert expected == {item["name"] for item in data["services"]}
    assert all(item.get("region") == "frankfurt" for item in data["services"])

    api = service(data, "alo186-continuity-api")
    assert api["type"] == "web"
    assert api["healthCheckPath"] == "/health/ready"
    assert api["preDeployCommand"] == "alembic upgrade head"
    assert api["autoDeployTrigger"] == "checksPass"
    assert "api.alo186.com" in api["domains"]
    api_env = env_map(api)
    assert api_env["ALO186_TOKEN_SECRET"].get("generateValue") is True
    assert api_env["ALO186_DATA_ENCRYPTION_KEY"].get("sync") is False
    assert api_env["ALO186_SMTP_PASSWORD"].get("sync") is False
    assert api_env["ALO186_SENTRY_DSN"].get("sync") is False
    assert "fromDatabase" in api_env["ALO186_DATABASE_URL"]

    backup = service(data, "alo186-r2-backup-cron")
    backup_env = env_map(backup)
    for key in (
        "ALO186_R2_ENDPOINT",
        "ALO186_R2_RESTIC_BUCKET",
        "AWS_ACCESS_KEY_ID",
        "AWS_SECRET_ACCESS_KEY",
        "RESTIC_PASSWORD",
        "ALO186_BACKUP_HEARTBEAT_URL",
    ):
        assert backup_env[key].get("sync") is False

    alloy = service(data, "alo186-grafana-alloy")
    alloy_env = env_map(alloy)
    assert "fromService" in alloy_env["ALO186_API_PRIVATE_HOSTPORT"]
    assert "fromService" in alloy_env["ALO186_METRICS_TOKEN"]
    assert alloy_env["GRAFANA_CLOUD_API_KEY"].get("sync") is False

    db = data["databases"][0]
    assert db["name"] == "alo186-prod-db"
    assert db["plan"] != "free"
    assert db["region"] == "frankfurt"
    assert db["postgresMajorVersion"] == "16"
    assert db["diskSizeGB"] >= 15
    assert db["storageAutoscalingEnabled"] is True
    assert db["ipAllowList"] == []


def test_database_url_normalization() -> None:
    sys.path.insert(0, str(ROOT / "alo186/sureklilik-api"))
    try:
        from app.config import normalize_database_url

        assert normalize_database_url("postgres://u:p@h/d") == "postgresql+psycopg://u:p@h/d"
        assert normalize_database_url("postgresql://u:p@h/d") == "postgresql+psycopg://u:p@h/d"
        assert (
            normalize_database_url("postgresql+psycopg://u:p@h/d")
            == "postgresql+psycopg://u:p@h/d"
        )
        assert normalize_database_url("sqlite:///x.db") == "sqlite:///x.db"
    finally:
        sys.path.pop(0)


def test_no_repository_secrets_and_backup_contract() -> None:
    inventory = yaml.safe_load(
        (ROOT / "alo186/infrastructure/secrets/secret-inventory.yaml").read_text(encoding="utf-8")
    )
    keys = {item["key"] for item in inventory["secrets"]}
    assert {"ALO186_TOKEN_SECRET", "RESTIC_PASSWORD", "CLOUDFLARE_API_TOKEN"} <= keys

    backup = (ROOT / "alo186/sureklilik-api/infra/backup/run_backup.sh").read_text(
        encoding="utf-8"
    )
    assert "pg_dump" in backup
    assert "sha256sum" in backup
    assert "restic backup" in backup
    assert "restic check" in backup
    assert "ALO186_R2_VAULT_BUCKET" in backup
    assert "/fail" in backup

    restore = (ROOT / "alo186/sureklilik-api/infra/backup/restore_verify.sh").read_text(
        encoding="utf-8"
    )
    assert "pg_restore --list" in restore
    assert "YES-RESTORE-ALO186" in restore


def test_secret_generator_permissions() -> None:
    script = ROOT / "alo186/infrastructure/secrets/generate_secrets.py"
    with tempfile.TemporaryDirectory() as directory:
        target = Path(directory) / "production.env"
        subprocess.run(
            [sys.executable, str(script), "--output", str(target)],
            check=True,
            capture_output=True,
            text=True,
        )
        mode = stat.S_IMODE(target.stat().st_mode)
        assert mode == 0o600
        content = target.read_text(encoding="utf-8")
        assert "ALO186_TOKEN_SECRET=" in content
        assert "ALO186_DATA_ENCRYPTION_KEY=" in content
        assert "RESTIC_PASSWORD=" in content
        assert len(content.split("ALO186_TOKEN_SECRET=", 1)[1].splitlines()[0]) >= 40


def test_dns_and_monitoring_are_safe_by_default() -> None:
    dns = (ROOT / "alo186/infrastructure/dns/sync_cloudflare_dns.py").read_text(
        encoding="utf-8"
    )
    assert "--apply" in dns
    assert "varsayılan dry-run" in dns
    assert "ALO186_CLOUDFLARE_PROXY" in dns
    assert "SPF" in dns and "otomatik değiştirilmedi" in dns

    workflow = (ROOT / ".github/workflows/alo186-production-synthetic.yml").read_text(
        encoding="utf-8"
    )
    assert "ALO186_PRODUCTION_MONITOR_ENABLED" in workflow
    assert "*/15 * * * *" in workflow
    assert "issues: write" in workflow

    alloy = (ROOT / "alo186/sureklilik-api/infra/monitoring/config.alloy").read_text(
        encoding="utf-8"
    )
    assert 'type        = "Bearer"' in alloy
    assert "GRAFANA_CLOUD_API_KEY" in alloy
    assert "insecure_skip_verify" not in alloy


def test_secret_inventory_is_metadata_only() -> None:
    inventory_path = ROOT / "alo186/infrastructure/secrets/secret-inventory.yaml"
    text = inventory_path.read_text(encoding="utf-8")
    forbidden = ("sk_live_", "AKIA", "BEGIN PRIVATE KEY", "postgresql://alo186:")
    assert not any(value in text for value in forbidden)


if __name__ == "__main__":
    import pytest

    raise SystemExit(pytest.main([__file__, "-q"]))
