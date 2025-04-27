[![Dev Container Ready](https://img.shields.io/badge/devcontainer-ready-blue?logo=visualstudiocode)](https://containers.dev/)
[![CI](https://github.com/LukV/waypath/actions/workflows/ci.yml/badge.svg)](https://github.com/your-username/your-repo/actions/workflows/ci.yml)
![Last Commit](https://img.shields.io/github/last-commit/LukV/waypath)
[![Codespaces Ready](https://img.shields.io/badge/Codespaces-Ready-blue?logo=github)](https://github.com/codespaces)

# 🚀 Waypath Backend

**Waypath** is an AI-driven workflow automation platform, starting with intelligent order processing. This is the backend service, built with FastAPI, uv, and a battery-included developer setup.

---

## 📦 Features

- ⚡ FastAPI app with CLI interface (`wpath`)
- ✅ Code quality via `ruff`, `mypy`, `pre-commit`, `commitizen`
- 🐳 Optional DevContainer support
- 🔁 GitHub Actions for integration and deployment
- 🧪 VSCode tasks + launch configurations
- 🧰 Makefile for common tasks

---

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

> 💥 Find all make commands in the Makefile under the project root folder.

---

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

---

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

Then open a Pull Request into main.

### Versioning & Releases

We use **semantic versioning** powered by `commitizen`.

Semantic Versioning Format
- MAJOR.MINOR.PATCH → like 1.4.2
- feat: → bumps minor
- fix: → bumps patch
- BREAKING CHANGE: → bumps major