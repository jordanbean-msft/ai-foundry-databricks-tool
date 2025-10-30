# Azure AI Foundry + Azure Databricks Integration

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Enterprise-ready integration enabling Azure AI Foundry agents to manage and interact with Azure Databricks workspaces through a comprehensive REST API.

## 🚀 Quick Links

- **[Quick Start Guide](docs/QUICKSTART.md)** - Get up and running in minutes
- **[API Coverage](docs/API_COVERAGE.md)** - 66 endpoints across 12 categories
- **[Usage Examples](docs/EXAMPLES.md)** - Sample agent interactions
- **[Authentication](docs/AUTHENTICATION.md)** - PAT and Managed Identity setup
- **[Troubleshooting](docs/TROUBLESHOOTING.md)** - Common issues and solutions

## ✨ Features

**Comprehensive API Coverage (66 endpoints)**

- 🖥️ Compute management (clusters, instance pools)
- 📊 Job orchestration and monitoring
- 📁 File system operations (DBFS)
- 🔐 Security (secrets, Unity Catalog)
- 🔄 Version control (Git repos)
- 📚 Dependency management (libraries)
- 🔍 Vector search and analytics

**Production-Ready**

- ✅ PAT authentication (stable)
- 🔄 Automatic connection management
- 📝 OpenAPI 3.0.3 specification
- 🛡️ Enterprise security practices

**Developer-Friendly**

- 🐍 Python-based provisioning
- 📦 `uv` dependency management
- 🤖 Azure AI Agent SDK integration
- 📖 Comprehensive documentation

## 📋 What You Need

- Azure AI Foundry project with OpenAI deployment
- Azure Databricks workspace
- Azure CLI authenticated
- Python 3.8+ with `uv` or `pip`

See [Prerequisites](docs/PREREQUISITES.md) for detailed requirements.

## 🏃 Quick Start

```bash
# 1. Authenticate with Azure
az login
az account set --subscription <subscription-id>

# 2. Install dependencies
cd src
uv sync

# 3. Deploy the agent
uv run create_databricks_agent_with_pat.py \
  --ai-foundry-project-endpoint "https://<account>.services.ai.azure.com/api/projects/<project>" \
  --ai-model-deployment-name "gpt-4o" \
  --databricks-workspace-url "https://adb-<workspace-id>.<region>.azuredatabricks.net" \
  --subscription-id "<subscription-id>" \
  --resource-group "<resource-group>" \
  --account-name "<account-name>" \
  --project-name "<project-name>"
```

See [Quick Start Guide](docs/QUICKSTART.md) for complete instructions and parameters.

## 📂 Repository Structure

```
.
├── src/
│   ├── azure_databricks_openapi_spec.json   # OpenAPI 3.0.3 spec (66 endpoints)
│   ├── create_databricks_agent_with_pat.py  # ✅ PAT provisioning (stable)
│   └── create_databricks_agent_with_managed_identity.py  # 🚧 Managed identity (WIP)
├── docs/
│   ├── QUICKSTART.md          # Getting started guide
│   ├── API_COVERAGE.md        # Complete API endpoint reference
│   ├── EXAMPLES.md            # Usage examples and code samples
│   ├── AUTHENTICATION.md      # Auth methods and setup
│   ├── TROUBLESHOOTING.md     # Common issues and solutions
│   ├── PREREQUISITES.md       # Detailed prerequisites
│   └── SECURITY.md            # Security best practices
└── README.md                  # This file
```

## 💡 Example Usage

Ask your agent to perform Databricks operations:

```text
"List all running Databricks clusters"

"Create a vector search index named 'docs_index' on endpoint 'my-endpoint'
 using table 'catalog.schema.documents' with primary key 'id'"

"Install pandas version 2.0.0 on cluster 'analytics-cluster'"

"List all catalogs in Unity Catalog"
```

See [Examples](docs/EXAMPLES.md) for more sample operations.

## 🔒 Authentication Status

| Method           | Status         | Documentation                            |
| ---------------- | -------------- | ---------------------------------------- |
| PAT              | ✅ Stable      | [Authentication](docs/AUTHENTICATION.md) |
| Managed Identity | 🚧 In Progress | [Authentication](docs/AUTHENTICATION.md) |

## 📚 Documentation

- **[Quick Start](docs/QUICKSTART.md)** - Step-by-step setup
- **[API Coverage](docs/API_COVERAGE.md)** - All 66 endpoints detailed
- **[Examples](docs/EXAMPLES.md)** - Code samples and agent prompts
- **[Authentication](docs/AUTHENTICATION.md)** - PAT and Managed Identity
- **[Prerequisites](docs/PREREQUISITES.md)** - Azure resources and permissions
- **[Troubleshooting](docs/TROUBLESHOOTING.md)** - Common issues
- **[Security](docs/SECURITY.md)** - Best practices

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 References

- [Azure Databricks REST API](https://docs.databricks.com/api/azure/workspace/introduction)
- [Azure AI Foundry Documentation](https://learn.microsoft.com/azure/ai-studio/)
- [Azure AI Agents SDK](https://learn.microsoft.com/azure/ai-services/agents/)
- [Managed Identity Overview](https://learn.microsoft.com/azure/active-directory/managed-identities-azure-resources/overview)

---

**Built with ❤️ for Azure AI Foundry and Databricks integration**
