# Base image
FROM python:3.12-slim

# Install system deps
RUN apt-get update && apt-get install -y \
    curl git build-essential sudo \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -ms /bin/bash vscode && \
    usermod -aG sudo vscode && \
    echo 'vscode ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

# Switch to vscode user
USER vscode

# Install Poetry as vscode user
RUN curl -sSL https://install.python-poetry.org | python3 -

# Set path to include poetry for non-login shell
ENV PATH="/home/vscode/.local/bin:$PATH"

# Set working directory
WORKDIR /workspace