from __future__ import annotations

import os
import subprocess
from pathlib import Path

from sqlalchemy import create_engine, inspect


def test_alembic_baseline_upgrade_and_downgrade(tmp_path: Path):
    project_dir = Path(__file__).resolve().parents[1]
    database_path = tmp_path / "migration-smoke.db"
    database_url = f"sqlite:///{database_path}"
    env = os.environ.copy()
    env.update(
        {
            "ALO186_ENV": "test",
            "ALO186_DATABASE_URL": database_url,
            "ALO186_TOKEN_SECRET": "migration-test-secret-at-least-32-characters",
            "ALO186_AUTO_CREATE_SCHEMA": "false",
            "PYTHONPATH": str(project_dir),
        }
    )

    upgrade = subprocess.run(
        ["alembic", "-c", "alembic.ini", "upgrade", "head"],
        cwd=project_dir,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert upgrade.returncode == 0, upgrade.stdout + upgrade.stderr

    engine = create_engine(database_url)
    tables = set(inspect(engine).get_table_names())
    expected = {
        "alembic_version",
        "users",
        "organizations",
        "memberships",
        "locations",
        "critical_loads",
        "assets",
        "asset_tests",
        "incidents",
        "incident_tasks",
        "audit_logs",
    }
    assert expected.issubset(tables)

    downgrade = subprocess.run(
        ["alembic", "-c", "alembic.ini", "downgrade", "base"],
        cwd=project_dir,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert downgrade.returncode == 0, downgrade.stdout + downgrade.stderr
    remaining = set(inspect(engine).get_table_names())
    assert remaining <= {"alembic_version"}
