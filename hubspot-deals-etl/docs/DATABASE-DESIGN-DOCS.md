# 🗄️ HubSpot Deals ETL - Database Schema

This document provides the complete database schema for the HubSpot Deals ETL service with two core tables: ScanJob and HubSpot Deals.

---

## 📋 Overview

The HubSpot Deals ETL database schema consists of two main tables:

1. **scan_jobs** - Core scan job management and tracking
2. **hubspot_deals** - Storage for extracted HubSpot Deal data

---

## 🏗️ Table 1: scan_jobs

**Purpose**: Core scan job management and status tracking

| **Column Name**         | **Type**    | **Constraints**           | **Description**                          |
|-------------------------|-------------|---------------------------|------------------------------------------|
| `id`                    | VARCHAR     | PRIMARY KEY               | Unique internal identifier               |
| `scan_id`               | VARCHAR     | UNIQUE, NOT NULL, INDEX   | External scan identifier                 |
| `status`                | VARCHAR     | NOT NULL, INDEX           | pending, running, completed, failed, cancelled |
| `scan_type`             | VARCHAR     | NOT NULL                  | Type of scan (full, incremental)         |
| `config`                | JSON        | NOT NULL                  | Scan configuration and parameters        |
| `organization_id`       | VARCHAR     | NULLABLE                  | Organization/tenant identifier           |
| `error_message`         | TEXT        | NULLABLE                  | Error details if scan failed            |
| `started_at`            | TIMESTAMP   | NULLABLE                  | When scan execution started             |
| `completed_at`          | TIMESTAMP   | NULLABLE                  | When scan finished                      |
| `total_items`           | INTEGER     | DEFAULT 0                 | Total items to process                  |
| `processed_items`       | INTEGER     | DEFAULT 0                 | Items successfully processed            |
| `failed_items`          | INTEGER     | DEFAULT 0                 | Items that failed processing            |
| `success_rate`          | VARCHAR     | NULLABLE                  | Calculated success percentage           |
| `batch_size`            | INTEGER     | DEFAULT 50                | Processing batch size                   |
| `created_at`            | TIMESTAMP   | NOT NULL                  | Record creation timestamp               |
| `updated_at`            | TIMESTAMP   | NOT NULL                  | Record last update timestamp            |

### **SQL Definition - scan_jobs**

```sql
CREATE TABLE scan_jobs (
    id VARCHAR(100) PRIMARY KEY,
    scan_id VARCHAR(100) UNIQUE NOT NULL,
    status VARCHAR(50) NOT NULL CHECK (status IN ('pending', 'running', 'completed', 'failed', 'cancelled')),
    scan_type VARCHAR(50) NOT NULL CHECK (scan_type IN ('full', 'incremental')),
    config JSON NOT NULL,
    organization_id VARCHAR(100),
    error_message TEXT,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    total_items INTEGER DEFAULT 0 CHECK (total_items >= 0),
    processed_items INTEGER DEFAULT 0 CHECK (processed_items >= 0),
    failed_items INTEGER DEFAULT 0 CHECK (failed_items >= 0),
    success_rate VARCHAR(20),
    batch_size INTEGER DEFAULT 50,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
```

### **Indexes - scan_jobs**

```sql
CREATE INDEX idx_scan_status_created ON scan_jobs(status, created_at);
CREATE INDEX idx_scan_id_status ON scan_jobs(scan_id, status);
CREATE INDEX idx_scan_type_status ON scan_jobs(scan_type, status);
CREATE INDEX idx_scan_org_status ON scan_jobs(organization_id, status);
```

---

## 🧩 Table 2: hubspot_deals

**Purpose**: Store normalized HubSpot Deal records for ETL, reporting, and analytics.

### **SQL Definition - hubspot_deals**

