import requests
from .base import BaseFetcher
from config.settings import settings
import time 

class AdzunaFetcher(BaseFetcher):
    #Fetch Jobs from Adzuna API

    BASE_URL = 'https://api.adzuna.com/v1/api/jobs'

    def __init__(self):
        super().__init__('adzuna')
        self.app_id = settings.ADZUNA_APP_ID
        self.app_key = settings.ADZUNA_APP_KEY

    
    def fetch_jobs(self, keyword, location='us'):
        """
        Fetch jobs from Adzuna

        Args:
            keyword : 'python developer'
            location: 'us'
        
        Returns:
            List of normalized job dictionaries
        """
        if not self.app_id or not self.app_key:
            self.logger.warning("Adzuna API credentials not configured")
            return []

        url = f'{self.BASE_URL}/{location}/search/1'

        parms = {
            'app_id' :  self.app_id,
            'app_key' : self.app_key,
            'what' : keyword,
            'results_per_page': 50,
            # 'content_type' : 'application/json'
        }

        try:
            self.logger.info(f"Fetching jobs from Adzuna: {keyword}")

            response = requests.get(
                url, 
                params = parms,
                timeout=settings.REQUEST_TIMEOUT
            )

            response.raise_for_status()
            data=response.json()

            raw_jobs = data.get('results', [])
            self.logger.info(f"Fetched{len(raw_jobs)} jobs from Adzuna")
            
            # Normalize to standard format
            normalized_jobs = []
            for job in raw_jobs:
                normalized = self._normalize_adzuna_job(job)
                normalized_jobs.append(normalized)
            
            # Respect rate limits
            time.sleep(settings.RATE_LIMIT_DELAY)
            
            return normalized_jobs
            
        except requests.RequestException as e:
            self.logger.error(f"Adzuna API error: {e}")
            return []
        except Exception as e:
            self.logger.exception(f"Unexpected error fetching from Adzuna: {e}")
            return []
        
    
    def _normalize_adzuna_job(self, raw_job):
        """Convert Adzuna format to our standard format"""
        return {
            'external_id': raw_job.get('id', ''),
            'title': raw_job.get('title', ''),
            'company': raw_job.get('company', {}).get('display_name', 'Unknown'),
            'location': raw_job.get('location', {}).get('display_name', ''),
            'description': raw_job.get('description', ''),
            'url': raw_job.get('redirect_url', ''),
            'job_type': raw_job.get('contract_type'),
            'salary_min': raw_job.get('salary_min'),
            'salary_max': raw_job.get('salary_max'),
            'posted_date': raw_job.get('created')
        }