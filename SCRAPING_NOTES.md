# Job Scraping Implementation Notes

## Current Status

The FreeSeek application attempts to scrape job listings from Indeed Belgium using multiple approaches. Due to Indeed's strong anti-bot protection, **all direct scraping methods are currently blocked**.

## Attempted Methods

### 1. **Playwright Browser Automation** ❌
- **Status**: Blocked
- **Error**: `Target page, context or browser has been closed`
- **Cause**: Indeed detects Playwright and closes the browser during JavaScript execution
- **Attempts**: 
  - Using stealth mode with `--disable-blink-features=AutomationControlled`
  - Direct selector queries (avoiding `page.evaluate()`)
  - Various timeout configurations
- **Result**: Browser consistently closed by Indeed's anti-bot system

### 2. **HTTP Requests with BeautifulSoup** ❌
- **Status**: Blocked
- **Error**: `403 Forbidden`
- **Cause**: Indeed blocks direct HTTP requests even with realistic headers
- **Attempts**:
  - Comprehensive browser-like headers
  - Session management with cookies
  - Random delays to mimic human behavior
  - Multiple User-Agent strings
- **Result**: Consistently receives 403 status code

### 3. **RSS Feed Scraping** ❌
- **Status**: Not Available
- **Error**: `404 Not Found`
- **Cause**: Indeed Belgium does not provide public RSS feeds
- **URL Tested**: `https://be.indeed.com/rss?q=developer&l=Bruges`
- **Result**: RSS endpoint does not exist

## Current Solution: Test Mode

To allow development and testing of the rest of the application (filtering, database, UI, etc.), the scraper now includes a **test mode** that generates sample jobs when all scraping methods fail.

### Test Jobs Generated:
1. Senior Full Stack Developer @ TechCorp
2. Python Backend Developer @ DataSolutions
3. React Frontend Developer @ WebAgency
4. DevOps Engineer @ CloudServices
5. Mobile App Developer @ AppStudio
6. AI/ML Engineer @ AILabs
7. Software Architect @ EnterpriseInc
8. QA Automation Engineer @ TestTech

These test jobs allow you to:
- ✅ See the "Scanning..." animation
- ✅ Test the job filtering logic
- ✅ Verify database storage
- ✅ Test the UI dashboard
- ✅ Develop LLM integration features
- ✅ Test proposal generation

## Recommended Solutions for Production

### Option 1: Official Indeed API (Best)
- **Pros**: Legal, reliable, no blocking
- **Cons**: Requires Indeed partner agreement
- **Link**: https://www.indeed.com/intl/en/hire/c/info/getting-started-indeed-api

### Option 2: Alternative Job Boards with APIs
Consider these alternatives that provide official APIs:

1. **Adzuna API** (Recommended)
   - **Features**: Free tier available, covers Belgium
   - **Link**: https://developer.adzuna.com/
   - **Coverage**: 20+ countries including Belgium

2. **Remotive API**
   - **Features**: Remote-focused jobs, free access
   - **Link**: https://remotive.com/api
   - **Best for**: Remote developer positions

3. **The Muse API**
   - **Features**: Tech jobs, well-documented
   - **Link**: https://www.themuse.com/developers/api/v2

4. **GitHub Jobs API** (Archived but alternatives exist)
   - **Alternative**: GraphQL Jobs API
   - **Link**: https://api.graphql.jobs/

### Option 3: RSS Feeds from Other Job Sites
Some job boards still provide RSS feeds:
- **Stack Overflow Jobs**: Has RSS feeds
- **AngelList**: Provides RSS for startups
- **RemoteOK**: RSS feeds available

### Option 4: Paid Scraping Services
- **ScraperAPI**: Handles anti-bot protection
- **Bright Data**: Professional web scraping
- **Apify**: Pre-built job scraping actors

## Technical Details

### Fallback Chain
The scraper tries methods in this order:
1. RSS Feed (fastest, least likely to be blocked)
2. HTTP with BeautifulSoup (moderate approach)
3. Playwright Browser (slowest, most resource-intensive)
4. Test Mode (generates sample data)

### Code Location
- Main scraper: `backend/app/scraper.py`
- Methods:
  - `scrape_indeed_rss()` - RSS feed approach
  - `scrape_indeed_http()` - HTTP requests
  - `scrape_indeed()` - Playwright browser
  - `scrape_test_jobs()` - Test data generator

## For Developers

### Enabling Real Scraping
If you have access to an API or alternative source:

1. **Create a new scraper method in `scraper.py`:**
```python
def scrape_from_api(self, location: str, max_jobs: int) -> List[Job]:
    # Your API integration here
    pass
```

2. **Update `scrape_all()` method:**
```python
# Try your API first
api_jobs = self.scrape_from_api(location, max_per_platform)
if len(api_jobs) > 0:
    all_jobs.extend(api_jobs)
else:
    # Fall back to existing methods
    ...
```

### Disabling Test Mode
To disable test mode (will return 0 jobs if scraping fails):

In `scraper.py`, remove or comment out:
```python
if len(indeed_jobs) == 0:
    indeed_jobs = self.scrape_test_jobs(max_per_platform)
```

## Logs

The scraper logs show the progression:
```
INFO - Starting Indeed RSS scrape
ERROR - RSS request error: 404 Client Error
INFO - RSS scrape returned 0 jobs, trying HTTP...
INFO - Starting Indeed HTTP scrape (fallback method)
ERROR - HTTP request error: 403 Client Error
INFO - HTTP scrape returned 0 jobs, trying Playwright as last resort...
WARNING - All scraping methods failed. Using test mode to generate sample jobs.
```

## Conclusion

While direct scraping of Indeed is currently blocked, the application architecture is sound and can easily be adapted to use:
- Official APIs from job boards
- Alternative job sources
- Paid scraping services

The test mode ensures the rest of the application (UI, filtering, database, LLM integration) can be developed and tested without being blocked by scraping limitations.
