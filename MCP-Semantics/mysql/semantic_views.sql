-- ============================================================
-- SEMANTIC LAYER: Views on top of the Data Mart (datamart DB)
-- All views live in the semantic_layer schema created below.
-- Raw Fact / Dimension tables are in the `datamart` schema.
-- ============================================================

CREATE DATABASE IF NOT EXISTS semantic_layer
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE semantic_layer;

-- ============================================================
-- COMPONENT 1 — BASE SEMANTIC VIEWS
-- Purpose: standardised joins, business-friendly columns,
--          hide raw complexity from consumers.
-- ============================================================

-- --------------------------------------------------------
-- sem_sales_base
-- Single business-friendly sales grain (transaction level)
-- --------------------------------------------------------
CREATE OR REPLACE VIEW sem_sales_base AS
SELECT
    fs.sale_id,
    fs.invoice_date,
    dt.year_month,
    dt.year,
    dt.quarter,
    dt.month,
    dc.customer_id,
    dc.customer_name,
    dc.region,
    dc.zone,
    dc.team,
    dc.customer_type,
    dp.product_id,
    dp.product_name,
    dp.category,
    dp.brand,
    dpl.plant_id,
    dpl.plant_name,
    dpl.state,
    fs.quantity,
    fs.gmv,
    fs.margin,
    fs.is_dp                   AS is_dropship,
    fs.discount,
    fs.net_revenue
FROM datamart.Fact_Sales          fs
JOIN datamart.Dim_Customer        dc  ON dc.customer_id  = fs.customer_id
JOIN datamart.Dim_Product         dp  ON dp.product_id   = fs.product_id
JOIN datamart.Dim_Time            dt  ON dt.time_id       = fs.time_id
JOIN datamart.Dim_Plant           dpl ON dpl.plant_id     = fs.plant_id;


-- --------------------------------------------------------
-- sem_purchase_base
-- Single business-friendly purchase grain (transaction level)
-- --------------------------------------------------------
CREATE OR REPLACE VIEW sem_purchase_base AS
SELECT
    fp.purchase_id,
    fp.purchase_date,
    dt.year_month,
    dt.year,
    dt.quarter,
    dt.month,
    dp.product_id,
    dp.product_name,
    dp.category,
    dp.brand,
    dpl.plant_id,
    dpl.plant_name,
    dpl.state,
    fp.quantity,
    fp.purchase_value,
    fp.landed_cost,
    fp.vendor_id,
    fp.vendor_name
FROM datamart.Fact_Purchase        fp
JOIN datamart.Dim_Product          dp  ON dp.product_id = fp.product_id
JOIN datamart.Dim_Time             dt  ON dt.time_id     = fp.time_id
JOIN datamart.Dim_Plant            dpl ON dpl.plant_id   = fp.plant_id;


-- --------------------------------------------------------
-- sem_inventory_base
-- Single business-friendly inventory snapshot grain
-- --------------------------------------------------------
CREATE OR REPLACE VIEW sem_inventory_base AS
SELECT
    fi.inventory_id,
    fi.snapshot_date,
    dt.year_month,
    dt.year,
    dt.month,
    dp.product_id,
    dp.product_name,
    dp.category,
    dp.brand,
    dpl.plant_id,
    dpl.plant_name,
    dpl.state,
    fi.opening_stock,
    fi.closing_stock,
    fi.stock_value,
    fi.days_of_inventory
FROM datamart.Fact_Inventory       fi
JOIN datamart.Dim_Product          dp  ON dp.product_id = fi.product_id
JOIN datamart.Dim_Time             dt  ON dt.time_id     = fi.time_id
JOIN datamart.Dim_Plant            dpl ON dpl.plant_id   = fi.plant_id;


-- ============================================================
-- COMPONENT 2 — KPI VIEWS
-- Purpose: predefined, certified business metric calculations.
-- ============================================================

-- --------------------------------------------------------
-- sem_monthly_sales_kpi
-- GMV and Margin aggregated at Year-Month x Region grain
-- --------------------------------------------------------
CREATE OR REPLACE VIEW sem_monthly_sales_kpi AS
SELECT
    year_month,
    year,
    month,
    region,
    zone,
    SUM(gmv)                                        AS gmv,
    SUM(margin)                                     AS margin,
    SUM(net_revenue)                                AS net_revenue,
    SUM(quantity)                                   AS total_quantity,
    COUNT(DISTINCT sale_id)                         AS transaction_count,
    COUNT(DISTINCT customer_id)                     AS unique_customers,
    ROUND(SUM(margin) / NULLIF(SUM(gmv), 0) * 100, 2) AS margin_pct,
    SUM(CASE WHEN is_dropship = 1 THEN gmv ELSE 0 END) AS dropship_gmv,
    SUM(CASE WHEN is_dropship = 0 THEN gmv ELSE 0 END) AS non_dropship_gmv
FROM sem_sales_base
GROUP BY
    year_month, year, month, region, zone;


-- --------------------------------------------------------
-- sem_customer_profitability
-- Customer-level profitability at monthly grain
-- --------------------------------------------------------
CREATE OR REPLACE VIEW sem_customer_profitability AS
SELECT
    year_month,
    year,
    region,
    customer_id,
    customer_name,
    customer_type,
    team,
    SUM(gmv)                                           AS gmv,
    SUM(margin)                                        AS margin,
    SUM(net_revenue)                                   AS net_revenue,
    COUNT(DISTINCT sale_id)                            AS orders,
    ROUND(SUM(margin) / NULLIF(SUM(gmv), 0) * 100, 2) AS margin_pct,
    SUM(CASE WHEN is_dropship = 1 THEN gmv ELSE 0 END) AS dropship_gmv
FROM sem_sales_base
GROUP BY
    year_month, year, region, customer_id, customer_name, customer_type, team;


-- --------------------------------------------------------
-- sem_margin_kpi
-- Margin breakdown at Category x Month grain
-- --------------------------------------------------------
CREATE OR REPLACE VIEW sem_margin_kpi AS
SELECT
    year_month,
    year,
    month,
    region,
    category,
    brand,
    SUM(gmv)                                            AS gmv,
    SUM(margin)                                         AS margin,
    ROUND(SUM(margin) / NULLIF(SUM(gmv), 0) * 100, 2)  AS margin_pct,
    SUM(net_revenue)                                    AS net_revenue,
    SUM(CASE WHEN is_dropship = 1 THEN margin ELSE 0 END) AS dropship_margin,
    SUM(CASE WHEN is_dropship = 0 THEN margin ELSE 0 END) AS non_dropship_margin
FROM sem_sales_base
GROUP BY
    year_month, year, month, region, category, brand;
