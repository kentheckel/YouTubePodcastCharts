# cPanel Git Deployment Setup Guide

This guide will help you set up automatic deployment from your Git repository to your cPanel hosting's public_html folder.

## Prerequisites
- cPanel hosting account with Git Version Control feature
- Your repository pushed to a Git provider (GitHub, GitLab, Bitbucket, etc.)
- SSH access to your cPanel account (recommended)

## Step-by-Step Setup

### 1. Access Git Version Control in cPanel
1. Log into your cPanel dashboard
2. Look for "Git Version Control" under the "Files" section
3. Click on "Git Version Control"

### 2. Create a New Repository
1. Click "Create Repository"
2. Fill in the repository details:
   - **Repository URL**: Your git repository URL (e.g., `https://github.com/kentheckel/YouTubePodcastCharts.git`)
   - **Repository Path**: Choose a path OUTSIDE of public_html (e.g., `/home/youtufov/repositories/YouTubePodcastCharts`)
   - **Repository Name**: Give it a meaningful name
   - **Branch**: Usually `main` or `master`

### 3. Configure Deployment Script
After creating the repository, you need to set up automatic deployment to public_html:

1. In the Git Version Control interface, find your repository
2. Click "Manage" next to your repository
3. Look for "Deployment Script" or "Post-receive hook" section
4. Choose one of these deployment methods:

#### Method A: Using the PHP Script (Recommended)
```php
<?php exec('/home/youtufov/repositories/YouTubePodcastCharts/deploy.php'); ?>
```

#### Method B: Using the Bash Script
```bash
#!/bin/bash
/home/youtufov/repositories/YouTubePodcastCharts/deploy.sh
```

#### Method C: Simple Copy Command (Basic)
```bash
#!/bin/bash
cp -r /home/youtufov/repositories/YouTubePodcastCharts/*.html /home/youtufov/public_html/
cp -r /home/youtufov/repositories/YouTubePodcastCharts/*.json /home/youtufov/public_html/
```

### 4. Update the Deployment Scripts
**IMPORTANT**: You must update the paths in both `deploy.php` and `deploy.sh` files:

1. Replace `yourusername` with your actual cPanel username
2. Update the paths to match your cPanel directory structure

In `deploy.php`, change:
```php
$public_html_dir = '/home/youtufov/public_html';
```

In `deploy.sh`, change:
```bash
PUBLIC_HTML_DIR="/home/youtufov/public_html"
```

### 5. Test the Deployment
1. Make a small change to your repository (like updating a comment in index.html)
2. Push the changes to your Git provider
3. In cPanel Git Version Control, click "Pull or Deploy" on your repository
4. Check your website to see if the changes appear

### 6. Enable Automatic Deployment (Optional)
Some cPanel providers support webhooks for automatic deployment:
1. In your Git provider (GitHub/GitLab), go to repository settings
2. Add a webhook pointing to your cPanel's git webhook URL
3. This will automatically deploy when you push changes

## Troubleshooting

### Common Issues:

1. **Permission Denied Errors**
   - Make sure your deployment script has execute permissions
   - Run: `chmod +x deploy.sh` via SSH or File Manager

2. **Files Not Copying**
   - Check that paths in deployment scripts are correct
   - Verify your cPanel username in the paths
   - Check file permissions (should be 644 for files, 755 for directories)

3. **Repository Not Updating**
   - Make sure you're pushing to the correct branch
   - Check if the repository path in cPanel is correct
   - Try manually pulling in cPanel Git interface

4. **Website Not Showing Changes**
   - Clear browser cache
   - Check if files actually copied to public_html
   - Verify file permissions

### Getting Your cPanel Username:
If you're unsure of your cPanel username:
1. Check your cPanel URL - it's often in the format: `youtufov.yourdomain.com:2083`
2. Look at the top right of your cPanel dashboard
3. Use SSH: `whoami` command
4. Check File Manager - the path shows `/home/youtufov/`

## File Structure After Deployment
Your public_html should contain:
```
public_html/
├── index.html (your homepage)
├── podcast.html
├── complete_podcast_timeline.json
├── podcast_data.json
└── other necessary files
```

## Security Notes
- The deployment scripts automatically exclude sensitive files (.py, .txt, .env, etc.)
- Your Git repository folder should be OUTSIDE of public_html for security
- Only web-safe files (HTML, CSS, JS, JSON, images) are copied to public_html

## Next Steps
After successful deployment:
1. Visit your domain to see your podcast charts website live
2. Set up a cron job to update your podcast data regularly (if needed)
3. Configure SSL certificate for HTTPS
4. Set up monitoring for your website

---

Need help? Check your cPanel documentation or contact your hosting provider's support team. 