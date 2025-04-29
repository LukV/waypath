# Base image with Python 3.12
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl build-essential git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry globally
ENV POETRY_VERSION=1.8.2
RUN curl -sSL https://install.python-poetry.org | python3 - \
    && ln -s /root/.local/bin/poetry /usr/local/bin/poetry

# Make sure poetry is available
RUN poetry --version

# Disable interactive prompts and configure in-project virtualenvs
ENV POETRY_NO_INTERACTION=1
ENV POETRY_VIRTUALENVS_IN_PROJECT=true

# Copy only dependency files first
COPY pyproject.toml poetry.lock ./

# Install only main (production) dependencies
RUN poetry install --only main

# Now copy the actual source code
COPY . .

# Install your own package into the venv (without reinstalling dependencies)
RUN poetry install --only main --no-root

# Set environment variables
ENV PYTHONPATH=/app/src
ENV PATH="/app/.venv/bin:$PATH"

# Expose the application port
EXPOSE 8000

# Set the entrypoint and command
ENTRYPOINT ["poetry", "run"]
CMD ["uvicorn", "api.app:app", "--host", "0.0.0.0", "--port", "8000"]
