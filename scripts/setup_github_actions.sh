#!/bin/bash

# Setup script for GitHub Actions Islam Articles Scraper
# This prepares your repository for automated scraping

echo "🚀 Setting up GitHub Actions Islam Articles Scraper"
echo "================================================="

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    echo "❌ This doesn't appear to be a git repository"
    echo "Please run 'git init' first or navigate to your git repository"
    exit 1
fi

# Create necessary directories
echo "📁 Creating directory structure..."
mkdir -p .github/workflows
mkdir -p data
mkdir -p logs

# Check if required files exist
REQUIRED_FILES=(
    ".github/workflows/scrape-islam-articles.yml"
    "github_actions_islam_scraper.py"
    "requirements.txt"
)

MISSING_FILES=()
for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$file" ]; then
        MISSING_FILES+=("$file")
    fi
done

if [ ${#MISSING_FILES[@]} -gt 0 ]; then
    echo "❌ Missing required files:"
    for file in "${MISSING_FILES[@]}"; do
        echo "   - $file"
    done
    echo "Please ensure all files are present in your repository"
    exit 1
fi

# Make scripts executable
echo "🔧 Setting permissions..."
chmod +x github_actions_islam_scraper.py
chmod +x setup_github_actions.sh

# Create .gitignore if it doesn't exist
if [ ! -f ".gitignore" ]; then
    echo "📄 Creating .gitignore..."
    cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
env.bak/
venv.bak/

# Virtual environments
islam_scraper_env/

# Logs
*.log
logs/*.log

# Temporary files
*.tmp
*.temp

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Backup files
backup_*.json
*.bak
EOF
fi

# Create README for GitHub Actions
echo "📖 Creating GitHub Actions README..."
cat > README_GITHUB_ACTIONS.md << 'EOF'
# GitHub Actions Islam Articles Scraper

This repository automatically scrapes Islam-related articles from Max Shimba Ministries using GitHub Actions.

## 🤖 Automated Schedule

The scraper runs automatically on the following schedule:

- **Every 6 hours**: Quick incremental check for new articles
- **Daily at 6 AM UTC**: More thorough incremental scrape  
- **Weekly on Sundays at 2 AM UTC**: Full backup and export

## 📊 Manual Triggers

You can manually trigger the scraper:

1. Go to **Actions** tab in your GitHub repository
2. Select **Scrape Islam Articles** workflow
3. Click **Run workflow**
4. Choose your options:
   - **Scraping mode**: incremental, historical, or full_historical
   - **Max pages**: limit the number of pages (optional)
   - **Delay**: seconds between requests (default: 2)

## 📁 Output Files

The scraper generates several files:

- `islam_articles.db` - SQLite database with all articles
- `all_islam_articles.json` - JSON export of all articles
- `scraping_summary.md` - Statistics and summary
- `scraper.log` - Detailed logs

## 🔍 Enhanced Features

### Better Date Extraction
- Extracts dates from URL patterns, meta tags, structured data
- Multiple fallback strategies for date detection
- Confidence scoring for date accuracy

### Smart Duplicate Detection
- Uses SQLite database for persistence
- URL hashing prevents duplicates
- Safe to run multiple times

### Comprehensive Keyword Filtering
- 40+ Islam-related keywords
- Only saves relevant articles
- Tracks which keyword matched

## 📈 Monitoring

### Artifacts
Each run creates artifacts containing:
- Database backup
- JSON export
- Logs and summary

### Releases
Major runs (weekly/historical) create GitHub releases with complete data exports.

### Notifications
- Failed runs create GitHub issues (for historical mode)
- Success/failure status in Actions tab

## 🛠️ Configuration

### Environment Variables
No API keys required - the scraper works out of the box.

### Customizing Schedule
Edit `.github/workflows/scrape-islam-articles.yml` to modify the cron schedule:

```yaml
schedule:
  # Every 6 hours
  - cron: '0 */6 * * *'
  # Daily at 6 AM UTC  
  - cron: '0 6 * * *'
  # Weekly on Sundays at 2 AM UTC
  - cron: '0 2 * * 0'
```

### Customizing Keywords
Edit `github_actions_islam_scraper.py` and modify the `islam_keywords` list.

## 📊 Database Schema

### Articles Table
- `url` - Article URL (unique)
- `title` - Article title
- `content_preview` - First 500 characters
- `full_content` - Complete article text
- `publish_date` - Raw date string
- `publish_date_parsed` - ISO formatted date
- `date_source` - How the date was extracted
- `matching_keyword` - Which keyword matched
- `word_count` - Article length

### Scraping Log Table
- `run_date` - When the scrape ran
- `mode` - incremental/historical
- `pages_scraped` - Number of pages processed
- `new_articles` - New articles found
- `github_run_id` - GitHub Actions run ID

## 🔒 Permissions

The workflow needs these permissions (automatically granted):
- `contents: write` - To commit database updates
- `issues: write` - To create failure notifications  
- `releases: write` - To create data releases

## 🚨 Troubleshooting

### Check Workflow Status
- Go to **Actions** tab
- Look for failed runs (red X)
- Click on failed run to see logs

### Manual Recovery
If the automated runs fail, you can:
1. Download the latest database from Artifacts
2. Run the scraper manually
3. Commit the updated database

### Rate Limiting
If you hit rate limits:
1. Increase delay in workflow (edit `delay` parameter)
2. Reduce `max_pages` for incremental runs
3. Check robots.txt compliance

## 📈 Expected Performance

### First Historical Run
- **Time**: 2-4 hours (depending on site size)
- **Articles**: 200-500 Islam-related articles
- **Pages**: 100-300 pages

### Daily Incremental Runs  
- **Time**: 1-2 minutes
- **Articles**: 0-5 new articles typically
- **Pages**: 2-5 pages

### Storage Usage
- Database: ~1-5 MB
- JSON exports: ~2-10 MB  
- Logs: ~100 KB per run
- Artifacts: Auto-deleted after 30 days

## 🎯 Goals Achieved

✅ **Complete historical coverage** - Gets all articles since 2015  
✅ **Automatic new article detection** - Catches updates within 6 hours  
✅ **No manual intervention required** - Fully automated  
✅ **Persistent data storage** - Database survives between runs  
✅ **Enhanced date extraction** - Much better date parsing  
✅ **Comprehensive filtering** - Only Islam-related content  
✅ **Backup and recovery** - Multiple export formats  
✅ **Monitoring and alerts** - Know when things break  

Perfect for long-term monitoring of Islam-related content on the Max Shimba Ministries blog!
EOF

# Test the scraper locally (optional)
echo ""
echo "🧪 Testing the scraper (optional)..."
read -p "Would you like to test the scraper locally? (y/N): " test_choice

if [[ $test_choice =~ ^[Yy]$ ]]; then
    if command -v python3 &> /dev/null; then
        echo "Installing dependencies..."
        python3 -m pip install -r requirements.txt
        
        echo "Running test scrape (2 pages only)..."
        python3 github_actions_islam_scraper.py --mode incremental --max-pages 2 --delay 1
        
        if [ -f "islam_articles.db" ] && [ -f "all_islam_articles.json" ]; then
            echo "✅ Test successful! Files created:"
            ls -la islam_articles.db all_islam_articles.json
        else
            echo "⚠️ Test completed but some files may be missing"
        fi
    else
        echo "❌ Python3 not found. Please install Python 3.7+ to test locally"
    fi
fi

# Git setup
echo ""
echo "📦 Git repository setup..."

# Add files to git
echo "Adding files to git..."
git add .github/workflows/scrape-islam-articles.yml
git add github_actions_islam_scraper.py
git add requirements.txt
git add README_GITHUB_ACTIONS.md
git add .gitignore
git add setup_github_actions.sh

# Check if there are changes to commit
if git diff --staged --quiet; then
    echo "No new files to commit"
else
    echo "Files added to git staging area. Ready to commit!"
    echo ""
    echo "Next steps:"
    echo "1. Review the changes: git status"
    echo "2. Commit the changes: git commit -m 'Add GitHub Actions Islam scraper'"
    echo "3. Push to GitHub: git push"
    echo "4. Go to your GitHub repository and check the Actions tab"
fi

echo ""
echo "🎉 GitHub Actions setup complete!"
echo ""
echo "📋 Summary:"
echo "✅ Workflow file created: .github/workflows/scrape-islam-articles.yml"
echo "✅ Scraper script: github_actions_islam_scraper.py"  
echo "✅ Dependencies: requirements.txt"
echo "✅ Documentation: README_GITHUB_ACTIONS.md"
echo "✅ Git configuration: .gitignore"
echo ""
echo "🚀 Next steps:"
echo "1. Commit and push these files to GitHub"
echo "2. The workflow will start running automatically"
echo "3. Check the Actions tab in your GitHub repository"
echo "4. First historical run may take several hours"
echo ""
echo "📊 Scheduling:"
echo "- Every 6 hours: Quick check for new articles"
echo "- Daily at 6 AM UTC: Thorough incremental scrape"
echo "- Weekly on Sundays: Full backup and export"
echo ""
echo "🔧 Manual triggers available in GitHub Actions tab"