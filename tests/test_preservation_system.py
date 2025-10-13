#!/usr/bin/env python3
"""
Test script for Enhanced Article Preservation System
Demonstrates creating individual files from existing database articles
"""

import sqlite3
import sys
import os
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from enhanced_article_preservator import EnhancedArticlePreservator

def test_with_existing_articles():
    """Test the preservation system with existing articles"""
    
    # Check if we have existing articles
    if not os.path.exists('islam_articles.db'):
        print("❌ No existing database found. Please run the scraper first.")
        return
    
    print("🧪 Testing Enhanced Article Preservation System")
    print("=" * 50)
    
    # Initialize the preservator
    preservator = EnhancedArticlePreservator(output_dir="enhanced_articles_test")
    
    # Get existing articles
    conn = sqlite3.connect('islam_articles.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT url, title, content_preview, publish_date, 
               matching_keyword, scraped_at
        FROM articles 
        LIMIT 3
    ''')
    
    existing_articles = cursor.fetchall()
    conn.close()
    
    if not existing_articles:
        print("❌ No articles found in existing database")
        return
    
    print(f"📊 Found {len(existing_articles)} articles to test with")
    
    # Process each article
    files_created = 0
    for url, title, content, pub_date, keyword, scraped_at in existing_articles:
        print(f"\n📄 Processing: {title[:50]}...")
        
        # Create article data structure
        article_data = {
            'url': url,
            'title': title,
            'content_preview': content,
            'full_content': content,  # Using preview as full content for demo
            'publish_date': pub_date,
            'publish_date_parsed': '2025-10-06T00:00:00',  # Demo date
            'date_source': 'demo',
            'matching_keyword': keyword,
            'scraped_at': scraped_at,
            'word_count': len(content.split()) if content else 0
        }
        
        # Save HTML file
        html_path = preservator.save_as_html(article_data)
        if html_path:
            files_created += 1
        
        # Save Markdown file
        md_path = preservator.save_as_markdown(article_data)
        if md_path:
            files_created += 1
    
    print(f"\n✅ Created {files_created} individual files")
    
    # Generate static website
    print("\n🌐 Generating static website...")
    website_path = preservator.generate_static_website()
    
    # Generate exports
    print("\n📊 Creating exports...")
    export_count = preservator.export_formats()
    
    print(f"\n🎉 Test complete!")
    print(f"📁 Output directory: {preservator.output_dir}")
    print(f"🌐 Website: {website_path}")
    print(f"📊 Articles processed: {export_count}")
    
    # Show directory structure
    print(f"\n📂 Directory structure created:")
    for root, dirs, files in os.walk(preservator.output_dir):
        level = root.replace(str(preservator.output_dir), '').count(os.sep)
        indent = ' ' * 2 * level
        print(f"{indent}{os.path.basename(root)}/")
        subindent = ' ' * 2 * (level + 1)
        for file in files[:5]:  # Show first 5 files in each directory
            print(f"{subindent}{file}")
        if len(files) > 5:
            print(f"{subindent}... and {len(files)-5} more files")

if __name__ == "__main__":
    test_with_existing_articles()