<?php
/**
 * Automated Cron Deployment Script for cPanel
 * 
 * This script is designed to run via cron job to automatically:
 * 1. Pull latest changes from Git repository
 * 2. Deploy website files to public_html
 * 3. Optionally update podcast data
 * 
 * Setup Instructions:
 * 1. Upload this file to your repository folder: /home/youtufov/repositories/YouTubePodcastCharts/
 * 2. Set up cron job in cPanel to run: php /home/youtufov/repositories/YouTubePodcastCharts/cron_deploy.php
 * 3. Recommended schedule: Every 30 minutes or hourly
 */

// Configuration
$repo_path = '/home/youtufov/repositories/YouTubePodcastCharts';
$public_html_path = '/home/youtufov/public_html';
$log_file = $repo_path . '/deployment.log';

// Function to log messages with timestamp
function log_message($message) {
    global $log_file;
    $timestamp = date('Y-m-d H:i:s');
    $log_entry = "[$timestamp] $message\n";
    file_put_contents($log_file, $log_entry, FILE_APPEND | LOCK_EX);
    echo $log_entry; // Also output to console for cron email
}

log_message("=== Starting Automated Deployment ===");

// Check if repository directory exists
if (!is_dir($repo_path)) {
    log_message("ERROR: Repository directory not found at: $repo_path");
    exit(1);
}

// Change to repository directory
chdir($repo_path);
log_message("Changed to repository directory: $repo_path");

// Pull latest changes from Git
log_message("Pulling latest changes from Git repository...");
$git_output = shell_exec('git pull origin main 2>&1');
log_message("Git pull output: " . trim($git_output));

// Check if there were any changes
if (strpos($git_output, 'Already up to date') !== false) {
    log_message("No changes detected. Skipping deployment.");
    log_message("=== Deployment Complete (No Changes) ===\n");
    exit(0);
}

// Deploy files to public_html
log_message("Changes detected. Starting deployment...");

// Create public_html directory if it doesn't exist
if (!is_dir($public_html_path)) {
    mkdir($public_html_path, 0755, true);
    log_message("Created public_html directory");
}

// Files to deploy
$files_to_deploy = [
    'index.html',
    'podcast.html',
    'complete_podcast_timeline.json',
    'podcast_data.json'
];

// Deploy each file
$deployed_count = 0;
foreach ($files_to_deploy as $filename) {
    $source_file = $repo_path . '/' . $filename;
    $target_file = $public_html_path . '/' . $filename;
    
    if (file_exists($source_file)) {
        if (copy($source_file, $target_file)) {
            // Set proper permissions
            chmod($target_file, 0644);
            log_message("Deployed: $filename");
            $deployed_count++;
        } else {
            log_message("ERROR: Failed to deploy $filename");
        }
    } else {
        log_message("WARNING: Source file not found: $filename");
    }
}

// Deploy any CSS files if they exist
$css_files = glob($repo_path . '/*.css');
foreach ($css_files as $css_file) {
    $filename = basename($css_file);
    $target_file = $public_html_path . '/' . $filename;
    if (copy($css_file, $target_file)) {
        chmod($target_file, 0644);
        log_message("Deployed CSS: $filename");
        $deployed_count++;
    }
}

// Deploy any JS files if they exist
$js_files = glob($repo_path . '/*.js');
foreach ($js_files as $js_file) {
    $filename = basename($js_file);
    $target_file = $public_html_path . '/' . $filename;
    if (copy($js_file, $target_file)) {
        chmod($target_file, 0644);
        log_message("Deployed JS: $filename");
        $deployed_count++;
    }
}

// Optional: Update podcast data (uncomment if you want automatic data updates)
/*
log_message("Updating podcast data...");
if (file_exists($repo_path . '/collect_weekly_data.py')) {
    $python_output = shell_exec('cd ' . $repo_path . ' && python3 collect_weekly_data.py 2>&1');
    log_message("Python script output: " . trim($python_output));
    
    // Re-deploy JSON files after data update
    foreach (['complete_podcast_timeline.json', 'podcast_data.json'] as $json_file) {
        $source_file = $repo_path . '/' . $json_file;
        $target_file = $public_html_path . '/' . $json_file;
        if (file_exists($source_file)) {
            copy($source_file, $target_file);
            chmod($target_file, 0644);
            log_message("Re-deployed updated: $json_file");
        }
    }
}
*/

log_message("Deployment completed successfully! Deployed $deployed_count files.");
log_message("=== Deployment Complete ===\n");

// Clean up old log entries (keep last 100 lines)
$log_content = file_get_contents($log_file);
$log_lines = explode("\n", $log_content);
if (count($log_lines) > 100) {
    $recent_lines = array_slice($log_lines, -100);
    file_put_contents($log_file, implode("\n", $recent_lines));
}

?> 