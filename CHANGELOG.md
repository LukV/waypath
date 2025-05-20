## v0.31.0 (2025-05-20)

### Feat

- detect document type as part of pipeline
- add support for polling processing status
- Add support for invoices to API
- support parsing invoices with cli
- **routers/job.py**: add get_job_by_user_and_file endpoint
- split status in order status and processing status
- add filename to order object
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

- **schemas/invoice.py**: add status to Invoice pydantic schema
- drop and recreate lines on updating order or invoice lines
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

- move /upload to orders in prep of support invoices
- **factories.py**: create parser and extractor factories to support any doc parser and model
- refactor order processing logic to service orchestrator pattern

### Perf

- **database.py**: asynchronous database communication
