variable "resource_group_name" {
  type        = string
  default     = "rg-waypath-dev"
  description = "Name of the Azure Resource Group"
}

variable "location" {
  type        = string
  default     = "westeurope"
  description = "Azure region"
}

variable "app_name" {
  type        = string
  default     = "waypath-api-dev"
  description = "Name of the Azure Container App"
}

variable "acr_name" {
  type        = string
  default     = "waypathacrdev"
  description = "Name of the Azure Container Registry"
}