# Manuka DSIT MCP Demo

## Overview


## Features
* End-to-end MCP sever creation examples
* Sample notebooks and scripts for data processing
* Documentation and usage guides

## Requirements
* Databricks workspace access

## Setup Instructions

## Usage
* Run the sample notebooks to explore data pipelines and integration workflows.
* Modify scripts and configurations to suit your own data and requirements.
* Refer to the documentation for detailed guides and examples.

## Deployment Methods

### Option 1: CLI Asset Bundle (Recommended for Quick Deploy)

Deploy both MCP apps with a single command using the Databricks CLI:

```bash
bash scripts/deploy_bundle.sh dev
```

Features:
- One-command deployment of all apps
- Uses [databricks.yml](databricks.yml) configuration
- App selection prompt (deploy one or both)
- Optional flags: `--force`, `--auto-approve`, `--no-start`
- Requires Databricks CLI and authentication

**Usage Examples:**
```bash
# Deploy with interactive prompts
bash scripts/deploy_bundle.sh dev

# Auto-approve all prompts
bash scripts/deploy_bundle.sh dev --auto-approve

# Deploy without starting apps (manual start later)
bash scripts/deploy_bundle.sh dev --no-start
```

### Option 2: Databricks Notebook SDK (For Interactive Deployment)

Deploy apps interactively from a Databricks notebook using the Python SDK:

1. Open notebook: [04_deploy_dft_mcp_wheel.ipynb](notebooks/04_deploy_dft_mcp_wheel.ipynb)
2. Run cells in order:
   - Cell 1: Configuration (customize app name and paths)
   - Cell 2: SDK upgrade and Python restart
   - Cell 3: Sync repo, upload files, create and deploy app
3. Monitor deployment progress in notebook output

Features:
- Deploy from Databricks notebook UI
- Interactive configuration and customization
- Real-time deployment status and logs
- Good for testing and development workflows
- Requires workspace write access

## Architecture Overview

### Deployment Architecture

Both deployment methods follow the same core process but use different entry points:

```
┌─────────────────────────────────────────────────────────────────┐
│                     MCP Server Source Code                       │
│         (Python app in custom_mcps/dft-mcp-server)               │
└────────────────┬────────────────────────────────────────────────┘
                 │
         ┌───────┴──────────────────┐
         │                          │
    ┌────▼────┐          ┌──────────▼────────┐
    │ CLI     │          │ Databricks        │
    │ Bundle  │          │ Notebook          │
    │         │          │ (Python SDK)      │
    └────┬────┘          └──────────┬────────┘
         │                          │
    ┌────▼──────────────────────────▼──────┐
    │   Databricks APIs                    │
    │ • Repos API (sync source)            │
    │ • Workspace API (upload)             │
    │ • Apps API (deploy)                  │
    └────┬───────────────────────────────┘
         │
    ┌────▼────────────────┐
    │  Databricks Apps    │

    │  (Live HTTP Server) │
    └─────────────────────┘
```

### Component Descriptions

| Component | Role | Details |
|-----------|------|---------|
| **Source Code** | MCP server implementation | FastAPI + FastMCP, includes tools/resources |
| **CLI Bundle** | Infrastructure-as-code | `databricks.yml` defines app config and targets |
| **Notebook SDK** | Dynamic deployment engine | Python SDK controls Repos, Workspace, Apps APIs |
| **Databricks Repos** | Git synchronization | Syncs GitHub repo to `/Workspace/Repos/` |
| **Workspace API** | File management | Uploads source files to workspace paths |
| **Apps API** | App lifecycle | Creates apps, manages deployments, tracks status |
| **Databricks Apps** | Runtime environment | Runs HTTP server, forwards requests via OAuth |

### CLI Asset Bundle Workflow

```
1. Workspace (local or terminal)
   │
   └─→ bash scripts/deploy_bundle.sh dev
       │
       └─→ databricks CLI
           ├─ Validates databricks.yml
           ├─ Reads app configuration
           ├─ Syncs app source code
           └─ Deploys to Databricks Apps
           
2. Databricks Apps (running)
   │
   ├─ App 1: dft-mcp-server
   │  └─ HTTP endpoint ready
   │
   └─ App 2: mcp-server-hello-world
      └─ HTTP endpoint ready
```

**Best for**: CI/CD pipelines, production deployments, one-click automation

### Notebook SDK Workflow

```
1. Databricks Notebook (browser/workspace)
   │
   └─→ Cell 1: Configure paths & app name
       │
       └─→ Cell 2: Upgrade SDK, restart Python
           │
           └─→ Cell 3: Deploy
               ├─ Repos API
               │  └─ Sync GitHub repo to workspace
               │
               ├─ Workspace API
               │  └─ Upload source files (with parent dir tracking)
               │
               └─ Apps API
                  ├─ Create app if missing
                  └─ Deploy & wait for completion
                  
2. Real-time output
   │
   ├─ Status messages
   ├─ Error handling
   └─ Deployment completion status
```

**Best for**: Development, testing, interactive workflows, debugging

### Data Flow

```
GitHub Repository
    │
    ├─ (CLI) Local git clone
    │        │
    │        └─→ databricks.yml config
    │            └─→ CLI bundle deploy
    │
    └─ (SDK) Databricks Repos API  
             │
             └─→ Git sync to /Workspace/Repos/
                 │
                 ├─ Workspace API: Upload files
                 │  └─→ /Workspace/Users/<user>/dft-mcp-server-app/
                 │
                 └─ Apps API: Create & Deploy
                    └─→ Databricks Apps (live)
```

## Project Structure
* `notebooks/` - Sample Databricks notebooks
* `custom_mcps/` - Sample custom mcp server code
* `README.md` - Project documentation

## Contact
For questions or support, please contact the project maintainer at xuanang.leo.liu@gmail.com.