"""
Job scheduler for automated job hunting
Runs every 3 hours during business hours (8am-6pm) on weekdays
"""
import asyncio
import logging
from datetime import datetime, time
from typing import Optional
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from app.database import Database
from app.scraper import scrape_jobs
from app.filter import JobFilter
from app.llm_service import LLMService
from app.apply_bot import apply_to_job
from app.models import JobStatus, Job

logger = logging.getLogger(__name__)


class JobHunterScheduler:
    """Scheduler for automated job hunting"""
    
    def __init__(
        self,
        db: Database,
        job_filter: JobFilter,
        llm_service: LLMService,
        cv_path: str,
        max_applications_per_day: int = 10,
        auto_apply_enabled: bool = False,
        location: str = "Bruges"
    ):
        """
        Initialize scheduler
        
        Args:
            db: Database instance
            job_filter: Job filter instance
            llm_service: LLM service instance
            cv_path: Path to CV file
            max_applications_per_day: Maximum applications to send per day
            auto_apply_enabled: Whether to automatically apply to jobs
            location: Target location for job search
        """
        self.db = db
        self.job_filter = job_filter
        self.llm_service = llm_service
        self.cv_path = cv_path
        self.max_applications_per_day = max_applications_per_day
        self.auto_apply_enabled = auto_apply_enabled
        self.location = location
        
        self.scheduler = AsyncIOScheduler()
        self._running = False
        self._currently_scanning = False  # Track if a scan is in progress
    
    def is_business_hours(self) -> bool:
        """Check if current time is within business hours - DISABLED, always returns True"""
        # Business hours check is disabled - scanning runs 24/7
        return True
    
    async def run_job_scan(self):
        """Run complete job scanning and application process"""
        self._currently_scanning = True  # Mark scan as started
        
        logger.info("=" * 60)
        logger.info("Starting automated job scan")
        logger.info("=" * 60)
        
        try:
            # Check if we should run
            if not self.is_business_hours():
                logger.info("Skipping scan - outside business hours")
                return
            
            # Check daily application limit
            today_count = self.db.get_applications_count_today()
            if today_count >= self.max_applications_per_day:
                logger.info(f"Daily limit reached: {today_count}/{self.max_applications_per_day}")
                return
            
            # Step 1: Scrape jobs
            logger.info("Step 1: Scraping jobs...")
            jobs = await scrape_jobs(location=self.location, headless=True)
            logger.info(f"Found {len(jobs)} jobs")
            
            # Step 2: Filter jobs
            logger.info("Step 2: Filtering jobs...")
            filtered_jobs = self.job_filter.filter_jobs(jobs, min_score=30)
            logger.info(f"Filtered to {len(filtered_jobs)} relevant jobs")
            
            # Step 3: Save to database
            logger.info("Step 3: Saving to database...")
            new_jobs = []
            for job in filtered_jobs:
                job_id = self.db.create_job(job)
                if job_id:
                    job.id = job_id
                    new_jobs.append(job)
            
            logger.info(f"Saved {len(new_jobs)} new jobs (duplicates skipped)")
            
            # Step 4: Generate proposals and apply (if enabled)
            if self.auto_apply_enabled and new_jobs:
                logger.info("Step 4: Generating proposals and applying...")
                
                # Sort by match score (highest first)
                new_jobs.sort(key=lambda j: j.match_score, reverse=True)
                
                applied_count = 0
                for job in new_jobs:
                    # Check limit
                    current_count = self.db.get_applications_count_today()
                    if current_count >= self.max_applications_per_day:
                        logger.info("Daily application limit reached")
                        break
                    
                    try:
                        # Generate proposal
                        logger.info(f"Generating proposal for: {job.title}")
                        proposal = self.llm_service.generate_proposal_with_variability(
                            job.description, job.title
                        )
                        
                        if not proposal:
                            logger.error("Failed to generate proposal")
                            continue
                        
                        # Save proposal
                        proposal_id = self.db.create_proposal(job.id, proposal)
                        self.db.update_job_status(job.id, JobStatus.PROPOSAL_GENERATED)
                        
                        # Apply to job
                        logger.info(f"Applying to: {job.title}")
                        status, error_msg = await apply_to_job(
                            job, proposal, self.cv_path, headless=True
                        )
                        
                        # Record application
                        self.db.create_application(job.id, proposal_id, status, error_msg)
                        
                        if status == JobStatus.APPLIED:
                            applied_count += 1
                            logger.info(f"✓ Successfully applied! ({applied_count}/{self.max_applications_per_day})")
                        else:
                            logger.info(f"Application status: {status.value}")
                        
                        # Delay between applications (2-6 minutes)
                        import random
                        delay = random.uniform(120, 360)
                        logger.info(f"Waiting {delay:.0f} seconds before next application...")
                        await asyncio.sleep(delay)
                        
                    except Exception as e:
                        logger.error(f"Error processing job {job.title}: {e}")
                        continue
                
                logger.info(f"Applied to {applied_count} jobs in this scan")
            else:
                logger.info("Step 4: Auto-apply disabled - skipping applications")
            
            logger.info("Job scan completed successfully")
            
        except Exception as e:
            logger.error(f"Error in job scan: {e}", exc_info=True)
        
        finally:
            self._currently_scanning = False  # Mark scan as complete
        
        logger.info("=" * 60)
    
    def start(self):
        """Start the scheduler"""
        if self._running:
            logger.warning("Scheduler already running")
            return
        
        # Schedule job every 3 hours
        self.scheduler.add_job(
            self.run_job_scan,
            CronTrigger(hour='*/3'),  # Every 3 hours
            id='job_scan',
            name='Automated Job Scan',
            replace_existing=True
        )
        
        self.scheduler.start()
        self._running = True
        logger.info("Scheduler started - running every 3 hours")
    
    def stop(self):
        """Stop the scheduler"""
        if not self._running:
            return
        
        self.scheduler.shutdown()
        self._running = False
        logger.info("Scheduler stopped")
    
    def is_running(self) -> bool:
        """Check if scheduler is running"""
        return self._running
    
    def is_scanning(self) -> bool:
        """Check if a job scan is currently in progress"""
        return self._currently_scanning
    
    async def run_now(self):
        """Manually trigger a job scan"""
        logger.info("Manual job scan triggered")
        await self.run_job_scan()
