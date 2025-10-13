# 🔧 Scraping Modes & Delays: Complete Technical Guide

## 🎯 **What Are Scraping Modes?**

Scraping modes control **HOW AGGRESSIVE** and **HOW COMPREHENSIVE** the scraper operates. Each mode has different goals, page limits, and stopping conditions.

---

## 📊 **Available Scraping Modes Explained**

### **1. `incremental` Mode (Default)**
```yaml
Purpose: Quick check for NEW articles only
Pages: 3-5 pages maximum
Duration: 1-3 minutes
When to use: Daily automated checks
Stopping condition: When no new articles found OR page limit reached
```

**How it works:**
```python
# Incremental Mode Logic:
current_url = "https://maxshimbaministries.org/"  # Start with newest
page_count = 0
max_pages = 5  # Limited scope

while current_url and page_count < max_pages:
    articles = scrape_page(current_url)
    new_articles_found = 0
    
    for article in articles:
        if not already_in_database(article.url):  # Check for duplicates
            save_article(article)
            new_articles_found += 1
        else:
            print("📋 EXISTS: Article already in database")
    
    # SMART STOPPING: If no new articles on first 2 pages, probably caught up
    if page_count >= 2 and total_new_articles == 0:
        print("✅ No new articles found - database is up to date!")
        break
    
    page_count += 1
    current_url = find_next_page(soup)
```

**Example Output:**
```
🔄 Starting INCREMENTAL scrape (max 5 pages)
📄 Page 1: Found 6 Islam articles
   ✅ NEW: Latest Article [2025-10-12]
   ✅ NEW: Recent Study [2025-10-10]
   📋 EXISTS: Older Article [already in database]

📄 Page 2: Found 4 Islam articles  
   📋 EXISTS: All articles already in database
   
✅ No new articles found - database is up to date!
Result: 2 new articles, 2 minutes duration
```

---

### **2. `historical` Mode**
```yaml
Purpose: Get MANY articles, but with reasonable limits
Pages: 20-100 pages (configurable)
Duration: 20 minutes - 2 hours
When to use: Weekly comprehensive updates
Stopping condition: Page limit reached OR no more pages
```

**How it works:**
```python
# Historical Mode Logic:
max_pages = 50  # Reasonable limit for weekly runs
page_count = 0

while current_url and page_count < max_pages:
    articles = scrape_page(current_url)
    
    # Save ALL Islam-related articles found (even if duplicates detected)
    for article in articles:
        if is_islam_related(article):
            save_result = save_article(article)  # Database prevents duplicates
            if save_result:
                print(f"✅ NEW: {article.title}")
            else:
                print(f"📋 EXISTS: {article.title}")
    
    page_count += 1
    current_url = find_next_page(soup)
    
    # Progress update every 10 pages
    if page_count % 10 == 0:
        print(f"📊 Progress: {page_count} pages, {new_articles} new articles")
```

**Example Output:**
```
🚀 Starting HISTORICAL scrape (max 50 pages)
📄 Page 1-10: 23 new articles found (recent months)
📄 Page 11-20: 18 new articles found (mid-2025)
📄 Page 21-30: 15 new articles found (early 2025)
📄 Page 31-40: 12 new articles found (late 2024)
📄 Page 41-50: 8 new articles found (mid-2024)

Result: 76 new articles spanning 18 months, 1.5 hours duration
```

---

### **3. `full_historical` Mode**
```yaml
Purpose: Get EVERYTHING back to 2015 (complete archive)
Pages: UNLIMITED (until pagination ends)
Duration: 2-6 hours
When to use: Initial setup or complete rebuild
Stopping condition: No more pages exist OR critical error
```

**How it works:**
```python
# Full Historical Mode Logic:
max_pages = 999999  # Effectively unlimited
page_count = 0

print("🚀 Starting FULL HISTORICAL scrape (unlimited pages)")
print("⚠️  This will take several hours to get ALL articles since 2015")

while current_url and page_count < max_pages:
    articles = scrape_page(current_url)
    
    # Process every single article found
    for article in articles:
        if is_islam_related(article):
            save_article(article)  # Duplicates automatically handled
    
    # Find next page (following Blogger pagination)
    next_url = find_next_page(soup)
    if not next_url or next_url == current_url:
        print("🔚 Reached the end of pagination - got everything!")
        break
    
    current_url = next_url
    page_count += 1
    
    # Backup progress every 25 pages (for very long runs)
    if page_count % 25 == 0:
        create_backup(f"backup_after_{page_count}_pages.json")
```

