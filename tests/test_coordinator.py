"""Tests for searchconsole_mcp/coordinator.py."""

import json
from unittest.mock import AsyncMock, patch

import pytest

from searchconsole_mcp.coordinator import (
    MCP_TOOLS,
    TOOL_FUNCTIONS,
    _build_tools,
    _sig_to_json_schema,
    call_tool,
    list_tools,
)


class TestSigToJsonSchema:
    """Tests for _sig_to_json_schema function."""

    def test_empty_function(self):
        """Test schema generation for function with no params."""

        def empty_func():
            pass

        schema, required = _sig_to_json_schema(empty_func)
        assert schema == {"type": "object", "properties": {}}
        assert required == []

    def test_required_param(self):
        """Test that required params are marked required."""

        def func_with_required(name: str):
            pass

        schema, required = _sig_to_json_schema(func_with_required)
        assert "name" in schema["properties"]
        assert schema["properties"]["name"]["type"] == "string"
        assert "name" in required

    def test_optional_param(self):
        """Test that optional params (with defaults) are not required."""

        def func_with_optional(name: str = "default"):
            pass

        schema, required = _sig_to_json_schema(func_with_optional)
        assert "name" not in required
        assert schema["properties"]["name"]["default"] == "default"

    def test_int_param(self):
        """Test that int params get integer type."""

        def func_with_int(count: int):
            pass

        schema, required = _sig_to_json_schema(func_with_int)
        assert schema["properties"]["count"]["type"] == "integer"

    def test_bool_param(self):
        """Test that bool params get boolean type."""

        def func_with_bool(active: bool):
            pass

        schema, required = _sig_to_json_schema(func_with_bool)
        assert schema["properties"]["active"]["type"] == "boolean"


class TestBuildTools:
    """Tests for _build_tools function."""

    def test_builds_all_tools(self):
        """Test that all 7 tools are built."""
        tools = _build_tools()
        assert len(tools) == 7
        tool_names = [t.name for t in tools]
        assert "get_sites" in tool_names
        assert "query_search_analytics" in tool_names
        assert "inspect_url" in tool_names

    def test_tools_have_descriptions(self):
        """Test that tools have descriptions from docstrings."""
        tools = _build_tools()
        for tool in tools:
            assert tool.description is not None
            assert len(tool.description) > 0

    def test_tools_have_schemas(self):
        """Test that tools have input schemas."""
        tools = _build_tools()
        for tool in tools:
            assert tool.inputSchema is not None
            assert tool.inputSchema.get("type") == "object"


class TestListTools:
    """Tests for list_tools async function."""

    @pytest.mark.asyncio
    async def test_returns_cached_tools(self):
        """Test that list_tools returns MCP_TOOLS."""
        result = await list_tools()
        assert result == MCP_TOOLS
        assert len(result) == 7


class TestCallTool:
    """Tests for call_tool async function."""

    @pytest.mark.asyncio
    async def test_unknown_tool(self):
        """Test calling unknown tool returns error."""
        result = await call_tool("unknown_tool", {})
        assert len(result) == 1
        assert result[0].type == "text"
        error_data = json.loads(result[0].text)
        assert "error" in error_data
        assert "not found" in error_data["error"]

    @pytest.mark.asyncio
    async def test_get_sites_success(self):
        """Test successful get_sites call."""
        mock_result = [{"siteUrl": "https://example.com/"}]

        with patch.object(TOOL_FUNCTIONS["get_sites"], "__call__", return_value=mock_result):
            # Need to use AsyncMock for async functions
            TOOL_FUNCTIONS["get_sites"] = AsyncMock(return_value=mock_result)

            result = await call_tool("get_sites", {})
            assert len(result) == 1
            assert result[0].type == "text"
            data = json.loads(result[0].text)
            assert data[0]["siteUrl"] == "https://example.com/"
