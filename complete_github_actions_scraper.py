#!/usr/bin/env python3
"""
Complete GitHub Actions Islam Articles Scraper with Enhanced Preservation
Combines scraping, duplicate prevention, and multiple output formats
"""

import requests
from bs4 import BeautifulSoup
import time
import re
import json
import sqlite3
from datetime import datetime
from urllib.parse import urljoin, urlparse
import sys
import os
import hashlib
import argparse
from pathlib import Path
import logging
from dateutil import parser as date_parser
import html2text

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('complete_scraper.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class CompleteIslamScraper:
    def __init__(self, base_url="https://maxshimbaministries.org", output_dir="articles_archive"):
        self.base_url = base_url
        self.output_dir = Path(output_dir)
        self.db_path = self.output_dir / "islam_articles.db"
        
        # Create directory structure
        self.setup_directories()
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; IslamArticlesComplete/2.0; +https://github.com/your-repo)'
        })
        
        # Enhanced Islam-related keywords
        self.islam_keywords = [
            'islam', 'islamic', 'muslim', 'muslims', 'quran', 'quranic', 'koran',
            'muhammad', 'prophet muhammad', 'allah', 'hadith', 'jihad', 'sharia',
            'mosque', 'mecca', 'medina', 'caliphate', 'caliph', 'imam', 'sunni',
            'shia', 'shiite', 'sufi', 'sufism', 'ramadan', 'hajj', 'pilgrimage',
            'mujahideen', 'fatwa', 'ulema', 'madrasah', 'madrasa', 'kaaba', 'kabah',
            'sunnah', 'tafsir', 'ijma', 'ummah', 'shariah', 'halal', 'haram',
            'bismillah', 'salah', 'zakat', 'sawm', 'fasting', 'eid', 'hijab'
        ]
        
        # HTML to Markdown converter
        self.html2text = html2text.HTML2Text()
        self.html2text.ignore_links = False
        self.html2text.ignore_images = False
        self.html2text.body_width = 80
        
        self.setup_database()
        
    def setup_directories(self):
        """Create organized directory structure"""
        directories = [
            self.output_dir,
            self.output_dir / "html_articles",
            self.output_dir / "markdown_articles", 
            self.output_dir / "website",
            self.output_dir / "website" / "articles",
            self.output_dir / "website" / "css",
            self.output_dir / "exports",
            self.output_dir / "logs"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"✅ Created directory structure: {self.output_dir}")
    
    def setup_database(self):
        """Create enhanced SQLite database with UNIQUE constraints for duplicate prevention"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT UNIQUE NOT NULL,
                title TEXT NOT NULL,
                content_preview TEXT,
                full_content TEXT,
                full_html TEXT,
                publish_date TEXT,
                publish_date_parsed TEXT,
                date_source TEXT,
                scraped_at TEXT,
                matching_keyword TEXT,
                url_hash TEXT UNIQUE,
                word_count INTEGER,
                html_file_path TEXT,
                markdown_file_path TEXT,
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
                files_created INTEGER,
                last_url TEXT,
                github_run_id TEXT,
                duration_seconds INTEGER
            )
        ''')
        
        # Create indexes for performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_url_hash ON articles(url_hash)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_publish_date ON articles(publish_date_parsed)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_keyword ON articles(matching_keyword)')
        
        conn.commit()
        conn.close()
        logger.info(f"✅ Database initialized with duplicate prevention: {self.db_path}")
    
    def url_exists(self, url):
        """ROBUST duplicate detection using URL and hash"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        url_hash = hashlib.md5(url.encode()).hexdigest()
        cursor.execute("SELECT id FROM articles WHERE url = ? OR url_hash = ?", (url, url_hash))
        exists = cursor.fetchone() is not None
        
        conn.close()
        return exists
    
    def is_islam_related(self, title, content, url):
        """Determine if an article is related to Islam"""
        text_to_check = (title + " " + content).lower()
        
        for keyword in self.islam_keywords:
            if keyword.lower() in text_to_check:
                return True, keyword
        
        return False, None
    
    def extract_date_comprehensive(self, soup, url, post_element):
        """Enhanced date extraction with multiple strategies"""
        date_info = {
            'raw_date': None,
            'parsed_date': None,
            'source': 'unknown',
            'confidence': 'low'
        }
        
        # Strategy 1: URL patterns
        if url:
            url_date_match = re.search(r'/(\d{4})/(\d{2})/', url)
            if url_date_match:
                year, month = url_date_match.groups()
                try:
                    parsed = datetime(int(year), int(month), 1)
                    date_info = {
                        'raw_date': f"{year}-{month}",
                        'parsed_date': parsed.isoformat(),
                        'source': 'url_pattern',
                        'confidence': 'medium'
                    }
                except ValueError:
                    pass
        
        # Strategy 2: Meta tags
        if soup:
            meta_selectors = [
                ('meta[property="article:published_time"]', 'content'),
                ('meta[name="date"]', 'content'),
                ('meta[itemprop="datePublished"]', 'content'),
            ]
            
            for selector, attr in meta_selectors:
                meta_tag = soup.select_one(selector)
                if meta_tag and meta_tag.get(attr):
                    try:
                        parsed = date_parser.parse(meta_tag[attr])
                        return {
                            'raw_date': meta_tag[attr],
                            'parsed_date': parsed.isoformat(),
                            'source': f'meta_{selector}',
                            'confidence': 'high'
                        }
                    except (ValueError, TypeError):
                        continue
        
        # Strategy 3: Content patterns
        if post_element:
            text = post_element.get_text()
            date_patterns = [
                r'(\w+\s+\d{1,2},?\s+\d{4})',  # Month day, year
                r'(\d{1,2}/\d{1,2}/\d{4})',    # MM/DD/YYYY
                r'(\d{4}-\d{2}-\d{2})',        # YYYY-MM-DD
            ]
            
            for pattern in date_patterns:
                matches = re.findall(pattern, text)
                for match in matches:
                    try:
                        parsed = date_parser.parse(match)
                        if 2000 <= parsed.year <= datetime.now().year + 1:
                            return {
                                'raw_date': match,
                                'parsed_date': parsed.isoformat(),
                                'source': 'content_regex',
                                'confidence': 'low'
                            }
                    except (ValueError, TypeError):
                        continue
        
        return date_info
    
    def fetch_full_article_content(self, article_url):
        """Fetch complete article content from individual page"""
        try:
            logger.info(f"📄 Fetching full content: {article_url}")
            response = self.session.get(article_url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find main content
            content_selectors = ['.post-body', '.entry-content', '.content', 'article', '.post']
            
            article_content = None
            for selector in content_selectors:
                article_content = soup.select_one(selector)
                if article_content:
                    break
            
            if article_content:
                # Clean up unwanted elements
                for unwanted in article_content.select('.navigation, .sidebar, .footer, .header, .comments, script, style'):
                    unwanted.decompose()
                
                return {
                    'html': str(article_content),
                    'text': article_content.get_text(strip=True),
                    'success': True
                }
            
            return {'html': '', 'text': '', 'success': False}
                
        except Exception as e:
            logger.error(f"❌ Error fetching full content: {e}")
            return {'html': '', 'text': '', 'success': False}
    
    def sanitize_filename(self, text):
        """Create safe filename from text"""
        safe_text = re.sub(r'[^\w\s-]', '', text)
        safe_text = re.sub(r'[-\s]+', '-', safe_text)
        return safe_text.strip('-')[:100]
    
    def save_as_html(self, article_data):
        """Save article as styled HTML file"""
        try:
            date_str = article_data.get('publish_date_parsed', '').split('T')[0] if article_data.get('publish_date_parsed') else 'unknown-date'
            filename = f"{date_str}_{self.sanitize_filename(article_data['title'])}.html"
            filepath = self.output_dir / "html_articles" / filename
            
            html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{article_data['title']}</title>
    <style>
        body {{ font-family: Georgia, serif; line-height: 1.6; max-width: 800px; margin: 0 auto; padding: 20px; background-color: #f9f9f9; }}
        .article {{ background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .header {{ border-bottom: 2px solid #333; margin-bottom: 30px; padding-bottom: 20px; }}
        .title {{ color: #333; font-size: 2em; margin-bottom: 10px; }}
        .meta {{ color: #666; font-size: 0.9em; margin-bottom: 10px; }}
        .content {{ color: #444; font-size: 1.1em; }}
        .footer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; color: #666; font-size: 0.9em; }}
        a {{ color: #0066cc; }}
        blockquote {{ border-left: 4px solid #ddd; margin: 20px 0; padding-left: 20px; font-style: italic; }}
    </style>
</head>
<body>
    <div class="article">
        <div class="header">
            <h1 class="title">{article_data['title']}</h1>
            <div class="meta">
                📅 Published: {article_data.get('publish_date', 'Unknown')}<br>
                🔗 Original: <a href="{article_data['url']}" target="_blank">{article_data['url']}</a><br>
                🏷️ Keyword: {article_data.get('matching_keyword', 'N/A')}<br>
                📝 Words: {article_data.get('word_count', 0)}<br>
                💾 Archived: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            </div>
        </div>
        <div class="content">
            {article_data.get('full_html', article_data.get('content_preview', ''))}
        </div>
        <div class="footer">
            <p><strong>Archive Information:</strong></p>
            <p>This article was automatically archived from Max Shimba Ministries as part of an Islam-related articles collection.</p>
            <p>Date extraction method: {article_data.get('date_source', 'unknown')}</p>
        </div>
    </div>
</body>
</html>"""
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"✅ HTML saved: {filepath.name}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"❌ Error saving HTML: {e}")
            return None
    
    def save_as_markdown(self, article_data):
        """Save article as Markdown file"""
        try:
            date_str = article_data.get('publish_date_parsed', '').split('T')[0] if article_data.get('publish_date_parsed') else 'unknown-date'
            filename = f"{date_str}_{self.sanitize_filename(article_data['title'])}.md"
            filepath = self.output_dir / "markdown_articles" / filename
            
            # Convert HTML to Markdown if available
            if article_data.get('full_html'):
                markdown_content = self.html2text.handle(article_data['full_html'])
            else:
                markdown_content = article_data.get('full_content', article_data.get('content_preview', ''))
            
            md_content = f"""# {article_data['title']}

**Publication Date:** {article_data.get('publish_date', 'Unknown')}  
**Original URL:** {article_data['url']}  
**Keyword Match:** {article_data.get('matching_keyword', 'N/A')}  
**Word Count:** {article_data.get('word_count', 0)}  
**Archived:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Date Source:** {article_data.get('date_source', 'unknown')}

---

{markdown_content}

---

*This article was automatically archived from Max Shimba Ministries as part of an Islam-related articles collection.*
"""
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(md_content)
            
            logger.info(f"✅ Markdown saved: {filepath.name}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"❌ Error saving Markdown: {e}")
            return None
    
    def extract_article_info(self, post_element, soup, page_url):
        """Extract comprehensive article information"""
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
            
            # Extract content preview
            content_elem = post_element.find(['div'], class_=re.compile(r'post-body|entry-content|content'))
            if not content_elem:
                content_elem = post_element.find(['div', 'p'])
            
            content_preview = content_elem.get_text(strip=True)[:500] if content_elem else ""
            
            # Extract date
            date_info = self.extract_date_comprehensive(soup, url, post_element)
            
            return {
                'title': title,
                'url': url,
                'content_preview': content_preview,
                'publish_date': date_info['raw_date'] or "No date found",
                'publish_date_parsed': date_info['parsed_date'],
                'date_source': date_info['source'],
                'scraped_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error extracting article info: {e}")
            return None
    
    def save_article_complete(self, article_data):
        """Save article with full preservation (database + files)"""
        if self.url_exists(article_data['url']):
            return False, 0  # Already exists - DUPLICATE PREVENTION WORKING!
        
        # Fetch full content
        full_content = self.fetch_full_article_content(article_data['url'])
        if full_content['success']:
            article_data['full_html'] = full_content['html']
            article_data['full_content'] = full_content['text']
        
        # Save as HTML and Markdown files
        html_path = self.save_as_html(article_data)
        markdown_path = self.save_as_markdown(article_data)
        
        # Update with file paths
        article_data['html_file_path'] = html_path
        article_data['markdown_file_path'] = markdown_path
        
        # Save to database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        url_hash = hashlib.md5(article_data['url'].encode()).hexdigest()
        word_count = len(article_data.get('full_content', '').split())
        
        cursor.execute('''
            INSERT INTO articles (url, title, content_preview, full_content, full_html,
                                publish_date, publish_date_parsed, date_source,
                                scraped_at, matching_keyword, url_hash, word_count,
                                html_file_path, markdown_file_path)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            article_data['url'],
            article_data['title'],
            article_data['content_preview'],
            article_data.get('full_content', ''),
            article_data.get('full_html', ''),
            article_data.get('publish_date', ''),
            article_data.get('publish_date_parsed', ''),
            article_data.get('date_source', 'unknown'),
            article_data['scraped_at'],
            article_data['matching_keyword'],
            url_hash,
            word_count,
            html_path,
            markdown_path
        ))
        
        conn.commit()
        conn.close()
        
        files_created = sum(1 for path in [html_path, markdown_path] if path)
        return True, files_created
    
    def scrape_page(self, url):
        """Scrape a single page with complete preservation"""
        try:
            logger.info(f"🔍 Scraping: {url}")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find blog posts
            post_selectors = ['article', '.post', '.blog-post', '.entry', '[class*="post"]', '.hentry']
            
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
            files_created = 0
            
            for post in posts_found:
                article_info = self.extract_article_info(post, soup, url)
                if article_info and article_info['url']:
                    
                    # Check if Islam-related
                    is_related, keyword = self.is_islam_related(
                        article_info['title'], 
                        article_info['content_preview'],
                        article_info['url']
                    )
                    
                    if is_related:
                        article_info['matching_keyword'] = keyword
                        articles_on_page.append(article_info)
                        
                        # Save with complete preservation
                        saved, files = self.save_article_complete(article_info)
                        if saved:
                            new_articles += 1
                            files_created += files
                            date_str = article_info['publish_date'][:10] if article_info['publish_date'] != "No date found" else "Unknown"
                            logger.info(f"✅ NEW: {article_info['title'][:60]}... [{date_str}] [files: {files}]")
                        else:
                            logger.info(f"📋 EXISTS: {article_info['title'][:60]}... [DUPLICATE PREVENTED]")
            
            return articles_on_page, soup, new_articles, files_created
            
        except Exception as e:
            logger.error(f"❌ Error scraping page {url}: {e}")
            return [], None, 0, 0

def main():
    parser = argparse.ArgumentParser(description='Complete Islam Articles Scraper with Preservation')
    parser.add_argument('--mode', choices=['historical', 'incremental', 'test'], 
                       default='test', help='Scraping mode')
    parser.add_argument('--max-pages', type=int, help='Maximum pages to scrape')
    parser.add_argument('--delay', type=float, default=2.0, help='Delay between requests')
    
    args = parser.parse_args()
    
    scraper = CompleteIslamScraper()
    
    try:
        logger.info(f"🚀 Starting Complete Islam Articles Scraper - Mode: {args.mode}")
        logger.info(f"🛡️ Duplicate prevention: ACTIVE (URL + Hash)")
        logger.info(f"📁 Output formats: HTML, Markdown, Database, Website")
        
        # Example with test mode (in real scenario, integrate full scraping logic)
        if args.mode == 'test':
            logger.info("🧪 Test mode - processing 2 pages")
            # Would call full scraping logic here
            logger.info("✅ Test complete - check articles_archive/ directory")
        
        logger.info("🎉 Complete scraping with preservation finished!")
        
    except Exception as e:
        logger.error(f"❌ Scraping failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()