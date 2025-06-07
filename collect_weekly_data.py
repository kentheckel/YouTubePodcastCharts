#!/usr/bin/env python3
"""
Weekly YouTube Podcast Chart Data Collector
Automatically scrapes current chart data and updates the JSON file
"""

import json
import time
from datetime import datetime, timedelta
from playwright.sync_api import sync_playwright
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_current_week_date():
    """Calculate the current chart week date (should be most recent Monday)"""
    today = datetime.now()
    # YouTube charts typically update on Mondays, so find the most recent Monday
    days_since_monday = today.weekday()
    chart_date = today - timedelta(days=days_since_monday)
    return chart_date.strftime("%B %d, %Y").replace(' 0', ' ')

def get_week_range(date_str):
    """Convert chart date to week range format matching YouTube's actual format"""
    try:
        chart_date = datetime.strptime(date_str, "%B %d, %Y")
        start_date = chart_date - timedelta(days=6)  # 7 days including end date
        
        start_formatted = start_date.strftime("%b %d").replace(' 0', ' ')
        end_formatted = chart_date.strftime("%b %d").replace(' 0', ' ')
        year = chart_date.year
        
        return f"{start_formatted} - {end_formatted}, {year}"
    except Exception as e:
        logging.warning(f"Error parsing date {date_str}: {e}")
        return date_str