```sql
CREATE TABLE hubspot_deals (
    -- Primary Key & Identifiers
    deal_id VARCHAR(50) PRIMARY KEY,
    hs_object_id VARCHAR(50) NOT NULL,
    
    -- Deal Core Information
    deal_name VARCHAR(500),
    pipeline VARCHAR(100),
    dealstage VARCHAR(100),
    dealtype VARCHAR(100),
    amount DECIMAL(15, 2) CHECK (amount IS NULL OR amount >= 0),
    currency VARCHAR(10) DEFAULT 'USD',
    close_date TIMESTAMP WITH TIME ZONE,
    description TEXT,
    
    -- Owner & Assignment
    owner_id VARCHAR(50),
    hubspot_owner_id VARCHAR(50),
    
    -- Deal Metrics
    num_associated_contacts INTEGER DEFAULT 0,
    num_associated_companies INTEGER DEFAULT 0,
    hs_forecast_amount DECIMAL(15, 2),
    hs_forecast_probability DECIMAL(5, 2) CHECK (hs_forecast_probability IS NULL OR (hs_forecast_probability BETWEEN 0 AND 100)),
    
    -- Status Flags
    is_archived BOOLEAN DEFAULT FALSE,
    archived BOOLEAN DEFAULT FALSE,
    hs_is_closed_won BOOLEAN DEFAULT FALSE,
    hs_is_closed_lost BOOLEAN DEFAULT FALSE,
    
    -- Priority
    hs_priority VARCHAR(50),
    
    -- HubSpot Timestamps
    createdate TIMESTAMP WITH TIME ZONE,
    hs_lastmodifieddate TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE,
    
    -- Raw Data Storage
    raw_properties JSON NOT NULL,
    
    -- ETL Metadata (CRITICAL - Required by Task 1.3)
    extracted_at TIMESTAMP WITH TIME ZONE NOT NULL,
    scan_job_id VARCHAR(100) NOT NULL,
    _tenant_id VARCHAR(100) NOT NULL,
    _extracted_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    _scan_id VARCHAR(100) NOT NULL,
    _load_id VARCHAR(100),
    _dlt_id VARCHAR(100) UNIQUE,
    
    -- Data Quality & Versioning
    _source_system VARCHAR(50) DEFAULT 'hubspot',
    _api_version VARCHAR(20) DEFAULT 'v3',
    _is_deleted BOOLEAN DEFAULT FALSE,
    
    -- Foreign Key
    CONSTRAINT fk_scan_job FOREIGN KEY (scan_job_id) REFERENCES scan_jobs(id) ON DELETE CASCADE
);
```

### **Column Definitions - hubspot_deals**

