from __future__ import annotations

import argparse
import json
from pathlib import Path

import yaml


ALLOWED_TYPES = {"web", "worker", "cron", "pserv", "keyvalue"}
REQUIRED_PRODUCTION_ENV = {
    "ALO186_ENV": "production",
    "ALO186_AUTO_CREATE_SCHEMA": "false",
    "ALO186_EXPOSE_TEST_TOKENS": "false",
}
DATABASE_SERVICES = {
    "alo186-continuity-api",
    "alo186-email-worker",
    "alo186-retention-cron",
}


def env_map(service: dict) -> dict[str, dict]:
    return {
        item["key"]: item
        for item in service.get("envVars", [])
        if isinstance(item, dict) and item.get("key")
    }


def validate(path: Path) -> dict[str, object]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    failures: list[str] = []
    warnings: list[str] = []

    if not isinstance(data, dict):
        return {
            "ok": False,
            "failures": ["render.yaml kök nesnesi sözlük olmalıdır."],
            "warnings": [],
        }

    databases = data.get("databases") or []
    services = data.get("services") or []
    names: set[str] = set()

    for item in [*databases, *services]:
        name = item.get("name") if isinstance(item, dict) else None
        if not name:
            failures.append("Bütün database/service kayıtlarının adı olmalıdır.")
            continue
        if name in names:
            failures.append(f"Tekrarlanan service/database adı: {name}")
        names.add(name)

    database_names = {item.get("name") for item in databases if isinstance(item, dict)}
    if "alo186-postgres" not in database_names:
        failures.append("alo186-postgres database tanımı eksik.")

    service_by_name = {
        item.get("name"): item for item in services if isinstance(item, dict)
    }
    required_services = {
        "alo186-continuity-api": "web",
        "alo186-email-worker": "worker",
        "alo186-retention-cron": "cron",
        "alo186-r2-backup-cron": "cron",
        "alo186-grafana-alloy": "worker",
    }
    for name, expected_type in required_services.items():
        service = service_by_name.get(name)
        if not service:
            failures.append(f"Zorunlu Render servisi eksik: {name}")
            continue
        if service.get("type") != expected_type:
            failures.append(f"{name} type {expected_type} olmalı.")

    for service in services:
        name = service.get("name", "<adsız>")
        service_type = service.get("type")
        if service_type not in ALLOWED_TYPES:
            failures.append(f"{name}: bilinmeyen service type {service_type!r}")
        if service.get("region") != "frankfurt":
            failures.append(f"{name}: region frankfurt olmalı.")
        if service.get("runtime") == "docker":
            root_dir = service.get("rootDir")
            dockerfile_path = service.get("dockerfilePath")
            if not root_dir or not dockerfile_path:
                failures.append(f"{name}: Docker rootDir/dockerfilePath eksik.")
        if service_type == "cron" and not service.get("schedule"):
            failures.append(f"{name}: cron schedule eksik.")
        if service_type == "web" and not service.get("healthCheckPath"):
            failures.append(f"{name}: healthCheckPath eksik.")

        variables = env_map(service)
        if name in DATABASE_SERVICES:
            for key, value in REQUIRED_PRODUCTION_ENV.items():
                item = variables.get(key)
                if not item or str(item.get("value", "")).lower() != value:
                    failures.append(f"{name}: {key}={value} olmalı.")
            db = variables.get("ALO186_DATABASE_URL")
            if not db or db.get("fromDatabase", {}).get("name") != "alo186-postgres":
                failures.append(
                    f"{name}: ALO186_DATABASE_URL alo186-postgres'ten gelmeli."
                )

        for item in service.get("envVars", []):
            if not isinstance(item, dict) or not item.get("key"):
                failures.append(f"{name}: geçersiz envVars satırı.")
                continue
            modes = sum(
                bool(item.get(field))
                for field in (
                    "value",
                    "generateValue",
                    "sync",
                    "fromDatabase",
                    "fromService",
                )
            )
            if modes == 0:
                warnings.append(f"{name}: {item['key']} için değer kaynağı görünmüyor.")
            if (
                item.get("key", "").endswith(("SECRET", "PASSWORD", "DSN", "API_KEY"))
                and "value" in item
                and item["value"]
            ):
                warnings.append(
                    f"{name}: {item['key']} sabit value içeriyor; secret store tercih edilmeli."
                )

    api = service_by_name.get("alo186-continuity-api") or {}
    api_env = env_map(api)
    for key in (
        "ALO186_TOKEN_SECRET",
        "ALO186_DATA_ENCRYPTION_KEY",
        "ALO186_METRICS_TOKEN",
        "ALO186_SMTP_USERNAME",
        "ALO186_SMTP_PASSWORD",
    ):
        item = api_env.get(key)
        if not item:
            failures.append(f"API secret/env eksik: {key}")
        elif not (
            item.get("generateValue")
            or item.get("sync") is False
            or item.get("fromService")
        ):
            failures.append(f"API secret güvenli kaynakta değil: {key}")

    for key, expected in {
        "ALO186_KG_SEED_PUBLIC": "true",
        "ALO186_KG_SEED_STRICT": "false",
        "ALO186_KG_SEED_TIMEOUT": "30",
    }.items():
        item = api_env.get(key)
        if not item or str(item.get("value", "")).lower() != expected:
            failures.append(
                f"API Knowledge Graph ayarı eksik veya hatalı: {key}={expected}"
            )

    backup = service_by_name.get("alo186-r2-backup-cron") or {}
    backup_env = env_map(backup)
    for key in (
        "RESTIC_REPOSITORY",
        "RESTIC_PASSWORD",
        "AWS_ACCESS_KEY_ID",
        "AWS_SECRET_ACCESS_KEY",
        "ALO186_BACKUP_HEARTBEAT_URL",
    ):
        item = backup_env.get(key)
        if not item or item.get("sync") is not False:
            failures.append(
                f"Backup secret kullanıcı tarafından sync:false olarak girilmeli: {key}"
            )
    if (backup_env.get("ALO186_BACKUP_KEEP_YEARLY") or {}).get("value") != "3":
        failures.append("Backup yıllık retention 3 olmalı.")
    db = backup_env.get("ALO186_DATABASE_URL")
    if not db or db.get("fromDatabase", {}).get("name") != "alo186-postgres":
        failures.append("Backup ALO186_DATABASE_URL alo186-postgres'ten gelmeli.")

    alloy = service_by_name.get("alo186-grafana-alloy") or {}
    alloy_env = env_map(alloy)
    for key in (
        "GRAFANA_CLOUD_PROMETHEUS_URL",
        "GRAFANA_CLOUD_PROMETHEUS_USERNAME",
        "GRAFANA_CLOUD_API_KEY",
    ):
        item = alloy_env.get(key)
        if not item or item.get("sync") is not False:
            failures.append(f"Grafana Alloy secret/env sync:false olmalı: {key}")
    metrics_item = alloy_env.get("ALO186_METRICS_TOKEN")
    if (
        not metrics_item
        or metrics_item.get("fromService", {}).get("name")
        != "alo186-continuity-api"
    ):
        failures.append("Grafana Alloy metrics token API servisinden gelmeli.")

    retention = service_by_name.get("alo186-retention-cron") or {}
    retention_command = str(retention.get("dockerCommand", ""))
    if "app.worker retention-once" not in retention_command:
        failures.append("Retention cron retention-once çalıştırmalı.")
    if "app.knowledge_seed sync-public" not in retention_command:
        failures.append("Retention cron günlük Knowledge Graph sync çalıştırmalı.")

    if api.get("autoDeployTrigger") != "checksPass":
        warnings.append("API autoDeployTrigger checksPass değil.")
    if api.get("preDeployCommand") != "./scripts/render_predeploy.sh":
        failures.append("API preDeployCommand render_predeploy.sh olmalı.")

    return {
        "ok": not failures,
        "serviceCount": len(services),
        "databaseCount": len(databases),
        "failures": failures,
        "warnings": warnings,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="ALO186 Render Blueprint semantik kontrolü")
    parser.add_argument("path", nargs="?", default="render.yaml")
    args = parser.parse_args()
    result = validate(Path(args.path))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result["ok"] else 1)


if __name__ == "__main__":
    main()
