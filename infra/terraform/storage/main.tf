terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
  }
}

provider "azurerm" {
  features {}
}


# A) Create a new resource group
resource "azurerm_resource_group" "oo_storage_rg" {
  name     = var.resource_group_name
  location = var.location
}

# B) Use existing resource group
# data "azurerm_resource_group" "oo_storage_rg" {
#   name = var.resource_group_name
# }

resource "azurerm_storage_account" "storage" {
  name                     = var.storage_account_name
  resource_group_name      = azurerm_resource_group.oo_storage_rg.name
  location                 = azurerm_resource_group.oo_storage_rg.location
  account_tier             = "Standard"
  account_replication_type = "LRS"

  tags = {
    project = "oo"
    environment = "dev"
  }
}
