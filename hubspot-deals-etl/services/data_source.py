"""
HubSpot Deals DLT Data Source

This module implements the DLT data source for extracting HubSpot deals.
"""

import dlt
from typing import Iterator, Dict, Any, Optional, List
from datetime import datetime, timezone
import logging

from services.api_service import HubSpotAPIService, HubSpotAPIError

logger = logging.getLogger(__name__)


def transform_deal(deal: Dict[str, Any], 
                   tenant_id: str, 
                   scan_id: str,
                   extracted_at: datetime) -> Dict[str, Any]:
    """
    Transform HubSpot deal to database format
    
    Args:
        deal: Raw deal object from HubSpot API
        tenant_id: Tenant identifier
        scan_id: Scan batch identifier
        extracted_at: Extraction timestamp
        
    Returns:
        Transformed deal record
    """
    properties = deal.get("properties", {})
    
    # Helper function to safely get numeric values
    def get_numeric(value):
        if value is None or value == "":
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None
    
    # Helper function to safely get boolean values
    def get_boolean(value):
        if value is None or value == "":
            return None
        if isinstance(value, bool):
            return value
        return str(value).lower() == "true"
    
    # Helper function to safely get datetime values
    def get_datetime(value):
        if value is None or value == "":
            return None
        try:
            # HubSpot returns ISO 8601 format
            return value
        except:
            return None
    
    # Build transformed record
    transformed = {
        # Primary identifiers
        "deal_id": deal.get("id"),
        "hs_object_id": deal.get("id"),
        
        # Core deal information
        "deal_name": properties.get("dealname"),
        "amount": get_numeric(properties.get("amount")),
        "currency": properties.get("deal_currency_code", "USD"),
        "dealstage": properties.get("dealstage"),
        "dealtype": properties.get("dealtype"),
        "pipeline": properties.get("pipeline"),
        "description": properties.get("description"),
        
        # Owner & Assignment
        "owner_id": properties.get("hubspot_owner_id"),
        "hubspot_owner_id": properties.get("hubspot_owner_id"),
        
        # Deal Metrics
        "num_associated_contacts": int(properties.get("num_associated_contacts", 0) or 0),
        "num_associated_companies": int(properties.get("num_associated_companies", 0) or 0),
        "hs_forecast_amount": get_numeric(properties.get("hs_forecast_amount")),
        "hs_forecast_probability": get_numeric(properties.get("hs_forecast_probability")),
        
        # Status Flags
        "is_archived": deal.get("archived", False),
        "archived": deal.get("archived", False),
        "hs_is_closed_won": get_boolean(properties.get("hs_is_closed_won")),
        "hs_is_closed_lost": get_boolean(properties.get("hs_is_closed_lost")),
        
        # Priority
        "hs_priority": properties.get("hs_priority"),
        
        # Dates & Timestamps
        "close_date": get_datetime(properties.get("closedate")),
        "createdate": get_datetime(properties.get("createdate")),
        "hs_lastmodifieddate": get_datetime(properties.get("hs_lastmodifieddate")),
        "created_at": deal.get("createdAt"),
        "updated_at": deal.get("updatedAt"),
        
        # Raw data storage
        "raw_properties": properties,
        
        # ETL Metadata (CRITICAL)
        "extracted_at": extracted_at.isoformat(),
        "_tenant_id": tenant_id,
        "_extracted_at": extracted_at.isoformat(),
        "_scan_id": scan_id,
        "_source_system": "hubspot",
        "_api_version": "v3",
        "_is_deleted": False,
    }
    
    return transformed


