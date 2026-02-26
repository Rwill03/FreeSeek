"""
FastAPI main application for Freelance Auto Hunter
"""
import logging
import os
import asyncio
from contextlib import asynccontextmanager
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from app.database import Database
from app.models import Job, JobStatus, DashboardStats, Proposal
from app.filter import JobFilter
from app.llm_service import LLMService
from app.scheduler import JobHunterScheduler

# Load environment variables
load_dotenv()

# Custom logging handler to collect logs
class LogCollector(logging.Handler):
    """Custom logging handler that collects logs for API retrieval"""
    def __init__(self, max_records=1000):
        super().__init__()
        self.records = []
        self.max_records = max_records
    
    def emit(self, record):
        """Collect log record"""
        try:
            # Only collect scheduler and llm service logs
            if record.name in ['app.scheduler', 'app.llm_service', 'app.scraper', 'app.filter']:
                msg = self.format(record)
                self.records.append(msg)
                # Keep only recent records
                if len(self.records) > self.max_records:
                    self.records.pop(0)
        except Exception:
            self.handleError(record)
    
    def get_logs(self):
        """Get all collected logs as a single string"""
        return '\n'.join(self.records)
    
    def clear(self):
        """Clear collected logs"""
        self.records = []

# Create log collector
log_collector = LogCollector()
log_collector.setFormatter(
    logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("freelance_hunter.log"),
        logging.StreamHandler(),
        log_collector
    ]
)
logger = logging.getLogger(__name__)

