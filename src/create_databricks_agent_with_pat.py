"""Provision (create or update) an Azure AI Foundry agent with Databricks
access using a Personal Access Token (PAT).

Full setup in one run:
1. Create Databricks PAT
2. Create (or update) Custom Keys connection
3. Create (or update) agent with Databricks OpenAPI tool

Prerequisites:
* Azure CLI login OR managed identity
* Databricks workspace access (can create PAT)
* Contributor on AI Foundry account & project

Usage (example - auto-create PAT):
        uv run create_databricks_agent_with_pat.py \
            --ai-foundry-project-endpoint \
                "https://<account>.services.ai.azure.com/api/projects/<project>" \
            --ai-model-deployment-name "gpt-4o" \
            --databricks-workspace-url \
                "https://adb-xxxxxxxxxxxxxxxx.azuredatabricks.net" \
            --subscription-id <sub-id> \
            --resource-group <rg-name> \
            --account-name <ai-foundry-account> \
            --project-name <project-name> \
            --agent-name DatabricksVectorSearchAgent \
            --connection-name databricks-pat-connection

Outputs JSON describing agent + connection.

Provide an existing PAT instead of creating a new one:
        uv run create_databricks_agent_with_pat.py ... \
            --databricks-pat <existing-pat-token>
"""

import argparse
import json
import logging
from pathlib import Path

import requests
from azure.ai.agents.models import (OpenApiConnectionAuthDetails,
                                    OpenApiConnectionSecurityScheme,
                                    OpenApiFunctionDefinition,
                                    OpenApiToolDefinition)
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="[%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)


def create_databricks_pat(
    databricks_workspace_url: str,
    credential: DefaultAzureCredential,
    comment: str = "AI Foundry Agent",
    lifetime_days: int = 90,
) -> str:
    """
    Create a Databricks Personal Access Token using the Databricks API.

    Args:
        databricks_workspace_url: The Databricks workspace URL
        credential: Azure credential to get Databricks token
        comment: Comment for the PAT
        lifetime_days: Token lifetime in days (max 730, recommended 90)

    Returns:
        The generated PAT token
    """
    logger.info("Creating Databricks Personal Access Token...")

    # Get Azure AD token for Databricks
    token = credential.get_token(
        "2ff814a6-3304-4ab8-85cb-cd0e6f879c1d/.default"
    ).token

    # Create PAT using Databricks API
    url = f"{databricks_workspace_url}/api/2.0/token/create"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    lifetime_seconds = lifetime_days * 24 * 60 * 60
    payload = {
        "comment": comment,
        "lifetime_seconds": lifetime_seconds,
    }

    response = requests.post(url, headers=headers, json=payload, timeout=30)

    if response.status_code != 200:
        error_msg = (
            f"Failed to create PAT: {response.status_code} - {response.text}"
        )
        logger.error(error_msg)
        raise RuntimeError(error_msg)

    pat_data = response.json()
    pat_token = pat_data.get("token_value")

    if not pat_token:
        raise RuntimeError(f"PAT token not found in response: {pat_data}")

    logger.info("✓ PAT created (expires in %d days)", lifetime_days)
    token_id = pat_data.get("token_info", {}).get("token_id")
    if token_id:
        logger.info("  Token ID: %s", token_id)

    return pat_token


def create_ai_foundry_connection(
    connection_name: str,
    databricks_pat: str,
    subscription_id: str,
    resource_group: str,
    account_name: str,
    project_name: str,
) -> str:
    """
    Create an AI Foundry connection with the Databricks PAT.

    Uses Azure REST API to create a Custom Keys connection in the project.

    Args:
        project_client: AI Foundry project client (for compatibility)
        connection_name: Name for the connection
        databricks_pat: The Databricks PAT token
        subscription_id: Azure subscription ID
        resource_group: Resource group name
        account_name: AI Foundry account name
        project_name: AI Foundry project name

    Returns:
        Connection ID
    """
    logger.info("Creating AI Foundry connection: %s", connection_name)

    # Get Azure management token
    credential = DefaultAzureCredential()
    token = credential.get_token("https://management.azure.com/.default")

    # Build connection resource ID
    connection_id = (
        f"/subscriptions/{subscription_id}/resourceGroups/{resource_group}/"
        f"providers/Microsoft.CognitiveServices/accounts/{account_name}/"
        f"projects/{project_name}/connections/{connection_name}"
    )

    # REST API endpoint
    api_version = "2025-04-01-preview"
    base_mgmt = "https://management.azure.com"
    url = f"{base_mgmt}{connection_id}?api-version={api_version}"

    # Connection payload - Custom Keys type with Authorization header
    payload = {
        "properties": {
            "category": "CustomKeys",
            "authType": "CustomKeys",
            "isSharedToAll": False,
            "target": "https://placeholder.example.com",  # placeholder target
            "metadata": {
                "ApiType": "Databricks",
                "ResourceId": "databricks-api",
            },
            "credentials": {
                "keys": {
                    "Authorization": f"Bearer {databricks_pat}"
                }
            },
        }
    }

    headers = {
        "Authorization": f"Bearer {token.token}",
        "Content-Type": "application/json",
    }

    response = requests.put(url, json=payload, headers=headers, timeout=30)

    if response.status_code in (200, 201):
        logger.info("✓ Connection created: %s", connection_name)
        return connection_id
    else:
        error_msg = (
            "Failed to create connection: "
            f"{response.status_code} - {response.text}"
        )
        logger.error(error_msg)
        raise RuntimeError(error_msg)


