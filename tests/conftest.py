import sys
import types
import os

os.environ.setdefault("ANYIO_BACKEND", "asyncio")

fake_db = types.ModuleType("app.database")


class _FakeBase:
    pass


fake_db.Base = _FakeBase
fake_db.AsyncSessionLocal = None
fake_db.engine = None
sys.modules["app.database"] = fake_db
