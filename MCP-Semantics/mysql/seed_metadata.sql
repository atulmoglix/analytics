-- ============================================================
-- SEED DATA: Populate meta_ tables with initial definitions
-- Run after metadata_tables.sql
-- ============================================================

USE semantic_meta;

-- --------------------------------------------------------
-- meta_column_definition seeds
-- --------------------------------------------------------
INSERT INTO meta_column_definition
    (table_name, column_name, business_name, business_definition, data_type, allowed_values, owner, sensitivity_level)
VALUES
-- Fact_Sales
('Fact_Sales', 'sale_id',       'Sale ID',          'Unique identifier for each sales transaction.',                              'INT',      NULL,                       'Data Engineering', 'Internal'),
('Fact_Sales', 'invoice_date',  'Invoice Date',     'Date the sales invoice was raised.',                                         'DATE',     NULL,                       'Data Engineering', 'Internal'),
('Fact_Sales', 'customer_id',   'Customer ID',      'Foreign key to Dim_Customer. Identifies the buying customer.',               'INT',      NULL,                       'Data Engineering', 'Internal'),
('Fact_Sales', 'product_id',    'Product ID',       'Foreign key to Dim_Product.',                                                'INT',      NULL,                       'Data Engineering', 'Internal'),
('Fact_Sales', 'plant_id',      'Plant ID',         'Foreign key to Dim_Plant. Fulfilment location.',                            'INT',      NULL,                       'Data Engineering', 'Internal'),
('Fact_Sales', 'time_id',       'Time ID',          'Foreign key to Dim_Time.',                                                   'INT',      NULL,                       'Data Engineering', 'Internal'),
('Fact_Sales', 'gmv',           'GMV',              'Gross Merchandise Value. Total invoice value before any deductions.',        'DECIMAL',  NULL,                       'Analytics',        'Confidential'),
('Fact_Sales', 'margin',        'Margin',           'Absolute margin earned on the transaction (GMV minus COGS).',                'DECIMAL',  NULL,                       'Analytics',        'Confidential'),
('Fact_Sales', 'net_revenue',   'Net Revenue',      'GMV net of discounts and returns.',                                          'DECIMAL',  NULL,                       'Analytics',        'Confidential'),
('Fact_Sales', 'quantity',      'Quantity',         'Number of units sold in the transaction.',                                   'INT',      NULL,                       'Data Engineering', 'Internal'),
('Fact_Sales', 'discount',      'Discount',         'Total discount value applied on the invoice.',                               'DECIMAL',  NULL,                       'Analytics',        'Internal'),
('Fact_Sales', 'is_dp',         'Is Dropship',      'Indicates whether the transaction is fulfilled via Dropship model.',         'TINYINT',  '1 = Dropship, 0 = Non-Dropship', 'Analytics', 'Internal'),

-- Dim_Customer
('Dim_Customer', 'customer_id',   'Customer ID',    'Unique customer identifier.',                                                 'INT',    NULL,  'Data Engineering', 'Internal'),
('Dim_Customer', 'customer_name', 'Customer Name',  'Registered business name of the customer.',                                  'VARCHAR',NULL,  'Data Engineering', 'Confidential'),
('Dim_Customer', 'region',        'Region',         'Geographical sales region the customer belongs to.',                         'VARCHAR',NULL,  'Data Engineering', 'Internal'),
('Dim_Customer', 'zone',          'Zone',           'Sub-region or zone classification within a region.',                         'VARCHAR',NULL,  'Data Engineering', 'Internal'),
('Dim_Customer', 'team',          'Sales Team',     'Sales team responsible for managing this customer account.',                 'VARCHAR',NULL,  'Data Engineering', 'Internal'),
('Dim_Customer', 'customer_type', 'Customer Type',  'Segment classification of the customer (e.g., Enterprise, SMB, Long-Tail).', 'VARCHAR',NULL,  'Data Engineering', 'Internal'),

-- Dim_Product
('Dim_Product', 'product_id',   'Product ID',       'Unique product/SKU identifier.',           'INT',    NULL, 'Data Engineering', 'Internal'),
('Dim_Product', 'product_name', 'Product Name',     'Display name of the product/SKU.',         'VARCHAR',NULL, 'Data Engineering', 'Internal'),
('Dim_Product', 'category',     'Category',         'L1 product category (e.g., Safety, MRO).',  'VARCHAR',NULL, 'Data Engineering', 'Internal'),
('Dim_Product', 'brand',        'Brand',            'Manufacturer brand of the product.',        'VARCHAR',NULL, 'Data Engineering', 'Internal'),

