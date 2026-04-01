"""MCP server singleton — registers all tools and handles tool calls."""

import inspect
import json
import logging
from typing import Any

from mcp import types as mcp_types
from mcp.server.lowlevel import Server

from searchconsole_mcp.tools import (
    delete_sitemap,
    get_sitemap,
    get_sites,
    inspect_url,
    list_sitemaps,
    query_search_analytics,
    submit_sitemap,
)

logger = logging.getLogger(__name__)

# ── Tool registry ──────────────────────────────────────────────────────────

TOOL_FUNCTIONS: dict[str, Any] = {
    f.__name__: f
    for f in [
        get_sites,
        query_search_analytics,
        get_sitemap,
        list_sitemaps,
        submit_sitemap,
        delete_sitemap,
        inspect_url,
    ]
}


def _sig_to_json_schema(
    func: Any,
) -> tuple[dict[str, Any], list[str]]:
    """Convert a function's signature into a JSON Schema object."""
    sig = inspect.signature(func)
    properties: dict[str, Any] = {}
    required: list[str] = []

    for param_name, param in sig.parameters.items():
        if param_name in ("return",):
            continue
        schema: dict[str, Any] = {"type": "string"}
        ann = param.annotation
        if ann is not inspect.Parameter.empty:
            if ann is int:
                schema["type"] = "integer"
            elif ann is bool:
                schema["type"] = "boolean"
            elif hasattr(ann, "__origin__"):
                args = getattr(ann, "__args__", ())
                if int in args:
                    schema["type"] = "integer"
                elif bool in args:
                    schema["type"] = "boolean"
        if param.default is inspect.Parameter.empty:
            required.append(param_name)
        elif param.default is not None:
            schema["default"] = param.default
        properties[param_name] = schema

    schema_dict: dict[str, Any] = {"type": "object", "properties": properties}
    if required:
        schema_dict["required"] = required
    return schema_dict, required


def _build_tools() -> list[mcp_types.Tool]:
    tools: list[mcp_types.Tool] = []
    for name, func in TOOL_FUNCTIONS.items():
        doc = inspect.getdoc(func) or func.__doc__ or ""
        schema, _ = _sig_to_json_schema(func)
        tools.append(
            mcp_types.Tool(
                name=name,
                description=doc.strip(),
                inputSchema=schema,
            )
        )
    return tools


app = Server(name="Google Search Console MCP Server")
MCP_TOOLS = _build_tools()


@app.list_tools()
async def list_tools() -> list[mcp_types.Tool]:
    """Return all registered MCP tools."""
    return MCP_TOOLS


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[mcp_types.Content]:
    """Execute a registered tool by name with the provided arguments."""
    if name not in TOOL_FUNCTIONS:
        error_text = json.dumps({"error": f"Tool '{name}' not found."})
        return [mcp_types.TextContent(type="text", text=error_text)]

    try:
        result = await TOOL_FUNCTIONS[name](**arguments)
        if isinstance(result, (dict, list)):
            text = json.dumps(result, indent=2, ensure_ascii=False)
        elif isinstance(result, str):
            text = result
        else:
            text = str(result)
        return [mcp_types.TextContent(type="text", text=text)]
    except Exception as e:
        logger.error("Tool '%s' failed: %s", name, e, exc_info=True)
        error_text = json.dumps({"error": f"Tool '{name}' failed: {e}"})
        return [mcp_types.TextContent(type="text", text=error_text)]
