#!/usr/bin/env python3
"""
Enhanced script to scrape YouTube podcast chart data from Wayback Machine URLs
with robust parsing and debugging capabilities.
"""

import requests
from bs4 import BeautifulSoup
import json
import time
from datetime import datetime
import re

def debug_page_content(soup, url):
    """Debug function to analyze the page structure"""
    print(f"\n🔍 DEBUG: Analyzing page structure for {url}")
    
    # Check if we got the actual page or an error
    title = soup.find('title')
    if title:
        print(f"Page title: {title.get_text().strip()}")
    
    # Look for common YouTube elements
    youtube_indicators = [
        'ytd-', 'yt-', 'youtube', 'charts', 'podcast', 'playlist'
    ]
    
    found_elements = []
    for indicator in youtube_indicators:
        elements = soup.find_all(attrs={'class': re.compile(indicator, re.I)})
        if elements:
            found_elements.append(f"{indicator}: {len(elements)} elements")
    
    if found_elements:
        print(f"YouTube-related elements found: {', '.join(found_elements)}")
    else:
        print("❌ No obvious YouTube elements found")
    
    # Check for any list-like structures
    lists = soup.find_all(['ul', 'ol', 'div'], class_=re.compile(r'(list|item|entry|chart|rank)', re.I))
    if lists:
        print(f"Found {len(lists)} potential list structures")
    
    # Look for any text mentioning podcasts or rankings
    text = soup.get_text().lower()
    if 'podcast' in text:
        print("✅ 'podcast' text found in page")
    if 'chart' in text:
        print("✅ 'chart' text found in page")
    if 'rank' in text:
        print("✅ 'rank' text found in page")

def try_multiple_selectors(soup):
    """Try multiple selector strategies to find podcast entries"""
    
    # Strategy 1: Look for specific YouTube chart selectors
    selectors = [
        # YouTube-specific selectors
        'ytd-rich-item-renderer',
        'ytd-video-renderer',
        'ytd-playlist-renderer',
        '[data-testid*="chart"]',
        '[data-testid*="video"]',
        '[data-testid*="playlist"]',
        
        # Generic chart selectors
        '[class*="chart-item"]',
        '[class*="chart-entry"]',
        '[class*="ranking-item"]',
        '[class*="list-item"]',
        
        # Container selectors that might hold chart items
        '[id*="contents"] > *',
        '[class*="contents"] > *',
        '[class*="items"] > *',
        
        # Look for anything with numbers (ranks)
        'li:contains("1")',
        'div:contains("#1")',
        
        # Broad selectors for any structured content
        'article', 'section[class*="item"]', 'div[class*="item"]'
    ]
    
    for selector in selectors:
        try:
            elements = soup.select(selector)
            if elements and len(elements) > 10:  # Likely a list of chart items
                print(f"✅ Found {len(elements)} elements with selector: {selector}")
                return elements, selector
            elif elements:
                print(f"Found {len(elements)} elements with selector: {selector} (may be too few)")
        except Exception as e:
            print(f"Error with selector '{selector}': {e}")
    
    return [], None

def extract_podcast_info_flexible(element, rank):
    """Flexible extraction of podcast information from various element types"""
    
    # Try to find text that looks like a podcast/channel name
    name = None
    
    # Look for text in various elements
    text_selectors = ['h3', 'h2', 'h4', 'a', 'span[class*="title"]', '[id*="title"]']
    for sel in text_selectors:
        elem = element.select_one(sel)
        if elem:
            text = elem.get_text(strip=True)
            if text and len(text) > 2 and len(text) < 100:  # Reasonable name length
                name = text
                break
    
    # If no specific title found, try the main text content
    if not name:
        name = element.get_text(strip=True)
        # Clean up the text
        if name:
            # Remove extra whitespace and take first reasonable part
            name = ' '.join(name.split())
            if len(name) > 100:
                name = name[:97] + "..."
    
    # Try to find thumbnail
    thumbnail_url = ""
    img = element.find('img')
    if img:
        thumbnail_url = img.get('src', '') or img.get('data-src', '') or img.get('data-thumb', '')
        if thumbnail_url and not thumbnail_url.startswith('http'):
            if thumbnail_url.startswith('//'):
                thumbnail_url = 'https:' + thumbnail_url
            elif thumbnail_url.startswith('/'):
                thumbnail_url = 'https://www.youtube.com' + thumbnail_url
    
    # Try to find URL
    channel_url = ""
    link = element.find('a', href=True)
    if link:
        href = link['href']
        if href:
            if href.startswith('/'):
                channel_url = 'https://www.youtube.com' + href
            elif href.startswith('http'):
                channel_url = href
    
    return {
        "name": name or f"Unknown Podcast {rank}",
        "thumbnail": thumbnail_url,
        "url": channel_url
    }

