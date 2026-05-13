"""
HTTP Client with Retry Logic and Rate Limiting
Handles timeout, 5xx errors, 429/503 with exponential backoff
"""

import requests
import time
import logging
import os
from typing import Dict, Any, Optional

# Configuration from environment or defaults
CRAWL_MAX_RETRIES = int(os.getenv('CRAWL_MAX_RETRIES', '3'))
CRAWL_HTTP_TIMEOUT = int(os.getenv('CRAWL_HTTP_TIMEOUT', '10'))
CRAWL_BASE_DELAY_SEC = float(os.getenv('CRAWL_BASE_DELAY_SEC', '2'))
MIN_REQUEST_INTERVAL_SEC = float(os.getenv('CRAWL_MIN_REQUEST_INTERVAL_SEC', '0.45'))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RateLimitError(Exception):
    """Raised when rate limit is exceeded"""
    pass

class CrawlerHTTPError(Exception):
    """Base exception for crawler HTTP errors"""
    pass

class TransientHTTPError(CrawlerHTTPError):
    """Transient HTTP error that may succeed on retry"""
    pass

def rate_limit_pause():
    """Pause between requests to avoid rate limiting"""
    time.sleep(MIN_REQUEST_INTERVAL_SEC)

def post_json_with_retries(
    url: str,
    payload: Dict[str, Any],
    headers: Optional[Dict[str, str]] = None,
    max_retries: int = CRAWL_MAX_RETRIES,
    timeout: int = CRAWL_HTTP_TIMEOUT
) -> requests.Response:
    """
    POST JSON with retry logic and exponential backoff
    
    Args:
        url: Target URL
        payload: JSON payload
        headers: HTTP headers
        max_retries: Maximum number of retries
        timeout: Request timeout in seconds
        
    Returns:
        Response object
        
    Raises:
        RateLimitError: When rate limit is exceeded after retries
        CrawlerHTTPError: When request fails after retries
    """
    
    if headers is None:
        headers = {
            "User-Agent": "Mozilla/5.0 (compatible; ITJobsCrawler/1.0)",
            "Content-Type": "application/json"
        }
    
    last_exception = None
    
    for attempt in range(max_retries):
        try:
            logger.debug(f"Attempt {attempt + 1}/{max_retries} for {url}")
            
            response = requests.post(
                url,
                json=payload,
                headers=headers,
                timeout=timeout
            )
            
            # Handle rate limiting (429, 503)
            if response.status_code in [429, 503]:
                retry_after = int(response.headers.get('Retry-After', CRAWL_BASE_DELAY_SEC * (2 ** attempt)))
                logger.warning(f"⚠️  Rate limited (HTTP {response.status_code}). Waiting {retry_after}s...")
                
                if attempt < max_retries - 1:
                    time.sleep(retry_after)
                    continue
                else:
                    raise RateLimitError(f"Rate limit exceeded after {max_retries} retries")
            
            # Handle server errors (5xx)
            if 500 <= response.status_code < 600:
                wait_time = CRAWL_BASE_DELAY_SEC * (2 ** attempt)
                logger.warning(f"⚠️  Server error {response.status_code}. Waiting {wait_time}s...")
                
                if attempt < max_retries - 1:
                    time.sleep(wait_time)
                    continue
                else:
                    raise CrawlerHTTPError(f"Server error {response.status_code} after {max_retries} retries")
            
            # Success or client error (4xx except 429)
            response.raise_for_status()
            return response
            
        except requests.exceptions.Timeout as e:
            logger.warning(f"⚠️  Timeout on attempt {attempt + 1}")
            last_exception = e
            
            if attempt < max_retries - 1:
                wait_time = CRAWL_BASE_DELAY_SEC * (2 ** attempt)
                time.sleep(wait_time)
                continue
                
        except requests.exceptions.ConnectionError as e:
            logger.warning(f"⚠️  Connection error on attempt {attempt + 1}")
            last_exception = e
            
            if attempt < max_retries - 1:
                wait_time = CRAWL_BASE_DELAY_SEC * (2 ** attempt)
                time.sleep(wait_time)
                continue
                
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Request error: {e}")
            last_exception = e
            break
    
    # All retries failed
    raise CrawlerHTTPError(f"Request failed after {max_retries} retries: {last_exception}")

def get_with_retries(
    url: str,
    headers: Optional[Dict[str, str]] = None,
    max_retries: int = CRAWL_MAX_RETRIES,
    timeout: int = CRAWL_HTTP_TIMEOUT
) -> requests.Response:
    """
    GET request with retry logic
    
    Similar to post_json_with_retries but for GET requests
    """
    
    if headers is None:
        headers = {
            "User-Agent": "Mozilla/5.0 (compatible; ITJobsCrawler/1.0)"
        }
    
    last_exception = None
    
    for attempt in range(max_retries):
        try:
            response = requests.get(
                url,
                headers=headers,
                timeout=timeout
            )
            
            if response.status_code in [429, 503]:
                retry_after = int(response.headers.get('Retry-After', CRAWL_BASE_DELAY_SEC * (2 ** attempt)))
                logger.warning(f"⚠️  Rate limited. Waiting {retry_after}s...")
                
                if attempt < max_retries - 1:
                    time.sleep(retry_after)
                    continue
                else:
                    raise RateLimitError(f"Rate limit exceeded after {max_retries} retries")
            
            if 500 <= response.status_code < 600:
                wait_time = CRAWL_BASE_DELAY_SEC * (2 ** attempt)
                logger.warning(f"⚠️  Server error {response.status_code}. Waiting {wait_time}s...")
                
                if attempt < max_retries - 1:
                    time.sleep(wait_time)
                    continue
                else:
                    raise CrawlerHTTPError(f"Server error after {max_retries} retries")
            
            response.raise_for_status()
            return response
            
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
            logger.warning(f"⚠️  Error on attempt {attempt + 1}: {e}")
            last_exception = e
            
            if attempt < max_retries - 1:
                wait_time = CRAWL_BASE_DELAY_SEC * (2 ** attempt)
                time.sleep(wait_time)
                continue
                
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Request error: {e}")
            last_exception = e
            break
    
    raise CrawlerHTTPError(f"Request failed after {max_retries} retries: {last_exception}")


def post_notify(
    url: str,
    json_body: Dict[str, Any],
    headers: Optional[Dict[str, str]] = None,
    timeout: int = 10
) -> bool:
    """
    POST notification to API (non-critical, don't fail on error)
    
    Args:
        url: Target URL
        json_body: JSON payload
        headers: HTTP headers
        timeout: Request timeout
        
    Returns:
        True if successful, False otherwise
    """
    try:
        if headers is None:
            headers = {'Content-Type': 'application/json'}
        
        response = requests.post(
            url,
            json=json_body,
            headers=headers,
            timeout=timeout
        )
        response.raise_for_status()
        logger.info(f"✅ Notification sent to {url}")
        return True
        
    except Exception as e:
        logger.warning(f"⚠️  Failed to send notification: {e}")
        return False