| Column Name | Data Type | Constraints | Description |
|-----------|----------|------------|------------|
| `deal_id` | VARCHAR(50) | PRIMARY KEY | Unique Deal ID from HubSpot |
| `hs_object_id` | VARCHAR(50) | NOT NULL | HubSpot internal object ID |
| `deal_name` | VARCHAR(500) | NULLABLE | Deal name |
| `pipeline` | VARCHAR(100) | NULLABLE | Sales pipeline ID |
| `dealstage` | VARCHAR(100) | NULLABLE | Current deal stage |
| `dealtype` | VARCHAR(100) | NULLABLE | Type of deal (newbusiness, existingbusiness) |
| `amount` | DECIMAL(15,2) | NULLABLE | Deal amount |
| `currency` | VARCHAR(10) | DEFAULT 'USD' | Deal currency |
| `close_date` | TIMESTAMP | NULLABLE | Expected close date |
| `description` | TEXT | NULLABLE | Deal description |
| `owner_id` | VARCHAR(50) | NULLABLE | HubSpot owner ID (legacy) |
| `hubspot_owner_id` | VARCHAR(50) | NULLABLE | HubSpot owner ID |
| `num_associated_contacts` | INTEGER | DEFAULT 0 | Number of associated contacts |
| `num_associated_companies` | INTEGER | DEFAULT 0 | Number of associated companies |
| `hs_forecast_amount` | DECIMAL(15,2) | NULLABLE | Forecasted amount |
| `hs_forecast_probability` | DECIMAL(5,2) | NULLABLE | Win probability (0-100) |
| `is_archived` | BOOLEAN | DEFAULT FALSE | Archived flag (legacy) |
| `archived` | BOOLEAN | DEFAULT FALSE | Archived flag |
| `hs_is_closed_won` | BOOLEAN | DEFAULT FALSE | Closed won status |
| `hs_is_closed_lost` | BOOLEAN | DEFAULT FALSE | Closed lost status |
| `hs_priority` | VARCHAR(50) | NULLABLE | Deal priority |
| `createdate` | TIMESTAMP | NULLABLE | HubSpot creation date |
| `hs_lastmodifieddate` | TIMESTAMP | NULLABLE | Last modified date in HubSpot |
| `created_at` | TIMESTAMP | NULLABLE | HubSpot API createdAt |
| `updated_at` | TIMESTAMP | NULLABLE | HubSpot API updatedAt |
| `raw_properties` | JSON | NOT NULL | Full properties object from HubSpot API |
| `extracted_at` | TIMESTAMP | NOT NULL | ETL extraction timestamp (legacy) |
| `scan_job_id` | VARCHAR(100) | NOT NULL, INDEX | Reference to scan_jobs.id |
| **`_tenant_id`** | **VARCHAR(100)** | **NOT NULL** | **Multi-tenant identifier** |
| **`_extracted_at`** | **TIMESTAMP** | **NOT NULL** | **UTC timestamp of extraction** |
| **`_scan_id`** | **VARCHAR(100)** | **NOT NULL** | **Scan batch identifier** |
| **`_load_id`** | **VARCHAR(100)** | **NULLABLE** | **DLT load identifier** |
| **`_dlt_id`** | **VARCHAR(100)** | **UNIQUE** | **DLT unique row identifier** |
| `_source_system` | VARCHAR(50) | DEFAULT 'hubspot' | Source system identifier |
| `_api_version` | VARCHAR(20) | DEFAULT 'v3' | HubSpot API version |
| `_is_deleted` | BOOLEAN | DEFAULT FALSE | Soft delete flag |

---

### 🔑 **Indexes - hubspot_deals**

```sql
-- Foreign Key Index
CREATE INDEX idx_deals_scan_job ON hubspot_deals(scan_job_id);

-- Pipeline & Stage Analysis
CREATE INDEX idx_deals_pipeline ON hubspot_deals(pipeline);
CREATE INDEX idx_deals_stage ON hubspot_deals(dealstage);
CREATE INDEX idx_deals_pipeline_stage ON hubspot_deals(pipeline, dealstage);

-- Owner Queries
CREATE INDEX idx_deals_owner ON hubspot_deals(owner_id);
CREATE INDEX idx_deals_hubspot_owner ON hubspot_deals(hubspot_owner_id);

-- Date-Based Queries
CREATE INDEX idx_deals_updated ON hubspot_deals(updated_at);
CREATE INDEX idx_deals_closedate ON hubspot_deals(close_date) WHERE close_date IS NOT NULL;
CREATE INDEX idx_deals_createdate ON hubspot_deals(createdate) WHERE createdate IS NOT NULL;
CREATE INDEX idx_deals_lastmodified ON hubspot_deals(hs_lastmodifieddate) WHERE hs_lastmodifieddate IS NOT NULL;

-- ETL Metadata Indexes (CRITICAL for performance)
CREATE INDEX idx_deals_tenant ON hubspot_deals(_tenant_id);
CREATE INDEX idx_deals_extracted_at ON hubspot_deals(_extracted_at);
CREATE INDEX idx_deals_scan_id ON hubspot_deals(_scan_id);
CREATE UNIQUE INDEX idx_deals_dlt_id ON hubspot_deals(_dlt_id) WHERE _dlt_id IS NOT NULL;

-- Status Queries
CREATE INDEX idx_deals_archived ON hubspot_deals(archived);
CREATE INDEX idx_deals_won ON hubspot_deals(hs_is_closed_won) WHERE hs_is_closed_won = TRUE;
CREATE INDEX idx_deals_lost ON hubspot_deals(hs_is_closed_lost) WHERE hs_is_closed_lost = TRUE;

-- Composite Indexes for Common Queries
CREATE INDEX idx_deals_tenant_closedate ON hubspot_deals(_tenant_id, close_date) 
    WHERE close_date IS NOT NULL AND archived = FALSE;
CREATE INDEX idx_deals_owner_stage ON hubspot_deals(hubspot_owner_id, dealstage) 
    WHERE hubspot_owner_id IS NOT NULL;
```

