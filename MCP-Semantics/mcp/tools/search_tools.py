"""
MCP tools: Cross-domain semantic search across KPIs, columns, and rules.
"""

from mcp.server.fastmcp import FastMCP
from db import query

mcp = FastMCP("search")


@mcp.tool()
def semantic_search(keyword: str, limit: int = 30) -> dict:
    """
    Search across all metadata domains (KPIs, columns, business rules)
    with a single keyword. Returns a grouped result.

    Args:
        keyword: Search term, e.g. 'dropship', 'margin', 'region'.
        limit: Max results per domain (default 30).
    """
    like = f"%{keyword}%"

    kpis = query(
        """
        SELECT 'kpi' AS domain, kpi_name AS name, display_name, business_definition AS description
        FROM meta_kpi_definition
        WHERE is_active = 1
          AND (kpi_name LIKE %s OR display_name LIKE %s OR business_definition LIKE %s)
        ORDER BY kpi_name
        LIMIT %s
        """,
        (like, like, like, limit),
    )

    columns = query(
        """
        SELECT 'column' AS domain, CONCAT(table_name, '.', column_name) AS name,
               business_name AS display_name, business_definition AS description
        FROM meta_column_definition
        WHERE is_active = 1
          AND (column_name LIKE %s OR business_name LIKE %s OR business_definition LIKE %s)
        ORDER BY table_name, column_name
        LIMIT %s
        """,
        (like, like, like, limit),
    )

    rules = query(
        """
        SELECT 'business_rule' AS domain, rule_name AS name,
               rule_name AS display_name, rule_description AS description
        FROM meta_business_rules
        WHERE (rule_name LIKE %s OR rule_description LIKE %s)
          AND (effective_to IS NULL OR effective_to >= CURDATE())
        ORDER BY rule_name
        LIMIT %s
        """,
        (like, like, limit),
    )

    return {
        "keyword": keyword,
        "kpis":           kpis,
        "columns":        columns,
        "business_rules": rules,
        "total_results":  len(kpis) + len(columns) + len(rules),
    }


@mcp.tool()
def get_asset_ownership(asset_name: str) -> dict:
    """
    Return data owner, business owner, and sensitivity level for any
    registered asset (table, view, column, or KPI).

    Args:
        asset_name: e.g. 'Fact_Sales', 'sem_sales_base', 'GMV'.
    """
    row = query(
        """
        SELECT asset_type, asset_name, data_owner, business_owner, sensitivity_level, access_restrictions
        FROM meta_data_ownership
        WHERE UPPER(asset_name) = UPPER(%s)
        """,
        (asset_name,),
    )
    if not row:
        return {"error": f"Asset '{asset_name}' not found in ownership registry."}
    return row[0]
