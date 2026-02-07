import os   #import OS          
from dotenv import load_dotenv  #import dotenv

load_dotenv()   #load dot.env

class Settings:

    #database
    DATABASE_PATH = os.getenv('DATABASE_PATH', 'data/jobs.db')

    #API KEYS
    ADZUNA_APP_ID = os.getenv('ADZUNA_APP_ID', '')
    ADZUNA_APP_KEY = os.getenv('ADZUNA_APP_KEY', '')

    # Notifications
    EMAIL_FROM = os.getenv('EMAIL_FROM', '')
    EMAIL_TO = os.getenv('EMAIL_TO', '')
    SMTP_HOST = os.getenv('SMTP_HOST', 'smtp.gmail.com')
    SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
    SMTP_USER = os.getenv('SMTP_USER', '')
    SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')
    
    DISCORD_WEBHOOK = os.getenv('DISCORD_WEBHOOK', '')

    #Scrapping
    REQUEST_TIMEOUT = 10 
    RATE_LIMIT_DELAY = 1
    MAX_RETRIES = 3

    #FILTERS
    KEYWORDS = ["python","java","api","backend"]
    EXPERIENCE_LEVEL = "junior"
    LOCATIONS = ["remote", "texas","newyork"]

settings = Settings()