---

## 🔗 Relationships

### Primary Relationships
```sql
-- ScanJob to HubSpot Deals (One-to-Many)
scan_jobs.id ← hubspot_deals.scan_job_id
```

### Cascade Behavior
- **DELETE ScanJob**: Cascades to delete all related hubspot_deals records

### Relationship Diagram
```
┌─────────────────┐         1:N        ┌─────────────────┐
│   scan_jobs     │───────────────────▶│ hubspot_deals   │
│                 │                     │                 │
│ - id (PK)       │                     │ - deal_id (PK)  │
│ - scan_id       │                     │ - scan_job_id   │
│ - status        │                     │   (FK)          │
│ - org_id        │                     │ - _tenant_id    │
└─────────────────┘                     └─────────────────┘
```

---

## 📊 Common Queries

### **Scan Job Management**

```sql
-- Get scan job with status
SELECT id, scan_id, status, scan_type, total_items, processed_items 
FROM scan_jobs 
WHERE scan_id = 'scan_20250127_103000';

-- Get active scans
SELECT scan_id, status, started_at, scan_type 
FROM scan_jobs 
WHERE status IN ('running', 'pending') 
ORDER BY created_at DESC;

-- Get scan progress
SELECT 
    scan_id,
    total_items,
    processed_items,
    failed_items,
    CASE 
        WHEN total_items > 0 THEN ROUND((processed_items * 100.0 / total_items), 2)
        ELSE 0 
    END as progress_percentage,
    success_rate
FROM scan_jobs 
WHERE scan_id = 'scan_20250127_103000';
```

### **Deal Data Queries**

```sql
-- Get HubSpot Deals for a scan job
SELECT 
    deal_id,
    deal_name,
    dealstage,
    amount,
    pipeline,
    owner_id,
    close_date,
    updated_at
FROM hubspot_deals
WHERE scan_job_id = 'uuid-job-001'
ORDER BY updated_at DESC
LIMIT 100 OFFSET 0;

-- Get deals for specific tenant
SELECT 
    deal_id,
    deal_name,
    amount,
    dealstage,
    close_date
FROM hubspot_deals
WHERE _tenant_id = 'acme_corp_prod'
    AND archived = FALSE
ORDER BY close_date ASC;

-- Count deals by stage
SELECT dealstage, COUNT(*) AS total_deals, SUM(amount) as total_value
FROM hubspot_deals
WHERE scan_job_id = 'uuid-job-001'
GROUP BY dealstage
ORDER BY total_value DESC;

-- Search deals by name
SELECT deal_id, deal_name, amount, dealstage
FROM hubspot_deals
WHERE scan_job_id = 'uuid-job-001'
AND deal_name ILIKE '%Enterprise%';

-- Monthly deal pipeline report
SELECT 
    dealstage,
    COUNT(*) as deal_count,
    SUM(amount) as total_value,
    AVG(amount) as avg_value
FROM hubspot_deals
WHERE _tenant_id = 'acme_corp_prod'
    AND archived = FALSE
    AND close_date >= DATE_TRUNC('month', CURRENT_DATE)
    AND close_date < DATE_TRUNC('month', CURRENT_DATE) + INTERVAL '1 month'
GROUP BY dealstage
ORDER BY total_value DESC;

-- Deals won this quarter
SELECT 
    deal_id,
    deal_name,
    amount,
    close_date,
    hubspot_owner_id
FROM hubspot_deals
WHERE _tenant_id = 'acme_corp_prod'
    AND hs_is_closed_won = TRUE
    AND close_date >= DATE_TRUNC('quarter', CURRENT_DATE)
ORDER BY amount DESC;

-- Owner performance analysis
SELECT 
    hubspot_owner_id,
    COUNT(*) as total_deals,
    SUM(CASE WHEN hs_is_closed_won THEN 1 ELSE 0 END) as won_deals,
    SUM(amount) as total_value,
    AVG(amount) as avg_deal_value
FROM hubspot_deals
WHERE _tenant_id = 'acme_corp_prod'
    AND archived = FALSE
    AND createdate >= CURRENT_DATE - INTERVAL '90 days'
GROUP BY hubspot_owner_id
ORDER BY total_value DESC;

-- Incremental extraction query
SELECT deal_id, hs_lastmodifieddate
FROM hubspot_deals
WHERE _tenant_id = 'acme_corp_prod'
    AND hs_lastmodifieddate > (
        SELECT MAX(_extracted_at) 
        FROM hubspot_deals 
        WHERE _tenant_id = 'acme_corp_prod'
    )
ORDER BY hs_lastmodifieddate ASC;
```

