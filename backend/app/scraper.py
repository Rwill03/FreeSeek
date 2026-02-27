"""
Job scraper module using Playwright
Scrapes LinkedIn, Indeed Belgium, and optionally Upwork
"""
import asyncio
import logging
import random
import json
from typing import List, Optional
from playwright.async_api import async_playwright, Browser, Page, TimeoutError as PlaywrightTimeout
import requests
from bs4 import BeautifulSoup
import feedparser

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
        logger.info("Starting browser initialization...")
        self.playwright = await async_playwright().start()
        logger.info("Playwright started")
        
        # Use chromium with stealth settings
        try:
            self.browser = await self.playwright.chromium.launch(
                headless=self.headless,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--no-sandbox'
                ],
                timeout=30000
            )
            logger.info("Browser launched successfully")
        except Exception as e:
            logger.error(f"Failed to launch browser: {e}")
            raise
    
    async def close(self):
        """Close browser"""
        try:
            if self.browser:
                try:
                    await self.browser.close()
                except Exception as e:
                    logger.warning(f"Error closing browser: {e}")
            if hasattr(self, 'playwright'):
                try:
                    await self.playwright.stop()
                except Exception as e:
                    logger.warning(f"Error stopping playwright: {e}")
            logger.info("Browser closed")
        except Exception as e:
            logger.error(f"Error in close(): {e}")
    
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
        
        Note: LinkedIn requires authentication. This method is disabled.
        Use Indeed instead which is publicly accessible.
        """
        logger.info("LinkedIn scraping is disabled (requires authentication)")
        return []
    
    async def scrape_indeed(self, location: str = "Bruges", max_jobs: int = 10) -> List[Job]:
        """Scrape Indeed Belgium jobs"""
        logger.info("Starting Indeed scrape")
        jobs = []
        context = None
        page = None
        
        try:
            if not self.browser:
                logger.error("Browser not initialized")
                return jobs
            
            logger.info("Creating new context...")
            context = await self.browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )
            logger.info("Context created successfully")
            
            page = await context.new_page()
            logger.info("Page created successfully")
            
            # Indeed Belgium URL
            search_url = f"https://be.indeed.com/jobs?q=developer&l={location}"
            
            logger.info(f"Navigating to Indeed: {search_url}")
            try:
                await page.goto(search_url, wait_until='domcontentloaded', timeout=30000)
                logger.info("Navigation successful")
            except Exception as e:
                logger.error(f"Navigation failed: {e}")
                return jobs
            
            # Wait for job listings to appear after page load
            await asyncio.sleep(2)
            logger.info("Page loaded, waiting for job listings...")
            
            # Try to wait for job elements to be visible (don't evaluate JS)
            try:
                await page.wait_for_selector('[data-automation="SerpJob"]', timeout=5000)
                logger.info("Job listings appeared")
            except Exception as e:
                logger.debug(f"Timeout waiting for job selector: {e}")
            
            # Extract jobs using Playwright's built-in methods (no JavaScript evaluation)
            try:
                logger.info("Extracting jobs using Playwright selectors...")
                
                # Query selectors directly without page.evaluate()
                job_locators = await page.query_selector_all('[data-automation="SerpJob"]')
                logger.info(f"Found {len(job_locators)} job elements")
                
                for idx, job_el in enumerate(job_locators[:max_jobs]):
                    try:
                        # Extract title using inner text
                        title_el = await job_el.query_selector('h2 a, a[data-jk]')
                        title = await title_el.inner_text() if title_el else None
                        
                        # Extract link
                        href = await title_el.get_attribute('href') if title_el else None
                        if href:
                            # Convert relative URLs to absolute
                            if not href.startswith('http'):
                                href = f"https://be.indeed.com{href}"
                        
                        # Extract company name
                        company_el = await job_el.query_selector('[data-testid="company-name"], .company_location_text span:first-child')
                        company = await company_el.inner_text() if company_el else "Unknown"
                        
                        if title and href:
                            title = title.strip()[:100]
                            company = company.strip()[:50]
                            
                            job = Job(
                                title=title,
                                company=company,
                                description=title,
                                url=href,
                                url_hash="",
                                location=location,
                                platform=Platform.INDEED,
                                status=JobStatus.NEW
                            )
                            
                            jobs.append(job)
                            logger.info(f"Extracted Indeed job {idx+1}: {title}")
                        else:
                            logger.debug(f"Skipping job {idx} - missing title or link")
                    
                    except Exception as e:
                        logger.debug(f"Error extracting job {idx}: {e}")
                        continue
                
                logger.info(f"Successfully extracted {len(jobs)} jobs from Indeed")
                return jobs
                    
            except Exception as e:
                logger.error(f"Selector extraction error: {e}")
                return jobs
            
        except Exception as e:
            logger.error(f"Indeed scraping error: {e}")
        finally:
            # Always close context if it exists
            if context:
                try:
                    await context.close()
                    logger.info("Context closed")
                except Exception as e:
                    logger.warning(f"Error closing Indeed context: {e}")
        
        logger.info(f"Scraped {len(jobs)} jobs from Indeed using Playwright")
        return jobs
    
    def scrape_indeed_http(self, location: str = "Bruges", max_jobs: int = 10) -> List[Job]:
        """
        Scrape Indeed Belgium jobs using HTTP requests (fallback if Playwright fails)
        More resilient to bot detection than Playwright
        """
        logger.info("Starting Indeed HTTP scrape (fallback method)")
        jobs = []
        
        try:
            # Build search URL
            search_url = f"https://be.indeed.com/jobs?q=developer&l={location}"
            logger.info(f"Fetching Indeed page: {search_url}")
            
            # Use comprehensive headers to mimic real browser more convincingly
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9,nl;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'Cache-Control': 'max-age=0',
            }
            
            # Create session for connection pooling and cookie handling
            session = requests.Session()
            session.headers.update(headers)
            
            # Add random delay to appear human
            import time
            time.sleep(random.uniform(2, 4))
            
            # Fetch the page with timeout and allow redirects
            response = session.get(search_url, timeout=20, allow_redirects=True)
            
            logger.info(f"Got response status: {response.status_code}")
            
            if response.status_code == 200:
                # Parse HTML
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find job cards (Indeed Belgium uses these selectors)
                job_cards = soup.find_all('div', {'class': 'job_seen_beacon'})
                if not job_cards:
                    # Try alternative selectors
                    job_cards = soup.find_all('td', {'class': 'resultContent'})
                if not job_cards:
                    job_cards = soup.find_all('div', {'data-jk': True})
                
                logger.info(f"Found {len(job_cards)} job cards in HTML")
                
                for idx, card in enumerate(job_cards[:max_jobs]):
                    try:
                        # Extract title (try multiple selectors)
                        title_el = card.find('h2', {'class': 'jobTitle'}) or card.find('h2') or card.find('a', {'data-jk': True})
                        if title_el:
                            # Get text from the element, handling nested spans
                            title = title_el.get_text(strip=True)
                        else:
                            title = None
                        
                        # Extract link
                        link_el = card.find('a', {'class': 'jcs-JobTitle'}) or card.find('a', href=True)
                        href = link_el.get('href') if link_el else None
                        if href and not href.startswith('http'):
                            # Handle relative URLs
                            if href.startswith('/'):
                                href = f"https://be.indeed.com{href}"
                            else:
                                href = f"https://be.indeed.com/{href}"
                        
                        # Extract company
                        company_el = card.find('span', {'class': 'companyName'}) or card.find('span', {'data-testid': 'company-name'})
                        if not company_el:
                            company_el = card.find('div', {'class': 'company_location_text'})
                            if company_el:
                                company_el = company_el.find('span')
                        
                        company = company_el.get_text(strip=True) if company_el else "Unknown"
                        
                        if title and href:
                            title = title[:100]
                            company = company[:50]
                            
                            job = Job(
                                title=title,
                                company=company,
                                description=title,
                                url=href,
                                url_hash="",
                                location=location,
                                platform=Platform.INDEED,
                                status=JobStatus.NEW
                            )
                            
                            jobs.append(job)
                            logger.info(f"Extracted Indeed HTTP job {idx+1}: {title} at {company}")
                        else:
                            logger.debug(f"Skipping job {idx} - missing title or link (title={bool(title)}, href={bool(href)})")
                    
                    except Exception as e:
                        logger.debug(f"Error extracting job {idx}: {e}")
                        continue
            else:
                logger.warning(f"Got non-200 status: {response.status_code}")
                if response.status_code == 403:
                    logger.warning("Indeed is blocking our requests (403 Forbidden). Consider using RSS feeds or API alternatives.")
            
        except requests.RequestException as e:
            logger.error(f"HTTP request error: {e}")
        except Exception as e:
            logger.error(f"Indeed HTTP scrape error: {e}")
        
        logger.info(f"Scraped {len(jobs)} jobs from Indeed using HTTP")
        return jobs
    
    def scrape_indeed_rss(self, location: str = "Bruges", max_jobs: int = 10) -> List[Job]:
        """
        Scrape Indeed Belgium jobs using RSS feed
        RSS feeds are typically more permissive than web scraping
        """
        logger.info("Starting Indeed RSS scrape")
        jobs = []
        
        try:
            # Build RSS feed URL for Indeed Belgium
            # Format: https://be.indeed.com/rss?q=developer&l=Bruges
            rss_url = f"https://be.indeed.com/rss?q=developer&l={location}"
            logger.info(f"Fetching Indeed RSS feed: {rss_url}")
            
            # Add headers for the RSS request
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            }
            
            # Fetch the RSS feed
            response = requests.get(rss_url, headers=headers, timeout=15)
            response.raise_for_status()
            
            logger.info(f"Got RSS response status: {response.status_code}")
            
            if response.status_code == 200:
                # Parse RSS feed
                feed = feedparser.parse(response.content)
                
                logger.info(f"Found {len(feed.entries)} jobs in RSS feed")
                
                for idx, entry in enumerate(feed.entries[:max_jobs]):
                    try:
                        # Extract job details from RSS entry
                        title = entry.get('title', '').strip()
                        link = entry.get('link', '')
                        
                        # Company name is often in the description or summary
                        summary = entry.get('summary', '') or entry.get('description', '')
                        
                        # Try to extract company from summary (Indeed RSS often has format "Company - Location")
                        company = "Unknown"
                        if summary:
                            # Parse summary to find company
                            soup = BeautifulSoup(summary, 'html.parser')
                            text = soup.get_text()
                            if ' - ' in text:
                                parts = text.split(' - ')
                                if len(parts) >= 2:
                                    company = parts[0].strip()[:50]
                        
                        if title and link:
                            title = title[:100]
                            
                            job = Job(
                                title=title,
                                company=company,
                                description=summary[:200] if summary else title,
                                url=link,
                                url_hash="",
                                location=location,
                                platform=Platform.INDEED,
                                status=JobStatus.NEW
                            )
                            
                            jobs.append(job)
                            logger.info(f"Extracted Indeed RSS job {idx+1}: {title} at {company}")
                        else:
                            logger.debug(f"Skipping RSS entry {idx} - missing title or link")
                    
                    except Exception as e:
                        logger.debug(f"Error extracting RSS entry {idx}: {e}")
                        continue
            else:
                logger.warning(f"RSS request failed with status: {response.status_code}")
        
        except requests.RequestException as e:
            logger.error(f"RSS request error: {e}")
        except Exception as e:
            logger.error(f"Indeed RSS scrape error: {e}")
        
        logger.info(f"Scraped {len(jobs)} jobs from Indeed using RSS")
        return jobs
    
    def scrape_test_jobs(self, max_jobs: int = 5) -> List[Job]:
        """
        Generate test jobs for development/testing
        Use this when real scraping is blocked
        """
        logger.info(f"Generating {max_jobs} test jobs")
        jobs = []
        
        test_data = [
            ("Senior Full Stack Developer", "TechCorp", "https://example.com/jobs/1"),
            ("Python Backend Developer", "DataSolutions", "https://example.com/jobs/2"),
            ("React Frontend Developer", "WebAgency", "https://example.com/jobs/3"),
            ("DevOps Engineer", "CloudServices", "https://example.com/jobs/4"),
            ("Mobile App Developer", "AppStudio", "https://example.com/jobs/5"),
            ("AI/ML Engineer", "AILabs", "https://example.com/jobs/6"),
            ("Software Architect", "EnterpriseInc", "https://example.com/jobs/7"),
            ("QA Automation Engineer", "TestTech", "https://example.com/jobs/8"),
        ]
        
        for idx in range(min(max_jobs, len(test_data))):
            title, company, url = test_data[idx]
            job = Job(
                title=title,
                company=company,
                description=f"{title} position at {company}. Great opportunity for experienced developers.",
                url=f"{url}?test={random.randint(1000,9999)}",  # Add random param to ensure unique URLs
                url_hash="",
                location="Bruges",
                platform=Platform.INDEED,
                status=JobStatus.NEW
            )
            jobs.append(job)
            logger.info(f"Generated test job {idx+1}: {title} at {company}")
        
        logger.info(f"Generated {len(jobs)} test jobs")
        return jobs
    
    def scrape_remoteok(self, max_jobs: int = 10) -> List[Job]:
        """
        Scrape RemoteOK - Popular remote job board with RSS feed
        URL: https://remoteok.com/remote-dev-jobs
        """
        logger.info("Starting RemoteOK scrape")
        jobs = []
        
        try:
            # RemoteOK has a public RSS feed
            rss_url = "https://remoteok.com/remote-dev-jobs.rss"
            logger.info(f"Fetching RemoteOK RSS: {rss_url}")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            }
            
            response = requests.get(rss_url, headers=headers, timeout=15)
            response.raise_for_status()
            
            logger.info(f"Got RemoteOK response: {response.status_code}")
            
            if response.status_code == 200:
                feed = feedparser.parse(response.content)
                logger.info(f"Found {len(feed.entries)} jobs in RemoteOK RSS")
                
                for idx, entry in enumerate(feed.entries[:max_jobs]):
                    try:
                        title = entry.get('title', '').strip()
                        link = entry.get('link', '')
                        summary = entry.get('summary', '') or entry.get('description', '')
                        
                        # Extract company from title (RemoteOK format: "Position at Company")
                        company = "RemoteOK"
                        if ' at ' in title:
                            parts = title.split(' at ')
                            if len(parts) >= 2:
                                company = parts[1].strip()[:50]
                        
                        if title and link:
                            job = Job(
                                title=title[:100],
                                company=company,
                                description=summary[:200] if summary else title,
                                url=link,
                                url_hash="",
                                location="Remote",
                                platform=Platform.REMOTEOK,
                                status=JobStatus.NEW
                            )
                            jobs.append(job)
                            logger.info(f"Extracted RemoteOK job {idx+1}: {title}")
                    
                    except Exception as e:
                        logger.debug(f"Error extracting RemoteOK job {idx}: {e}")
                        continue
        
        except Exception as e:
            logger.error(f"RemoteOK scrape error: {e}")
        
        logger.info(f"Scraped {len(jobs)} jobs from RemoteOK")
        return jobs
    
    def scrape_weworkremotely(self, max_jobs: int = 10) -> List[Job]:
        """
        Scrape We Work Remotely - Remote job board with RSS
        URL: https://weworkremotely.com/
        """
        logger.info("Starting We Work Remotely scrape")
        jobs = []
        
        try:
            # We Work Remotely RSS feed for programming jobs
            rss_url = "https://weworkremotely.com/categories/remote-programming-jobs.rss"
            logger.info(f"Fetching We Work Remotely RSS: {rss_url}")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            }
            
            response = requests.get(rss_url, headers=headers, timeout=15)
            response.raise_for_status()
            
            logger.info(f"Got We Work Remotely response: {response.status_code}")
            
            if response.status_code == 200:
                feed = feedparser.parse(response.content)
                logger.info(f"Found {len(feed.entries)} jobs in We Work Remotely RSS")
                
                for idx, entry in enumerate(feed.entries[:max_jobs]):
                    try:
                        title = entry.get('title', '').strip()
                        link = entry.get('link', '')
                        summary = entry.get('summary', '') or entry.get('description', '')
                        
                        # Extract company from summary
                        company = "We Work Remotely"
                        if summary:
                            soup = BeautifulSoup(summary, 'html.parser')
                            text = soup.get_text()
                            # WWR format often has company in first line
                            lines = [l.strip() for l in text.split('\n') if l.strip()]
                            if len(lines) > 1:
                                company = lines[0][:50]
                        
                        if title and link:
                            job = Job(
                                title=title[:100],
                                company=company,
                                description=summary[:200] if summary else title,
                                url=link,
                                url_hash="",
                                location="Remote",
                                platform=Platform.WEWORKREMOTELY,
                                status=JobStatus.NEW
                            )
                            jobs.append(job)
                            logger.info(f"Extracted We Work Remotely job {idx+1}: {title}")
                    
                    except Exception as e:
                        logger.debug(f"Error extracting We Work Remotely job {idx}: {e}")
                        continue
        
        except Exception as e:
            logger.error(f"We Work Remotely scrape error: {e}")
        
        logger.info(f"Scraped {len(jobs)} jobs from We Work Remotely")
        return jobs
    
    def scrape_remotive(self, max_jobs: int = 10) -> List[Job]:
        """
        Scrape Remotive - Remote jobs with RSS feed
        URL: https://remotive.com/
        """
        logger.info("Starting Remotive scrape")
        jobs = []
        
        try:
            # Remotive RSS feed
            rss_url = "https://remotive.com/api/remote-jobs/feed"
            logger.info(f"Fetching Remotive RSS: {rss_url}")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            }
            
            response = requests.get(rss_url, headers=headers, timeout=15)
            response.raise_for_status()
            
            logger.info(f"Got Remotive response: {response.status_code}")
            
            if response.status_code == 200:
                feed = feedparser.parse(response.content)
                logger.info(f"Found {len(feed.entries)} jobs in Remotive RSS")
                
                for idx, entry in enumerate(feed.entries[:max_jobs]):
                    try:
                        title = entry.get('title', '').strip()
                        link = entry.get('link', '')
                        summary = entry.get('summary', '') or entry.get('description', '')
                        
                        # Extract company
                        company = "Remotive"
                        if summary:
                            soup = BeautifulSoup(summary, 'html.parser')
                            # Try to find company in summary
                            company_tag = soup.find('strong')
                            if company_tag:
                                company = company_tag.get_text(strip=True)[:50]
                        
                        if title and link:
                            job = Job(
                                title=title[:100],
                                company=company,
                                description=summary[:200] if summary else title,
                                url=link,
                                url_hash="",
                                location="Remote",
                                platform=Platform.REMOTIVE,
                                status=JobStatus.NEW
                            )
                            jobs.append(job)
                            logger.info(f"Extracted Remotive job {idx+1}: {title}")
                    
                    except Exception as e:
                        logger.debug(f"Error extracting Remotive job {idx}: {e}")
                        continue
        
        except Exception as e:
            logger.error(f"Remotive scrape error: {e}")
        
        logger.info(f"Scraped {len(jobs)} jobs from Remotive")
        return jobs
    
    def scrape_freelancer(self, max_jobs: int = 10) -> List[Job]:
        """
        Scrape Freelancer.com jobs via RSS
        URL: https://www.freelancer.com/
        """
        logger.info("Starting Freelancer.com scrape")
        jobs = []
        
        try:
            # Freelancer.com RSS for software development projects
            rss_url = "https://www.freelancer.com/rss.xml?category=56&country=BE"
            logger.info(f"Fetching Freelancer.com RSS: {rss_url}")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            }
            
            response = requests.get(rss_url, headers=headers, timeout=15)
            response.raise_for_status()
            
            logger.info(f"Got Freelancer.com response: {response.status_code}")
            
            if response.status_code == 200:
                feed = feedparser.parse(response.content)
                logger.info(f"Found {len(feed.entries)} jobs in Freelancer.com RSS")
                
                for idx, entry in enumerate(feed.entries[:max_jobs]):
                    try:
                        title = entry.get('title', '').strip()
                        link = entry.get('link', '')
                        summary = entry.get('summary', '') or entry.get('description', '')
                        
                        if title and link:
                            job = Job(
                                title=title[:100],
                                company="Freelancer.com",
                                description=summary[:200] if summary else title,
                                url=link,
                                url_hash="",
                                location="Belgium",
                                platform=Platform.FREELANCER,
                                status=JobStatus.NEW
                            )
                            jobs.append(job)
                            logger.info(f"Extracted Freelancer.com job {idx+1}: {title}")
                    
                    except Exception as e:
                        logger.debug(f"Error extracting Freelancer.com job {idx}: {e}")
                        continue
        
        except Exception as e:
            logger.error(f"Freelancer.com scrape error: {e}")
        
        logger.info(f"Scraped {len(jobs)} jobs from Freelancer.com")
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
        
        # RemoteOK - Remote developer jobs (RSS available)
        try:
            logger.info("Scraping RemoteOK...")
            remoteok_jobs = self.scrape_remoteok(max_per_platform)
            all_jobs.extend(remoteok_jobs)
            logger.info(f"RemoteOK: Found {len(remoteok_jobs)} jobs")
        except Exception as e:
            logger.error(f"Failed to scrape RemoteOK: {e}")
        
        # We Work Remotely - Remote programming jobs (RSS available)
        try:
            logger.info("Scraping We Work Remotely...")
            wwremotely_jobs = self.scrape_weworkremotely(max_per_platform)
            all_jobs.extend(wwremotely_jobs)
            logger.info(f"We Work Remotely: Found {len(wwremotely_jobs)} jobs")
        except Exception as e:
            logger.error(f"Failed to scrape We Work Remotely: {e}")
        
        # Remotive - Remote jobs (RSS available)
        try:
            logger.info("Scraping Remotive...")
            remotive_jobs = self.scrape_remotive(max_per_platform)
            all_jobs.extend(remotive_jobs)
            logger.info(f"Remotive: Found {len(remotive_jobs)} jobs")
        except Exception as e:
            logger.error(f"Failed to scrape Remotive: {e}")
        
        # Freelancer.com - Freelance projects (RSS available)
        try:
            logger.info("Scraping Freelancer.com...")
            freelancer_jobs = self.scrape_freelancer(max_per_platform)
            all_jobs.extend(freelancer_jobs)
            logger.info(f"Freelancer.com: Found {len(freelancer_jobs)} jobs")
        except Exception as e:
            logger.error(f"Failed to scrape Freelancer.com: {e}")
        
        # LinkedIn (disabled - requires authentication)
        try:
            linkedin_jobs = await self.scrape_linkedin(location, max_per_platform)
            all_jobs.extend(linkedin_jobs)
        except Exception as e:
            logger.error(f"Failed to scrape LinkedIn: {e}")
        
        # Indeed - try RSS first (most reliable), then HTTP, then Playwright
        try:
            logger.info("Scraping Indeed Belgium...")
            indeed_jobs = self.scrape_indeed_rss(location, max_per_platform)
            if len(indeed_jobs) == 0:
                logger.info("Indeed RSS returned 0 jobs, trying HTTP...")
                indeed_jobs = self.scrape_indeed_http(location, max_per_platform)
            if len(indeed_jobs) == 0:
                logger.info("Indeed HTTP returned 0 jobs, trying Playwright...")
                indeed_jobs = await self.scrape_indeed(location, max_per_platform)
            logger.info(f"Indeed Belgium: Found {len(indeed_jobs)} jobs")
            all_jobs.extend(indeed_jobs)
        except Exception as e:
            logger.error(f"Failed to scrape Indeed: {e}")
        
        # If no jobs found from any platform, use test mode
        if len(all_jobs) == 0:
            logger.warning("No jobs found from any platform. Using test mode to generate sample jobs.")
            logger.warning("NOTE: Most platforms have anti-bot protection or require APIs.")
            logger.warning("RSS feeds from RemoteOK, We Work Remotely, and Remotive should work.")
            test_jobs = self.scrape_test_jobs(max_per_platform)
            all_jobs.extend(test_jobs)
        
        logger.info(f"=" * 70)
        logger.info(f"Total jobs scraped from all platforms: {len(all_jobs)}")
        logger.info(f"=" * 70)
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
