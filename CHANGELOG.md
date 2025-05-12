## v0.25.0 (2025-05-12)

### Feat

- support doc upload from web site
- search orders by name, address and invoice number
- add order stats
- remove unique constraint for order numbers
- add order processing status
- add reset passwords endpoints
- add crud for user and order entities
- accept mail messages at /inbound-emails
- support azure DI and azure OpenAI as parser and extractors
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

- **Dockerfile**: trust Azure’s X-Forwarded-Proto: https header and preserve the original HTTPS scheme
- Change @model_validator async to sync for Pydantic v2
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
