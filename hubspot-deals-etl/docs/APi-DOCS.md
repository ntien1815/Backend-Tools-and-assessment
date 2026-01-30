# HubSpot Deals ETL Service - API Documentation

## 📋 Table of Contents
1. [Overview](#overview)
2. [Authentication](#authentication)
3. [Base URLs](#base-urls)
4. [Common Response Formats](#common-response-formats)
5. [API Endpoints](#api-endpoints)
6. [Scan Endpoints](#scan-endpoints)
7. [Health & Stats Endpoints](#health--stats-endpoints)
8. [Error Handling](#error-handling)
9. [Examples](#examples)
10. [Rate Limiting](#rate-limiting)
11. [Changelog](#changelog)

## 🔍 Overview

The HubSpot Deals ETL Service provides REST API endpoints for extracting deal data from HubSpot CRM accounts. The service manages extraction jobs (scans), tracks progress, and provides access to extracted deal data.

### API Version
- **Version**: 1.0.0
- **Base Path**: `/api/v1`
- **Content Type**: `application/json`
- **Documentation**: Available at `/docs` (Swagger UI)

### Key Features
- **Full & Incremental Extraction**: Extract all deals or only modified deals
- **Multi-Tenant Support**: Isolate data by tenant/organization
- **Progress Tracking**: Real-time scan progress monitoring
- **Flexible Filtering**: Filter by pipeline, stage, date ranges
- **Pagination**: Efficient data retrieval with pagination support

## 🔐 Authentication

All API requests (except `/health`) require authentication using an API Key.

### Required Credentials
- **API Key**: Service-level authentication token
- **HubSpot Access Token**: Private App access token for HubSpot API (provided in scan config)

### Required Permissions
- `scans.read` - Read scan status and results
- `scans.write` - Start, cancel, and remove scans
- `deals.read` - Access extracted deal data

### Authentication Headers
```http
Authorization: Bearer <YOUR_API_KEY>
Content-Type: application/json
```

## 🌐 Base URLs

### Development
```
http://localhost:5200
```

### Staging
```
http://localhost:5201
```

### Production
```
http://localhost:5202
```

### Swagger Documentation
```
http://localhost:5200/docs
```

## 📊 Common Response Formats

### Success Response
```json
{
  "status": "success",
  "data": {},
  "message": "Operation completed successfully",
  "timestamp": "2025-01-27T10:30:00Z"
}
```

### Error Response (Validation)
```json
{
  "error": "validation_error",
  "message": "Input validation failed",
  "details": {
    "tenant_id": "Field is required",
    "config.hubspot_access_token": "Invalid token format"
  },
  "timestamp": "2025-01-27T10:30:00Z"
}
```

### Error Response (Application Logic)
```json
{
  "error": "not_found",
  "message": "Scan not found: scan_20250127_103000",
  "timestamp": "2025-01-27T10:30:00Z"
}
```

### Pagination Response
```json
{
  "pagination": {
    "page": 1,
    "limit": 100,
    "total_results": 495,
    "total_pages": 5,
    "has_next": true,
    "has_previous": false
  }
}
```

## 🔍 Scan Endpoints

### 1. Start Deal Extraction

**POST** `/api/v1/scans/start`

Initiates a new HubSpot Deals extraction scan.

#### Request Body
```json
{
  "tenant_id": "acme_corp_prod",
  "scan_type": "full",
  "config": {
    "hubspot_access_token": "pat-na1-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
    "properties": [
      "dealname",
      "amount",
      "dealstage",
      "closedate",
      "pipeline",
      "createdate",
      "dealtype"
    ],
    "filters": {
      "archived": false,
      "pipeline": "default"
    },
    "batch_size": 100
  }
}
```

#### Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `tenant_id` | string | Yes | Unique identifier for tenant/organization (max 100 chars) |
| `scan_type` | string | Yes | Type of scan: "full" or "incremental" |
| `config.hubspot_access_token` | string | Yes | HubSpot Private App Access Token |
| `config.properties` | array | No | List of deal properties to extract (default: all) |
| `config.filters.archived` | boolean | No | Include archived deals (default: false) |
| `config.filters.pipeline` | string | No | Filter by specific pipeline (default: all) |
| `config.batch_size` | integer | No | Deals per batch (default: 100, max: 100) |

#### Response (202 Accepted)
```json
{
  "status": "accepted",
  "message": "Scan initiated successfully",
  "scan_id": "scan_20250127_103000_abc123",
  "scan_job_id": "uuid-job-001",
  "tenant_id": "acme_corp_prod",
  "scan_type": "full",
  "estimated_duration_minutes": 5,
  "created_at": "2025-01-27T10:30:00Z",
  "links": {
    "self": "/api/v1/scans/scan_20250127_103000_abc123",
    "status": "/api/v1/scans/scan_20250127_103000_abc123",
    "results": "/api/v1/scans/scan_20250127_103000_abc123/results"
  }
}
```

#### Status Codes
- **202**: Scan started successfully
- **400**: Invalid request data
- **401**: Unauthorized - Invalid API key
- **409**: Scan already in progress for this tenant
- **500**: Internal server error

---

### 2. Get Scan Status

**GET** `/api/v1/scans/{scan_id}`

Retrieves the current status and progress of a scan.

#### Path Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `scan_id` | string | Yes | Unique scan identifier (e.g., scan_20250127_103000_abc123) |

#### Response (Running Scan)
```json
{
  "scan_id": "scan_20250127_103000_abc123",
  "scan_job_id": "uuid-job-001",
  "tenant_id": "acme_corp_prod",
  "status": "running",
  "scan_type": "full",
  "progress": {
    "total_items": 500,
    "processed_items": 250,
    "failed_items": 5,
    "percentage": 50.0,
    "success_rate": "98.00%"
  },
  "timing": {
    "started_at": "2025-01-27T10:30:00Z",
    "estimated_completion": "2025-01-27T10:35:00Z",
    "elapsed_seconds": 150
  },
  "config": {
    "batch_size": 100,
    "properties_count": 7
  },
  "links": {
    "self": "/api/v1/scans/scan_20250127_103000_abc123",
    "results": "/api/v1/scans/scan_20250127_103000_abc123/results",
    "cancel": "/api/v1/scans/scan_20250127_103000_abc123/cancel"
  }
}
```

#### Response (Completed Scan)
```json
{
  "scan_id": "scan_20250127_103000_abc123",
  "scan_job_id": "uuid-job-001",
  "tenant_id": "acme_corp_prod",
  "status": "completed",
  "scan_type": "full",
  "progress": {
    "total_items": 500,
    "processed_items": 495,
    "failed_items": 5,
    "percentage": 100.0,
    "success_rate": "99.00%"
  },
  "timing": {
    "started_at": "2025-01-27T10:30:00Z",
    "completed_at": "2025-01-27T10:35:30Z",
    "duration_seconds": 330
  },
  "results_summary": {
    "total_deals": 495,
    "total_value": 24750000.00,
    "avg_deal_value": 50000.00,
    "pipelines": {
      "default": 450,
      "sales-2024": 45
    },
    "stages": {
      "qualifiedtobuy": 150,
      "presentationscheduled": 200,
      "closedwon": 100,
      "closedlost": 45
    }
  },
  "links": {
    "self": "/api/v1/scans/scan_20250127_103000_abc123",
    "results": "/api/v1/scans/scan_20250127_103000_abc123/results"
  }
}
```

#### Response (Failed Scan)
```json
{
  "scan_id": "scan_20250127_103000_abc123",
  "scan_job_id": "uuid-job-001",
  "tenant_id": "acme_corp_prod",
  "status": "failed",
  "scan_type": "full",
  "error": {
    "code": "authentication_error",
    "message": "HubSpot API authentication failed: Invalid access token",
    "details": "The provided access token has expired or been revoked"
  },
  "progress": {
    "total_items": 500,
    "processed_items": 0,
    "failed_items": 0,
    "percentage": 0.0
  },
  "timing": {
    "started_at": "2025-01-27T10:30:00Z",
    "failed_at": "2025-01-27T10:30:05Z"
  }
}
```

#### Status Values
- **pending**: Scan queued but not started
- **running**: Scan in progress
- **completed**: Scan finished successfully
- **failed**: Scan encountered an error
- **cancelled**: Scan was cancelled by user

#### Status Codes
- **200**: Status retrieved successfully
- **400**: Invalid scan ID format
- **404**: Scan not found
- **500**: Internal server error

---

### 3. Get Scan Results

**GET** `/api/v1/scans/{scan_id}/results`

Retrieves paginated deal data from a completed scan.

#### Path Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `scan_id` | string | Yes | Unique scan identifier |

#### Query Parameters
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `page` | integer | No | 1 | Page number (minimum: 1) |
| `limit` | integer | No | 100 | Results per page (1-1000) |
| `filter_stage` | string | No | - | Filter by deal stage |
| `filter_pipeline` | string | No | - | Filter by pipeline |
| `sort_by` | string | No | closedate | Sort field (closedate, amount, createdate) |
| `sort_order` | string | No | asc | Sort order (asc or desc) |

#### Response
```json
{
  "scan_id": "scan_20250127_103000_abc123",
  "tenant_id": "acme_corp_prod",
  "status": "completed",
  "pagination": {
    "page": 1,
    "limit": 10,
    "total_results": 495,
    "total_pages": 50,
    "has_next": true,
    "has_previous": false
  },
  "filters_applied": {
    "sort_by": "amount",
    "sort_order": "desc"
  },
  "results": [
    {
      "id": "12345678901",
      "dealname": "Enterprise Software License - Acme Corp",
      "amount": 100000.00,
      "dealstage": "closedwon",
      "closedate": "2025-03-15T00:00:00Z",
      "pipeline": "default",
      "dealtype": "newbusiness",
      "hubspot_owner_id": "123456",
      "createdate": "2025-01-15T10:30:00Z",
      "hs_lastmodifieddate": "2025-01-26T08:15:00Z",
      "archived": false,
      "metadata": {
        "extracted_at": "2025-01-27T10:35:00Z",
        "scan_id": "scan_20250127_103000_abc123"
      }
    },
    {
      "id": "12345678902",
      "dealname": "Marketing Consultation Package",
      "amount": 75000.00,
      "dealstage": "presentationscheduled",
      "closedate": "2025-02-28T00:00:00Z",
      "pipeline": "default",
      "dealtype": "existingbusiness",
      "hubspot_owner_id": "123457",
      "createdate": "2025-01-10T14:20:00Z",
      "hs_lastmodifieddate": "2025-01-25T16:45:00Z",
      "archived": false,
      "metadata": {
        "extracted_at": "2025-01-27T10:35:00Z",
                "scan_id": "scan_20250127_103000_abc123"
      }
    }
  ],
  "summary": {
    "total_value": 24750000.00,
    "avg_value": 50000.00,
    "min_value": 5000.00,
    "max_value": 100000.00
  },
  "links": {
    "self": "/api/v1/scans/scan_20250127_103000_abc123/results?page=1&limit=10",
    "next": "/api/v1/scans/scan_20250127_103000_abc123/results?page=2&limit=10",
    "scan": "/api/v1/scans/scan_20250127_103000_abc123"
  }
}
```

#### Status Codes
- **200**: Results retrieved successfully
- **400**: Invalid parameters
- **404**: Scan not found
- **409**: Scan not completed yet
- **500**: Internal server error

---

### 4. Cancel Scan

**POST** `/api/v1/scans/{scan_id}/cancel`

Cancels a running or pending scan.

#### Path Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `scan_id` | string | Yes | Unique scan identifier |

#### Request Body (Optional)
```json
{
  "reason": "User requested cancellation"
}
```

#### Response
```json
{
  "status": "success",
  "message": "Scan cancelled successfully",
  "scan_id": "scan_20250127_103000_abc123",
  "previous_status": "running",
  "current_status": "cancelled",
  "progress_at_cancellation": {
    "processed_items": 250,
    "total_items": 500,
    "percentage": 50.0
  },
  "cancelled_at": "2025-01-27T10:33:00Z",
  "links": {
    "scan": "/api/v1/scans/scan_20250127_103000_abc123"
  }
}
```

#### Status Codes
- **200**: Scan cancelled successfully
- **400**: Invalid scan ID or cannot cancel
- **404**: Scan not found
- **409**: Scan already completed/failed/cancelled
- **500**: Internal server error

---

### 5. Remove Scan

**DELETE** `/api/v1/scans/{scan_id}`

Removes a scan and all associated deal data from the system.

#### Path Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `scan_id` | string | Yes | Unique scan identifier |

#### Response
```json
{
  "status": "success",
  "message": "Scan and 495 deals removed successfully",
  "scan_id": "scan_20250127_103000_abc123",
  "deleted_deals": 495,
  "deleted_at": "2025-01-27T11:00:00Z"
}
```

#### Status Codes
- **200**: Scan removed successfully
- **400**: Invalid scan ID format
- **404**: Scan not found
- **500**: Internal server error

---

## 🏥 Health & Stats Endpoints

### 1. Health Check

**GET** `/health`

Returns the overall health status of the service. No authentication required.

#### Response (Healthy)
```json
{
  "status": "healthy",
  "service": "hubspot_deals",
  "version": "1.0.0",
  "timestamp": "2025-01-27T10:30:00Z",
  "database": {
    "status": "connected",
    "latency_ms": 5
  },
  "components": {
    "api": "healthy",
    "database": "healthy",
    "extraction_service": "healthy"
  }
}
```

#### Response (Unhealthy)
```json
{
  "status": "unhealthy",
  "service": "hubspot_deals",
  "version": "1.0.0",
  "timestamp": "2025-01-27T10:30:00Z",
  "error": "Database connection failed",
  "components": {
    "api": "healthy",
    "database": "unhealthy",
    "extraction_service": "degraded"
  }
}
```

#### Status Codes
- **200**: Service is healthy
- **503**: Service is unhealthy

---

### 2. Service Statistics

**GET** `/api/v1/stats`

Returns service statistics and performance metrics.

#### Response
```json
{
  "total_scans": 1523,
  "active_scans": 3,
  "completed_scans": 1450,
  "failed_scans": 70,
  "total_deals_extracted": 2458920,
  "average_scan_duration_seconds": 180,
  "success_rate": 95.2,
  "uptime": "15 days, 7:24:15",
  "memory_usage": "512MB",
  "cpu_usage": "15%",
  "last_scan": "2025-01-27T10:25:00Z"
}
```

#### Status Codes
- **200**: Statistics retrieved successfully
- **401**: Unauthorized
- **500**: Internal server error

---

## ⚠️ Error Handling

### Error Response Formats

#### Validation Errors (400)
```json
{
  "error": "validation_error",
  "message": "Input validation failed",
  "details": {
    "tenant_id": "Field is required",
    "config.hubspot_access_token": "Invalid token format"
  },
  "timestamp": "2025-01-27T10:30:00Z"
}
```

#### Authentication Errors (401)
```json
{
  "error": "unauthorized",
  "message": "Invalid or missing API key",
  "timestamp": "2025-01-27T10:30:00Z"
}
```

#### Not Found Errors (404)
```json
{
  "error": "not_found",
  "message": "Scan not found: scan_20250127_103000_abc123",
  "timestamp": "2025-01-27T10:30:00Z"
}
```

#### Conflict Errors (409)
```json
{
  "error": "conflict",
  "message": "Scan already in progress for tenant: acme_corp_prod",
  "active_scan_id": "scan_20250127_100000_xyz789",
  "timestamp": "2025-01-27T10:30:00Z"
}
```

#### Rate Limit Errors (429)
```json
{
  "error": "rate_limit_exceeded",
  "message": "Too many requests. Maximum 10 scans per minute.",
  "retry_after": 30,
  "timestamp": "2025-01-27T10:30:00Z"
}
```

#### HubSpot API Errors (503)
```json
{
  "error": "service_unavailable",
  "message": "HubSpot API is unreachable",
  "details": "Connection timeout after 30s",
  "timestamp": "2025-01-27T10:30:00Z"
}
```

#### Server Errors (500)
```json
{
  "error": "internal_error",
  "message": "An unexpected error occurred",
  "incident_id": "inc_20250127_103000_123",
  "timestamp": "2025-01-27T10:30:00Z"
}
```

### Common Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `validation_error` | 400 | Input validation failed |
| `unauthorized` | 401 | Authentication required or failed |
| `forbidden` | 403 | Insufficient permissions |
| `not_found` | 404 | Resource not found |
| `conflict` | 409 | Resource state conflict |
| `rate_limit_exceeded` | 429 | Too many requests |
| `internal_error` | 500 | Server error |
| `service_unavailable` | 503 | Service temporarily unavailable |
| `authentication_error` | 503 | HubSpot authentication failed |

---

## 📚 Examples

### Complete Extraction Workflow

#### 1. Start Full Extraction
```bash
curl -X POST "http://localhost:5200/api/v1/scans/start" \
  -H "Authorization: Bearer your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_id": "acme_corp_prod",
    "scan_type": "full",
    "config": {
      "hubspot_access_token": "pat-na1-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
      "properties": ["dealname", "amount", "dealstage", "closedate", "pipeline"],
      "batch_size": 100
    }
  }'
```

#### 2. Monitor Progress
```bash
# Poll every 5 seconds
while true; do
  curl "http://localhost:5200/api/v1/scans/scan_20250127_103000_abc123" \
    -H "Authorization: Bearer your-api-key"
  sleep 5
done
```

#### 3. Get Results (First Page)
```bash
curl "http://localhost:5200/api/v1/scans/scan_20250127_103000_abc123/results?page=1&limit=50" \
  -H "Authorization: Bearer your-api-key"
```

#### 4. Get Filtered Results
```bash
# Get only closed won deals
curl "http://localhost:5200/api/v1/scans/scan_20250127_103000_abc123/results?filter_stage=closedwon&sort_by=amount&sort_order=desc" \
  -H "Authorization: Bearer your-api-key"
```

#### 5. Cancel Scan (if needed)
```bash
curl -X POST "http://localhost:5200/api/v1/scans/scan_20250127_103000_abc123/cancel" \
  -H "Authorization: Bearer your-api-key" \
  -H "Content-Type: application/json" \
  -d '{"reason": "User requested cancellation"}'
```

#### 6. Remove Scan (cleanup)
```bash
curl -X DELETE "http://localhost:5200/api/v1/scans/scan_20250127_103000_abc123" \
  -H "Authorization: Bearer your-api-key"
```

---

### Python Examples

#### Start Extraction
```python
import requests

url = "http://localhost:5200/api/v1/scans/start"
headers = {
    "Authorization": "Bearer your-api-key",
    "Content-Type": "application/json"
}
payload = {
    "tenant_id": "acme_corp_prod",
    "scan_type": "full",
    "config": {
        "hubspot_access_token": "pat-na1-xxxxxxxx",
        "properties": ["dealname", "amount", "dealstage"],
        "batch_size": 100
    }
}

response = requests.post(url, json=payload, headers=headers)
print(response.json())
scan_id = response.json()["scan_id"]
```

#### Monitor Progress
```python
import requests
import time

def monitor_scan(scan_id, api_key):
    url = f"http://localhost:5200/api/v1/scans/{scan_id}"
    headers = {"Authorization": f"Bearer {api_key}"}
    
    while True:
        response = requests.get(url, headers=headers)
        data = response.json()
        
        status = data["status"]
        progress = data.get("progress", {})
        
        print(f"Status: {status} - Progress: {progress.get('percentage', 0)}%")
        
        if status in ["completed", "failed", "cancelled"]:
            break
        
        time.sleep(5)
    
    return data

result = monitor_scan("scan_20250127_103000_abc123", "your-api-key")
```

#### Get Paginated Results
```python
import requests

def get_all_deals(scan_id, api_key):
    base_url = f"http://localhost:5200/api/v1/scans/{scan_id}/results"
    headers = {"Authorization": f"Bearer {api_key}"}
    
    all_deals = []
    page = 1
    
    while True:
        response = requests.get(
            base_url,
            params={"page": page, "limit": 100},
            headers=headers
        )
        
        if response.status_code != 200:
            print(f"Error: {response.status_code}")
            break
        
        data = response.json()
        all_deals.extend(data["results"])
        
        if not data["pagination"]["has_next"]:
            break
        
        page += 1
    
    return all_deals

deals = get_all_deals("scan_20250127_103000_abc123", "your-api-key")
print(f"Total deals: {len(deals)}")
```

#### Filter and Sort Results
```python
import requests

url = "http://localhost:5200/api/v1/scans/scan_20250127_103000_abc123/results"
headers = {"Authorization": "Bearer your-api-key"}
params = {
    "filter_stage": "closedwon",
    "sort_by": "amount",
    "sort_order": "desc",
    "limit": 50
}

response = requests.get(url, params=params, headers=headers)
deals = response.json()["results"]

for deal in deals:
    print(f"{deal['dealname']}: ${deal['amount']}")
```

#### Error Handling
```python
import requests
from requests.exceptions import RequestException

def start_scan_with_error_handling(tenant_id, token, api_key):
    url = "http://localhost:5200/api/v1/scans/start"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "tenant_id": tenant_id,
        "scan_type": "full",
        "config": {
            "hubspot_access_token": token,
            "batch_size": 100
        }
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        return response.json()
    
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 400:
            print(f"Validation error: {e.response.json()}")
        elif e.response.status_code == 401:
            print("Authentication failed - check API key")
        elif e.response.status_code == 409:
            print("Scan already in progress")
        else:
            print(f"HTTP error: {e}")
    
    except RequestException as e:
        print(f"Request failed: {e}")
    
    return None

result = start_scan_with_error_handling("acme_corp_prod", "pat-na1-xxxxx", "your-api-key")
```

---

### PowerShell Examples

#### Start Extraction
```powershell
$headers = @{
    "Authorization" = "Bearer your-api-key"
    "Content-Type" = "application/json"
}

$body = @{
    tenant_id = "acme_corp_prod"
    scan_type = "full"
    config = @{
        hubspot_access_token = "pat-na1-xxxxxxxx"
        properties = @("dealname", "amount", "dealstage")
        batch_size = 100
    }
} | ConvertTo-Json -Depth 10

$response = Invoke-RestMethod -Uri "http://localhost:5200/api/v1/scans/start" `
    -Method Post -Headers $headers -Body $body

Write-Host "Scan started: $($response.scan_id)"
```

#### Get Status
```powershell
$scanId = "scan_20250127_103000_abc123"
$headers = @{"Authorization" = "Bearer your-api-key"}

$status = Invoke-RestMethod -Uri "http://localhost:5200/api/v1/scans/$scanId" `
    -Headers $headers

Write-Host "Status: $($status.status)"
Write-Host "Progress: $($status.progress.percentage)%"
```

#### Get Results
```powershell
$scanId = "scan_20250127_103000_abc123"
$headers = @{"Authorization" = "Bearer your-api-key"}

$results = Invoke-RestMethod -Uri "http://localhost:5200/api/v1/scans/$scanId/results?limit=10" `