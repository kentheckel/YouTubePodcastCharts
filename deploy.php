<?php
/**
 * Git Deployment Script for cPanel
 * This script automatically deploys files from git repository to public_html
 * 
 * Instructions:
 * 1. Place this file in your git repository root
 * 2. Set this as the deployment script in cPanel Git Version Control
 * 3. Make sure the paths below match your cPanel setup
 */

// Configuration - Update these paths for your cPanel setup
$repo_dir = __DIR__; // Current directory (git repository)
$public_html_dir = '/home/youtufov/public_html'; // Update 'yourusername' with your actual cPanel username

// Files and directories to deploy (add more as needed)
$files_to_deploy = [
    'index.html',
    'podcast.html',
    '*.json',  // All JSON files
    '*.css',   // All CSS files if any
    '*.js',    // All JavaScript files if any
    'assets/*', // Assets directory if exists
    'images/*', // Images directory if exists
    'css/*',    // CSS directory if exists
    'js/*'      // JS directory if exists
];

// Files and directories to exclude from deployment
$exclude_files = [
    '*.py',           // Python scripts
    '*.txt',          // Text files
    'requirements.txt',
    'README.md',
    'DATA_CLEANUP_README.md',
    '.git',
    '.github',
    '.venv',
    '.gitignore',
    'deploy.php',     // Don't deploy this script itself
    '*.csv',          // CSV files
    '*.zip',          // ZIP files
    '.DS_Store',      // Mac system files
    'Private & Shared'
];

echo "Starting deployment...\n";

// Function to copy files recursively
function copyFiles($source, $dest, $exclude = []) {
    if (!file_exists($dest)) {
        mkdir($dest, 0755, true);
    }
    
    $iterator = new RecursiveIteratorIterator(
        new RecursiveDirectoryIterator($source, RecursiveDirectoryIterator::SKIP_DOTS),
        RecursiveIteratorIterator::SELF_FIRST
    );
    
    foreach ($iterator as $item) {
        $target = $dest . DIRECTORY_SEPARATOR . $iterator->getSubPathName();
        
        // Check if file should be excluded
        $should_exclude = false;
        foreach ($exclude as $pattern) {
            if (fnmatch($pattern, $item->getFilename()) || 
                fnmatch($pattern, $iterator->getSubPathName())) {
                $should_exclude = true;
                break;
            }
        }
        
        if ($should_exclude) {
            continue;
        }
        
        if ($item->isDir()) {
            if (!file_exists($target)) {
                mkdir($target, 0755, true);
            }
        } else {
            copy($item, $target);
            echo "Copied: " . $iterator->getSubPathName() . "\n";
        }
    }
}

// Deploy specific files
foreach ($files_to_deploy as $pattern) {
    $files = glob($repo_dir . '/' . $pattern);
    foreach ($files as $file) {
        if (is_file($file)) {
            $filename = basename($file);
            $target = $public_html_dir . '/' . $filename;
            
            // Check if file should be excluded
            $should_exclude = false;
            foreach ($exclude_files as $exclude_pattern) {
                if (fnmatch($exclude_pattern, $filename)) {
                    $should_exclude = true;
                    break;
                }
            }
            
            if (!$should_exclude) {
                copy($file, $target);
                echo "Deployed: $filename\n";
            }
        }
    }
}

echo "Deployment completed successfully!\n";
echo "Website files have been copied to public_html\n";
echo "Your site should now be live at your domain\n";
?> 