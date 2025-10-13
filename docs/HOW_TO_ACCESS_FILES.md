# 🗂️ How to Access Your HTML, Markdown & All Files

## 📥 **Getting Your Files from GitHub Actions**

The scraper creates hundreds of individual files, but GitHub Actions runs in the cloud. Here's how to access everything:

## 🎯 **Method 1: Artifacts (Recommended)**

### **Download After Each Run**
1. Go to: https://github.com/lioneltchami/islamicdilemma/actions
2. Click on any completed run
3. Scroll down to **"Artifacts"** section
4. Download: **"complete-articles-archive"**
5. Extract the ZIP file

### **What You Get:**
```
complete-articles-archive.zip
├── articles_archive/
│   ├── 📄 html_articles/              # Individual HTML files
│   │   ├── 2015-03-15_First-Article.html
│   │   ├── 2015-04-22_Second-Article.html
│   │   ├── 2025-10-06_Latest-Article.html
│   │   └── ... (hundreds more)
│   ├── 📝 markdown_articles/          # Individual Markdown files  
│   │   ├── 2015-03-15_First-Article.md
│   │   ├── 2015-04-22_Second-Article.md
│   │   └── ... (hundreds more)
│   ├── 🌐 website/                    # Complete browsable website
│   │   ├── index.html                 # Open this in browser!
│   │   └── css/style.css
│   ├── 📊 exports/
│   │   ├── complete_articles.json    # All data in JSON
│   │   └── articles_metadata.csv     # Spreadsheet format
│   └── 💾 islam_articles.db          # SQLite database
```

## 🚀 **Method 2: GitHub Releases (Weekly Backups)**

### **Permanent Storage**
- **When**: Every Sunday at 2 AM UTC
- **What**: Complete archive as release assets
- **Benefit**: Never expires (unlike artifacts)

### **How to Access:**
1. Go to: https://github.com/lioneltchami/islamicdilemma/releases
2. Find latest release (e.g., "data-20251012-0200")
3. Download: **articles-archive.tar.gz**
4. Extract with: `tar -xzf articles-archive.tar.gz`

## 💾 **Method 3: Repository Files (Database Only)**

### **Always Available in Repo:**
- `islam_articles.db` - Complete database
- `all_islam_articles.json` - JSON export
- Both committed automatically after each run

### **Generate Files Locally:**
```bash
# Clone repo
git clone https://github.com/lioneltchami/islamicdilemma.git
cd islamicdilemma

# Install dependencies
pip install -r requirements.txt

# Generate all files from database
python enhanced_article_preservator.py --mode export
```

## 🌐 **Method 4: Browse Online (Coming Soon)**

We can set up GitHub Pages to host the static website:
```
https://lioneltchami.github.io/islamicdilemma/
```

---

# 📅 **File Organization & Dating System**

## 🔤 **File Naming Convention**
```
Format: YYYY-MM-DD_Article-Title.html
Examples:
- 2015-03-15_First-Islam-Article.html
- 2020-07-22_Muhammad-Analysis.html  
- 2025-10-06_Latest-Article.html
```

## 📊 **Chronological Organization**

### **In File Browser:**
Files automatically sort chronologically when listed:
```
📄 2015-03-15_Oldest-Article.html
📄 2015-04-22_Second-Article.html
📄 2015-06-10_Third-Article.html
...
📄 2025-10-06_Newest-Article.html
```

### **In Website:**
- **Default sort**: Newest first (reverse chronological)
- **Filter by year**: 2015, 2016, 2017, etc.
- **Search by date range**: Custom filtering
- **Timeline view**: Visual chronological browse

### **In Database:**
```sql
-- All articles chronologically
SELECT title, publish_date_parsed, url 
FROM articles 
ORDER BY publish_date_parsed ASC;

-- Articles by year
SELECT COUNT(*), strftime('%Y', publish_date_parsed) as year
FROM articles 
GROUP BY year 
ORDER BY year;
```

---

# 📈 **Expected File Counts by Era**

Based on typical blog patterns:

```
📊 Estimated Distribution:
├── 2015-2017: ~50-80 articles   (early period)
├── 2018-2020: ~80-120 articles  (growth period)  
├── 2021-2023: ~100-150 articles (peak period)
└── 2024-2025: ~50-80 articles   (recent period)

Total Expected: 280-430 Islam-related articles
File Count: 560-860 files (HTML + Markdown)
```

---

# 🎯 **Quick Access Guide**

## **For Reading Articles:**
1. **Download artifacts** from latest GitHub Action run
2. **Extract ZIP** to your computer
3. **Open `website/index.html`** in browser for browsing
4. **Or browse `html_articles/`** for individual files

## **For Research/Analysis:**
1. **Download `complete_articles.json`** for structured data
2. **Download `articles_metadata.csv`** for spreadsheet analysis
3. **Download `islam_articles.db`** for SQL queries

## **For Offline Archive:**
1. **Download release** (permanent storage)
2. **Extract to external drive** for backup
3. **Copy `website/` folder** for portable browsing

---

# 🔄 **Update Process**

## **Getting New Articles:**
1. **Automatic**: Files updated every 6 hours via GitHub Actions
2. **Download latest artifacts** to get new articles
3. **Database always current** in repository
4. **Weekly releases** capture complete snapshots

## **Incremental Updates:**
- **New files appear** with recent dates
- **Database grows** but never duplicates
- **Website updates** automatically with new content
- **Existing files unchanged** (immutable archive)

---

# 💡 **Pro Tips**

## **Best Practices:**
- ✅ **Download weekly releases** for permanent storage
- ✅ **Keep local backup** on external drive  
- ✅ **Use website interface** for browsing and search
- ✅ **Use individual files** for detailed reading
- ✅ **Use database/JSON** for analysis and research

## **Storage Estimates:**
- **Individual HTML files**: ~20-50 KB each
- **Individual Markdown files**: ~10-20 KB each  
- **Complete archive**: 50-200 MB total
- **Database**: 5-20 MB
- **Website**: 2-5 MB

## **Automation:**
The system handles all file organization automatically:
- ✅ **Chronological naming**
- ✅ **Duplicate prevention** 
- ✅ **Metadata extraction**
- ✅ **Multi-format generation**
- ✅ **Website compilation**

**You just download and use - everything is perfectly organized!** 📚