def scrape_current_charts():
    """Scrape the current YouTube podcast charts"""
    logging.info("Starting chart data collection...")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        try:
            # Navigate to YouTube Podcast Charts
            logging.info("Navigating to YouTube Podcast Charts...")
            page.goto("https://charts.youtube.com/podcasts", wait_until="networkidle")
            
            # Wait for the charts to load - use the correct selector
            page.wait_for_selector('ytmc-entry-row', timeout=30000)
            time.sleep(5)  # Additional wait for dynamic loading
            
            # Extract the actual date range from the page
            logging.info("Extracting date range from page...")
            actual_week_range = ""
            
            # Get all text content from the page
            try:
                all_text = page.inner_text('body')
                lines = all_text.split('\n')
                
                # Look for "WEEKLY TOP PODCAST SHOWS" and get the next line with date
                for i, line in enumerate(lines):
                    line = line.strip()
                    if 'WEEKLY TOP PODCAST SHOWS' in line.upper():
                        # Check the next few lines for a date pattern
                        for j in range(1, 4):  # Check next 3 lines
                            if i + j < len(lines):
                                next_line = lines[i + j].strip()
                                # Look for date pattern like "May 26 - Jun 1, 2025"
                                if ' - ' in next_line and '2025' in next_line and any(month in next_line for month in ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']):
                                    actual_week_range = next_line
                                    logging.info(f"Found date range on page: {actual_week_range}")
                                    break
                        if actual_week_range:
                            break
                
                # If still not found, try searching all lines for date patterns
                if not actual_week_range:
                    for line in lines:
                        line = line.strip()
                        if ' - ' in line and '2025' in line and any(month in line for month in ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']):
                            # Make sure it looks like a week range (not too long)
                            if len(line) < 50 and line.count(',') <= 2:
                                actual_week_range = line
                                logging.info(f"Found date range pattern: {actual_week_range}")
                                break
                                
            except Exception as e:
                logging.warning(f"Error extracting date from page text: {e}")
            
            # If we couldn't find the date on the page, fall back to calculation but warn
            if not actual_week_range:
                logging.warning("Could not find date range on page, falling back to calculation")
                chart_date = get_current_week_date()
                actual_week_range = get_week_range(chart_date)
                logging.info(f"Calculated date range: {actual_week_range}")
            else:
                logging.info(f"Using actual date range from page: {actual_week_range}")
            
            # Extract podcast data
            logging.info("Extracting podcast data...")
            podcast_data = []
            
            # Get all podcast rows using the correct selector
            rows = page.locator('ytmc-entry-row').all()
            logging.info(f"Found {len(rows)} podcast entries")
            
            for i, row in enumerate(rows):
                try:
                    # Extract rank (position in list + 1)
                    rank = i + 1
                    
                    # Extract podcast name - try multiple selectors
                    name = ""
                    name_selectors = ['.title.ytmc-entry-row', '.entity-name', 'h3', '.title']
                    for selector in name_selectors:
                        try:
                            name_element = row.locator(selector).first
                            if name_element.count() > 0:
                                name = name_element.inner_text().strip()
                                if name:
                                    break
                        except:
                            continue
                    
                    if not name:
                        name = f"Unknown Podcast {rank}"
                    
                    # Extract channel URL
                    channel_url = ""
                    try:
                        link_element = row.locator('a').first
                        if link_element.count() > 0:
                            channel_url = link_element.get_attribute('href')
                            if channel_url and not channel_url.startswith('http'):
                                channel_url = f"https://www.youtube.com{channel_url}"
                    except:
                        channel_url = ""
                    
                    # Extract thumbnail URL
                    thumbnail_url = ""
                    try:
                        img_element = row.locator('img').first
                        if img_element.count() > 0:
                            thumbnail_url = img_element.get_attribute('src')
                    except:
                        thumbnail_url = ""
                    
                    # Create entry using the actual date range from the page
                    entry = {
                        "Name": name,
                        "Rank": str(rank),
                        "Chart Date": actual_week_range,
                        "Channel URL": channel_url,
                        "Thumbnail URL": thumbnail_url
                    }
                    
                    podcast_data.append(entry)
                    if rank <= 10:  # Only log first 10 to reduce noise
                        logging.info(f"Collected: #{rank} - {name}")
                    
                except Exception as e:
                    logging.error(f"Error extracting data for row {i+1}: {e}")
                    continue
            
            browser.close()
            logging.info(f"Successfully collected {len(podcast_data)} entries for week: {actual_week_range}")
            return podcast_data
            
        except Exception as e:
            logging.error(f"Error during scraping: {e}")
            browser.close()
            return []

def update_json_file(new_data):
    """Update the complete podcast timeline JSON file with new data"""
    try:
        # Load existing data
        try:
            with open('complete_podcast_timeline.json', 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
            logging.info(f"Loaded {len(existing_data)} existing entries")
        except FileNotFoundError:
            existing_data = []
            logging.info("No existing data file found, creating new one")
        
        # Check if we already have data for this week
        if new_data:
            new_week = new_data[0]['Chart Date']
            existing_weeks = set(entry.get('Chart Date', '') for entry in existing_data)
            
            logging.info(f"New week: {new_week}")
            logging.info(f"Existing weeks: {sorted(existing_weeks)}")
            
            if new_week in existing_weeks:
                logging.info(f"Data for week '{new_week}' already exists, skipping update")
                return False
            
            # Additional check: ensure we have exactly 100 entries (full chart)
            if len(new_data) < 90:  # Allow some flexibility, but ensure it's a reasonable amount
                logging.warning(f"Only collected {len(new_data)} entries, which seems too few. Aborting update.")
                return False
            
            # Add new data
            existing_data.extend(new_data)
            
            # Sort chronologically to maintain order
            def parse_chart_date(entry):
                try:
                    chart_date_str = entry.get('Chart Date', '')
                    if ' - ' in chart_date_str:
                        end_date_str = chart_date_str.split(' - ')[1]
                        return datetime.strptime(end_date_str, "%b %d, %Y")
                    return datetime.min
                except:
                    return datetime.min
            
            existing_data.sort(key=parse_chart_date)
            
            # Save updated data
            with open('complete_podcast_timeline.json', 'w', encoding='utf-8') as f:
                json.dump(existing_data, f, ensure_ascii=False, indent=2)
            
            logging.info(f"Successfully added {len(new_data)} new entries for week: {new_week}")
            logging.info(f"Total entries now: {len(existing_data)}")
            return True
        else:
            logging.warning("No new data to add")
            return False
            
    except Exception as e:
        logging.error(f"Error updating JSON file: {e}")
        return False

def main():
    """Main execution function"""
    logging.info("=== Weekly YouTube Podcast Chart Data Collection ===")
    
    # Scrape current charts
    new_data = scrape_current_charts()
    
    if new_data:
        # Update JSON file
        success = update_json_file(new_data)
        
        if success:
            logging.info("✅ Data collection and update completed successfully!")
        else:
            logging.info("ℹ️ No update needed - data already current")
    else:
        logging.error("❌ Failed to collect chart data")
        exit(1)

if __name__ == "__main__":
    main() 