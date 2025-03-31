variable "location" {
  description = "Azure region"
  default     = "westus2"
}

variable "resource_group_name" {
  description = "Resource group name"
  default     = "oo-k8s-rg"
}

variable "aks_cluster_name" {
  description = "AKS cluster name"
  default     = "oo-k8s"
}

variable "aks_dns_prefix" {
  description = "DNS prefix for AKS"
  default     = "oo-dns"
}

variable "node_count" {
  description = "Number of nodes in the default node pool"
  default     = 3
}

variable "vm_size" {
  description = "VM size for AKS nodes"
  # For testing the deployment - v3 (allows nested virtualization)
  default     = "Standard_D2_v3"  
  # For real environment - v3 (allows nested virtualization)
  #default     = "Standard_D3_v3"
}
