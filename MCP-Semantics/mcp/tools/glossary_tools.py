"""
MCP tools: Business rules / glossary access.
"""

from mcp.server.fastmcp import FastMCP
from db import query, query_one

mcp = FastMCP("glossary")


@mcp.tool()
def get_business_rule(rule_name: str) -> dict:
    """
    Return the full description and scope of a named business rule.

    Args:
        rule_name: e.g. 'GMV Definition', 'Dropship Definition'.
    """
    row = query_one(
        """
        SELECT
            rule_name,
            rule_description,
            source_tables,
            effective_from,
            effective_to,
            owner
        FROM meta_business_rules
        WHERE UPPER(rule_name) = UPPER(%s)
        """,
        (rule_name,),
    )
    if not row:
        return {"error": f"Business rule '{rule_name}' not found."}

    row["effective_from"] = str(row["effective_from"]) if row["effective_from"] else None
    row["effective_to"]   = str(row["effective_to"])   if row["effective_to"]   else "Currently Active"
    return row


@mcp.tool()
def list_business_rules(active_only: bool = True) -> list[dict]:
    """
    List all documented business rules.

    Args:
        active_only: If True, return only currently active rules (effective_to IS NULL).
    """
    if active_only:
        return query(
            """
            SELECT rule_name, source_tables, effective_from, owner
            FROM meta_business_rules
            WHERE effective_to IS NULL
            ORDER BY rule_name
            """
        )
    return query(
        """
        SELECT rule_name, source_tables, effective_from, effective_to, owner
        FROM meta_business_rules
        ORDER BY rule_name
        """
    )


@mcp.tool()
def search_business_rules(keyword: str) -> list[dict]:
    """
    Search business rules by keyword across rule_name and rule_description.

    Args:
        keyword: e.g. 'dropship', 'allocation', 'margin'.
    """
    like = f"%{keyword}%"
    return query(
        """
        SELECT
            rule_name,
            rule_description,
            source_tables,
            effective_from,
            owner
        FROM meta_business_rules
        WHERE (rule_name LIKE %s OR rule_description LIKE %s)
          AND (effective_to IS NULL OR effective_to >= CURDATE())
        ORDER BY rule_name
        """,
        (like, like),
    )


@mcp.tool()
def get_data_quality_rules(table_name: str | None = None) -> list[dict]:
    """
    Return data quality validation rules, optionally filtered by table.

    Args:
        table_name: Optional table filter, e.g. 'Fact_Sales'.
    """
    if table_name:
        return query(
            """
            SELECT rule_name, target_table, target_column, validation_logic, severity, owner
            FROM meta_data_quality_rules
            WHERE target_table = %s AND is_active = 1
            ORDER BY severity, rule_name
            """,
            (table_name,),
        )
    return query(
        """
        SELECT rule_name, target_table, target_column, validation_logic, severity, owner
        FROM meta_data_quality_rules
        WHERE is_active = 1
        ORDER BY severity, rule_name
        """
    )
