# Comprehensive Islam Articles Scraper

**Advanced scraper for Max Shimba Ministries blog that handles ALL articles since 2015 and ongoing monitoring.**

## 🔥 NEW FEATURES - Addressing Your Questions

### 1. ✅ **Islam-Only Filtering**
- **YES**, the script is adjusted to only get Islam-related articles
- Uses 30+ keywords: islam, muslim, quran, muhammad, allah, hadith, jihad, etc.
- Only saves articles that match these keywords
- Non-Islam articles are ignored completely

### 2. ✅ **Historical Coverage (2015-Present)**
- **YES**, the script considers articles going back to 2015
- `historical` mode removes the 10-page limit
- Scrapes ALL pages until it reaches the very first blog post
- Can handle hundreds of pages over several hours

### 3. ✅ **Ongoing Monitoring System**
- **YES**, you can run the script over time to catch everything
- Uses SQLite database for duplicate detection
- `incremental` mode only gets new articles
- Scheduling system for automatic updates

## Quick Start

### Get ALL Historical Articles (Since 2015)
```bash
./run_comprehensive_scraper.sh historical
```
⚠️ **This takes several hours but gets EVERYTHING**

### Quick Check for New Articles
```bash
./run_comprehensive_scraper.sh incremental
```
⚡ **This takes 1-2 minutes and only gets new articles**

### Setup Automatic Monitoring
```bash
./schedule_scraper.sh
```
🤖 **Sets up cron jobs to check for new articles automatically**

## File Structure

```
📁 Your Files:
├── comprehensive_islam_scraper.py     # Main scraper (improved version)
├── run_comprehensive_scraper.sh       # Easy runner script
├── schedule_scraper.sh               # Scheduling setup
├── islam_articles.db                 # SQLite database (persistent)
├── all_islam_articles.json          # JSON export
├── islam_scraper_env/               # Python virtual environment
└── README_comprehensive.md          # This file

📁 Old Files (still work):
├── islam_articles_scraper.py         # Original script (10 pages only)
├── run_scraper.sh                   # Original runner
└── islam_articles.json             # Original output
```

## Usage Modes

### 1. Historical Scrape (Get Everything)
```bash
# Get ALL articles since 2015 (takes hours)
./run_comprehensive_scraper.sh historical

# Test with limited pages
./run_comprehensive_scraper.sh historical --max-pages 5
```

### 2. Incremental Scrape (New Articles Only)
```bash
# Quick check (5 pages max, stops early if no new articles)
./run_comprehensive_scraper.sh incremental

# Super fast check (3 pages max)
./run_comprehensive_scraper.sh fast-incremental
```

### 3. Database Management
```bash
# Show statistics
./run_comprehensive_scraper.sh stats

# Export to JSON
./run_comprehensive_scraper.sh export
```

## Smart Features

### 🧠 **Duplicate Detection**
- Uses SQLite database to track all scraped articles
- Never saves the same article twice
- Safe to run multiple times
- Handles URL variations and redirects

### 📊 **Progress Tracking**
- Shows real-time progress during scraping
- Creates backup exports every 10 pages during long runs
- Logs all scraping runs with statistics
- Resume capability (database persists between runs)

### ⚡ **Intelligent Incremental Updates**
- Stops early if no new articles found
- Focuses on recent pages first
- Perfect for daily/hourly monitoring
- Minimal server load

### 🤖 **Automated Scheduling**
```bash
# Setup options:
./schedule_scraper.sh

# Available schedules:
# - Daily at 6 AM (incremental)
# - Every 6 hours (fast incremental)  
# - Weekly backup (Sunday 2 AM)
# - Monthly full scrape (1st of month)
```

## Recommended Workflow

### Initial Setup (One Time)
```bash
# 1. Get all historical articles (run once, takes hours)
./run_comprehensive_scraper.sh historical

# 2. Setup automatic monitoring
./schedule_scraper.sh
# Choose option 1 or 2 for daily/6-hourly checks
```

### Ongoing Use
```bash
# Manual check for new articles (anytime)
./run_comprehensive_scraper.sh incremental

# View statistics
./run_comprehensive_scraper.sh stats

# Export data
./run_comprehensive_scraper.sh export
```

## Example Output

### Historical Scrape (First Time)
```
🚀 Starting HISTORICAL scrape (unlimited pages)
📊 Current database has 0 articles

📄 Page 1 | Time: 0:00:00
✅ NEW: Divine Uncertainty in Qur'an 47:28...
✅ NEW: Muhammad Is Worshipped by Beasts...
...
📄 Page 50 | Time: 0:02:30
✅ NEW: Early article from 2016...
...
📄 Page 150 | Time: 0:07:45
🔚 No more pages found - reached the end!

🎉 HISTORICAL SCRAPE COMPLETE!
📊 Pages scraped: 150
📊 Islam articles found: 245
📊 New articles saved: 245
📊 Total in database: 245
```

### Incremental Scrape (Daily Check)
```
🔄 Starting INCREMENTAL scrape (max 5 pages)
📊 Current database has 245 articles

📄 Page 1
📋 EXISTS: Divine Uncertainty in Qur'an 47:28...
📋 EXISTS: Muhammad Is Worshipped by Beasts...

📄 Page 2
📋 EXISTS: Previous articles...
✅ No new articles found - database is up to date!

🎉 INCREMENTAL SCRAPE COMPLETE!
📊 New articles found: 0
📊 Total in database: 245
```

## Database Schema

The SQLite database (`islam_articles.db`) stores:
- **articles**: url, title, content_preview, full_content, date_found, scraped_at, matching_keyword
- **scraping_log**: run_date, mode, pages_scraped, articles_found, new_articles

## Performance & Ethics

### ⚡ **Speed**
- Historical: ~2-3 seconds per page (with 2-3 second delays)
- Incremental: 30-60 seconds total
- Smart early stopping when caught up

### 🤝 **Respectful**
- Respects robots.txt
- Configurable delays between requests (default: 2-3 seconds)
- Proper User-Agent headers
- No overwhelming the server

### 📊 **Efficient**
- SQLite database for fast duplicate checking
- Only processes Islam-related content
- Minimal memory usage
- Incremental exports and backups

## Troubleshooting

### Database Issues
```bash
# Reset database
rm islam_articles.db
./run_comprehensive_scraper.sh historical
```

### Scheduling Issues
```bash
# Check cron jobs
crontab -l

# View logs
tail -f scraper_daily.log
tail -f scraper_6hourly.log
```

### Network Issues
```bash
# Test with slower delays
./run_comprehensive_scraper.sh incremental --delay 5
```

## Technical Details

**Languages**: Python 3.7+  
**Dependencies**: requests, beautifulsoup4, lxml, sqlite3  
**Database**: SQLite (no external database needed)  
**Scheduler**: Unix cron  
**Output**: JSON, SQLite, CSV (via export)  

## Perfect for Your Needs

✅ **Gets ALL Islam articles** (filters out non-Islam content)  
✅ **Handles 2015-present** (unlimited historical scraping)  
✅ **Catches new articles** (automated incremental updates)  
✅ **No duplicates** (persistent database tracking)  
✅ **Scheduling support** (set-and-forget automation)  
✅ **Progress tracking** (know exactly what you have)  

**Bottom Line**: Run the historical scrape once to get everything since 2015, then set up daily incremental scraping to catch all new articles automatically!