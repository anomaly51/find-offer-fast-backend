import pytest

from app.core.config import cors_allow_credentials, cors_origins, validate_production_config


def test_development_cors_supports_local_frontend_credentials(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "development")
    monkeypatch.delenv("CORS_ORIGINS", raising=False)

    assert "http://localhost:5173" in cors_origins()
    assert "http://127.0.0.1:5173" in cors_origins()
    assert cors_allow_credentials() is True


def test_validate_production_config_rejects_wildcard_cors(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.setenv("SECRET_KEY", "test-secret")
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://user:pass@db/app")
    monkeypatch.setenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq/")
    monkeypatch.setenv("CORS_ORIGINS", "*")
    monkeypatch.setenv("COOKIE_SECURE", "true")

    with pytest.raises(RuntimeError, match="CORS_ORIGINS cannot contain"):
        validate_production_config()