def load_databricks_openapi_spec() -> dict:
    """Load the Databricks OpenAPI specification from file."""
    spec_path = (
        Path(__file__).parent / "azure_databricks_openapi_spec.json"
    )

    if not spec_path.exists():
        raise FileNotFoundError(
            f"OpenAPI spec not found at {spec_path}. "
            "Ensure azure_databricks_openapi_spec.json is in this directory."
        )

    with open(spec_path, "r", encoding="utf-8") as f:
        return json.load(f)


def customize_openapi_spec_for_workspace(
    spec: dict, databricks_workspace_url: str
) -> dict:
    """
    Customize the OpenAPI spec with workspace URL and PAT auth.

    Removes Entra ID oauth2 scheme; switches to API key (Bearer token).
    """
    customized_spec = spec.copy()

    # Update the server URL with the actual workspace
    if "servers" in customized_spec and len(customized_spec["servers"]) > 0:
        customized_spec["servers"][0]["url"] = databricks_workspace_url

    # Update security schemes to use API key (Bearer token) instead of oauth2
    if (
        "components" in customized_spec
        and "securitySchemes" in customized_spec["components"]
    ):
        customized_spec["components"]["securitySchemes"] = {
            "bearerAuth": {
                "type": "apiKey",
                "name": "Authorization",
                "in": "header",
                "description": "Databricks PAT: Bearer <token>"
            }
        }

    # Update security to use bearerAuth
    customized_spec["security"] = [{"bearerAuth": []}]

    return customized_spec


def register_databricks_openapi_tool(
    project_endpoint: str,
    databricks_workspace_url: str,
    connection_name: str,
    agent_name: str,
    model_deployment_name: str,
    subscription_id: str,
    resource_group: str,
    account_name: str,
    project_name: str,
    databricks_pat: str | None = None,
    pat_lifetime_days: int = 90,
    pat_comment: str = "AI Foundry Agent",
) -> str:
    """
    Complete setup: Create PAT, create connection, and register agent.

    Returns the agent ID.
    """
    credential = DefaultAzureCredential()
    project_client = AIProjectClient(
        credential=credential, endpoint=project_endpoint
    )

    # Step 1: Use provided PAT or create a new one
    if databricks_pat:
        if not databricks_pat.strip():
            raise ValueError("--databricks-pat cannot be empty when provided")
        logger.info("Using provided Databricks PAT (skipping creation).")
        pat_token = databricks_pat.strip()
        pat_source = "provided"
    else:
        pat_token = create_databricks_pat(
            databricks_workspace_url=databricks_workspace_url,
            credential=credential,
            comment=pat_comment,
            lifetime_days=pat_lifetime_days,
        )
        pat_source = "generated"

    # Step 2: Create AI Foundry connection
    connection_id = create_ai_foundry_connection(
        connection_name=connection_name,
        databricks_pat=pat_token,
        subscription_id=subscription_id,
        resource_group=resource_group,
        account_name=account_name,
        project_name=project_name,
    )

    # Step 3: Set up OpenAPI tool with connection auth
    logger.info("Setting up Databricks OpenAPI tool...")

    client = project_client.agents

    # Load and customize OpenAPI spec
    openapi_spec = load_databricks_openapi_spec()
    openapi_spec = customize_openapi_spec_for_workspace(
        openapi_spec, databricks_workspace_url
    )

    # Configure connection-based authentication (API key)
    connection_auth = OpenApiConnectionAuthDetails(
        security_scheme=OpenApiConnectionSecurityScheme(
            connection_id=connection_id
        )
    )

    # Create OpenAPI function definition
    openapi_function = OpenApiFunctionDefinition(
        name="databricks_api",
        description=(
            "Access to Azure Databricks REST API including clusters, jobs, "
            "workspace management, command execution, and vector search"
        ),
        spec=openapi_spec,
        auth=connection_auth,
    )

    # Wrap in OpenApiToolDefinition
    openapi_tool = OpenApiToolDefinition(openapi=openapi_function)

    logger.info("Creating/updating agent: %s", agent_name)

    # Check if agent exists
    agents = client.list_agents()
    existing_agent = None
    for agent in agents:
        if agent.name == agent_name:
            existing_agent = agent
            break

    instructions = (
        "You are a helpful AI assistant with access to Azure Databricks. "
        "You can help users interact with Databricks resources including "
        "clusters, jobs, workspaces and vector search endpoints. "
        "When users ask about Databricks resources, use the "
        "databricks_api tool to retrieve information."
    )
    if existing_agent:
        logger.info("Updating existing agent: %s", existing_agent.id)
        agent = client.update_agent(
            agent_id=existing_agent.id,
            name=agent_name,
            model=model_deployment_name,
            instructions=instructions,
            tools=[openapi_tool],
        )
    else:
        logger.info("Creating new agent")
        agent = client.create_agent(
            name=agent_name,
            model=model_deployment_name,
            instructions=instructions,
            tools=[openapi_tool],
        )

    logger.info("Databricks OpenAPI tool registered successfully.")

    # Emit configuration as JSON for easy parsing
    logger.info("Emitting agent configuration JSON")
    config = {
        "ai_foundry_project_endpoint": project_endpoint,
        "ai_model_deployment_name": model_deployment_name,
        "ai_foundry_agent_id": agent.id,
        "agent_name": agent.name,
        "databricks_workspace_url": databricks_workspace_url,
        "auth_type": "PersonalAccessToken",
        "connection_name": connection_name,
        "connection_id": connection_id,
        "pat_lifetime_days": (
            pat_lifetime_days if pat_source == "generated" else None
        ),
        "pat_source": pat_source,
    }
    print(json.dumps(config, indent=2))

    return agent.id


