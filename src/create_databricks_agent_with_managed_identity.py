#!/usr/bin/env -S uv run
"""Create AI Foundry agent with Databricks Vector Search using Managed Identity.

This script:
1. Creates an Azure AI Foundry connection with Managed Identity auth
2. Registers the Databricks OpenAPI spec as a tool
3. Creates an agent that can call Databricks APIs using a user-assigned managed identity

Prerequisites:
* AI Foundry project with user-assigned managed identity enabled
* Managed identity granted "Contributor" role on Databricks workspace
* Databricks workspace URL and resource ID

Example:
    uv run create_databricks_agent_with_managed_identity.py \
        --subscription-id <SUB> \
        --resource-group <RG> \
        --ai-foundry-project-endpoint <project_url> \
        --ai-model-deployment-name gpt-4o \
        --databricks-workspace-url https://adb-1234567890123456.azuredatabricks.net \
        --databricks-resource-id /subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.Databricks/workspaces/{name} \
        --agent-name DatabricksVectorSearchAgent
"""

import argparse
import json
import logging
import sys
from pathlib import Path

from azure.ai.agents.models import (OpenApiFunctionDefinition,
                                    OpenApiManagedAuthDetails,
                                    OpenApiManagedSecurityScheme,
                                    OpenApiToolDefinition)
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger(__name__)


def load_databricks_openapi_spec() -> dict:
    """Load the Databricks OpenAPI specification."""
    script_dir = Path(__file__).parent
    openapi_file = script_dir / "azure_databricks_openapi_spec.json"
    if not openapi_file.exists():
        raise FileNotFoundError(
            f"Databricks OpenAPI spec not found: {openapi_file}"
        )
    with open(openapi_file, "r", encoding="utf-8") as f:
        return json.load(f)


def customize_openapi_spec_for_workspace(
    spec: dict, databricks_workspace_url: str
) -> dict:
    """Customize the OpenAPI spec with the specific workspace URL."""
    customized_spec = spec.copy()

    # Update the server URL with the actual workspace
    if "servers" in customized_spec and len(customized_spec["servers"]) > 0:
        customized_spec["servers"][0]["url"] = databricks_workspace_url

    return customized_spec


def register_databricks_openapi_tool(
    project_endpoint: str,
    databricks_workspace_url: str,
    agent_name: str,
    model_deployment_name: str,
) -> str:
    """
    Register Databricks as an OpenAPI tool in AI Foundry agent.

    Returns the agent ID.
    """
    logger.info("Setting up Databricks OpenAPI tool with Managed Identity...")

    credential = DefaultAzureCredential()
    project_client = AIProjectClient(
        credential=credential, endpoint=project_endpoint
    )
    client = project_client.agents

    # Load and customize OpenAPI spec
    openapi_spec = load_databricks_openapi_spec()
    openapi_spec = customize_openapi_spec_for_workspace(
        openapi_spec, databricks_workspace_url
    )

    # Configure managed identity authentication
    # The audience is the Azure Databricks resource ID for authentication
    managed_identity_auth = OpenApiManagedAuthDetails(
        security_scheme=OpenApiManagedSecurityScheme(
            audience="2ff814a6-3304-4ab8-85cb-cd0e6f879c1d"  # Azure Databricks App ID
        )
    )

    # Create OpenAPI function definition
    openapi_function = OpenApiFunctionDefinition(
        name="databricks_api",
        description=(
            "Access to Azure Databricks REST API including clusters, jobs, "
            "workspace management, command execution, and vector search operations"
        ),
        spec=openapi_spec,
        auth=managed_identity_auth,
    )

    tool_definition = OpenApiToolDefinition(openapi=openapi_function)

    # Create or update agent
    logger.info(f"Creating/updating agent: {agent_name}")
    agents = client.list_agents()
    existing_agent = next((a for a in agents if a.name == agent_name), None)

    instructions = """You are an AI assistant with access to Azure Databricks APIs.

You can help with:
- Managing Databricks clusters (list, create, start, stop, delete)
- Running and monitoring Databricks jobs
- Managing workspace notebooks and files
- Executing commands on clusters
- Vector search operations (creating endpoints and indexes, querying vectors)

When using the Databricks API:
1. Always check cluster status before executing commands
2. Use appropriate error handling
3. For vector search, understand the difference between Delta Sync and Direct Access indexes
4. Remember that authentication is handled automatically via managed identity

Be helpful and provide clear explanations of what you're doing."""

    if existing_agent:
        logger.info(f"Updating existing agent: {existing_agent.id}")
        client.update_agent(
            agent_id=existing_agent.id,
            name=agent_name,
            description="AI Agent with access to Azure Databricks APIs via Managed Identity",
            instructions=instructions,
            tools=[tool_definition],
            model=model_deployment_name,
        )
        agent_id = existing_agent.id
    else:
        logger.info(f"Creating new agent: {agent_name}")
        agent = client.create_agent(
            model=model_deployment_name,
            name=agent_name,
            description="AI Agent with access to Azure Databricks APIs via Managed Identity",
            instructions=instructions,
            tools=[tool_definition],
        )
        agent_id = agent.id

    logger.info("Databricks OpenAPI tool registered successfully.")
    return agent_id


def parse_args(argv: list[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description=(
            "Create AI Foundry agent with Databricks access via Managed Identity. "
            "Print agent metadata as JSON."
        )
    )

    # Required args
    p.add_argument(
        "--ai-foundry-project-endpoint",
        required=True,
        dest="ai_foundry_project",
        help="AI Foundry project endpoint URL",
    )
    p.add_argument(
        "--ai-model-deployment-name",
        required=True,
        dest="ai_model_deployment_name",
        help="Model deployment name (e.g. gpt-4o)",
    )
    p.add_argument(
        "--databricks-workspace-url",
        required=True,
        dest="databricks_workspace_url",
        help="Databricks workspace URL (e.g., https://adb-1234567890123456.azuredatabricks.net)",
    )

    # Optional args
    p.add_argument(
        "--agent-name",
        default="DatabricksVectorSearchAgent",
        help="Name for the AI agent",
    )
    p.add_argument(
        "--debug",
        action="store_true",
        help="Print full traceback on error",
    )
    p.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging",
    )

    return p.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    try:
        agent_id = register_databricks_openapi_tool(
            project_endpoint=args.ai_foundry_project,
            databricks_workspace_url=args.databricks_workspace_url,
            agent_name=args.agent_name,
            model_deployment_name=args.ai_model_deployment_name,
        )

        output_payload = {
            "ai_foundry_project_endpoint": args.ai_foundry_project,
            "ai_model_deployment_name": args.ai_model_deployment_name,
            "ai_foundry_agent_id": agent_id,
            "agent_name": args.agent_name,
            "databricks_workspace_url": args.databricks_workspace_url,
            "auth_type": "ManagedIdentity",
            "databricks_audience": "2ff814a6-3304-4ab8-85cb-cd0e6f879c1d",
        }

        logger.info("Emitting agent configuration JSON")
        print(json.dumps(output_payload, indent=2))
        return 0

    except Exception as ex:
        logger.error(f"Error: {ex}")
        if args.debug:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
