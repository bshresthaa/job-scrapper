
# src/services/deduplicator.py
import hashlib
import json
from difflib import SequenceMatcher
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

def generate_content_hash(job):
    """Generate hash for job based on key fields"""
    content = {
        'title': job.get('title', '').lower().strip(),
        'company': job.get('company', '').lower().strip(),
        'location': job.get('location', '').lower().strip()
    }
    
    content_str = json.dumps(content, sort_keys=True)
    return hashlib.md5(content_str.encode()).hexdigest()

def is_similar(job1, job2, threshold=0.85):
    """Check if two jobs are similar using fuzzy matching"""
    
    title_similarity = SequenceMatcher(
        None,
        job1.get('title', '').lower(),
        job2.get('title', '').lower()
    ).ratio()
    
    company_match = (
        job1.get('company', '').lower() == job2.get('company', '').lower()
    )
    
    return title_similarity >= threshold and company_match

def is_duplicate(job, db, check_fuzzy=True):
    """
    Check if job is duplicate
    
    Args:
        job: Job dictionary
        db: Database instance
        check_fuzzy: Whether to do fuzzy matching (slower)
    
    Returns:
        Boolean indicating if job is duplicate
    """
    # Generate content hash
    content_hash = generate_content_hash(job)
    job['content_hash'] = content_hash
    
    # Check exact hash match
    if db.job_exists_by_hash(content_hash):
        logger.debug(f"Duplicate found by hash: {job['title']}")
        return True
    
    # Optional fuzzy matching for recent jobs
    if check_fuzzy:
        recent_jobs = db.query_jobs(limit=100)
        
        for existing_job in recent_jobs:
            if is_similar(job, existing_job):
                logger.debug(f"Duplicate found by fuzzy match: {job['title']}")
                return True
    
    return False