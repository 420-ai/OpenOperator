# Install

```bash
helm install windows-computers-release ./ --namespace computers --create-namespace
```

```bash
helm install windows-computers-release ./ \
  --set azureFileSecret.storageAccountName=oostorage4444 \
  --set azureFileSecret.storageAccountKey=$(az storage account keys list --account-name oostorage4444 --query "[0].value" -o tsv)
```

# Upgrade

```bash
helm upgrade windows-computers-release ./ --namespace computers
```
