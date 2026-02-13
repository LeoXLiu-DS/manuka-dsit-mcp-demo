# Databricks notebook source
# MAGIC %pip install --upgrade databricks-sdk

# COMMAND ----------

dbutils.library.restartPython()

# COMMAND ----------

dbutils.widgets.text("catalog", "dsit_mcp", "Catalog")
dbutils.widgets.text("schema", "02_silver", "Schema")
dbutils.widgets.text("warehouse_id", "0999489443c958fe", "Warehouse ID")

# COMMAND ----------

# MAGIC %md
# MAGIC Replace warehouse_id with the ID in free edition. Navigate to the Compute tab, then to SQL warehouses. Click on "Serverless Starter Warehouse" and copy the ID in brackets the name field.

# COMMAND ----------

from databricks.sdk import WorkspaceClient
from databricks.sdk.service import catalog as catalog_service

w = WorkspaceClient()

catalog = dbutils.widgets.get("catalog")
schema = dbutils.widgets.get("schema")
warehouse_id = dbutils.widgets.get("warehouse_id")

# COMMAND ----------

#check if warehouse exists else raise error
try:
  w.warehouses.get(id=warehouse_id)
except:
  raise Exception(f"warehouse {warehouse_id} does not exist")

# COMMAND ----------

# DBTITLE 1,Cell 4
import json

# Define the Genie space configuration with columns sorted alphabetically
space_config = {
    "version": 2,
    "data_sources": {
        "tables": [
            {
                "identifier": f"`{catalog}`.`{schema}`.silver_pupil_dest_data",
                "column_configs": sorted([
                    { "column_name": "admission_policy", "enable_format_assistance": True, "enable_entity_matching": True },
                    { "column_name": "apprenticeship_level_2", "enable_format_assistance": True, "enable_entity_matching": True },
                    { "column_name": "apprenticeship_level_3", "enable_format_assistance": True, "enable_entity_matching": True },
                    { "column_name": "apprenticeship_level_4_plus", "enable_format_assistance": True, "enable_entity_matching": True },
                    { "column_name": "apprenticeships", "enable_format_assistance": True, "enable_entity_matching": True },
                    { "column_name": "breakdown", "enable_format_assistance": True, "enable_entity_matching": True },
                    { "column_name": "breakdown_topic", "enable_format_assistance": True, "enable_entity_matching": True },
                    { "column_name": "cohort", "enable_format_assistance": True, "enable_entity_matching": True },
                    { "column_name": "cohort_level", "enable_format_assistance": True, "enable_entity_matching": True },
                    { "column_name": "cohort_level_group", "enable_format_assistance": True, "enable_entity_matching": True },
                    { "column_name": "country_code", "enable_format_assistance": True, "enable_entity_matching": True },
                    { "column_name": "country_name", "enable_format_assistance": True, "enable_entity_matching": True },
                    { "column_name": "data_type", "enable_format_assistance": True, "enable_entity_matching": True },
                    { "column_name": "destination_unknown", "enable_format_assistance": True, "enable_entity_matching": True },
                    { "column_name": "education", "enable_format_assistance": True, "enable_entity_matching": True },
                    { "column_name": "employment", "enable_format_assistance": True, "enable_entity_matching": True },
                    { "column_name": "entry_gender", "enable_format_assistance": True, "enable_entity_matching": True },
                    { "column_name": "further_ed_level_1", "enable_format_assistance": True, "enable_entity_matching": True },
                    { "column_name": "further_ed_level_2", "enable_format_assistance": True, "enable_entity_matching": True },
                    { "column_name": "further_ed_level_3", "enable_format_assistance": True, "enable_entity_matching": True },
                    { "column_name": "further_education", "enable_format_assistance": True, "enable_entity_matching": True },
                    { "column_name": "geographic_level", "enable_format_assistance": True, "enable_entity_matching": True },
                    { "column_name": "higher_education", "enable_format_assistance": True, "enable_entity_matching": True },
                    { "column_name": "institution_group", "enable_format_assistance": True, "enable_entity_matching": True },
                    { "column_name": "institution_type", "enable_format_assistance": True, "enable_entity_matching": True },
                    { "column_name": "la_name", "enable_format_assistance": True, "enable_entity_matching": True },
                    { "column_name": "lad_code", "enable_format_assistance": True, "enable_entity_matching": True },
                    { "column_name": "lad_name", "enable_format_assistance": True, "enable_entity_matching": True },
                    { "column_name": "local_authority_selection_status", "enable_format_assistance": True, "enable_entity_matching": True },
                    { "column_name": "new_la_code", "enable_format_assistance": True, "enable_entity_matching": True },
                    { "column_name": "not_sustained_destination", "enable_format_assistance": True, "enable_entity_matching": True },
                    { "column_name": "old_la_code", "enable_format_assistance": True, "enable_entity_matching": True },
                    { "column_name": "overall", "enable_format_assistance": True, "enable_entity_matching": True },
                    { "column_name": "pcon_code", "enable_format_assistance": True, "enable_entity_matching": True },
                    { "column_name": "pcon_name", "enable_format_assistance": True, "enable_entity_matching": True },
                    { "column_name": "region_code", "enable_format_assistance": True, "enable_entity_matching": True },
                    { "column_name": "region_name", "enable_format_assistance": True, "enable_entity_matching": True },
                    { "column_name": "school_laestab", "enable_format_assistance": True, "enable_entity_matching": True },
                    { "column_name": "school_name", "enable_format_assistance": True, "enable_entity_matching": True },
                    { "column_name": "school_urn", "enable_format_assistance": True, "enable_entity_matching": True },
                    { "column_name": "time_identifier", "enable_format_assistance": True, "enable_entity_matching": True },
                    { "column_name": "time_period", "enable_format_assistance": True, "enable_entity_matching": True },
                    { "column_name": "version", "enable_format_assistance": True, "enable_entity_matching": True }
                ], key=lambda x: x["column_name"])
            }
        ]
    },
}

