#!/usr/bin/env python3
"""
Playwright-based scraper for Wayback Machine - renders JavaScript like a real browser
"""

import json
import html
from playwright.sync_api import sync_playwright
import time

def scrape_wayback_with_playwright(wayback_url, chart_week_range):
    """Use Playwright to render the Wayback Machine page and extract data"""
    print(f"\n🎯 Playwright Scraping: {wayback_url}")
    print(f"📅 Week range: {chart_week_range}")
    
    results = []
    
    with sync_playwright() as p:
        # Launch browser with more permissive settings
        browser = p.chromium.launch(
            headless=True,  # Set to False to see what's happening
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox'
            ]
        )
        
        try:
            page = browser.new_page()
            
            # Set a reasonable user agent
            page.set_extra_http_headers({
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            })
            
            print("🌐 Loading Wayback Machine page...")
            page.goto(wayback_url, wait_until='networkidle', timeout=60000)
            
            # Wait a bit more for any dynamic content to load
            print("⏳ Waiting for content to load...")
            time.sleep(5)
            
            # First, let's see what's actually on the page
            page_title = page.title()
            print(f"📄 Page title: {page_title}")
            
            # Check if we can find known podcast names in the page
            page_content = page.content()
            known_podcasts = ['Joe Rogan', 'Kill Tony', 'Rotten Mango']
            found_podcasts = []
            
            for podcast in known_podcasts:
                if podcast.lower() in page_content.lower():
                    found_podcasts.append(podcast)
                    print(f"✅ Found '{podcast}' in page content!")
            
            if not found_podcasts:
                print("❌ No known podcasts found in rendered page content")
                
                # Let's see what we actually have
                print("\n🔍 DEBUG: Looking for any text content...")
                
                # Try to find any meaningful content
                all_text = page.evaluate("document.body.innerText")[:1000]
                print(f"Page text preview: {all_text}")
                
                # Check if this is a Wayback Machine error/redirect
                if "wayback machine" in all_text.lower() or "not found" in all_text.lower():
                    print("⚠️  This appears to be a Wayback Machine error page")
                    return []
                
                # Save screenshot for debugging
                page.screenshot(path="wayback_screenshot.png")
                print("📸 Saved screenshot as wayback_screenshot.png")
                
                return []
            
            print(f"🎉 SUCCESS! Found {len(found_podcasts)} podcasts in rendered page")
            
            # Now try to extract the data using your known selectors
            print("\n🔍 Looking for YouTube chart elements...")
            
            # Try the original selectors first
            try:
                entry_elements = page.query_selector_all("ytmc-entry-row")
                print(f"📊 Found {len(entry_elements)} ytmc-entry-row elements")
                
                if entry_elements:
                    for i, element in enumerate(entry_elements):
                        try:
                            # Extract rank
                            rank_element = element.query_selector("span#rank")
                            if rank_element:
                                rank = int(rank_element.inner_text().strip())
                            else:
                                rank = i + 1
                            
                            # Extract title
                            title_element = element.query_selector("div#entity-title")
                            if not title_element:
                                continue
                                
                            title = title_element.inner_text().strip()
                            if not title or len(title) < 2:
                                continue
                            
                            # Extract URL from endpoint attribute
                            url = ""
                            endpoint_attr = title_element.get_attribute("endpoint")
                            if endpoint_attr:
                                try:
                                    data = json.loads(html.unescape(endpoint_attr))
                                    url = data.get("urlEndpoint", {}).get("url", "")
                                except:
                                    pass
                            
                            # Extract thumbnail
                            thumb_element = element.query_selector("img.podcasts-thumbnail")
                            thumb_url = ""
                            if thumb_element:
                                thumb_url = thumb_element.get_attribute("src") or ""
                            
                            # Create entry
                            entry = {
                                "Name": title,
                                "Chart Date": chart_week_range,
                                "Rank": str(rank),
                                "Channel URL": url,
                                "Thumbnail URL": thumb_url
                            }
                            
                            results.append(entry)
                            print(f"  ✅ #{rank}: {title[:50]}...")
                            
                        except Exception as e:
                            print(f"  ⚠️  Error processing element {i+1}: {e}")
                            continue
                
                else:
                    print("❌ No ytmc-entry-row elements found")
                    
                    # Try alternative approaches
                    print("\n🔍 Trying alternative selectors...")
                    
                    # Look for any elements containing the podcast names we found
                    for podcast in found_podcasts:
                        elements = page.query_selector_all(f"text={podcast}")
                        print(f"📍 Found {len(elements)} elements containing '{podcast}'")
                        
                        # If we found elements, try to understand their structure
                        if elements:
                            for i, elem in enumerate(elements[:3]):
                                try:
                                    # Get the parent structure
                                    parent_info = page.evaluate("""
                                        (element) => {
                                            let parent = element.parentElement;
                                            return {
                                                tagName: parent ? parent.tagName : null,
                                                className: parent ? parent.className : null,
                                                innerHTML: parent ? parent.innerHTML.substring(0, 200) : null
                                            };
                                        }
                                    """, elem)
                                    print(f"    Element {i+1} parent: <{parent_info.get('tagName')}> class='{parent_info.get('className')}'")
                                except Exception as e:
                                    print(f"    Error analyzing element {i+1}: {e}")
                
            except Exception as e:
                print(f"❌ Error with selectors: {e}")
            
            # Save the full rendered HTML for inspection
            with open('wayback_rendered.html', 'w', encoding='utf-8') as f:
                f.write(page.content())
            print("💾 Saved rendered HTML to wayback_rendered.html")
            
        finally:
            browser.close()
    
    return results

def main():
    """Main function using Playwright"""
    print("🎯 Wayback Machine Scraper - Using Playwright (Browser Rendering)")
    print("=" * 70)
    
    wayback_urls = [
        ("https://web.archive.org/web/20250515184935/https://charts.youtube.com/podcasts", "May 5 - May 11, 2025"),
        ("https://web.archive.org/web/20250521211257/https://charts.youtube.com/podcasts", "May 12 - May 18, 2025"),
    ]
    
    all_data = []
    
    for i, (url, week_range) in enumerate(wayback_urls, 1):
        print(f"\n{'='*70}")
        print(f"📊 SCRAPING {i}/{len(wayback_urls)} WITH PLAYWRIGHT")
        print(f"{'='*70}")
        
        entries = scrape_wayback_with_playwright(url, week_range)
        all_data.extend(entries)
        
        if entries:
            print(f"\n🎉 SUCCESS! Found {len(entries)} entries from {week_range}")
            for entry in entries[:5]:
                print(f"  #{entry['Rank']}: {entry['Name']}")
        else:
            print(f"\n❌ No data extracted from {week_range}")
        
        if i < len(wayback_urls):
            print("\n⏳ Waiting 5 seconds before next request...")
            time.sleep(5)
    
    print(f"\n{'='*70}")
    print(f"📊 FINAL RESULTS")
    print(f"{'='*70}")
    
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
            
    else:
        print("❌ No data extracted")
        print("\n💡 Next steps:")
        print("1. Check the saved screenshot and HTML files")
        print("2. The Wayback Machine might not have captured the full page")
        print("3. Try different archived dates or manual extraction")

if __name__ == "__main__":
    main() 