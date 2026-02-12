"""
NaPTAN (National Public Transport Access Nodes) API Client.

This module provides an async HTTP client for querying the Department for Transport
NaPTAN API, which provides data about public transport access points across Great Britain.

API Documentation: https://naptan.api.dft.gov.uk/swagger
"""

import csv
import io
from typing import Optional

import httpx


# API Configuration
BASE_URL = "https://naptan.api.dft.gov.uk"

# Default timeout for API requests (seconds) - longer due to file downloads
DEFAULT_TIMEOUT = 120.0

# ATCO Area Code to Region mapping
# ATCO codes are 3-digit prefixes used to identify administrative areas
ATCO_REGION_MAPPING = {
    # North East
    "410": "Northumberland",
    "420": "Tyne and Wear",
    "430": "Durham",
    # North West
    "050": "Merseyside",
    "060": "Greater Manchester",
    "180": "Cheshire",
    "200": "Lancashire",
    "210": "Cumbria",
    # Yorkshire and The Humber
    "370": "South Yorkshire",
    "450": "West Yorkshire",
    "320": "North Yorkshire",
    "220": "East Riding of Yorkshire",
    # East Midlands
    "270": "Derbyshire",
    "290": "Nottinghamshire",
    "260": "Leicestershire",
    "340": "Northamptonshire",
    "280": "Lincolnshire",
    # West Midlands
    "430": "West Midlands",
    "200": "Staffordshire",
    "350": "Shropshire",
    "240": "Herefordshire",
    "570": "Warwickshire",
    "560": "Worcestershire",
    # East of England
    "040": "Cambridgeshire",
    "160": "Essex",
    "230": "Hertfordshire",
    "300": "Norfolk",
    "380": "Suffolk",
    "020": "Bedfordshire",
    # London
    "490": "London",
    # South East
    "250": "Kent",
    "390": "Surrey",
    "400": "East Sussex",
    "410": "West Sussex",
    "240": "Hampshire",
    "030": "Buckinghamshire",
    "340": "Oxfordshire",
    "010": "Berkshire",
    # South West
    "120": "Devon",
    "090": "Cornwall",
    "110": "Dorset",
    "360": "Somerset",
    "190": "Gloucestershire",
    "540": "Wiltshire",
    "080": "Bristol",
    # Wales
    "511": "Cardiff",
    "512": "Swansea",
    "513": "Newport",
    "520": "South Wales",
    "530": "North Wales",
    "540": "Mid Wales",
    # Scotland
    "600": "Edinburgh",
    "609": "Glasgow",
    "610": "Aberdeen",
    "639": "Highland",
}

# Region name to ATCO codes mapping (reverse lookup with multiple codes per region)
REGION_ATCO_CODES = {
    "North East": ["410", "420", "430"],
    "North West": ["050", "060", "180", "200", "210"],
    "Yorkshire and The Humber": ["370", "450", "320", "220"],
    "East Midlands": ["270", "290", "260", "340", "280"],
    "West Midlands": ["430", "200", "350", "240", "570", "560"],
    "East of England": ["040", "160", "230", "300", "380", "020"],
    "London": ["490"],
    "South East": ["250", "390", "400", "410", "240", "030", "340", "010"],
    "South West": ["120", "090", "110", "360", "190", "540", "080"],
    "Wales": ["511", "512", "513", "520", "530", "540"],
    "Scotland": ["600", "609", "610", "639"],
}

# Stop types in NaPTAN
STOP_TYPES = {
    "BCT": "Bus/Coach bay/stand/stop within a Bus/Coach Station",
    "BCS": "Bus/Coach Station",
    "BCQ": "Bus/Coach Station bay",
    "BCE": "Bus/Coach Station entrance",
    "BST": "On-street bus/coach stop",
    "PLT": "Platform at a Railway Station",
    "RSE": "Railway Station entrance",
    "RLY": "Railway Station",
    "MET": "Metro/Underground platform",
    "TXR": "Taxi rank",
    "AIR": "Airport",
    "FER": "Ferry terminal",
    "FTD": "Ferry berth",
    "GAT": "Airport gate",
}

# Transport type groupings
TRANSPORT_TYPES = {
    "bus": ["BCT", "BCS", "BCQ", "BCE", "BST"],
    "rail": ["PLT", "RSE", "RLY"],
    "metro": ["MET"],
    "tram": ["MET"],  # Trams often use MET type
    "underground": ["MET"],
    "air": ["AIR", "GAT"],
    "ferry": ["FER", "FTD"],
    "taxi": ["TXR"],
}


class NaPTANApiError(Exception):
    """Exception raised for NaPTAN API errors."""
    pass


