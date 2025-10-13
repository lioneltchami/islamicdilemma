#!/bin/bash

# Comprehensive Islam Articles Scraper Runner
# Handles different scraping modes and scheduling

echo "🕌 Comprehensive Islam Articles Scraper"
echo "======================================"

# Check if virtual environment exists
if [ ! -d "islam_scraper_env" ]; then
    echo "❌ Virtual environment not found. Setting up..."
    python3 -m venv islam_scraper_env
    source islam_scraper_env/bin/activate
    pip install requests beautifulsoup4 lxml
    echo "✅ Virtual environment created"
else
    source islam_scraper_env/bin/activate
    echo "✅ Virtual environment activated"
fi

# Show current options
echo ""
echo "Available modes:"
echo "1. historical  - Scrape ALL articles since 2015 (takes hours)"
echo "2. incremental - Quick check for new articles (5 pages max)"
echo "3. stats       - Show database statistics"
echo "4. export      - Export all articles to JSON"
echo ""

# Get mode from command line argument or prompt user
if [ -z "$1" ]; then
    read -p "Select mode (1-4) or enter mode name: " mode_input
    
    case $mode_input in
        1) MODE="historical" ;;
        2) MODE="incremental" ;;
        3) MODE="stats" ;;
        4) MODE="export" ;;
        *) MODE="$mode_input" ;;
    esac
else
    MODE="$1"
fi

# Run the appropriate mode
case $MODE in
    "historical")
        echo "🚀 Starting FULL HISTORICAL scrape..."
        echo "⚠️  This will take several hours to get all articles since 2015"
        echo "📊 Progress backups will be created every 10 pages"
        read -p "Continue? (y/N): " confirm
        if [[ $confirm =~ ^[Yy]$ ]]; then
            python comprehensive_islam_scraper.py --mode historical --delay 3
        else
            echo "❌ Cancelled"
        fi
        ;;
    "incremental")
        echo "🔄 Running incremental scrape (checking for new articles)..."
        python comprehensive_islam_scraper.py --mode incremental --delay 2
        ;;
    "fast-incremental")
        echo "⚡ Running fast incremental scrape..."
        python comprehensive_islam_scraper.py --mode incremental --max-pages 3 --delay 1
        ;;
    "stats")
        echo "📊 Showing database statistics..."
        python comprehensive_islam_scraper.py --mode stats
        ;;
    "export")
        echo "📄 Exporting all articles to JSON..."
        python comprehensive_islam_scraper.py --mode export
        ;;
    "test")
        echo "🧪 Running test scrape (2 pages only)..."
        python comprehensive_islam_scraper.py --mode historical --max-pages 2 --delay 1
        ;;
    *)
        echo "❌ Unknown mode: $MODE"
        echo "Available modes: historical, incremental, fast-incremental, stats, export, test"
        exit 1
        ;;
esac

echo ""
echo "✅ Scraping completed!"
echo "📄 Check islam_articles.db for the SQLite database"
echo "📊 Run './run_comprehensive_scraper.sh stats' to see statistics"

deactivate