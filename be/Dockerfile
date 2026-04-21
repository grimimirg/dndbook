FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    curl \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

COPY pyproject.toml .

RUN python -m venv .venv && \
    .venv/bin/pip install --upgrade pip && \
    uv pip install --python .venv/bin/python .

ENV PATH="/app/.venv/bin:$PATH"
ENV VIRTUAL_ENV="/app/.venv"

COPY . .

RUN mkdir -p uploads && \
    chmod +x docker-entrypoint.sh init-db.sh

EXPOSE 5000

ENTRYPOINT ["./docker-entrypoint.sh"]