**Example Output:**
```
🚀 Starting FULL HISTORICAL scrape (unlimited pages)
⚠️  This will take several hours to get ALL articles since 2015

📄 Page 1-25: October 2025 articles (15 new Islam articles)
📄 Page 26-50: August-September 2025 (22 new)
📄 Page 51-75: June-July 2025 (18 new)
...
📄 Page 126-150: 2022 articles (31 new)
📄 Page 151-175: 2021 articles (28 new)
...
📄 Page 276-300: 2016-2017 articles (19 new)
📄 Page 301-325: 2015-2016 articles (12 new)
📄 Page 326: Early 2015 articles (3 new)

🔚 Reached the end of pagination - got everything!
Result: 287 Islam articles spanning 2015-2025, 4.2 hours duration
```

---

### **4. `weekly_full` Mode**
```yaml
Purpose: Comprehensive weekly backup
Pages: 30-75 pages (medium scope)
Duration: 30-90 minutes  
When to use: Sunday maintenance runs
Stopping condition: Page limit OR reasonable time limit
```

---

## ⏱️ **What Is Delay & Why It's Critical**

**Delay = Time to wait between HTTP requests to the target website**

### **🚨 Why Delay Is Essential:**

#### **1. Server Respect & Ethics**
```python
# Without delay (BAD):
for page in pages:
    response = requests.get(page)  # IMMEDIATE REQUEST
    # Server gets hammered with rapid-fire requests
    
# With delay (GOOD):
for page in pages:
    response = requests.get(page)
    time.sleep(delay)  # RESPECTFUL PAUSE
```

#### **2. Avoiding Rate Limits**
```
❌ No Delay → Server Response:
Request 1: 200 OK
Request 2: 200 OK  
Request 3: 200 OK
Request 4: 429 Too Many Requests (BLOCKED!)
Request 5: 403 Forbidden (IP BANNED!)

✅ With Delay → Server Response:
Request 1: 200 OK ... wait 2 seconds ...
Request 2: 200 OK ... wait 2 seconds ...
Request 3: 200 OK ... wait 2 seconds ...
All requests: 200 OK (SMOOTH OPERATION)
```

#### **3. Server Load Consideration**
```
Max Shimba Ministries server specs (typical blog):
├── Shared hosting or small VPS
├── Limited concurrent connections
├── Likely serves regular visitors too
└── Not built for high-volume scraping

Our approach:
├── 2-3 second delays = respectful
├── Server can handle other visitors
├── We get our data without disruption
└── Sustainable long-term operation
```

---

## 🔢 **Delay Values & Their Impact**

### **Delay Comparison Table:**

| Delay | Requests/Min | Impact | Use Case | Risk Level |
|-------|--------------|---------|-----------|------------|
| 0s | 60+ | ⚡ Fastest | 🚨 Emergency only | 🔴 High risk |
| 1s | 60 | 🏃 Fast | Testing only | 🟠 Medium risk |
| 2s | 30 | ⚖️ Balanced | ✅ Default production | 🟢 Low risk |
| 3s | 20 | 🐌 Slower | Historical runs | 🟢 Very safe |
| 5s | 12 | 🚶 Conservative | Maximum politeness | 🟢 Ultra safe |

### **Real-World Time Calculations:**

#### **Incremental Mode (5 pages, 2s delay):**
```
Pages: 5
Articles per page: ~8-12
Requests: 5 page requests
Time: (5 × 2s delays) + (5 × 1s request time) = 15 seconds
Total duration: ~1-2 minutes including processing
```

#### **Historical Mode (50 pages, 2s delay):**
```  
Pages: 50
Articles per page: ~8-12
Requests: 50 page requests
Time: (50 × 2s delays) + (50 × 1s request time) = 150 seconds = 2.5 minutes
Total duration: ~20-30 minutes including processing
```

#### **Full Historical Mode (300 pages, 3s delay):**
```
Pages: 300 (estimated for complete history)
Articles per page: ~8-12
Requests: 300 page requests  
Time: (300 × 3s delays) + (300 × 1s request time) = 1200 seconds = 20 minutes
Total duration: ~3-4 hours including processing and file creation
```

---

## ⚙️ **How Delays Are Configured**

### **In GitHub Actions Workflow:**
```yaml
# Different delays for different schedules:
- cron: '0 */6 * * *'     # Every 6 hours
  delay: 1                # Fast incremental (low server load time)
  
- cron: '0 6 * * *'       # Daily at 6 AM  
  delay: 2                # Standard balanced approach
  
- cron: '0 2 * * 0'       # Weekly on Sunday
  delay: 3                # Conservative for long runs
```

### **Manual Control:**
```bash
# Fast test run
python scraper.py --mode incremental --delay 1

# Standard run  
python scraper.py --mode historical --delay 2

# Conservative historical
python scraper.py --mode full_historical --delay 3

# Maximum politeness
python scraper.py --mode full_historical --delay 5
```

