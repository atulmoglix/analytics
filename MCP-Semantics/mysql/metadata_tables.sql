-- ============================================================
-- METADATA REPOSITORY: All meta_ tables live in a dedicated
-- schema (semantic_meta) created below.
-- ============================================================

CREATE DATABASE IF NOT EXISTS semantic_meta
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE semantic_meta;

-- --------------------------------------------------------
-- Column-level data dictionary
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS meta_column_definition (
    id               INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    table_name       VARCHAR(100)  NOT NULL,
    column_name      VARCHAR(100)  NOT NULL,
    business_name    VARCHAR(200)  NOT NULL,
    business_definition TEXT       NOT NULL,
    data_type        VARCHAR(50)   NOT NULL,
    allowed_values   TEXT          NULL COMMENT 'JSON or free-text list, e.g. "1=Dropship, 0=Non-Dropship"',
    owner            VARCHAR(100)  NOT NULL,
    sensitivity_level ENUM('Public','Internal','Confidential','Restricted') NOT NULL DEFAULT 'Internal',
    is_active        TINYINT(1)   NOT NULL DEFAULT 1,
    created_at       DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at       DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uq_table_column (table_name, column_name)
);

-- --------------------------------------------------------
-- KPI / Metric registry
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS meta_kpi_definition (
    id                  INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    kpi_name            VARCHAR(100)  NOT NULL UNIQUE,
    display_name        VARCHAR(200)  NOT NULL,
    business_definition TEXT          NOT NULL,
    formula_sql         TEXT          NOT NULL COMMENT 'SQL fragment or reference view name',
    grain               VARCHAR(200)  NOT NULL COMMENT 'e.g. Customer x Month x Region',
    owner               VARCHAR(100)  NOT NULL,
    certified_flag      TINYINT(1)   NOT NULL DEFAULT 0,
    certified_by        VARCHAR(100)  NULL,
    certified_on        DATE          NULL,
    source_view         VARCHAR(100)  NULL,
    is_active           TINYINT(1)   NOT NULL DEFAULT 1,
    created_at          DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at          DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- --------------------------------------------------------
-- Business rules documentation
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS meta_business_rules (
    id               INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    rule_name        VARCHAR(200)  NOT NULL UNIQUE,
    rule_description TEXT          NOT NULL,
    source_tables    VARCHAR(500)  NULL COMMENT 'Comma-separated list of tables this rule applies to',
    effective_from   DATE          NOT NULL,
    effective_to     DATE          NULL COMMENT 'NULL = currently active',
    owner            VARCHAR(100)  NOT NULL,
    created_at       DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at       DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- --------------------------------------------------------
-- Data quality rules
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS meta_data_quality_rules (
    id               INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    rule_name        VARCHAR(200)  NOT NULL UNIQUE,
    target_table     VARCHAR(100)  NOT NULL,
    target_column    VARCHAR(100)  NULL,
    validation_logic TEXT          NOT NULL COMMENT 'SQL WHERE clause or expression that returns violating rows',
    severity         ENUM('Critical','High','Medium','Low') NOT NULL DEFAULT 'High',
    owner            VARCHAR(100)  NOT NULL,
    is_active        TINYINT(1)   NOT NULL DEFAULT 1,
    created_at       DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at       DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- --------------------------------------------------------
-- Security & ownership metadata
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS meta_data_ownership (
    id                    INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    asset_type            ENUM('Table','View','Column','KPI') NOT NULL,
    asset_name            VARCHAR(200) NOT NULL,
    data_owner            VARCHAR(100) NOT NULL,
    business_owner        VARCHAR(100) NOT NULL,
    sensitivity_level     ENUM('Public','Internal','Confidential','Restricted') NOT NULL DEFAULT 'Internal',
    access_restrictions   TEXT NULL,
    created_at            DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at            DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uq_asset (asset_type, asset_name)
);
