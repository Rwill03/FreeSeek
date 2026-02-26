"""
Database models for Freelance Auto Hunter
"""
from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel


class JobStatus(str, Enum):
    """Job application status"""
    NEW = "new"
    FILTERED = "filtered"
    PROPOSAL_GENERATED = "proposal_generated"
    APPLIED = "applied"
    MANUAL_REVIEW = "manual_review"
    FAILED = "failed"
    DUPLICATE = "duplicate"


class Platform(str, Enum):
    """Supported job platforms"""
    LINKEDIN = "linkedin"
    INDEED = "indeed"
    UPWORK = "upwork"


class Job(BaseModel):
    """Job model"""
    id: Optional[int] = None
    title: str
    company: str
    description: str
    budget: Optional[str] = None
    url: str
    url_hash: str
    location: str
    platform: Platform
    status: JobStatus = JobStatus.NEW
    match_score: int = 0
    created_at: Optional[datetime] = None
    applied_at: Optional[datetime] = None


class Proposal(BaseModel):
    """Proposal model"""
    id: Optional[int] = None
    job_id: int
    content: str
    generated_at: Optional[datetime] = None


class Application(BaseModel):
    """Application tracking model"""
    id: Optional[int] = None
    job_id: int
    proposal_id: int
    status: JobStatus
    error_message: Optional[str] = None
    applied_at: Optional[datetime] = None


class DashboardStats(BaseModel):
    """Dashboard statistics"""
    jobs_found_today: int
    applications_sent_today: int
    pending_manual: int
    failed_today: int
    success_rate: float
    total_jobs: int