-- Dim_Time
('Dim_Time', 'time_id',    'Time ID',    'Surrogate key for the date dimension.',        'INT',    NULL, 'Data Engineering', 'Internal'),
('Dim_Time', 'year_month', 'Year Month', 'Calendar period in YYYY-MM format.',           'VARCHAR',NULL, 'Data Engineering', 'Internal'),
('Dim_Time', 'year',       'Year',       'Calendar year.',                               'INT',    NULL, 'Data Engineering', 'Internal'),
('Dim_Time', 'quarter',    'Quarter',    'Fiscal/Calendar quarter (Q1–Q4).',             'VARCHAR',NULL, 'Data Engineering', 'Internal'),
('Dim_Time', 'month',      'Month',      'Month number (1–12).',                         'INT',    NULL, 'Data Engineering', 'Internal'),

-- Dim_Plant
('Dim_Plant', 'plant_id',   'Plant ID',   'Unique identifier for a fulfilment plant.',   'INT',    NULL, 'Data Engineering', 'Internal'),
('Dim_Plant', 'plant_name', 'Plant Name', 'Name of the fulfilment plant.',               'VARCHAR',NULL, 'Data Engineering', 'Internal'),
('Dim_Plant', 'state',      'State',      'Indian state where the plant is located.',    'VARCHAR',NULL, 'Data Engineering', 'Internal')
;


-- --------------------------------------------------------
-- meta_kpi_definition seeds
-- --------------------------------------------------------
INSERT INTO meta_kpi_definition
    (kpi_name, display_name, business_definition, formula_sql, grain, owner, certified_flag, certified_by, certified_on, source_view)
VALUES
(
    'GMV',
    'Gross Merchandise Value',
    'Total value of goods invoiced to customers before discounts, returns, or deductions. Primary top-line revenue indicator.',
    'SUM(gmv)',
    'Customer x Invoice Date',
    'Analytics',
    1, 'Atul Rai', '2024-01-01',
    'sem_monthly_sales_kpi'
),
(
    'Margin',
    'Absolute Margin',
    'Gross profit earned on sales. Calculated as GMV minus Cost of Goods Sold (COGS). Represents the absolute earnings before operating expenses.',
    'SUM(margin)',
    'Customer x Invoice Date',
    'Analytics',
    1, 'Atul Rai', '2024-01-01',
    'sem_monthly_sales_kpi'
),
(
    'Margin_Pct',
    'Margin Percentage',
    'Margin as a percentage of GMV. Key profitability efficiency metric.',
    'ROUND(SUM(margin) / NULLIF(SUM(gmv), 0) * 100, 2)',
    'Customer x Month x Region',
    'Analytics',
    1, 'Atul Rai', '2024-01-01',
    'sem_margin_kpi'
),
(
    'Net_Revenue',
    'Net Revenue',
    'GMV net of trade discounts and sales returns. Represents actual recognised revenue.',
    'SUM(net_revenue)',
    'Customer x Invoice Date',
    'Analytics',
    1, 'Atul Rai', '2024-01-01',
    'sem_monthly_sales_kpi'
),
(
    'Dropship_GMV',
    'Dropship GMV',
    'GMV from transactions where goods are shipped directly from the vendor to the customer (is_dp = 1). Used to monitor Dropship channel contribution.',
    'SUM(CASE WHEN is_dropship = 1 THEN gmv ELSE 0 END)',
    'Customer x Month',
    'Analytics',
    1, 'Atul Rai', '2024-01-01',
    'sem_monthly_sales_kpi'
),
(
    'Customer_Profitability',
    'Customer Profitability',
    'Margin earned per customer over a time period. Used in customer tiering and opex allocation decisions.',
    'SUM(margin) at customer_id grain',
    'Customer x Month',
    'Analytics',
    1, 'Atul Rai', '2024-01-01',
    'sem_customer_profitability'
)
;


-- --------------------------------------------------------
-- meta_business_rules seeds
-- --------------------------------------------------------
INSERT INTO meta_business_rules
    (rule_name, rule_description, source_tables, effective_from, effective_to, owner)
