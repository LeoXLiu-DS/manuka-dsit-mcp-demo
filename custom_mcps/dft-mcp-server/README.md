# DfE MCP Server

An MCP (Model Context Protocol) server for Department for Education apprenticeship statistics, built with FastMCP and deployable on Databricks Apps.

## Overview

This server wraps the [DfE Education Statistics API](https://api.education.gov.uk/statistics/docs/) and exposes apprenticeship data through the MCP protocol. It enables AI agents to query:

- **Apprenticeship starts** - Programme commencements
- **Achievements** - Completions
- **Participation** - Active apprentices

Data is available at national and regional levels, filterable by age group and apprenticeship level.

## Features

- 2 MCP tools for querying and discovering data
- 1 MCP resource with schema/metadata
- 1 MCP prompt for guided regional analysis
- Async HTTP client for DfE API
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
uv run dfe-mcp-server
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
| `search_apprenticeship_data` | Query statistics with filters (region, age, level, year) |
| `get_available_data` | Discover available regions, metrics, years |

### Resources

| URI | Description |
|-----|-------------|
| `dfe://schema/apprenticeship-statistics` | Schema and metadata |

### Prompts

| Name | Description |
|------|-------------|
| `regional-analysis` | Guided analysis for a region |

## Example Usage

### Discover Available Data

```python
get_available_data(data_type="all")
```

### Query National Starts

```python
search_apprenticeship_data(
    query_type="single_region",
    region="national",
    metric="starts"
)
```

### Compare Regions

```python
search_apprenticeship_data(
    query_type="compare_regions",
    region="North East",
    compare_to=["London", "South West"],
    level="higher"
)
```

### Regional Rankings

```python
search_apprenticeship_data(
    query_type="rankings",
    metric="starts",
    age_group="under_19",
    bottom_n=5
)
```

### Time Series

```python
search_apprenticeship_data(
    query_type="trends",
    region="North East",
    metric="starts"
)
```

## Data Coverage

- **Geography**: England (national + 9 regions)
- **Time**: 2017/18 to 2025/26
- **Metrics**: Starts, Achievements, Participation
- **Levels**: Intermediate (L2), Advanced (L3), Higher (L4+)
- **Age groups**: Under 19, 19-24, 25+

## Deployment to Databricks Apps

1. Configure `app.yaml` if needed
2. Deploy using Databricks CLI:

```bash
databricks apps create dfe-mcp-server --source-code-path .
databricks apps deploy dfe-mcp-server
```

3. Test via AI Playground or MCP client

## Project Structure

```
dfe-mcp-server/
├── server/
│   ├── app.py          # FastAPI + FastMCP setup
│   ├── main.py         # Entry point
│   ├── tools.py        # MCP tools, resources, prompts
│   ├── dfe_api.py      # DfE API client
│   └── utils.py        # Auth helpers
├── scripts/dev/        # Development scripts
├── tests/              # Integration tests
├── pyproject.toml      # Dependencies
├── app.yaml            # Databricks Apps config
└── CLAUDE.md           # AI assistant context
```

## License

This project uses data from the DfE Education Statistics API under the [Open Government Licence v3.0](https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/).

## Related

- [DfE Education Statistics API](https://api.education.gov.uk/statistics/docs/)
- [Model Context Protocol](https://modelcontextprotocol.io)
- [FastMCP](https://github.com/jlowin/fastmcp)
- [Databricks Apps](https://docs.databricks.com/en/dev-tools/databricks-apps/)
