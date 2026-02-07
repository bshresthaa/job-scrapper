# scripts/cli.py
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import argparse
from src.models.database import db
from scripts.run_scraper import main as run_scraper

def list_jobs(args):
    """List jobs"""
    jobs = db.query_jobs(keyword=args.keyword, location=args.location, limit=args.limit)
    
    if not jobs:
        print("No jobs found")
        return
    
    print(f"\nFound {len(jobs)} jobs:\n")
    print("-" * 80)
    
    for job in jobs:
        print(f"ID: {job['id']}")
        print(f"Title: {job['title']}")
        print(f"Company: {job['company']}")
        print(f"Location: {job.get('location', 'N/A')}")
        print(f"URL: {job['url']}")
        print("-" * 80)

def track_application(args):
    """Track job application"""
    job = db.get_job(args.job_id)
    
    if not job:
        print(f"Job {args.job_id} not found")
        return
    
    db.track_application(args.job_id, args.notes)
    print(f"✓ Tracked application for: {job['title']} at {job['company']}")

def show_applications(args):
    """Show applications"""
    apps = db.get_applications(status=args.status)
    
    if not apps:
        print("No applications found")
        return
    
    print(f"\nFound {len(apps)} applications:\n")
    print("-" * 80)
    
    for app in apps:
        print(f"Applied: {app['applied_at']}")
        print(f"Job: {app['title']} at {app['company']}")
        print(f"Status: {app['status']}")
        if app.get('notes'):
            print(f"Notes: {app['notes']}")
        print("-" * 80)

def main():
    parser = argparse.ArgumentParser(description='Job Scraper CLI')
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Scrape command
    scrape_parser = subparsers.add_parser('scrape', help='Run scraper')
    
    # List jobs command
    list_parser = subparsers.add_parser('list', help='List jobs')
    list_parser.add_argument('--keyword', help='Filter by keyword')
    list_parser.add_argument('--location', help='Filter by location')
    list_parser.add_argument('--limit', type=int, default=20, help='Max results')
    
    # Apply command
    apply_parser = subparsers.add_parser('apply', help='Track application')
    apply_parser.add_argument('job_id', type=int, help='Job ID')
    apply_parser.add_argument('--notes', help='Application notes')
    
    # Applications command
    apps_parser = subparsers.add_parser('applications', help='Show applications')
    apps_parser.add_argument('--status', help='Filter by status')
    
    args = parser.parse_args()
    
    if args.command == 'scrape':
        run_scraper()
    elif args.command == 'list':
        list_jobs(args)
    elif args.command == 'apply':
        track_application(args)
    elif args.command == 'applications':
        show_applications(args)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()