# Serialize to JSON string
serialized_space = json.dumps(space_config)


# COMMAND ----------

# DBTITLE 1,Cell 5
# Create the Genie space
genie_space = w.genie.create_space(
    description="Space for analyzing Pupil Destination data",
    warehouse_id=warehouse_id,
    serialized_space=serialized_space,
    title="Pupil Destinations"
)

print(f"Created Genie space with ID: {genie_space.space_id}")

# COMMAND ----------

# DBTITLE 1,Cell 7
import json

# Define the Genie space configuration for silver_stops
space_config_stops = {
    "version": 2,
    "data_sources": {
        "tables": [
            {
                "identifier": f"`{catalog}`.`{schema}`.silver_stop_codes",
                "column_configs": [
                    { "column_name": "Description", "enable_format_assistance": True, "enable_entity_matching": True },
                    { "column_name": "StopType", "enable_format_assistance": True, "enable_entity_matching": True },
                    { "column_name": "id", "enable_format_assistance": True, "enable_entity_matching": True }
                ]
            },
            {
                "identifier": f"`{catalog}`.`{schema}`.silver_stops",
                "column_configs": [
                    { "column_name": "ATCOCode", "enable_format_assistance": True, "enable_entity_matching": True },
                    { "column_name": "AdministrativeAreaCode", "enable_format_assistance": True, "enable_entity_matching": True },
                    { "column_name": "Bearing", "enable_format_assistance": True, "enable_entity_matching": True },
                    { "column_name": "BusStopType", "enable_format_assistance": True, "enable_entity_matching": True },
                    { "column_name": "CommonName", "enable_format_assistance": True, "enable_entity_matching": True },
                    { "column_name": "CreationDateTime", "enable_format_assistance": True, "enable_entity_matching": True },
                    { "column_name": "GridType", "enable_format_assistance": True, "enable_entity_matching": True },
                    { "column_name": "Indicator", "enable_format_assistance": True, "enable_entity_matching": True },
                    { "column_name": "LocalityCentre", "enable_format_assistance": True, "enable_entity_matching": True },
                    { "column_name": "LocalityName", "enable_format_assistance": True, "enable_entity_matching": True },
                    { "column_name": "Modification", "enable_format_assistance": True, "enable_entity_matching": True },
                    { "column_name": "ModificationDateTime", "enable_format_assistance": True, "enable_entity_matching": True },
                    { "column_name": "NaptanCode", "enable_format_assistance": True, "enable_entity_matching": True },
                    { "column_name": "NptgLocalityCode", "enable_format_assistance": True, "enable_entity_matching": True },
                    { "column_name": "ParentLocalityName", "enable_format_assistance": True, "enable_entity_matching": True },
                    { "column_name": "RevisionNumber", "enable_format_assistance": True, "enable_entity_matching": True },
                    { "column_name": "Status", "enable_format_assistance": True, "enable_entity_matching": True },
                    { "column_name": "StopCodeId", "enable_format_assistance": True, "enable_entity_matching": True },
                    { "column_name": "Street", "enable_format_assistance": True, "enable_entity_matching": True },
                    { "column_name": "TimingStatus", "enable_format_assistance": True, "enable_entity_matching": True },
                    { "column_name": "Town", "enable_format_assistance": True, "enable_entity_matching": True },
                    { "column_name": "geography", "enable_format_assistance": True, "enable_entity_matching": True }
                ]
            }
        ]
    },
}

# Serialize to JSON string
serialized_space_stops = json.dumps(space_config_stops)


# COMMAND ----------

# DBTITLE 1,Cell 8
# Create the Genie space for silver_stops
genie_space_stops = w.genie.create_space(
    description="Space for analyzing stop data",
    warehouse_id=warehouse_id,
    serialized_space=serialized_space_stops,
    title="National Stops"
)

print(f"Created Genie space with ID: {genie_space_stops.space_id}")
