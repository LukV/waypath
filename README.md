# 🚀 Waypath Backend

**Waypath** is an AI-driven workflow automation platform, starting with intelligent order processing. This is the backend service, built with FastAPI, uv, and a battery-included developer setup.

---

## 📦 Features

- ⚡ FastAPI app with CLI interface (`wpath`)
- ✅ Code quality via `ruff`, `mypy`, `pre-commit`, `commitizen`
- 🐳 Optional DevContainer support
- 🔁 GitHub Actions-ready
- 🧪 VSCode tasks + launch configurations
- 🧰 Makefile for common tasks

---

## 🛠️ Setup

```bash
git clone https://github.com/your-org/waypath-backend.git
cd waypath-backend
make install
```

> Installs dependencies and sets up pre-commit hooks

---

## ▶️ Run the App

### Run FastAPI API
```bash
cd src/api
uv run fastapi dev
```

Visit: [http://localhost:8000](http://localhost:8000)

### Run CLI
```bash
wpath hello --name "Waypath dev"
```

---

## 🧪 Development

### Code quality
```bash
make lint       # Ruff lint
make format     # Ruff format
make typecheck  # Mypy strict checks
```

---

## 🚀 Contributing

```bash
git checkout -b feat/my-change
# Make your changes

git add .
make commit     # Uses Commitizen to prompt for a conventional commit message

# After merging and tagging a release
make bump       # Bumps version and updates changelog
git push origin feat/my-change
# Open a pull request
```

---

## 🗂 Structure

```
src/
├── api/         # FastAPI app
└── core/        # Typer CLI
.vscode/         # Dev tooling (tasks, launch)
.devcontainer/   # Optional remote dev setup
Makefile         # CLI shortcuts
pyproject.toml   # Config for all tools
```

---

## 🔮 Coming Soon

- [ ] Production Dockerfile
- [ ] Terraform infra (Azure Container App, ACR)
- [ ] CI/CD via GitHub Actions
- [ ] LLM-powered parsing pipeline

---

## 📜 License

MIT © Luk Verhelst / Dataframe One

---

> Questions? Ideas? Feedback? Let’s build Waypath together.
