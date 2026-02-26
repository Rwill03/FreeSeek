"""
Auto-apply bot for submitting job applications
Uses Playwright for browser automation
"""
import asyncio
import logging
import random
from pathlib import Path
from typing import Optional, Tuple
from playwright.async_api import async_playwright, Browser, Page, TimeoutError as PlaywrightTimeout

from app.models import Job, Platform, JobStatus

logger = logging.getLogger(__name__)


class AutoApplyBot:
    """Automated job application bot"""
    
    def __init__(self, cv_path: str, headless: bool = True):
        """
        Initialize bot
        
        Args:
            cv_path: Path to CV/resume PDF file
            headless: Run browser in headless mode
        """
        self.cv_path = Path(cv_path)
        if not self.cv_path.exists():
            raise FileNotFoundError(f"CV file not found: {cv_path}")
        
        self.headless = headless
        self.browser: Optional[Browser] = None
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()
    
    async def initialize(self):
        """Initialize browser"""
        self.playwright = await async_playwright().start()
        
        # Use chromium with stealth settings
        self.browser = await self.playwright.chromium.launch(
            headless=self.headless,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox'
            ]
        )
        logger.info("Auto-apply bot initialized")
    
    async def close(self):
        """Close browser"""
        if self.browser:
            await self.browser.close()
        if hasattr(self, 'playwright'):
            await self.playwright.stop()
        logger.info("Auto-apply bot closed")
    
    async def random_delay(self, min_sec: float = 1.0, max_sec: float = 3.0):
        """Random human-like delay"""
        delay = random.uniform(min_sec, max_sec)
        await asyncio.sleep(delay)
    
    async def human_type(self, page: Page, selector: str, text: str):
        """Type text with human-like delays"""
        await page.fill(selector, "")
        for char in text:
            await page.type(selector, char, delay=random.uniform(50, 150))
    
    async def check_for_screening_questions(self, page: Page) -> bool:
        """Check if there are screening questions that need manual review"""
        # Common selectors for screening questions
        screening_selectors = [
            'input[type="radio"]',
            'input[type="checkbox"]:not([name*="terms"]):not([name*="agree"])',
            'textarea[required]',
            'select[required]'
        ]
        
        for selector in screening_selectors:
            elements = await page.query_selector_all(selector)
            if len(elements) > 2:  # More than basic fields
                logger.info("Screening questions detected")
                return True
        
        return False
    
    async def apply_linkedin(self, job: Job, proposal: str) -> Tuple[JobStatus, Optional[str]]:
        """
        Apply to LinkedIn job
        
        Returns:
            (status, error_message)
        """
        logger.info(f"Attempting to apply to LinkedIn job: {job.title}")
        
        try:
            context = await self.browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            )
            page = await context.new_page()
            
            # Navigate to job
            await page.goto(job.url, wait_until='domcontentloaded', timeout=30000)
            await self.random_delay(2, 4)
            
            # Look for Easy Apply button
            easy_apply_button = await page.query_selector('button.jobs-apply-button')
            
            if not easy_apply_button:
                logger.warning("No Easy Apply button found - might need manual application")
                await context.close()
                return JobStatus.MANUAL_REVIEW, "No Easy Apply button found"
            
            # Click Easy Apply
            await easy_apply_button.click()
            await self.random_delay(2, 3)
            
            # Check for screening questions
            if await self.check_for_screening_questions(page):
                await context.close()
                return JobStatus.MANUAL_REVIEW, "Has screening questions"
            
            # Fill in cover letter/message if available
            try:
                message_field = await page.wait_for_selector('textarea', timeout=5000)
                await self.human_type(page, 'textarea', proposal)
                await self.random_delay(1, 2)
            except PlaywrightTimeout:
                logger.info("No message field found")
            
            # Upload CV if there's a file input
            try:
                file_input = await page.query_selector('input[type="file"]')
                if file_input:
                    await file_input.set_input_files(str(self.cv_path))
                    logger.info("CV uploaded")
                    await self.random_delay(1, 2)
            except Exception as e:
                logger.warning(f"Could not upload CV: {e}")
            
            # Click Next/Submit buttons
            submit_button = await page.query_selector('button[aria-label*="Submit"]')
            if not submit_button:
                submit_button = await page.query_selector('button:has-text("Submit")')
            
            if not submit_button:
                logger.warning("Could not find submit button")
                await context.close()
                return JobStatus.MANUAL_REVIEW, "Could not find submit button"
            
            # Submit application
            await submit_button.click()
            await self.random_delay(2, 4)
            
            # Check for confirmation
            try:
                await page.wait_for_selector('text="Your application was sent"', timeout=5000)
                logger.info(f"Successfully applied to: {job.title}")
                await context.close()
                return JobStatus.APPLIED, None
            except PlaywrightTimeout:
                logger.warning("Could not confirm application submission")
                await context.close()
                return JobStatus.MANUAL_REVIEW, "Could not confirm submission"
            
        except Exception as e:
            logger.error(f"Error applying to LinkedIn job: {e}")
            return JobStatus.FAILED, str(e)
    
    async def apply_indeed(self, job: Job, proposal: str) -> Tuple[JobStatus, Optional[str]]:
        """
        Apply to Indeed job
        
        Returns:
            (status, error_message)
        """
        logger.info(f"Attempting to apply to Indeed job: {job.title}")
        
        try:
            context = await self.browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            )
            page = await context.new_page()
            
            # Navigate to job
            await page.goto(job.url, wait_until='domcontentloaded', timeout=30000)
            await self.random_delay(2, 4)
            
            # Look for Apply button
            apply_button = await page.query_selector('button[id*="apply"]')
            if not apply_button:
                apply_button = await page.query_selector('button:has-text("Apply")')
            
            if not apply_button:
                logger.warning("No Apply button found")
                await context.close()
                return JobStatus.MANUAL_REVIEW, "No Apply button found"
            
            # Click Apply
            await apply_button.click()
            await self.random_delay(2, 3)
            
            # Check for screening questions
            if await self.check_for_screening_questions(page):
                await context.close()
                return JobStatus.MANUAL_REVIEW, "Has screening questions"
            
            # Fill cover letter if available
            try:
                message_field = await page.wait_for_selector('textarea[id*="message"]', timeout=5000)
                await self.human_type(page, 'textarea[id*="message"]', proposal)
                await self.random_delay(1, 2)
            except PlaywrightTimeout:
                logger.info("No message field found")
            
            # Upload CV
            try:
                file_input = await page.query_selector('input[type="file"]')
                if file_input:
                    await file_input.set_input_files(str(self.cv_path))
                    logger.info("CV uploaded")
                    await self.random_delay(1, 2)
            except Exception as e:
                logger.warning(f"Could not upload CV: {e}")
            
            # Submit application
            submit_button = await page.query_selector('button[type="submit"]')
            if not submit_button:
                submit_button = await page.query_selector('button:has-text("Submit")')
            
            if not submit_button:
                logger.warning("Could not find submit button")
                await context.close()
                return JobStatus.MANUAL_REVIEW, "Could not find submit button"
            
            await submit_button.click()
            await self.random_delay(2, 4)
            
            # Check for confirmation
            try:
                confirmation = await page.wait_for_selector('text="Application submitted"', timeout=5000)
                if confirmation:
                    logger.info(f"Successfully applied to: {job.title}")
                    await context.close()
                    return JobStatus.APPLIED, None
            except PlaywrightTimeout:
                pass
            
            # Sometimes there's no clear confirmation
            logger.info(f"Application likely submitted to: {job.title}")
            await context.close()
            return JobStatus.APPLIED, None
            
        except Exception as e:
            logger.error(f"Error applying to Indeed job: {e}")
            return JobStatus.FAILED, str(e)
    
    async def apply_to_job(self, job: Job, proposal: str) -> Tuple[JobStatus, Optional[str]]:
        """
        Apply to job based on platform
        
        Args:
            job: Job to apply to
            proposal: Generated proposal text
            
        Returns:
            (status, error_message)
        """
        logger.info(f"Starting application to: {job.title} on {job.platform.value}")
        
        # Add random delay to avoid detection
        await self.random_delay(2, 6)
        
        if job.platform == Platform.LINKEDIN:
            return await self.apply_linkedin(job, proposal)
        elif job.platform == Platform.INDEED:
            return await self.apply_indeed(job, proposal)
        else:
            logger.warning(f"Unsupported platform: {job.platform}")
            return JobStatus.MANUAL_REVIEW, f"Platform {job.platform} not supported"


async def apply_to_job(job: Job, proposal: str, cv_path: str, 
                      headless: bool = True) -> Tuple[JobStatus, Optional[str]]:
    """
    Convenience function to apply to a job
    
    Usage:
        status, error = await apply_to_job(job, proposal, "path/to/cv.pdf")
    """
    async with AutoApplyBot(cv_path=cv_path, headless=headless) as bot:
        return await bot.apply_to_job(job, proposal)
