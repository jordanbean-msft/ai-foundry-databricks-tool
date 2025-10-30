# Quick Start Guide

## Step 1: Authenticate with Azure

```bash
az login
az account set --subscription <subscription-id>
```

## Step 2: Run the Provisioning Script

Navigate to the `src/` directory and run:

```bash
cd src
uv run create_databricks_agent_with_pat.py \
  --ai-foundry-project-endpoint "https://<account-name>.services.ai.azure.com/api/projects/<project-name>" \
  --ai-model-deployment-name "gpt-4o" \
  --databricks-workspace-url "https://adb-<workspace-id>.<region>.azuredatabricks.net" \
  --subscription-id "<subscription-id>" \
  --resource-group "<resource-group-name>" \
  --account-name "<ai-foundry-account-name>" \
  --project-name "<project-name>" \
  --agent-name "DatabricksVectorSearchAgent" \
  --connection-name "databricks-pat-connection" \
  --pat-lifetime-days 90
```

## Using an Existing PAT

```bash
cd src
uv run create_databricks_agent_with_pat.py \
  --ai-foundry-project-endpoint "https://<account-name>.services.ai.azure.com/api/projects/<project-name>" \
  --ai-model-deployment-name "gpt-4o" \
  --databricks-workspace-url "https://adb-<workspace-id>.<region>.azuredatabricks.net" \
  --subscription-id "<subscription-id>" \
  --resource-group "<resource-group-name>" \
  --account-name "<ai-foundry-account-name>" \
  --project-name "<project-name>" \
  --agent-name "DatabricksVectorSearchAgent" \
  --connection-name "databricks-pat-connection" \
  --databricks-pat "<your-existing-databricks-pat>"
```

## Parameter Reference

| Parameter                       | Description                                         | Example                                                            |
| ------------------------------- | --------------------------------------------------- | ------------------------------------------------------------------ |
| `--ai-foundry-project-endpoint` | Full project endpoint URL                           | `https://my-account.services.ai.azure.com/api/projects/my-project` |
| `--ai-model-deployment-name`    | OpenAI model deployment name                        | `gpt-4o`, `gpt-4`, `gpt-35-turbo`                                  |
| `--databricks-workspace-url`    | Databricks workspace URL                            | `https://adb-1234567890123456.5.azuredatabricks.net`               |
| `--subscription-id`             | Azure subscription GUID                             | `12345678-1234-1234-1234-123456789012`                             |
| `--resource-group`              | Resource group containing AI Foundry account        | `rg-my-ai-foundry`                                                 |
| `--account-name`                | AI Foundry account name (CognitiveServices account) | `my-ai-foundry-account`                                            |
| `--project-name`                | AI Foundry project name                             | `my-project`                                                       |
| `--agent-name`                  | Name for the agent (created/updated)                | `DatabricksVectorSearchAgent`                                      |
| `--connection-name`             | Name for the Custom Keys connection                 | `databricks-pat-connection`                                        |
| `--pat-lifetime-days`           | PAT expiration (default 90, max 730)                | `90`                                                               |
| `--databricks-pat`              | Optional: use existing PAT (skips creation)         | `dapi...`                                                          |

## Next Steps

- See [Usage Examples](EXAMPLES.md) for sample agent interactions
- Review [API Coverage](API_COVERAGE.md) for available endpoints
- Check [Troubleshooting](TROUBLESHOOTING.md) if you encounter issues
