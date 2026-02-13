#!/bin/bash
set -euo pipefail

# Usage: build_wheel_bundle.sh [-a app-name] [-p profile] [-w workspace-path]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"

DEFAULT_APP_NAME="dft-mcp-server"
DEFAULT_PROFILE="default"

APP_NAME=""
PROFILE=""
WS_PATH=""

while getopts ":a:p:w:h" opt; do
  case "$opt" in
    a) APP_NAME="$OPTARG" ;;
    p) PROFILE="$OPTARG" ;;
    w) WS_PATH="$OPTARG" ;;
    h)
      echo "Usage: $0 [-a app-name] [-p profile] [-w workspace-path]"
      exit 0
      ;;
    \?)
      echo "Error: invalid option -$OPTARG"
      exit 1
      ;;
    :)
      echo "Error: option -$OPTARG requires an argument"
      exit 1
      ;;
  esac
done

if [ -z "$APP_NAME" ]; then
  read -p "Databricks app name [${DEFAULT_APP_NAME}]: " APP_NAME
  APP_NAME="${APP_NAME:-$DEFAULT_APP_NAME}"
fi

if [ -z "$PROFILE" ]; then
  read -p "Databricks CLI profile [${DEFAULT_PROFILE}]: " PROFILE
  PROFILE="${PROFILE:-$DEFAULT_PROFILE}"
fi

if [ -z "$WS_PATH" ]; then
  read -p "Workspace upload path (e.g., /Workspace/Users/you@company.com/dft-mcp-server-app): " WS_PATH
fi

if [ -z "$WS_PATH" ]; then
  echo "Error: workspace path is required"
  exit 1
fi

cd "$PROJECT_ROOT"

echo "Step 1: Build wheel"
python -m pip install --upgrade build
python -m build --wheel

WHEEL_FILE="$(ls -t dist/dft_mcp_server-*.whl | head -n 1)"
if [ -z "$WHEEL_FILE" ]; then
  echo "Error: wheel file not found in dist/"
  exit 1
fi

cp "$WHEEL_FILE" deploy/wheel_app/dft_mcp_server.whl

echo "Step 2: Create app if needed"
if ! databricks apps get "$APP_NAME" --profile "$PROFILE" >/dev/null 2>&1; then
  databricks apps create "$APP_NAME" --profile "$PROFILE"
fi

echo "Step 3: Upload app bundle"
databricks workspace import-dir deploy/wheel_app "$WS_PATH" --profile "$PROFILE"

echo "Step 4: Deploy app"
databricks apps deploy "$APP_NAME" --profile "$PROFILE" --source-code-path "$WS_PATH"

echo "Done: $APP_NAME deployed from $WS_PATH"
