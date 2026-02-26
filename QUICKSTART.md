# Freelance Auto Hunter - Quick Reference

## 🚀 Quick Start Commands

### First Time Setup
```bash
# macOS/Linux
chmod +x setup.sh
./setup.sh

# Windows
setup.bat
```

### Running the Application

**Backend (Terminal 1):**
```bash
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate
python -m app.main
```

**Frontend (Terminal 2):**
```bash
cd frontend
npm run dev
```

Or use quick start scripts:
```bash
# macOS/Linux
./run-backend.sh   # Terminal 1
./run-frontend.sh  # Terminal 2

# Windows
run-backend.bat    # Terminal 1
run-frontend.bat   # Terminal 2
```

## 🔑 Essential Configuration

### .env File
```bash
LLM_API_KEY=your_groq_api_key_here
TARGET_LOCATION=Bruges
ENABLE_AUTO_APPLY=false  # Start with false!
CV_FILE_PATH=./cv.pdf
```

### Get Free LLM API Key
- Groq: https://console.groq.com
- HuggingFace: https://huggingface.co/settings/tokens

## 📊 Dashboard Features

### Control Panel
- **Run Job Scan Now**: Manual job search trigger
- **Auto-Apply Toggle**: Enable/disable automation
- **Refresh Data**: Update dashboard

### Job Statuses
- 🟢 **New**: Ready for review
- 🔵 **Proposal Generated**: AI proposal created
- ✅ **Applied**: Successfully submitted
- 🟠 **Manual Review**: Needs attention
- 🔴 **Failed**: Application error

## 🎯 Recommended Workflow

### Phase 1: Testing (Days 1-3)
```bash
# .env settings
ENABLE_AUTO_APPLY=false
MAX_APPLICATIONS_PER_DAY=5
```
1. Run manual scans
2. Review generated proposals
3. Manually apply to jobs

### Phase 2: Semi-Auto (Days 4-7)
```bash
# .env settings
ENABLE_AUTO_APPLY=true
MAX_APPLICATIONS_PER_DAY=5
```
1. Monitor applications daily
2. Check proposal quality
3. Review manual_review jobs

### Phase 3: Full Auto (Week 2+)
```bash
# .env settings
ENABLE_AUTO_APPLY=true
MAX_APPLICATIONS_PER_DAY=10
```
1. Let it run automatically
2. Check dashboard daily
3. Handle manual reviews

## 🛠️ Troubleshooting

### Backend won't start
```bash
# Check Python version
python3 --version  # Should be 3.11+

# Reinstall dependencies
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

### Frontend won't start
```bash
# Check Node version
node --version  # Should be 18+

# Reinstall dependencies
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### No jobs found
- Check internet connection
- Verify target location
- Some sites may require manual login
- Check logs: `backend/freelance_hunter.log`

### LLM errors
- Verify API key in .env
- Check API provider setting
- Test API key: https://console.groq.com

### Playwright errors
```bash
# Reinstall browsers
cd backend
source venv/bin/activate
playwright install chromium
```

## 📁 Important Files

| File | Purpose |
|------|---------|
| `.env` | Configuration (API keys, settings) |
| `cv.pdf` | Your resume/CV |
| `freelance_hunter.db` | Database (auto-created) |
| `freelance_hunter.log` | Application logs |
| `backend/app/main.py` | Backend entry point |
| `frontend/src/App.jsx` | Frontend entry point |

## 🔐 Security Checklist

- [ ] Never commit .env file
- [ ] Keep API keys private
- [ ] Don't share database file
- [ ] Test with auto-apply OFF first
- [ ] Review proposals before enabling auto-apply
- [ ] Start with low daily limits

## 📈 Monitoring

### Check Logs
```bash
# Real-time logs
tail -f freelance_hunter.log

# Search for errors
grep ERROR freelance_hunter.log
```

### Database Stats
```bash
# View database
cd backend
source venv/bin/activate
python -c "from app.database import Database; db = Database(); print(db.get_dashboard_stats())"
```

### API Endpoints
- Dashboard: http://localhost:5173
- API Docs: http://localhost:8000/docs
- API Stats: http://localhost:8000/api/stats
- API Jobs: http://localhost:8000/api/jobs

## 🎨 Customization

### Adjust Skill Keywords
Edit `backend/app/main.py`:
```python
skill_keywords = [
    "ai", "python", "fastapi", "react",
    "your", "custom", "keywords"
]
```

### Change Proposal Profile
Edit `backend/app/llm_service.py`:
```python
MY_PROFILE = """
Your custom profile here
"""
```

### Modify Filters
Edit `backend/app/filter.py` for custom filtering logic

## 💡 Tips for Success

1. **Start Conservative**: Begin with manual review
2. **Good CV**: Use a well-formatted PDF
3. **Accurate Profile**: Update your skills in llm_service.py
4. **Monitor Daily**: Check dashboard and logs
5. **Adjust Keywords**: Fine-tune based on results
6. **Respect Limits**: Don't spam applications
7. **Quality Over Quantity**: Focus on relevant jobs

## 🆘 Getting Help

1. Check this guide
2. Read README.md
3. Check logs: `freelance_hunter.log`
4. Test with simpler settings
5. Verify environment variables

## 📞 Useful Commands

```bash
# View logs
tail -f freelance_hunter.log

# Reset database
rm freelance_hunter.db

# Update dependencies
cd backend && pip install -r requirements.txt --upgrade
cd frontend && npm update

# Check Python packages
pip list

# Check Node packages
npm list

# Test scraper only
cd backend
source venv/bin/activate
python -c "import asyncio; from app.scraper import scrape_jobs; asyncio.run(scrape_jobs('Bruges'))"
```

---

**Remember**: Always test thoroughly before enabling auto-apply!
