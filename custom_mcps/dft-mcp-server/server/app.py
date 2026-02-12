"""
FastAPI application configuration for the DfT MCP server.

This module sets up the core application by:
1. Creating and configuring the FastMCP server instance
2. Loading and registering all MCP tools
3. Setting up CORS middleware for cross-origin requests
4. Combining MCP routes with standard FastAPI routes
5. Optionally serving static files for a web frontend

The MCP (Model Context Protocol) server provides tools for querying
Department for Transport NaPTAN transport access point data.
"""

from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastmcp import FastMCP

from .tools import load_tools
from .utils import header_store

mcp_server = FastMCP(name="dft-mcp-server")

STATIC_DIR = Path(__file__).parent / "../static"

# Load and register all tools with the MCP server
# Tools are defined in server/tools.py
load_tools(mcp_server)

# Convert the MCP server to a streamable HTTP application
# This creates a FastAPI app that implements the MCP protocol over HTTP
mcp_app = mcp_server.http_app()

# ============================================================================
# FastAPI Application Setup
# ============================================================================

# Create a separate FastAPI instance for additional API endpoints
# This allows you to add custom routes alongside the MCP endpoints
app = FastAPI(
    title="DfT MCP Server",
    description="MCP Server for Department for Transport NaPTAN Data",
    version="0.1.0",
    lifespan=mcp_app.lifespan,  # Share the lifespan context with MCP app
)


@app.get("/", include_in_schema=False)
async def serve_index():
    """Serve the index page"""
    if STATIC_DIR.exists() and (STATIC_DIR / "index.html").exists():
        return FileResponse(STATIC_DIR / "index.html")
    else:
        return {
            "message": "DfT MCP Server is running",
            "status": "healthy",
            "description": "Department for Transport NaPTAN Transport Data API"
        }


# Create the final application by combining MCP routes with custom API routes
# This is the application that uvicorn will serve
combined_app = FastAPI(
    title="Combined DfT MCP App",
    routes=[
        *mcp_app.routes,  # MCP protocol routes (tools, resources, etc.)
        *app.routes,  # Your custom API routes (if any)
    ],
    lifespan=mcp_app.lifespan,  # Use MCP's lifespan for proper startup/shutdown
)

# Export the combined_app for uvicorn to import
# Usage: uvicorn server.app:combined_app


# HTML page to show when browser accesses /mcp directly
MCP_BROWSER_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DfT MCP Server - MCP Endpoint</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 2rem;
            line-height: 1.6;
            color: #333;
        }
        h1 { color: #1a365d; }
        h2 { color: #2c5282; margin-top: 2rem; }
        code {
            background: #f1f5f9;
            padding: 0.2rem 0.4rem;
            border-radius: 4px;
            font-size: 0.9em;
        }
        pre {
            background: #f1f5f9;
            padding: 1rem;
            border-radius: 8px;
            overflow-x: auto;
        }
        .success { color: #059669; }
        .info-box {
            background: #dbeafe;
            border-left: 4px solid #2563eb;
            padding: 1rem;
            margin: 1rem 0;
            border-radius: 0 8px 8px 0;
        }
        a { color: #2563eb; }
    </style>
</head>
<body>
    <h1>DfT MCP Server</h1>
    <p class="success">✓ MCP endpoint is active</p>

    <div class="info-box">
        <strong>This is an MCP (Model Context Protocol) endpoint.</strong><br>
        It uses Server-Sent Events (SSE) and requires an MCP-compatible client.
    </div>

    <h2>How to Connect</h2>

    <h3>1. Databricks AI Playground</h3>
    <p>Add this server as a tool in AI Playground to test interactively.</p>

    <h3>2. Claude Code / MCP Client</h3>
    <p>Configure your MCP client to connect to:</p>
    <pre><code>{endpoint_url}</code></pre>

    <h3>3. Programmatic Access</h3>
    <pre><code>from databricks_mcp import DatabricksMCPClient

client = DatabricksMCPClient(
    server_url="{endpoint_url}",
    workspace_client=your_workspace_client
)

# List available tools
tools = client.list_tools()

# Call a tool
result = client.call_tool("get_available_data", {{"data_type": "all"}})</code></pre>

    <h2>Available Tools</h2>
    <ul>
        <li><strong>get_transport_coverage</strong> - Get transport access points for a region/locality</li>
        <li><strong>count_access_points</strong> - Count transport nodes by type in a region</li>
        <li><strong>get_available_data</strong> - Discover available regions and transport types</li>
    </ul>

    <h2>Resources</h2>
    <ul>
        <li><code>dft://schema/transport-access-points</code> - Data schema and metadata</li>
    </ul>

    <h2>Prompts</h2>
    <ul>
        <li><strong>transport-accessibility-analysis</strong> - Guided transport analysis template</li>
    </ul>

    <p><a href="/">← Back to home</a></p>
</body>
</html>
"""


# Middleware to handle browser requests to /mcp endpoint
@combined_app.middleware("http")
async def handle_mcp_browser_request(request: Request, call_next):
    """
    Middleware to handle browser requests to /mcp endpoint.

    If a browser (without Accept: text/event-stream) hits /mcp,
    return a helpful HTML page instead of the SSE error.
    """
    # Check if this is a request to /mcp
    if request.url.path == "/mcp":
        accept_header = request.headers.get("accept", "")
        # If client doesn't accept SSE, it's likely a browser
        if "text/event-stream" not in accept_header:
            # Return helpful HTML page
            endpoint_url = str(request.url)
            html_content = MCP_BROWSER_PAGE.replace("{endpoint_url}", endpoint_url)
            return HTMLResponse(content=html_content, status_code=200)

    return await call_next(request)


# Adds middleware to capture the user token from the request headers
@combined_app.middleware("http")
async def capture_headers(request: Request, call_next):
    """Middleware to capture request headers for authentication"""
    header_store.set(dict(request.headers))
    return await call_next(request)
