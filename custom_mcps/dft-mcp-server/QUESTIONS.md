# Questions You Can Ask the DfT MCP Tool

This MCP server exposes transport access point data from the Department for Transport NaPTAN API. Use the questions below as prompts for an MCP client.

## Quick Discovery
- What regions are available?
- What transport types can I query?
- Show me all stop type codes and descriptions.
- What data does this server provide?

## Regional Coverage
- What public transport access points are available in London?
- Show all rail stations in the North East.
- List bus stops in Yorkshire and The Humber.
- What transport nodes are available in Sheffield?

## Counts and Summaries
- How many transport access points are there in London?
- Count bus stops in the West Midlands.
- Compare rail station counts between North West and South East.
- How many airports are there in Scotland?

## Locality-Focused Questions
- Show transport access points around Manchester.
- List metro stations in Newcastle.
- Find tram stops in Sheffield.

## Mode-Specific Queries
- Show all ferry terminals in Wales.
- Find taxi ranks in London.
- List all airports in England.

## Rankings and Comparisons (Multiple Calls)
- Compare bus stop coverage between London and South West.
- Which region has the most rail stations?
- For each region, count metro stations and rank them.

## Intelligent Questions (Multi-Step Analysis)
- Identify the top 3 regions with the highest rail station counts and summarize why those regions might be well served.
- Compare bus stop density between London and the South East, then suggest which localities could be under-served.
- For a given region, list access points by transport type and explain the dominant modes.
- Show transport coverage for Manchester and recommend the best transport modes to prioritize for accessibility improvements.
- Find regions with relatively high metro station counts but low rail station counts, and summarize the pattern.
- Compare airport and ferry terminal availability across Scotland, Wales, and South West England.
- For London, retrieve bus, rail, and metro access points and summarize the balance across modes.
- Use available regions and transport types to propose a shortlist of areas for a pilot transport-accessibility program.

## Schema and Metadata
- Show the schema for transport access points.
- What stop type codes exist for bus services?
- What is the geographic coverage of this data?

## Example Tool Calls
- get_available_data(data_type="all")
- get_transport_coverage(region="London", transport_type="bus", limit=50)
- get_transport_coverage(locality="Sheffield", transport_type="tram")
- count_access_points(region="North East")
- count_access_points(region="London", transport_type="rail")
