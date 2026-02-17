# Manuka DSIT MCP Demo

A comprehensive demonstration of Model Context Protocol (MCP) server creation and deployment on Databricks, showcasing both Genie Space MCP servers and custom MCP servers for AI-powered data analysis.

## Overview

This repository provides end-to-end examples for creating and deploying MCP servers on Databricks, enabling AI agents to access and query organizational data through standardized protocols. The demo includes:

- **Genie Space MCP Server**: End-to-end pipeline for the creation of a conversational AI interface over structured data (UK Pupil Destinations dataset)
- **Custom MCP Server**: A purpose-built server wrapping the Department for Transport (DfT) NaPTAN API for transport access point data
- **AI Playground Integration**: Connect and test MCP servers with Databricks LLMs

This demo is designed for data practitioners, AI engineers, and anyone interested in extending AI capabilities with custom data sources using the Model Context Protocol.

## Features

✨ **Key Capabilities:**
- 🚀 End-to-end MCP server creation examples (Genie Space + Custom)
- 📊 Sample data ingestion and transformation notebooks
- 🏗️ Databricks Apps deployment for custom MCP servers
- 🤖 AI Playground integration for testing and exploration
- 📚 Comprehensive documentation and step-by-step guides

## Project Structure

```
manuka-dsit-mcp-demo/
├── notebooks/                         # Databricks notebooks for data processing
│   ├── 00_set_up.ipynb                # Catalog and schema setup
│   ├── 01_ingest_pupil_dest_data.py   # Data ingestion (Bronze layer)
│   ├── 02a_transform_bronze.ipynb     # CSV to Bronze Delta table
│   ├── 02b_transform_silver.ipynb     # Bronze -> Silver transform
│   └── 03_create_genie_space.py       # Genie Space creation script
│
├── custom_mcps/                       # Custom MCP server implementations
│   └── dft-mcp-server/                # DfT NaPTAN transport data server
│       ├── server/                    # Server source code
│       │   ├── app.py                 # FastAPI + FastMCP setup
│       │   ├── main.py                # Entry point
│       │   ├── tools.py               # MCP tools, resources, prompts
│       │   ├── naptan_api.py          # NaPTAN API client
│       │   └── utils.py               # Utility functions
│       ├── scripts/dev/               # Development scripts
│       ├── tests/                     # Integration tests
│       ├── static/                    # Static web assets
│       ├── pyproject.toml             # Python dependencies
│       ├── app.yaml                   # Databricks Apps config
│       ├── CLAUDE.md                  # AI assistant context
│       └── README.md                  # DfT MCP server documentation
│
├── README.md                          # This file - main documentation
└── .gitignore                         # Git ignore rules
```

## Requirements

### Databricks Account
- Databricks workspace (Free Tier or higher)
- Unity Catalog enabled (for Genie Spaces)

