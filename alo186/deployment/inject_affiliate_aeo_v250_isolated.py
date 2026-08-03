from __future__ import annotations

"""Isolated artifact wrapper for affiliate AEO v250.

Some historical static-site transformations can materialise route aliases as
hard links or symbolic links inside the temporary Pages artifact. Writing a
route-specific AEO block through a shared inode can then leak that block into
another target page and produce duplicate deep-link identifiers.

This wrapper breaks link sharing for every v250 target before delegating to the
base injector, verifies that each route owns only its declared identifiers, and
stores an auditable isolation receipt in ``pages-release.json``. Ambiguous or
contaminated artifacts fail closed.
"""

import json
import os
import stat
from pathlib import Path

import inject_affiliate_aeo_v250 as base

VERSION = base.VERSION
TARGETS = base.TARGETS


def _atomic_write_text(path: Path, text: str) -> None:
    """Replace *path* atomically so shared inodes and symlinks are detached."""
    path.parent.mkdir(parents=True, exist_ok=True)
    original_mode = None
    try:
        original_mode = stat.S_IMODE(path.stat().st_mode)
    except FileNotFoundError:
        pass

    temporary = path.with_name(
        f".{path.name}.affiliate-aeo-v250-{os.getpid()}-{id(path)}.tmp"
    )
    try:
        temporary.write_text(text, encoding="utf-8")
        if original_mode is not None:
            temporary.chmod(original_mode)
        temporary.replace(path)
    finally:
        try:
            temporary.unlink()
        except FileNotFoundError:
            pass


def _declared_ids(target: base.TargetSpec) -> set[str]:
    values = {target.scenario_id}
    values.update(item.deep_id for item in target.recommendations)
    values.update(item[0] for item in target.faq_items)
    return values


def _detach_target_files(site: Path) -> dict[str, object]:
    records: list[dict[str, object]] = []
    inode_groups_before: dict[tuple[int, int], list[str]] = {}

    snapshots: dict[str, str] = {}
    for target in TARGETS:
        path = site / target.file
        if not path.is_file():
            raise FileNotFoundError(f"AEO v250 hedef sayfası eksik: {path}")
        snapshots[target.key] = path.read_text(encoding="utf-8", errors="strict")
        details = path.stat()
        inode_groups_before.setdefault((details.st_dev, details.st_ino), []).append(
            target.key
        )
        records.append(
            {
                "target": target.key,
                "path": target.file.as_posix(),
                "wasSymlink": path.is_symlink(),
                "linksBefore": details.st_nlink,
                "deviceBefore": details.st_dev,
                "inodeBefore": details.st_ino,
            }
        )

    # Write from the complete pre-mutation snapshot. This prevents a write to
    # one shared inode from changing the source text that a later target reads.
    for target in TARGETS:
        _atomic_write_text(site / target.file, snapshots[target.key])

    seen_after: dict[tuple[int, int], str] = {}
    for record, target in zip(records, TARGETS):
        path = site / target.file
        details = path.stat()
        inode_key = (details.st_dev, details.st_ino)
        if inode_key in seen_after:
            raise RuntimeError(
                "AEO v250 hedef izolasyonu başarısız: "
                f"{target.key} ile {seen_after[inode_key]} aynı inode'u kullanıyor"
            )
        seen_after[inode_key] = target.key
        record.update(
            {
                "linksAfter": details.st_nlink,
                "deviceAfter": details.st_dev,
                "inodeAfter": details.st_ino,
                "detached": (
                    record["wasSymlink"]
                    or record["linksBefore"] > 1
                    or record["inodeBefore"] != details.st_ino
                    or record["deviceBefore"] != details.st_dev
                ),
            }
        )

    shared_groups = [
        sorted(values)
        for values in inode_groups_before.values()
        if len(values) > 1
    ]
    return {
        "policy": "atomic-target-replacement-before-route-specific-injection",
        "targetCount": len(TARGETS),
        "sharedInodeGroupsBefore": shared_groups,
        "sharedInodeGroupCountBefore": len(shared_groups),
        "records": records,
    }


