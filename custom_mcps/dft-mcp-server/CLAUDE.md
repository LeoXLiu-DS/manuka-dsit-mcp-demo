# CLAUDE.md - DfT MCP Server

This file provides context about this project for AI assistants like Claude.

## Project Overview

This is an **MCP (Model Context Protocol) server** for Department for Transport (DfT) NaPTAN data. It wraps the NaPTAN API and exposes transport access point data through MCP tools, resources, and prompts.

**Demo Context:** This server is part of a cross-departmental data sharing demo where DWP's AI agent queries transport data from DfT to inform workforce and employment policy analysis.

**Key Concepts:**
- **MCP Server**: Exposes tools/resources/prompts via the Model Context Protocol over HTTP
- **NaPTAN API**: The underlying data source (naptan.api.dft.gov.uk)
- **Databricks Apps**: The deployment platform where this server runs

## Available MCP Primitives

### Tools (3)

| Tool | Description |
|------|-------------|
| `get_transport_coverage` | Get transport access points for a region/locality |
| `count_access_points` | Count transport nodes by type in a region |
| `get_available_data` | Discover available regions and transport types |

### Resources (1)

| Resource URI | Description |
|--------------|-------------|
| `dft://schema/transport-access-points` | Schema and metadata for NaPTAN data |

### Prompts (1)

| Prompt | Description |
|--------|-------------|
| `transport-accessibility-analysis` | Guided transport analysis template |

## Project Structure

```
dft-mcp-server/
├── server/
│   ├── app.py          # FastAPI + FastMCP setup
│   ├── main.py         # Entry point (uvicorn runner)
│   ├── tools.py        # MCP tools, resources, prompts
│   ├── naptan_api.py   # NaPTAN API client
│   └── utils.py        # Databricks auth helpers
├── scripts/
│   └── dev/
│       ├── start_server.sh         # Start server locally
│       └── query_remote.py         # Remote testing script
├── tests/
│   └── test_integration_server.py  # Integration tests
├── pyproject.toml      # Dependencies and build config
├── app.yaml            # Databricks Apps config
└── README.md
```

## Key Files

### `server/tools.py`

Contains all MCP primitives:

1. **`get_transport_coverage` tool** - Query transport access points:
   - `region`: Region name (e.g., "London", "North East")
   - `atco_code`: ATCO area code for precise filtering
   - `locality`: Locality name (e.g., "Sheffield")
   - `transport_type`: Filter by mode ("bus", "rail", "metro", etc.)
   - `limit`: Maximum results (default: 100)

2. **`count_access_points` tool** - Get aggregate counts:
   - `region`: Region name
   - `transport_type`: Optional filter by mode

3. **`get_available_data` tool** - Discovery interface:
   - `data_type`: "regions", "transport_types", "stop_types", "all"

4. **`dft://schema/transport-access-points` resource** - JSON schema with:
   - Transport type definitions
   - Stop type codes
   - Geographic coverage
   - Data quality notes

5. **`transport-accessibility-analysis` prompt** - Guided analysis template

### `server/naptan_api.py`

Async HTTP client for the NaPTAN API:
- Base URL: `https://naptan.api.dft.gov.uk`
- Returns CSV data parsed into dictionaries
- Includes ATCO code to region mapping

Key methods:
- `get_access_nodes()` - Get transport access points
- `count_access_points_by_type()` - Count by stop type
- `search_access_points()` - Search with filters

## Development Commands

```bash
# Start server locally
./scripts/dev/start_server.sh

# Or run directly
uv run uvicorn server.app:combined_app --reload --port 8001

# Run integration tests
uv run pytest tests/

# Format code
uv run ruff format .
```

## Data Available

### Regions
- England: North East, North West, Yorkshire and The Humber, East Midlands, West Midlands, East of England, London, South East, South West
- Wales
- Scotland

### Transport Types
- **bus**: Bus and coach stops, stations, bays
- **rail**: Railway stations and platforms
- **metro**: Metro and underground stations
- **tram**: Tram stops
- **air**: Airports and gates
- **ferry**: Ferry terminals
- **taxi**: Taxi ranks

### Stop Type Codes
- `BST`: On-street bus/coach stop
- `BCS`: Bus/Coach Station
- `RLY`: Railway Station
- `PLT`: Platform at Railway Station
- `MET`: Metro/Underground platform
- `AIR`: Airport
- `FER`: Ferry terminal
- `TXR`: Taxi rank

## Example Queries

```python
# Get available data
get_available_data(data_type="all")

# Count all transport in London
count_access_points(region="London")

# Count bus stops in North East
count_access_points(region="North East", transport_type="bus")

# Get rail stations in Yorkshire
get_transport_coverage(
    region="Yorkshire and The Humber",
    transport_type="rail"
)

# Search for transport in Sheffield
get_transport_coverage(locality="Sheffield", limit=50)
```

## Important Notes for AI Assistants

1. **Use `get_available_data` first** to see valid regions and transport types
2. **Bus stops dominate counts** - they typically outnumber all other types combined
3. **Metro data is limited** to areas with metro systems (London, Newcastle, etc.)
4. **ATCO codes** provide more precise filtering than region names
5. **Data is continuously updated** - NaPTAN is a live dataset

## Demo Scenarios

For the DSIT workshop demo, these queries demonstrate the server's capabilities:

1. "What transport data is available?"
   → Uses `get_available_data`

2. "How many bus stops are in the North East?"
   → Uses `count_access_points`

3. "Show me rail stations in Sheffield"
   → Uses `get_transport_coverage`

4. "Analyze transport accessibility for North East"
   → Uses `transport-accessibility-analysis` prompt

## Deployment

### Prerequisites

1. **Install Databricks CLI**:
   ```bash
   brew install databricks/tap/databricks
   ```

2. **Configure Databricks CLI profile**:
   ```bash
   databricks configure --profile dbw-ai-sandbox-usw
   ```

### Sync and Deploy

```bash
# Sync local code to Databricks workspace
databricks sync --profile dbw-ai-sandbox-usw . /Workspace/Users/leo.liu@manuka-ai.co.uk/dft-mcp-server

# Deploy the app
databricks apps deploy dft-mcp-server --profile dbw-ai-sandbox-usw --source-code-path /Workspace/Users/leo.liu@manuka-ai.co.uk/dft-mcp-server

# Check app status
databricks apps get dft-mcp-server --profile dbw-ai-sandbox-usw
```

### First-time Setup

```bash
# Create a new Databricks App
databricks apps create dft-mcp-server --profile dbw-ai-sandbox-usw \
  --description "Department for Transport MCP server"
```

## Testing with Service Principal

Credentials are stored in `/Users/leo.liu/Documents/Workspace/DSIT/.env`:

```python
from databricks.sdk import WorkspaceClient
from databricks_mcp import DatabricksMCPClient
import json

workspace_client = WorkspaceClient(
    host='https://adb-4220042800209384.4.azuredatabricks.net',
    client_id='<CLIENT_ID>',
    client_secret='<CLIENT_SECRET>'
)

mcp_client = DatabricksMCPClient(
    server_url='https://dft-mcp-server-4220042800209384.4.azure.databricksapps.com/mcp',
    workspace_client=workspace_client
)

# Test: Get available data
result = mcp_client.call_tool('get_available_data', {'data_type': 'all'})
print(result.content[0].text)

# Test: Count transport in London
result = mcp_client.call_tool('count_access_points', {'region': 'London'})
print(json.loads(result.content[0].text))
```
