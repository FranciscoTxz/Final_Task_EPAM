import sys
import types
import os

# Force AnyIO to use asyncio backend (avoid trying to use 'trio' if not installed)
os.environ.setdefault("ANYIO_BACKEND", "asyncio")

# Prevent importing the real `app.database` during test collection
# (the app would create an engine that needs asyncpg). Insert a fake module
# into sys.modules before app modules are imported by the tests.
fake_db = types.ModuleType("app.database")


class _FakeBase:
    pass


fake_db.Base = _FakeBase
fake_db.AsyncSessionLocal = None
fake_db.engine = None
sys.modules["app.database"] = fake_db
