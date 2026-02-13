# Development Scripts

Scripts for testing and developing the MCP server.

## Quick Reference

| Script | Purpose | Environment |
|--------|---------|-------------|
| `query_remote.sh` | Test deployed app (interactive OAuth) | Databricks App |
| `start_server.sh` | Start local dev server | `localhost:8000` |
| `generate_oauth_token.py` | Generate OAuth tokens | Any |

## Deployment

### Quick Deploy (CLI Asset Bundle)

From the repo root:

```bash
bash scripts/deploy_bundle.sh dev
```

Select option `2` to deploy this app, or `3` to deploy both apps.

### Interactive Deploy (Notebook SDK)

From the repo root, open and run: [notebooks/04_deploy_dft_mcp_wheel.ipynb](../../../../notebooks/04_deploy_dft_mcp_wheel.ipynb)

Customize to deploy this app by updating:
- `REPO_DIR` to `custom_mcps/mcp-server-hello-world`
- `APP_NAME` to `mcp-server-hello-world` or your preferred name

## Testing

### Local Testing
```bash
./scripts/dev/start_server.sh  # Terminal 1
```

```python
from databricks_mcp import DatabricksMCPClient
mcp_client = DatabricksMCPClient(
    server_url="http://localhost:8000"
)
# List available MCP tools
print(mcp_client.list_tools())
```

### Remote Testing
```bash
# Interactive (walks you through OAuth)
./scripts/dev/query_remote.sh

Tests: All tools with user-level OAuth authentication

## Development Workflow

1. Add tool to `server/tools.py`
3. Test locally: Either follow the local testing above or run the integration tests
4. Deploy to Databricks Apps
5. Test deployed: `./scripts/dev/query_remote.sh`

