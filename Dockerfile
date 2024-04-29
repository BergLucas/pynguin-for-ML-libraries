# Base
FROM python:3.10.14-slim-bookworm AS base

ENV PYTHONUNBUFFERED=1

WORKDIR "/app"

# Environment
FROM base AS environment

RUN python -m venv ".venv"

ARG REQUIREMENTS_PATH

COPY "$REQUIREMENTS_PATH" "requirements.txt"

RUN /app/.venv/bin/pip install pip==23.3.1 -r "requirements.txt"

# Runner
FROM base AS runner

ENV PYNGUIN_DANGER_AWARE=1

RUN apt-get update && \
    apt-get install -y git && \
    rm -rf /var/lib/apt/lists/* && \
    adduser app

COPY "experiment.py" "experiment.py"

COPY "pynguin" "pynguin"

COPY --from=environment "/app/.venv" ".venv"

ENV PATH="/app/.venv/bin:$PATH"

ARG MODULES_CSV_PATH

COPY "$MODULES_CSV_PATH" "modules.csv"

USER app

ENTRYPOINT [ "python", "experiment.py" ]
