# 📋 hubspot_deals - Integration with HubSpot CRM API

This document explains the HubSpot CRM REST API endpoints required by the hubspot_deals service to extract Deal objects data from HubSpot accounts.

---

## 📋 Overview

The hubspot_deals service integrates with HubSpot CRM API v3 to extract Deal (crm.objects.deals) data from HubSpot accounts. Below are the required and optional endpoints:

### ✅ **Required Endpoint (Essential)**
| **API Endpoint**                    | **Purpose**                          | **Version** | **Required Permissions** | **Usage**    |
|-------------------------------------|--------------------------------------|-------------|--------------------------|--------------|
| `/crm/v3/objects/deals`    | List and paginate HubSpot deals         | v3 | crm.objects.deals.read       | **Required** |

### 🔧 Optional Endpoints (Advanced Features)

| API Endpoint | Purpose | Version | Required Permissions | Usage |
|-------------|--------|---------|----------------------|-------|
| `/crm/v3/objects/deals/{dealId}` | Retrieve detailed information for a specific deal | v3 | `crm.objects.deals.read` | Optional |
| `/crm/v3/properties/deals` | Retrieve deal property definitions | v3 | `crm.schemas.deals.read` | Optional |

### 🎯 Recommendation
**Start with only the required endpoint.**  
The `/crm/v3/objects/deals` endpoint provides all essential deal data required for ETL, reporting, and analytics use cases.

---

## 🔐 Authentication Requirements

### **Private App Access Token Authentication**
```http
Authorization: Bearer {HUBSPOT_PRIVATE_APP_TOKEN}
Content-Type: application/json
```

### **Required Permissions**
- **crm.objects.deals.read**: Read access to Deal objects for listing and extraction

---

## 🌐 HubSpot API Endpoints

### 🎯 **PRIMARY ENDPOINT (Required for Basic Deal Extraction)**

### 1. **List Deals** - `/crm/v3/objects/deals` ✅ **REQUIRED**

**Purpose**: Get paginated list of all deals - **THIS IS ALL YOU NEED FOR BASIC DEAL EXTRACTION**

**Method**: `GET`

**URL**: `https://api.hubapi.com/crm/v3/objects/deals`

**Query Parameters**:
```
?limit=100&properties=dealname,amount,dealstage,closedate,pipeline,createdate&after={cursor}
```

| Parameter | Type | Required | Description | Default | Example |
|-----------|------|----------|-------------|---------|---------|
| `limit` | integer | No | Number of deals per page (max 100) | 10 | 100 |
| `properties` | string | No | Comma-separated list of properties to return | All default properties | `dealname,amount,dealstage` |
| `after` | string | No | Cursor for pagination (from previous response) | - | `MTA0NzUyMzI5Mw%3D%3D` |
| `archived` | boolean | No | Whether to include archived deals | false | true |

**Request Example**:
```http
GET https://api.hubapi.com/crm/v3/objects/deals?limit=100&properties=dealname,amount,dealstage,closedate,pipeline
Authorization: Bearer pat-na1-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
Content-Type: application/json
```

**Response Structure** (Contains ALL essential deal data):
```json
{
  "results": [
    {
      "id": "12345678901",
      "properties": {
        "amount": "50000",
        "closedate": "2025-03-15T00:00:00.000Z",
        "createdate": "2025-01-15T10:30:00.000Z",
        "dealname": "Enterprise Software License",
        "dealstage": "presentationscheduled",
        "hs_lastmodifieddate": "2025-01-26T08:15:00.000Z",
        "hs_object_id": "12345678901",
        "pipeline": "default"
      },
      "createdAt": "2025-01-15T10:30:00.000Z",
      "updatedAt": "2025-01-26T08:15:00.000Z",
      "archived": false
    },
    {
      "id": "12345678902",
      "properties": {
        "amount": "25000",
        "closedate": "2025-02-28T00:00:00.000Z",
        "createdate": "2025-01-10T14:20:00.000Z",
        "dealname": "Marketing Consultation Package",
        "dealstage": "qualifiedtobuy",
        "hs_lastmodifieddate": "2025-01-25T16:45:00.000Z",
        "hs_object_id": "12345678902",
        "pipeline": "default"
      },
      "createdAt": "2025-01-10T14:20:00.000Z",
      "updatedAt": "2025-01-25T16:45:00.000Z",
      "archived": false
    }
  ],
  "paging": {
    "next": {
      "after": "MTA0NzUyMzI5Mw%3D%3D",
      "link": "https://api.hubapi.com/crm/v3/objects/deals?after=MTA0NzUyMzI5Mw%3D%3D&limit=100"
    }
  }
}
```

