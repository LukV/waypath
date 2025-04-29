[![Dev Container Ready](https://img.shields.io/badge/devcontainer-ready-blue?logo=visualstudiocode)](https://containers.dev/)
[![CI](https://github.com/LukV/waypath/actions/workflows/ci.yml/badge.svg)](https://github.com/LukV/waypath/actions/workflows/ci.yml)
![Last Commit](https://img.shields.io/github/last-commit/LukV/waypath)
[![Codespaces Ready](https://img.shields.io/badge/Codespaces-Ready-blue?logo=github)](https://github.com/codespaces)

# 🚀 Waypath Backend

**Waypath** is a skeleton Python backend service, built with FastAPI, poetry, and a battery-included developer setup.

## 📦 Features

- ⚡ FastAPI app with CLI interface (`wpath`)
- ✅ CI/CD via `ruff`, `mypy`, `pre-commit`, `commitizen`
- 🐳 DevContainer support
- 🔁 GitHub Actions for integration and deployment to Azure

## 🛠️ Setup Your Development Environment

### 1. Prerequisites
- Python 3.12+
- [VSCode](https://code.visualstudio.com/)
- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- [Git](https://git-scm.com/)
- Poetry
  Install Poetry
  ```bash
  curl -sSL https://install.python-poetry.org | python3 -
  # ensure Poetry is available in your shell:
  poetry --version
  ```

> 💥 Pro tip: You can use pyenv to install and manage specific Python versions, then let Poetry use it via `poetry env use $(pyenv which python)`.

### 2. Clone and Set Up

```bash
git clone https://github.com/LukV/waypath.git
cd waypath
make install # Installs dependencies and sets up pre-commit hooks
```

## ▶️ Run the App

### Run FastAPI API
```bash
make serve
```

Your app is now running at [http://localhost:8000](http://localhost:8000)

### Run CLI
```bash
poetry run wpath --name "Waypath dev"
```

## 🧪 Development

### Coding Standards & Pre-commit

Use ruff and mypy for code quality.

```bash
make lint       # Ruff lint
make format     # Ruff format
make typecheck  # Mypy strict checks
```

Use  [Conventional Commits](https://www.conventionalcommits.org/) via:

```bash
make commit
```

Run checks before committing:

```bash
poetry run pre-commit run --all-files
```

### Git Workflow

#### Branch Strategy
- `main`: The only long-lived branch.
- `feature/*`: For new features.
- `fix/*`: For bugfixes.

#### Typical Flow

```bash
git checkout main
git pull origin main
git checkout -b feature/my-change
# Make changes
git add .
poetry run pre-commit run --all-files
make commit
git push origin feature/my-change
```

This triggers the CI Github Action. Then open a Pull Request into main.

### From PR to Azure Deployment

We use **semantic versioning** powered by `commitizen`.

Semantic Versioning Format
- MAJOR.MINOR.PATCH → like 1.4.2
- feat: → bumps minor
- fix: → bumps patch
- BREAKING CHANGE: → bumps major

### Before Deployment

Before GitHub Actions can deploy the app, **the Azure infrastructure must exist**.  
Follow the guide here to spin it up using Terraform:  
[Terraform README](https://github.com/LukV/waypath/blob/main/terraform/README.md)

### Deployment Flow After Merge

1. PR is reviewed and squash-merged into `main`.
2. GitHub Actions automatically triggers the `Release & Deploy` workflow:
   - 📂 Checkout the repo
   - 📦 Install Poetry & Python 3.12
   - ✅ Run lint and type checks
   - 📘 Generate changelog
   - 🔢 Auto-bump the version
   - 🚀 Push updated version and changelog to GitHub
   - 🔐 Login to Azure securely
   - 🐳 Build and push Docker image to Azure Container Registry
   - 🔄 Restart Azure Container App using the new image

### Key Details

- **Trigger:** on every push to `main` or manually (`workflow_dispatch`)
- **Version bump:** handled automatically inside the GitHub Action
- **Docker image tags:** both latest and commit SHA
- **Deployment:** happens via Azure CLI commands in the workflow

Result:  
💚 **Your changes are deployed live on Azure** — no manual action needed.


## Common Tasks

| Task                        | Command                                      |
|-----------------------------|----------------------------------------------|
| Start API locally           | `make serve`                                 |
| Run pre-commit checks       | `poetry run pre-commit run --all-files`      |
| Add dependencies            | `poetry add some-lib; poetry update`         |
| Lock dependencies           | `poetry lock`                                |
| Lint and type check         | `make lint`                                  |
| Commit with structure       | `cz commit`                                  |
| Run tests                   | `make test`                                  |


You're ready to contribute. Ask questions, push often, and keep learning! 🚀

