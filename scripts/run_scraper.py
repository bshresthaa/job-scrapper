# scripts/run_scraper.py
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.models.database import db
from src.fetchers.adzuna import AdzunaFetcher
from src.services.deduplicator import is_duplicate, generate_content_hash
from src.services.notifier import Notifier
from src.utils.logger import setup_logger
from config.settings import settings

logger = setup_logger(__name__)

def main():
    """Main scraper logic"""
    logger.info("=" * 60)
    logger.info("Starting job scraper")
    logger.info("=" * 60)
    
    # Ensure sources are registered
    source = db.get_source_by_name('adzuna')
    if not source:
        db.insert_source('adzuna', AdzunaFetcher.BASE_URL)
        source = db.get_source_by_name('adzuna')
    
    source_id = source['id']
    
    # Initialize fetcher
    fetcher = AdzunaFetcher()
    
    total_new_jobs = 0
    total_duplicates = 0
    
    # Fetch jobs for each keyword
    for keyword in settings.KEYWORDS:
        logger.info(f"Searching for: {keyword}")
        
        jobs = fetcher.fetch_jobs(keyword)
        
        for job in jobs:
            job['source_id'] = source_id
            
            # Check for duplicates
            if is_duplicate(job, db):
                total_duplicates += 1
                continue
            
            # Insert new job
            job_id = db.insert_job(job)
            
            if job_id:
                total_new_jobs += 1
                logger.info(f"New job found: {job['title']} at {job['company']}")
                
                # Send notifications
                job['id'] = job_id
                notification_results = Notifier.notify(job)
                
                # Record notifications
                for channel, success in notification_results.items():
                    if success:
                        db.record_notification(job_id, channel)
    
    logger.info("=" * 60)
    logger.info(f"Scraper finished")
    logger.info(f"New jobs: {total_new_jobs}")
    logger.info(f"Duplicates skipped: {total_duplicates}")
    logger.info("=" * 60)

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        logger.exception(f"Scraper crashed: {e}")
        sys.exit(1)