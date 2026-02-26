# 🎯 Freelance Auto Hunter - Project Overview

## What is this?

An intelligent, automated system that:
1. **Searches** for freelance jobs on LinkedIn and Indeed
2. **Filters** jobs based on your location and skills
3. **Generates** personalized proposals using AI (Groq/HuggingFace)
4. **Applies** automatically using browser automation
5. **Tracks** everything in a database with a clean dashboard

## Technology Stack

### Backend (Python)
- **FastAPI**: Modern web framework
- **Playwright**: Browser automation (stealth mode)
- **SQLite**: Database (no setup required)
- **APScheduler**: Cron job scheduling
- **Groq/HuggingFace**: Free LLM APIs for proposals

### Frontend (React)
- **React**: UI framework
- **Vite**: Fast build tool
- **Tailwind CSS**: Styling
- **Axios**: API client

## Architecture

```
┌─────────────────┐
│   React         │  Dashboard UI
│   Frontend      │  (Port 5173)
└────────┬────────┘
         │ HTTP/REST
         ▼
┌─────────────────┐
│   FastAPI       │  API Server
│   Backend       │  (Port 8000)
└────────┬────────┘
         │
    ┌────┴────┬──────────┬──────────┐
    ▼         ▼          ▼          ▼
┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐
│Scraper │ │Filter  │ │  LLM   │ │ Apply  │
│Module  │ │Module  │ │Service │ │  Bot   │
└───┬────┘ └────────┘ └───┬────┘ └────────┘
    │                      │
    │  Playwright          │  Groq/HF API
    ▼                      ▼
┌────────┐            ┌─────────┐
│LinkedIn│            │   LLM   │
│Indeed  │            │ Provider│
└────────┘            └─────────┘
```

## Data Flow

1. **Scheduler** triggers every 3 hours (business hours only)
2. **Scraper** visits job sites with Playwright
3. **Filter** checks location and skills, scores jobs
4. **Database** stores new jobs (deduplicates)
5. **LLM Service** generates personalized proposals
6. **Apply Bot** visits job pages and submits applications
7. **Dashboard** displays stats and job status

## Key Features

### 🤖 Intelligent Automation
- Human-like delays and behavior
- Stealth mode to avoid detection
- Random delays between actions
- Session management

### 🎯 Smart Filtering
- Location-based (Bruges + radius)
- Skill keyword matching
- Match scoring (0-100)
- Configurable thresholds

### ✍️ AI Proposal Generation
- Uses free-tier LLM APIs
- 3 tone variants for variety
- Max 180 words (professional)
- Mentions specific job details
- Retry logic with backoff

### 🛡️ Safety First
- Daily application limits
- Duplicate prevention (URL hashing)
- Business hours only (8am-6pm)
- Weekend skip
- Comprehensive logging
- Manual review flags

### 📊 Dashboard
- Real-time statistics
- Job status tracking
- Proposal viewer
- Manual controls
- Auto-apply toggle

## File Structure

```
FreeSeek/
├── backend/
│   ├── app/
│   │   ├── main.py           # FastAPI app & API endpoints
│   │   ├── models.py         # Pydantic data models
│   │   ├── database.py       # SQLite operations
│   │   ├── scraper.py        # Playwright job scraping
│   │   ├── filter.py         # Job filtering logic
│   │   ├── llm_service.py    # LLM proposal generation
│   │   ├── apply_bot.py      # Auto-apply automation
│   │   └── scheduler.py      # APScheduler cron jobs
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   └── Dashboard.jsx # Main UI component
│   │   ├── App.jsx           # React app root
│   │   ├── main.jsx          # Entry point
│   │   ├── api.js            # API client
│   │   └── index.css         # Tailwind styles
│   ├── package.json
│   ├── vite.config.js
│   └── tailwind.config.js
│
├── .env                      # Your configuration
├── .env.example              # Configuration template
├── cv.pdf                    # Your resume
├── freelance_hunter.db       # SQLite database
├── freelance_hunter.log      # Application logs
│
├── setup.sh / setup.bat      # Setup scripts
├── run-backend.sh / .bat     # Backend launcher
├── run-frontend.sh / .bat    # Frontend launcher
│
├── README.md                 # Full documentation
├── QUICKSTART.md             # Quick reference
├── CV_README.md              # CV instructions
└── PROJECT_OVERVIEW.md       # This file
```

## Configuration

### Required (.env)
```bash
LLM_API_KEY=your_key_here        # Get from Groq/HuggingFace
CV_FILE_PATH=./cv.pdf            # Path to your CV
```

