#!/usr/bin/env python3
"""
Generate HTML, Markdown, and Website files from existing database
Use this to recreate all files locally after downloading the database
"""

import sys
import os
import sqlite3
from pathlib import Path
import argparse
import json

# Add parent directory to path to import our modules
sys.path.append(str(Path(__file__).parent.parent))

try:
    from enhanced_article_preservator import EnhancedArticlePreservator
except ImportError:
    print("❌ Could not import enhanced_article_preservator")
    print("Make sure you're running this from the repository root")
    sys.exit(1)

def generate_files_from_database(db_path="islam_articles.db", output_dir="articles_archive"):
    """Generate all files from an existing database"""
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found: {db_path}")
        print("Available files:")
        for file in os.listdir('.'):
            if file.endswith('.db'):
                print(f"   📄 {file}")
        return False
    
    print(f"🗃️  Using database: {db_path}")
    
    # Initialize preservator
    preservator = EnhancedArticlePreservator(output_dir=output_dir)
    preservator.db_path = Path(db_path).resolve()
    
    # Connect to database and get all articles
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT COUNT(*) FROM articles
    ''')
    total_count = cursor.fetchone()[0]
    
    if total_count == 0:
        print("❌ No articles found in database")
        return False
    
    print(f"📊 Found {total_count} articles in database")
    
    # Get all articles
    cursor.execute('''
        SELECT url, title, content_preview, full_content, 
               publish_date, publish_date_parsed, date_source,
               matching_keyword, scraped_at
        FROM articles 
        ORDER BY publish_date_parsed DESC
    ''')
    
    articles = cursor.fetchall()
    conn.close()
    
    print(f"🔄 Generating files for {len(articles)} articles...")
    
    html_count = 0
    md_count = 0
    
    # Generate files for each article
    for i, article_data in enumerate(articles, 1):
        url, title, content_preview, full_content, pub_date, parsed_date, date_source, keyword, scraped_at = article_data
        
        # Prepare article data structure
        article = {
            'url': url,
            'title': title,
            'content_preview': content_preview or '',
            'full_content': full_content or content_preview or '',
            'publish_date': pub_date or 'Unknown date',
            'publish_date_parsed': parsed_date,
            'date_source': date_source or 'database',
            'matching_keyword': keyword,
            'scraped_at': scraped_at,
            'word_count': len((full_content or content_preview or '').split())
        }
        
        # Generate HTML file
        html_path = preservator.save_as_html(article)
        if html_path:
            html_count += 1
        
        # Generate Markdown file
        md_path = preservator.save_as_markdown(article)
        if md_path:
            md_count += 1
        
        # Progress update
        if i % 10 == 0:
            print(f"   📄 Processed {i}/{len(articles)} articles...")
    
    print(f"✅ Generated {html_count} HTML files")
    print(f"✅ Generated {md_count} Markdown files")
    
    # Generate static website
    print("🌐 Generating static website...")
    website_path = preservator.generate_static_website()
    
    # Generate exports
    print("📊 Creating exports...")
    export_count = preservator.export_formats()
    
    print(f"\n🎉 File generation complete!")
    print(f"📁 Output directory: {output_dir}")
    print(f"🌐 Website: {website_path}")
    print(f"📄 Total files created: {html_count + md_count}")
    
    # Show directory structure
    print(f"\n📂 Generated structure:")
    output_path = Path(output_dir)
    for subdir in ['html_articles', 'markdown_articles', 'website', 'exports']:
        subdir_path = output_path / subdir
        if subdir_path.exists():
            file_count = len([f for f in subdir_path.rglob('*') if f.is_file()])
            print(f"   📁 {subdir}/  ({file_count} files)")
    
    print(f"\n🚀 Ready to use:")
    print(f"   📖 Open: {output_dir}/website/index.html")
    print(f"   📄 Browse: {output_dir}/html_articles/")
    print(f"   📝 Read: {output_dir}/markdown_articles/")
    
    return True

def main():
    parser = argparse.ArgumentParser(description='Generate all files from Islam articles database')
    parser.add_argument('--database', '-d', default='islam_articles.db', 
                       help='Path to SQLite database file')
    parser.add_argument('--output', '-o', default='articles_archive',
                       help='Output directory for generated files')
    parser.add_argument('--force', '-f', action='store_true',
                       help='Overwrite existing output directory')
    
    args = parser.parse_args()
    
    # Check if output directory exists
    if os.path.exists(args.output) and not args.force:
        response = input(f"Output directory '{args.output}' already exists. Overwrite? (y/N): ")
        if not response.lower().startswith('y'):
            print("Cancelled")
            return
    
    print("🚀 Islam Articles File Generator")
    print("=" * 40)
    print(f"📂 Database: {args.database}")
    print(f"📁 Output: {args.output}")
    print()
    
    success = generate_files_from_database(args.database, args.output)
    
    if success:
        print("\n✅ Success! All files generated.")
        print(f"📖 Open {args.output}/website/index.html to browse your archive")
    else:
        print("\n❌ Failed to generate files")
        sys.exit(1)

if __name__ == "__main__":
    main()