# syntax=docker/dockerfile:1
FROM mcr.microsoft.com/vscode/devcontainers/python:3.12

# Create and activate a virtual environment.
RUN python -m venv .venv
ENV PATH=.venv/bin:$PATH
ENV VIRTUAL_ENV=.venv

# Install python dependencies for testing.
WORKDIR /workspace
COPY pyproject.toml .
RUN pip install --no-cache-dir poetry==1.8.4 && poetry install --no-root