### **Control Operations**

```sql
-- Get scan job status and basic info
SELECT scan_id, status, started_at, completed_at, error_message
FROM scan_jobs 
WHERE scan_id = 'scan_20250127_103000';

-- Cancel a scan (update status)
UPDATE scan_jobs 
SET status = 'cancelled', 
    completed_at = CURRENT_TIMESTAMP,
    updated_at = CURRENT_TIMESTAMP,
    error_message = 'Cancelled by user'
WHERE scan_id = 'scan_20250127_103000' 
AND status IN ('pending', 'running');
```

---

## 🛠️ Implementation Examples

### **Creating a New Scan Job**

```sql
-- Create scan job for HubSpot Deals extraction
INSERT INTO scan_jobs (
    id, 
    scan_id, 
    status, 
    scan_type, 
    config, 
    organization_id, 
    batch_size
) VALUES (
    'uuid-job-001', 
    'scan_20250127_103000', 
    'pending', 
    'full', 
    '{"hubspot_access_token": "pat-na1-xxxxx", "properties": ["dealname", "amount", "dealstage"], "batch_size": 100}'::json,
    'acme_corp_prod', 
    100
);
```

### **Adding Deal Records**

```sql
-- Insert HubSpot Deal
INSERT INTO hubspot_deals (
    deal_id,
    hs_object_id,
    deal_name,
    dealstage,
    dealtype,
    amount,
    currency,
    pipeline,
    close_date,
    owner_id,
    hubspot_owner_id,
    raw_properties,
    extracted_at,
    scan_job_id,
    _tenant_id,
    _scan_id,
    createdate,
    updated_at
) VALUES (
    '12345678901',
    '12345678901',
    'Enterprise Software License - Acme Corp',
    'presentationscheduled',
    'newbusiness',
    50000.00,
    'USD',
    'default',
    '2025-03-15 00:00:00+00',
    'owner-001',
    'owner-001',
    '{"dealname": "Enterprise Software License", "amount": "50000", "dealstage": "presentationscheduled"}'::json,
    CURRENT_TIMESTAMP,
    'uuid-job-001',
    'acme_corp_prod',
    'scan_20250127_103000',
    '2025-01-15 10:30:00+00',
    '2025-01-26 08:15:00+00'
);

-- Update scan job progress
UPDATE scan_jobs 
SET processed_items = processed_items + 1,
    updated_at = CURRENT_TIMESTAMP
WHERE id = 'uuid-job-001';
```

### **Status Updates**

```sql
-- Start scan
UPDATE scan_jobs 
SET status = 'running', 
    started_at = CURRENT_TIMESTAMP,
    updated_at = CURRENT_TIMESTAMP
WHERE scan_id = 'scan_20250127_103000';

-- Complete scan
UPDATE scan_jobs 
SET status = 'completed', 
    completed_at = CURRENT_TIMESTAMP,
    updated_at = CURRENT_TIMESTAMP,
    success_rate = CASE 
        WHEN total_items > 0 THEN 
            ROUND(((total_items - failed_items) * 100.0 / total_items), 2)::TEXT || '%'
        ELSE '100%' 
    END
WHERE scan_id = 'scan_20250127_103000';
```

