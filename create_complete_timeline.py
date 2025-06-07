#!/usr/bin/env python3
"""
Comprehensive script to merge all YouTube podcast chart data sources:
1. Wayback Machine historical data (May 5-11, May 12-18)
2. Corrected CSV data (May 23-29, May 26-Jun 1) 
3. Any additional manual data

Creates one complete, accurate timeline with proper week ranges.
"""

import json
from datetime import datetime

def load_json_data(filename):
    """Load data from a JSON file"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"⚠️  File {filename} not found - skipping")
        return []
    except Exception as e:
        print(f"❌ Error loading {filename}: {e}")
        return []

def merge_all_data_sources():
    """Merge all available data sources"""
    print("📂 Loading all data sources...")
    
    # Load all data sources
    wayback_data = load_json_data("wayback_historical_data.json")
    corrected_csv_data = load_json_data("corrected_csv_data.json")
    
    print(f"  Wayback Machine data: {len(wayback_data)} entries")
    print(f"  Corrected CSV data: {len(corrected_csv_data)} entries")
    
    # Combine all data
    all_data = []
    all_data.extend(wayback_data)
    all_data.extend(corrected_csv_data)
    
    # Remove duplicates
    unique_data = []
    seen_entries = set()
    
    for entry in all_data:
        # Create unique key based on name, date, and rank
        key = f"{entry.get('Name', '')}_{entry.get('Chart Date', '')}_{entry.get('Rank', '')}"
        if key not in seen_entries:
            unique_data.append(entry)
            seen_entries.add(key)
    
    print(f"🔀 Total merged entries: {len(unique_data)} (removed {len(all_data) - len(unique_data)} duplicates)")
    
    return unique_data

def analyze_complete_timeline(data):
    """Analyze the complete timeline and identify any gaps"""
    if not data:
        print("No data to analyze")
        return
    
    print("\n📅 Complete Timeline Analysis:")
    print("=" * 50)
    
    # Get all unique weeks
    weeks = list(set([entry.get('Chart Date', '') for entry in data if entry.get('Chart Date')]))
    weeks.sort()
    
    print(f"Total weeks with data: {len(weeks)}")
    print("\nWeeks covered:")
    for i, week in enumerate(weeks, 1):
        week_count = len([e for e in data if e.get('Chart Date') == week])
        status = "✅" if week_count >= 90 else "⚠️" if week_count >= 50 else "❌"
        print(f"  {status} {week}: {week_count} entries")
    
    # Expected timeline (you can adjust this)
    expected_weeks = [
        "May 5 - May 11, 2025",
        "May 12 - May 18, 2025", 
        "May 19 - May 25, 2025",  # This might be missing
        "May 23 - May 29, 2025",
        "May 26 - Jun 1, 2025"
    ]
    
    print(f"\n🔍 Gap Analysis:")
    missing_weeks = []
    for expected_week in expected_weeks:
        if expected_week not in weeks:
            missing_weeks.append(expected_week)
            print(f"  ❌ Missing: {expected_week}")
        else:
            print(f"  ✅ Found: {expected_week}")
    
    if missing_weeks:
        print(f"\n⚠️  You have {len(missing_weeks)} missing week(s) that may need manual data entry")
    else:
        print(f"\n🎉 Complete timeline! No gaps detected.")

def generate_podcast_report(data):
    """Generate report about podcast performance"""
    if not data:
        return
    
    print(f"\n🎯 Podcast Performance Report:")
    print("=" * 50)
    
    # Count appearances per podcast
    podcast_counts = {}
    podcast_weeks = {}
    
    for entry in data:
        name = entry.get('Name', '')
        week = entry.get('Chart Date', '')
        rank = int(entry.get('Rank', 0))
        
        if name:
            podcast_counts[name] = podcast_counts.get(name, 0) + 1
            
            if name not in podcast_weeks:
                podcast_weeks[name] = []
            podcast_weeks[name].append({'week': week, 'rank': rank})
    
    # Most consistent podcasts
    print("Most frequently charting podcasts:")
    sorted_podcasts = sorted(podcast_counts.items(), key=lambda x: x[1], reverse=True)
    for i, (name, count) in enumerate(sorted_podcasts[:10], 1):
        print(f"  {i}. {name}: {count} weeks")
    
    # Biggest movers (if we have multiple weeks of data)
    weeks_list = sorted(list(set([entry.get('Chart Date', '') for entry in data])))
    if len(weeks_list) >= 2:
        print(f"\n📈 Biggest Movers (between first and last week):")
        
        first_week = weeks_list[0]
        last_week = weeks_list[-1]
        
        first_week_data = {e['Name']: int(e['Rank']) for e in data if e.get('Chart Date') == first_week}
        last_week_data = {e['Name']: int(e['Rank']) for e in data if e.get('Chart Date') == last_week}
        
        movers = []
        for name in first_week_data:
            if name in last_week_data:
                change = first_week_data[name] - last_week_data[name]  # Positive = moved up
                movers.append((name, change, first_week_data[name], last_week_data[name]))
        
        # Biggest climbers
        climbers = sorted([m for m in movers if m[1] > 0], key=lambda x: x[1], reverse=True)[:5]
        if climbers:
            print("  📈 Biggest Climbers:")
            for name, change, old_rank, new_rank in climbers:
                print(f"    {name}: #{old_rank} → #{new_rank} (+{change})")

def save_complete_timeline(data, filename="complete_podcast_timeline.json"):
    """Save the complete timeline"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Complete timeline saved to {filename}")
        return True
    except Exception as e:
        print(f"❌ Error saving timeline: {e}")
        return False

def main():
    """Main function to create complete timeline"""
    print("🚀 YouTube Podcast Chart - Complete Timeline Creator")
    print("=" * 60)
    
    # Merge all data sources
    complete_data = merge_all_data_sources()
    
    if not complete_data:
        print("❌ No data found. Make sure you've run:")
        print("  1. python scrape_wayback_charts.py")
        print("  2. python fix_csv_dates.py")
        return
    
    # Analyze the complete timeline
    analyze_complete_timeline(complete_data)
    
    # Generate podcast performance report
    generate_podcast_report(complete_data)
    
    # Save the complete timeline
    if save_complete_timeline(complete_data):
        print("\n✅ Complete timeline creation successful!")
        print("\n🎯 Next steps:")
        print("1. Review the analysis above")
        print("2. Fill any missing weeks manually if needed")
        print("3. Update your website to use complete_podcast_timeline.json")
        print("4. Your chart will now show accurate week ranges!")
    else:
        print("\n❌ Failed to save complete timeline")

if __name__ == "__main__":
    main() 