# Islam Articles Scraper

This script scrapes articles about Islam from the Max Shimba Ministries blog (https://maxshimbaministries.org).

## Features

- ✅ Respects robots.txt
- ✅ Rate-limited requests (2-second delays)
- ✅ Handles pagination automatically
- ✅ Filters articles using Islam-related keywords
- ✅ Extracts title, URL, content preview, and date
- ✅ Saves results to JSON format
- ✅ Provides detailed console output

## Files

- `islam_articles_scraper.py` - Main scraper script
- `run_scraper.sh` - Convenience script to run the scraper
- `islam_articles.json` - Output file with scraped articles
- `islam_scraper_env/` - Python virtual environment

## Usage

### Option 1: Use the convenience script
```bash
./run_scraper.sh
```

### Option 2: Manual execution
```bash
# Activate virtual environment
source islam_scraper_env/bin/activate

# Run the scraper
python islam_articles_scraper.py

# Deactivate virtual environment
deactivate
```

## Output

The script will:
1. Check robots.txt for ethical compliance
2. Scrape up to 10 pages of blog posts
3. Filter for Islam-related content using keywords
4. Save results to `islam_articles.json`
5. Display a summary of found articles

## Keywords Used for Filtering

The script looks for articles containing these Islam-related terms:
- islam, islamic, muslim, muslims
- quran, quranic, koran
- muhammad, prophet muhammad, allah
- hadith, jihad, sharia, mosque
- mecca, medina, caliphate, caliph
- imam, sunni, shia, shiite
- sufi, sufism, ramadan, hajj
- and more...

## Recent Test Results

Last run found **26 Islam-related articles** across 10 pages of the blog.

## Configuration

You can modify the script to:
- Change the maximum number of pages scraped (default: 10)
- Add or remove keyword filters
- Adjust the delay between requests
- Change the output filename

Edit the variables at the top of `islam_articles_scraper.py` to customize behavior.