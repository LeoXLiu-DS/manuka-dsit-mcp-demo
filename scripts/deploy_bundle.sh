#!/bin/bash
set -euo pipefail

if [ "${1:-}" = "-h" ] || [ "${1:-}" = "--help" ]; then
	echo "Usage: $0 [target] [--no-start] [--force] [--auto-approve]"
	echo "  target         Bundle target name (default: dev)"
	echo "  --no-start     Skip starting apps after deploy"
	echo "  --force        Force-override Git branch validation"
	echo "  --auto-approve Skip interactive approvals"
	exit 0
fi

TARGET="${1:-dev}"
NO_START="false"
FORCE_DEPLOY="false"
AUTO_APPROVE="false"

for arg in "${@:2}"; do
	case "$arg" in
		--no-start) NO_START="true" ;;
		--force) FORCE_DEPLOY="true" ;;
		--auto-approve) AUTO_APPROVE="true" ;;
	esac
done

echo "Deploying Databricks Asset Bundle (target: $TARGET)"

DEPLOY_ARGS=("-t" "$TARGET")
if [ "$FORCE_DEPLOY" = "true" ]; then
	DEPLOY_ARGS+=("--force")
fi
if [ "$AUTO_APPROVE" = "true" ]; then
	DEPLOY_ARGS+=("--auto-approve")
fi

databricks bundle validate -t "$TARGET"
databricks bundle deploy "${DEPLOY_ARGS[@]}"

echo "Deploying app source from bundle path"
BUNDLE_NAME="manuka-dsit-mcp-demo"
CURRENT_USER=$(databricks current-user me -o json | python -c "import json, sys; print(json.load(sys.stdin)['userName'])")
BUNDLE_ROOT="/Workspace/Users/${CURRENT_USER}/.bundle/${BUNDLE_NAME}/${TARGET}"
DFT_SRC="${BUNDLE_ROOT}/files/custom_mcps/dft-mcp-server"
HELLO_SRC="${BUNDLE_ROOT}/files/custom_mcps/mcp-server-hello-world"

echo "Select app to deploy:"
echo "  1) dft-mcp-server"
echo "  2) mcp-server-hello-world"
echo "  3) both"
read -p "Choice [3]: " DEPLOY_CHOICE
DEPLOY_CHOICE="${DEPLOY_CHOICE:-3}"

DEPLOY_DFT="false"
DEPLOY_HELLO="false"
case "$DEPLOY_CHOICE" in
	1) DEPLOY_DFT="true" ;;
	2) DEPLOY_HELLO="true" ;;
	3) DEPLOY_DFT="true"; DEPLOY_HELLO="true" ;;
	*)
		echo "Invalid choice: $DEPLOY_CHOICE"
		exit 1
		;;
esac

if [ "$DEPLOY_DFT" = "true" ]; then
	databricks apps deploy dft-mcp-server --source-code-path "$DFT_SRC"
fi
if [ "$DEPLOY_HELLO" = "true" ]; then
	databricks apps deploy mcp-server-hello-world --source-code-path "$HELLO_SRC"
fi

if [ "$NO_START" = "true" ]; then
	echo "Skipping app start"
else
	echo "Select app to start:"
	echo "  1) dft-mcp-server"
	echo "  2) mcp-server-hello-world"
	echo "  3) both"
	read -p "Choice [3]: " START_CHOICE
	START_CHOICE="${START_CHOICE:-3}"

	start_if_stopped() {
		local app_name="$1"
		local state
		state=$(databricks apps get "$app_name" -o json | python -c "import json, sys; print(json.load(sys.stdin)['compute_status']['state'])")
		if [ "$state" = "ACTIVE" ]; then
			echo "Skipping start for $app_name (compute already ACTIVE)"
			return 0
		fi
		databricks apps start "$app_name"
	}

	case "$START_CHOICE" in
		1)
			start_if_stopped dft-mcp-server
			;;
		2)
			start_if_stopped mcp-server-hello-world
			;;
		3)
			start_if_stopped dft-mcp-server
			start_if_stopped mcp-server-hello-world
			;;
		*)
			echo "Invalid choice: $START_CHOICE"
			exit 1
			;;
	esac
fi

echo "Done"
