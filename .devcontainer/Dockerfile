# syntax=docker/dockerfile:1

# Stage 1 — Get latest uv from Astral
# hadolint ignore=DL3006
FROM ghcr.io/astral-sh/uv:latest AS uv

# Stage 2 — Devcontainer base with Debian and non-root user
FROM mcr.microsoft.com/vscode/devcontainers/base:debian-11

# Install extra system libs
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy uv + uvx from builder image
COPY --from=uv --chown=vscode:vscode /uv /bin/uv
COPY --from=uv --chown=vscode:vscode /uvx /bin/uvx

# Set working directory inside container
WORKDIR /workspace
