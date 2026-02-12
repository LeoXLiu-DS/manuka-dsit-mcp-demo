#!/usr/bin/env python3
"""
Test remote DfE MCP server deployed as a Databricks App.

This script tests the remote MCP server with user-level OAuth authentication,
calling tools to verify the DfE apprenticeship data functionality.

Usage:
    python query_remote.py --host <host> --token <token> --app-url <app-url>

Example:
    python query_remote.py \\
        --host https://dbc-a1b2345c-d6e7.cloud.databricks.com \\
        --token eyJr...Dkag \\
        --app-url https://dbc-a1b2345c-d6e7.cloud.databricks.com/serving-endpoints/dfe-mcp-server
"""

import argparse
import sys

from databricks.sdk import WorkspaceClient
from databricks_mcp import DatabricksMCPClient


def main():
    parser = argparse.ArgumentParser(
        description="Test remote DfE MCP server deployed as Databricks App"
    )

    parser.add_argument("--host", required=True, help="Databricks workspace URL")

    parser.add_argument("--token", required=True, help="OAuth access token")

    parser.add_argument("--app-url", required=True, help="Databricks App URL (without /mcp suffix)")

    args = parser.parse_args()

    print("=" * 70)
    print("Testing Remote DfE MCP Server - Databricks App")
    print("=" * 70)
    print(f"\nWorkspace: {args.host}")
    print(f"App URL: {args.app_url}")
    print()

    try:
        # Create WorkspaceClient with OAuth token
        print("Step 1: Creating WorkspaceClient with OAuth token...")
        workspace_client = WorkspaceClient(host=args.host, token=args.token)
        print("✓ WorkspaceClient created successfully")
        print()

        # Create MCP client
        mcp_url = f"{args.app_url}/mcp"
        print(f"Step 2: Connecting to MCP server at {mcp_url}...")
        mcp_client = DatabricksMCPClient(server_url=mcp_url, workspace_client=workspace_client)
        print("✓ MCP client connected successfully")
        print()

        # List available tools
        print("Step 3: Listing available MCP tools...")
        print("-" * 70)
        tools = mcp_client.list_tools()
        for tool in tools:
            print(f"  - {tool.name}: {tool.description[:60]}...")
        print("-" * 70)
        print(f"✓ Found {len(tools)} tools")
        print()

        # List available resources
        print("Step 4: Listing available MCP resources...")
        print("-" * 70)
        resources = mcp_client.list_resources()
        for resource in resources:
            print(f"  - {resource.uri}")
        print("-" * 70)
        print(f"✓ Found {len(resources)} resources")
        print()

        # List available prompts
        print("Step 5: Listing available MCP prompts...")
        print("-" * 70)
        prompts = mcp_client.list_prompts()
        for prompt in prompts:
            print(f"  - {prompt.name}")
        print("-" * 70)
        print(f"✓ Found {len(prompts)} prompts")
        print()

        # Test get_available_data tool
        print("Step 6: Testing get_available_data tool...")
        print("-" * 70)
        result = mcp_client.call_tool("get_available_data", {"data_type": "regions"})
        print(result)
        print("-" * 70)
        print("✓ get_available_data tool works")
        print()

        # Test search_apprenticeship_data tool
        print("Step 7: Testing search_apprenticeship_data tool...")
        print("-" * 70)
        result = mcp_client.call_tool("search_apprenticeship_data", {
            "query_type": "single_region",
            "region": "National",
            "metric": "starts"
        })
        print(result)
        print("-" * 70)
        print("✓ search_apprenticeship_data tool works")
        print()

        print("=" * 70)
        print("✓ All Tests Passed!")
        print("=" * 70)

    except Exception as e:
        print()
        print("=" * 70)
        print(f"✗ Error: {e}")
        print("=" * 70)
        sys.exit(1)


if __name__ == "__main__":
    main()
