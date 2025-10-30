# Authentication

## Overview

Two authentication methods are available:

| Method                            | Script                                                 | Status         | When to Use                                                     |
| --------------------------------- | ------------------------------------------------------ | -------------- | --------------------------------------------------------------- |
| PAT (Custom Keys connection)      | `src/create_databricks_agent_with_pat.py`              | ✅ Stable      | Fast setup; environments without managed identity configuration |
| Managed Identity (AAD token flow) | `src/create_databricks_agent_with_managed_identity.py` | 🚧 In progress | Future long-term secure deployments                             |

> **Status:** Managed identity script is currently incomplete; token acquisition + tool registration logic is present but end-to-end Databricks API access via managed identity is not yet validated. Use the PAT script until this is resolved.

## PAT Authentication Flow

The recommended approach using Personal Access Tokens:

1. Script generates PAT (or uses provided PAT)
2. Connection stores `Authorization: Bearer <PAT>`
3. OpenAPI tool uses connection-based auth for each function call

### PAT Script Features

The PAT script (`src/create_databricks_agent_with_pat.py`):

- Automatically creates/updates the Custom Keys connection (no portal step required)
- Registers the Databricks OpenAPI tool with connection-based auth
- Supports both generated and user-provided PATs

**Output JSON includes:**

```jsonc
{
  "ai_foundry_project_endpoint": "...",
  "ai_model_deployment_name": "gpt-4o",
  "ai_foundry_agent_id": "asst_...",
  "agent_name": "DatabricksVectorSearchAgent",
  "databricks_workspace_url": "https://adb-....azuredatabricks.net",
  "auth_type": "PersonalAccessToken",
  "connection_name": "databricks-pat-connection",
  "connection_id": "/subscriptions/.../connections/databricks-pat-connection",
  "pat_lifetime_days": 90, // null when existing PAT supplied
  "pat_source": "generated" // "provided" if passed via --databricks-pat
}
```

**Notes:**

- When you pass an existing PAT, it's not logged and `pat_lifetime_days` is omitted (`null`)
- Rotate generated PATs before expiry (default 90 days; max 730)

## Managed Identity Flow (Not Yet Working)

⚠️ **This flow is not functional. These steps are for future reference only.**

<details>
<summary>Click to expand managed identity setup (incomplete)</summary>

### Planned Flow

1. Agent invokes tool
2. AI Foundry acquires AAD token for Databricks audience `2ff814a6-3304-4ab8-85cb-cd0e6f879c1d`
3. Token injected automatically
4. Databricks validates and responds

### Setup Steps (Not Working)

**Step 1: Enable Managed Identity**

```bash
az cognitiveservices account identity assign \
  --name <ai-foundry-account-name> \
  --resource-group <resource-group>
```

**Step 2: Grant RBAC Permissions**

```bash
PRINCIPAL_ID=$(az cognitiveservices account identity show \
  --name <ai-foundry-account-name> \
  --resource-group <resource-group> \
  --query principalId -o tsv)

az role assignment create \
  --assignee $PRINCIPAL_ID \
  --role "Contributor" \
  --scope /subscriptions/<sub-id>/resourceGroups/<rg>/providers/Microsoft.Databricks/workspaces/<workspace>
```

**Step 3: Run Script (expect failures)**

```bash
cd src
uv run create_databricks_agent_with_managed_identity.py \
  --subscription-id <subscription-id> \
  --resource-group <resource-group> \
  --ai-foundry-project-endpoint https://<account>.services.ai.azure.com/api/projects/<project> \
  --ai-model-deployment-name gpt-4o \
  --databricks-workspace-url https://adb-1234567890123456.azuredatabricks.net \
  --agent-name DatabricksVectorSearchAgent
```

</details>

## Code Examples

### PAT Tool Registration (Conceptual Extract)

```python
from azure.ai.agents.models import (
  OpenApiConnectionAuthDetails,
  OpenApiConnectionSecurityScheme,
  OpenApiFunctionDefinition,
  OpenApiToolDefinition,
)

auth = OpenApiConnectionAuthDetails(
  security_scheme=OpenApiConnectionSecurityScheme(connection_id="<connection-arm-id>")
)

openapi_function = OpenApiFunctionDefinition(
  name="databricks_api",
  description="Databricks REST API tool",
  spec=openapi_spec,
  auth=auth,
)

tool_def = OpenApiToolDefinition(openapi=openapi_function)
```

Managed identity example remains similar but uses `OpenApiManagedAuthDetails` instead.