### Local Development (Optional)
- Python 3.11+
- [uv](https://github.com/astral-sh/uv) for dependency management
- Git for version control


## Setup and Usage Instructions

### Step 1: Create a Databricks Free Tier Account

If you don't already have a Databricks account, follow these steps:

1. **Navigate to Databricks Free Tier signup:**
   - Databricks Free Edition: https://www.databricks.com/learn/free-edition

2. **Sign up for a Free Tier account:**
   - Click "Sign Up for Free Edition" or "Try Databricks"
   - Fill in your email and enter verification code 
   - Or continue with your Google or Microsoft account
   - Click 'Get Free Edition' and then 'Continue' to set up your Databricks Account

### Step 2: Clone the Repository into Databricks

1. **Open your Databricks workspace**
2. **Navigate to your user folder:**
   - Click **Workspace** in the left sidebar
   - Open the **Workspace** folder
   - Click **Users**
   - Click the folder with your email address
3. **Create a Git folder:**
   - Click the **Create** button
   - Select **Git folder**
   - In the **Git repository URL** field, enter: `https://github.com/LeoXLiu-DS/manuka-dsit-mcp-demo.git`
   - Click **Create Git folder**
4. **Verify the clone:**
   - You should see the repository cloned under your user folder
   - You should see all folders: `notebooks/`, `custom_mcps/`, etc.

### Step 3: Create a Genie Space MCP Server

A Genie Space provides a natural language interface to query your data using AI. Follow these steps to create one:

#### 3.1 Prepare the Data

1. **Open the data ingestion notebook:**
   - Navigate to `/Workspace/Users/<your-username>/manuka-dsit-mcp-demo/notebooks/`
   - Open `00_set_up.ipynb`
   - Run all cells to set up the catalog and schema

2. **Ingest the Pupil Destinations dataset:**
   - Open `01_ingest_pupil_dest_data.ipynb`
   - Run all cells to download the KS5 Pupil Destinations dataset from the UK Explore Education Statistics API, extract the zip file, and store the data in the catalog created in the previous step
   - Verify data ingestion: in Catalog, check the `pupil_destination_data` volume under `dsit_mcp.01_bronze`

3. **Transform data to Bronze table:**
   - Open `02a_transform_bronze.ipynb`
   - Run all cells to read the ingested CSV file from the Bronze volume and save it as a Delta table (`bronze_pupil_dest_data`) in the `dsit_mcp.01_bronze` schema

4. **Transform data to Silver table:**
   - Open `02b_transform_silver.ipynb`
   - Run all cells to read the Bronze table, drop all-null columns, rename abbreviated column names to descriptive names (e.g. `he` → `higher_education`, `appren` → `apprenticeships`), create a Silver table with column-level comments, and write the cleaned data to `dsit_mcp.02_silver.silver_pupil_dest_data`

#### 3.2 Create the Genie Space

1. **Run the Genie Space creation script:**
   - Open `03_create_genie_space.ipynb`
   - Review the configuration:
     - Catalog: `dsit_mcp`
     - Schema: `02_silver`
   - Run all cells to create the Genie Space

2. **Verify Genie Space creation:**
   - Navigate to "Genie" in the Databricks sidebar
   - Find your newly created Genie Space named 'Pupil Destination'
   - Open the genie space and test with a sample query: "Show me apprenticeship destinations by region"



### Step 4: Create a Custom MCP Server (DfT Transport Data)

This section demonstrates deploying a custom MCP server that wraps the UK Department for Transport NaPTAN API.

#### 4.1 Deploy via Databricks Apps UI

1. **Access Databricks Apps:**
   - In your Databricks workspace, click **"Compute"** in the left sidebar
   - Then select 'Apps' tab

2. **Create a new Databricks App:**
   - Click **"Create App"** button
   - Choose **"Create a custom app"** option
   - **App name**: `mcp-dft`
   - **Description**: "Department for Transport NaPTAN MCP Server"
   - Click **Create app** button to create the app
 

#### 4.2 Deploy the Custom MCP Server

1. **Deploy the app:**
   - Once the app is successfully created, click the **Deploy** button
   - Browse to select `/Workspace/Users/<your-username>/manuka-dsit-mcp-demo/custom_mcps/dft-mcp-server`
   - Click the **Deploy** button
2. **Monitor deployment:**
   - Wait for the app status to change to **Running**

#### 4.3 Verify the Deployment

1. **Test the health endpoint:**
   - Open a browser and navigate to the App URL (without `/mcp`)
   - You should see a landing page: "DfT MCP Server is running"

2. **Review available tools:**
   - The page will list the available MCP tools:
     - `get_transport_coverage` - Query transport access points
     - `count_access_points` - Count transport nodes by type
     - `get_available_data` - Discover available data

3. **Check MCP endpoint:**
   - Navigate to `<App URL>/mcp`
   - You should see an MCP information page (not an error)

### Step 5: Connect to Databricks AI Playground

Now that both MCP servers are deployed, connect them to the AI Playground to test with LLMs.

#### 5.1 Access the AI Playground

1. **Open AI Playground:**
   - In the workspace, click **"Playground"** in the left sidebar

2. **Select a foundation model:**
   - Choose **Llama 4 Maverick** or another available model

#### 5.2 Add Genie Space MCP Server

1. Click the **"Tools"** dropdown

2. Click **Add tool**

3. Select the **MCP Servers** tab

4. Under **Genie Space MCP server**, click the dropdown, select **Pupil Destinations** and click **Save**

5. **Verify connection:**
   - The Genie Space: **Pupil Destinations** should appear in the tools MCP Servers list
   - Try a sample query such as "Show me apprenticeship destinations by region"

#### 5.3 Add Custom DfT MCP Server

1. Click **"Tools"**, click **Add tool**, and select the **MCP Servers** tab again

2. Under **MCP Servers on Databricks Apps**, click the dropdown, select **mcp-dft** and click **Save**

3. **Verify connection:**
   - The **mcp-dft** should appear in the tools MCP Servers list

#### 5.4 Test and Explore

The AI Playground will automatically route queries to the appropriate MCP server based on the prompt. Try these examples:

**Test Genie Space MCP:**
```
Prompt: "Show me the top 5 regions with the highest percentage of pupils going into apprenticeships."
```

**Test DfT MCP Server:**
```
Prompt: "How many bus stops are in the North East region?"
```

**Combined Query:**
```
Prompt: "Compare the transport accessibility (number of bus stops) with
apprenticeship outcomes for the North East region. Are areas with better
transport infrastructure seeing higher apprenticeship uptake?"
```


## Additional Resources

### Documentation
- [Model Context Protocol](https://modelcontextprotocol.io/) - Official MCP specification
- [FastMCP](https://github.com/jlowin/fastmcp) - Python framework for building MCP servers
- [Databricks Apps](https://docs.databricks.com/en/dev-tools/databricks-apps/) - Complete deployment guide
- [Databricks Genie](https://docs.databricks.com/en/genie/) - Genie Spaces documentation
- [Unity Catalog](https://docs.databricks.com/en/data-governance/unity-catalog/) - Data governance guide

### Data Sources
- [UK Pupil Destinations Data](https://explore-education-statistics.service.gov.uk/) - Department for Education
- [NaPTAN API](https://naptan.api.dft.gov.uk/swagger) - Department for Transport transport data


## Contributing

Contributions are welcome! Please feel free to:
- Report issues
- Suggest improvements
- Submit pull requests
- Share your own MCP server implementations

## License

This project uses data from:
- UK Department for Education (Open Government Licence v3.0)
- UK Department for Transport NaPTAN API (Open Government Licence v3.0)

## Contact

For questions, feedback, or support:
- **Email**: xuanang.leo.liu@gmail.com
- **GitHub Issues**: [Submit an issue](https://github.com/LeoXLiu-DS/manuka-dsit-mcp-demo/issues)
