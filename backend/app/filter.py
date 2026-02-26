"""
Job filtering service
Filters jobs based on location and skill keywords
"""
import logging
from typing import List
import re

from app.models import Job, JobStatus

logger = logging.getLogger(__name__)


class JobFilter:
    """Filter jobs based on criteria"""
    
    def __init__(self, location_keywords: List[str], skill_keywords: List[str], 
                 location_radius_km: int = 30):
        self.location_keywords = [kw.lower() for kw in location_keywords]
        self.skill_keywords = [kw.lower() for kw in skill_keywords]
        self.location_radius_km = location_radius_km
    
    def calculate_match_score(self, job: Job) -> int:
        """
        Calculate match score for job (0-100)
        Based on skill keyword matches in title and description
        """
        score = 0
        text = f"{job.title} {job.description}".lower()
        
        # Check skill keywords (each match adds points)
        skill_matches = 0
        for keyword in self.skill_keywords:
            if keyword in text:
                skill_matches += 1
        
        # Base score from skill matches (max 80 points)
        if skill_matches > 0:
            score = min(80, skill_matches * 15)
        
        # Bonus for title matches (20 points)
        title_lower = job.title.lower()
        for keyword in self.skill_keywords:
            if keyword in title_lower:
                score += 20
                break
        
        # Cap at 100
        return min(100, score)
    
    def matches_location(self, job: Job) -> bool:
        """Check if job location matches criteria"""
        location_lower = job.location.lower()
        
        # Check if any location keyword matches
        for keyword in self.location_keywords:
            if keyword in location_lower:
                return True
        
        # Additional location keywords that might indicate nearby
        if "remote" in location_lower or "belgium" in location_lower:
            return True
        
        return False
    
    def matches_skills(self, job: Job, min_score: int = 30) -> bool:
        """Check if job matches skill requirements"""
        score = self.calculate_match_score(job)
        return score >= min_score
    
    def filter_job(self, job: Job, min_score: int = 30) -> Job:
        """
        Filter single job and update status and match score
        
        Returns job with updated status and match_score
        """
        # Check location
        if not self.matches_location(job):
            logger.info(f"Job filtered out (location): {job.title} - {job.location}")
            job.status = JobStatus.FILTERED
            job.match_score = 0
            return job
        
        # Calculate match score
        job.match_score = self.calculate_match_score(job)
        
        # Check if meets minimum score
        if job.match_score < min_score:
            logger.info(f"Job filtered out (low score {job.match_score}): {job.title}")
            job.status = JobStatus.FILTERED
            return job
        
        # Job passes filter
        logger.info(f"Job passed filter (score {job.match_score}): {job.title}")
        job.status = JobStatus.NEW
        return job
    
    def filter_jobs(self, jobs: List[Job], min_score: int = 30) -> List[Job]:
        """
        Filter list of jobs
        
        Returns only jobs that pass the filter
        """
        filtered_jobs = []
        for job in jobs:
            filtered_job = self.filter_job(job, min_score)
            if filtered_job.status != JobStatus.FILTERED:
                filtered_jobs.append(filtered_job)
        
        logger.info(f"Filtered {len(jobs)} jobs -> {len(filtered_jobs)} passed")
        return filtered_jobs
