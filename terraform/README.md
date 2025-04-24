# Waypath Azure Infrastructure

This Terraform configuration provisions the infrastructure for the Waypath backend, which includes a containerized FastAPI application deployed on Azure Container Apps. Below is a visual overview and description of the components:

```
+-------------------------------------------------+
| Resource Group (rg-waypath-dev)                 |
|                                                 |
|   +-----------------------------------------+   |
|   | Container App Environment               |   |
|   | (waypath-api-dev-env)                   |   |
|   |                                         |   |
|   |   +----------------------------------+  |   |
|   |   | Container App                    |  |   |
|   |   | (waypath-api-dev)                |  |   |
|   |   | - Core API service               |  |   |
|   |   | - Runs Docker image from ACR     |  |   |
|   |   | - 0.5 vCPU / 1 Gi memory         |  |   |
|   |   | - Listens on port 8000           |  |   |
|   |   | - Publicly accessible            |  |   |
|   |   | - Uses secret for ACR login      |  |   |
|   |   +----------------------------------+  |   |
|   +-----------------------------------------+   |
|                                                 |
|   +-----------------------------------------+   |
|   | Azure Container Registry (waypathacrdev)|   |
|   | - Hosts Docker images for deployments   |   |
|   +-----------------------------------------+   |
+-------------------------------------------------+
```

## Resources

- **Resource Group**: Groups all Azure resources for easier management.
- **Container Registry (ACR)**: Stores Docker images. Used for deploying the backend application.
- **Container App Environment**: Provides a hosting context for container apps with network and logging settings.
- **Container App**: Deploys the FastAPI backend using the image from ACR, with autoscaling, secrets for ACR access, and public ingress enabled.

## Usage

- Deploy with:
  ```
  terraform init
  terraform apply
  ```

- Make sure the Docker image `waypath:latest` is pushed to ACR before deploying the app.