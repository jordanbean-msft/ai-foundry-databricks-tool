# API Coverage

The OpenAPI specification (`src/azure_databricks_openapi_spec.json`) provides **66 endpoints across 12 categories**.

## Compute & Infrastructure

### Clusters API (5 endpoints)

- Create, list, get, start, stop, delete clusters

### Instance Pools API (4 endpoints)

- Manage instance pools for cost optimization

## Jobs & Execution

### Jobs API (5 endpoints)

- Create, list, run, monitor jobs

### Command Execution API (3 endpoints)

- Execute code on clusters

## Data & Storage

### DBFS API (5 endpoints)

- File system operations (list, read, write, delete, mkdir)

### Unity Catalog API (8 endpoints)

- Manage catalogs, schemas, tables

### Vector Search API (11 endpoints)

- Vector search endpoints, indexes, and queries

## Development & Dependencies

### Workspace API (4 endpoints)

- Manage notebooks and directories

### Repos API (5 endpoints)

- Git repository integrations

### Libraries API (4 endpoints)

- Install/uninstall cluster libraries

## Security & Configuration

### Secrets API (6 endpoints)

- Secret scopes and secret management

### SQL Warehouses API (6 endpoints)

- SQL compute resources

## Complete Endpoint List

See the [OpenAPI specification](../src/azure_databricks_openapi_spec.json) for complete endpoint definitions, parameters, and response schemas.
