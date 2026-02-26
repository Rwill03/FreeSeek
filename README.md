# Freelance Auto Hunter

A production-ready web application that automatically searches for freelance jobs, filters them based on your skills, generates tailored proposals using AI, and can automatically apply to jobs using browser automation.

## 🎯 Features

- **Multi-Platform Scraping**: Searches LinkedIn and Indeed Belgium for freelance jobs
- **Smart Filtering**: Filters jobs by location and skill match (AI, Python, React, etc.)
- **AI Proposal Generation**: Uses Groq or HuggingFace LLM to generate personalized proposals
- **Auto-Apply**: Automatically applies to jobs using Playwright browser automation
- **Scheduling**: Runs every 3 hours during business hours (8am-6pm, weekdays)
- **Dashboard**: Clean React interface to monitor and control the system
- **Safety Features**: Daily application limits, duplicate detection, error handling

## 📂 Project Structure

```
FreeSeek/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI application
│   │   ├── models.py            # Data models
│   │   ├── database.py          # SQLite database manager
│   │   ├── scraper.py           # Job scraping with Playwright
│   │   ├── filter.py            # Job filtering logic
│   │   ├── llm_service.py       # LLM proposal generation
│   │   ├── apply_bot.py         # Auto-apply automation
│   │   └── scheduler.py         # APScheduler jobs
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   └── Dashboard.jsx    # Main dashboard UI
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   ├── api.js               # API client
│   │   └── index.css
│   ├── package.json
│   ├── vite.config.js
│   └── tailwind.config.js
├── .env.example
├── .env                         # Your config (create from .env.example)
├── cv.pdf                       # Your CV/resume
└── README.md
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- npm or yarn

### 1. Clone and Setup

```bash
cd FreeSeek
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium

# Copy and configure environment variables
cp ../.env.example ../.env
# Edit .env with your settings (see Configuration section)
```

### 3. Frontend Setup

```bash
cd ../frontend

# Install dependencies
npm install
```

### 4. Add Your CV

Place your CV/resume as a PDF file in the project root:

```bash
# From project root
cp /path/to/your/cv.pdf ./cv.pdf
```

### 5. Configuration

Edit `.env` file in the project root:

```bash
# Get a free Groq API key from: https://console.groq.com
LLM_API_KEY=your_groq_api_key_here

# Set your target location
TARGET_LOCATION=Bruges

# Configure auto-apply (start with false to test)
ENABLE_AUTO_APPLY=false

# Set path to your CV
CV_FILE_PATH=./cv.pdf
```

### 6. Run the Application

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate
python -m app.main
# Or: uvicorn app.main:app --reload
```

Backend will be available at: http://localhost:8000

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

Frontend will be available at: http://localhost:5173

## 📋 Configuration Guide

### Getting LLM API Keys

#### Option 1: Groq (Recommended)
1. Visit https://console.groq.com
2. Sign up for free account
3. Generate API key
4. Free tier includes generous limits

#### Option 2: HuggingFace
1. Visit https://huggingface.co
2. Sign up and go to Settings > Access Tokens
3. Create new token
4. Set `LLM_PROVIDER=huggingface` in .env

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `LLM_PROVIDER` | LLM provider (groq or huggingface) | groq |
| `LLM_API_KEY` | Your LLM API key | Required |
| `TARGET_LOCATION` | Job search location | Bruges |
| `LOCATION_RADIUS` | Search radius in km | 30 |
| `MAX_APPLICATIONS_PER_DAY` | Daily application limit | 10 |
| `ENABLE_AUTO_APPLY` | Enable auto-apply (true/false) | false |
| `CV_FILE_PATH` | Path to your CV PDF | ./cv.pdf |

## 🎮 Using the Dashboard

### Control Panel

1. **Run Job Scan Now**: Manually trigger a job search
2. **Refresh Data**: Update the dashboard with latest data
3. **Auto-Apply Toggle**: Enable/disable automatic job applications

### Jobs Table

- **View Job**: Opens job listing in new tab
- **View Proposal**: See generated proposal for applied jobs
- **Generate**: Create proposal for new jobs

### Status Indicators

- 🟢 **New**: Job found and filtered
- 🔵 **Proposal Generated**: AI proposal created
- ✅ **Applied**: Successfully applied
- 🟠 **Manual Review**: Needs manual attention
- 🔴 **Failed**: Application failed
- ⚫ **Filtered**: Didn't meet criteria

## 🤖 How It Works

