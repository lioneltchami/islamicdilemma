#!/usr/bin/env python3
"""
Enhanced Article Preservation System
Saves Islam articles in multiple readable formats with full content
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
import shutil

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EnhancedArticlePreservator:
    def __init__(self, base_url="https://maxshimbaministries.org", output_dir="articles_archive"):
        self.base_url = base_url
        self.output_dir = Path(output_dir)
        self.db_path = self.output_dir / "islam_articles.db"
        
        # Create directory structure
        self.setup_directories()
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; IslamArticlesPreservator/1.0)'
        })
        
        # Enhanced Islam-related keywords
        self.islam_keywords = [
            'islam', 'islamic', 'muslim', 'muslims', 'quran', 'quranic', 'koran',
            'muhammad', 'prophet muhammad', 'allah', 'hadith', 'jihad', 'sharia',
            'mosque', 'mecca', 'medina', 'caliphate', 'caliph', 'imam', 'sunni',
            'shia', 'shiite', 'sufi', 'sufism', 'ramadan', 'hajj', 'pilgrimage',
            'mujahideen', 'fatwa', 'ulema', 'madrasah', 'madrasa', 'kaaba', 'kabah',
            'sunnah', 'tafsir', 'ijma', 'ummah', 'shariah', 'halal', 'haram'
        ]
        
        # HTML to Markdown converter
        self.html2text = html2text.HTML2Text()
        self.html2text.ignore_links = False
        self.html2text.ignore_images = False
        self.html2text.body_width = 80
        
        self.setup_database()
        
    def setup_directories(self):
        """Create organized directory structure for different formats"""
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
        """Create enhanced SQLite database"""
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
                duration_seconds INTEGER
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info(f"✅ Database initialized: {self.db_path}")
    
    def url_exists(self, url):
        """Check if URL already exists with robust duplicate detection"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        url_hash = hashlib.md5(url.encode()).hexdigest()
        cursor.execute("SELECT id FROM articles WHERE url = ? OR url_hash = ?", (url, url_hash))
        exists = cursor.fetchone() is not None
        
        conn.close()
        return exists
    
    def sanitize_filename(self, text):
        """Create safe filename from text"""
        # Remove or replace problematic characters
        safe_text = re.sub(r'[^\w\s-]', '', text)
        safe_text = re.sub(r'[-\s]+', '-', safe_text)
        return safe_text.strip('-')[:100]  # Limit length
    
    def fetch_full_article_content(self, article_url):
        """Fetch the complete article content from individual article page"""
        try:
            logger.info(f"📄 Fetching full content: {article_url}")
            response = self.session.get(article_url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find the main article content
            content_selectors = [
                '.post-body',
                '.entry-content', 
                '.content',
                'article',
                '.post',
                '[class*="content"]'
            ]
            
            article_content = None
            for selector in content_selectors:
                article_content = soup.select_one(selector)
                if article_content:
                    break
            
            if not article_content:
                # Fallback: try to find content in the body
                article_content = soup.find('body')
            
            if article_content:
                # Clean up the content - remove navigation, ads, etc.
                for unwanted in article_content.select('.navigation, .sidebar, .footer, .header, .comments, script, style'):
                    unwanted.decompose()
                
                # Get both HTML and text content
                full_html = str(article_content)
                full_text = article_content.get_text(strip=True)
                
                return {
                    'html': full_html,
                    'text': full_text,
                    'success': True
                }
            else:
                logger.warning(f"⚠️ Could not find article content in {article_url}")
                return {'html': '', 'text': '', 'success': False}
                
        except Exception as e:
            logger.error(f"❌ Error fetching full content for {article_url}: {e}")
            return {'html': '', 'text': '', 'success': False}
    
    def save_as_html(self, article_data):
        """Save article as individual HTML file with styling"""
        try:
            # Create filename
            date_str = article_data.get('publish_date_parsed', '').split('T')[0] if article_data.get('publish_date_parsed') else 'unknown-date'
            filename = f"{date_str}_{self.sanitize_filename(article_data['title'])}.html"
            filepath = self.output_dir / "html_articles" / filename
            
            # Create HTML template
            html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{article_data['title']}</title>
    <style>
        body {{
            font-family: Georgia, serif;
            line-height: 1.6;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f9f9f9;
        }}
        .article {{
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .header {{
            border-bottom: 2px solid #333;
            margin-bottom: 30px;
            padding-bottom: 20px;
        }}
        .title {{
            color: #333;
            font-size: 2em;
            margin-bottom: 10px;
        }}
        .meta {{
            color: #666;
            font-size: 0.9em;
            margin-bottom: 10px;
        }}
        .content {{
            color: #444;
            font-size: 1.1em;
        }}
        .footer {{
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            color: #666;
            font-size: 0.9em;
        }}
        a {{ color: #0066cc; }}
        blockquote {{
            border-left: 4px solid #ddd;
            margin: 20px 0;
            padding-left: 20px;
            font-style: italic;
        }}
    </style>
</head>
<body>
    <div class="article">
        <div class="header">
            <h1 class="title">{article_data['title']}</h1>
            <div class="meta">
                📅 Published: {article_data.get('publish_date', 'Unknown date')}<br>
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
            <p>This article was automatically archived from the Max Shimba Ministries blog as part of an Islam-related articles collection.</p>
            <p>Date extraction method: {article_data.get('date_source', 'unknown')}</p>
        </div>
    </div>
</body>
</html>"""
            
            # Write HTML file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"✅ HTML saved: {filepath.name}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"❌ Error saving HTML: {e}")
            return None
    
    def save_as_markdown(self, article_data):
        """Save article as clean Markdown file"""
        try:
            # Create filename
            date_str = article_data.get('publish_date_parsed', '').split('T')[0] if article_data.get('publish_date_parsed') else 'unknown-date'
            filename = f"{date_str}_{self.sanitize_filename(article_data['title'])}.md"
            filepath = self.output_dir / "markdown_articles" / filename
            
            # Convert HTML to Markdown if available, otherwise use text
            if article_data.get('full_html'):
                markdown_content = self.html2text.handle(article_data['full_html'])
            else:
                markdown_content = article_data.get('full_content', article_data.get('content_preview', ''))
            
            # Create Markdown with metadata
            md_content = f"""# {article_data['title']}

**Publication Date:** {article_data.get('publish_date', 'Unknown date')}  
**Original URL:** {article_data['url']}  
**Keyword Match:** {article_data.get('matching_keyword', 'N/A')}  
**Word Count:** {article_data.get('word_count', 0)}  
**Archived:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Date Source:** {article_data.get('date_source', 'unknown')}

---

{markdown_content}

---

*This article was automatically archived from the Max Shimba Ministries blog as part of an Islam-related articles collection.*
"""
            
            # Write Markdown file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(md_content)
            
            logger.info(f"✅ Markdown saved: {filepath.name}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"❌ Error saving Markdown: {e}")
            return None
    
    def save_article_enhanced(self, article_data):
        """Save article to database and create files"""
        if self.url_exists(article_data['url']):
            return False, 0  # Already exists
        
        # Fetch full article content
        full_content = self.fetch_full_article_content(article_data['url'])
        if full_content['success']:
            article_data['full_html'] = full_content['html']
            article_data['full_content'] = full_content['text']
        
        # Save as HTML file
        html_path = self.save_as_html(article_data)
        
        # Save as Markdown file  
        markdown_path = self.save_as_markdown(article_data)
        
        # Update article data with file paths
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
    
    def generate_static_website(self):
        """Generate a browsable static website with all articles"""
        logger.info("🌐 Generating static website...")
        
        # Create CSS file
        css_content = """
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        }
        .header {
            text-align: center;
            border-bottom: 3px solid #333;
            margin-bottom: 30px;
            padding-bottom: 20px;
        }
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .stat-card {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }
        .stat-number {
            font-size: 2em;
            font-weight: bold;
            color: #0066cc;
        }
        .articles-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
            gap: 20px;
        }
        .article-card {
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 20px;
            background: white;
            transition: transform 0.2s;
        }
        .article-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        .article-title {
            font-size: 1.2em;
            font-weight: bold;
            margin-bottom: 10px;
        }
        .article-meta {
            color: #666;
            font-size: 0.9em;
            margin-bottom: 10px;
        }
        .article-preview {
            color: #444;
            margin-bottom: 15px;
        }
        .article-links {
            display: flex;
            gap: 10px;
        }
        .btn {
            padding: 8px 15px;
            text-decoration: none;
            border-radius: 5px;
            font-size: 0.9em;
            font-weight: bold;
        }
        .btn-html {
            background: #e7f3ff;
            color: #0066cc;
        }
        .btn-markdown {
            background: #f0f8e7;
            color: #28a745;
        }
        .btn-original {
            background: #fff3cd;
            color: #856404;
        }
        """
        
        css_path = self.output_dir / "website" / "css" / "style.css"
        with open(css_path, 'w') as f:
            f.write(css_content)
        
        # Get all articles from database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT url, title, content_preview, publish_date, publish_date_parsed,
                   matching_keyword, word_count, html_file_path, markdown_file_path
            FROM articles 
            ORDER BY publish_date_parsed DESC, scraped_at DESC
        ''')
        
        articles = cursor.fetchall()
        
        # Generate article cards HTML
        article_cards = []
        for article in articles:
            url, title, preview, pub_date, parsed_date, keyword, word_count, html_path, md_path = article
            
            # Create relative paths
            html_rel = f"../html_articles/{Path(html_path).name}" if html_path else None
            md_rel = f"../markdown_articles/{Path(md_path).name}" if md_path else None
            
            card_html = f"""
            <div class="article-card">
                <div class="article-title">{title}</div>
                <div class="article-meta">
                    📅 {pub_date} | 🏷️ {keyword} | 📝 {word_count} words
                </div>
                <div class="article-preview">
                    {preview[:200]}...
                </div>
                <div class="article-links">
                    {f'<a href="{html_rel}" class="btn btn-html">📄 HTML</a>' if html_rel else ''}
                    {f'<a href="{md_rel}" class="btn btn-markdown">📝 Markdown</a>' if md_rel else ''}
                    <a href="{url}" target="_blank" class="btn btn-original">🔗 Original</a>
                </div>
            </div>
            """
            article_cards.append(card_html)
        
        # Get statistics
        cursor.execute('SELECT COUNT(*) FROM articles')
        total_articles = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(DISTINCT matching_keyword) FROM articles')
        total_keywords = cursor.fetchone()[0]
        
        cursor.execute('SELECT SUM(word_count) FROM articles')
        total_words = cursor.fetchone()[0] or 0
        
        conn.close()
        
        # Generate index.html
        index_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Islam Articles Archive - Max Shimba Ministries</title>
    <link rel="stylesheet" href="css/style.css">
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🕌 Islam Articles Archive</h1>
            <p>Complete collection of Islam-related articles from Max Shimba Ministries</p>
            <p><em>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</em></p>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-number">{total_articles}</div>
                <div>Total Articles</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{total_keywords}</div>
                <div>Keywords Matched</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{total_words:,}</div>
                <div>Total Words</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{len([a for a in articles if a[7]])}</div>
                <div>HTML Files</div>
            </div>
        </div>
        
        <div class="articles-grid">
            {''.join(article_cards)}
        </div>
    </div>
</body>
</html>"""
        
        index_path = self.output_dir / "website" / "index.html"
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(index_html)
        
        logger.info(f"✅ Static website generated: {index_path}")
        return str(index_path)
    
    def export_formats(self):
        """Export articles in various formats"""
        logger.info("📊 Exporting in multiple formats...")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Export detailed JSON
        cursor.execute('''
            SELECT url, title, content_preview, full_content, publish_date, 
                   publish_date_parsed, date_source, matching_keyword, word_count,
                   html_file_path, markdown_file_path, scraped_at
            FROM articles 
            ORDER BY publish_date_parsed DESC
        ''')
        
        articles = []
        for row in cursor.fetchall():
            articles.append({
                'url': row[0],
                'title': row[1],
                'content_preview': row[2],
                'full_content': row[3],
                'publish_date': row[4],
                'publish_date_parsed': row[5],
                'date_source': row[6],
                'matching_keyword': row[7],
                'word_count': row[8],
                'html_file_path': row[9],
                'markdown_file_path': row[10],
                'scraped_at': row[11]
            })
        
        # Save detailed JSON
        json_path = self.output_dir / "exports" / "complete_articles.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(articles, f, indent=2, ensure_ascii=False)
        
        # Save CSV for analysis
        import csv
        csv_path = self.output_dir / "exports" / "articles_metadata.csv"
        with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['title', 'url', 'publish_date', 'matching_keyword', 'word_count', 'html_file', 'markdown_file']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for article in articles:
                writer.writerow({
                    'title': article['title'],
                    'url': article['url'],
                    'publish_date': article['publish_date'],
                    'matching_keyword': article['matching_keyword'],
                    'word_count': article['word_count'],
                    'html_file': Path(article['html_file_path']).name if article['html_file_path'] else '',
                    'markdown_file': Path(article['markdown_file_path']).name if article['markdown_file_path'] else ''
                })
        
        conn.close()
        
        logger.info(f"✅ Exports complete: {json_path}, {csv_path}")
        return len(articles)

def main():
    parser = argparse.ArgumentParser(description='Enhanced Article Preservation System')
    parser.add_argument('--mode', choices=['test', 'incremental', 'historical'], 
                       default='test', help='Scraping mode')
    parser.add_argument('--max-pages', type=int, default=2, help='Maximum pages to scrape')
    parser.add_argument('--delay', type=float, default=2.0, help='Delay between requests')
    
    args = parser.parse_args()
    
    preservator = EnhancedArticlePreservator()
    
    logger.info(f"🚀 Starting Enhanced Article Preservation - Mode: {args.mode}")
    
    # For demonstration, let's use the existing articles from the database
    # In a real scenario, you'd integrate this with the scraping logic
    
    # Generate website and exports
    website_path = preservator.generate_static_website()
    export_count = preservator.export_formats()
    
    logger.info("🎉 Enhanced preservation complete!")
    logger.info(f"📄 Website: {website_path}")
    logger.info(f"📊 Articles exported: {export_count}")
    logger.info(f"📁 All files in: {preservator.output_dir}")

if __name__ == "__main__":
    main()