from app.config import normalize_database_url


def test_render_postgres_url_uses_psycopg3_sqlalchemy_dialect():
    assert (
        normalize_database_url("postgresql://user:pass@host.internal/database")
        == "postgresql+psycopg://user:pass@host.internal/database"
    )
    assert (
        normalize_database_url("postgres://user:pass@host.internal/database")
        == "postgresql+psycopg://user:pass@host.internal/database"
    )


def test_existing_explicit_dialect_and_sqlite_are_unchanged():
    assert (
        normalize_database_url("postgresql+psycopg://user:pass@host/database")
        == "postgresql+psycopg://user:pass@host/database"
    )
    assert normalize_database_url("sqlite:///./test.db") == "sqlite:///./test.db"
