## v0.18.0 (2025-05-04)

### Feat

- add hello cli endpoint
- store orders in a database
- **cli.py**: convert markdown to a pydantic model
- **cli.py**: parse documents with LlamaParse
- remove icon and role from User entity
- add create user endpoint
- switch uv to pip
- **terraform**: adds deploy to azure
- initial commit

### Fix

- build fix error
- fix build error
- fix merge conflict
- migrate from uv to poetry
- **deploy.yml**: Fix build errors
- **deploy.yml**: fix build error
- **deploy.yml**: fix build error
- **deploy.yml**: fix build error

### Refactor

- **factories.py**: create parser and extractor factories to support any doc parser and model
- refactor order processing logic to service orchestrator pattern

### Perf

- **database.py**: asynchronous database communication
