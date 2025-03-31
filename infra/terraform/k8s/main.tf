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
resource "azurerm_resource_group" "oo_rg" {
  name     = var.resource_group_name
  location = var.location
}

# B) Use existing resource group
# data "azurerm_resource_group" "oo_rg" {
#   name = var.resource_group_name
# }

resource "azurerm_kubernetes_cluster" "oo_aks" {
  name                = var.aks_cluster_name
  location            = azurerm_resource_group.oo_rg.location
  resource_group_name = azurerm_resource_group.oo_rg.name
  dns_prefix          = var.aks_dns_prefix

  identity {
    type = "SystemAssigned"
  }

  default_node_pool {
    name                = "sysnodepool"
    node_count          = 1
    vm_size             = "Standard_DS2_v2" # Minimum 2+ cores, 4+ GB RAM
  }

  tags = {
    project = "oo"
    environment = "dev"
  }
}

resource "azurerm_kubernetes_cluster_node_pool" "usernp" {
  name                  = "usernodepool"
  kubernetes_cluster_id = azurerm_kubernetes_cluster.oo_aks.id
  vm_size               = var.vm_size
  node_count            = var.node_count
  mode                  = "User"
  os_type               = "Linux"
}
