# src/services/notifier.py
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
from config.settings import settings
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class Notifier:
    """Send job notifications via email and Discord"""
    
    @staticmethod
    def send_email(job):
        """Send email notification for new job"""
        if not settings.EMAIL_FROM or not settings.EMAIL_TO:
            logger.warning("Email not configured")
            return False
        
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"🎯 New Job: {job['title']} at {job['company']}"
            msg['From'] = settings.EMAIL_FROM
            msg['To'] = settings.EMAIL_TO
            
            # Email body
            text = f"""
New job posting found!

Title: {job['title']}
Company: {job['company']}
Location: {job.get('location', 'N/A')}
Type: {job.get('job_type', 'N/A')}

Apply here: {job['url']}

---
Sent by Job Scraper
            """
            
            html = f"""
<html>
  <body>
    <h2>🎯 New Job Posting</h2>
    <p><strong>{job['title']}</strong> at <strong>{job['company']}</strong></p>
    <ul>
      <li><strong>Location:</strong> {job.get('location', 'N/A')}</li>
      <li><strong>Type:</strong> {job.get('job_type', 'N/A')}</li>
      <li><strong>Salary:</strong> {job.get('salary_min', 'N/A')} - {job.get('salary_max', 'N/A')}</li>
    </ul>
    <p><a href="{job['url']}">Apply Now</a></p>
  </body>
</html>
            """
            
            msg.attach(MIMEText(text, 'plain'))
            msg.attach(MIMEText(html, 'html'))
            
            # Send email
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                server.starttls()
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.send_message(msg)
            
            logger.info(f"Email sent for job: {job['title']}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False
    
    @staticmethod
    def send_discord(job):
        """Send Discord notification via webhook"""
        if not settings.DISCORD_WEBHOOK:
            logger.warning("Discord webhook not configured")
            return False
        
        try:
            embed = {
                "title": f"{job['title']}",
                "description": f"**{job['company']}** - {job.get('location', 'N/A')}",
                "color": 3447003,  # Blue
                "fields": [
                    {
                        "name": "Type",
                        "value": job.get('job_type', 'N/A'),
                        "inline": True
                    },
                    {
                        "name": "Experience",
                        "value": job.get('experience_level', 'N/A'),
                        "inline": True
                    }
                ],
                "url": job['url']
            }
            
            payload = {
                "username": "Job Scraper Bot",
                "embeds": [embed]
            }
            
            response = requests.post(settings.DISCORD_WEBHOOK, json=payload)
            response.raise_for_status()
            
            logger.info(f"Discord notification sent for job: {job['title']}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send Discord notification: {e}")
            return False
    
    @staticmethod
    def notify(job, channels=['email', 'discord']):
        """Send notifications via specified channels"""
        results = {}
        
        if 'email' in channels:
            results['email'] = Notifier.send_email(job)
        
        if 'discord' in channels:
            results['discord'] = Notifier.send_discord(job)
        
        return results