**✅ This endpoint provides ALL the default deal fields:**
- **id**: Unique HubSpot deal ID
- **properties**: All deal properties (dealname, amount, dealstage, closedate, pipeline, etc.)
- **createdAt**: Deal creation timestamp
- **updatedAt**: Last modification timestamp
- **archived**: Whether the deal is archived

**Common Deal Properties** (use in `properties` parameter):
- `dealname`: Name of the deal
- `amount`: Deal value/amount
- `dealstage`: Current stage in pipeline (qualifiedtobuy, presentationscheduled, closedwon, closedlost, etc.)
- `closedate`: Expected or actual close date
- `pipeline`: Pipeline ID the deal belongs to
- `createdate`: When the deal was created
- `hs_lastmodifieddate`: Last modification date
- `dealtype`: Type of deal (newbusiness, existingbusiness, etc.)
- `description`: Deal description
- `hubspot_owner_id`: ID of deal owner

**Rate Limit**: 150 requests per 10 seconds (with burst allowance)

---

## 🔧 **OPTIONAL ENDPOINTS (Advanced Features Only)**

> **⚠️ Note**: These endpoints are NOT required for basic deal extraction. Only implement if you need advanced deal analytics like custom properties metadata or individual deal details.

### 2. **Get Deal Details** - `/crm/v3/objects/deals/{dealId}` 🔧 **OPTIONAL**

**Purpose**: Get detailed information for a specific deal

**When to use**: Only if you need additional deal metadata not available in list endpoint

**Method**: `GET`

**URL**: `https://api.hubapi.com/crm/v3/objects/deals/{dealId}`

**Query Parameters**:
```
?properties=dealname,amount,dealstage,closedate&associations=contacts,companies
```

**Request Example**:
```http
GET https://api.hubapi.com/crm/v3/objects/deals/12345678901?properties=dealname,amount,dealstage
Authorization: Bearer pat-na1-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
Content-Type: application/json
```

**Response Structure**:
```json
{
  "id": "12345678901",
  "properties": {
    "amount": "50000",
    "closedate": "2025-03-15T00:00:00.000Z",
    "createdate": "2025-01-15T10:30:00.000Z",
    "dealname": "Enterprise Software License",
    "dealstage": "presentationscheduled",
    "hs_lastmodifieddate": "2025-01-26T08:15:00.000Z",
    "pipeline": "default"
  },
  "createdAt": "2025-01-15T10:30:00.000Z",
  "updatedAt": "2025-01-26T08:15:00.000Z",
  "archived": false
}
```

---

### 3. **Get Deal Properties Metadata** - `/crm/v3/properties/deals` 🔧 **OPTIONAL**

**Purpose**: Get all available deal property definitions and their metadata

**When to use**: Only if you need to understand available custom properties or property types

**Method**: `GET`

**URL**: `https://api.hubapi.com/crm/v3/properties/deals`

**Request Example**:
```http
GET https://api.hubapi.com/crm/v3/properties/deals
Authorization: Bearer pat-na1-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
Content-Type: application/json
```

**Response Structure**:
```json
{
  "results": [
    {
      "name": "dealname",
      "label": "Deal Name",
      "type": "string",
      "fieldType": "text",
      "description": "Name of the deal",
      "groupName": "dealinformation",
      "displayOrder": 1,
      "hasUniqueValue": false,
      "hidden": false,
      "modificationMetadata": {
        "archivable": false,
        "readOnlyValue": false,
        "readOnlyDefinition": true
      }
    },
    {
      "name": "amount",
      "label": "Amount",
      "type": "number",
      "fieldType": "number",
      "description": "The total value of the deal in the deal's currency",
      "groupName": "dealinformation",
      "displayOrder": 2,
      "hasUniqueValue": false,
      "hidden": false
    }
  ]
}
```

---

## 📊 Data Extraction Flow

### 🎯 **SIMPLE FLOW (Recommended - Using Only Required Endpoint)**

### **Single Endpoint Approach - `/crm/v3/objects/deals` Only**
```python
def extract_all_deals_simple():
    """Extract all deals using only the /crm/v3/objects/deals endpoint"""
    base_url = "https://api.hubapi.com"
    access_token = "pat-na1-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    all_deals = []
    after_cursor = None
    
    while True:
        params = {
            "limit": 100,
            "properties": "dealname,amount,dealstage,closedate,pipeline,createdate,dealtype"
        }
        
        if after_cursor:
            params["after"] = after_cursor
        
        response = requests.get(
            f"{base_url}/crm/v3/objects/deals",
            params=params,
            headers=headers
        )
        
        if response.status_code != 200:
            print(f"Error: {response.status_code} - {response.text}")
            break
        
        data = response.json()
        deals = data.get("results", [])
        
        if not deals:  # No more deals
            break
            
        all_deals.extend(deals)
        
        # Check if there's a next page
        paging = data.get("paging", {})
        if "next" not in paging:
            break
            
        after_cursor = paging["next"]["after"]
    
    return all_deals

# This gives you ALL essential deal data:
# - id, dealname, amount, dealstage
# - closedate, pipeline, createdate
# - createdAt, updatedAt, archived status
```

