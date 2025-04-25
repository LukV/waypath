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
- [uv](https://github.com/astral-sh/uv):  
  Install with:
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```

### 2. Clone and Set Up

```bash
git clone https://github.com/LukV/waypath.git
cd waypath
make install # Installs dependencies and sets up pre-commit hooks
```

>  💥 Find all make commands in the Makefile under the project root folder.

---

## ▶️ Run the App

### Run FastAPI API
```bash
make serve
```

Your app is now running at [http://localhost:8000](http://localhost:8000)

### Run CLI
```bash
wpath --name "Waypath dev"
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
uv run --link-mode=copy pre-commit run --all-files
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
uv run --link-mode=copy pre-commit run --all-files
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