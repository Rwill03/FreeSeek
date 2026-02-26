"""
Job scraper module using Playwright
Scrapes LinkedIn, Indeed Belgium, and optionally Upwork
"""
import asyncio
import logging
import random
from typing import List, Optional
from playwright.async_api import async_playwright, Browser, Page, TimeoutError as PlaywrightTimeout

from app.models import Job, Platform, JobStatus

logger = logging.getLogger(__name__)


class JobScraper:
    """Scrapes freelance job listings from multiple platforms"""
    
    def __init__(self, headless: bool = True):
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
        logger.info("Browser initialized")
    
    async def close(self):
        """Close browser"""
        if self.browser:
            await self.browser.close()
        if hasattr(self, 'playwright'):
            await self.playwright.stop()
        logger.info("Browser closed")
    
    async def random_delay(self, min_sec: float = 1.0, max_sec: float = 3.0):
        """Random human-like delay"""
        delay = random.uniform(min_sec, max_sec)
        await asyncio.sleep(delay)
    
    async def human_type(self, page: Page, selector: str, text: str):
        """Type text with human-like delays"""
        await page.fill(selector, "")  # Clear first
        for char in text:
            await page.type(selector, char, delay=random.uniform(50, 150))
    
    async def scrape_linkedin(self, location: str = "Bruges", max_jobs: int = 10) -> List[Job]:
        """
        Scrape LinkedIn jobs
        
        Note: This requires manual login session or cookies
        For production, you'd need to implement session persistence
        """
        logger.info("Starting LinkedIn scrape")
        jobs = []
        context = None
        
        try:
            if not self.browser:
                logger.error("Browser not initialized")
                return jobs
                
            context = await self.browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            )
            page = await context.new_page()
            
            # Build search URL (contract jobs in Bruges)
            search_url = f"https://www.linkedin.com/jobs/search/?keywords=developer&location={location}&f_C=1%2C2%2C3&f_JT=C"
            
            logger.info(f"Navigating to LinkedIn: {search_url}")
            await page.goto(search_url, wait_until='domcontentloaded', timeout=30000)
            await self.random_delay(2, 4)
            
            # Wait for job listings
            try:
                await page.wait_for_selector('.jobs-search__results-list', timeout=10000)
            except PlaywrightTimeout:
                logger.warning("LinkedIn: Could not find job listings (might need login)")
                if context:
                    await context.close()
                return jobs
            
            # Get job cards
            job_cards = await page.query_selector_all('.job-search-card')
            logger.info(f"Found {len(job_cards)} LinkedIn job cards")
            
            for card in job_cards[:max_jobs]:
                try:
                    # Extract job data
                    title_elem = await card.query_selector('.base-search-card__title')
                    company_elem = await card.query_selector('.base-search-card__subtitle')
                    location_elem = await card.query_selector('.job-search-card__location')
                    link_elem = await card.query_selector('a')
                    
                    if not all([title_elem, company_elem, link_elem]):
                        continue
                    
                    title = (await title_elem.inner_text()).strip()
                    company = (await company_elem.inner_text()).strip()
                    location_text = (await location_elem.inner_text()).strip() if location_elem else location
                    url = await link_elem.get_attribute('href')
                    
                    # Clean URL
                    if '?' in url:
                        url = url.split('?')[0]
                    
                    # Get job description (requires clicking into job)
                    await card.click()
                    await self.random_delay(1, 2)
                    
                    description = ""
                    try:
                        desc_elem = await page.wait_for_selector('.show-more-less-html__markup', timeout=5000)
                        description = (await desc_elem.inner_text()).strip()
                    except PlaywrightTimeout:
                        logger.warning(f"Could not load description for: {title}")
                        description = title  # Fallback
                    
                    job = Job(
                        title=title,
                        company=company,
                        description=description,
                        url=url,
                        url_hash="",  # Will be set by database
                        location=location_text,
                        platform=Platform.LINKEDIN,
                        status=JobStatus.NEW
                    )
                    
                    jobs.append(job)
                    logger.info(f"Scraped LinkedIn job: {title}")
                    
                    await self.random_delay(1, 2)
                    
                except Exception as e:
                    logger.error(f"Error scraping LinkedIn job card: {e}")
                    continue
            
            if context:
                await context.close()
            
        except Exception as e:
            logger.error(f"LinkedIn scraping error: {e}", exc_info=True)
            if context:
                try:
                    await context.close()
                except:
                    pass
        
        logger.info(f"Scraped {len(jobs)} jobs from LinkedIn")
        return jobs
    
    async def scrape_indeed(self, location: str = "Bruges", max_jobs: int = 10) -> List[Job]:
        """Scrape Indeed Belgium jobs"""
        logger.info("Starting Indeed scrape")
        jobs = []
        context = None
        
        try:
            if not self.browser:
                logger.error("Browser not initialized")
                return jobs
                
            context = await self.browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            )
            page = await context.new_page()
            
            # Indeed Belgium URL
            search_url = f"https://be.indeed.com/jobs?q=developer+freelance&l={location}"
            
            logger.info(f"Navigating to Indeed: {search_url}")
            await page.goto(search_url, wait_until='domcontentloaded', timeout=30000)
            await self.random_delay(2, 4)
            
            # Wait for job listings
            try:
                await page.wait_for_selector('.job_seen_beacon', timeout=10000)
            except PlaywrightTimeout:
                logger.warning("Indeed: Could not find job listings")
                if context:
                    await context.close()
                return jobs
            
            # Get job cards
            job_cards = await page.query_selector_all('.job_seen_beacon')
            logger.info(f"Found {len(job_cards)} Indeed job cards")
            
            for card in job_cards[:max_jobs]:
                try:
                    # Extract job data
                    title_elem = await card.query_selector('h2.jobTitle')
                    company_elem = await card.query_selector('[data-testid="company-name"]')
                    location_elem = await card.query_selector('[data-testid="text-location"]')
                    link_elem = await card.query_selector('h2.jobTitle a')
                    
                    if not all([title_elem, company_elem, link_elem]):
                        continue
                    
                    title = (await title_elem.inner_text()).strip()
                    company = (await company_elem.inner_text()).strip()
                    location_text = (await location_elem.inner_text()).strip() if location_elem else location
                    href = await link_elem.get_attribute('href')
                    url = f"https://be.indeed.com{href}" if href.startswith('/') else href
                    
                    # Get snippet/description
                    description = title
                    snippet_elem = await card.query_selector('.job-snippet')
                    if snippet_elem:
                        description = (await snippet_elem.inner_text()).strip()
                    
                    job = Job(
                        title=title,
                        company=company,
                        description=description,
                        url=url,
                        url_hash="",
                        location=location_text,
                        platform=Platform.INDEED,
                        status=JobStatus.NEW
                    )
                    
                    jobs.append(job)
                    logger.info(f"Scraped Indeed job: {title}")
                    
                    await self.random_delay(0.5, 1.5)
                    
                except Exception as e:
                    logger.error(f"Error scraping Indeed job card: {e}")
                    continue
            
            if context:
                await context.close()
            
        except Exception as e:
            logger.error(f"Indeed scraping error: {e}", exc_info=True)
            if context:
                try:
                    await context.close()
                except:
                    pass
        
        logger.info(f"Scraped {len(jobs)} jobs from Indeed")
        return jobs
    
    async def scrape_upwork(self, max_jobs: int = 10) -> List[Job]:
        """
        Scrape Upwork jobs (optional)
        
        Note: Upwork has strong bot detection. This is a basic implementation.
        For production, consider using Upwork API or RSS feeds.
        """
        logger.info("Starting Upwork scrape")
        jobs = []
        context = None
        
        try:
            if not self.browser:
                logger.error("Browser not initialized")
                return jobs
                
            context = await self.browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            )
            page = await context.new_page()
            
            # Upwork search (public feed)
            search_url = "https://www.upwork.com/nx/search/jobs/?q=python%20developer&sort=recency"
            
            logger.info(f"Navigating to Upwork: {search_url}")
            await page.goto(search_url, wait_until='domcontentloaded', timeout=30000)
            await self.random_delay(3, 5)
            
            # Upwork often requires login - this is just a placeholder
            logger.warning("Upwork scraping is experimental and may require authentication")
            
            if context:
                await context.close()
            
        except Exception as e:
            logger.error(f"Upwork scraping error: {e}", exc_info=True)
            if context:
                try:
                    await context.close()
                except:
                    pass
        
        logger.info(f"Scraped {len(jobs)} jobs from Upwork")
        return jobs
    
    async def scrape_all(self, location: str = "Bruges", max_per_platform: int = 10) -> List[Job]:
        """
        Scrape all platforms
        
        Args:
            location: Target location
            max_per_platform: Max jobs to scrape per platform
            
        Returns:
            List of all scraped jobs
        """
        all_jobs = []
        
        # LinkedIn
        try:
            linkedin_jobs = await self.scrape_linkedin(location, max_per_platform)
            all_jobs.extend(linkedin_jobs)
        except Exception as e:
            logger.error(f"Failed to scrape LinkedIn: {e}")
        
        # Indeed
        try:
            indeed_jobs = await self.scrape_indeed(location, max_per_platform)
            all_jobs.extend(indeed_jobs)
        except Exception as e:
            logger.error(f"Failed to scrape Indeed: {e}")
        
        # Upwork (optional)
        # try:
        #     upwork_jobs = await self.scrape_upwork(max_per_platform)
        #     all_jobs.extend(upwork_jobs)
        # except Exception as e:
        #     logger.error(f"Failed to scrape Upwork: {e}")
        
        logger.info(f"Total jobs scraped: {len(all_jobs)}")
        return all_jobs


async def scrape_jobs(location: str = "Bruges", headless: bool = True) -> List[Job]:
    """
    Convenience function to scrape jobs
    
    Usage:
        jobs = await scrape_jobs(location="Bruges")
    """
    async with JobScraper(headless=headless) as scraper:
        jobs = await scraper.scrape_all(location=location)
        return jobs