---

### 🔧 **ADVANCED FLOW (Optional - Multiple Endpoints)**

> **⚠️ Only use this if you need property metadata or individual deal details**

### **Step 1: Get Property Definitions (Optional)**
```python
# Get all available deal properties first
response = requests.get(
    f"{base_url}/crm/v3/properties/deals",
    headers=headers
)
properties_metadata = response.json()
```

### **Step 2: Batch Deal Retrieval**
```python
# Get deals in batches of 100
after_cursor = None
while True:
    response = requests.get(
        f"{base_url}/crm/v3/objects/deals",
        params={
            "limit": 100,
            "properties": "dealname,amount,dealstage,closedate",
            "after": after_cursor
        },
        headers=headers
    )
    deals_data = response.json()
    deals = deals_data.get("results", [])
    
    if not deals or "paging" not in deals_data:
        break
    
    after_cursor = deals_data["paging"]["next"]["after"]
```

### **Step 3: Get Individual Deal Details (Optional)**
```python
# Get detailed information for specific deals
for deal in deals:
    response = requests.get(
        f"{base_url}/crm/v3/objects/deals/{deal['id']}",
        params={
            "properties": "dealname,amount,dealstage,closedate",
            "associations": "contacts,companies"
        },
        headers=headers
    )
    detailed_deal = response.json()
```

---

## ⚡ Performance Considerations

### **Rate Limiting**
- **Default Limit**: 150 requests per 10 seconds per API token
- **Burst Limit**: 200 requests per 10 seconds (short duration)
- **Daily Limit**: 500,000 requests per day for Professional/Enterprise accounts
- **Best Practice**: Implement exponential backoff on 429 responses

### **Batch Processing**
- **Recommended Batch Size**: 100 deals per request (maximum allowed)
- **Concurrent Requests**: Max 10 parallel requests
- **Request Interval**: 70ms between requests to stay under rate limits (14 requests/sec)

### **Error Handling**
```http
# Rate limit exceeded
HTTP/429 Too Many Requests
Retry-After: 1

# Authentication failed  
HTTP/401 Unauthorized
{
  "status": "error",
  "message": "Invalid access token",
  "category": "INVALID_AUTHENTICATION"
}

# Insufficient permissions
HTTP/403 Forbidden
{
  "status": "error",
  "message": "This access token does not have the proper permissions",
  "category": "MISSING_SCOPES"
}

# Deal not found
HTTP/404 Not Found
{
  "status": "error",
  "message": "resource not found",
  "category": "OBJECT_NOT_FOUND"
}
```

---

## 🔒 Security Requirements

### **API Token Permissions**

#### ✅ **Required (Minimum Permissions)**
```
Required Scopes:
- crm.objects.deals.read (for basic deal information)
```

#### 🔧 **Optional (Advanced Features)**
```
Additional Scopes (only if using optional endpoints):
- crm.schemas.deals.read (for deal property metadata)
- crm.objects.contacts.read (if fetching associated contacts)
- crm.objects.companies.read (if fetching associated companies)
```

### **User Permissions**

#### ✅ **Required (Minimum)**
The Private App must have:
- **Read** access to **Deals** (CRM Objects)

#### 🔧 **Optional (Advanced Features)**
Additional permissions (only if using optional endpoints):
- **Read** access to **Contacts** (for deal-contact associations)
- **Read** access to **Companies** (for deal-company associations)

---

## 📈 Monitoring & Debugging

### **Request Headers for Debugging**
```http
Authorization: Bearer pat-na1-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
Content-Type: application/json
User-Agent: HubSpotDealsETL/1.0
X-Request-ID: deal-scan-001-batch-1
```

### **Response Validation**
```python
def validate_deal_response(deal_data):
    required_fields = ["id", "properties", "createdAt", "updatedAt"]
    for field in required_fields:
        if field not in deal_data:
            raise ValueError(f"Missing required field: {field}")
    
    # Validate required properties
    required_props = ["dealname", "dealstage"]
    for prop in required_props:
        if prop not in deal_data.get("properties", {}):
            print(f"Warning: Missing property: {prop}")
```

### **API Usage Metrics**
- Track requests per 10 seconds
- Monitor response times
- Log rate limit headers (`X-HubSpot-RateLimit-Remaining`)
- Track authentication failures

---

## 🧪 Testing API Integration

### **Test Authentication**
```bash
curl -X GET \
  "https://api.hubapi.com/crm/v3/objects/deals?limit=1" \
  -H "Authorization: Bearer pat-na1-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx" \
  -H "Content-Type: application/json"
```

