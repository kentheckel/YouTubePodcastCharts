#!/usr/bin/env python3
"""
Enhanced scraper targeting JSON data embedded in script tags from Wayback Machine
"""

import requests
from bs4 import BeautifulSoup
import json
import re
import time

def extract_json_from_scripts(soup, url):
    """Extract JSON data from script tags that might contain chart data"""
    print(f"\n🔍 Analyzing script tags for JSON data...")
    
    scripts = soup.find_all('script')
    found_data = []
    
    for i, script in enumerate(scripts):
        if not script.string:
            continue
            
        text = script.string.strip()
        if not text or len(text) < 100:
            continue
            
        # Check if this script contains chart/podcast related data
        if any(keyword in text.lower() for keyword in ['podcast', 'chart', 'playlist', 'video']):
            print(f"📊 Script {i+1}: {len(text)} chars, contains chart-related data")
            
            # Try to extract JSON objects from the script
            json_objects = extract_json_objects(text, i+1)
            if json_objects:
                found_data.extend(json_objects)
    
    return found_data

def extract_json_objects(script_text, script_num):
    """Extract JSON objects from script text"""
    json_objects = []
    
    # Look for various JSON patterns
    patterns = [
        # Standard JSON assignment: var data = {...}
        r'var\s+\w+\s*=\s*(\{.*?\});',
        r'let\s+\w+\s*=\s*(\{.*?\});',
        r'const\s+\w+\s*=\s*(\{.*?\});',
        
        # Direct JSON objects
        r'(\{[^{}]*"[^"]*"[^{}]*\})',
        
        # Array of objects
        r'(\[.*?\{.*?\}.*?\])',
        
        # YouTube-specific patterns
        r'"videoRenderer":\s*(\{.*?\})',
        r'"playlistRenderer":\s*(\{.*?\})',
        r'"channelRenderer":\s*(\{.*?\})',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, script_text, re.DOTALL | re.MULTILINE)
        for match in matches:
            try:
                # Clean up the match
                cleaned = match.strip()
                if cleaned.startswith('{') or cleaned.startswith('['):
                    # Try to parse as JSON
                    data = json.loads(cleaned)
                    if isinstance(data, (dict, list)):
                        json_objects.append({
                            'script_num': script_num,
                            'pattern': pattern,
                            'data': data,
                            'size': len(cleaned)
                        })
                        print(f"  ✅ Found JSON object ({len(cleaned)} chars)")
            except json.JSONDecodeError:
                # Try to fix common JSON issues
                try:
                    # Remove trailing commas
                    fixed = re.sub(r',(\s*[}\]])', r'\1', cleaned)
                    data = json.loads(fixed)
                    json_objects.append({
                        'script_num': script_num,
                        'pattern': pattern,
                        'data': data,
                        'size': len(fixed)
                    })
                    print(f"  ✅ Found JSON object after fixing ({len(fixed)} chars)")
                except:
                    continue
    
    return json_objects

def search_for_podcast_data(json_objects):
    """Search through JSON objects for podcast/chart data"""
    podcast_entries = []
    
    for obj in json_objects:
        data = obj['data']
        found_podcasts = search_json_recursive(data, [], obj['script_num'])
        podcast_entries.extend(found_podcasts)
    
    return podcast_entries

def search_json_recursive(data, path, script_num, max_depth=10):
    """Recursively search JSON data for podcast information"""
    if max_depth <= 0:
        return []
    
    podcasts = []
    
    if isinstance(data, dict):
        # Look for keys that suggest this is a video/playlist/channel item
        if any(key in data for key in ['title', 'name', 'videoId', 'playlistId', 'channelId']):
            podcast = extract_podcast_from_object(data, path, script_num)
            if podcast:
                podcasts.append(podcast)
        
        # Recurse into nested objects
        for key, value in data.items():
            if isinstance(value, (dict, list)):
                nested_podcasts = search_json_recursive(value, path + [key], script_num, max_depth - 1)
                podcasts.extend(nested_podcasts)
    
    elif isinstance(data, list):
        # Look for arrays that might contain chart items
        for i, item in enumerate(data):
            if isinstance(item, (dict, list)):
                nested_podcasts = search_json_recursive(item, path + [f'[{i}]'], script_num, max_depth - 1)
                podcasts.extend(nested_podcasts)
    
    return podcasts

