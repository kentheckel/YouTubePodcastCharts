#!/bin/bash

# Git Deployment Script for cPanel
# This script automatically deploys files from git repository to public_html
# 
# Instructions:
# 1. Place this file in your git repository root
# 2. Make it executable: chmod +x deploy.sh
# 3. Set this as the deployment script in cPanel Git Version Control
# 4. Update the PUBLIC_HTML_DIR path below with your actual cPanel username

# Configuration - Update this path for your cPanel setup
PUBLIC_HTML_DIR="/home/yourusername/public_html"  # Update 'yourusername' with your actual cPanel username
REPO_DIR="$(pwd)"

echo "Starting deployment from $REPO_DIR to $PUBLIC_HTML_DIR..."

# Create public_html directory if it doesn't exist
mkdir -p "$PUBLIC_HTML_DIR"

# Copy main HTML files
echo "Copying HTML files..."
cp -v index.html "$PUBLIC_HTML_DIR/" 2>/dev/null || echo "index.html not found"
cp -v podcast.html "$PUBLIC_HTML_DIR/" 2>/dev/null || echo "podcast.html not found"

# Copy JSON data files (needed for your podcast charts)
echo "Copying JSON data files..."
cp -v *.json "$PUBLIC_HTML_DIR/" 2>/dev/null || echo "No JSON files found"

# Copy CSS files if they exist
if ls *.css 1> /dev/null 2>&1; then
    echo "Copying CSS files..."
    cp -v *.css "$PUBLIC_HTML_DIR/"
fi

# Copy JavaScript files if they exist
if ls *.js 1> /dev/null 2>&1; then
    echo "Copying JavaScript files..."
    cp -v *.js "$PUBLIC_HTML_DIR/"
fi

# Copy assets directory if it exists
if [ -d "assets" ]; then
    echo "Copying assets directory..."
    cp -rv assets "$PUBLIC_HTML_DIR/"
fi

# Copy images directory if it exists
if [ -d "images" ]; then
    echo "Copying images directory..."
    cp -rv images "$PUBLIC_HTML_DIR/"
fi

# Copy css directory if it exists
if [ -d "css" ]; then
    echo "Copying css directory..."
    cp -rv css "$PUBLIC_HTML_DIR/"
fi

# Copy js directory if it exists
if [ -d "js" ]; then
    echo "Copying js directory..."
    cp -rv js "$PUBLIC_HTML_DIR/"
fi

# Set proper permissions
echo "Setting file permissions..."
find "$PUBLIC_HTML_DIR" -type f -name "*.html" -exec chmod 644 {} \;
find "$PUBLIC_HTML_DIR" -type f -name "*.json" -exec chmod 644 {} \;
find "$PUBLIC_HTML_DIR" -type f -name "*.css" -exec chmod 644 {} \;
find "$PUBLIC_HTML_DIR" -type f -name "*.js" -exec chmod 644 {} \;
find "$PUBLIC_HTML_DIR" -type d -exec chmod 755 {} \;

echo "Deployment completed successfully!"
echo "Website files have been copied to public_html"
echo "Your site should now be live at your domain"
echo "Make sure to update the PUBLIC_HTML_DIR path in this script with your actual cPanel username" 