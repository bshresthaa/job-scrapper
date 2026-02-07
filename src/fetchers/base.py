from abc import ABC, abstractmethod
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class BaseFetcher(ABC):
    #abstract base class for job fetchers

    def __init__(self, source_name):
        self.source_name = source_name
        self.logger = logger
    
    @abstractmethod
    def fetch_jobs(self, keyword, location=None):
        #Fetch jobs from source
        pass
    
    def normalize_job(self, raw_job):
        #Convert raw job data to standard format
        return {
            'external_id' : str(raw_job.get('id','')),
            'title': raw_job.get('title', ''),
            'company': raw_job.get('company', ''),
            'location': raw_job.get('location', ''),
            'description': raw_job.get('description', ''),
            'url': raw_job.get('url', ''),
            'job_type': raw_job.get('type'),
            'posted_date': raw_job.get('created_at')
        }
