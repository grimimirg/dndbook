FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    curl \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

COPY pyproject.toml .

# RUN python -m venv .venv && \
#     .venv/bin/pip install --upgrade pip && \
#     uv pip install --python .venv/bin/python .

RUN python -m venv .venv && \
    .venv/bin/pip install --upgrade pip && \
    .venv/bin/pip install "flask>=3.0.0" "flask-cors>=4.0.0" "flask-sqlalchemy>=3.1.0" "flask-socketio>=5.3.0" "python-socketio>=5.10.0" "sqlalchemy>=2.0.0" "psycopg2-binary>=2.9.0" "pyjwt>=2.8.0" "python-dotenv>=1.0.0" "werkzeug>=3.0.0" "alembic>=1.13.0" "eventlet>=0.33.0"

ENV PATH="/app/.venv/bin:$PATH"
ENV VIRTUAL_ENV="/app/.venv"

COPY . .

RUN mkdir -p uploads && \
    chmod +x docker-entrypoint.sh init-db.sh

EXPOSE 5000

ENTRYPOINT ["./docker-entrypoint.sh"]