### **In Code Implementation:**
```python
def scrape_with_delay(pages, delay):
    for page_url in pages:
        print(f"🔍 Scraping: {page_url}")
        
        # Make request
        response = requests.get(page_url)
        
        # Process content
        articles = parse_articles(response.content)
        save_articles(articles)
        
        # RESPECTFUL DELAY
        print(f"⏱️ Waiting {delay} seconds...")
        time.sleep(delay)
        
        # Continue to next page
```

---

## 🎯 **Mode Selection Strategy**

### **When to Use Each Mode:**

#### **Use `incremental` when:**
- ✅ Checking for new articles (daily)
- ✅ You have an existing database
- ✅ You want quick updates (1-3 minutes)
- ✅ Server load should be minimal

#### **Use `historical` when:**
- ✅ Weekly comprehensive updates
- ✅ You suspect you missed some articles
- ✅ You want to go back a few months/years
- ✅ Reasonable time budget (30-90 minutes)

#### **Use `full_historical` when:**
- ✅ First-time setup (getting everything)
- ✅ Complete database rebuild
- ✅ Research project needing ALL articles
- ✅ You have 3-6 hours available

---

## 🛡️ **Ethical & Technical Safeguards**

### **Built-in Protections:**
```python
# 1. Robots.txt Compliance
def check_robots_txt():
    robots_url = urljoin(base_url, '/robots.txt')
    response = requests.get(robots_url)
    # Parse and respect robots.txt rules

# 2. Request Rate Limiting  
def respectful_request(url, delay):
    response = requests.get(url, timeout=30)
    time.sleep(delay)  # MANDATORY DELAY
    return response

# 3. Error Handling & Backoff
def safe_scrape(url):
    try:
        response = requests.get(url)
        if response.status_code == 429:  # Too Many Requests
            print("⚠️ Rate limited, increasing delay...")
            time.sleep(delay * 2)  # Double the delay
    except requests.RequestException as e:
        print(f"❌ Error: {e}, skipping this page")

# 4. Progress Monitoring
def monitor_progress():
    if page_count % 10 == 0:
        print(f"📊 Progress: {page_count} pages completed")
        create_checkpoint()  # Save progress
```

---

## 📈 **Performance vs. Politeness Balance**

### **Optimization Philosophy:**
```
🎯 Our Approach: "Fast Enough, Respectful Always"

├── Speed: Get articles efficiently
├── Respect: Never overload the server  
├── Reliability: Handle errors gracefully
├── Sustainability: Can run for years
└── Ethics: Follow web scraping best practices
```

### **Real-World Impact:**
```
Scenario: Full historical scrape (300 pages)

With 1s delay:
├── Duration: ~2 hours
├── Server impact: Medium
├── Risk: Possible rate limiting
└── Sustainability: Questionable

With 2s delay (our default):
├── Duration: ~3 hours  
├── Server impact: Low
├── Risk: Very low
└── Sustainability: Excellent ✅

With 3s delay (conservative):
├── Duration: ~4 hours
├── Server impact: Minimal
├── Risk: Negligible  
└── Sustainability: Perfect ✅
```

---

## 🎛️ **Practical Usage Examples**

### **GitHub Actions Manual Trigger:**
```yaml
# In GitHub Actions interface:
Scraping Mode: [incremental ▼]
Max Pages: [5]
Delay: [2.0] seconds

# What this means:
- Check recent articles only
- Stop after 5 pages or when caught up
- Wait 2 seconds between page requests
- Total time: ~2-5 minutes
```

### **Command Line Usage:**
```bash
# Quick daily check
python scraper.py --mode incremental --delay 2

# Weekly comprehensive  
python scraper.py --mode historical --max-pages 50 --delay 2

# Complete archive (first time)
python scraper.py --mode full_historical --delay 3

# Ultra-conservative research run
python scraper.py --mode full_historical --delay 5 --max-pages 1000
```

---

## 🔍 **Bottom Line Understanding**

### **Scraping Mode:**
- **Controls SCOPE**: How much to scrape
- **Controls STOPPING**: When to stop scraping  
- **Controls PURPOSE**: What we're trying to achieve
- **Controls TIME**: How long the operation takes

### **Delay:**
- **Ensures ETHICS**: Respectful to server
- **Prevents BLOCKING**: Avoids rate limits
- **Enables SUSTAINABILITY**: Can run forever
- **Balances SPEED**: Fast enough, polite always

### **The Sweet Spot:**
- **`incremental` + 2s delay**: Perfect for daily automation
- **`historical` + 2s delay**: Great for weekly updates  
- **`full_historical` + 3s delay**: Ideal for complete archives

**Result: Professional, ethical, sustainable scraping that gets every Islam article without overwhelming the server!** 🎯✅