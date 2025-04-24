provider "azurerm" {
  features {}
  subscription_id = "ce029a16-1901-40e0-81d2-660951841d59"
}

resource "azurerm_resource_group" "waypath" {
  name     = var.resource_group_name
  location = var.location
}

resource "azurerm_container_registry" "acr" {
  name                = var.acr_name
  resource_group_name = azurerm_resource_group.waypath.name
  location            = azurerm_resource_group.waypath.location
  sku                 = "Basic"
  admin_enabled       = true
}

resource "azurerm_container_app_environment" "env" {
  name                = "${var.app_name}-env"
  location            = azurerm_resource_group.waypath.location
  resource_group_name = azurerm_resource_group.waypath.name
}

resource "azurerm_container_app" "app" {
  name                         = var.app_name
  container_app_environment_id = azurerm_container_app_environment.env.id
  resource_group_name          = azurerm_resource_group.waypath.name
  revision_mode                = "Single"

  secret {
    name  = "registry-password"
    value = azurerm_container_registry.acr.admin_password
  }

  template {
    container {
      name   = "waypath"
      image  = "${azurerm_container_registry.acr.login_server}/waypath:latest"
      cpu    = 0.5
      memory = "1.0Gi"

      env {
        name      = "REGISTRY_PASSWORD"
        secret_name = "registry-password"
      }
    }
  }

  ingress {
    external_enabled = true
    target_port      = 8000

    traffic_weight {
      percentage      = 100
      latest_revision = true
    }
  }

  registry {
    server               = azurerm_container_registry.acr.login_server
    username             = azurerm_container_registry.acr.admin_username
    password_secret_name = "registry-password"
  }
}