### 1. Job Scraping
- Uses Playwright with stealth mode
- Scrapes LinkedIn and Indeed Belgium every 3 hours
- Random delays to avoid detection
- Extracts: title, company, description, location, URL

### 2. Filtering
- Checks location (Bruges + 30km radius)
- Matches against skill keywords
- Calculates match score (0-100)
- Filters out low-scoring jobs (<30)

### 3. Proposal Generation
- Uses LLM (Groq/HuggingFace) to generate proposals
- Max 180 words
- Mentions specific job details
- Confident, professional tone
- 3 tone variants for variety
- Retry logic with exponential backoff

### 4. Auto-Apply
- Opens job page with Playwright
- Fills application form
- Uploads CV
- Pastes proposal
- Submits application
- Captures confirmation
- 2-6 minute delay between applications

### 5. Scheduling
- Runs every 3 hours
- Only during 8am-6pm
- Skips weekends
- Respects daily limits

## 🛡️ Safety Features

- **Duplicate Detection**: URL hashing prevents duplicate applications
- **Daily Limits**: Configurable max applications per day
- **Business Hours**: Only applies during work hours
- **Manual Review**: Flags jobs with screening questions
- **Error Handling**: Comprehensive logging and retry logic
- **Rate Limiting**: Random delays between actions

## 📊 Database

SQLite database (`freelance_hunter.db`) stores:
- Jobs with status tracking
- Generated proposals
- Application history
- Success/failure tracking

## 🔧 Advanced Usage

### Manual Job Scan

```python
# From backend directory
python -c "import asyncio; from app.scraper import scrape_jobs; asyncio.run(scrape_jobs())"
```

### Generate Proposal Only

```python
from app.llm_service import LLMService

llm = LLMService(api_key="your_key", provider="groq")
proposal = llm.generate_proposal(job_description, job_title)
```

### Custom Filtering

Edit `backend/app/filter.py` to adjust:
- Location matching logic
- Skill keywords
- Scoring algorithm

## 🐛 Troubleshooting

### "No Apply button found"
- Website structure may have changed
- Job might require login
- Status set to "Manual Review"

### LLM Errors
- Check API key is valid
- Verify API provider is correct
- Check internet connection
- Review logs in `freelance_hunter.log`

### Playwright Errors
- Run: `playwright install chromium`
- Some sites require manual login first
- Check headless mode settings

### Database Locked
- Close other connections to database
- Restart the backend server

## 📝 Extending

### Add New Job Platform

1. Create scraper method in `backend/app/scraper.py`
2. Add platform to `Platform` enum in `models.py`
3. Add apply method in `apply_bot.py`

### Custom LLM Provider

1. Add provider logic to `llm_service.py`
2. Update `.env.example` with new provider option

### Email Notifications

Add to `scheduler.py`:
```python
import smtplib
# Send email when high-scoring job found
if job.match_score >= 80:
    send_email_notification(job)
```

## ⚠️ Legal & Ethical Considerations

- **Terms of Service**: Respect platform ToS
- **Rate Limiting**: Built-in delays to avoid being blocked
- **Authenticity**: Proposals are AI-assisted but should represent you accurately
- **Responsibility**: Review applications before enabling auto-apply
- **LinkedIn**: Use at your own risk; LinkedIn actively detects automation

## 🔐 Security

- Never commit `.env` file
- Keep API keys secure
- Don't share database file
- Review generated proposals
- Start with `ENABLE_AUTO_APPLY=false` to test

## 📈 Future Enhancements (Optional)

- [ ] Email notifications for high-match jobs
- [ ] Job scoring visualization
- [ ] Review-before-apply mode
- [ ] Support for more platforms (Upwork, Freelancer.com)
- [ ] Browser session persistence
- [ ] Export application history
- [ ] Success analytics dashboard

## 📄 License

This project is for personal use. Respect job platforms' Terms of Service.

## 🤝 Support

For issues or questions:
1. Check logs: `freelance_hunter.log`
2. Review environment variables
3. Test with `ENABLE_AUTO_APPLY=false` first
4. Verify API keys are valid

## 🎉 Tips for Success

1. **Start Conservative**: Begin with auto-apply disabled
2. **Review Proposals**: Check generated proposals are high quality
3. **Adjust Filters**: Fine-tune location and skill keywords
4. **Monitor Daily**: Check dashboard regularly
5. **Update Profile**: Edit your profile in `llm_service.py` to be accurate
6. **Good CV**: Ensure your CV is up-to-date
7. **Test First**: Run manual scans before enabling scheduling

---

**Happy Job Hunting! 🚀**
