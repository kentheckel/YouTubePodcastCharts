#!/usr/bin/env python3
"""
Script to fix the CSV dates and convert them to proper YouTube chart week ranges.
This preserves your existing work while correcting the date mapping.
"""

import csv
import json
from datetime import datetime

def convert_csv_to_proper_weeks(csv_filename, output_filename):
    """
    Convert CSV data with collection dates to proper chart week ranges
    
    Date mapping based on your data:
    - May 29, 2025 CSV entries = May 23-29, 2025 chart week
    - June 7, 2025 CSV entries = May 26-Jun 1, 2025 chart week
    (Excluding June 2, 2025 as it's duplicate data for the same chart week as June 7)
    """
    
    # Define the date mapping
    date_mapping = {
        "May 29, 2025": "May 23 - May 29, 2025",
        "June 2, 2025": "May 26 - Jun 1, 2025",  # Duplicate - will be skipped
        "June 7, 2025": "May 26 - Jun 1, 2025"  # Keep the more recent collection
    }
    
    print("🔄 Converting CSV data to proper chart week ranges...")
    print("Date mappings:")
    for csv_date, chart_week in date_mapping.items():
        if csv_date == "June 2, 2025":
            print(f"  {csv_date} → {chart_week} (SKIPPED - duplicate)")
        else:
            print(f"  {csv_date} → {chart_week}")
    print()
    
    converted_data = []
    
    try:
        with open(csv_filename, 'r', encoding='utf-8') as csvfile:
            # Try to detect if there's a BOM
            first_line = csvfile.readline()
            csvfile.seek(0)
            
            # Read CSV data
            reader = csv.DictReader(csvfile)
            
            for row in reader:
                # Handle BOM in column names
                name_key = None
                for key in row.keys():
                    if 'Name' in key:
                        name_key = key
                        break
                
                if not name_key:
                    print(f"Warning: Could not find Name column in row: {row}")
                    continue
                
                # Get the original chart date from CSV
                original_date = row.get('Chart Date', '').strip()
                
                # Skip June 2, 2025 entries as they're duplicates of June 7, 2025 (same chart week)
                if original_date == "June 2, 2025":
                    continue
                
                # Convert to proper chart week range
                proper_week = date_mapping.get(original_date, original_date)
                
                # Create corrected entry
                corrected_entry = {
                    "Name": row[name_key].strip(),
                    "Chart Date": proper_week,
                    "Rank": row.get('Rank', '').strip(),
                    "Channel URL": row.get('Channel URL', '').strip(),
                    "Thumbnail URL": row.get('Thumbnail URL', '').strip()
                }
                
                converted_data.append(corrected_entry)
        
        print(f"✅ Successfully converted {len(converted_data)} entries")
        
        # Save to JSON
        with open(output_filename, 'w', encoding='utf-8') as jsonfile:
            json.dump(converted_data, jsonfile, indent=2, ensure_ascii=False)
        
        print(f"💾 Corrected data saved to {output_filename}")
        
        # Generate summary
        week_counts = {}
        for entry in converted_data:
            week = entry['Chart Date']
            week_counts[week] = week_counts.get(week, 0) + 1
        
        print("\n📊 Data summary by corrected week:")
        for week, count in sorted(week_counts.items()):
            print(f"  {week}: {count} entries")
        
        return converted_data
        
    except FileNotFoundError:
        print(f"❌ Error: Could not find {csv_filename}")
        return []
    except Exception as e:
        print(f"❌ Error processing CSV: {e}")
        return []

def create_complete_timeline():
    """
    Create a script to combine all data sources into one complete timeline
    """
    print("\n🔗 Next steps to create complete timeline:")
    print("1. Run the wayback scraper: python scrape_wayback_charts.py")
    print("2. This script will create corrected CSV data")
    print("3. Run the comprehensive merger script")

def main():
    """Main function"""
    print("🎯 YouTube Podcast Chart Date Fixer")
    print("=" * 40)
    
    # Convert your existing CSV data
    csv_filename = "YouTube Podcast Charts 202051ef802980d4a63af327dff12c2b_all.csv"
    output_filename = "corrected_csv_data.json"
    
    converted_data = convert_csv_to_proper_weeks(csv_filename, output_filename)
    
    if converted_data:
        print("\n✅ CSV data conversion complete!")
        create_complete_timeline()
    else:
        print("\n❌ CSV conversion failed")

if __name__ == "__main__":
    main() 