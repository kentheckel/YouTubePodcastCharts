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
    """Convert chart date to week range format"""
    try:
        chart_date = datetime.strptime(date_str, "%B %d, %Y")
        start_date = chart_date - timedelta(days=6)  # 7 days including end date
        
        start_formatted = start_date.strftime("%b %d").replace(' 0', ' ')
        end_formatted = chart_date.strftime("%b %d").replace(' 0', ' ')
        year = chart_date.year
        
        return f"{start_formatted} - {end_formatted}, {year}"
    except:
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
            
            # Wait for the charts to load
            page.wait_for_selector('[data-test-id="entity-row"]', timeout=30000)
            time.sleep(5)  # Additional wait for dynamic loading
            
            # Extract podcast data
            logging.info("Extracting podcast data...")
            podcast_data = []
            chart_date = get_current_week_date()
            week_range = get_week_range(chart_date)
            
            # Get all podcast rows
            rows = page.locator('[data-test-id="entity-row"]').all()
            logging.info(f"Found {len(rows)} podcast entries")
            
            for i, row in enumerate(rows):
                try:
                    # Extract rank (position in list + 1)
                    rank = i + 1
                    
                    # Extract podcast name
                    name_element = row.locator('.entity-name').first
                    name = name_element.inner_text().strip() if name_element.count() > 0 else f"Unknown Podcast {rank}"
                    
                    # Extract channel URL
                    link_element = row.locator('a').first
                    channel_url = link_element.get_attribute('href') if link_element.count() > 0 else ""
                    if channel_url and not channel_url.startswith('http'):
                        channel_url = f"https://www.youtube.com{channel_url}"
                    
                    # Extract thumbnail URL
                    img_element = row.locator('img').first
                    thumbnail_url = img_element.get_attribute('src') if img_element.count() > 0 else ""
                    
                    # Create entry
                    entry = {
                        "Name": name,
                        "Rank": str(rank),
                        "Chart Date": week_range,
                        "Channel URL": channel_url,
                        "Thumbnail URL": thumbnail_url
                    }
                    
                    podcast_data.append(entry)
                    logging.info(f"Collected: #{rank} - {name}")
                    
                except Exception as e:
                    logging.error(f"Error extracting data for row {i+1}: {e}")
                    continue
            
            browser.close()
            logging.info(f"Successfully collected {len(podcast_data)} entries")
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
            existing_weeks = set(entry['Chart Date'] for entry in existing_data)
            
            if new_week in existing_weeks:
                logging.info(f"Data for week '{new_week}' already exists, skipping update")
                return False
            
            # Add new data
            existing_data.extend(new_data)
            
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