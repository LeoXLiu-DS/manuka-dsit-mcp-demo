# Databricks notebook source
import requests, os, shutil, zipfile
from databricks.sdk import WorkspaceClient
from databricks.sdk.service import catalog as catalog_service

w = WorkspaceClient()

dbutils.widgets.text("catalog", "dsit_mcp", "Catalog")
dbutils.widgets.text("schema", "01_bronze", "Schema")

catalog = dbutils.widgets.get("catalog")
schema = dbutils.widgets.get("schema")

volume_path = f"/Volumes/{catalog}/{schema}/pupil_destination_data/"

try:
    # Create a managed volume
    w.volumes.create(
        catalog_name=catalog,
        schema_name=schema,
        name="pupil_destination_data",
        volume_type=catalog_service.VolumeType.MANAGED
    )
    print(f"Volume 'pupil_destination_data' created successfully in {catalog}.{schema}.")

except Exception as e:
    if "already exists" in str(e):
        print(f"Volume 'stop_data' already exists in {catalog}.{schema}. Proceeding with data ingestion.")
    else:
        print(f"An error occurred while creating the volume: {e}")
        raise

# stop data filtered for West Midlands region
api_url = "https://content.explore-education-statistics.service.gov.uk/api/releases/4f12d515-38a6-4bd1-b9f6-2323b5879fda/files?fromPage=ReleaseDownloads"

def download_pupil_destination_data(volume_path):
    """
    Downloads the pupil destination data from the specified API endpoint, saves it to a temporary location, and then extracts it to the specified volume path.
    """

    zip_filename = f"pupil_dest.zip"

    landing_dir = f"{volume_path}landing"
    zip_path = f"{volume_path}landing/{zip_filename}"
    os.makedirs(landing_dir, exist_ok=True)

    print(f"Starting download from {api_url}")
    # Stream download to avoid loading the whole file into memory
    with requests.get(api_url, stream=True) as resp:
        resp.raise_for_status()
        with open(zip_path, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
    print(f"Successfully downloaded zip file to: {zip_path}")


    try:
        # Unzip to temporary directory
        print(f"Extracting zip file to temporary directory...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(volume_path)

    except:
        print(f"Error occurred while extracting zip file.")
        raise

    print("Download and extraction process completed successfully!")
    return True

# Execute the download function
download_pupil_destination_data(volume_path)