def extract_podcast_from_object(obj, path, script_num):
    """Extract podcast information from a JSON object"""
    
    # Look for title/name
    title = None
    for title_key in ['title', 'name', 'text', 'runs']:
        if title_key in obj:
            title_data = obj[title_key]
            if isinstance(title_data, str):
                title = title_data
            elif isinstance(title_data, dict) and 'runs' in title_data:
                # YouTube often stores text in runs
                runs = title_data['runs']
                if isinstance(runs, list) and runs:
                    title = ''.join([run.get('text', '') for run in runs if isinstance(run, dict)])
            elif isinstance(title_data, dict) and 'simpleText' in title_data:
                title = title_data['simpleText']
            break
    
    if not title or len(title) < 3:
        return None
    
    # Look for thumbnails
    thumbnail_url = ""
    for thumb_key in ['thumbnail', 'thumbnails', 'avatar']:
        if thumb_key in obj:
            thumb_data = obj[thumb_key]
            if isinstance(thumb_data, dict):
                if 'thumbnails' in thumb_data and isinstance(thumb_data['thumbnails'], list):
                    thumbnails = thumb_data['thumbnails']
                    if thumbnails:
                        thumbnail_url = thumbnails[0].get('url', '')
                elif 'url' in thumb_data:
                    thumbnail_url = thumb_data['url']
            break
    
    # Look for URLs/IDs
    url = ""
    for url_key in ['videoId', 'playlistId', 'channelId', 'navigationEndpoint']:
        if url_key in obj:
            url_data = obj[url_key]
            if isinstance(url_data, str):
                if url_key == 'videoId':
                    url = f"https://www.youtube.com/watch?v={url_data}"
                elif url_key == 'playlistId':
                    url = f"https://www.youtube.com/playlist?list={url_data}"
                elif url_key == 'channelId':
                    url = f"https://www.youtube.com/channel/{url_data}"
            break
    
    return {
        'title': title,
        'thumbnail_url': thumbnail_url,
        'url': url,
        'path': ' -> '.join(path),
        'script_num': script_num,
        'source_object': obj
    }

def scrape_wayback_json(wayback_url, chart_week_range):
    """Scrape JSON data from Wayback Machine page"""
    print(f"\n🚀 JSON Scraping: {wayback_url}")
    print(f"📅 Week range: {chart_week_range}")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(wayback_url, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'lxml')
        
        # Extract JSON from scripts
        json_objects = extract_json_from_scripts(soup, wayback_url)
        
        if not json_objects:
            print("❌ No JSON objects found in scripts")
            return []
        
        print(f"📊 Found {len(json_objects)} JSON objects total")
        
        # Search for podcast data
        podcast_data = search_for_podcast_data(json_objects)
        
        if not podcast_data:
            print("❌ No podcast data found in JSON objects")
            return []
        
        print(f"🎯 Found {len(podcast_data)} potential podcast entries")
        
        # Convert to standard format
        podcast_entries = []
        for i, podcast in enumerate(podcast_data, 1):
            entry = {
                "Name": podcast['title'],
                "Chart Date": chart_week_range,
                "Rank": str(i),
                "Channel URL": podcast['url'],
                "Thumbnail URL": podcast['thumbnail_url']
            }
            podcast_entries.append(entry)
            print(f"  #{i}: {podcast['title'][:50]}...")
        
        return podcast_entries
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return []

def main():
    """Main function"""
    print("🎯 YouTube Chart JSON Extractor")
    print("=" * 50)
    
    wayback_urls = [
        ("https://web.archive.org/web/20250515184935/https://charts.youtube.com/podcasts", "May 5 - May 11, 2025"),
        ("https://web.archive.org/web/20250521211257/https://charts.youtube.com/podcasts", "May 12 - May 18, 2025"),
    ]
    
    all_data = []
    
    for i, (url, week_range) in enumerate(wayback_urls, 1):
        print(f"\n{'='*60}")
        print(f"📊 PROCESSING {i}/{len(wayback_urls)}")
        print(f"{'='*60}")
        
        entries = scrape_wayback_json(url, week_range)
        all_data.extend(entries)
        
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
        
        print(f"✅ Successfully extracted {len(all_data)} entries")
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

if __name__ == "__main__":
    main() 