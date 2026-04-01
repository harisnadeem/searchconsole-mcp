"""MCP server entrypoint for Google Search Console."""

import asyncio
import logging
import sys
import traceback

from searchconsole_mcp.coordinator import app

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


async def run_server_async():
    """Run the MCP server using stdio transport."""
    from mcp.server.stdio import stdio_server

    init_options = app.create_initialization_options()
    async with stdio_server() as (read_stream, write_stream):
        logger.info("Google Search Console MCP Server started.")
        await app.run(read_stream, write_stream, init_options)


def run_server():
    """Synchronous entry point for the CLI."""
    try:
        asyncio.run(run_server_async())
    except KeyboardInterrupt:
        logger.info("MCP Server stopped by interrupt.")
        sys.exit(0)
    except Exception:
        logger.error("MCP Server (stdio) encountered an error:")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    run_server()
