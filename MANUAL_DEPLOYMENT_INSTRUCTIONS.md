# Manual Deployment Instructions for cPanel

When your cPanel doesn't have automatic deployment script options, use these methods:

## Method 1: Web-Based Deployment Trigger

1. **Upload trigger_deploy.php** to your public_html folder using File Manager
2. **Change the password** in the file (line 12): 
   ```php
   $deploy_password = "your-secure-password-here";
   ```
3. **Visit your deployment URL**: `https://yourdomain.com/trigger_deploy.php`
4. **Enter your password** and click Deploy
5. **Delete the trigger_deploy.php file** when you're done (for security)

## Method 2: Manual File Manager Copy

1. **Set up Git repository** in cPanel Git Version Control:
   - Repository URL: `https://github.com/kentheckel/YouTubePodcastCharts.git`
   - Repository Path: `/home/youtufov/repositories/YouTubePodcastCharts`

2. **When you want to update your site**:
   - Go to Git Version Control in cPanel
   - Click "Pull or Deploy" (or just "Pull")
   - Go to File Manager
   - Navigate to `/home/youtufov/repositories/YouTubePodcastCharts/`
   - Select these files:
     - `index.html`
     - `podcast.html`
     - `complete_podcast_timeline.json`
     - `podcast_data.json`
   - Copy them
   - Go to `/home/youtufov/public_html/`
   - Paste the files (overwrite existing ones)

## Method 3: Terminal Commands (if available)

If your cPanel has Terminal access:

```bash
# Navigate to repository
cd /home/youtufov/repositories/YouTubePodcastCharts

# Pull latest changes
git pull

# Run deployment script
php deploy.php
```

## Files That Should Be In public_html After Deployment:
- `index.html` (your homepage)
- `podcast.html`
- `complete_podcast_timeline.json`
- `podcast_data.json`

## Security Notes:
- Never leave `trigger_deploy.php` on your server permanently
- Use a strong password if you do keep it temporarily
- Your Git repository folder should stay outside of public_html
- Only copy web-safe files to public_html

## Troubleshooting:
- If files don't appear, check file permissions (644 for files, 755 for folders)
- Clear browser cache to see changes
- Make sure you're copying to the right public_html folder
- Check that the repository path matches what you set in cPanel Git 