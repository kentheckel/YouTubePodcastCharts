#!/usr/bin/env python3
"""
Script to merge historical Wayback Machine data with current data
and analyze gaps in the YouTube podcast chart timeline.
"""

import json
from datetime import datetime, timedelta
import pandas as pd

def load_json_data(filename):
    """Load data from a JSON file"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"File {filename} not found")
        return []
    except Exception as e:
        print(f"Error loading {filename}: {e}")
        return []

def analyze_data_gaps(data):
    """Analyze gaps in the chart data timeline"""
    if not data:
        return
    
    # Get all unique dates
    dates = list(set([entry.get('Chart Date', '') for entry in data if entry.get('Chart Date')]))
    dates.sort()
    
    print("📅 Chart Data Timeline Analysis:")
    print(f"Total weeks with data: {len(dates)}")
    print("Weeks covered:")
    for i, date in enumerate(dates, 1):
        print(f"  {i}. {date}")
    
    # Identify missing weeks (this would need manual input of expected weeks)
    print("\n⚠️  Missing weeks analysis:")
    print("To complete the analysis, manually compare against expected YouTube chart release schedule")

def merge_data_sources(historical_data, current_data):
    """Merge historical and current data, removing duplicates"""
    all_data = []
    
    # Add historical data
    all_data.extend(historical_data)
    
    # Add current data, checking for duplicates
    existing_entries = set()
    for entry in all_data:
        key = f"{entry.get('Name', '')}_{entry.get('Chart Date', '')}_{entry.get('Rank', '')}"
        existing_entries.add(key)
    
    for entry in current_data:
        key = f"{entry.get('Name', '')}_{entry.get('Chart Date', '')}_{entry.get('Rank', '')}"
        if key not in existing_entries:
            all_data.append(entry)
            existing_entries.add(key)
    
    return all_data

def clean_chart_data(data):
    """Clean and standardize the chart data"""
    cleaned_data = []
    
    for entry in data:
        # Ensure all required fields exist
        cleaned_entry = {
            "Name": entry.get('Name', '').strip(),
            "Chart Date": entry.get('Chart Date', '').strip(),
            "Rank": str(entry.get('Rank', '')).strip(),
            "Channel URL": entry.get('Channel URL', '').strip(),
            "Thumbnail URL": entry.get('Thumbnail URL', '').strip()
        }
        
        # Skip entries with missing essential data
        if not cleaned_entry['Name'] or not cleaned_entry['Chart Date'] or not cleaned_entry['Rank']:
            continue
        
        # Validate rank is a number
        try:
            rank_num = int(cleaned_entry['Rank'])
            if 1 <= rank_num <= 100:
                cleaned_data.append(cleaned_entry)
        except ValueError:
            continue
    
    return cleaned_data

def generate_data_report(data):
    """Generate a comprehensive report about the chart data"""
    if not data:
        print("No data to analyze")
        return
    
    print("📊 YouTube Podcast Chart Data Report")
    print("=" * 50)
    
    # Basic stats
    total_entries = len(data)
    unique_podcasts = len(set([entry['Name'] for entry in data]))
    unique_weeks = len(set([entry['Chart Date'] for entry in data]))
    
    print(f"Total chart entries: {total_entries}")
    print(f"Unique podcasts: {unique_podcasts}")
    print(f"Weeks of data: {unique_weeks}")
    
    # Podcast appearance frequency
    podcast_counts = {}
    for entry in data:
        name = entry['Name']
        podcast_counts[name] = podcast_counts.get(name, 0) + 1
    
    print(f"\n🎯 Most frequently charting podcasts:")
    sorted_podcasts = sorted(podcast_counts.items(), key=lambda x: x[1], reverse=True)
    for i, (name, count) in enumerate(sorted_podcasts[:10], 1):
        print(f"  {i}. {name}: {count} weeks")
    
    # Weekly data completeness
    print(f"\n📅 Data completeness by week:")
    week_counts = {}
    for entry in data:
        week = entry['Chart Date']
        week_counts[week] = week_counts.get(week, 0) + 1
    
    for week, count in sorted(week_counts.items()):
        completeness = f"{count}/100" if count <= 100 else f"{count} (>100)"
        status = "✅" if count >= 90 else "⚠️" if count >= 50 else "❌"
        print(f"  {status} {week}: {completeness} entries")

def save_merged_data(data, filename="merged_podcast_data.json"):
    """Save the merged and cleaned data"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Merged data saved to {filename}")
    except Exception as e:
        print(f"Error saving merged data: {e}")

def main():
    """Main function to merge and analyze chart data"""
    print("🔄 YouTube Podcast Chart Data Merger")
    print("=" * 40)
    
    # Load data files
    print("\n📂 Loading data files...")
    historical_data = load_json_data("historical_podcast_data.json")
    current_data = load_json_data("podcast_data.json")
    
    print(f"Historical data entries: {len(historical_data)}")
    print(f"Current data entries: {len(current_data)}")
    
    # Merge data
    print("\n🔀 Merging data sources...")
    merged_data = merge_data_sources(historical_data, current_data)
    print(f"Merged entries (before cleaning): {len(merged_data)}")
    
    # Clean data
    print("\n🧹 Cleaning data...")
    cleaned_data = clean_chart_data(merged_data)
    print(f"Cleaned entries: {len(cleaned_data)}")
    
    # Generate report
    print("\n📊 Generating data report...")
    generate_data_report(cleaned_data)
    
    # Analyze gaps
    print("\n🔍 Analyzing data gaps...")
    analyze_data_gaps(cleaned_data)
    
    # Save merged data
    save_merged_data(cleaned_data)
    
    print("\n✅ Data merge complete!")
    print("Next steps:")
    print("1. Review the data report above")
    print("2. Check 'merged_podcast_data.json' for the combined data")
    print("3. Update your website to use the merged data file")
    print("4. Manually fill any missing weeks as needed")

if __name__ == "__main__":
    main() 