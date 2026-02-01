"""
Run HubSpot Deals ETL Pipeline

This script runs the complete DLT pipeline to extract deals from HubSpot
and load them into PostgreSQL.
"""

import os
import dlt
from dotenv import load_dotenv
from services.data_source import hubspot_deals_source
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


def run_pipeline(
    tenant_id: str = "test_account",
    scan_type: str = "full",
    batch_size: int = 100
):
    """
    Run the HubSpot Deals ETL pipeline
    
    Args:
        tenant_id: Tenant/organization identifier
        scan_type: Type of scan (full or incremental)
        batch_size: Number of deals per API request
    """
    
    logger.info("=" * 70)
    logger.info("HUBSPOT DEALS ETL PIPELINE")
    logger.info("=" * 70)
    
    # Get configuration from environment
    access_token = os.getenv("HUBSPOT_ACCESS_TOKEN")
    database_url = os.getenv("DATABASE_URL")
    
    if not access_token:
        logger.error("❌ HUBSPOT_ACCESS_TOKEN not found in .env")
        return False
    
    if not database_url:
        logger.error("❌ DATABASE_URL not found in .env")
        return False
    
    logger.info(f"\n📋 Configuration:")
    logger.info(f"  - Tenant ID: {tenant_id}")
    logger.info(f"  - Scan Type: {scan_type}")
    logger.info(f"  - Batch Size: {batch_size}")
    logger.info(f"  - Database: {database_url.split('@')[1] if '@' in database_url else 'configured'}")
    
    try:
        # Initialize DLT source
        logger.info(f"\n🔧 Initializing DLT source...")
        source = hubspot_deals_source(
            access_token=access_token,
            tenant_id=tenant_id,
            batch_size=batch_size
        )
        
        logger.info(f"✅ Source initialized: {source}")
        
        # Create DLT pipeline
        logger.info(f"\n🚀 Creating DLT pipeline...")
        pipeline = dlt.pipeline(
            pipeline_name="hubspot_deals",
            destination="postgres",
            dataset_name="hubspot_deals",
            progress="log"
        )
        
        logger.info(f"✅ Pipeline created: {pipeline.pipeline_name}")
        
        # Run the pipeline
        logger.info(f"\n📦 Running extraction...")
        logger.info(f"-" * 70)
        
        load_info = pipeline.run(source)
        
        logger.info(f"-" * 70)
        logger.info(f"\n✅ Pipeline completed successfully!")
        
        # Print results
        logger.info(f"\n📊 Results:")
        logger.info(f"  - Pipeline: {load_info.pipeline.pipeline_name}")
        logger.info(f"  - Dataset: {load_info.pipeline.dataset_name}")
        logger.info(f"  - Loads: {len(load_info.loads_ids)}")
        
        # Print package info
        if load_info.has_failed_jobs:
            logger.error(f"  - Failed jobs: {len(load_info.load_packages[0].jobs['failed_jobs'])}")
            for job in load_info.load_packages[0].jobs['failed_jobs']:
                logger.error(f"    - {job}")
        else:
            logger.info(f"  - Status: All jobs completed successfully")
        
        # Print table statistics
        logger.info(f"\n📈 Tables loaded:")
        for package in load_info.load_packages:
            for table_name, table_metrics in package.schema_update.items():
                logger.info(f"  - {table_name}: {table_metrics}")
        
        logger.info(f"\n" + "=" * 70)
        logger.info(f"✅ ETL PIPELINE COMPLETED")
        logger.info(f"=" * 70)
        
        return True
        
    except Exception as e:
        logger.error(f"\n❌ Pipeline failed: {e}", exc_info=True)
        return False


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run HubSpot Deals ETL Pipeline")
    parser.add_argument("--tenant-id", default="test_account", help="Tenant ID")
    parser.add_argument("--scan-type", default="full", choices=["full", "incremental"], help="Scan type")
    parser.add_argument("--batch-size", type=int, default=100, help="Batch size")
    
    args = parser.parse_args()
    
    success = run_pipeline(
        tenant_id=args.tenant_id,
        scan_type=args.scan_type,
        batch_size=args.batch_size
    )
    
    exit(0 if success else 1)