def scrape_wayback_chart(wayback_url, chart_week_range):
    """
    Enhanced scraper for podcast chart data from a Wayback Machine URL
    """
    print(f"\n🚀 Scraping: {wayback_url}")
    print(f"📅 Week range: {chart_week_range}")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
    }
    
    try:
        response = requests.get(wayback_url, headers=headers, timeout=30)
        response.raise_for_status()
        
        print(f"📥 Response status: {response.status_code}")
        print(f"📄 Content length: {len(response.content)} bytes")
        
        soup = BeautifulSoup(response.content, 'lxml')  # Try lxml parser for better performance
        
        # Debug the page content
        debug_page_content(soup, wayback_url)
        
        # Try multiple selector strategies
        elements, successful_selector = try_multiple_selectors(soup)
        
        if not elements:
            print("❌ No suitable elements found with any selector")
            
            # Last resort: look for any structured content with numbers
            print("\n🔍 Last resort: Looking for any numbered content...")
            all_text = soup.get_text()
            lines = [line.strip() for line in all_text.split('\n') if line.strip()]
            
            # Look for lines that might contain rankings
            potential_entries = []
            for i, line in enumerate(lines):
                if re.search(r'^[#]?[1-9]\d*[\.\):\s]', line) and len(line) > 5:
                    potential_entries.append((i, line))
            
            if potential_entries:
                print(f"Found {len(potential_entries)} potential ranked entries in text")
                for i, (line_num, line) in enumerate(potential_entries[:10]):
                    print(f"  {i+1}: {line[:80]}...")
            
            return []
        
        print(f"🎯 Processing {len(elements)} elements found with: {successful_selector}")
        
        podcast_entries = []
        
        for i, element in enumerate(elements[:100], 1):  # Process up to 100 entries
            try:
                info = extract_podcast_info_flexible(element, i)
                
                if info['name'] and len(info['name']) > 2:
                    podcast_entry = {
                        "Name": info['name'],
                        "Chart Date": chart_week_range,
                        "Rank": str(i),
                        "Channel URL": info['url'],
                        "Thumbnail URL": info['thumbnail']
                    }
                    
                    podcast_entries.append(podcast_entry)
                    print(f"  #{i}: {info['name'][:50]}...")
                
                # Stop if we have a good number of entries
                if len(podcast_entries) >= 100:
                    break
                    
            except Exception as e:
                print(f"⚠️  Error processing element {i}: {e}")
                continue
        
        print(f"✅ Successfully extracted {len(podcast_entries)} podcast entries")
        return podcast_entries
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
        return []
    except Exception as e:
        print(f"❌ Parsing error: {e}")
        return []

def scrape_multiple_wayback_urls(wayback_urls):
    """
    Scrape multiple Wayback Machine URLs and combine the data
    """
    all_entries = []
    
    for i, (wayback_url, chart_week_range) in enumerate(wayback_urls, 1):
        print(f"\n{'='*60}")
        print(f"📊 SCRAPING {i}/{len(wayback_urls)}")
        print(f"{'='*60}")
        
        entries = scrape_wayback_chart(wayback_url, chart_week_range)
        all_entries.extend(entries)
        
        # Be respectful to the Wayback Machine servers
        if i < len(wayback_urls):
            print("⏳ Waiting 3 seconds before next request...")
            time.sleep(3)
    
    return all_entries

def save_to_json(data, filename="wayback_historical_data.json"):
    """Save the scraped data to a JSON file"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Data saved to {filename}")
        return True
    except Exception as e:
        print(f"❌ Error saving to JSON: {e}")
        return False

def main():
    """Main function to run the enhanced scraping process"""
    
    print("🎯 Enhanced YouTube Podcast Chart Wayback Scraper")
    print("=" * 60)
    
    # Add your Wayback Machine URLs here
    wayback_urls = [
        ("https://web.archive.org/web/20250515184935/https://charts.youtube.com/podcasts", "May 5 - May 11, 2025"),
        ("https://web.archive.org/web/20250521211257/https://charts.youtube.com/podcasts", "May 12 - May 18, 2025"),
    ]
    
    if not wayback_urls:
        print("❌ Please add your Wayback Machine URLs to the wayback_urls list")
        return
    
    print(f"📋 Configured to scrape {len(wayback_urls)} archived pages")
    
    all_data = scrape_multiple_wayback_urls(wayback_urls)
    
    print(f"\n{'='*60}")
    print(f"📊 FINAL RESULTS")
    print(f"{'='*60}")
    
    if all_data:
        success = save_to_json(all_data)
        if success:
            print(f"✅ Successfully scraped {len(all_data)} total entries from {len(wayback_urls)} weeks")
            
            # Show summary by week
            week_summary = {}
            for entry in all_data:
                week = entry.get('Chart Date', 'Unknown')
                week_summary[week] = week_summary.get(week, 0) + 1
            
            print("\n📅 Entries by week:")
            for week, count in week_summary.items():
                print(f"  {week}: {count} entries")
        else:
            print("❌ Failed to save data")
    else:
        print("❌ No data was scraped successfully")
        print("\n💡 Troubleshooting suggestions:")
        print("1. Check if the Wayback Machine URLs are accessible")
        print("2. YouTube's page structure may have changed significantly")
        print("3. Try different archived dates or different chart pages")

if __name__ == "__main__":
    main() 