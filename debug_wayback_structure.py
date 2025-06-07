#!/usr/bin/env python3
"""
Comprehensive debug script to analyze the Wayback Machine page structure
"""

import requests
from bs4 import BeautifulSoup
import re

def analyze_wayback_structure(url):
    """Analyze the actual structure of the Wayback Machine page"""
    print(f"🔍 DEEP ANALYSIS: {url}")
    print("=" * 80)
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    response = requests.get(url, headers=headers, timeout=30)
    soup = BeautifulSoup(response.content, 'lxml')
    
    # 1. Look for ALL text mentioning known podcasts
    all_text = soup.get_text()
    known_podcasts = [
        'Joe Rogan', 'Kill Tony', 'Rotten Mango', 'Tucker Carlson',
        'Shawn Ryan', 'H3 Podcast', 'Diary of a CEO', 'Lex Fridman'
    ]
    
    print("🎯 SEARCHING FOR KNOWN PODCASTS IN TEXT:")
    found_podcasts = []
    for podcast in known_podcasts:
        if podcast.lower() in all_text.lower():
            found_podcasts.append(podcast)
            print(f"  ✅ Found: {podcast}")
    
    if not found_podcasts:
        print("  ❌ No known podcasts found in page text")
        return
    
    print(f"\n🎉 SUCCESS! Found {len(found_podcasts)} known podcasts in the page!")
    
    # 2. Find the lines containing these podcasts
    lines = all_text.split('\n')
    podcast_lines = []
    for i, line in enumerate(lines):
        line_clean = line.strip()
        if line_clean and any(podcast.lower() in line_clean.lower() for podcast in found_podcasts):
            podcast_lines.append((i, line_clean))
    
    print(f"\n📝 LINES CONTAINING PODCASTS ({len(podcast_lines)} found):")
    for line_num, line in podcast_lines[:10]:  # Show first 10
        print(f"  Line {line_num}: {line[:100]}...")
    
    # 3. Now find the HTML elements containing these texts
    print(f"\n🔍 FINDING HTML ELEMENTS CONTAINING PODCAST NAMES:")
    podcast_elements = []
    
    for podcast in found_podcasts:
        elements = soup.find_all(text=re.compile(podcast, re.I))
        for element in elements:
            parent = element.parent
            if parent:
                podcast_elements.append((podcast, parent))
                print(f"  📍 '{podcast}' found in: <{parent.name}> with classes: {parent.get('class', [])}")
    
    # 4. Analyze the structure around podcast elements
    if podcast_elements:
        print(f"\n🏗️  ANALYZING STRUCTURE AROUND PODCAST ELEMENTS:")
        
        # Group by parent tag types
        parent_tags = {}
        for podcast, element in podcast_elements:
            tag_name = element.name
            if tag_name not in parent_tags:
                parent_tags[tag_name] = []
            parent_tags[tag_name].append((podcast, element))
        
        for tag, elements in parent_tags.items():
            print(f"\n  📊 {len(elements)} podcasts found in <{tag}> elements:")
            for podcast, elem in elements[:3]:  # Show first 3
                attrs = elem.attrs
                print(f"    - {podcast}: {attrs}")
                
                # Look at the parent and siblings
                if elem.parent:
                    siblings = elem.parent.find_all()
                    print(f"      Parent <{elem.parent.name}> has {len(siblings)} child elements")
    
    # 5. Look for numbered lists or ranking structures
    print(f"\n🔢 LOOKING FOR RANKING STRUCTURES:")
    
    # Find elements with numbers that might be ranks
    numbered_elements = soup.find_all(text=re.compile(r'^\s*[1-9]\d*\s*$'))
    if numbered_elements:
        print(f"  Found {len(numbered_elements)} elements with just numbers:")
        for i, num_elem in enumerate(numbered_elements[:10]):
            parent = num_elem.parent
            print(f"    {num_elem.strip()}: in <{parent.name}> {parent.get('class', [])}")
    
    # 6. Look for any table or list structures
    tables = soup.find_all('table')
    lists = soup.find_all(['ul', 'ol'])
    divs_with_numbers = soup.find_all('div', text=re.compile(r'\d+'))
    
    print(f"\n📊 STRUCTURAL ELEMENTS:")
    print(f"  Tables: {len(tables)}")
    print(f"  Lists: {len(lists)}")
    print(f"  Divs with numbers: {len(divs_with_numbers)}")
    
    # 7. Extract a sample of the raw HTML around podcast mentions
    print(f"\n📄 RAW HTML SAMPLES:")
    for podcast, element in podcast_elements[:3]:
        print(f"\n  🎯 HTML around '{podcast}':")
        # Get the grandparent to see more context
        context_elem = element.parent.parent if element.parent and element.parent.parent else element.parent
        if context_elem:
            html_sample = str(context_elem)[:500]  # First 500 chars
            print(f"    {html_sample}...")
    
    # 8. Save the full HTML for manual inspection
    with open('wayback_full_page.html', 'w', encoding='utf-8') as f:
        f.write(soup.prettify())
    print(f"\n💾 Saved full page HTML to wayback_full_page.html")

def main():
    """Analyze the Wayback Machine page with podcast data"""
    url = "https://web.archive.org/web/20250515184935/https://charts.youtube.com/podcasts"
    analyze_wayback_structure(url)

if __name__ == "__main__":
    main() 