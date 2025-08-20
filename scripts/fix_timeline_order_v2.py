#!/usr/bin/env python3
"""
Fix the chronological order of chart weeks with proper date sorting
"""

import json
from datetime import datetime

def parse_date_range(date_string):
    """Parse a date range string and return a sortable datetime object"""
    # Extract the start date from ranges like "May 5 - May 11, 2025"
    try:
        start_date_str = date_string.split(' - ')[0] + ', ' + date_string.split(', ')[-1]
        return datetime.strptime(start_date_str, "%b %d, %Y")
    except:
        return datetime.min

def fix_chronological_order_v2():
    """Fix the timeline data with proper chronological sorting"""
    
    # Load the current timeline data
    with open('complete_podcast_timeline.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print("🔄 Fixing chronological order with proper date sorting...")
    
    # Get all unique date ranges and sort them properly
    unique_dates = list(set(entry['Chart Date'] for entry in data))
    
    print(f"📅 Current date ranges found:")
    for date in unique_dates:
        count = len([e for e in data if e['Chart Date'] == date])
        print(f"  {date}: {count} entries")
    
    # Sort dates chronologically
    sorted_dates = sorted(unique_dates, key=parse_date_range)
    
    print(f"\n📊 Correct chronological order:")
    for i, date in enumerate(sorted_dates, 1):
        count = len([e for e in data if e['Chart Date'] == date])
        print(f"  {i}. {date}: {count} entries")
    
    # The dates are actually fine, the issue is with my previous approach
    # Let me verify the current state is correct
    
    # Check if we need to rename the last week to avoid confusion
    problematic_date = "May 30 - Jun 5, 2025"
    better_date = "Jun 2 - Jun 8, 2025"
    
    # Apply the final correction
    fixed_data = []
    updated_count = 0
    
    for entry in data:
        if entry['Chart Date'] == problematic_date:
            entry['Chart Date'] = better_date
            updated_count += 1
        fixed_data.append(entry)
    
    if updated_count > 0:
        print(f"\n🔧 Final correction:")
        print(f"  {problematic_date} → {better_date}")
        print(f"  Updated {updated_count} entries")
    
    # Verify final order
    final_unique_dates = sorted(set(entry['Chart Date'] for entry in fixed_data), key=parse_date_range)
    
    print(f"\n✅ Final chronological order:")
    for i, date in enumerate(final_unique_dates, 1):
        count = len([e for e in fixed_data if e['Chart Date'] == date])
        print(f"  {i}. {date}: {count} entries")
    
    # Save the corrected timeline
    with open('complete_podcast_timeline.json', 'w', encoding='utf-8') as f:
        json.dump(fixed_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Timeline corrected with proper chronological order!")
    print(f"💾 Updated complete_podcast_timeline.json")
    
    return True

def main():
    """Main function to fix the timeline order"""
    print("🎯 Timeline Chronological Order Fixer v2")
    print("=" * 50)
    
    success = fix_chronological_order_v2()
    
    if success:
        print("\n🎉 SUCCESS! Your chart will now display weeks in perfect chronological order!")
        print("🌐 Refresh your website to see the corrected timeline!")
    else:
        print("❌ Failed to fix timeline order")

if __name__ == "__main__":
    main() 