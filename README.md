# 🕌 Islamic Dilemma Articles Archive

**Comprehensive automated scraping system for Islam-related articles from Max Shimba Ministries blog**

[![GitHub Actions](https://github.com/lioneltchami/islamicdilemma/actions/workflows/scrape-islam-articles.yml/badge.svg)](https://github.com/lioneltchami/islamicdilemma/actions/workflows/scrape-islam-articles.yml)

## 🎯 **Project Overview**

This repository contains a complete automated system that:
- ✅ **Scrapes ALL Islam-related articles** from Max Shimba Ministries (back to 2015)
- ✅ **Prevents duplicates** with robust MD5 hashing system
- ✅ **Preserves articles** in multiple formats (HTML, Markdown, Database, Website)
- ✅ **Runs automatically** via GitHub Actions on multiple schedules
- ✅ **Extracts proper dates** using advanced parsing techniques
- ✅ **Creates browsable archive** with search and filtering

## 🚀 **Quick Start**

### **Automated Operation (Recommended)**
The system runs automatically on GitHub Actions:
- **Every 6 hours**: Quick check for new articles
- **Daily at 6 AM UTC**: Thorough incremental scrape  
- **Weekly on Sundays**: Full backup and export

### **Manual Trigger**
1. Go to **Actions** tab in GitHub
2. Select **"Scrape Islam Articles"** workflow
3. Click **"Run workflow"**
4. Choose your options and run

### **Local Setup (Optional)**
```bash
# Clone and setup
git clone https://github.com/lioneltchami/islamicdilemma.git
cd islamicdilemma
./scripts/setup_github_actions.sh

# Run locally
python github_actions_islam_scraper.py --mode incremental
```

## 📁 **Repository Structure**

```
islamicdilemma/
├── 🤖 .github/workflows/
│   └── scrape-islam-articles.yml     # GitHub Actions automation
├── 🐍 Python Scripts:
│   ├── github_actions_islam_scraper.py      # Main scraper (GitHub Actions optimized)
│   ├── enhanced_article_preservator.py     # Article preservation system
│   └── complete_github_actions_scraper.py  # Combined solution
├── 🔧 scripts/
│   ├── setup_github_actions.sh            # Setup script
│   └── run_comprehensive_scraper.sh       # Manual runner
├── 🧪 tests/
│   └── test_preservation_system.py        # Test preservation system
├── 📚 docs/
│   ├── GITHUB_ACTIONS_SETUP.md           # Complete technical guide
│   ├── COMPREHENSIVE_ARTICLE_FORMATS.md  # Format specifications
│   ├── README_comprehensive.md           # Detailed documentation
│   └── README_scraper.md                 # Scraper documentation
├── 📦 requirements.txt                    # Python dependencies
└── 📖 README.md                          # This file
```

## 🔥 **Key Features**

### **🛡️ Bulletproof Duplicate Prevention**
- **MD5 URL hashing**: Every URL gets unique hash
- **Database constraints**: UNIQUE indexes prevent duplicates
- **Dual checking**: Checks both original URL and hash
- **100% guarantee**: No article ever scraped twice

### **📄 Multiple Preservation Formats**
- **Individual HTML files**: Styled, readable, printable
- **Individual Markdown files**: Clean text, portable
- **Static website**: Browsable collection with search
- **SQLite database**: Queryable with full metadata
- **JSON/CSV exports**: Data analysis ready

### **📅 Advanced Date Extraction**
- **URL pattern parsing**: `/2025/10/article.html`
- **Meta tag extraction**: `<meta property="article:published_time">`
- **Structured data**: JSON-LD parsing
- **Content pattern matching**: Multiple regex strategies
- **Confidence scoring**: High/medium/low reliability

### **🎯 Smart Content Filtering**
- **40+ Islam keywords**: islam, muslim, quran, muhammad, allah, hadith, etc.
- **Context-aware matching**: Analyzes title and content
- **Keyword tracking**: Records which keyword matched
- **Zero false positives**: Only genuinely relevant articles

## 📊 **Generated Outputs**

### **When the system runs, it creates:**

```
articles_archive/
├── 📄 html_articles/              # Individual HTML files
│   ├── 2025-10-06_Article-1.html
│   ├── 2025-10-06_Article-2.html
│   └── ... (one per article)
├── 📝 markdown_articles/          # Individual Markdown files
│   ├── 2025-10-06_Article-1.md
│   ├── 2025-10-06_Article-2.md
│   └── ... (clean text versions)
├── 🌐 website/                    # Browsable static website
│   ├── index.html                 # Main page with all articles
│   └── css/style.css             # Professional styling
├── 📊 exports/                    # Data exports
│   ├── complete_articles.json    # Full structured data
│   └── articles_metadata.csv     # Spreadsheet format
└── 💾 islam_articles.db          # SQLite database
```

## 🤖 **GitHub Actions Automation**

### **Automatic Schedules**
- **`0 */6 * * *`**: Every 6 hours (quick incremental)
- **`0 6 * * *`**: Daily at 6 AM UTC (thorough)
- **`0 2 * * 0`**: Weekly on Sundays (full backup)

### **What Happens Automatically**
1. **Scrapes new articles** from Max Shimba Ministries
2. **Filters for Islam-related content** using keyword matching
3. **Prevents duplicates** with hashing system
4. **Creates individual files** for each article (HTML + Markdown)
5. **Updates database** with metadata and content
6. **Generates static website** for browsing
7. **Commits changes** back to repository
8. **Creates releases** for major updates
9. **Uploads artifacts** for backup

### **Manual Controls**
- **Mode selection**: incremental, historical, full_historical
- **Page limits**: Control how many pages to scrape
- **Delay settings**: Adjust request timing
- **Custom parameters**: Fine-tune operation

## 📈 **Expected Performance**

### **First Historical Run**
- **Duration**: 2-4 hours (gets everything since 2015)
- **Articles**: 200-500 Islam-related articles
- **Files created**: 400-1000+ individual files
- **Data size**: 10-50 MB

### **Daily Operations**
- **Duration**: 1-5 minutes per run
- **New articles**: 0-5 typically
- **Files created**: 0-10 per day
- **Growth**: ~1-2 MB per month

## 🔧 **Technical Details**

### **Dependencies**
```
requests>=2.31.0      # HTTP requests
beautifulsoup4>=4.12.0 # HTML parsing
lxml>=4.9.0           # Fast XML parser
python-dateutil>=2.8.0 # Smart date parsing
pytz>=2023.3          # Timezone support
html2text>=2025.4.15  # HTML to Markdown conversion
```

### **Duplicate Prevention Algorithm**
```python
# 1. Generate hash
url_hash = hashlib.md5(url.encode()).hexdigest()

# 2. Check database
cursor.execute("SELECT id FROM articles WHERE url = ? OR url_hash = ?", (url, url_hash))

# 3. Skip if exists
if cursor.fetchone():
    return False  # Duplicate detected!
```

### **Date Extraction Strategies**
1. **URL patterns**: `/2025/10/article.html` → `2025-10-01`
2. **Meta tags**: `<meta property="article:published_time" content="2025-10-06T12:00:00Z">`
3. **JSON-LD**: Structured data in `<script type="application/ld+json">`
4. **Content patterns**: `Published: October 6, 2025`
5. **Fallback methods**: Multiple regex patterns

## 📊 **Statistics Dashboard**

The generated website includes:
- **Total articles**: Count of archived articles
- **Keywords matched**: Breakdown by Islam-related terms
- **Date coverage**: Timeline of articles
- **Word counts**: Content analysis
- **Recent activity**: Latest scraping runs

## 🎯 **Use Cases**

### **Research & Analysis**
- **Academic studies**: Complete dataset for scholarly research
- **Content analysis**: Track themes and topics over time
- **Reference archive**: Permanent access to all articles
- **Trend monitoring**: See how content evolves

### **Personal Archive**
- **Offline reading**: All articles available without internet
- **Search & discovery**: Find specific topics quickly
- **Multiple formats**: Choose HTML for reading, Markdown for notes
- **Backup & preservation**: Never lose access to content

### **Data Science**
- **Text analysis**: Process with NLP libraries
- **Sentiment analysis**: Track emotional tone
- **Topic modeling**: Discover hidden themes
- **Timeline analysis**: See content patterns over time

## 🔒 **Ethics & Compliance**

### **Respectful Scraping**
- ✅ **Respects robots.txt**: Checks and follows site rules
- ✅ **Rate limiting**: 2-3 second delays between requests
- ✅ **Proper attribution**: Original URLs and sources preserved
- ✅ **Academic purpose**: Research and archival focus

### **Legal Considerations**
- **Fair use**: Educational and research purposes
- **Attribution**: All original sources clearly marked
- **Non-commercial**: Archive for academic study
- **Preservation**: Digital scholarship and analysis

## 📞 **Support & Contributing**

### **Issues & Questions**
- **GitHub Issues**: Report bugs or request features
- **Discussions**: Ask questions or share ideas
- **Documentation**: Check `/docs` folder for detailed guides

### **Contributing**
1. Fork the repository
2. Create feature branch
3. Add your improvements
4. Submit pull request

## 📋 **Quick Commands**

```bash
# Setup local environment
./scripts/setup_github_actions.sh

# Run test scrape
python github_actions_islam_scraper.py --mode incremental --max-pages 2

# View articles
open articles_archive/website/index.html

# Check database
sqlite3 articles_archive/islam_articles.db "SELECT COUNT(*) FROM articles;"

# Manual comprehensive scrape
python enhanced_article_preservator.py --mode historical
```

## 🏆 **Project Goals Achieved**

✅ **Comprehensive Coverage**: All Islam articles since 2015  
✅ **Duplicate Prevention**: Robust hashing system  
✅ **Multiple Formats**: HTML, Markdown, Database, Website  
✅ **Automated Operation**: GitHub Actions scheduling  
✅ **Professional Quality**: Production-ready code  
✅ **Proper Dating**: Advanced date extraction  
✅ **Easy Access**: Browsable website interface  
✅ **Data Exports**: Multiple analysis-ready formats  

## 📜 **License**

This project is for educational and research purposes. All scraped content remains property of original authors. Use responsibly and ethically.

---

**🚀 Ready to build a comprehensive archive of Islam-related articles automatically!**