def _validate_target_isolation(site: Path) -> dict[str, object]:
    ownership = {target.key: _declared_ids(target) for target in TARGETS}
    all_declared = set().union(*ownership.values())
    errors: list[str] = []
    reports: list[dict[str, object]] = []

    for target in TARGETS:
        path = site / target.file
        html = path.read_text(encoding="utf-8", errors="strict")
        ids = [base.unescape(match.group(2)).strip() for match in base.ID_RE.finditer(html)]
        own = ownership[target.key]
        missing = sorted(value for value in own if ids.count(value) == 0)
        duplicate = sorted(value for value in own if ids.count(value) != 1)
        foreign = sorted((set(ids) & all_declared) - own)
        marker_count = html.count(base.MARKER)
        schema_marker_count = html.count(base.SCHEMA_MARKER)
        style_marker_count = html.count(base.STYLE_MARKER)

        if missing:
            errors.append(
                f"{target.key}: kendi deep-link kimlikleri eksik: {', '.join(missing)}"
            )
        if duplicate:
            errors.append(
                f"{target.key}: kendi deep-link kimlikleri tekil değil: {', '.join(duplicate)}"
            )
        if foreign:
            errors.append(
                f"{target.key}: başka hedefe ait deep-link kimlikleri bulundu: {', '.join(foreign)}"
            )
        if marker_count != 1 or schema_marker_count != 1 or style_marker_count != 1:
            errors.append(
                f"{target.key}: marker sayıları geçersiz "
                f"(visible={marker_count}, schema={schema_marker_count}, style={style_marker_count})"
            )

        reports.append(
            {
                "target": target.key,
                "declaredIdCount": len(own),
                "missingIds": missing,
                "duplicateIds": duplicate,
                "foreignIds": foreign,
                "markerCount": marker_count,
                "schemaMarkerCount": schema_marker_count,
                "styleMarkerCount": style_marker_count,
            }
        )

    if errors:
        raise RuntimeError("AEO v250 hedef izolasyonu ihlali: " + "; ".join(errors))

    return {
        "ok": True,
        "targetCount": len(TARGETS),
        "declaredIdCount": len(all_declared),
        "targets": reports,
    }


def _write_release_receipt(
    site: Path,
    detach_receipt: dict[str, object],
    isolation_receipt: dict[str, object],
) -> None:
    path = site / "pages-release.json"
    if not path.is_file():
        return
    payload = json.loads(path.read_text(encoding="utf-8"))
    current = payload.get("affiliateAeoV250")
    if not isinstance(current, dict):
        raise RuntimeError("pages-release.json affiliateAeoV250 makbuzu eksik")
    current["targetFileIsolation"] = {
        "detach": detach_receipt,
        "validation": isolation_receipt,
    }
    payload["affiliateAeoV250"] = current
    _atomic_write_text(
        path,
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
    )


def inject(site: Path, base_path: str = "") -> dict[str, object]:
    resolved = site.resolve()
    detach_receipt = _detach_target_files(resolved)
    result = base.inject(resolved, base_path)
    isolation_receipt = _validate_target_isolation(resolved)
    _write_release_receipt(resolved, detach_receipt, isolation_receipt)
    base._refresh_checksums(resolved)
    result["targetFileIsolation"] = {
        "detach": detach_receipt,
        "validation": isolation_receipt,
    }
    return result


def main() -> None:
    parser = base.argparse.ArgumentParser(
        description="ALO186 affiliate AEO v250 isolated artifact wrapper"
    )
    parser.add_argument("--site", type=Path, required=True)
    parser.add_argument("--base-path", default="")
    args = parser.parse_args()
    print(json.dumps(inject(args.site, args.base_path), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