### **Test Deal Search**
```bash
curl -X GET \
  "https://api.hubapi.com/crm/v3/objects/deals?limit=5&properties=dealname,amount,dealstage" \
  -H "Authorization: Bearer pat-na1-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx" \
  -H "Content-Type: application/json"
```

### **Test Deal Details**
```bash
curl -X GET \
  "https://api.hubapi.com/crm/v3/objects/deals/12345678901" \
  -H "Authorization: Bearer pat-na1-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx" \
  -H "Content-Type: application/json"
```

---

## 🚨 Common Issues & Solutions

### **Issue**: 401 Unauthorized
**Solution**: Verify Private App Access Token is correct and active
```bash
# Check token format (should start with "pat-na1-" or "pat-eu1-")
echo $HUBSPOT_ACCESS_TOKEN
```

### **Issue**: 403 Forbidden - Missing Scopes
**Solution**: Check Private App has "crm.objects.deals.read" scope enabled
1. Go to HubSpot Settings → Integrations → Private Apps
2. Click on your app
3. Check "Scopes" tab
4. Ensure "crm.objects.deals.read" is checked

### **Issue**: 429 Rate Limited
**Solution**: Implement retry with exponential backoff
```python
import time
import random

def retry_with_backoff(func, max_retries=5):
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if "429" in str(e):
                wait_time = (2 ** attempt) + random.uniform(0, 1)
                print(f"Rate limited. Waiting {wait_time:.2f}s...")
                time.sleep(wait_time)
            else:
                raise
    raise Exception("Max retries exceeded")
```

### **Issue**: Empty Deal List
**Solution**: 
1. Check if test account has any deals created
2. Verify API token has access to the correct HubSpot account
3. Check if `archived=true` parameter is needed

### **Issue**: Missing Properties in Response
**Solution**: Explicitly request properties in the `properties` parameter
```python
params = {
    "limit": 100,
    "properties": "dealname,amount,dealstage,closedate,pipeline,createdate"
}
```

---

## 💡 **Implementation Recommendations**

### 🎯 **Phase 1: Start Simple (Recommended)**
1. Implement only `/crm/v3/objects/deals` endpoint
2. Extract basic deal data (id, dealname, amount, dealstage, closedate)
3. Use pagination with `after` cursor
4. This covers 95% of deal analytics needs

### 🔧 **Phase 2: Add Advanced Features (If Needed)**
1. Add `/crm/v3/objects/deals/{dealId}` for individual deal details
2. Add `/crm/v3/properties/deals` for property metadata
3. Add association fetching for contacts/companies
4. Implement incremental extraction using `hs_lastmodifieddate`

### ⚡ **Performance Tips**
- **Simple approach**: 1 API call per 100 deals
- **Advanced approach**: 1 + N API calls (N = number of deals for details)
- Use maximum `limit=100` to minimize API calls
- Cache property metadata (it rarely changes)
- Start simple to minimize API usage and complexity!

---

## 📦 Complete Deal Properties List

### **Default Properties** (Always Available)
```
dealname                 - Deal name
amount                   - Deal amount/value
dealstage                - Current pipeline stage
closedate                - Expected/actual close date
pipeline                 - Pipeline ID
createdate               - Creation date
hs_lastmodifieddate      - Last modified date
hs_object_id             - HubSpot internal ID
dealtype                 - Deal type (newbusiness, existingbusiness, etc.)
description              - Deal description
hubspot_owner_id         - Deal owner user ID
num_associated_contacts  - Number of associated contacts
num_associated_companies - Number of associated companies
```

### **Common Custom Properties** (May vary by account)
```
deal_currency_code       - Currency code (USD, EUR, etc.)
hs_priority              - Deal priority
hs_forecast_amount       - Forecasted amount
hs_forecast_probability  - Win probability
hs_is_closed_won         - Closed won status
hs_is_closed_lost        - Closed lost status
```

---

## 📞 Support Resources

- **HubSpot API Documentation**: https://developers.hubspot.com/docs/api/crm/deals
- **Rate Limiting Guide**: https://developers.hubspot.com/docs/api/usage-details
- **Authentication Guide**: https://developers.hubspot.com/docs/api/private-apps
- **Deal Properties Reference**: https://developers.hubspot.com/docs/api/crm/properties

---

## 📝 Notes for Implementation

1. **Always use cursor-based pagination** with `after` parameter (not offset-based)
2. **Store the `after` cursor** for resuming interrupted extractions
3. **Handle archived deals** separately if needed with `archived=true` parameter
4. **Use batch size of 100** for optimal performance
5. **Implement exponential backoff** for rate limit handling
6. **Log all API responses** for debugging and monitoring
7. **Validate response structure** before processing
8. **Handle timezone conversions** for date fields (HubSpot uses UTC)