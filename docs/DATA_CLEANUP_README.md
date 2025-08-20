# YouTube Podcast Chart Data Cleanup

This guide explains how to use the data cleanup scripts to get proper historical chart data from Wayback Machine archives.

## 📋 Overview

You currently have chart data with collection dates, but need actual chart week periods. These scripts will help you:

1. **Scrape historical data** from Wayback Machine URLs
2. **Merge and clean** all data sources
3. **Analyze gaps** and generate reports
4. **Fill missing weeks** manually

## 🚀 Quick Start

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Get Wayback Machine URLs

1. Go to [web.archive.org](https://web.archive.org)
2. Search for YouTube chart URLs like:
   - `https://www.youtube.com/charts/`
   - `https://www.youtube.com/feed/charts/`
   - `https://charts.youtube.com/`
3. Find snapshots from the weeks you need
4. Copy the Wayback Machine URLs

### Step 3: Configure the Scraper

Edit `scrape_wayback_charts.py` and add your URLs to the `wayback_urls` list:

```python
wayback_urls = [
    ("https://web.archive.org/web/20250520123456/https://www.youtube.com/charts/", "May 13 - May 19, 2025"),
    ("https://web.archive.org/web/20250527123456/https://www.youtube.com/charts/", "May 20 - May 26, 2025"),
    # Add more URLs here...
]
```

### Step 4: Run the Scraper

```bash
python scrape_wayback_charts.py
```

This will create `historical_podcast_data.json`

### Step 5: Merge and Analyze Data

```bash
python merge_chart_data.py
```

This will:
- Merge your current `podcast_data.json` with `historical_podcast_data.json`
- Clean and deduplicate the data
- Generate a comprehensive report
- Create `merged_podcast_data.json`

### Step 6: Update Your Website

Replace the JSON file your website uses with the new merged data:

```bash
cp merged_podcast_data.json podcast_data.json
```

## 📊 What Each Script Does

### `scrape_wayback_charts.py`
- Scrapes YouTube podcast charts from Wayback Machine URLs
- Extracts podcast names, ranks, thumbnails, and channel URLs
- Handles different YouTube page structures
- Respectful scraping with delays

### `merge_chart_data.py`
- Merges historical and current data
- Removes duplicates
- Cleans and validates data
- Generates detailed reports
- Identifies missing weeks

## 🔧 Troubleshooting

### Script finds no chart entries
- YouTube's HTML structure may have changed
- Try different Wayback Machine snapshots
- Check if the URL actually contains chart data

### Missing weeks
- Not all weeks may be archived
- You'll need to manually fill these gaps
- The merger script will identify which weeks are missing

### Rate limiting
- The scraper includes delays to be respectful
- If you get blocked, wait and try again later
- Consider reducing the number of URLs per run

## 📅 Manual Gap Filling

For weeks not available in Wayback Machine:

1. Check the data report for missing weeks
2. Use interpolation or estimation based on surrounding weeks
3. Add manual entries to the JSON file
4. Re-run the merger to validate

## 🎯 Expected Week Format

Make sure your week ranges match this format:
```
"May 13 - May 19, 2025"
"May 20 - May 26, 2025"
"May 27 - Jun 2, 2025"
```

## 📈 Next Steps

1. Run the scripts as described above
2. Review the generated data report
3. Fill any missing weeks manually
4. Update your chart website
5. Set up regular data collection for future weeks

## 🆘 Need Help?

- Check the console output for detailed error messages
- Verify your Wayback Machine URLs work in a browser
- Ensure the JSON files are valid (use a JSON validator)
- Try running scripts on a smaller subset first 