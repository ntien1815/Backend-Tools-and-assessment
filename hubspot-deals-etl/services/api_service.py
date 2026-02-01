import requests
import time
import logging
from typing import Dict, List, Optional, Any
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

logger = logging.getLogger(__name__)


class HubSpotAPIError(Exception):
    """Custom exception for HubSpot API errors"""
    pass


class HubSpotAPIService:
    """
    Service for interacting with HubSpot CRM API v3
    
    Handles:
    - Authentication
    - Rate limiting
    - Pagination
    - Error handling
    - Retries
    """
    
    def __init__(self, access_token: str, api_base_url: str = "https://api.hubapi.com", 
                 api_version: str = "v3", timeout: int = 30, max_retries: int = 3):
        """
        Initialize HubSpot API Service
        
        Args:
            access_token: HubSpot Private App Access Token
            api_base_url: Base URL for HubSpot API
            api_version: API version (default: v3)
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries for failed requests
        """
        if not access_token:
            raise ValueError("HubSpot access token is required")
        
        self.access_token = access_token
        self.api_base_url = api_base_url.rstrip('/')
        self.api_version = api_version
        self.timeout = timeout
        self.max_retries = max_retries
        
        # Setup session with retry strategy
        self.session = self._create_session()
        
        # Rate limiting
        self.last_request_time = 0
        self.min_request_interval = 0.1  # 100ms between requests (10 req/sec)
        
        logger.info(f"HubSpot API Service initialized - Base URL: {self.api_base_url}")
    
    def _create_session(self) -> requests.Session:
        """Create requests session with retry strategy"""
        session = requests.Session()
        
        # Retry strategy for transient errors
        retry_strategy = Retry(
            total=self.max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session
    
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with authentication"""
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "User-Agent": "HubSpot-Deals-ETL/1.0"
        }
    
    def _rate_limit(self):
        """Apply rate limiting between requests"""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        
        if time_since_last_request < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last_request
            logger.debug(f"Rate limiting: sleeping for {sleep_time:.3f}s")
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def _make_request(self, method: str, url: str, **kwargs) -> requests.Response:
        """
        Make HTTP request with rate limiting and error handling
        
        Args:
            method: HTTP method (GET, POST, etc.)
            url: Request URL
            **kwargs: Additional arguments for requests
            
        Returns:
            Response object
            
        Raises:
            HubSpotAPIError: If request fails
        """
        self._rate_limit()
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                headers=self._get_headers(),
                timeout=self.timeout,
                **kwargs
            )
            
            # Check for HTTP errors
            if response.status_code == 401:
                raise HubSpotAPIError("Authentication failed: Invalid access token")
            elif response.status_code == 403:
                raise HubSpotAPIError("Forbidden: Insufficient permissions")
            elif response.status_code == 429:
                # Rate limit hit
                retry_after = response.headers.get('Retry-After', 1)
                logger.warning(f"Rate limit hit. Retry after {retry_after}s")
                time.sleep(int(retry_after))
                # Retry the request
                return self._make_request(method, url, **kwargs)
            elif response.status_code >= 400:
                error_data = response.json() if response.content else {}
                error_msg = error_data.get('message', f'HTTP {response.status_code}')
                raise HubSpotAPIError(f"API request failed: {error_msg}")
            
            response.raise_for_status()
            return response
            
        except requests.exceptions.Timeout:
            raise HubSpotAPIError(f"Request timeout after {self.timeout}s")
        except requests.exceptions.ConnectionError:
            raise HubSpotAPIError("Connection error: Unable to reach HubSpot API")
        except requests.exceptions.RequestException as e:
            raise HubSpotAPIError(f"Request failed: {str(e)}")
    
    def verify_credentials(self) -> bool:
        """
        Verify API credentials by making a test request
        
        Returns:
            True if credentials are valid, False otherwise
        """
        try:
            url = f"{self.api_base_url}/crm/{self.api_version}/objects/deals"
            params = {"limit": 1}
            
            response = self._make_request("GET", url, params=params)
            logger.info("✅ HubSpot credentials verified successfully")
            return True
            
        except HubSpotAPIError as e:
            logger.error(f"❌ Credential verification failed: {e}")
            return False
    
    def get_deals(self, 
                  limit: int = 100,
                  after: Optional[str] = None,
                  properties: Optional[List[str]] = None,
                  archived: bool = False) -> Dict[str, Any]:
        """
        Get deals from HubSpot with pagination
        
        Args:
            limit: Number of deals per request (max 100)
            after: Pagination cursor from previous response
            properties: List of deal properties to retrieve
            archived: Whether to include archived deals
            
        Returns:
            Dict containing:
                - results: List of deal objects
                - paging: Pagination info (if more results available)
                
        Raises:
            HubSpotAPIError: If API request fails
        """
        # Validate limit
        if limit > 100:
            logger.warning(f"Limit {limit} exceeds max 100, setting to 100")
            limit = 100
        
        # Build URL
        url = f"{self.api_base_url}/crm/{self.api_version}/objects/deals"
        
        # Build query parameters
        params = {
            "limit": limit,
            "archived": str(archived).lower()
        }
        
        if after:
            params["after"] = after
        
        if properties:
            params["properties"] = ",".join(properties)
        
        logger.info(f"Fetching deals - Limit: {limit}, After: {after}, Archived: {archived}")
        
        try:
            response = self._make_request("GET", url, params=params)
            data = response.json()
            
            results_count = len(data.get("results", []))
            has_more = "paging" in data and "next" in data["paging"]
            
            logger.info(f"Retrieved {results_count} deals. Has more: {has_more}")
            
            return data
            
        except HubSpotAPIError as e:
            logger.error(f"Failed to fetch deals: {e}")
            raise
    
    def get_deal_by_id(self, deal_id: str, properties: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Get a single deal by ID
        
        Args:
            deal_id: HubSpot deal ID
            properties: List of properties to retrieve
            
        Returns:
            Deal object
            
        Raises:
            HubSpotAPIError: If deal not found or request fails
        """
        url = f"{self.api_base_url}/crm/{self.api_version}/objects/deals/{deal_id}"
        
        params = {}
        if properties:
            params["properties"] = ",".join(properties)
        
        logger.info(f"Fetching deal ID: {deal_id}")
        
        try:
            response = self._make_request("GET", url, params=params)
            data = response.json()
            
            logger.info(f"Retrieved deal: {data.get('properties', {}).get('dealname', 'N/A')}")
            return data
            
        except HubSpotAPIError as e:
            logger.error(f"Failed to fetch deal {deal_id}: {e}")
            raise
    
    def get_all_deals(self, 
                      properties: Optional[List[str]] = None,
                      archived: bool = False,
                      batch_size: int = 100) -> List[Dict[str, Any]]:
        """
        Get all deals using pagination
        
        Args:
            properties: List of deal properties to retrieve
            archived: Whether to include archived deals
            batch_size: Number of deals per API request
            
        Returns:
            List of all deal objects
            
        Raises:
            HubSpotAPIError: If API requests fail
        """
        all_deals = []
        after = None
        page = 1
        
        logger.info("Starting full deals extraction...")
        
        while True:
            try:
                data = self.get_deals(
                    limit=batch_size,
                    after=after,
                    properties=properties,
                    archived=archived
                )
                
                results = data.get("results", [])
                all_deals.extend(results)
                
                logger.info(f"Page {page}: Retrieved {len(results)} deals. Total: {len(all_deals)}")
                
                # Check if there are more pages
                paging = data.get("paging", {})
                if "next" not in paging:
                    logger.info(f"✅ Extraction complete. Total deals: {len(all_deals)}")
                    break
                
                # Get next page cursor
                after = paging["next"]["after"]
                page += 1
                
            except HubSpotAPIError as e:
                logger.error(f"Error during full extraction on page {page}: {e}")
                raise
        
        return all_deals
    
    def get_deal_properties(self) -> List[Dict[str, Any]]:
        """
        Get all available deal properties and their metadata
        
        Returns:
            List of property definitions
            
        Raises:
            HubSpotAPIError: If API request fails
        """
        url = f"{self.api_base_url}/crm/{self.api_version}/properties/deals"
        
        logger.info("Fetching deal properties metadata...")
        
        try:
            response = self._make_request("GET", url)
            data = response.json()
            
            results = data.get("results", [])
            logger.info(f"Retrieved {len(results)} deal properties")
            
            return results
            
        except HubSpotAPIError as e:
            logger.error(f"Failed to fetch deal properties: {e}")
            raise
    
    def close(self):
        """Close the session"""
        if self.session:
            self.session.close()
            logger.info("HubSpot API Service session closed")


# Convenience function for testing
def test_connection(access_token: str) -> bool:
    """
    Test HubSpot API connection
    
    Args:
        access_token: HubSpot access token
        
    Returns:
        True if connection successful
    """
    try:
        service = HubSpotAPIService(access_token)
        result = service.verify_credentials()
        service.close()
        return result
    except Exception as e:
        logger.error(f"Connection test failed: {e}")
        return False