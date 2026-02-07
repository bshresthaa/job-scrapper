import sqlite3
from contextlib import contextmanager
from datetime import datetime
from config.settings import settings
import os

class Database:
    def __init__(self, db_path = None):
        self.db_path = db_path or settings.DATABASE_PATH
        self.ensure_db_exists()

    def ensure_db_exists(self):
        #Create db and tables if they don't exists yet
        os.makedirs(os.path.dirname(self.db_path), exist_ok = True)

        with self.get_connection() as conn:
            conn.executescript('''
                CREATE TABLE IF NOT EXISTS sources (
                               id INTEGER PRIMARY KEY AUTOINCREMENT,
                               name TEXT NOT NULL UNIQUE,
                               base_url TEXT NOT NULL,
                               api_key TEXT,
                               is_active BOOLEAN DEFAULT 1,
                               last_scrapped_at TIMESTAMP,
                               created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP         
                );   

                CREATE TABLE IF NOT EXISTS jobs(
                               id INTEGER PRIMARY KEY AUTOINCREMENT,
                               source_id INTEGER NOT NULL,
                               external_id TEXT NOT NULL,
                               title TEXT NOT NULL,
                               company TEXT NOT NULL,
                               location TEXT NOT NULL,
                               description TEXT NOT NULL,
                               job_type TEXT,
                               experience_level TEXT,
                               salary_min INTEGER,
                               salary_max INTEGER,
                               salary_currency TEXT DEFAULT 'USD', 
                               url TEXT NOT NULL,
                               posted_date TIMESTAMP,
                               scrapped_at TIMESTAMP CURRENT_TIMESTAMP,
                               is_active BOOLEAN DEFAULT 1,
                               content_hash TEXT,

                               FOREIGN KEY (source_id) REFERENCES sources(id), UNIQUE(source_id, external_id)
                );
                
                CREATE INDEX IF NOT EXISTS idx_jobs_title ON jobs(title);
                CREATE INDEX IF NOT EXISTS idx_jobs_location ON jobs(location);
                CREATE INDEX IF NOT EXISTS idx_jobs_posted_date ON jobs(posted_date DESC);
                CREATE INDEX IF NOT EXISTS idx_jobs_company ON jobs(company);
                CREATE INDEX IF NOT EXISTS idx_content_hash ON jobs(content_hash);
                               
                CREATE TABLE IF NOT EXISTS applications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    job_id INTEGER NOT NULL,
                    status TEXT NOT NULL DEFAULT 'applied',
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    notes TEXT,
                    resume_version TEXT,
                    
                    FOREIGN KEY (job_id) REFERENCES jobs(id)
                );
                
                CREATE TABLE IF NOT EXISTS notifications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    job_id INTEGER NOT NULL,
                    channel TEXT NOT NULL,
                    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'sent',
                    
                    FOREIGN KEY (job_id) REFERENCES jobs(id)
                );               
                    ''')
    
    @contextmanager
    def get_connection(self): 
        #context manager for database connections
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except:
            conn.rollback()
            raise
        finally:
            conn.close()
        
    def insert_source(self, name, base_url, api_key=None):
        #add a job source
        with self.get_connection() as conn: 
            cursor = conn.execute(
                'INSERT OR IGNORE INTO sources (name, base_url,api_key) VALUES (?,?,?)',
                (name, base_url,api_key)
            )
            return cursor.lastrowid
    
    def get_source_by_name(self,name): 
        with self.get_connection() as conn:
            row = conn.execute(
                'SELECT * FROM sources WHERE name = ?',
                (name,) ).fetchone()
            return dict(row) if row else None; 

    def insert_job(self, job_data):
        #insert a new job
        with self.get_connection() as conn:
            try:
                    cursor = conn.execute('''
                        INSERT INTO jobs (
                            source_id, external_id, title, company, location,
                            description, job_type, experience_level,
                            salary_min, salary_max, salary_currency,
                            url, posted_date, content_hash
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        job_data['source_id'],
                        job_data['external_id'],
                        job_data['title'],
                        job_data['company'],
                        job_data.get('location'),
                        job_data.get('description'),
                        job_data.get('job_type'),
                        job_data.get('experience_level'),
                        job_data.get('salary_min'),
                        job_data.get('salary_max'),
                        job_data.get('salary_currency', 'USD'),
                        job_data['url'],
                        job_data.get('posted_date'),
                        job_data.get('content_hash')
                    ))
                    return cursor.lastrowid
            except sqlite3.IntegrityError:
                    # Duplicate job
                    return None 

    def job_exists_by_hash(self,content_hash):
            #check if job exists by content hash
            with self.get_connection() as conn:
                row = conn.execute(
                    'SELECT id FROM jobs WHERE content_hash = ? AND  is_active = 1',
                    (content_hash,) ).fetchone()
                return row is not None
                

    def query_jobs(self, keyword=None, location=None, limit=50):
            #Query jobs with filter
            query = 'SELECT * FROM jobs WHERE is_active =1'
            parms = []

            if keyword:
                query += ' AND (title LIKE ? or description LIKE ? OR company LIKE ?)'
                search_term = f'%{keyword}%'
                parms.extend([search_term, search_term, search_term])

            if location:
                query += ' AND location LIKE ?'
                parms.append(f'%{location}%')
        
            with self.get_connection() as conn:
                rows = conn.execute(query, parms).fetchall()
                return [dict(row) for row in rows]
    

    def track_applicatoin(self, job_id, notes=None):
            with self.get_connection() as conn:
                cursor = conn.execute(
                    'INSERT INTO applications (job_id, notes) VALUES (?,?)',
                    (job_id, notes)
                )
                return cursor.lastrowid

    def get_application(self, status=None):
            query = '''
                SELECT a.*, j.title, j.company, j.url
                FROM applications a 
                JOIN jobs j ON a.job_id = j.id
                '''
            parms = []

            if status:
                query += 'WHERE a.status = ?'
                parms.append(status)
        
            query += 'ORDER BY a.applied_at DESC'

            with self.get_connection() as conn:
                rows = conn.execute(query, parms).fetachall()
                return [dict(row) for row in rows]
            
    def record_notification(self, job_id, channel):
        """Record that notification was sent"""
        with self.get_connection() as conn:
            conn.execute(
                'INSERT INTO notifications (job_id, channel) VALUES (?, ?)',
                (job_id, channel)
            )
            
db = Database()