---

## 📈 Performance Considerations

### **Indexing Strategy**
- **Primary Operations**: Index on `scan_id`, `status`, `deal_id`
- **Multi-Tenancy**: Index on `_tenant_id` (CRITICAL)
- **Filtering**: Index on `pipeline`, `dealstage`, `owner_id`
- **Pagination**: Composite indexes on frequently queried columns
- **Foreign Keys**: Always index foreign key columns (`scan_job_id`)
- **Date Ranges**: Index on date columns (`close_date`, `hs_lastmodifieddate`)

### **Data Retention**

```sql
-- Archive completed scans older than 90 days
CREATE TABLE scan_jobs_archive AS SELECT * FROM scan_jobs WHERE FALSE;

-- Move old data
INSERT INTO scan_jobs_archive 
SELECT * FROM scan_jobs 
WHERE status = 'completed' 
AND completed_at < CURRENT_DATE - INTERVAL '90 days';

-- Clean up
DELETE FROM scan_jobs 
WHERE status = 'completed' 
AND completed_at < CURRENT_DATE - INTERVAL '90 days';
```

---

## 🛡️ Data Integrity

### **Constraints**

```sql
-- Ensure valid status values
ALTER TABLE scan_jobs ADD CONSTRAINT check_valid_status 
CHECK (status IN ('pending', 'running', 'completed', 'failed', 'cancelled'));

-- Ensure valid scan types
ALTER TABLE scan_jobs ADD CONSTRAINT check_valid_scan_type
CHECK (scan_type IN ('full', 'incremental'));

-- Ensure positive values
ALTER TABLE scan_jobs ADD CONSTRAINT check_positive_counts 
CHECK (total_items >= 0 AND processed_items >= 0 AND failed_items >= 0);

-- Ensure valid deal amounts
ALTER TABLE hubspot_deals ADD CONSTRAINT check_deal_amount
CHECK (amount IS NULL OR amount >= 0);

-- Ensure valid probability range
ALTER TABLE hubspot_deals ADD CONSTRAINT check_probability_range
CHECK (hs_forecast_probability IS NULL OR (hs_forecast_probability BETWEEN 0 AND 100));
```

### **Triggers**

```sql
-- Auto-update timestamps for scan_jobs
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_scan_jobs_updated_at
    BEFORE UPDATE ON scan_jobs 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at();

-- Auto-update timestamps for hubspot_deals
CREATE TRIGGER trigger_hubspot_deals_updated_at
    BEFORE UPDATE ON hubspot_deals 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at();
```

---

## 💡 Best Practices

1. **Use appropriate batch sizes** for your data volume (default: 100 for HubSpot)
2. **Implement proper error handling** and store error details in `error_message`
3. **Regular cleanup** of old scan jobs and results based on retention policies
4. **Monitor scan progress** using `processed_items` and `failed_items`
5. **Use JSON config** to store flexible scan parameters and authentication details
6. **Always filter by `_tenant_id`** for multi-tenant queries
7. **Use `_scan_id`** to track and group extraction batches
8. **Leverage `_dlt_id`** for DLT framework integration

### **Common Patterns**

- **Progress Tracking**: Update `processed_items` and `failed_items` as scan progresses
- **Error Recovery**: Store detailed error information in `error_message` field
- **Flexible Configuration**: Use JSON `config` field for scan parameters, auth details, filters
- **Status Management**: Use clear status transitions (pending → running → completed/failed/cancelled)
- **Data Organization**: Use meaningful `scan_id` values for easy identification (e.g., `scan_20250127_103000`)
- **Multi-Tenancy**: Always include `_tenant_id` in WHERE clauses for security

---

**Database Schema Version**: 2.0  
**Last Updated**: January 27, 2025  
**Compatible With**: PostgreSQL 12+, MySQL 8.0+, SQLite 3.35+