class NaPTANApiClient:
    """
    Async HTTP client for the NaPTAN API.

    Provides methods to query transport access points including bus stops,
    rail stations, metro stations, and other public transport nodes.
    """

    def __init__(self, timeout: float = DEFAULT_TIMEOUT):
        """
        Initialize the NaPTAN API client.

        Args:
            timeout: Request timeout in seconds (default: 120 for large downloads)
        """
        self.base_url = BASE_URL
        self.timeout = timeout
        self._client: Optional[httpx.AsyncClient] = None
        self._localities_cache: Optional[list[dict]] = None
        self._access_nodes_cache: dict[str, list[dict]] = {}

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create the async HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=self.timeout,
                headers={
                    "Accept": "text/csv",
                    "User-Agent": "DfT-MCP-Server/0.1.0"
                }
            )
        return self._client

    async def close(self):
        """Close the HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None

    async def _request_csv(self, endpoint: str, params: dict = None) -> list[dict]:
        """
        Make an HTTP request and parse CSV response.

        Args:
            endpoint: API endpoint path
            params: Query parameters

        Returns:
            list[dict]: Parsed CSV rows as dictionaries

        Raises:
            NaPTANApiError: If the request fails
        """
        client = await self._get_client()
        try:
            response = await client.get(endpoint, params=params)
            response.raise_for_status()

            # Parse CSV response
            content = response.text
            reader = csv.DictReader(io.StringIO(content))
            return list(reader)

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                raise NaPTANApiError("Rate limit exceeded. Please try again later.")
            raise NaPTANApiError(
                f"API request failed: {e.response.status_code} - {e.response.text}"
            )
        except httpx.RequestError as e:
            raise NaPTANApiError(f"Request error: {str(e)}")

    async def get_access_nodes(
        self,
        atco_area_codes: list[str] = None,
        use_cache: bool = True
    ) -> list[dict]:
        """
        Get transport access nodes (stops/stations).

        Args:
            atco_area_codes: List of ATCO area codes to filter by.
                            If None, returns national dataset (very large).
            use_cache: Whether to use cached data if available.

        Returns:
            list[dict]: Access nodes with details including coordinates,
                       stop type, and administrative area.
        """
        cache_key = ",".join(sorted(atco_area_codes)) if atco_area_codes else "national"

        if use_cache and cache_key in self._access_nodes_cache:
            return self._access_nodes_cache[cache_key]

        params = {"dataFormat": "csv"}
        if atco_area_codes:
            params["atcoAreaCodes"] = ",".join(atco_area_codes)

        result = await self._request_csv("/v1/access-nodes", params)

        if use_cache:
            self._access_nodes_cache[cache_key] = result

        return result

    async def get_localities(self, use_cache: bool = True) -> list[dict]:
        """
        Get locality information from NPTG (National Public Transport Gazetteer).

        Returns:
            list[dict]: Localities with names, codes, and administrative areas.
        """
        if use_cache and self._localities_cache is not None:
            return self._localities_cache

        result = await self._request_csv("/v1/nptg/localities")

        if use_cache:
            self._localities_cache = result

        return result

    async def get_available_regions(self) -> list[str]:
        """Get list of available region names."""
        return list(REGION_ATCO_CODES.keys())

    async def get_available_transport_types(self) -> list[str]:
        """Get list of available transport types."""
        return list(TRANSPORT_TYPES.keys())

    async def count_access_points_by_type(
        self,
        atco_area_codes: list[str] = None,
        transport_type: str = None
    ) -> dict[str, int]:
        """
        Count transport access points by stop type.

        Args:
            atco_area_codes: ATCO area codes to filter by
            transport_type: Filter by transport type (bus, rail, etc.)

        Returns:
            dict: Counts by stop type
        """
        nodes = await self.get_access_nodes(atco_area_codes)

        # Filter by transport type if specified
        if transport_type and transport_type in TRANSPORT_TYPES:
            valid_stop_types = TRANSPORT_TYPES[transport_type]
            nodes = [n for n in nodes if n.get("StopType") in valid_stop_types]

        # Count by stop type
        counts = {}
        for node in nodes:
            stop_type = node.get("StopType", "Unknown")
            counts[stop_type] = counts.get(stop_type, 0) + 1

        return counts

    async def search_access_points(
        self,
        atco_area_codes: list[str] = None,
        transport_type: str = None,
        locality_name: str = None,
        limit: int = 100
    ) -> list[dict]:
        """
        Search for transport access points with filters.

        Args:
            atco_area_codes: ATCO area codes to filter by
            transport_type: Filter by transport type (bus, rail, metro, etc.)
            locality_name: Filter by locality name (case-insensitive partial match)
            limit: Maximum number of results to return

        Returns:
            list[dict]: Matching access points with key details
        """
        nodes = await self.get_access_nodes(atco_area_codes)

        # Filter by transport type
        if transport_type and transport_type in TRANSPORT_TYPES:
            valid_stop_types = TRANSPORT_TYPES[transport_type]
            nodes = [n for n in nodes if n.get("StopType") in valid_stop_types]

        # Filter by locality name
        if locality_name:
            locality_lower = locality_name.lower()
            nodes = [
                n for n in nodes
                if locality_lower in n.get("LocalityName", "").lower()
            ]

        # Format and limit results
        results = []
        for node in nodes[:limit]:
            results.append({
                "atco_code": node.get("ATCOCode", ""),
                "name": node.get("CommonName", ""),
                "locality": node.get("LocalityName", ""),
                "stop_type": node.get("StopType", ""),
                "stop_type_description": STOP_TYPES.get(node.get("StopType", ""), "Unknown"),
                "latitude": node.get("Latitude", ""),
                "longitude": node.get("Longitude", ""),
                "administrative_area": node.get("AdministrativeAreaCode", ""),
            })

        return results

    def get_atco_codes_for_region(self, region: str) -> list[str]:
        """
        Get ATCO area codes for a region name.

        Args:
            region: Region name (e.g., "London", "North East")

        Returns:
            list[str]: ATCO area codes for the region
        """
        # Try exact match first
        if region in REGION_ATCO_CODES:
            return REGION_ATCO_CODES[region]

        # Try case-insensitive match
        region_lower = region.lower()
        for name, codes in REGION_ATCO_CODES.items():
            if name.lower() == region_lower:
                return codes

        return []


# Singleton client instance
_client: Optional[NaPTANApiClient] = None


def get_naptan_client() -> NaPTANApiClient:
    """Get the shared NaPTAN API client instance."""
    global _client
    if _client is None:
        _client = NaPTANApiClient()
    return _client
