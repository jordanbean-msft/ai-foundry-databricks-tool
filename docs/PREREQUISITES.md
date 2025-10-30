# Prerequisites

## Azure Resources Required

Before running the PAT provisioning script, you need:

### 1. Azure AI Foundry Project

- A CognitiveServices account (kind: `AIServices` or `AIHub`)
- A project within that account
- Note the account name, project name, resource group, and subscription ID

### 2. Azure Databricks Workspace

- An active Databricks workspace
- Note the workspace URL (format: `https://adb-<workspace-id>.<region>.azuredatabricks.net`)

### 3. Azure OpenAI Deployment

- A deployed model in your AI Foundry project (e.g., `gpt-4o`, `gpt-4`, `gpt-35-turbo`)
- Note the deployment name

### 4. Azure Permissions

Your Azure CLI identity or managed identity needs:

- `Contributor` role on the Databricks workspace (to create PAT via API)
- `Contributor` role on the AI Foundry account/project (to create connections)

## Python Dependencies

The repository uses `uv` for dependency management. Install dependencies:

```bash
cd src
uv sync
```

Alternatively, install manually:

```bash
pip install azure-ai-projects azure-ai-agents azure-identity requests
```
