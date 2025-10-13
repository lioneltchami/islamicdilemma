#!/usr/bin/env python3
"""
GitHub Actions Islam Articles Scraper
Enhanced version with better date extraction and GitHub Actions optimization
"""

import requests
from bs4 import BeautifulSoup
import time
import re
import json
import sqlite3
from datetime import datetime, timedelta
from urllib.parse import urljoin, urlparse
import sys
import os
import hashlib
import argparse
from pathlib import Path
import logging
from dateutil import parser as date_parser
import pytz

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class GitHubActionsIslamScraper:
    def __init__(self, base_url="https://maxshimbaministries.org", db_path="islam_articles.db"):
        self.base_url = base_url
        self.db_path = db_path
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; IslamArticlesScraper/1.0; +https://github.com/your-repo)'
        })
        
        # Enhanced Islam-related keywords
        self.islam_keywords = [
            'islam', 'islamic', 'muslim', 'muslims', 'quran', 'quranic', 'koran',
            'muhammad', 'prophet muhammad', 'allah', 'hadith', 'jihad', 'sharia',
            'mosque', 'mecca', 'medina', 'caliphate', 'caliph', 'imam', 'sunni',
            'shia', 'shiite', 'sufi', 'sufism', 'ramadan', 'hajj', 'pilgrimage',
            'mujahideen', 'fatwa', 'ulema', 'madrasah', 'madrasa', 'kaaba', 'kabah',
            'sunnah', 'tafsir', 'ijma', 'ummah', 'shariah', 'halal', 'haram',
            'bismillah', 'salah', 'zakat', 'sawm', 'fasting', 'eid', 'hijab',
            'burqa', 'minaret', 'mihrab', 'qibla', 'umrah', 'tawaf', 'iftar',
            'sahur', 'tarawih', 'khutbah', 'jummah', 'dua', 'dhikr', 'takbir'
        ]
        
        self.setup_database()
        
    def setup_database(self):
        """Create SQLite database for persistent storage"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT UNIQUE NOT NULL,
                title TEXT NOT NULL,
                content_preview TEXT,
                full_content TEXT,
                publish_date TEXT,
                publish_date_parsed TEXT,
                date_source TEXT,
                scraped_at TEXT,
                matching_keyword TEXT,
                url_hash TEXT UNIQUE,
                word_count INTEGER,
                last_updated TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scraping_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_date TEXT,
                mode TEXT,
                pages_scraped INTEGER,
                articles_found INTEGER,
                new_articles INTEGER,
                last_url TEXT,
                github_run_id TEXT,
                duration_seconds INTEGER
            )
        ''')
        
        # Add indexes for better performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_url_hash ON articles(url_hash)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_publish_date ON articles(publish_date_parsed)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_keyword ON articles(matching_keyword)')
        
        conn.commit()
        conn.close()
        logger.info(f"✅ Database initialized: {self.db_path}")
    
    def extract_date_comprehensive(self, soup, url, post_element):
        """
        Enhanced date extraction using multiple strategies
        """
        date_info = {
            'raw_date': None,
            'parsed_date': None,
            'source': 'unknown',
            'confidence': 'low'
        }
        
        strategies = [
            self._extract_date_from_url,
            self._extract_date_from_meta,
            self._extract_date_from_structured_data,
            self._extract_date_from_post_element,
            self._extract_date_from_content,
        ]
        
        for strategy in strategies:
            try:
                result = strategy(soup, url, post_element)
                if result and result['parsed_date']:
                    # If we found a high confidence date, use it
                    if result['confidence'] == 'high':
                        return result
                    # Otherwise, keep the best one so far
                    if date_info['confidence'] != 'high':
                        date_info = result
            except Exception as e:
                logger.debug(f"Date extraction strategy failed: {e}")
                continue
        
        return date_info
    
    def _extract_date_from_url(self, soup, url, post_element):
        """Extract date from URL pattern"""
        if not url:
            return None
        
        # Pattern: /2025/10/article-name.html
        url_date_match = re.search(r'/(\d{4})/(\d{2})/', url)
        if url_date_match:
            year, month = url_date_match.groups()
            try:
                parsed = datetime(int(year), int(month), 1)
                return {
                    'raw_date': f"{year}-{month}",
                    'parsed_date': parsed.isoformat(),
                    'source': 'url_pattern',
                    'confidence': 'medium'
                }
            except ValueError:
                pass
        
        # Pattern: article-name-2025-10-15.html
        url_date_match = re.search(r'-(\d{4})-(\d{2})-(\d{2})', url)
        if url_date_match:
            year, month, day = url_date_match.groups()
            try:
                parsed = datetime(int(year), int(month), int(day))
                return {
                    'raw_date': f"{year}-{month}-{day}",
                    'parsed_date': parsed.isoformat(),
                    'source': 'url_filename',
                    'confidence': 'high'
                }
            except ValueError:
                pass
        
        return None
    
    def _extract_date_from_meta(self, soup, url, post_element):
        """Extract date from meta tags"""
        meta_selectors = [
            ('meta[property="article:published_time"]', 'content'),
            ('meta[property="article:modified_time"]', 'content'),
            ('meta[name="date"]', 'content'),
            ('meta[name="publish_date"]', 'content'),
            ('meta[name="publication_date"]', 'content'),
            ('meta[name="DC.date.issued"]', 'content'),
            ('meta[itemprop="datePublished"]', 'content'),
            ('meta[itemprop="dateCreated"]', 'content'),
        ]
        
        for selector, attr in meta_selectors:
            meta_tag = soup.select_one(selector)
            if meta_tag and meta_tag.get(attr):
                date_str = meta_tag[attr]
                try:
                    parsed = date_parser.parse(date_str)
                    return {
                        'raw_date': date_str,
                        'parsed_date': parsed.isoformat(),
                        'source': f'meta_{selector}',
                        'confidence': 'high'
                    }
                except (ValueError, TypeError):
                    continue
        
        return None
    
    def _extract_date_from_structured_data(self, soup, url, post_element):
        """Extract date from JSON-LD structured data"""
        scripts = soup.find_all('script', type='application/ld+json')
        for script in scripts:
            try:
                data = json.loads(script.string)
                if isinstance(data, dict):
                    # Handle single object
                    date_str = (data.get('datePublished') or 
                               data.get('dateCreated') or 
                               data.get('publishedDate'))
                    if date_str:
                        parsed = date_parser.parse(date_str)
                        return {
                            'raw_date': date_str,
                            'parsed_date': parsed.isoformat(),
                            'source': 'json_ld',
                            'confidence': 'high'
                        }
                elif isinstance(data, list):
                    # Handle array of objects
                    for item in data:
                        if isinstance(item, dict):
                            date_str = (item.get('datePublished') or 
                                       item.get('dateCreated') or 
                                       item.get('publishedDate'))
                            if date_str:
                                parsed = date_parser.parse(date_str)
                                return {
                                    'raw_date': date_str,
                                    'parsed_date': parsed.isoformat(),
                                    'source': 'json_ld_array',
                                    'confidence': 'high'
                                }
            except (json.JSONDecodeError, ValueError, TypeError):
                continue
        
        return None
    
    def _extract_date_from_post_element(self, soup, url, post_element):
        """Extract date from post element selectors"""
        if not post_element:
            return None
        
        date_selectors = [
            ('time[datetime]', 'datetime'),
            ('time', 'text'),
            ('[class*="date"]', 'text'),
            ('[class*="publish"]', 'text'),
            ('[class*="time"]', 'text'),
            ('.entry-date', 'text'),
            ('.post-date', 'text'),
            ('.published', 'text'),
            ('[itemprop="datePublished"]', 'text'),
            ('[itemprop="dateCreated"]', 'text'),
        ]
        
        for selector, attr_type in date_selectors:
            elements = post_element.select(selector)
            for element in elements:
                if attr_type == 'datetime' and element.get('datetime'):
                    date_str = element['datetime']
                else:
                    date_str = element.get_text(strip=True)
                
                if date_str:
                    try:
                        parsed = date_parser.parse(date_str)
                        return {
                            'raw_date': date_str,
                            'parsed_date': parsed.isoformat(),
                            'source': f'post_element_{selector}',
                            'confidence': 'medium' if attr_type == 'datetime' else 'low'
                        }
                    except (ValueError, TypeError):
                        continue
        
        return None
    
    def _extract_date_from_content(self, soup, url, post_element):
        """Extract date from content text using regex patterns"""
        content_element = post_element or soup
        text = content_element.get_text() if content_element else ""
        
        # Common date patterns
        date_patterns = [
            r'Published:?\s*(\w+\s+\d{1,2},?\s+\d{4})',
            r'Posted:?\s*(\w+\s+\d{1,2},?\s+\d{4})',
            r'Date:?\s*(\w+\s+\d{1,2},?\s+\d{4})',
            r'(\w+\s+\d{1,2},?\s+\d{4})',  # Generic month day, year
            r'(\d{1,2}/\d{1,2}/\d{4})',    # MM/DD/YYYY
            r'(\d{4}-\d{2}-\d{2})',        # YYYY-MM-DD
        ]
        
        for pattern in date_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    parsed = date_parser.parse(match)
                    # Only accept dates that seem reasonable (after 2000, not in future)
                    if 2000 <= parsed.year <= datetime.now().year + 1:
                        return {
                            'raw_date': match,
                            'parsed_date': parsed.isoformat(),
                            'source': 'content_regex',
                            'confidence': 'low'
                        }
                except (ValueError, TypeError):
                    continue
        
        return None
    
    def url_exists(self, url):
        """Check if URL already exists in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        url_hash = hashlib.md5(url.encode()).hexdigest()
        cursor.execute("SELECT id FROM articles WHERE url = ? OR url_hash = ?", (url, url_hash))
        exists = cursor.fetchone() is not None
        
        conn.close()
        return exists
    
    def save_article(self, article_data):
        """Save article to database, avoiding duplicates"""
        if self.url_exists(article_data['url']):
            return False
            
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        url_hash = hashlib.md5(article_data['url'].encode()).hexdigest()
        word_count = len(article_data.get('full_content', '').split())
        
        cursor.execute('''
            INSERT INTO articles (url, title, content_preview, full_content, 
                                publish_date, publish_date_parsed, date_source,
                                scraped_at, matching_keyword, url_hash, word_count)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            article_data['url'],
            article_data['title'],
            article_data['content_preview'],
            article_data.get('full_content', ''),
            article_data.get('publish_date', ''),
            article_data.get('publish_date_parsed', ''),
            article_data.get('date_source', 'unknown'),
            article_data['scraped_at'],
            article_data['matching_keyword'],
            url_hash,
            word_count
        ))
        
        conn.commit()
        conn.close()
        return True
    
    def is_islam_related(self, title, content, url):
        """Determine if an article is related to Islam"""
        text_to_check = (title + " " + content).lower()
        
        for keyword in self.islam_keywords:
            if keyword.lower() in text_to_check:
                return True, keyword
        
        return False, None
    
    def extract_article_info(self, post_element, soup, page_url):
        """Extract comprehensive information from a blog post element"""
        try:
            # Extract title
            title_elem = post_element.find(['h1', 'h2', 'h3'], class_=re.compile(r'post-title|entry-title|title'))
            if not title_elem:
                title_elem = post_element.find(['h1', 'h2', 'h3'])
            
            title = title_elem.get_text(strip=True) if title_elem else "No title found"
            
            # Extract URL
            link_elem = title_elem.find('a') if title_elem else None
            if not link_elem:
                link_elem = post_element.find('a', href=True)
            
            url = link_elem['href'] if link_elem else None
            if url and not url.startswith('http'):
                url = urljoin(self.base_url, url)
            
            # Extract content
            content_elem = post_element.find(['div'], class_=re.compile(r'post-body|entry-content|content'))
            if not content_elem:
                content_elem = post_element.find(['div', 'p'])
            
            full_content = content_elem.get_text(strip=True) if content_elem else ""
            content_preview = full_content[:500] if full_content else ""
            
            # Extract date using comprehensive method
            date_info = self.extract_date_comprehensive(soup, url, post_element)
            
            article_data = {
                'title': title,
                'url': url,
                'content_preview': content_preview,
                'full_content': full_content,
                'publish_date': date_info['raw_date'] or "No date found",
                'publish_date_parsed': date_info['parsed_date'],
                'date_source': date_info['source'],
                'scraped_at': datetime.now().isoformat()
            }
            
            return article_data
            
        except Exception as e:
            logger.error(f"Error extracting article info: {e}")
            return None
    
    def scrape_page(self, url):
        """Scrape a single page for blog posts"""
        try:
            logger.info(f"🔍 Scraping: {url}")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find blog posts
            post_selectors = [
                'article',
                '.post',
                '.blog-post', 
                '.entry',
                '[class*="post"]',
                '.hentry'
            ]
            
            posts_found = []
            for selector in post_selectors:
                posts = soup.select(selector)
                if posts:
                    posts_found = posts
                    break
            
            if not posts_found:
                posts_found = soup.find_all('div', class_=re.compile(r'post|entry|article'))
            
            articles_on_page = []
            new_articles = 0
            
            for post in posts_found:
                article_info = self.extract_article_info(post, soup, url)
                if article_info and article_info['url']:
                    
                    # Check if it's Islam-related
                    is_related, keyword = self.is_islam_related(
                        article_info['title'], 
                        article_info['content_preview'],
                        article_info['url']
                    )
                    
                    if is_related:
                        article_info['matching_keyword'] = keyword
                        articles_on_page.append(article_info)
                        
                        # Save to database
                        if self.save_article(article_info):
                            new_articles += 1
                            date_str = article_info['publish_date'][:10] if article_info['publish_date'] != "No date found" else "Unknown date"
                            logger.info(f"✅ NEW: {article_info['title'][:60]}... [{date_str}] [keyword: {keyword}]")
                        else:
                            logger.info(f"📋 EXISTS: {article_info['title'][:60]}...")
            
            return articles_on_page, soup, new_articles
            
        except Exception as e:
            logger.error(f"❌ Error scraping page {url}: {e}")
            return [], None, 0
    
    def find_next_page_url(self, soup):
        """Find the URL for the next page of blog posts"""
        next_selectors = [
            'a[title*="Older"]',
            '.blog-pager-older-link',
            '.blog-pager a[href*="max-results"]'
        ]
        
        for selector in next_selectors:
            try:
                next_link = soup.select_one(selector)
                if next_link and next_link.get('href'):
                    next_url = next_link['href']
                    if not next_url.startswith('http'):
                        next_url = urljoin(self.base_url, next_url)
                    return next_url
            except:
                continue
        
        # Fallback: look for "Older Posts" text
        for link in soup.find_all('a', href=True):
            if 'older' in link.get_text().lower():
                next_url = link['href']
                if not next_url.startswith('http'):
                    next_url = urljoin(self.base_url, next_url)
                return next_url
        
        return None
    
    def scrape_articles(self, mode='incremental', max_pages=None, delay=2):
        """Main scraping method"""
        start_time = datetime.now()
        
        if mode == 'historical':
            logger.info(f"🚀 Starting HISTORICAL scrape")
            max_pages = max_pages or 999999  # Unlimited
        else:
            logger.info(f"🔄 Starting INCREMENTAL scrape")
            max_pages = max_pages or 5
        
        logger.info(f"📊 Current database has {self.get_article_count()} articles")
        
        current_url = self.base_url
        page_count = 0
        total_new_articles = 0
        total_articles_found = 0
        
        while current_url and page_count < max_pages:
            page_count += 1
            logger.info(f"\n📄 Page {page_count} | Elapsed: {datetime.now() - start_time}")
            
            articles, soup, new_articles = self.scrape_page(current_url)
            total_articles_found += len(articles)
            total_new_articles += new_articles
            
            # For incremental mode, stop if no new articles on first 2 pages
            if mode == 'incremental' and page_count >= 2 and total_new_articles == 0:
                logger.info("✅ No new articles found - database is up to date!")
                break
            
            if soup:
                next_url = self.find_next_page_url(soup)
                if next_url and next_url != current_url:
                    current_url = next_url
                else:
                    logger.info("🔚 No more pages found - reached the end!")
                    break
            else:
                break
            
            time.sleep(delay)
        
        duration = datetime.now() - start_time
        
        # Log the run
        self.log_scraping_run(mode, page_count, total_articles_found, total_new_articles, current_url, duration.total_seconds())
        
        logger.info(f"\n🎉 SCRAPING COMPLETE!")
        logger.info(f"📊 Pages scraped: {page_count}")
        logger.info(f"📊 Islam articles found: {total_articles_found}")
        logger.info(f"📊 New articles saved: {total_new_articles}")
        logger.info(f"📊 Total in database: {self.get_article_count()}")
        logger.info(f"⏱️ Total time: {duration}")
        
        return {
            'pages_scraped': page_count,
            'articles_found': total_articles_found,
            'new_articles': total_new_articles,
            'total_in_db': self.get_article_count(),
            'duration': duration.total_seconds()
        }
    
    def get_article_count(self):
        """Get total count of articles in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM articles")
        count = cursor.fetchone()[0]
        conn.close()
        return count
    
    def log_scraping_run(self, mode, pages_scraped, articles_found, new_articles, last_url, duration):
        """Log the scraping run details"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        github_run_id = os.environ.get('GITHUB_RUN_ID', '')
        
        cursor.execute('''
            INSERT INTO scraping_log (run_date, mode, pages_scraped, articles_found, 
                                    new_articles, last_url, github_run_id, duration_seconds)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now().isoformat(),
            mode,
            pages_scraped,
            articles_found,
            new_articles,
            last_url,
            github_run_id,
            duration
        ))
        
        conn.commit()
        conn.close()
    
    def export_to_json(self, filename="all_islam_articles.json"):
        """Export all articles from database to JSON"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT url, title, content_preview, publish_date, publish_date_parsed, 
                   date_source, scraped_at, matching_keyword, word_count
            FROM articles 
            ORDER BY publish_date_parsed DESC, scraped_at DESC
        ''')
        
        articles = []
        for row in cursor.fetchall():
            articles.append({
                'url': row[0],
                'title': row[1], 
                'content_preview': row[2],
                'publish_date': row[3],
                'publish_date_parsed': row[4],
                'date_source': row[5],
                'scraped_at': row[6],
                'matching_keyword': row[7],
                'word_count': row[8]
            })
        
        conn.close()
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(articles, f, indent=2, ensure_ascii=False)
        
        logger.info(f"📄 Exported {len(articles)} articles to {filename}")
        return len(articles)

def main():
    parser = argparse.ArgumentParser(description='GitHub Actions Islam Articles Scraper')
    parser.add_argument('--mode', choices=['historical', 'incremental'], 
                       default='incremental', help='Scraping mode')
    parser.add_argument('--max-pages', type=int, help='Maximum pages to scrape')
    parser.add_argument('--delay', type=float, default=2.0, help='Delay between requests')
    parser.add_argument('--export-file', default='all_islam_articles.json', help='Export filename')
    
    args = parser.parse_args()
    
    scraper = GitHubActionsIslamScraper()
    
    try:
        # Run scraping
        results = scraper.scrape_articles(
            mode=args.mode,
            max_pages=args.max_pages,
            delay=args.delay
        )
        
        # Export data
        article_count = scraper.export_to_json(args.export_file)
        
        # Set GitHub Actions outputs
        if os.environ.get('GITHUB_ACTIONS'):
            with open(os.environ['GITHUB_OUTPUT'], 'a') as f:
                f.write(f"pages_scraped={results['pages_scraped']}\n")
                f.write(f"new_articles={results['new_articles']}\n")
                f.write(f"total_articles={results['total_in_db']}\n")
                f.write(f"export_count={article_count}\n")
        
        logger.info("✅ Scraping completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Scraping failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()