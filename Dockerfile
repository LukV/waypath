FROM python:3.12-slim

WORKDIR /app

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl=7.74.0-1.3+deb11u7 build-essential=12.9 git=1:2.30.2-1+deb11u2 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry (globally, not in virtualenv)
ENV POETRY_VERSION=1.8.2
SHELL ["/bin/bash", "-o", "pipefail", "-c"]
RUN curl -sSL https://install.python-poetry.org | python3 - \
    && ln -s /root/.local/bin/poetry /usr/local/bin/poetry

# Make sure poetry is available
RUN poetry --version

# Avoid copying local .venv
COPY pyproject.toml poetry.lock ./

# Disable virtualenvs being created outside the container
ENV POETRY_VIRTUALENVS_IN_PROJECT=true
ENV POETRY_NO_INTERACTION=1

# Install main dependencies and this package
RUN poetry install --only main

# Now copy the actual source code
COPY . .

# Expose port
EXPOSE 8000

# Set Python path for module resolution
ENV PYTHONPATH=/app/src

ENTRYPOINT ["poetry", "run"]
CMD ["uvicorn", "api.app:app", "--host", "0.0.0.0", "--port", "8000"]
