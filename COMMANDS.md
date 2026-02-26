# Freelance Auto Hunter - Command Cheat Sheet

## 🚀 Setup & Installation

```bash
# Initial setup (run once)
./setup.sh                    # macOS/Linux
setup.bat                     # Windows

# Make scripts executable (macOS/Linux only)
chmod +x setup.sh run-*.sh
```

## ▶️ Running the Application

### Start Backend (Terminal 1)
```bash
cd backend
source venv/bin/activate      # macOS/Linux
venv\Scripts\activate         # Windows
python -m app.main

# Or use quick script
./run-backend.sh              # macOS/Linux
run-backend.bat               # Windows
```

### Start Frontend (Terminal 2)
```bash
cd frontend
npm run dev

# Or use quick script
./run-frontend.sh             # macOS/Linux
run-frontend.bat              # Windows
```

### Access Points
- Dashboard: http://localhost:5173
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## 🔧 Configuration

```bash
# Edit configuration
nano .env                     # macOS/Linux
notepad .env                  # Windows

# Copy example config
cp .env.example .env          # macOS/Linux
copy .env.example .env        # Windows

# Add your CV
cp ~/Documents/cv.pdf ./cv.pdf
```

## 📊 Database & Logs

```bash
# View logs (real-time)
tail -f freelance_hunter.log  # macOS/Linux
type freelance_hunter.log     # Windows

# Search logs for errors
grep ERROR freelance_hunter.log
findstr ERROR freelance_hunter.log  # Windows

# Reset database (deletes all data!)
rm freelance_hunter.db
del freelance_hunter.db       # Windows

# Backup database
cp freelance_hunter.db backup_$(date +%Y%m%d).db
```

## 🧪 Testing & Development

```bash
# Test scraper only
cd backend
source venv/bin/activate
python -c "import asyncio; from app.scraper import scrape_jobs; asyncio.run(scrape_jobs('Bruges'))"

# Test LLM service
python -c "from app.llm_service import LLMService; llm = LLMService('your_key'); print(llm.generate_proposal('Python developer needed', 'Python Dev'))"

# Run backend with reload
cd backend
uvicorn app.main:app --reload

# Build frontend for production
cd frontend
npm run build
```

## 🔄 Updates & Maintenance

```bash
# Update Python packages
cd backend
source venv/bin/activate
pip install -r requirements.txt --upgrade

# Update Node packages
cd frontend
npm update

# Reinstall Playwright browsers
cd backend
playwright install chromium

# Clean install (if broken)
cd backend
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cd frontend
rm -rf node_modules package-lock.json
npm install
```

## 📈 Monitoring

```bash
# Check Python version
python3 --version

# Check Node version
node --version

# Check installed Python packages
cd backend && pip list

# Check installed Node packages
cd frontend && npm list --depth=0

# Check disk space
df -h .                       # macOS/Linux
dir                           # Windows

# Check running processes
ps aux | grep python          # macOS/Linux
ps aux | grep node

# Check ports in use
lsof -i :8000                 # macOS/Linux (backend)
lsof -i :5173                 # macOS/Linux (frontend)
netstat -ano | findstr :8000  # Windows
```

## 🐛 Debugging

```bash
# Run backend in non-headless mode (see browser)
# Edit backend/app/scraper.py: headless=False

# Check API health
curl http://localhost:8000
curl http://localhost:8000/api/stats

# Test database connection
cd backend
source venv/bin/activate
python -c "from app.database import Database; db = Database(); print('OK')"

# View database content (SQLite)
sqlite3 freelance_hunter.db "SELECT * FROM jobs LIMIT 5;"
sqlite3 freelance_hunter.db ".tables"
sqlite3 freelance_hunter.db ".schema jobs"

# Check file permissions
ls -la                        # macOS/Linux
dir                           # Windows
```

## 🧹 Cleanup

```bash
# Remove all generated files
rm -rf backend/venv backend/__pycache__ backend/app/__pycache__
rm -rf frontend/node_modules frontend/dist
rm freelance_hunter.db freelance_hunter.log
rm .env

# Start fresh
./setup.sh
```

## 📦 Git Commands

```bash
# Initialize git (if not done)
git init
git add .
git commit -m "Initial commit"

# Important: Don't commit secrets!
# Make sure .gitignore includes:
# .env
# *.db
# *.log
# venv/
# node_modules/

# Check what will be committed
git status

# Create .gitignore from template
cat > .gitignore << 'EOF'
.env
*.db
*.log
venv/
node_modules/
__pycache__/
dist/
EOF
```

## 🔑 API Key Management

```bash
# Get Groq API key
# Visit: https://console.groq.com
# Sign up → API Keys → Create

# Test API key
curl https://api.groq.com/openai/v1/models \
  -H "Authorization: Bearer YOUR_API_KEY"

# Set in .env
echo "LLM_API_KEY=your_key_here" >> .env
```

## 📱 Quick Actions

```bash
# One-liner: Fresh start
./setup.sh && cp ~/Documents/cv.pdf ./cv.pdf && nano .env

# One-liner: Start everything
./run-backend.sh & ./run-frontend.sh

# One-liner: View live logs
tail -f freelance_hunter.log | grep -i "error\|success\|applied"

# One-liner: Check today's stats
sqlite3 freelance_hunter.db "SELECT status, COUNT(*) FROM jobs WHERE DATE(created_at) = DATE('now') GROUP BY status;"
```

## 🎯 Common Workflows

### First Time Setup
```bash
1. ./setup.sh
2. cp ~/cv.pdf ./cv.pdf
3. nano .env  # Add API key
4. ./run-backend.sh  # Terminal 1
5. ./run-frontend.sh # Terminal 2
6. Open http://localhost:5173
```

### Daily Check
```bash
1. tail -f freelance_hunter.log
2. Open http://localhost:5173
3. Check stats
4. Review manual_review jobs
```

### Troubleshooting
```bash
1. tail -f freelance_hunter.log | grep ERROR
2. Check .env file
3. Verify API key
4. Test scraper manually
5. Check Python/Node versions
```

### Updating Profile
```bash
1. nano backend/app/llm_service.py
2. Edit MY_PROFILE section
3. Restart backend
4. Test proposal generation
```

## 💾 Backup

```bash
# Backup everything important
tar -czf backup_$(date +%Y%m%d).tar.gz \
  .env \
  cv.pdf \
  freelance_hunter.db \
  backend/app/*.py

# Restore from backup
tar -xzf backup_YYYYMMDD.tar.gz
```

## 🚦 Status Checks

```bash
# Is backend running?
curl -s http://localhost:8000 && echo "✅ Backend OK" || echo "❌ Backend Down"

# Is frontend running?
curl -s http://localhost:5173 && echo "✅ Frontend OK" || echo "❌ Frontend Down"

# Check all systems
curl -s http://localhost:8000/api/stats | python3 -m json.tool
```

## 📞 Emergency Commands

```bash
# Kill all Python processes (危险!)
killall python3               # macOS/Linux
taskkill /F /IM python.exe    # Windows

# Kill all Node processes (危险!)
killall node                  # macOS/Linux
taskkill /F /IM node.exe      # Windows

# Kill specific port
kill $(lsof -t -i:8000)       # macOS/Linux
```

---

**Tip**: Bookmark this file for quick reference! 🔖
