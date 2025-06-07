#!/usr/bin/env python3
"""
Debug script to inspect the actual content from Wayback Machine pages
"""

import requests
from bs4 import BeautifulSoup
import re

def inspect_wayback_page(url):
    """Inspect the actual content of a Wayback Machine page"""
    print(f"\n🔍 INSPECTING: {url}")
    print("=" * 80)
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'lxml')
        
        # 1. Check the page title and basic structure
        title = soup.find('title')
        print(f"📄 Page title: {title.get_text().strip() if title else 'No title'}")
        
        # 2. Look for any script tags that might contain data
        scripts = soup.find_all('script')
        print(f"📜 Found {len(scripts)} script tags")
        
        # Check for JSON data in scripts
        for i, script in enumerate(scripts):
            if script.string:
                text = script.string
                if 'podcast' in text.lower() or 'chart' in text.lower():
                    print(f"  📊 Script {i+1} contains chart/podcast data ({len(text)} chars)")
                    # Look for JSON-like structures
                    if '{' in text and '}' in text:
                        print(f"    Contains JSON-like data")
                        # Try to find YouTube video/playlist IDs
                        if 'PLk1Sqn_f33K' in text or 'playlist' in text:
                            print(f"    ✅ Contains playlist references!")
        
        # 3. Look for any divs or containers that might hold chart data
        containers = soup.find_all(['div', 'section', 'main'], class_=re.compile(r'(chart|content|container|main)', re.I))
        print(f"📦 Found {len(containers)} potential content containers")
        
        # 4. Check for any tables or lists
        tables = soup.find_all('table')
        lists = soup.find_all(['ul', 'ol'])
        print(f"📊 Found {len(tables)} tables, {len(lists)} lists")
        
        # 5. Look for links that might point to playlists or channels
        links = soup.find_all('a', href=True)
        youtube_links = [link for link in links if 'youtube.com' in link.get('href', '')]
        playlist_links = [link for link in youtube_links if 'playlist' in link.get('href', '')]
        print(f"🔗 Found {len(youtube_links)} YouTube links, {len(playlist_links)} playlist links")
        
        if playlist_links:
            print("  📋 Sample playlist links:")
            for i, link in enumerate(playlist_links[:5]):
                href = link.get('href', '')
                text = link.get_text(strip=True)
                print(f"    {i+1}. {text[:50]}... -> {href[:80]}...")
        
        # 6. Look for text that contains rankings or numbers
        all_text = soup.get_text()
        lines = [line.strip() for line in all_text.split('\n') if line.strip()]
        
        # Find lines with podcast names we recognize
        known_podcasts = ['joe rogan', 'rotten mango', 'kill tony', 'tucker carlson']
        matching_lines = []
        for line in lines:
            if any(podcast in line.lower() for podcast in known_podcasts):
                matching_lines.append(line)
        
        if matching_lines:
            print(f"🎯 Found {len(matching_lines)} lines mentioning known podcasts:")
            for line in matching_lines[:10]:
                print(f"  - {line[:100]}...")
        
        # 7. Check if this is actually a Wayback Machine error page
        if 'wayback machine' in all_text.lower() and len(all_text) < 5000:
            print("⚠️  This might be a Wayback Machine error/redirect page")
        
        # 8. Save a sample of the HTML for manual inspection
        sample_filename = f"wayback_sample_{url.split('/')[-2]}.html"
        with open(sample_filename, 'w', encoding='utf-8') as f:
            f.write(str(soup.prettify())[:10000])  # First 10KB
        print(f"💾 Saved HTML sample to {sample_filename}")
        
        return soup
        
    except Exception as e:
        print(f"❌ Error inspecting page: {e}")
        return None

def main():
    """Inspect both Wayback Machine URLs"""
    urls = [
        "https://web.archive.org/web/20250515184935/https://charts.youtube.com/podcasts",
        "https://web.archive.org/web/20250521211257/https://charts.youtube.com/podcasts"
    ]
    
    for url in urls:
        inspect_wayback_page(url)

if __name__ == "__main__":
    main() 