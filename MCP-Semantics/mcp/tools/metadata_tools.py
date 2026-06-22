"""
MCP tools: Column metadata lookup and metric explanation.
"""

from mcp.server.fastmcp import FastMCP
from db import query, query_one

mcp = FastMCP("metadata")


@mcp.tool()
def search_columns(keyword: str, limit: int = 20) -> list[dict]:
    """
    Search the data dictionary for columns matching a keyword.
    Searches across column_name, business_name, and business_definition.

    Args:
        keyword: Search term, e.g. 'dropship', 'margin', 'customer'.
        limit: Max rows to return (default 20).
    """
    like = f"%{keyword}%"
    return query(
        """
        SELECT
            table_name,
            column_name,
            business_name,
            business_definition,
            data_type,
            allowed_values,
            owner,
            sensitivity_level
        FROM meta_column_definition
        WHERE is_active = 1
          AND (
              column_name        LIKE %s
           OR business_name      LIKE %s
           OR business_definition LIKE %s
          )
        ORDER BY table_name, column_name
        LIMIT %s
        """,
        (like, like, like, limit),
    )


@mcp.tool()
def get_column_definition(table_name: str, column_name: str) -> dict:
    """
    Return the full business definition for a specific column.

    Args:
        table_name: e.g. 'Fact_Sales'.
        column_name: e.g. 'is_dp'.
    """
    row = query_one(
        """
        SELECT
            table_name,
            column_name,
            business_name,
            business_definition,
            data_type,
            allowed_values,
            owner,
            sensitivity_level
        FROM meta_column_definition
        WHERE table_name   = %s
          AND column_name  = %s
          AND is_active    = 1
        """,
        (table_name, column_name),
    )
    if not row:
        return {"error": f"Column '{table_name}.{column_name}' not found."}
    return row


@mcp.tool()
def explain_metric(metric_name: str) -> dict:
    """
    Explain a business metric or KPI in plain English — definition, formula,
    grain, certification status, and business rules that affect it.

    Args:
        metric_name: e.g. 'Margin %', 'Customer Opex Allocation', 'GMV'.
    """
    kpi = query_one(
        """
        SELECT
            kpi_name,
            display_name,
            business_definition,
            formula_sql,
            grain,
            owner,
            certified_flag,
            certified_by,
            source_view
        FROM meta_kpi_definition
        WHERE (UPPER(kpi_name) = UPPER(%s) OR UPPER(display_name) = UPPER(%s))
          AND is_active = 1
        LIMIT 1
        """,
        (metric_name, metric_name),
    )
    if not kpi:
        return {"error": f"Metric '{metric_name}' not found."}

    related_rules = query(
        """
        SELECT rule_name, rule_description
        FROM meta_business_rules
        WHERE (source_tables LIKE %s OR rule_name LIKE %s)
          AND (effective_to IS NULL OR effective_to >= CURDATE())
        """,
        (f"%{kpi['kpi_name']}%", f"%{kpi['kpi_name']}%"),
    )

    kpi["certified"] = bool(kpi.pop("certified_flag"))
    kpi["related_business_rules"] = related_rules
    return kpi


@mcp.tool()
def list_tables() -> list[dict]:
    """List all tables registered in the data dictionary with their owners."""
    return query(
        """
        SELECT DISTINCT
            table_name,
            owner,
            MAX(sensitivity_level) AS max_sensitivity
        FROM meta_column_definition
        WHERE is_active = 1
        GROUP BY table_name, owner
        ORDER BY table_name
        """
    )


@mcp.tool()
def get_table_columns(table_name: str) -> list[dict]:
    """
    Return all documented columns for a given table.

    Args:
        table_name: e.g. 'Fact_Sales', 'Dim_Customer'.
    """
    rows = query(
        """
        SELECT
            column_name,
            business_name,
            business_definition,
            data_type,
            allowed_values,
            sensitivity_level
        FROM meta_column_definition
        WHERE table_name = %s AND is_active = 1
        ORDER BY column_name
        """,
        (table_name,),
    )
    if not rows:
        return [{"error": f"No columns found for table '{table_name}'."}]
    return rows
