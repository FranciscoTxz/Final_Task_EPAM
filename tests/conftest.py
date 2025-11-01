import sys
import types
import os

# Forzar backend asyncio de anyio (evita intentar usar 'trio' si no está instalado)
os.environ.setdefault("ANYIO_BACKEND", "asyncio")

# Evitar la importación real de `app.database` durante la colección de pruebas
# (la aplicación crea un engine que requiere asyncpg). Insertamos un módulo
# falso en sys.modules antes de que los módulos de la app sean importados
# por los tests.
fake_db = types.ModuleType("app.database")


class _FakeBase:
    pass


fake_db.Base = _FakeBase
fake_db.AsyncSessionLocal = None
fake_db.engine = None
sys.modules["app.database"] = fake_db
