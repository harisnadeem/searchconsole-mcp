"""Tests for searchconsole_mcp/tools/__init__.py and tool functions."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from searchconsole_mcp.tools import (
    _quote,
    get_sites,
    query_search_analytics,
    get_sitemap,
    list_sitemaps,
    submit_sitemap,
    delete_sitemap,
    inspect_url,
)


class TestQuote:
    """Tests for the _quote helper function."""

    def test_quote_simple_url(self):
        """Test quoting a simple URL without special chars."""
        url = "https://example.com/"
        result = _quote(url)
        assert result == "https%3A%2F%2Fexample.com%2F"

    def test_quote_sc_domain(self):
        """Test quoting sc-domain format."""
        url = "sc-domain:example.com"
        result = _quote(url)
        assert result == "sc-domain%3Aexample.com"


class TestGetSites:
    """Tests for get_sites tool."""

    @pytest.mark.asyncio
    async def test_get_sites_returns_list(self):
        """Test that get_sites returns a list of sites."""
        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "siteEntry": [
                {"siteUrl": "https://example.com/", "permissionLevel": "siteOwner"},
            ]
        }
        mock_client.get.return_value = mock_response

        with patch("searchconsole_mcp.tools.get_authenticated_client", return_value=mock_client):
            result = await get_sites()
            assert len(result) == 1
            assert result[0]["siteUrl"] == "https://example.com/"


class TestQuerySearchAnalytics:
    """Tests for query_search_analytics tool."""

    @pytest.mark.asyncio
    async def test_basic_query(self):
        """Test a basic search analytics query."""
        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "rows": [{"keys": ["2025-03-01"], "clicks": 100, "impressions": 1000}]
        }
        mock_client.post.return_value = mock_response

        with patch("searchconsole_mcp.tools.get_authenticated_client", return_value=mock_client):
            result = await query_search_analytics(
                site_url="https://example.com/",
                start_date="2025-03-01",
                end_date="2025-03-31",
            )
            assert "rows" in result
            assert result["rows"][0]["clicks"] == 100


class TestInspectUrl:
    """Tests for the inspect URL tool."""

    @pytest.mark.asyncio
    async def test_inspect_url_success(self):
        """Test successful URL inspection."""
        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "inspectionResult": {
                "indexStatusResult": {"coverageState": "Submitted and indexed"},
                "mobileUsabilityResult": {"verdict": "PASS"},
            }
        }
        mock_client.post.return_value = mock_response

        with patch("searchconsole_mcp.tools.get_authenticated_client", return_value=mock_client):
            result = await inspect_url("https://example.com/", "https://example.com/page")
            assert "inspectionResult" in result
