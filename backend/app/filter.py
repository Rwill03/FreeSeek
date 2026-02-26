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
    
    def is_it_job(self, job: Job) -> bool:
        """
        Check if job is an IT/tech position
        
        Returns True if job appears to be IT-related,
        False if it's clearly non-IT (sales, marketing, support, etc)
        """
        text = f"{job.title} {job.description}".lower()
        title_lower = job.title.lower()
        
        # Non-IT exclusion keywords - strong indicators of non-IT jobs
        non_it_keywords = [
            "sales", "account manager", "business development",
            "marketing", "content", "copywriter", "seo specialist",
            "recruiter", "hr", "human resources", "talent acquisition",
            "fundraiser", "volunteer", "ambassador", "community manager",
            "customer success", "customer support", "support",
            "administrative", "legal", "accountant", "finance", "accounting",
            "growth", "daily spotlight", "restaurant", "chef", "cook",
            "writer", "journalist", "design", "graphic", "illustrator",
            "structural", "architectural", "construction", "building", "plumbing",
            "hvac", "electrical", "carpentry", "salon", "beauty", "hair",
            "counselling", "psychotherapy", "therapy", "counselor"
        ]
        
        # Count non-IT keywords in title (stricter for title matching)
        non_it_in_title = sum(1 for keyword in non_it_keywords if keyword in title_lower)
        non_it_in_text = sum(1 for keyword in non_it_keywords if keyword in text)
        
        # If strong non-IT signals, exclude
        if non_it_in_title >= 1 or non_it_in_text >= 2:
            logger.debug(f"Excluding non-IT job: {job.title}")
            return False
        
        # Core IT keywords that strongly indicate an IT job
        core_it_keywords = [
            "developer", "programmer", "python", "javascript", "typescript",
            "java", "c#", "c++", "react", "api", "database", "sql",
            "backend", "frontend", "fullstack", "full stack", "devops",
            "kubernetes", "docker", "aws", "azure", "gcp", "cloud",
            "software", "code", "coding", "programming",
            "ai", "machine learning", "data science", "nlp", "blockchain",
            "security", "cybersecurity", "penetration", "testing", "qa",
            "web development", "web developer"
        ]
        
        # Check for core IT keywords
        core_it_score = sum(1 for keyword in core_it_keywords if keyword in text)
        
        # If has core IT keywords, include it
        if core_it_score > 0:
            return True
        
        # "Engineer" alone is risky - check in context
        if "engineer" in text and core_it_score == 0:
            # Check if this engineer is clearly IT (DevOps, Software, Web, etc.)
            it_engineer_patterns = ["software engineer", "web engineer", "devops", "platform engineer", "cloud engineer"]
            if any(pattern in text for pattern in it_engineer_patterns):
                return True
            # Otherwise, it might be civil/architectural/etc - skip it
            return False
        
        # Supplementary keywords (less strict)
        supplementary_keywords = [
            "tech", "application", "system", "platform", "framework",
            "infrastructure", "deployment", "automation"
        ]
        
        supp_score = sum(1 for keyword in supplementary_keywords if keyword in text)
        
        # If has multiple supplementary keywords and is remote/freelance, likely IT
        if supp_score >= 2 and ("remote" in text or "freelance" in text):
            return True
        
        # Default: exclude if no IT indicators found
        return False
    
    
    def filter_job(self, job: Job, min_score: int = 30) -> Job:
        """
        Filter single job and update status and match score
        
        Returns job with updated status and match_score
        """
        # First check if it's an IT-related job
        if not self.is_it_job(job):
            logger.info(f"Job filtered out (not IT): {job.title} at {job.company}")
            job.status = JobStatus.FILTERED
            job.match_score = 0
            return job
        
        # Check location
        if not self.matches_location(job):
            logger.info(f"Job filtered out (location): {job.title} - {job.location}")
            job.status = JobStatus.FILTERED
            job.match_score = 0
            return job
        
        # Calculate match score
        job.match_score = self.calculate_match_score(job)
        
        # For IT jobs, require higher minimum score - generic titles need more keywords
        # "Engineer" alone needs at least 50 points to be included
        min_score_for_job = min_score
        if "engineer" in job.title.lower() and job.match_score < 50:
            # Generic engineer title without enough skill matches
            logger.info(f"Job filtered out (low score {job.match_score} for generic job): {job.title}")
            job.status = JobStatus.FILTERED
            return job
        
        # Check if meets minimum score
        if job.match_score < min_score_for_job:
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
