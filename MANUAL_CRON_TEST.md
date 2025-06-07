# Manual Cron Job Testing Guide

Since your site isn't loading yet, let's manually trigger the deployment to get it working immediately.

## Option 1: Test via cPanel Terminal (Best)

If your cPanel has Terminal access:

1. **Go to cPanel → Terminal**
2. **Navigate to your repository:**
   ```bash
   cd /home/youtufov/repositories/YouTubePodcastCharts
   ```
3. **Run the deployment script manually:**
   ```bash
   php cron_deploy.php
   ```

This will show you exactly what happens and any errors.

## Option 2: Test via SSH (If Available)

If you have SSH access to your server:

1. **SSH into your server:**
   ```bash
   ssh youtufov@yourdomain.com
   ```
2. **Navigate to repository:**
   ```bash
   cd /home/youtufov/repositories/YouTubePodcastCharts
   ```
3. **Test the deployment:**
   ```bash
   php cron_deploy.php
   ```

## Option 3: Manual File Copy via File Manager

If Terminal/SSH aren't available:

1. **Go to cPanel → File Manager**
2. **Navigate to:** `/home/youtufov/repositories/YouTubePodcastCharts/`
3. **Select these files:**
   - `index.html`
   - `podcast.html`
   - `complete_podcast_timeline.json`
   - `podcast_data.json`
4. **Copy them (Ctrl+C or right-click → Copy)**
5. **Navigate to:** `/home/youtufov/public_html/`
6. **Paste the files (Ctrl+V or right-click → Paste)**
7. **Overwrite if asked**

## Option 4: Use the Web-Based Trigger

1. **Upload `trigger_deploy.php` to your public_html folder**
2. **Visit:** `https://yourdomain.com/trigger_deploy.php`
3. **Enter password:** `deploy123` (or whatever you changed it to)
4. **Click Deploy**

## What to Check After Manual Deployment

1. **Visit your domain** - Does it show your podcast charts site?
2. **Check if these files exist in public_html:**
   - `index.html` (your homepage)
   - `podcast.html`
   - `complete_podcast_timeline.json`
   - `podcast_data.json`

## Troubleshooting Common Issues

### If Repository Doesn't Exist
The cPanel Git repository might not be set up yet:
1. **Go to cPanel → Git Version Control**
2. **Create Repository with:**
   - URL: `https://github.com/kentheckel/YouTubePodcastCharts.git`
   - Path: `/home/youtufov/repositories/YouTubePodcastCharts`
   - Branch: `main`

### If Files Don't Copy
- **Check file permissions** - should be 644 for files, 755 for folders
- **Verify paths** - make sure `/home/youtufov/` matches your actual username
- **Check disk space** - ensure you have enough space

### If Site Still Doesn't Load
- **Clear browser cache**
- **Check if domain is pointing to the right hosting**
- **Verify public_html is the correct web root**
- **Check for `.htaccess` issues**

## Expected Output from Manual Run

When you run `php cron_deploy.php`, you should see something like:

```
[2024-01-15 14:30:01] === Starting Automated Deployment ===
[2024-01-15 14:30:01] Changed to repository directory: /home/youtufov/repositories/YouTubePodcastCharts
[2024-01-15 14:30:01] Pulling latest changes from Git repository...
[2024-01-15 14:30:02] Git pull output: Already up to date.
[2024-01-15 14:30:02] Changes detected. Starting deployment...
[2024-01-15 14:30:02] Deployed: index.html
[2024-01-15 14:30:02] Deployed: podcast.html
[2024-01-15 14:30:02] Deployed: complete_podcast_timeline.json
[2024-01-15 14:30:02] Deployed: podcast_data.json
[2024-01-15 14:30:02] Deployment completed successfully! Deployed 4 files.
```

## Next Steps After Manual Test

Once manual deployment works:
1. **Set up the cron job** for automatic updates
2. **Test the cron job** by making a small change and pushing to GitHub
3. **Monitor the deployment log** at `/home/youtufov/repositories/YouTubePodcastCharts/deployment.log`

---

**Quick Start:** Try Option 3 (File Manager copy) first - it's the most straightforward and doesn't require terminal access! 