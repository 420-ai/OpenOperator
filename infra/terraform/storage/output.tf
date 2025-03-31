output "storage_account_connection_string" {
  value       = azurerm_storage_account.storage.primary_connection_string
  description = "The connection string for the storage account"
  sensitive   = true
}