# Global instances
db: Database = None
scheduler: JobHunterScheduler = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for FastAPI app"""
    global db, scheduler
    
    # Startup
    logger.info("Starting Freelance Auto Hunter...")
    
    # Initialize database
    db = Database()
    
    # Initialize components
    location_keywords = ["bruges", "brugge", "belgium", "remote"]
    skill_keywords = [
        # Languages
        "python", "javascript", "typescript", "java", "c#", "c++", "rust", "go", "kotlin",
        "php", "ruby", "swift", "objective-c", "groovy", "scala",
        # Frontend
        "react", "vue", "angular", "nextjs", "nuxt", "svelte", "frontend", "ui", "ux",
        "html", "css", "tailwind", "bootstrap",
        # Backend
        "fastapi", "django", "flask", "spring", "express", "nestjs", "rails", "aspnet",
        "backend", "api", "rest", "graphql",
        # Data & AI
        "machine learning", "ai", "data science", "nlp", "computer vision",
        "tensorflow", "pytorch", "scikit-learn", "pandas", "numpy", "analytics",
        # DevOps & Infrastructure
        "devops", "kubernetes", "docker", "aws", "azure", "gcp", "cloud",
        "ci/cd", "jenkins", "gitlab", "github", "infrastructure", "terraform",
        # Database
        "sql", "postgresql", "mysql", "mongodb", "redis", "elasticsearch", "database",
        # Other Tech
        "automation", "odoo", "fullstack", "full stack", "software",
        "developer", "engineer", "programmer", "architect", "qa", "testing",
        "security", "cybersecurity", "blockchain", "web3", "mobile", "ios", "android"
    ]
    
    job_filter = JobFilter(
        location_keywords=location_keywords,
        skill_keywords=skill_keywords,
        location_radius_km=int(os.getenv("LOCATION_RADIUS", "30"))
    )
    
    llm_service = LLMService(
        api_key=os.getenv("LLM_API_KEY", ""),
        provider=os.getenv("LLM_PROVIDER", "groq")
    )
    
    # Initialize scheduler
    scheduler = JobHunterScheduler(
        db=db,
        job_filter=job_filter,
        llm_service=llm_service,
        cv_path=os.getenv("CV_FILE_PATH", "cv.pdf"),
        max_applications_per_day=int(os.getenv("MAX_APPLICATIONS_PER_DAY", "10")),
        auto_apply_enabled=os.getenv("ENABLE_AUTO_APPLY", "false").lower() == "true",
        location=os.getenv("TARGET_LOCATION", "Bruges")
    )
    
    # Start scheduler
    scheduler.start()
    
    logger.info("Application started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down...")
    if scheduler:
        scheduler.stop()
    logger.info("Application stopped")


# Create FastAPI app
app = FastAPI(
    title="Freelance Auto Hunter",
    description="Automated freelance job hunting and application system",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response models
class JobResponse(BaseModel):
    """Job response model"""
    id: int
    title: str
    company: str
    description: str
    budget: Optional[str]
    url: str
    location: str
    platform: str
    status: str
    match_score: int
    created_at: str
    applied_at: Optional[str]


class ProposalResponse(BaseModel):
    """Proposal response model"""
    id: int
    job_id: int
    content: str
    generated_at: str


class RunScanRequest(BaseModel):
    """Request to run job scan"""
    manual: bool = True


class GenerateProposalRequest(BaseModel):
    """Request to generate proposal"""
    job_id: int


class MarkAppliedRequest(BaseModel):
    """Request to mark job as applied"""
    job_id: int


class ToggleAutoApplyRequest(BaseModel):
    """Request to toggle auto-apply"""
    enabled: bool


# API Endpoints
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Freelance Auto Hunter API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/api/stats", response_model=DashboardStats)
async def get_stats():
    """Get dashboard statistics"""
    try:
        stats = db.get_dashboard_stats()
        return stats
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/jobs", response_model=List[JobResponse])
async def get_jobs(status: Optional[str] = None, limit: int = 100):
    """Get jobs list"""
    try:
        if status:
            jobs = db.get_jobs_by_status(JobStatus(status), limit=limit)
        else:
            jobs = db.get_all_jobs(limit=limit)
        
        return [
            JobResponse(
                id=job.id,
                title=job.title,
                company=job.company,
                description=job.description,
                budget=job.budget,
                url=job.url,
                location=job.location,
                platform=job.platform.value,
                status=job.status.value,
                match_score=job.match_score,
                created_at=job.created_at.isoformat() if job.created_at else "",
                applied_at=job.applied_at.isoformat() if job.applied_at else None
            )
            for job in jobs
        ]
    except Exception as e:
        logger.error(f"Error getting jobs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/jobs/{job_id}", response_model=JobResponse)
async def get_job(job_id: int):
    """Get single job by ID"""
    try:
        job = db.get_job(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        return JobResponse(
            id=job.id,
            title=job.title,
            company=job.company,
            description=job.description,
            budget=job.budget,
            url=job.url,
            location=job.location,
            platform=job.platform.value,
            status=job.status.value,
            match_score=job.match_score,
            created_at=job.created_at.isoformat() if job.created_at else "",
            applied_at=job.applied_at.isoformat() if job.applied_at else None
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting job: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/jobs/{job_id}/proposal", response_model=ProposalResponse)
async def get_job_proposal(job_id: int):
    """Get proposal for job"""
    try:
        proposal = db.get_proposal_for_job(job_id)
        if not proposal:
            raise HTTPException(status_code=404, detail="Proposal not found")
        
        return ProposalResponse(
            id=proposal.id,
            job_id=proposal.job_id,
            content=proposal.content,
            generated_at=proposal.generated_at.isoformat() if proposal.generated_at else ""
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting proposal: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/scan")
async def run_scan(request: RunScanRequest):
    """Manually trigger job scan"""
    try:
        if request.manual:
            # Mark as scanning immediately
            scheduler._currently_scanning = True
            # Create and schedule the async task
            asyncio.ensure_future(scheduler.run_job_scan())
            logger.info("Scheduled manual job scan task")
            return {"message": "Job scan started", "status": "running", "scanning": True}
        else:
            raise HTTPException(status_code=400, detail="Invalid request")
    except Exception as e:
        logger.error(f"Error running scan: {e}")
        scheduler._currently_scanning = False
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/generate-proposal")
async def generate_proposal(request: GenerateProposalRequest):
    """Generate proposal for specific job"""
    try:
        job = db.get_job(request.job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        # Check if proposal already exists
        existing = db.get_proposal_for_job(request.job_id)
        if existing:
            return {
                "message": "Proposal already exists",
                "proposal_id": existing.id,
                "content": existing.content
            }
        
        # Generate new proposal
        proposal = scheduler.llm_service.generate_proposal_with_variability(
            job.description, job.title
        )
        
        if not proposal:
            raise HTTPException(status_code=500, detail="Failed to generate proposal")
        
        # Save proposal
        proposal_id = db.create_proposal(request.job_id, proposal)
        db.update_job_status(request.job_id, JobStatus.PROPOSAL_GENERATED)
        
        return {
            "message": "Proposal generated",
            "proposal_id": proposal_id,
            "content": proposal
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating proposal: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/jobs/mark-applied")
async def mark_job_applied(request: MarkAppliedRequest):
    """Mark job as manually applied"""
    try:
        job = db.get_job(request.job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        # Update job status to applied
        from datetime import datetime
        db.update_job_status(request.job_id, JobStatus.APPLIED)
        
        # Update applied_at timestamp
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE jobs SET applied_at = ? WHERE id = ?",
            (datetime.now().isoformat(), request.job_id)
        )
        conn.commit()
        conn.close()
        
        logger.info(f"Job {request.job_id} marked as manually applied")
        return {
            "message": "Job marked as applied successfully",
            "job_id": request.job_id,
            "status": "applied"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error marking job as applied: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/toggle-auto-apply")
async def toggle_auto_apply(request: ToggleAutoApplyRequest):
    """Toggle auto-apply feature"""
    try:
        scheduler.auto_apply_enabled = request.enabled
        status = "enabled" if request.enabled else "disabled"
        logger.info(f"Auto-apply {status}")
        return {
            "message": f"Auto-apply {status}",
            "enabled": request.enabled
        }
    except Exception as e:
        logger.error(f"Error toggling auto-apply: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/scheduler/status")
async def get_scheduler_status():
    """Get scheduler status"""
    try:
        return {
            "running": scheduler.is_running(),
            "scanning": scheduler.is_scanning(),
            "auto_apply_enabled": scheduler.auto_apply_enabled,
            "max_applications_per_day": scheduler.max_applications_per_day,
            "applications_today": db.get_applications_count_today()
        }
    except Exception as e:
        logger.error(f"Error getting scheduler status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/logs")
async def get_logs():
    """Get collected LLM job search logs"""
    try:
        logs_text = log_collector.get_logs()
        return {
            "logs": logs_text if logs_text else "No logs available yet. Run a job scan to generate logs.",
            "timestamp": str(__import__('datetime').datetime.now().isoformat())
        }
    except Exception as e:
        logger.error(f"Error getting logs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
