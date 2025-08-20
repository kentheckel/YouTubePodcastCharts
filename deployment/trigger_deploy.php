<?php
/**
 * Manual Deployment Trigger for cPanel
 * 
 * Upload this file to your public_html folder
 * Visit: https://yourdomain.com/trigger_deploy.php to manually deploy
 * 
 * SECURITY WARNING: Remove this file after setup or add password protection
 */

// Simple password protection (optional - change this password)
$deploy_password = "deploy123";  // Change this to something secure
$entered_password = isset($_GET['password']) ? $_GET['password'] : '';

if ($entered_password !== $deploy_password) {
    echo "<h1>Deployment Trigger</h1>";
    echo "<p>Please provide the password:</p>";
    echo "<form method='get'>";
    echo "<input type='password' name='password' placeholder='Enter password'>";
    echo "<input type='submit' value='Deploy'>";
    echo "</form>";
    echo "<p><small>Usage: yourdomain.com/trigger_deploy.php?password=deploy123</small></p>";
    exit;
}

echo "<h1>Starting Deployment...</h1>";
echo "<pre>";

// Path to your git repository
$repo_path = '/home/youtufov/repositories/YouTubePodcastCharts';
$public_html_path = '/home/youtufov/public_html';

// Check if repository exists
if (!is_dir($repo_path)) {
    echo "ERROR: Repository not found at: $repo_path\n";
    echo "Please check your repository path in cPanel Git Version Control.\n";
    exit;
}

// Change to repository directory
chdir($repo_path);

// Pull latest changes first
echo "Pulling latest changes from repository...\n";
$output = shell_exec('git pull 2>&1');
echo $output . "\n";

// Run deployment script
echo "Running deployment script...\n";
if (file_exists($repo_path . '/deploy.php')) {
    include($repo_path . '/deploy.php');
} else {
    // Manual deployment if deploy.php doesn't exist
    echo "deploy.php not found, running manual deployment...\n";
    
    // Copy HTML files
    $html_files = glob($repo_path . '/*.html');
    foreach ($html_files as $file) {
        $filename = basename($file);
        if (copy($file, $public_html_path . '/' . $filename)) {
            echo "Copied: $filename\n";
        }
    }
    
    // Copy JSON files
    $json_files = glob($repo_path . '/*.json');
    foreach ($json_files as $file) {
        $filename = basename($file);
        // Skip certain files we don't want to deploy
        if (strpos($filename, 'wayback') === false && 
            strpos($filename, 'corrected_csv') === false) {
            if (copy($file, $public_html_path . '/' . $filename)) {
                echo "Copied: $filename\n";
            }
        }
    }
    
    echo "Manual deployment completed!\n";
}

echo "</pre>";
echo "<h2>Deployment Complete!</h2>";
echo "<p><a href='/'>Visit your website</a></p>";
echo "<p><strong>Security Note:</strong> Remember to delete this file when you're done setting up!</p>";
?> 