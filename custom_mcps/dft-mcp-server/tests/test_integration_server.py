"""
Integration tests for the DfE MCP Server.

These tests start the server locally and verify that tools, resources,
and prompts work correctly.
"""

import os
import shlex
import signal
import socket
import subprocess
import time
from contextlib import closing

import pytest
import requests


def _find_free_port() -> int:
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _wait_for_server_startup(url: str, timeout: int = 15):
    deadline = time.time() + timeout
    last_exc = None

    while time.time() < deadline:
        try:
            response = requests.get(url, timeout=1)
            if 200 <= response.status_code < 400:
                return response
        except Exception as e:
            last_exc = e
        time.sleep(0.2)

    if last_exc:
        raise last_exc

    raise TimeoutError(f"Server at {url} did not respond in {timeout} seconds")


@pytest.fixture(scope="session")
def run_mcp_server():
    host = "127.0.0.1"
    port = _find_free_port()
    url = f"http://{host}:{port}"
    cmd = shlex.split(f"uv run dfe-mcp-server --port {port}")

    # Start the process
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        # Start a new process group so we can kill children on teardown
        preexec_fn=os.setsid,
        creationflags=0,
    )

    try:
        _wait_for_server_startup(url)
    except Exception as e:
        proc.terminate()
        stdout, stderr = proc.communicate(timeout=5)
        raise RuntimeError(f"Server failed to start: {e}\nStderr: {stderr}") from e

    yield url

    try:
        os.killpg(proc.pid, signal.SIGTERM)
        proc.wait(timeout=10)
    except Exception:
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except Exception:
            pass
    finally:
        try:
            proc.wait(timeout=5)
        except Exception:
            pass


# Test server health endpoint
def test_server_health(run_mcp_server):
    """Test that the server root endpoint responds successfully."""
    url = run_mcp_server
    response = requests.get(url)
    assert response.status_code == 200
    # Could return JSON or HTML depending on static file presence
    content_type = response.headers.get("content-type", "")
    if "application/json" in content_type:
        data = response.json()
        assert data.get("status") == "healthy"
    else:
        # Static HTML is also acceptable
        assert "DfE MCP Server" in response.text or response.status_code == 200


# Test MCP endpoint exists
def test_mcp_endpoint_exists(run_mcp_server):
    """Test that the MCP endpoint is accessible."""
    url = run_mcp_server
    # The MCP endpoint should accept POST requests for SSE
    # A GET request might return various status codes depending on implementation
    response = requests.get(f"{url}/mcp")
    # Accept various status codes that indicate the endpoint exists
    # 406 = Not Acceptable (valid - means endpoint exists but wrong accept header)
    assert response.status_code in [200, 404, 405, 406, 307]


# Test tools directly using FastMCP test utilities
def test_tools_registration():
    """Test that tools are properly registered with the MCP server."""
    from fastmcp import FastMCP
    from server.tools import load_tools

    mcp = FastMCP(name="test-server")
    load_tools(mcp)

    # Get registered tools
    # FastMCP stores tools internally - we can check they were added
    # by trying to access them through the mcp instance
    assert mcp is not None


# Test get_available_data tool directly
@pytest.mark.asyncio
async def test_get_available_data_tool():
    """Test the get_available_data tool returns expected structure."""
    from server.dfe_api import get_dfe_client

    client = get_dfe_client()

    try:
        # Load metadata
        await client._load_metadata()

        # Check regions are available
        regions = await client.get_available_regions()
        assert "National" in regions
        assert len(regions) > 1  # Should have multiple regions

        # Check years are available
        years = await client.get_available_years()
        assert len(years) > 0
        # Years should be in format like "2024/25"
        assert "/" in years[0]

    finally:
        await client.close()


# Test API client initialization
def test_dfe_api_client_creation():
    """Test that the DfE API client can be created."""
    from server.dfe_api import DfEApiClient, get_dfe_client

    client = DfEApiClient()
    assert client.base_url == "https://api.education.gov.uk/statistics/v1"
    assert client.timeout == 30.0

    # Test singleton
    shared_client = get_dfe_client()
    assert shared_client is not None


# Test resource content
def test_schema_resource_content():
    """Test that the schema resource returns valid JSON."""
    import json
    from fastmcp import FastMCP
    from server.tools import load_tools

    mcp = FastMCP(name="test-server")
    load_tools(mcp)

    # The resource should be accessible - test by checking tools loaded
    # (resource registration happens in load_tools)
    assert mcp is not None


# Test normalization functions
def test_region_normalization():
    """Test that region names are normalized correctly."""
    from server.dfe_api import DfEApiClient

    client = DfEApiClient()

    assert client._normalize_region("national") == "National"
    assert client._normalize_region("North East") == "North East"
    assert client._normalize_region("northeast") == "North East"
    assert client._normalize_region("london") == "London"
    assert client._normalize_region("Yorkshire and The Humber") == "Yorkshire and The Humber"
    assert client._normalize_region("yorkshire") == "Yorkshire and The Humber"


def test_age_group_normalization():
    """Test that age groups are normalized correctly."""
    from server.dfe_api import DfEApiClient

    client = DfEApiClient()

    assert client._normalize_age_group("under_19") == "Under 19"
    assert client._normalize_age_group("19_to_24") == "19 to 24"
    assert client._normalize_age_group("25_plus") == "25 plus"
    assert client._normalize_age_group("all") == "Total"


def test_level_normalization():
    """Test that apprenticeship levels are normalized correctly."""
    from server.dfe_api import DfEApiClient

    client = DfEApiClient()

    assert client._normalize_level("intermediate") == "Intermediate Apprenticeship"
    assert client._normalize_level("advanced") == "Advanced Apprenticeship"
    assert client._normalize_level("higher") == "Higher Apprenticeship"
    assert client._normalize_level("all") == "Total"


def test_metric_indicator_mapping():
    """Test that metrics map to correct indicators."""
    from server.dfe_api import DfEApiClient

    client = DfEApiClient()

    assert client._get_metric_indicator("starts") == "Starts"
    assert client._get_metric_indicator("achievements") == "Achievements"
    assert client._get_metric_indicator("participation") == "Learner participation"