def main():
    parser = argparse.ArgumentParser(
        description="Create AI Foundry agent with Databricks PAT auth"
    )
    parser.add_argument(
        "--ai-foundry-project-endpoint",
        required=True,
        help="AI Foundry project endpoint URL",
    )
    parser.add_argument(
        "--ai-model-deployment-name",
        required=True,
        help="Azure OpenAI model deployment name (e.g., gpt-4.1)",
    )
    parser.add_argument(
        "--databricks-workspace-url",
        required=True,
        help="Databricks workspace URL",
    )
    parser.add_argument(
        "--agent-name",
        default="DatabricksVectorSearchAgent",
        help="Name for the agent (default: DatabricksVectorSearchAgent)",
    )
    parser.add_argument(
        "--connection-name",
        default="databricks-pat-connection",
        help="AI Foundry connection name (default: databricks-pat-connection)",
    )
    parser.add_argument(
        "--subscription-id",
        required=True,
        help="Azure subscription ID",
    )
    parser.add_argument(
        "--resource-group",
        required=True,
        help="Azure resource group name",
    )
    parser.add_argument(
        "--account-name",
        required=True,
        help="AI Foundry account name (CognitiveServices account)",
    )
    parser.add_argument(
        "--project-name",
        required=True,
        help="AI Foundry project name",
    )
    parser.add_argument(
        "--pat-lifetime-days",
        type=int,
        default=90,
        help="PAT lifetime in days (default: 90, max: 730)",
    )
    parser.add_argument(
        "--pat-comment",
        default="AI Foundry Agent",
        help="Comment for the PAT (default: AI Foundry Agent)",
    )
    parser.add_argument(
        "--databricks-pat",
        help="Use an existing Databricks PAT instead of creating a new one",
    )
    # Removed legacy skip/bypass PAT flags (script always creates PAT)
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose HTTP logging",
    )

    args = parser.parse_args()

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    if args.verbose:
        # Enable HTTP request/response logging
        import sys

        logging.basicConfig(
            level=logging.DEBUG,
            format="%(levelname)s [%(name)s] %(message)s",
            handlers=[logging.StreamHandler(sys.stdout)],
        )
        logging.getLogger("azure").setLevel(logging.DEBUG)

    try:
        agent_id = register_databricks_openapi_tool(
            project_endpoint=args.ai_foundry_project_endpoint,
            databricks_workspace_url=args.databricks_workspace_url,
            connection_name=args.connection_name,
            agent_name=args.agent_name,
            model_deployment_name=args.ai_model_deployment_name,
            subscription_id=args.subscription_id,
            resource_group=args.resource_group,
            account_name=args.account_name,
            project_name=args.project_name,
            databricks_pat=args.databricks_pat,
            pat_lifetime_days=args.pat_lifetime_days,
            pat_comment=args.pat_comment,
        )

        logger.info("Success! Agent ID: %s", agent_id)

    except (RuntimeError, requests.RequestException) as exc:
        logger.error("Failed to create/update agent: %s", exc)
        if args.debug:
            raise
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
