# How To Set Up

This repo contains two MCP server examples and sample notebooks.

## Prerequisites

- Python 3.11+
- Databricks workspace access
- [uv](https://github.com/astral-sh/uv) (recommended)

## Databricks Workspace Options

If you do not already have a workspace, you can use one of these options:

### Databricks Free Edition

- Sign up and create a free workspace: https://www.databricks.com/try-databricks
- Use the workspace URL when running notebooks and when configuring the Databricks CLI profile.

### Your Own Workspace

- Use your existing Databricks workspace URL and credentials.
- If you need to create a new workspace, follow the cloud provider setup guide:
	- AWS: https://docs.databricks.com/en/getting-started/overview.html
	- Azure: https://learn.microsoft.com/en-us/azure/databricks/getting-started/
	- GCP: https://docs.gcp.databricks.com/en/getting-started/index.html

## Set Up A Server

Choose one of the server folders and install dependencies with uv.

### DfE MCP server

```bash
cd custom_mcps/dft-mcp-server
uv sync
```

### Hello-world MCP server

```bash
cd custom_mcps/mcp-server-hello-world
uv sync
```

If you prefer pip for the hello-world server, see its README for the venv and `requirements.txt` steps.

## Databricks CLI Profile Setup

If you plan to deploy or use OAuth scripts, configure the Databricks CLI:

```bash
# Install or upgrade the CLI
brew install databricks

# Configure a profile named "default"
databricks configure
```

Use your workspace URL and a personal access token when prompted.

### Use A Named Profile

If you want a profile other than `default`, pass `--profile`:

```bash
databricks configure --profile my-workspace
```

Then use that profile in CLI commands:

```bash
databricks apps list --profile my-workspace
```

For scripts that accept a profile (like `scripts/dev/query_remote.sh`), select the same profile when prompted.

## Notebooks

The sample notebooks live in `notebooks/`. Run them in a Databricks workspace.
