# Usage Examples

## Using the Agent

Once the agent is created, interact with it via the Azure AI Projects SDK:

```python
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

# Connect to AI Foundry project
project_client = AIProjectClient(
    credential=DefaultAzureCredential(),
    endpoint="<your-project-endpoint>"
)

# Get the agent
agent = project_client.agents.get_agent("<agent-id>")

# Create a thread and send messages
thread = project_client.agents.create_thread()

# Ask the agent to list clusters
message = project_client.agents.create_message(
    thread_id=thread.id,
    role="user",
    content="List all Databricks clusters in the workspace"
)

# Run the agent
run = project_client.agents.create_and_process_run(
    thread_id=thread.id,
    assistant_id=agent.id
)

# Get the response
messages = project_client.agents.list_messages(thread_id=thread.id)
print(messages.data[0].content[0].text.value)
```

## Example Operations

### Compute Management

**List Clusters**

```
"List all running Databricks clusters"
```

**Create Instance Pool**

```
"Create an instance pool named 'ml-pool' using Standard_DS3_v2 nodes with
min 2 idle instances and max capacity of 10"
```

### Data & Storage

**DBFS File Operations**

```
"List all files in /mnt/data directory in DBFS"
"Read the contents of /mnt/configs/app.json from DBFS"
"Upload a file to /mnt/data/processed/results.csv in DBFS"
```

**Unity Catalog**

```
"List all catalogs in Unity Catalog"
"Create a schema named 'analytics' in the 'production' catalog"
"Show me all tables in catalog 'production' schema 'analytics'"
```

### Vector Search

**Create Vector Search Index**

```
"Create a vector search index named 'documents_index' on endpoint 'my-endpoint'
using the Delta table 'catalog.schema.documents' with primary key 'id'"
```

**Query Vector Search**

```
"Query the vector search index 'documents_index' with the text
'machine learning best practices' and return the top 5 results"
```

### Development & Dependencies

**Git Repository Integration**

```
"Create a new repo from https://github.com/myorg/notebooks using GitHub provider
in the path /Repos/Production/notebooks"
"Update the repo to branch 'feature/new-models'"
```

**Library Management**

```
"Install the pandas library version 2.0.0 on cluster 'analytics-cluster'"
"List all installed libraries on cluster 'ml-cluster'"
```

### Security

**Secrets Management**

```
"Create a secret scope named 'production-secrets'"
"Store a secret named 'api-key' with value 'xyz123' in scope 'production-secrets'"
"List all secrets in the 'production-secrets' scope"
```

### SQL & Analytics

**SQL Warehouses**

```
"Create a SQL warehouse named 'analytics-warehouse' with size 'Medium'"
"Start the SQL warehouse 'analytics-warehouse'"
"List all SQL warehouses and their current states"
```

### Code Execution

**Execute Spark Command**

```
"Create an execution context on cluster 'my-cluster' and run this Python code:
df = spark.read.table('catalog.schema.sales')
print(df.count())"
```
