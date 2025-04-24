output "container_app_url" {
  value       = azurerm_container_app.app.latest_revision_fqdn
  description = "Public URL of the Azure Container App"
}

output "acr_login_server" {
  value       = azurerm_container_registry.acr.login_server
  description = "Login server of the Azure Container Registry"
}