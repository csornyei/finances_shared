FROM python:3.13-alpine AS builder

RUN apk add --no-cache git

COPY --from=ghcr.io/astral-sh/uv:0.8.0 /uv /uvx /bin/

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN touch README.md

RUN uv sync --no-dev --locked --no-install-project

FROM python:3.13-alpine AS runtime

ENV VIRTUAL_ENV=/app/.venv
ENV PATH="${VIRTUAL_ENV}/bin:$PATH"

COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}

WORKDIR /app
COPY src ./src
COPY alembic ./alembic
COPY alembic.ini ./

ENTRYPOINT ["alembic"]
CMD ["upgrade", "head"]