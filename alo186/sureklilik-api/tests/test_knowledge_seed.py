from __future__ import annotations

from urllib.error import URLError

import pytest
from sqlalchemy import func, select

from app import knowledge_seed
from app.db import SessionLocal
from app.kg_models import KnowledgeAssertion, KnowledgeEntity, KnowledgeSource, KnowledgeVerificationRun


def full_dataset():
    provinces = [
        {"id": province_id, "name": "İstanbul" if province_id == 34 else f"İl {province_id}"}
        for province_id in range(1, 82)
    ]
    districts = [
        {"id": 1, "name": "Ümraniye", "provinceId": 34},
        {"id": 2, "name": "Esenyurt", "provinceId": 34},
    ]
    next_id = 3
    province_id = 1
    while len(districts) < 973:
        if province_id == 34:
            province_id = 35
        districts.append(
            {
                "id": next_id,
                "name": f"İlçe {next_id}",
                "provinceId": province_id,
            }
        )
        next_id += 1
        province_id = province_id + 1 if province_id < 81 else 1
    return provinces, districts


def test_public_seed_is_idempotent_and_covers_full_catalog(monkeypatch):
    provinces, districts = full_dataset()

    def fake_fetch(url: str, timeout: int):
        assert timeout == 15
        if "provinces" in url:
            return provinces, "a" * 64, 10
        return districts, "b" * 64, 20

    monkeypatch.setattr(knowledge_seed, "_fetch_json", fake_fetch)
    first = knowledge_seed.sync_public_graph(timeout=15, strict=True)
    second = knowledge_seed.sync_public_graph(timeout=15, strict=True)

    assert first["provinces"] == 81
    assert first["districts"] == 973
    assert first["remote_error"] is None
    assert first["entities_created"] > 1_000
    assert first["assertions_created"] > 1_000
    assert second["entities_created"] == 0
    assert second["assertions_created"] == 0
    assert second["entities_updated"] > 1_000
    assert second["assertions_updated"] > 1_000

    with SessionLocal() as db:
        assert db.scalar(select(func.count()).select_from(KnowledgeEntity).where(KnowledgeEntity.kind == "Province")) >= 81
        assert db.scalar(select(func.count()).select_from(KnowledgeEntity).where(KnowledgeEntity.kind == "District")) >= 973
        assert db.scalar(select(func.count()).select_from(KnowledgeEntity).where(KnowledgeEntity.kind == "DistributionCompany")) >= 21
        assert db.scalar(select(func.count()).select_from(KnowledgeEntity).where(KnowledgeEntity.kind == "Problem")) >= 25
        assert db.scalar(select(func.count()).select_from(KnowledgeEntity).where(KnowledgeEntity.kind == "ProductCategory")) >= 7
        assert db.scalar(select(func.count()).select_from(KnowledgeEntity).where(KnowledgeEntity.kind == "Product")) >= 7
        assert db.scalar(select(func.count()).select_from(KnowledgeSource).where(KnowledgeSource.scope_key == "global")) >= 5
        assert db.scalar(select(func.count()).select_from(KnowledgeAssertion).where(KnowledgeAssertion.scope_key == "global")) > 1_000
        assert db.scalar(select(func.count()).select_from(KnowledgeVerificationRun).where(KnowledgeVerificationRun.status == "verified")) >= 2

        umraniye = db.scalar(select(KnowledgeEntity).where(KnowledgeEntity.canonical_key == "district:1"))
        esenyurt = db.scalar(select(KnowledgeEntity).where(KnowledgeEntity.canonical_key == "district:2"))
        ayedas = db.scalar(select(KnowledgeEntity).where(KnowledgeEntity.canonical_key == "distribution-company:ayedas"))
        bedas = db.scalar(select(KnowledgeEntity).where(KnowledgeEntity.canonical_key == "distribution-company:bedas"))
        assert umraniye and esenyurt and ayedas and bedas
        assert db.scalar(
            select(KnowledgeAssertion).where(
                KnowledgeAssertion.subject_entity_id == umraniye.id,
                KnowledgeAssertion.predicate == "servedBy",
                KnowledgeAssertion.object_entity_id == ayedas.id,
            )
        )
        assert db.scalar(
            select(KnowledgeAssertion).where(
                KnowledgeAssertion.subject_entity_id == esenyurt.id,
                KnowledgeAssertion.predicate == "servedBy",
                KnowledgeAssertion.object_entity_id == bedas.id,
            )
        )


def test_seed_non_strict_keeps_static_graph_when_remote_dataset_is_unreachable(monkeypatch):
    def failing_fetch(_url: str, _timeout: int):
        raise URLError("dataset unavailable")

    monkeypatch.setattr(knowledge_seed, "_fetch_json", failing_fetch)
    result = knowledge_seed.sync_public_graph(timeout=10, strict=False)
    assert "dataset unavailable" in result["remote_error"]
    assert result["provinces"] == 0
    assert result["districts"] == 0

    with SessionLocal() as db:
        source = db.scalar(
            select(KnowledgeSource).where(KnowledgeSource.canonical_key == "source:turkiyeapi:2025")
        )
        assert source is not None
        assert source.status == "unreachable"
        assert db.scalar(
            select(func.count()).select_from(KnowledgeEntity).where(KnowledgeEntity.kind == "DistributionCompany")
        ) >= 21
        assert db.scalar(
            select(func.count()).select_from(KnowledgeEntity).where(KnowledgeEntity.kind == "Problem")
        ) >= 25
        assert db.scalar(
            select(func.count()).select_from(KnowledgeVerificationRun).where(
                KnowledgeVerificationRun.source_id == source.id,
                KnowledgeVerificationRun.status == "unreachable",
            )
        ) >= 1


def test_seed_strict_fails_when_dataset_coverage_is_incomplete(monkeypatch):
    def short_fetch(url: str, _timeout: int):
        if "provinces" in url:
            return [{"id": 1, "name": "Adana"}], "c" * 64, 1
        return [{"id": 1, "name": "Seyhan", "provinceId": 1}], "d" * 64, 1

    monkeypatch.setattr(knowledge_seed, "_fetch_json", short_fetch)
    with pytest.raises(RuntimeError, match="81 il"):
        knowledge_seed.sync_public_graph(timeout=10, strict=True)


def test_seed_cli_outputs_json(monkeypatch, capsys):
    provinces, districts = full_dataset()

    def fake_fetch(url: str, _timeout: int):
        return (provinces, "e" * 64, 2) if "provinces" in url else (districts, "f" * 64, 3)

    monkeypatch.setattr(knowledge_seed, "_fetch_json", fake_fetch)
    assert knowledge_seed.main(["sync-public", "--timeout", "10", "--strict"]) == 0
    output = capsys.readouterr().out
    assert '"provinces": 81' in output
    assert '"districts": 973' in output
    assert '"health"' in output
