# Etapa 1: builder para resolver dependencias
FROM python:3.12-slim AS builder

ENV POETRY_VERSION=2.2.1 \
    POETRY_HOME="/opt/poetry" \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    PIP_NO_CACHE_DIR=1 \
    PATH="/opt/poetry/bin:$PATH"

# Paquetes del sistema necesarios para compilar deps nativas (ajusta según tu proyecto)
RUN apt-get update && apt-get install -y --no-install-recommends \
      curl build-essential \
    && rm -rf /var/lib/apt/lists/*

# Instalar Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

WORKDIR /app

# Copiar solo archivos de dependencias para cachear instalación
COPY pyproject.toml poetry.lock* /app/

# Instalar dependencias (sin el propio paquete del proyecto)
RUN poetry install --no-ansi --no-root

# Etapa 2: runtime minimal
FROM python:3.12-slim AS runtime

ENV POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_CREATE=false \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PATH="/opt/poetry/bin:$PATH"\
    SECRET_KEY="AHAHalk@FHG@@hghg&1hgf21!"



# Dependencias del sistema mínimas en runtime (ajusta según libs usadas)
RUN apt-get update && apt-get install -y --no-install-recommends \
      curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiar binarios y site-packages desde builder (instalados a nivel del sistema)
COPY --from=builder /usr/local /usr/local

# Copiar el código de la app
COPY . /app

# Instalar el paquete del proyecto (si quieres que sea importable como paquete)
# Puedes omitir si no tienes package en pyproject
RUN python -m pip install --no-cache-dir .

# Exponer puerto
EXPOSE 8000

# Uvicorn en producción; ajusta workers segun CPU y añade --reload solo en dev
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
