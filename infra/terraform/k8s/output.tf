output "aks_cluster_name" {
  value = azurerm_kubernetes_cluster.oo_aks.name
}

output "kube_config" {
  value     = azurerm_kubernetes_cluster.oo_aks.kube_config_raw
  sensitive = true
}
