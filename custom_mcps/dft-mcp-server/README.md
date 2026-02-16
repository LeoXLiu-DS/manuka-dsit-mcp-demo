# DfT MCP Server

An MCP (Model Context Protocol) server for Department for Transport NaPTAN data, built with FastMCP and deployable on Databricks Apps.

## Overview

This server wraps the [DfT NaPTAN API](https://naptan.api.dft.gov.uk/swagger) and exposes transport access point data through the MCP protocol. It enables AI agents to query:

- **Transport coverage** - Access points by region/locality
- **Access point counts** - Statistics by transport type
- **Available data** - Regions, transport types, stop types

Data covers all public transport access points across Great Britain (England, Scotland, Wales).

## Features

- 3 MCP tools for querying and discovering transport data
- 1 MCP resource with schema/metadata
- 1 MCP prompt for guided transport analysis
- Async HTTP client for NaPTAN API
- Ready for Databricks Apps deployment

## Quick Start

### Prerequisites

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) (recommended)

### Installation

```bash
# Install dependencies
uv sync
```

### Run Locally

```bash
# Using the convenience script
./scripts/dev/start_server.sh

# Or directly
uv run dft-mcp-server
```

Server starts at `http://localhost:8000`.

### Run Tests

```bash
uv run pytest tests/
```

## MCP Primitives

### Tools

| Tool | Description |
|------|-------------|
| `get_transport_coverage` | Get transport access points for a region/locality |
| `count_access_points` | Count transport nodes by type in a region |
| `get_available_data` | Discover available regions, transport types, stop types |

### Resources

| URI | Description |
|-----|-------------|
| `dft://schema/transport-access-points` | Schema and metadata for NaPTAN data |

### Prompts

| Name | Description |
|------|-------------|
| `transport-accessibility-analysis` | Guided transport accessibility analysis for a region |

## Example Usage

### Discover Available Data

```python
get_available_data(data_type="all")
```

### Count Transport in London

```python
count_access_points(region="London")
```

### Get Rail Stations in Yorkshire

```python
get_transport_coverage(
    region="Yorkshire and The Humber",
    transport_type="rail"
)
```

### Search for Transport in Sheffield

```python
get_transport_coverage(
    locality="Sheffield",
    limit=50
)
```

### Count Bus Stops in North East

```python
count_access_points(
    region="North East",
    transport_type="bus"
)
```

## Data Coverage

- **Geography**: England (9 regions), Scotland, Wales
- **Transport Types**: Bus, Rail, Metro, Tram, Air, Ferry, Taxi
- **Stop Types**: BST, BCS, RLY, PLT, MET, AIR, FER, TXR, and more
- **Data Source**: NaPTAN (National Public Transport Access Nodes)
- **Updates**: Continuous (live dataset)

## Deployment to Databricks Apps

1. Configure `app.yaml` if needed
2. Deploy using Databricks CLI:

```bash
databricks apps create dft-mcp-server --source-code-path .
databricks apps deploy dft-mcp-server
```

3. Test via AI Playground or MCP client

## Project Structure

```
dft-mcp-server/
├── server/
│   ├── app.py          # FastAPI + FastMCP setup
│   ├── main.py         # Entry point
│   ├── tools.py        # MCP tools, resources, prompts
│   ├── naptan_api.py   # NaPTAN API client
│   └── utils.py        # Auth helpers
├── scripts/dev/        # Development scripts
├── tests/              # Integration tests
├── pyproject.toml      # Dependencies
├── app.yaml            # Databricks Apps config
└── CLAUDE.md           # AI assistant context
```

## License

This project uses data from the DfT NaPTAN API under the [Open Government Licence v3.0](https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/).

## Related

- [NaPTAN API Documentation](https://naptan.api.dft.gov.uk/swagger)
- [Model Context Protocol](https://modelcontextprotocol.io)
- [FastMCP](https://github.com/jlowin/fastmcp)
- [Databricks Apps](https://docs.databricks.com/en/dev-tools/databricks-apps/)
