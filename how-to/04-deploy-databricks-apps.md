# How To Deploy To Databricks Apps

These servers are ready for Databricks Apps deployments.

## One-Click Deploy (Databricks Asset Bundle)

Deploy both apps with one command from the repo root:

```bash
bash scripts/deploy_bundle.sh dev
```

This uses `databricks.yml` and requires the Databricks CLI.

## Run From Databricks Notebook

Use the notebook to build and deploy from a Databricks cluster:

- [notebooks/04_deploy_dft_mcp_wheel.ipynb](../notebooks/04_deploy_dft_mcp_wheel.ipynb)

Checklist:

1) Open the notebook and read the run order in the first cell.
2) Update the repo URL in the clone step if needed.
3) Update `REPO_DIR` and `WS_PATH` to match your workspace.
4) Run the cells in order.

## DfE MCP server

### Wheel-based deploy (no repo in workspace)

Build the wheel locally, then deploy a small app bundle that installs the wheel.

```bash
cd custom_mcps/dft-mcp-server

# Build the wheel
python -m pip install build
python -m build --wheel

# Copy the wheel into the app bundle folder
cp dist/dft_mcp_server-*.whl deploy/wheel_app/dft_mcp_server.whl

# Create the app (first time)
databricks apps create dft-mcp-server

# Upload the app bundle to the workspace file system
databricks workspace import-dir deploy/wheel_app \
  /Workspace/Users/<your-user>/dft-mcp-server-app

# Deploy from the workspace path
databricks apps deploy dft-mcp-server \
  --source-code-path /Workspace/Users/<your-user>/dft-mcp-server-app
```

### Source deploy (repo in workspace)

From the server folder:

```bash
cd custom_mcps/dft-mcp-server

# Upload code to the workspace file system
databricks workspace import-dir . /Workspace/Users/<your-user>/dft-mcp-server

# Deploy updates from the workspace path
databricks apps deploy dft-mcp-server \
  --source-code-path /Workspace/Users/<your-user>/dft-mcp-server
```

## Hello-world MCP server

Deploy using the Databricks Apps UI or the Databricks CLI. See the Databricks Apps docs for detailed steps.

- https://docs.databricks.com/en/dev-tools/databricks-apps/deploy#deploy-the-app

## After Deploy

Test your app with an MCP client or in Databricks AI Playground.