### Optional (.env)
```bash
TARGET_LOCATION=Bruges           # Search location
LOCATION_RADIUS=30               # Search radius (km)
MAX_APPLICATIONS_PER_DAY=10      # Safety limit
ENABLE_AUTO_APPLY=false          # Start disabled!
LLM_PROVIDER=groq                # groq or huggingface
```

## Getting Started

### Quick Setup (5 minutes)
```bash
# 1. Run setup
./setup.sh  # or setup.bat on Windows

# 2. Configure
# Edit .env with your API key

# 3. Add CV
cp ~/path/to/cv.pdf ./cv.pdf

# 4. Start servers (2 terminals)
./run-backend.sh
./run-frontend.sh

# 5. Open browser
# http://localhost:5173
```

### First Run
1. Keep `ENABLE_AUTO_APPLY=false`
2. Click "Run Job Scan Now"
3. Review found jobs
4. Click "Generate" to test proposals
5. Check proposal quality
6. Manually apply to test
7. Only then enable auto-apply

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/stats` | GET | Dashboard statistics |
| `/api/jobs` | GET | List all jobs |
| `/api/jobs/{id}` | GET | Get specific job |
| `/api/jobs/{id}/proposal` | GET | Get job proposal |
| `/api/scan` | POST | Trigger job scan |
| `/api/generate-proposal` | POST | Generate proposal |
| `/api/toggle-auto-apply` | POST | Toggle automation |
| `/api/scheduler/status` | GET | Scheduler status |

## Database Schema

### jobs
- id, title, company, description, budget, url, url_hash
- location, platform, status, match_score
- created_at, applied_at

### proposals
- id, job_id, content, generated_at

### applications
- id, job_id, proposal_id, status, error_message, applied_at

## Workflow States

```
NEW → FILTERED (doesn't match)
NEW → PROPOSAL_GENERATED → APPLIED (success!)
NEW → PROPOSAL_GENERATED → MANUAL_REVIEW (screening questions)
NEW → PROPOSAL_GENERATED → FAILED (error)
```

## Scheduling

- **Frequency**: Every 3 hours
- **Hours**: 8:00 AM - 6:00 PM
- **Days**: Monday - Friday only
- **Limit**: Max N applications per day (configurable)
- **Delays**: 2-6 minutes between applications

## Safety Mechanisms

1. **Rate Limiting**: Max applications per day
2. **Duplicate Detection**: URL hashing
3. **Business Hours**: No weekend/night runs
4. **Manual Review**: Flags complex applications
5. **Error Handling**: Comprehensive try-catch
6. **Logging**: Everything logged to file
7. **Retry Logic**: 3 attempts with backoff

## Customization

### Change Skill Keywords
Edit `backend/app/main.py` around line 80

### Change Your Profile
Edit `MY_PROFILE` in `backend/app/llm_service.py`

### Add New Platform
1. Add scraper method in `scraper.py`
2. Add apply method in `apply_bot.py`
3. Add to `Platform` enum in `models.py`

## Troubleshooting

### Common Issues
1. **No jobs found**: Website changes, need login, or location issue
2. **LLM errors**: Invalid API key or rate limit
3. **Apply fails**: Site structure changed or captcha
4. **Database locked**: Close other connections

### Solutions
- Check logs: `tail -f freelance_hunter.log`
- Verify .env configuration
- Test scraper manually
- Start with lower limits
- Use headless=False for debugging

## Best Practices

1. ✅ Start with auto-apply OFF
2. ✅ Review proposals before enabling
3. ✅ Use low daily limits initially
4. ✅ Monitor logs daily
5. ✅ Keep CV updated
6. ✅ Respect platform ToS
7. ✅ Update profile to be accurate
8. ✅ Test thoroughly first

## Performance

- **Scraping**: ~30 seconds per platform
- **Filtering**: Instant
- **Proposal Gen**: 2-5 seconds per job
- **Applying**: 30-60 seconds per job
- **Full Cycle**: ~10-15 minutes for 10 jobs

## Security Notes

- Never commit .env file
- Don't share API keys
- Keep database private
- Review auto-apply behavior
- Start conservative

## Future Enhancements

- Email notifications
- More job platforms
- Advanced analytics
- Browser session persistence
- Success rate optimization
- A/B testing proposals
- Mobile app

## Support

1. Read README.md
2. Check QUICKSTART.md
3. Review logs
4. Test with simpler config
5. Verify API keys

## License

Personal use only. Respect job platform Terms of Service.

---

**Built for**: Automated freelance job hunting in Bruges, Belgium
**Goal**: Save time, increase applications, land more clients
**Status**: Production-ready ✅

Happy Job Hunting! 🚀
