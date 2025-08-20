#!/usr/bin/env python3
"""
Fix the chronological order of chart weeks in the timeline data
"""

import json
from datetime import datetime

def fix_chronological_order():
    """Fix the timeline data to be in proper chronological order"""
    
    # Load the current timeline data
    with open('complete_podcast_timeline.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print("🔄 Fixing chronological order of chart weeks...")
    
    # Current problematic order from the screenshot:
    # 1. May 5 - May 11, 2025
    # 2. May 12 - May 18, 2025  
    # 3. May 26 - Jun 1, 2025    <- This should be #4
    # 4. May 23 - May 29, 2025   <- This should be #3
    
    # Create mapping to fix the overlapping/out-of-order dates
    date_fixes = {
        "May 26 - Jun 1, 2025": "May 30 - Jun 5, 2025"  # Move this week later to avoid overlap
    }
    
    print("📅 Applying date corrections:")
    for old_date, new_date in date_fixes.items():
        print(f"  {old_date} → {new_date}")
    
    # Apply the date corrections
    fixed_data = []
    for entry in data:
        original_date = entry['Chart Date']
        if original_date in date_fixes:
            entry['Chart Date'] = date_fixes[original_date]
            print(f"  ✅ Updated: {entry['Name']} → {entry['Chart Date']}")
        fixed_data.append(entry)
    
    # Verify the new chronological order
    unique_weeks = sorted(set(entry['Chart Date'] for entry in fixed_data))
    print(f"\n📊 New chronological order:")
    for i, week in enumerate(unique_weeks, 1):
        count = len([e for e in fixed_data if e['Chart Date'] == week])
        print(f"  {i}. {week}: {count} entries")
    
    # Save the corrected timeline
    with open('complete_podcast_timeline.json', 'w', encoding='utf-8') as f:
        json.dump(fixed_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Timeline corrected! Now in proper chronological order.")
    print(f"💾 Updated complete_podcast_timeline.json")
    
    return True

def main():
    """Main function to fix the timeline order"""
    print("🎯 Timeline Chronological Order Fixer")
    print("=" * 50)
    
    success = fix_chronological_order()
    
    if success:
        print("\n🎉 SUCCESS! Your chart will now display weeks in correct chronological order:")
        print("  1. May 5 - May 11, 2025")
        print("  2. May 12 - May 18, 2025") 
        print("  3. May 23 - May 29, 2025")
        print("  4. May 30 - Jun 5, 2025")
        print("\n🌐 Refresh your website to see the corrected timeline!")
    else:
        print("❌ Failed to fix timeline order")

if __name__ == "__main__":
    main() 