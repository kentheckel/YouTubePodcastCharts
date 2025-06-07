# Automated Cron Job Deployment Setup

This guide will help you set up automated deployment using cPanel cron jobs, so your website updates automatically whenever you push changes to GitHub.

## Benefits of Cron Deployment
- ✅ **Fully automated** - No manual intervention needed
- ✅ **Regular updates** - Can run every 30 minutes, hourly, or daily
- ✅ **Logging** - Keeps track of all deployments
- ✅ **Smart deployment** - Only deploys when there are actual changes
- ✅ **Can include data updates** - Optionally update podcast data automatically

## Setup Instructions

### Step 1: Set Up Git Repository in cPanel
1. Go to **cPanel → Git Version Control**
2. Click **"Create Repository"**
3. Enter:
   - **Repository URL**: `https://github.com/kentheckel/YouTubePodcastCharts.git`
   - **Repository Path**: `/home/youtufov/repositories/YouTubePodcastCharts`
   - **Branch**: `main`

### Step 2: Set Up the Cron Job
1. Go to **cPanel → Cron Jobs**
2. Click **"Add New Cron Job"**
3. Choose your schedule (see options below)
4. Enter this command:
   ```bash
   php /home/youtufov/repositories/YouTubePodcastCharts/cron_deploy.php
   ```

### Step 3: Choose Your Schedule

#### Option A: Every 30 Minutes (Recommended)
- **Minute**: `*/30`
- **Hour**: `*`
- **Day**: `*`
- **Month**: `*`
- **Weekday**: `*`

#### Option B: Every Hour
- **Minute**: `0`
- **Hour**: `*`
- **Day**: `*`
- **Month**: `*`
- **Weekday**: `*`

#### Option C: Every 6 Hours
- **Minute**: `0`
- **Hour**: `*/6`
- **Day**: `*`
- **Month**: `*`
- **Weekday**: `*`

#### Option D: Daily at 2 AM
- **Minute**: `0`
- **Hour**: `2`
- **Day**: `*`
- **Month**: `*`
- **Weekday**: `*`

## How It Works

1. **Cron runs** at your scheduled time
2. **Script checks** for new commits in your GitHub repo
3. **If changes found**: 
   - Pulls latest code
   - Deploys files to public_html
   - Logs the deployment
4. **If no changes**: Skips deployment (saves resources)

## Files That Get Deployed Automatically
- `index.html` (your homepage)
- `podcast.html`
- `complete_podcast_timeline.json`
- `podcast_data.json`
- Any `.css` files
- Any `.js` files

## Monitoring Your Deployments

### Check the Log File
The script creates a log file at:
```
/home/youtufov/repositories/YouTubePodcastCharts/deployment.log
```

You can view this in cPanel File Manager to see:
- When deployments ran
- What files were deployed
- Any errors that occurred

### Sample Log Output
```
[2024-01-15 14:30:01] === Starting Automated Deployment ===
[2024-01-15 14:30:01] Pulling latest changes from Git repository...
[2024-01-15 14:30:02] Git pull output: Already up to date.
[2024-01-15 14:30:02] No changes detected. Skipping deployment.
[2024-01-15 14:30:02] === Deployment Complete (No Changes) ===
```

## Optional: Automatic Data Updates

If you want to automatically update your podcast data as well, uncomment the section in `cron_deploy.php` (lines 107-122). This will:
1. Run your `collect_weekly_data.py` script
2. Update the JSON files with fresh data
3. Deploy the updated data to your website

## Workflow After Setup

1. **Make changes** to your website locally
2. **Push to GitHub** (`git push`)
3. **Wait for next cron run** (max 30 minutes if using that schedule)
4. **Your website updates automatically!**

## Troubleshooting

### Cron Job Not Running
- Check cPanel → Cron Jobs to ensure it's active
- Verify the file path is correct
- Check if PHP is available on your server

### Files Not Deploying
- Check the log file for error messages
- Verify repository path is correct
- Ensure file permissions are set properly

### Git Pull Fails
- Check if your repository is accessible
- Verify the repository URL and branch name
- May need to set up SSH keys for private repositories

### No Email Notifications
- Cron jobs typically send email output to your cPanel email
- If you don't want emails, add `> /dev/null 2>&1` to the end of your cron command

## Advanced Configuration

### Custom File Deployment
Edit the `$files_to_deploy` array in `cron_deploy.php` to add/remove files:
```php
$files_to_deploy = [
    'index.html',
    'podcast.html',
    'complete_podcast_timeline.json',
    'podcast_data.json',
    'sitemap.xml',  // Add custom files
    'robots.txt'    // Add more as needed
];
```

### Change Log Retention
The script keeps the last 100 log entries. To change this, edit line 128:
```php
if (count($log_lines) > 50) {  // Keep only 50 entries
```

## Security Notes
- The cron script only deploys specific file types
- No sensitive files (.py, .txt, config files) are deployed
- Repository stays outside of public_html for security
- Log files are kept in the secure repository folder

---

This automated setup means you can now just push changes to GitHub and your website will update automatically within 30 minutes (or your chosen schedule)! 