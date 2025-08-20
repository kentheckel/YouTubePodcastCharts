# YouTube Podcast Charts - Folder Structure

This repository has been organized into logical folders for better maintainability and clarity.

## 📁 Folder Organization

### `/scripts/` - Python Scripts and Data Processing
Contains all Python scripts for:
- **Scraping scripts**: `scrape_podcast_charts.py`, `scrape_wayback_*.py`
- **Data processing**: `csv_to_json.py`, `merge_chart_data.py`, `fix_csv_dates.py`
- **Timeline creation**: `create_complete_timeline.py`, `fix_timeline_order*.py`
- **Data collection**: `collect_weekly_data.py`, `find_podcast_json.py`
- **Dataset building**: `build_top100_dataset.py` (main dataset builder)
- **Debug scripts**: `debug_wayback_*.py`
- **Testing & examples**: `test_dataset_builder.py`, `example_usage.py`
- **Dependencies**: `requirements.txt`

### `/web/` - Web Assets and Frontend
Contains all web-related files:
- **HTML pages**: `index.html`, `podcast.html`
- **Web assets**: `robots.txt`, `sitemap.xml`, `ads.txt`

### `/data/` - Data Files
Contains all data files:
- **JSON data**: `podcast_data.json`, `complete_podcast_timeline.json`, `wayback_historical_data.json`
- **CSV data**: `youtube_top_100_podcasts.csv`, `corrected_csv_data.json`

### `/deployment/` - Deployment and Server Files
Contains deployment-related files:
- **PHP scripts**: `deploy.php`, `cron_deploy.php`, `cron_update_data.php`
- **Shell scripts**: `deploy.sh`
- **Test files**: `test_deploy_local.php`, `quick_deploy_test.php`
- **Trigger files**: `trigger_deploy.php`

### `/docs/` - Documentation
Contains all documentation:
- **Main README**: `README.md`
- **Deployment guides**: `CPANEL_DEPLOYMENT_GUIDE.md`, `CRON_DEPLOYMENT_SETUP.md`
- **Manual instructions**: `MANUAL_DEPLOYMENT_INSTRUCTIONS.md`, `MANUAL_CRON_TEST.md`
- **Data cleanup**: `DATA_CLEANUP_README.md`
- **This file**: `FOLDER_STRUCTURE.md`

### `/temp/` - Temporary and Debug Files
Contains temporary and debug files:
- **Script outputs**: `script_*.txt` files
- **Debug HTML**: `wayback_*.html` files
- **Export files**: `*.zip` files

## 🔄 Migration Notes

- All Python scripts moved to `/scripts/`
- All web files moved to `/web/`
- All data files moved to `/data/`
- All deployment files moved to `/deployment/`
- All documentation moved to `/docs/`
- Temporary/debug files moved to `/temp/`

## 📋 File Types by Folder

| Folder | File Types | Purpose |
|--------|------------|---------|
| `/scripts/` | `.py`, `requirements.txt` | Python scripts and dependencies |
| `/web/` | `.html`, `.txt`, `.xml` | Web pages and assets |
| `/data/` | `.json`, `.csv` | Data storage |
| `/deployment/` | `.php`, `.sh` | Server deployment |
| `/docs/` | `.md` | Documentation |
| `/temp/` | `.txt`, `.html`, `.zip` | Temporary/debug files |

## 🚀 Benefits of This Organization

1. **Easier Navigation**: Related files are grouped together
2. **Better Maintenance**: Clear separation of concerns
3. **Cleaner Root**: Root directory is now much cleaner
4. **Logical Grouping**: Files are organized by their purpose
5. **Easier Collaboration**: Team members can quickly find relevant files

## 📝 Notes

- The `.git/` and `.github/` folders remain in the root as they are Git-specific
- The `.gitignore` file remains in the root as it affects the entire repository
- All file paths in scripts may need to be updated to reflect the new structure
