"""
MCP Tools, Resources, and Prompts for DfT NaPTAN Transport Data.

This module defines all the MCP primitives that the server exposes to clients:
- Tools: Callable functions for querying transport access point data
- Resources: Static schema and metadata information
- Prompts: Guided analysis templates

Data source: Department for Transport NaPTAN API
API Documentation: https://naptan.api.dft.gov.uk/swagger
"""

import json
from typing import Optional

from .naptan_api import (
    get_naptan_client,
    NaPTANApiError,
    STOP_TYPES,
    TRANSPORT_TYPES,
    REGION_ATCO_CODES,
)


def load_tools(mcp_server):
    """
    Register all MCP tools, resources, and prompts with the server.

    Args:
        mcp_server: The FastMCP server instance to register primitives with.
    """

    # =========================================================================
    # TOOLS
    # =========================================================================

    @mcp_server.tool
    async def get_transport_coverage(
        region: Optional[str] = None,
        atco_code: Optional[str] = None,
        locality: Optional[str] = None,
        transport_type: Optional[str] = None,
        limit: int = 100
    ) -> dict:
        """
        Get public transport access points (bus stops, rail stations, etc.) for a given area.

        Use this tool to understand transport connectivity and accessibility in a region.
        Returns a list of transport access points with their locations and types.

        Args:
            region: Region name (e.g., "London", "North East", "Yorkshire and The Humber").
                   Use get_available_data to see all valid regions.
            atco_code: ATCO area code for filtering (e.g., "490" for London, "370" for South Yorkshire).
                      Alternative to region - more precise filtering.
            locality: Locality name to search within (e.g., "Sheffield", "Manchester").
                     Performs case-insensitive partial matching.
            transport_type: Filter by transport mode. Options:
                - "bus": Bus and coach stops/stations
                - "rail": Railway stations and platforms
                - "metro": Metro/Underground stations
                - "tram": Tram stops
                - "air": Airports
                - "ferry": Ferry terminals
                - "taxi": Taxi ranks
                - None: All transport types (default)
            limit: Maximum number of results to return (default: 100, max: 500)

        Returns:
            dict: Transport coverage data with:
                - region: The region queried
                - transport_type: The transport type filter applied
                - count: Number of access points found
                - access_points: List of transport nodes with name, type, and coordinates
                - metadata: Source and query information

        Examples:
            - Get bus stops in London:
              region="London", transport_type="bus"

            - Get rail stations in Yorkshire:
              region="Yorkshire and The Humber", transport_type="rail"

            - Get all transport in Sheffield:
              locality="Sheffield"

            - Get metro stations using ATCO code:
              atco_code="490", transport_type="metro"
        """
        client = get_naptan_client()

        try:
            # Determine ATCO codes to use
            atco_codes = None
            region_name = "National"

            if atco_code:
                atco_codes = [atco_code]
                region_name = f"ATCO Area {atco_code}"
            elif region:
                atco_codes = client.get_atco_codes_for_region(region)
                region_name = region
                if not atco_codes:
                    return {
                        "error": f"Unknown region: {region}",
                        "available_regions": list(REGION_ATCO_CODES.keys()),
                        "suggestion": "Use get_available_data to see valid regions"
                    }

            # Limit the limit
            limit = min(limit, 500)

            # Search for access points
            access_points = await client.search_access_points(
                atco_area_codes=atco_codes,
                transport_type=transport_type,
                locality_name=locality,
                limit=limit
            )

            return {
                "region": region_name,
                "locality_filter": locality,
                "transport_type": transport_type or "all",
                "count": len(access_points),
                "access_points": access_points,
                "metadata": {
                    "source": "Department for Transport - NaPTAN",
                    "note": f"Showing up to {limit} results. Use locality filter for more specific queries."
                }
            }

        except NaPTANApiError as e:
            return {
                "error": str(e),
                "suggestion": "The NaPTAN API may be temporarily unavailable. Please try again."
            }
        except Exception as e:
            return {
                "error": f"Unexpected error: {str(e)}"
            }

    @mcp_server.tool
    async def count_access_points(
        region: Optional[str] = None,
        transport_type: Optional[str] = None
    ) -> dict:
        """
        Count transport access points by type in a region.

        Use this tool to get aggregate statistics about transport infrastructure
        in a region, broken down by transport mode (bus stops, rail stations, etc.).

        Args:
            region: Region name (e.g., "London", "North East", "Scotland").
                   If not specified, counts may be very large (national data).
            transport_type: Optional filter for specific transport mode:
                - "bus": Count only bus/coach stops and stations
                - "rail": Count only railway stations
                - "metro": Count only metro/underground stations
                - "air": Count only airports
                - "ferry": Count only ferry terminals
                - None: Count all transport types (default)

        Returns:
            dict: Count statistics with:
                - region: The region queried
                - total_count: Total number of access points
                - by_type: Breakdown by stop type (BST, RLY, MET, etc.)
                - by_type_description: Human-readable type descriptions
                - metadata: Source information

        Examples:
            - Count all transport in North East:
              region="North East"

            - Count bus stops in London:
              region="London", transport_type="bus"

            - Compare rail infrastructure:
              region="Yorkshire and The Humber", transport_type="rail"
        """
        client = get_naptan_client()

        try:
            # Determine ATCO codes
            atco_codes = None
            region_name = "National"

            if region:
                atco_codes = client.get_atco_codes_for_region(region)
                region_name = region
                if not atco_codes:
                    return {
                        "error": f"Unknown region: {region}",
                        "available_regions": list(REGION_ATCO_CODES.keys()),
                        "suggestion": "Use get_available_data to see valid regions"
                    }

            # Get counts by type
            counts = await client.count_access_points_by_type(
                atco_area_codes=atco_codes,
                transport_type=transport_type
            )

            # Add descriptions
            counts_with_descriptions = {}
            for stop_type, count in counts.items():
                description = STOP_TYPES.get(stop_type, "Unknown type")
                counts_with_descriptions[stop_type] = {
                    "count": count,
                    "description": description
                }

            total = sum(counts.values())

            return {
                "region": region_name,
                "transport_type_filter": transport_type or "all",
                "total_count": total,
                "by_type": counts,
                "by_type_description": counts_with_descriptions,
                "metadata": {
                    "source": "Department for Transport - NaPTAN",
                    "note": "Counts represent unique transport access points (stops, stations, platforms)"
                }
            }

        except NaPTANApiError as e:
            return {
                "error": str(e),
                "suggestion": "The NaPTAN API may be temporarily unavailable. Please try again."
            }
        except Exception as e:
            return {
                "error": f"Unexpected error: {str(e)}"
            }

    @mcp_server.tool
    async def get_available_data(
        data_type: str = "all"
    ) -> dict:
        """
        Discover what transport data is available to query.

        Use this tool first to understand what regions, transport types, and
        data categories can be queried before making specific data requests.

        Args:
            data_type: What to list. Options:
                - "regions": List all available regions
                - "transport_types": List transport modes (bus, rail, etc.)
                - "stop_types": List all stop type codes and descriptions
                - "all": Return everything (default)

        Returns:
            dict: Available data options with descriptions

        Example response for data_type="all":
            {
                "regions": ["London", "North East", "North West", ...],
                "transport_types": ["bus", "rail", "metro", "air", "ferry", "taxi"],
                "stop_types": {
                    "BST": "On-street bus/coach stop",
                    "RLY": "Railway Station",
                    ...
                }
            }
        """
        client = get_naptan_client()

        try:
            regions = await client.get_available_regions()
            transport_types = await client.get_available_transport_types()

            if data_type == "regions":
                return {
                    "regions": regions,
                    "note": "Use region names with get_transport_coverage or count_access_points"
                }

            elif data_type == "transport_types":
                return {
                    "transport_types": transport_types,
                    "descriptions": {
                        "bus": "Bus and coach stops, stations, and bays",
                        "rail": "Railway stations and platforms",
                        "metro": "Metro and underground stations",
                        "tram": "Tram stops (often shares codes with metro)",
                        "air": "Airports and airport gates",
                        "ferry": "Ferry terminals and berths",
                        "taxi": "Taxi ranks"
                    }
                }

            elif data_type == "stop_types":
                return {
                    "stop_types": STOP_TYPES,
                    "note": "These are the raw NaPTAN stop type codes"
                }

            else:  # "all"
                return {
                    "regions": regions,
                    "transport_types": transport_types,
                    "stop_types": STOP_TYPES,
                    "notes": {
                        "data_source": "Department for Transport NaPTAN API",
                        "geographic_coverage": "England, Scotland, Wales",
                        "data_freshness": "Updated continuously",
                        "license": "Open Government Licence v3.0"
                    }
                }

        except NaPTANApiError as e:
            return {
                "error": str(e),
                "suggestion": "The NaPTAN API may be temporarily unavailable."
            }
        except Exception as e:
            return {
                "error": f"Unexpected error: {str(e)}"
            }

    # =========================================================================
    # RESOURCES
    # =========================================================================

    @mcp_server.resource("dft://schema/transport-access-points")
    def get_transport_schema() -> str:
        """
        Schema and metadata for DfT NaPTAN transport access point data.

        This resource provides detailed documentation about the transport
        data available through this MCP server, including stop type definitions,
        geographic coverage, and data quality notes.
        """
        schema = {
            "dataset": "NaPTAN - National Public Transport Access Nodes",
            "source": "Department for Transport",
            "api_documentation": "https://naptan.api.dft.gov.uk/swagger",
            "license": "Open Government Licence v3.0",
            "description": (
                "NaPTAN provides a unique identifier for every point of access "
                "to public transport in Great Britain. This includes bus stops, "
                "rail stations, metro platforms, ferry terminals, and airports."
            ),
            "transport_types": {
                "bus": {
                    "description": "Bus and coach services",
                    "stop_types": ["BCT", "BCS", "BCQ", "BCE", "BST"],
                    "note": "Most common transport type by count"
                },
                "rail": {
                    "description": "National Rail services",
                    "stop_types": ["PLT", "RSE", "RLY"],
                    "note": "Includes platforms and station entrances"
                },
                "metro": {
                    "description": "Metro, Underground, and Light Rail",
                    "stop_types": ["MET"],
                    "note": "Includes London Underground, Tyne & Wear Metro, etc."
                },
                "air": {
                    "description": "Air transport",
                    "stop_types": ["AIR", "GAT"],
                    "note": "Airports and airport gates"
                },
                "ferry": {
                    "description": "Ferry services",
                    "stop_types": ["FER", "FTD"],
                    "note": "Terminals and berths"
                },
                "taxi": {
                    "description": "Taxi services",
                    "stop_types": ["TXR"],
                    "note": "Designated taxi ranks"
                }
            },
            "stop_type_codes": STOP_TYPES,
            "geographic_coverage": {
                "england": "All regions from North East to South West",
                "scotland": "All council areas",
                "wales": "All unitary authorities",
                "note": "Northern Ireland uses a separate system (Translink)"
            },
            "regions": {
                "england": [
                    "North East",
                    "North West",
                    "Yorkshire and The Humber",
                    "East Midlands",
                    "West Midlands",
                    "East of England",
                    "London",
                    "South East",
                    "South West"
                ],
                "wales": ["Wales"],
                "scotland": ["Scotland"]
            },
            "atco_codes": {
                "description": "ATCO area codes are 3-digit prefixes identifying administrative areas",
                "examples": {
                    "490": "London",
                    "370": "South Yorkshire",
                    "050": "Merseyside"
                }
            },
            "data_fields": {
                "ATCOCode": "Unique identifier for each access point",
                "CommonName": "Public-facing name of the stop/station",
                "LocalityName": "Name of the locality/town",
                "StopType": "Type code (BST, RLY, MET, etc.)",
                "Latitude": "WGS84 latitude coordinate",
                "Longitude": "WGS84 longitude coordinate",
                "AdministrativeAreaCode": "ATCO area code"
            },
            "data_quality_notes": [
                "Data is updated continuously as local authorities submit changes",
                "Some historical stops may still appear in the data",
                "Coordinates are generally accurate to a few meters",
                "Stop names may vary from common usage",
                "Some access points serve multiple transport modes"
            ],
            "use_cases": {
                "policy_analysis": [
                    "Assess transport accessibility in different regions",
                    "Identify areas with poor transport connectivity",
                    "Compare transport infrastructure across regions",
                    "Support employment and education accessibility studies"
                ],
                "cross_departmental": [
                    "Correlate transport access with education outcomes (with DfE data)",
                    "Analyze transport barriers to employment",
                    "Support regional development planning"
                ]
            }
        }
        return json.dumps(schema, indent=2)

    # =========================================================================
    # PROMPTS
    # =========================================================================

    @mcp_server.prompt("transport-accessibility-analysis")
    def transport_accessibility_prompt(region_name: str) -> str:
        """
        Guided analysis of transport accessibility for a specific region.

        Use this prompt to perform a comprehensive analysis of transport
        infrastructure in any region, understanding connectivity and
        identifying potential accessibility gaps.

        Args:
            region_name: The region to analyze (e.g., "North East", "London")
        """
        return f"""Analyze transport accessibility for {region_name}:

1. **Understand the data structure**
   First, read the schema resource (dft://schema/transport-access-points) to understand the available transport types and what the data represents.

2. **Verify data availability**
   Use get_available_data() to confirm {region_name} is a valid region and see what transport types are tracked.

3. **Get overall transport counts**
   Use count_access_points(region="{region_name}") to get a breakdown of all transport access points by type.

4. **Analyze by transport mode**
   Query each major transport type separately:
   - count_access_points(region="{region_name}", transport_type="bus") - Bus connectivity
   - count_access_points(region="{region_name}", transport_type="rail") - Rail connectivity
   - count_access_points(region="{region_name}", transport_type="metro") - Metro/Underground if applicable

5. **Explore specific localities**
   Use get_transport_coverage to look at transport in key towns/cities within {region_name}.

6. **Summarize findings**
   Present your findings in 3-4 bullet points suitable for policy makers, covering:
   - Overall transport infrastructure density
   - Dominant transport modes (bus vs rail)
   - Notable gaps or concentrations
   - Comparison to expectations for the region type (urban vs rural)

**Important notes:**
- Bus stops typically outnumber all other transport types combined
- Metro/underground data only exists for areas with these systems (London, Newcastle, etc.)
- Consider population density when interpreting raw counts
- Transport access is one factor in accessibility - frequency and connectivity matter too"""
