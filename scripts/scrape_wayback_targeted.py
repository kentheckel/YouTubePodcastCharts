#!/usr/bin/env python3
"""
Targeted Wayback Machine scraper using proven YouTube chart selectors
"""

import requests
from bs4 import BeautifulSoup
import json
import html
import time

def scrape_wayback_with_selectors(wayback_url, chart_week_range):
    """Scrape using the exact selectors from the working live scraper"""
    print(f"\n🎯 Targeted Scraping: {wayback_url}")
    print(f"📅 Week range: {chart_week_range}")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(wayback_url, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'lxml')
        
        # Look for the exact elements from your working scraper
        print("🔍 Searching for YouTube chart elements...")
        
        # 1. Look for ytmc-entry-row elements (main podcast containers)
        entry_rows = soup.find_all(attrs={'is': 'ytmc-entry-row'}) or soup.find_all('ytmc-entry-row')
        print(f"📊 Found {len(entry_rows)} ytmc-entry-row elements")
        
        if not entry_rows:
            # Alternative: look for any elements with ytmc in the name
            alt_elements = soup.find_all(attrs={'class': lambda x: x and 'ytmc' in str(x)})
            print(f"🔍 Found {len(alt_elements)} alternative ytmc elements")
            
            # Also look for generic row/entry patterns
            generic_rows = soup.find_all(['div', 'tr', 'li'], attrs={'class': lambda x: x and any(word in str(x).lower() for word in ['row', 'entry', 'item', 'rank'])})
            print(f"📋 Found {len(generic_rows)} generic row elements")
            
            entry_rows = alt_elements + generic_rows
        
        if not entry_rows:
            print("❌ No entry elements found with known selectors")
            
            # Debug: show what we do have
            print("\n🔍 DEBUG: Available elements:")
            all_divs = soup.find_all('div')[:20]  # First 20 divs
            for i, div in enumerate(all_divs):
                classes = div.get('class', [])
                if classes:
                    print(f"  div #{i+1}: class='{' '.join(classes)}'")
            
            return []
        
        print(f"🎯 Processing {len(entry_rows)} potential podcast entries...")
        
        podcast_entries = []
        for i, row in enumerate(entry_rows):
            try:
                # Extract rank using your selector
                rank_el = row.find('span', id='rank') or row.find(attrs={'id': 'rank'})
                if not rank_el:
                    # Try alternative rank selectors
                    rank_el = row.find(text=lambda x: x and x.strip().isdigit())
                    if rank_el:
                        rank = int(rank_el.strip())
                    else:
                        rank = i + 1  # Use position as fallback
                else:
                    rank = int(rank_el.get_text(strip=True))
                
                # Extract title using your selector
                title_el = row.find('div', id='entity-title') or row.find(attrs={'id': 'entity-title'})
                if not title_el:
                    # Try alternative title selectors
                    title_el = (row.find('h3') or row.find('h2') or row.find('h4') or 
                               row.find(attrs={'class': lambda x: x and 'title' in str(x).lower()}))
                
                if not title_el:
                    print(f"  ⚠️  Row {i+1}: No title found")
                    continue
                
                title = title_el.get_text(strip=True)
                if not title or len(title) < 2:
                    continue
                
                # Extract URL from endpoint attribute (your method)
                url = None
                endpoint_attr = title_el.get('endpoint')
                if endpoint_attr:
                    try:
                        data = json.loads(html.unescape(endpoint_attr))
                        url = data.get("urlEndpoint", {}).get("url")
                    except:
                        pass
                
                if not url:
                    # Try to find any link in the row
                    link_el = row.find('a', href=True)
                    if link_el:
                        href = link_el['href']
                        if 'youtube.com' in href:
                            url = href if href.startswith('http') else f"https://www.youtube.com{href}"
                
                # Extract thumbnail using your selector
                thumb_el = row.find('img', class_='podcasts-thumbnail') or row.find('img')
                thumb_url = ""
                if thumb_el:
                    thumb_url = thumb_el.get('src') or thumb_el.get('data-src') or thumb_el.get('data-thumb')
                    if thumb_url and not thumb_url.startswith('http'):
                        if thumb_url.startswith('//'):
                            thumb_url = 'https:' + thumb_url
                        elif thumb_url.startswith('/'):
                            thumb_url = 'https://www.youtube.com' + thumb_url
                
                # Create entry
                entry = {
                    "Name": title,
                    "Chart Date": chart_week_range,
                    "Rank": str(rank),
                    "Channel URL": url or "",
                    "Thumbnail URL": thumb_url or ""
                }
                
                podcast_entries.append(entry)
                print(f"  ✅ #{rank}: {title[:50]}...")
                
                # Stop if we have enough entries
                if len(podcast_entries) >= 100:
                    break
                    
            except Exception as e:
                print(f"  ⚠️  Error processing row {i+1}: {e}")
                continue
        
        print(f"✅ Successfully extracted {len(podcast_entries)} podcast entries")
        return podcast_entries
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return []

def main():
    """Main function using proven selectors"""
    print("🎯 Wayback Machine Scraper - Using Proven Selectors")
    print("=" * 60)
    
    # Test with the URL from your screenshot
    wayback_urls = [
        ("https://web.archive.org/web/20250515184935/https://charts.youtube.com/podcasts", "May 5 - May 11, 2025"),
        ("https://web.archive.org/web/20250521211257/https://charts.youtube.com/podcasts", "May 12 - May 18, 2025"),
    ]
    
    all_data = []
    
    for i, (url, week_range) in enumerate(wayback_urls, 1):
        print(f"\n{'='*60}")
        print(f"📊 SCRAPING {i}/{len(wayback_urls)}")
        print(f"{'='*60}")
        
        entries = scrape_wayback_with_selectors(url, week_range)
        all_data.extend(entries)
        
        if entries:
            print(f"\n🎉 SUCCESS! Found {len(entries)} entries from {week_range}")
            # Show first few entries
            for entry in entries[:5]:
                print(f"  #{entry['Rank']}: {entry['Name']}")
        
        if i < len(wayback_urls):
            print("⏳ Waiting 3 seconds...")
            time.sleep(3)
    
    print(f"\n{'='*60}")
    print(f"📊 FINAL RESULTS")
    print(f"{'='*60}")
    
    if all_data:
        # Save to JSON
        with open('wayback_historical_data.json', 'w', encoding='utf-8') as f:
            json.dump(all_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ SUCCESS! Extracted {len(all_data)} total entries")
        print(f"💾 Saved to wayback_historical_data.json")
        
        # Show summary
        week_summary = {}
        for entry in all_data:
            week = entry['Chart Date']
            week_summary[week] = week_summary.get(week, 0) + 1
        
        print("\n📅 Entries by week:")
        for week, count in week_summary.items():
            print(f"  {week}: {count} entries")
            
        print("\n🏆 Top 5 from each week:")
        for week in sorted(week_summary.keys()):
            week_entries = [e for e in all_data if e['Chart Date'] == week]
            week_entries.sort(key=lambda x: int(x['Rank']))
            print(f"\n📊 {week}:")
            for entry in week_entries[:5]:
                print(f"  #{entry['Rank']}: {entry['Name']}")
                
    else:
        print("❌ No data extracted")
        print("\n💡 The page structure might be different in the archived version")
        print("💡 Try running the debug script to see what elements are available")

if __name__ == "__main__":
    main() 