<?php
/**
 * Automated Podcast Data Update Script for cPanel
 * 
 * This script updates your podcast chart data and can run on a separate schedule
 * from the deployment script (e.g., weekly for data updates vs. hourly for code updates)
 * 
 * Setup Instructions:
 * 1. Upload this file to your repository folder: /home/youtufov/repositories/YouTubePodcastCharts/
 * 2. Set up cron job in cPanel to run: php /home/youtufov/repositories/YouTubePodcastCharts/cron_update_data.php
 * 3. Recommended schedule: Weekly (Sundays at 2 AM) or daily
 */

// Configuration
$repo_path = '/home/youtufov/repositories/YouTubePodcastCharts';
$public_html_path = '/home/youtufov/public_html';
$log_file = $repo_path . '/data_update.log';

// Function to log messages with timestamp
function log_message($message) {
    global $log_file;
    $timestamp = date('Y-m-d H:i:s');
    $log_entry = "[$timestamp] $message\n";
    file_put_contents($log_file, $log_entry, FILE_APPEND | LOCK_EX);
    echo $log_entry; // Also output to console for cron email
}

log_message("=== Starting Podcast Data Update ===");

// Check if repository directory exists
if (!is_dir($repo_path)) {
    log_message("ERROR: Repository directory not found at: $repo_path");
    exit(1);
}

// Change to repository directory
chdir($repo_path);
log_message("Changed to repository directory: $repo_path");

// Check if Python script exists
$python_script = $repo_path . '/collect_weekly_data.py';
if (!file_exists($python_script)) {
    log_message("ERROR: Python script not found at: $python_script");
    exit(1);
}

// Run the data collection script
log_message("Running podcast data collection script...");
$python_output = shell_exec('cd ' . $repo_path . ' && python3 collect_weekly_data.py 2>&1');
log_message("Python script output: " . trim($python_output));

// Check if the script generated/updated JSON files
$json_files_to_check = [
    'complete_podcast_timeline.json',
    'podcast_data.json'
];

$updated_files = [];
foreach ($json_files_to_check as $json_file) {
    $file_path = $repo_path . '/' . $json_file;
    if (file_exists($file_path)) {
        // Check if file was modified in the last 10 minutes (indicating recent update)
        $file_modified_time = filemtime($file_path);
        $current_time = time();
        if (($current_time - $file_modified_time) < 600) { // 10 minutes = 600 seconds
            $updated_files[] = $json_file;
            log_message("Detected recent update: $json_file");
        }
    }
}

if (empty($updated_files)) {
    log_message("No data files were updated. Check Python script execution.");
} else {
    log_message("Data update successful. Updated files: " . implode(', ', $updated_files));
    
    // Deploy updated files to public_html
    log_message("Deploying updated data files to public_html...");
    
    foreach ($updated_files as $filename) {
        $source_file = $repo_path . '/' . $filename;
        $target_file = $public_html_path . '/' . $filename;
        
        if (copy($source_file, $target_file)) {
            chmod($target_file, 0644);
            log_message("Deployed updated: $filename");
        } else {
            log_message("ERROR: Failed to deploy $filename");
        }
    }
    
    // Commit changes to git (optional - uncomment if you want to auto-commit data updates)
    /*
    log_message("Committing data updates to git...");
    $commit_message = "Automated podcast data update - " . date('Y-m-d H:i:s');
    shell_exec('git add *.json');
    $commit_output = shell_exec('git commit -m "' . $commit_message . '" 2>&1');
    log_message("Git commit output: " . trim($commit_output));
    
    // Push to repository (be careful with this - ensure you have proper git credentials set up)
    // $push_output = shell_exec('git push origin main 2>&1');
    // log_message("Git push output: " . trim($push_output));
    */
}

log_message("=== Podcast Data Update Complete ===\n");

// Clean up old log entries (keep last 50 lines)
$log_content = file_get_contents($log_file);
$log_lines = explode("\n", $log_content);
if (count($log_lines) > 50) {
    $recent_lines = array_slice($log_lines, -50);
    file_put_contents($log_file, implode("\n", $recent_lines));
}

?> 