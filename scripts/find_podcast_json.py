#!/usr/bin/env python3
"""
Targeted script to find actual podcast chart data in the JSON objects
"""

import requests
from bs4 import BeautifulSoup
import json
import re

def save_all_json_objects(url):
    """Save all JSON objects to files for manual inspection"""
    print(f"🔍 Extracting ALL JSON objects from {url}")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    response = requests.get(url, headers=headers, timeout=30)
    soup = BeautifulSoup(response.content, 'lxml')
    
    scripts = soup.find_all('script')
    all_json_data = []
    
    for i, script in enumerate(scripts):
        if not script.string:
            continue
            
        text = script.string.strip()
        if len(text) < 100:
            continue
            
        print(f"\n📄 Script {i+1}: {len(text)} characters")
        
        # Save the script content for manual inspection
        script_filename = f"script_{i+1}_{len(text)}.txt"
        with open(script_filename, 'w', encoding='utf-8') as f:
            f.write(text)
        print(f"💾 Saved to {script_filename}")
        
        # Look for specific patterns that might indicate chart data
        if any(keyword in text.lower() for keyword in ['podcast', 'chart', 'ranking', 'joe rogan', 'playlist']):
            print(f"  🎯 Contains potential chart keywords!")
            
            # Look for specific podcast names in the text
            known_podcasts = [
                'joe rogan', 'rotten mango', 'kill tony', 'tucker carlson',
                'shawn ryan', 'h3 podcast', 'diary of a ceo', 'lex fridman'
            ]
            
            found_podcasts = []
            for podcast in known_podcasts:
                if podcast in text.lower():
                    found_podcasts.append(podcast)
            
            if found_podcasts:
                print(f"  🎉 FOUND KNOWN PODCASTS: {', '.join(found_podcasts)}")
                
                # This script likely contains the chart data!
                chart_script_filename = f"CHART_DATA_script_{i+1}.txt"
                with open(chart_script_filename, 'w', encoding='utf-8') as f:
                    f.write(text)
                print(f"  💾 Saved chart data to {chart_script_filename}")
        
        # Look for JSON-like structures
        if text.count('{') > 5 and text.count('}') > 5:
            print(f"  📊 Contains JSON-like structures ({text.count('{')} opening braces)")
        
        # Look for YouTube IDs
        youtube_patterns = [
            r'PL[a-zA-Z0-9_-]{32}',  # Playlist IDs
            r'UC[a-zA-Z0-9_-]{22}',  # Channel IDs
            r'[a-zA-Z0-9_-]{11}',    # Video IDs (less specific)
        ]
        
        for pattern_name, pattern in [('Playlist IDs', youtube_patterns[0]), ('Channel IDs', youtube_patterns[1])]:
            matches = re.findall(pattern, text)
            if matches:
                print(f"  🔗 Found {len(matches)} {pattern_name}: {matches[:3]}...")
    
    print(f"\n✅ Saved {len(scripts)} script files for inspection")

def search_for_chart_structure(url):
    """Look for specific chart data structures"""
    print(f"\n🎯 Searching for chart data structures in {url}")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    response = requests.get(url, headers=headers, timeout=30)
    soup = BeautifulSoup(response.content, 'lxml')
    
    scripts = soup.find_all('script')
    
    for i, script in enumerate(scripts):
        if not script.string:
            continue
            
        text = script.string.strip()
        if len(text) < 1000:  # Focus on larger scripts
            continue
        
        # Look for patterns that suggest chart data
        chart_indicators = [
            r'"rank":\s*\d+',  # Rank: number
            r'"position":\s*\d+',  # Position: number
            r'"chartPosition":\s*\d+',  # Chart position
            r'"ranking":\s*\d+',  # Ranking
            r'\[\s*\{.*?"title".*?"rank".*?\}',  # Array of objects with title and rank
            r'\[\s*\{.*?"name".*?"position".*?\}',  # Array with name and position
        ]
        
        found_indicators = []
        for pattern in chart_indicators:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                found_indicators.append(f"{pattern}: {len(matches)} matches")
        
        if found_indicators:
            print(f"\n📊 Script {i+1} has chart-like structures:")
            for indicator in found_indicators:
                print(f"  - {indicator}")
                
            # Save this promising script
            chart_candidate_filename = f"chart_candidate_script_{i+1}.txt"
            with open(chart_candidate_filename, 'w', encoding='utf-8') as f:
                f.write(text)
            print(f"  💾 Saved to {chart_candidate_filename}")

def main():
    """Main function to find the actual chart data"""
    print("🎯 Podcast Chart Data Detective")
    print("=" * 50)
    
    url = "https://web.archive.org/web/20250515184935/https://charts.youtube.com/podcasts"
    
    # First, save all JSON objects for inspection
    save_all_json_objects(url)
    
    # Then, search for chart-like structures
    search_for_chart_structure(url)
    
    print("\n🔍 MANUAL INSPECTION REQUIRED:")
    print("1. Check the saved script files for podcast names")
    print("2. Look for files marked as 'CHART_DATA_script_*.txt'")
    print("3. Search for JSON arrays containing podcast/playlist data")
    print("4. The actual chart data might be in a different format than expected")

if __name__ == "__main__":
    main() 