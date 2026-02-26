"""
Database management for Freelance Auto Hunter
"""
import hashlib
import sqlite3
from datetime import datetime, timedelta
from typing import List, Optional
import logging

from app.models import Job, Proposal, Application, JobStatus, Platform, DashboardStats

logger = logging.getLogger(__name__)


class Database:
    """SQLite database manager"""
    
    def __init__(self, db_path: str = "freelance_hunter.db"):
        self.db_path = db_path
        self.init_db()
    
    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_db(self):
        """Initialize database tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Jobs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                company TEXT NOT NULL,
                description TEXT NOT NULL,
                budget TEXT,
                url TEXT NOT NULL,
                url_hash TEXT UNIQUE NOT NULL,
                location TEXT NOT NULL,
                platform TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'new',
                match_score INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                applied_at TIMESTAMP
            )
        """)
        
        # Proposals table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS proposals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id INTEGER NOT NULL,
                content TEXT NOT NULL,
                generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (job_id) REFERENCES jobs (id)
            )
        """)
        
        # Applications table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id INTEGER NOT NULL,
                proposal_id INTEGER NOT NULL,
                status TEXT NOT NULL,
                error_message TEXT,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (job_id) REFERENCES jobs (id),
                FOREIGN KEY (proposal_id) REFERENCES proposals (id)
            )
        """)
        
        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_jobs_created ON jobs(created_at)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_jobs_url_hash ON jobs(url_hash)")
        
        conn.commit()
        conn.close()
        logger.info("Database initialized successfully")
    
    def hash_url(self, url: str) -> str:
        """Generate hash for URL to detect duplicates"""
        return hashlib.sha256(url.encode()).hexdigest()
    
    def job_exists(self, url: str) -> bool:
        """Check if job already exists"""
        conn = self.get_connection()
        cursor = conn.cursor()
        url_hash = self.hash_url(url)
        cursor.execute("SELECT 1 FROM jobs WHERE url_hash = ?", (url_hash,))
        exists = cursor.fetchone() is not None
        conn.close()
        return exists
    
    def create_job(self, job: Job) -> Optional[int]:
        """Create new job entry"""
        if self.job_exists(job.url):
            logger.warning(f"Job already exists: {job.url}")
            return None
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        job.url_hash = self.hash_url(job.url)
        
        cursor.execute("""
            INSERT INTO jobs (title, company, description, budget, url, url_hash, 
                            location, platform, status, match_score)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (job.title, job.company, job.description, job.budget, job.url,
              job.url_hash, job.location, job.platform.value, job.status.value,
              job.match_score))
        
        job_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        logger.info(f"Created job: {job.title} (ID: {job_id})")
        return job_id
    
    def get_job(self, job_id: int) -> Optional[Job]:
        """Get job by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM jobs WHERE id = ?", (job_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return Job(
                id=row['id'],
                title=row['title'],
                company=row['company'],
                description=row['description'],
                budget=row['budget'],
                url=row['url'],
                url_hash=row['url_hash'],
                location=row['location'],
                platform=Platform(row['platform']),
                status=JobStatus(row['status']),
                match_score=row['match_score'],
                created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None,
                applied_at=datetime.fromisoformat(row['applied_at']) if row['applied_at'] else None
            )
        return None
    
    def get_jobs_by_status(self, status: JobStatus, limit: int = 100) -> List[Job]:
        """Get jobs by status"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM jobs WHERE status = ? ORDER BY created_at DESC LIMIT ?",
            (status.value, limit)
        )
        rows = cursor.fetchall()
        conn.close()
        
        return [Job(
            id=row['id'],
            title=row['title'],
            company=row['company'],
            description=row['description'],
            budget=row['budget'],
            url=row['url'],
            url_hash=row['url_hash'],
            location=row['location'],
            platform=Platform(row['platform']),
            status=JobStatus(row['status']),
            match_score=row['match_score'],
            created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None,
            applied_at=datetime.fromisoformat(row['applied_at']) if row['applied_at'] else None
        ) for row in rows]
    
    def update_job_status(self, job_id: int, status: JobStatus):
        """Update job status"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE jobs SET status = ? WHERE id = ?", (status.value, job_id))
        conn.commit()
        conn.close()
        logger.info(f"Updated job {job_id} status to {status.value}")
    
    def create_proposal(self, job_id: int, content: str) -> int:
        """Create proposal for job"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO proposals (job_id, content) VALUES (?, ?)",
            (job_id, content)
        )
        proposal_id = cursor.lastrowid
        conn.commit()
        conn.close()
        logger.info(f"Created proposal {proposal_id} for job {job_id}")
        return proposal_id
    
    def get_proposal(self, proposal_id: int) -> Optional[Proposal]:
        """Get proposal by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM proposals WHERE id = ?", (proposal_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return Proposal(
                id=row['id'],
                job_id=row['job_id'],
                content=row['content'],
                generated_at=datetime.fromisoformat(row['generated_at']) if row['generated_at'] else None
            )
        return None
    
    def get_proposal_for_job(self, job_id: int) -> Optional[Proposal]:
        """Get proposal for specific job"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM proposals WHERE job_id = ? ORDER BY generated_at DESC LIMIT 1",
            (job_id,)
        )
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return Proposal(
                id=row['id'],
                job_id=row['job_id'],
                content=row['content'],
                generated_at=datetime.fromisoformat(row['generated_at']) if row['generated_at'] else None
            )
        return None
    
    def create_application(self, job_id: int, proposal_id: int, status: JobStatus, 
                          error_message: Optional[str] = None) -> int:
        """Record application attempt"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO applications (job_id, proposal_id, status, error_message)
            VALUES (?, ?, ?, ?)
        """, (job_id, proposal_id, status.value, error_message))
        app_id = cursor.lastrowid
        
        # Update job status and applied_at timestamp
        cursor.execute("""
            UPDATE jobs SET status = ?, applied_at = CURRENT_TIMESTAMP WHERE id = ?
        """, (status.value, job_id))
        
        conn.commit()
        conn.close()
        logger.info(f"Created application {app_id} for job {job_id}")
        return app_id
    
    def get_applications_count_today(self) -> int:
        """Get count of successful applications today"""
        conn = self.get_connection()
        cursor = conn.cursor()
        today = datetime.now().date()
        cursor.execute("""
            SELECT COUNT(*) as count FROM applications 
            WHERE DATE(applied_at) = ? AND status = ?
        """, (today, JobStatus.APPLIED.value))
        count = cursor.fetchone()['count']
        conn.close()
        return count
    
    def get_dashboard_stats(self) -> DashboardStats:
        """Get dashboard statistics"""
        conn = self.get_connection()
        cursor = conn.cursor()
        today = datetime.now().date()
        
        # Jobs found today
        cursor.execute("SELECT COUNT(*) as count FROM jobs WHERE DATE(created_at) = ?", (today,))
        jobs_today = cursor.fetchone()['count']
        
        # Applications sent today
        cursor.execute("""
            SELECT COUNT(*) as count FROM applications 
            WHERE DATE(applied_at) = ? AND status = ?
        """, (today, JobStatus.APPLIED.value))
        apps_today = cursor.fetchone()['count']
        
        # Pending manual review
        cursor.execute("""
            SELECT COUNT(*) as count FROM jobs WHERE status = ?
        """, (JobStatus.MANUAL_REVIEW.value,))
        pending = cursor.fetchone()['count']
        
        # Failed today
        cursor.execute("""
            SELECT COUNT(*) as count FROM applications 
            WHERE DATE(applied_at) = ? AND status = ?
        """, (today, JobStatus.FAILED.value))
        failed = cursor.fetchone()['count']
        
        # Total jobs
        cursor.execute("SELECT COUNT(*) as count FROM jobs")
        total = cursor.fetchone()['count']
        
        # Success rate
        cursor.execute("SELECT COUNT(*) as count FROM applications WHERE status = ?", 
                      (JobStatus.APPLIED.value,))
        success = cursor.fetchone()['count']
        cursor.execute("SELECT COUNT(*) as count FROM applications")
        total_apps = cursor.fetchone()['count']
        success_rate = (success / total_apps * 100) if total_apps > 0 else 0.0
        
        conn.close()
        
        return DashboardStats(
            jobs_found_today=jobs_today,
            applications_sent_today=apps_today,
            pending_manual=pending,
            failed_today=failed,
            success_rate=round(success_rate, 2),
            total_jobs=total
        )
    
    def get_all_jobs(self, limit: int = 100) -> List[Job]:
        """Get all jobs with limit"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM jobs ORDER BY created_at DESC LIMIT ?", (limit,))
        rows = cursor.fetchall()
        conn.close()
        
        return [Job(
            id=row['id'],
            title=row['title'],
            company=row['company'],
            description=row['description'],
            budget=row['budget'],
            url=row['url'],
            url_hash=row['url_hash'],
            location=row['location'],
            platform=Platform(row['platform']),
            status=JobStatus(row['status']),
            match_score=row['match_score'],
            created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None,
            applied_at=datetime.fromisoformat(row['applied_at']) if row['applied_at'] else None
        ) for row in rows]
