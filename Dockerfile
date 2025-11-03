# Stage 1: builder to resolve dependencies
FROM python:3.12-slim AS builder

ENV POETRY_VERSION=2.2.1 \
    POETRY_HOME="/opt/poetry" \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    PIP_NO_CACHE_DIR=1 \
    PATH="/opt/poetry/bin:$PATH"

# System packages required to build native deps (adjust according to your project)
RUN apt-get update && apt-get install -y --no-install-recommends \
      curl build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

WORKDIR /app

# Copy only dependency files to cache installation
COPY pyproject.toml poetry.lock* /app/

# Install dependencies (without installing project package)
RUN poetry install --no-ansi --no-root

# Stage 2: minimal runtime
FROM python:3.12-slim AS runtime

ENV POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_CREATE=false \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PATH="/opt/poetry/bin:$PATH"\
    SECRET_KEY="AHAHalk@FHG@@hghg&1hgf21!"



# Minimal runtime system packages (adjust according to your libs)
RUN apt-get update && apt-get install -y --no-install-recommends \
      curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy binaries and site-packages from builder (installed system-wide)
COPY --from=builder /usr/local /usr/local

# Copy the app code
COPY . /app

# Install the project package (optional)
# You can omit this if you don't have a package in pyproject
RUN python -m pip install --no-cache-dir .

# Expose port
EXPOSE 8000

# Uvicorn in production; adjust workers according to CPU and add --reload only in dev
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
