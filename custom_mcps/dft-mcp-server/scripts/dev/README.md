# Developer Scripts

This directory contains scripts for local development and testing of the DfE MCP server.

## Deployment Scripts

### Quick Deployment to Databricks Apps

For one-click deployment from the repo root:

```bash
bash scripts/deploy_bundle.sh dev
```

This deploys using the Databricks Asset Bundle configuration ([databricks.yml](../../../../databricks.yml)).

### Notebook-Based Deployment

For interactive deployment from a Databricks notebook:

1. Open [notebooks/04_deploy_dft_mcp_wheel.ipynb](../../../../notebooks/04_deploy_dft_mcp_wheel.ipynb)
2. Run cells in order to deploy with real-time feedback
3. Customize app name and workspace paths as needed

## Testing Scripts

### `start_server.sh`

Starts the DfE MCP server locally for development.

```bash
./scripts/dev/start_server.sh
```

The server will be available at `http://localhost:8000`.

### `query_remote.sh`

Interactive script for testing a deployed DfE MCP server on Databricks Apps with OAuth authentication.

```bash
./scripts/dev/query_remote.sh
```

Follow the prompts to enter your Databricks profile and app name.

### `query_remote.py`

Python script for testing the remote MCP server. Used by `query_remote.sh` but can also be run directly:

```bash
python scripts/dev/query_remote.py \
    --host "https://your-workspace.cloud.databricks.com" \
    --token "your-oauth-token" \
    --app-url "https://your-workspace.cloud.databricks.com/serving-endpoints/dfe-mcp-server"
```

### `generate_oauth_token.py`

Generate OAuth tokens for Databricks workspace access:

```bash
python scripts/dev/generate_oauth_token.py \
    --host "https://your-workspace.cloud.databricks.com" \
    --scopes "all-apis offline_access"
```

## First-Time Setup

Make scripts executable:

```bash
chmod +x scripts/dev/*.sh
```