VALUES
(
    'GMV Definition',
    'GMV is the total invoice value billed to the customer. It includes the product cost and any applicable charges. It does NOT include GST. Returns and credit notes are netted separately and reflected in Net Revenue, not GMV.',
    'Fact_Sales',
    '2020-01-01', NULL,
    'Analytics'
),
(
    'Dropship Definition',
    'A transaction is classified as Dropship (is_dp = 1) when the goods are shipped directly from the vendor/supplier to the end customer without passing through a Moglix warehouse. Non-Dropship (is_dp = 0) means fulfilment from a Moglix plant/warehouse.',
    'Fact_Sales',
    '2020-01-01', NULL,
    'Analytics'
),
(
    'Customer Ownership Logic',
    'A customer is owned by the Sales Team that is tagged in Dim_Customer.team. In case of reassignment, historical transactions retain the old team tag; only new transactions carry the new team. Customer ownership disputes are resolved by the Revenue Operations team.',
    'Dim_Customer',
    '2020-01-01', NULL,
    'Revenue Operations'
),
(
    'Margin Calculation',
    'Margin = GMV - COGS. COGS is loaded from the procurement system via Fact_Purchase and allocated to sold units using a FIFO/WAC (Weighted Average Cost) methodology refreshed monthly. Margin figures for the current month are provisional until COGS is finalised at month-close.',
    'Fact_Sales, Fact_Purchase',
    '2020-01-01', NULL,
    'Analytics'
),
(
    'Opex Allocation',
    'Customer-level opex (warehousing, last-mile logistics, account management costs) is allocated proportionally to GMV within the customer segment. Allocation coefficients are reviewed quarterly by Finance.',
    'Fact_Sales',
    '2022-01-01', NULL,
    'Finance'
)
;


-- --------------------------------------------------------
-- meta_data_quality_rules seeds
-- --------------------------------------------------------
INSERT INTO meta_data_quality_rules
    (rule_name, target_table, target_column, validation_logic, severity, owner)
VALUES
(
    'Sales GMV Non-Negative',
    'Fact_Sales', 'gmv',
    'gmv < 0',
    'Critical',
    'Data Engineering'
),
(
    'Sales Invoice Date Not Future',
    'Fact_Sales', 'invoice_date',
    'invoice_date > CURDATE()',
    'High',
    'Data Engineering'
),
(
    'Sales Customer ID Orphan',
    'Fact_Sales', 'customer_id',
    'customer_id NOT IN (SELECT customer_id FROM datamart.Dim_Customer)',
    'Critical',
    'Data Engineering'
),
(
    'Sales Product ID Orphan',
    'Fact_Sales', 'product_id',
    'product_id NOT IN (SELECT product_id FROM datamart.Dim_Product)',
    'Critical',
    'Data Engineering'
),
(
    'Sales IS_DP Invalid Value',
    'Fact_Sales', 'is_dp',
    'is_dp NOT IN (0, 1)',
    'High',
    'Data Engineering'
),
(
    'Inventory Closing Stock Negative',
    'Fact_Inventory', 'closing_stock',
    'closing_stock < 0',
    'Medium',
    'Data Engineering'
)
;


-- --------------------------------------------------------
-- meta_data_ownership seeds
-- --------------------------------------------------------
INSERT INTO meta_data_ownership
    (asset_type, asset_name, data_owner, business_owner, sensitivity_level)
VALUES
('Table', 'Fact_Sales',               'Data Engineering', 'Analytics',         'Confidential'),
('Table', 'Fact_Purchase',            'Data Engineering', 'Supply Chain',       'Confidential'),
('Table', 'Fact_Inventory',           'Data Engineering', 'Supply Chain',       'Confidential'),
('Table', 'Dim_Customer',             'Data Engineering', 'Revenue Operations', 'Confidential'),
('Table', 'Dim_Product',              'Data Engineering', 'Category',           'Internal'),
('Table', 'Dim_Time',                 'Data Engineering', 'Analytics',          'Public'),
('Table', 'Dim_Plant',                'Data Engineering', 'Operations',         'Internal'),
('View',  'sem_sales_base',           'Analytics',        'Analytics',          'Confidential'),
('View',  'sem_monthly_sales_kpi',    'Analytics',        'Analytics',          'Confidential'),
('View',  'sem_customer_profitability','Analytics',       'Analytics',          'Confidential'),
('View',  'sem_margin_kpi',           'Analytics',        'Analytics',          'Confidential'),
('KPI',   'GMV',                      'Analytics',        'Analytics',          'Confidential'),
('KPI',   'Margin',                   'Analytics',        'Finance',            'Confidential'),
('KPI',   'Margin_Pct',               'Analytics',        'Finance',            'Confidential'),
('KPI',   'Dropship_GMV',             'Analytics',        'Analytics',          'Confidential')
;
