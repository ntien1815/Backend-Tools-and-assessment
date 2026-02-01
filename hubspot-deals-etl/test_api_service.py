"""Test HubSpot API Service"""

import os
import logging
from dotenv import load_dotenv
from services.api_service import HubSpotAPIService, test_connection

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

load_dotenv()

def main():
    """Test HubSpot API Service"""
    
    # Get token from environment
    access_token = os.getenv("HUBSPOT_ACCESS_TOKEN")
    
    if not access_token:
        print("❌ HUBSPOT_ACCESS_TOKEN not found in .env file")
        return
    
    print("=" * 60)
    print("HUBSPOT API SERVICE TEST")
    print("=" * 60)
    
    # Test 1: Connection test
    print("\n📡 Test 1: Connection Test")
    print("-" * 60)
    success = test_connection(access_token)
    if success:
        print("✅ Connection test PASSED")
    else:
        print("❌ Connection test FAILED")
        return
    
    # Test 2: Initialize service
    print("\n🔧 Test 2: Initialize Service")
    print("-" * 60)
    try:
        service = HubSpotAPIService(access_token)
        print("✅ Service initialized successfully")
    except Exception as e:
        print(f"❌ Service initialization failed: {e}")
        return
    
    # Test 3: Verify credentials
    print("\n🔐 Test 3: Verify Credentials")
    print("-" * 60)
    if service.verify_credentials():
        print("✅ Credentials verified")
    else:
        print("❌ Credentials verification failed")
        return
    
    # Test 4: Get deals (first page)
    print("\n📥 Test 4: Get Deals (First Page)")
    print("-" * 60)
    try:
        data = service.get_deals(limit=10)
        deals = data.get("results", [])
        paging = data.get("paging", {})
        
        print(f"✅ Retrieved {len(deals)} deals")
        
        if deals:
            print("\nFirst deal:")
            first_deal = deals[0]
            props = first_deal.get("properties", {})
            print(f"  - ID: {first_deal.get('id')}")
            print(f"  - Name: {props.get('dealname', 'N/A')}")
            print(f"  - Amount: ${props.get('amount', '0')}")
            print(f"  - Stage: {props.get('dealstage', 'N/A')}")
        
        if "next" in paging:
            print(f"\n📄 More pages available")
            print(f"  - Next cursor: {paging['next']['after'][:20]}...")
        else:
            print(f"\n✅ No more pages")
            
    except Exception as e:
        print(f"❌ Get deals failed: {e}")
        return
    
    # Test 5: Get all deals
    print("\n📦 Test 5: Get All Deals")
    print("-" * 60)
    try:
        all_deals = service.get_all_deals(
            properties=["dealname", "amount", "dealstage", "closedate"],
            batch_size=100
        )
        
        print(f"✅ Retrieved {len(all_deals)} total deals")
        
        if all_deals:
            print("\nDeal Summary:")
            total_value = sum(float(d.get("properties", {}).get("amount", 0) or 0) for d in all_deals)
            print(f"  - Total deals: {len(all_deals)}")
            print(f"  - Total value: ${total_value:,.2f}")
            
            # Group by stage
            stages = {}
            for deal in all_deals:
                stage = deal.get("properties", {}).get("dealstage", "unknown")
                stages[stage] = stages.get(stage, 0) + 1
            
            print(f"\n  Deals by stage:")
            for stage, count in sorted(stages.items()):
                print(f"    - {stage}: {count}")
                
    except Exception as e:
        print(f"❌ Get all deals failed: {e}")
        return
    
    # Test 6: Get deal properties metadata
    print("\n📋 Test 6: Get Deal Properties Metadata")
    print("-" * 60)
    try:
        properties = service.get_deal_properties()
        print(f"✅ Retrieved {len(properties)} deal properties")
        
        # Show first 5 properties
        print("\nFirst 5 properties:")
        for prop in properties[:5]:
            print(f"  - {prop['name']}: {prop['label']} ({prop['type']})")
            
    except Exception as e:
        print(f"❌ Get properties failed: {e}")
    
    # Cleanup
    service.close()
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS COMPLETED")
    print("=" * 60)

if __name__ == "__main__":
    main()