@dlt.resource(
    name="deals",
    write_disposition="merge",
    primary_key="deal_id",
    merge_key="deal_id"
)
def extract_deals(
    access_token: str,
    tenant_id: str,
    scan_id: str,
    properties: Optional[List[str]] = None,
    archived: bool = False,
    batch_size: int = 100,
    checkpoint_interval: int = 50
) -> Iterator[Dict[str, Any]]:
    """
    DLT resource for extracting HubSpot deals
    
    Args:
        access_token: HubSpot Private App access token
        tenant_id: Tenant/organization identifier
        scan_id: Unique scan batch identifier
        properties: List of deal properties to extract
        archived: Whether to include archived deals
        batch_size: Number of deals per API request
        checkpoint_interval: Save checkpoint every N deals
        
    Yields:
        Transformed deal records
    """
    logger.info(f"Starting deals extraction - Tenant: {tenant_id}, Scan: {scan_id}")
    
    # Initialize API service
    service = HubSpotAPIService(access_token)
    
    # Verify credentials
    if not service.verify_credentials():
        raise HubSpotAPIError("Invalid HubSpot credentials")
    
    # Extraction metadata
    extracted_at = datetime.now(timezone.utc)
    after_cursor = None
    page = 1
    total_deals = 0
    
    try:
        while True:
            logger.info(f"Fetching page {page} (batch size: {batch_size})")
            
            # Get deals from HubSpot
            data = service.get_deals(
                limit=batch_size,
                after=after_cursor,
                properties=properties,
                archived=archived
            )
            
            results = data.get("results", [])
            
            if not results:
                logger.info("No more deals to extract")
                break
            
            # Transform and yield deals
            for deal in results:
                transformed = transform_deal(
                    deal=deal,
                    tenant_id=tenant_id,
                    scan_id=scan_id,
                    extracted_at=extracted_at
                )
                
                total_deals += 1
                
                # Yield transformed deal
                yield transformed
                
                # Checkpoint logging
                if total_deals % checkpoint_interval == 0:
                    logger.info(f"Checkpoint: {total_deals} deals extracted")
            
            logger.info(f"Page {page}: Extracted {len(results)} deals. Total: {total_deals}")
            
            # Check for more pages
            paging = data.get("paging", {})
            if "next" not in paging:
                logger.info(f"✅ Extraction complete. Total deals: {total_deals}")
                break
            
            # Get next page cursor
            after_cursor = paging["next"]["after"]
            page += 1
            
    except HubSpotAPIError as e:
        logger.error(f"HubSpot API error during extraction: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during extraction: {e}", exc_info=True)
        raise
    finally:
        service.close()
        logger.info(f"Extraction session closed. Extracted {total_deals} deals")


@dlt.source
def hubspot_deals_source(
    access_token: str,
    tenant_id: str = "default",
    scan_id: Optional[str] = None,
    properties: Optional[List[str]] = None,
    archived: bool = False,
    batch_size: int = 100
):
    """
    DLT source for HubSpot deals extraction
    
    Args:
        access_token: HubSpot Private App access token
        tenant_id: Tenant/organization identifier
        scan_id: Unique scan batch identifier
        properties: List of deal properties to extract
        archived: Whether to include archived deals
        batch_size: Number of deals per API request
        
    Returns:
        DLT source with deals resource
    """
    # Generate scan_id if not provided
    if not scan_id:
        scan_id = f"scan_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
    
    logger.info(f"Initializing HubSpot Deals source - Scan ID: {scan_id}")
    
    # Default properties if not specified
    if not properties:
        properties = [
            "dealname",
            "amount",
            "dealstage",
            "dealtype",
            "pipeline",
            "closedate",
            "createdate",
            "hs_lastmodifieddate",
            "hubspot_owner_id",
            "deal_currency_code",
            "num_associated_contacts",
            "num_associated_companies",
            "hs_forecast_amount",
            "hs_forecast_probability",
            "hs_is_closed_won",
            "hs_is_closed_lost",
            "hs_priority",
            "description"
        ]
    
    return extract_deals(
        access_token=access_token,
        tenant_id=tenant_id,
        scan_id=scan_id,
        properties=properties,
        archived=archived,
        batch_size=batch_size
    )


# Convenience function for testing
def test_extraction(access_token: str, 
                   tenant_id: str = "test", 
                   limit: int = 10) -> List[Dict[str, Any]]:
    """
    Test extraction without DLT pipeline
    
    Args:
        access_token: HubSpot access token
        tenant_id: Tenant identifier
        limit: Maximum number of deals to extract
        
    Returns:
        List of extracted deals
    """
    logger.info(f"Starting test extraction (limit: {limit})")
    
    scan_id = f"test_scan_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
    extracted_at = datetime.now(timezone.utc)
    
    service = HubSpotAPIService(access_token)
    
    try:
        # Get deals
        data = service.get_deals(limit=limit)
        results = data.get("results", [])
        
        # Transform deals
        transformed_deals = []
        for deal in results:
            transformed = transform_deal(
                deal=deal,
                tenant_id=tenant_id,
                scan_id=scan_id,
                extracted_at=extracted_at
            )
            transformed_deals.append(transformed)
        
        logger.info(f"✅ Test extraction complete: {len(transformed_deals)} deals")
        return transformed_deals
        
    finally:
        service.close()