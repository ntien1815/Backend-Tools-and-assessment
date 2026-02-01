"""Test HubSpot Deals Data Source"""

import os
from dotenv import load_dotenv
from services.data_source import test_extraction, hubspot_deals_source
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

load_dotenv()

def main():
    """Test DLT Data Source"""
    
    access_token = os.getenv("HUBSPOT_ACCESS_TOKEN")
    
    if not access_token:
        print("❌ HUBSPOT_ACCESS_TOKEN not found")
        return
    
    print("=" * 60)
    print("HUBSPOT DEALS DATA SOURCE TEST")
    print("=" * 60)
    
    # Test 1: Simple extraction (without DLT)
    print("\n📦 Test 1: Simple Extraction (No DLT)")
    print("-" * 60)
    try:
        deals = test_extraction(access_token, tenant_id="test", limit=5)
        print(f"✅ Extracted {len(deals)} deals")
        
        if deals:
            print("\nFirst deal (transformed):")
            first = deals[0]
            print(f"  - Deal ID: {first['deal_id']}")
            print(f"  - Name: {first['deal_name']}")
            print(f"  - Amount: ${first['amount']}")
            print(f"  - Stage: {first['dealstage']}")
            print(f"  - Tenant ID: {first['_tenant_id']}")
            print(f"  - Scan ID: {first['_scan_id']}")
            print(f"  - Extracted At: {first['_extracted_at']}")
            
    except Exception as e:
        print(f"❌ Extraction failed: {e}")
        return
    
    # Test 2: DLT Source initialization
    print("\n🔧 Test 2: DLT Source Initialization")
    print("-" * 60)
    try:
        source = hubspot_deals_source(
            access_token=access_token,
            tenant_id="test_tenant",
            batch_size=10
        )
        print("✅ DLT source initialized successfully")
        print(f"  - Source: {source}")
        
    except Exception as e:
        print(f"❌ DLT source initialization failed: {e}")
        return
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS COMPLETED")
    print("=" * 60)

if __name__ == "__main__":
    main()
