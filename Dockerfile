# Base image with Python 3.12
FROM python:3.12-slim

# Set workdir
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl build-essential git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
ENV POETRY_VERSION=1.8.2
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="/root/.local/bin:$PATH"

# Copy only files needed to install dependencies
COPY pyproject.toml poetry.lock ./

# Install dependencies (without dev)
RUN poetry install --no-root --no-dev

# Now add the full project
COPY . .

# Install your packages
RUN poetry install --no-dev

# Activate virtualenv path for scripts
ENV PATH="/app/.venv/bin:$PATH"

# Expose port (optional)
EXPOSE 8000

# Set entrypoint
ENTRYPOINT ["poetry", "run"]

# Run FastAPI app
CMD ["uvicorn", "api.app:app", "--host", "0.0.0.0", "--port", "8000"]
