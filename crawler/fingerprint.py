"""
Content Fingerprinting for Duplicate Detection
Uses SHA-256 hash of (title, company, job_url) to detect duplicates
"""

import hashlib
from typing import Dict, Any

def generate_fingerprint(job: Dict[str, Any]) -> str:
    """
    Generate SHA-256 fingerprint for a job posting
    
    Args:
        job: Job dictionary with title, company, url
        
    Returns:
        SHA-256 hash string
    """
    
    # Extract key fields
    title = str(job.get('title', '')).strip().lower()
    company = str(job.get('company', '')).strip().lower()
    url = str(job.get('url', '')).strip().lower()
    
    # Combine fields
    content = f"{title}|{company}|{url}"
    
    # Generate SHA-256 hash
    fingerprint = hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    return fingerprint

def is_duplicate_by_fingerprint(
    fingerprint: str,
    seen_fingerprints: set
) -> bool:
    """
    Check if fingerprint already exists in the set
    
    Args:
        fingerprint: SHA-256 hash
        seen_fingerprints: Set of already seen fingerprints
        
    Returns:
        True if duplicate, False otherwise
    """
    return fingerprint in seen_fingerprints
