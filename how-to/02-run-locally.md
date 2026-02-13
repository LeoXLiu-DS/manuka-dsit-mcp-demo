# How To Run Locally

Both servers can be run locally on port 8000 by default.

## DfE MCP server

```bash
cd custom_mcps/dft-mcp-server
./scripts/dev/start_server.sh
```

Or:

```bash
uv run dft-mcp-server
```

## Hello-world MCP server

```bash
cd custom_mcps/mcp-server-hello-world
./scripts/dev/start_server.sh
```

Or:

```bash
uv run custom-mcp-server
```

The MCP endpoint is available at `http://localhost:8000/mcp`.
