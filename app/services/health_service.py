from pathlib import Path

from alembic.config import Config
from alembic.script import ScriptDirectory
from sqlalchemy import text

from app.services.reminder_queue import _connect
from db.database import SessionLocal


ALEMBIC_CONFIG_PATH = Path(__file__).resolve().parents[2] / "alembic.ini"


async def check_database() -> bool:
    try:
        async with SessionLocal() as db:
            await db.execute(text("SELECT 1"))
            result = await db.execute(text("SELECT version_num FROM alembic_version"))
            versions = set(result.scalars())
        expected_heads = set(
            ScriptDirectory.from_config(Config(str(ALEMBIC_CONFIG_PATH))).get_heads()
        )
    except Exception:
        return False
    return bool(expected_heads) and versions == expected_heads


async def check_rabbitmq() -> bool:
    try:
        connection = await _connect()
        async with connection:
            return True
    except Exception:
        return False
