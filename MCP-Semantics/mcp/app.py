"""
Semantic MCP Server — entry point.

Registers all tool modules and starts the FastMCP server.

Run locally:
    python app.py

Run as STDIO transport (for Claude Desktop / MCP client):
    python app.py --transport stdio
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

# Load env vars from config/.env (two levels up from mcp/)
_env_path = Path(__file__).parent.parent / "config" / ".env"
load_dotenv(_env_path)

# Ensure db.py and tools/ are importable
sys.path.insert(0, str(Path(__file__).parent))

from tools.kpi_tools      import mcp as kpi_mcp
from tools.metadata_tools import mcp as metadata_mcp
from tools.glossary_tools import mcp as glossary_mcp
from tools.search_tools   import mcp as search_mcp

# Main server
mcp = FastMCP(
    name="Semantic Analytics MCP",
    description=(
        "Enterprise Semantic Layer MCP Server. "
        "Provides governed access to certified KPIs, business metric definitions, "
        "column-level data dictionary, business rules, and data quality standards. "
        "Direct database access is NOT exposed."
    ),
)

# Mount sub-MCPs
mcp.mount(kpi_mcp)
mcp.mount(metadata_mcp)
mcp.mount(glossary_mcp)
mcp.mount(search_mcp)

if __name__ == "__main__":
    transport = "stdio" if "--transport" in sys.argv and "stdio" in sys.argv else "sse"
    port = int(os.environ.get("MCP_PORT", "8000"))

    if transport == "stdio":
        mcp.run(transport="stdio")
    else:
        mcp.run(transport="sse", host="0.0.0.0", port=port)
