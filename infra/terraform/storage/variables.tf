variable "location" {
  description = "Azure region"
  default     = "westus2"
}

variable "resource_group_name" {
  description = "Resource group name"
  default     = "oo-storage-rg"
}

variable "storage_account_name" {
  description = "The name of the storage account. Must be globally unique, 3-24 characters, and lowercase."
  default     = "oostorage4444"
}
