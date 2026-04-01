"""Tool functions for the Google Search Console MCP server.

Each async function corresponds to one MCP tool. They use google-auth ADC
and httpx for REST calls against the Search Console API v3.
"""

import urllib.parse
from typing import Any, Literal

from searchconsole_mcp.utils import GSC_BASE_URL, get_authenticated_client

__all__ = [
    "get_sites",
    "query_search_analytics",
    "get_sitemap",
    "list_sitemaps",
    "submit_sitemap",
    "delete_sitemap",
    "inspect_url",
]


def _quote(site_url: str) -> str:
    """URL-encode a site URL or path for use in GSC API paths."""
    return urllib.parse.quote(site_url, safe="")


# ---------------------------------------------------------------------------
# Sites
# ---------------------------------------------------------------------------


async def get_sites() -> list[dict[str, Any]]:
    """List all websites in the user's Search Console account.

    Returns a list of site entries, each containing 'siteUrl' and permission level.
    """
    client = await get_authenticated_client()
    response = await client.get(f"{GSC_BASE_URL}/sites")
    response.raise_for_status()
    data = response.json()
    return data.get("siteEntry", [])


# ---------------------------------------------------------------------------
# Search Analytics
# ---------------------------------------------------------------------------


async def query_search_analytics(
    site_url: str,
    start_date: str,
    end_date: str,
    dimensions: list[str] | None = None,
    search_type: Literal["web", "image", "video", "news", "discover", "googleNews"] | None = "web",
    row_limit: int | None = 1000,
    start_row: int | None = 0,
    data_state: Literal["final", "all"] | None = "final",
    aggregation_type: Literal["auto", "byPage", "byProperty"] | None = None,
    dimension_filter_groups: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Query Search Analytics data for a website.

    Args:
        site_url: The site to query, e.g. 'https://example.com/' or 'sc-domain:example.com'.
        start_date: Start date in YYYY-MM-DD format.
        end_date: End date in YYYY-MM-DD format.
        dimensions: Group results by these dimensions.
            Valid values: date, query, page, country, device, searchAppearance.
            Omit to get aggregate totals with no grouping.
        search_type: Type of search to filter by.
            Values: web (default), image, video, news, discover, googleNews.
        row_limit: Maximum number of rows to return (default 1000).
        start_row: Zero-based offset for pagination (default 0).
        data_state: Include only 'final' (default) confirmed data, or 'all'.
        aggregation_type: How to aggregate data.
            'auto' (default), 'byPage', or 'byProperty'.
        dimension_filter_groups: List of filter groups to apply.
            Each group has 'groupType' ('and'/'or') and 'filters' list.
            Each filter: {dimension, expression, operator}.
            Operators: equals, notEquals, contains, notContains,
                       beginsWith, notBeginsWith, endsWith, notEndsWith,
                       isEmpty, isNotEmpty.

    Returns:
        Dictionary with 'rows' (list of result rows) and 'responseAggregationType'.
        Each row contains dimension values in 'keys' plus:
        - clicks (total clicks)
        - impressions (total impressions)
        - ctr (click-through rate)
        - position (average search position)
    """
    client = await get_authenticated_client()

    payload: dict[str, Any] = {
        "startDate": start_date,
        "endDate": end_date,
        "rowLimit": row_limit,
        "startRow": start_row,
        "dataState": data_state.upper() if data_state else "FINAL",
        "type": (search_type or "web").upper(),
    }

    if dimensions:
        payload["dimensions"] = dimensions

    if aggregation_type:
        payload["aggregationType"] = aggregation_type.upper()

    if dimension_filter_groups:
        payload["dimensionFilterGroups"] = dimension_filter_groups

    url = f"{GSC_BASE_URL}/sites/{_quote(site_url)}/searchAnalytics/query"
    response = await client.post(url, json=payload)
    response.raise_for_status()
    return response.json()


# ---------------------------------------------------------------------------
# Sitemaps
# ---------------------------------------------------------------------------


async def list_sitemaps(site_url: str) -> dict[str, Any]:
    """List all sitemaps submitted for a website.

    Args:
        site_url: The site whose sitemaps to list, e.g. 'https://example.com/'.

    Returns:
        Dictionary with 'sitemap' list containing feedpath, type, contentsCounts,
        etc.
    """
    client = await get_authenticated_client()
    url = f"{GSC_BASE_URL}/sites/{_quote(site_url)}/sitemaps"
    response = await client.get(url)
    response.raise_for_status()
    return response.json()


async def get_sitemap(site_url: str, feedpath: str) -> dict[str, Any]:
    """Get details about a specific sitemap.

    Args:
        site_url: The site, e.g. 'https://example.com/'.
        feedpath: The sitemap path, e.g. '/sitemap.xml'.

    Returns:
        Dictionary with sitemap metadata (submitted/referenced counts,
        last downloaded, errors, warnings).
    """
    client = await get_authenticated_client()
    url = f"{GSC_BASE_URL}/sites/{_quote(site_url)}/sitemaps/{_quote(feedpath)}"
    response = await client.get(url)
    response.raise_for_status()
    return response.json()


async def submit_sitemap(site_url: str, feedpath: str) -> dict[str, Any]:
    """Submit (add) a sitemap to a website.

    Args:
        site_url: The site, e.g. 'https://example.com/'.
        feedpath: The sitemap path to submit, e.g. '/sitemap.xml'.

    Returns:
        Empty dict on success.
    """
    client = await get_authenticated_client()
    url = f"{GSC_BASE_URL}/sites/{_quote(site_url)}/sitemaps/{_quote(feedpath)}"
    response = await client.put(url)
    response.raise_for_status()
    if response.text:
        return response.json()
    return {"status": "success", "siteUrl": site_url, "feedpath": feedpath}


async def delete_sitemap(site_url: str, feedpath: str) -> dict[str, Any]:
    """Delete a sitemap from a website.

    Args:
        site_url: The site, e.g. 'https://example.com/'.
        feedpath: The sitemap path to delete, e.g. '/sitemap.xml'.

    Returns:
        Empty dict on success.
    """
    client = await get_authenticated_client()
    url = f"{GSC_BASE_URL}/sites/{_quote(site_url)}/sitemaps/{_quote(feedpath)}"
    response = await client.delete(url)
    response.raise_for_status()
    if response.text:
        return response.json()
    return {"status": "deleted"}


# ---------------------------------------------------------------------------
# URL Inspection
# ---------------------------------------------------------------------------


async def inspect_url(
    site_url: str,
    inspection_url: str,
    language_code: str = "en-US",
) -> dict[str, Any]:
    """Inspect the indexing status of a URL in Google.

    Args:
        site_url: The site URL registered in Search Console,
            e.g. 'https://example.com/'.
        inspection_url: The full URL to inspect,
            e.g. 'https://example.com/some-page'.
        language_code: The language code for the inspection request
            (default 'en-US').

    Returns:
        Dictionary with inspection result including indexStatus,
        coverageState, robots_txt_state, page_fetch_state, etc.
    """
    client = await get_authenticated_client()
    url = f"{GSC_BASE_URL}/urlInspection/index"

    payload = {
        "siteUrl": site_url,
        "inspectionUrl": inspection_url,
        "languageCode": language_code,
    }

    response = await client.post(url, json=payload)
    response.raise_for_status()
    return response.json()
