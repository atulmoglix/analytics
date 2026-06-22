"""
MCP tools: KPI definitions and certified KPI value retrieval.
"""

from mcp.server.fastmcp import FastMCP
from db import query, query_one

mcp = FastMCP("kpi")


@mcp.tool()
def get_kpi_definition(kpi_name: str) -> dict:
    """
    Return the certified definition, formula, owner, and certification status
    for a named KPI.

    Args:
        kpi_name: KPI identifier, e.g. 'GMV', 'Margin', 'Margin_Pct'.
    """
    row = query_one(
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
            certified_on,
            source_view
        FROM meta_kpi_definition
        WHERE UPPER(kpi_name) = UPPER(%s)
          AND is_active = 1
        """,
        (kpi_name,),
    )
    if not row:
        return {"error": f"KPI '{kpi_name}' not found or not active."}

    row["certified"] = bool(row.pop("certified_flag"))
    if row["certified_on"]:
        row["certified_on"] = str(row["certified_on"])
    return row


@mcp.tool()
def list_certified_kpis() -> list[dict]:
    """Return all certified KPIs with their display names and owners."""
    return query(
        """
        SELECT
            kpi_name,
            display_name,
            owner,
            certified_by,
            certified_on,
            source_view
        FROM meta_kpi_definition
        WHERE certified_flag = 1
          AND is_active = 1
        ORDER BY kpi_name
        """
    )


@mcp.tool()
def get_sales_kpi(
    breakdown: str = "region",
    year_month: str | None = None,
    region: str | None = None,
    limit: int = 50,
) -> list[dict]:
    """
    Retrieve aggregated sales KPI values from sem_monthly_sales_kpi.

    Args:
        breakdown: Grouping dimension — 'region', 'month', or 'region_month'.
        year_month: Optional filter, format 'YYYY-MM'.
        region: Optional region filter.
        limit: Max rows to return (default 50).
    """
    conditions = ["1=1"]
    params: list = []

    if year_month:
        conditions.append("year_month = %s")
        params.append(year_month)
    if region:
        conditions.append("region = %s")
        params.append(region)

    where = " AND ".join(conditions)

    group_map = {
        "region":       "region",
        "month":        "year_month",
        "region_month": "year_month, region",
    }
    group_by = group_map.get(breakdown, "region")

    sql = f"""
        SELECT
            {group_by},
            SUM(gmv)                AS gmv,
            SUM(margin)             AS margin,
            SUM(net_revenue)        AS net_revenue,
            SUM(total_quantity)     AS total_quantity,
            SUM(transaction_count)  AS transaction_count,
            SUM(unique_customers)   AS unique_customers,
            ROUND(SUM(margin) / NULLIF(SUM(gmv), 0) * 100, 2) AS margin_pct,
            SUM(dropship_gmv)       AS dropship_gmv,
            SUM(non_dropship_gmv)   AS non_dropship_gmv
        FROM semantic_layer.sem_monthly_sales_kpi
        WHERE {where}
        GROUP BY {group_by}
        ORDER BY {group_by}
        LIMIT %s
    """
    params.append(limit)
    return query(sql, tuple(params))
