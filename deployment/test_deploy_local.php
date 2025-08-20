<?php
/**
 * Local Test Version of Deployment Script
 * 
 * This simulates what the cPanel deployment would do
 * Run this locally to test the deployment logic
 */

// Simulate cPanel paths (for testing)
$repo_path = __DIR__; // Current directory (your local repo)
$public_html_path = __DIR__ . '/test_public_html'; // Test folder

// Create test public_html directory
if (!is_dir($public_html_path)) {
    mkdir($public_html_path, 0755, true);
    echo "Created test public_html directory: $public_html_path\n";
}

// Files to deploy
$files_to_deploy = [
    'index.html',
    'podcast.html',
    'complete_podcast_timeline.json',
    'podcast_data.json'
];

echo "=== Testing Deployment Logic ===\n";
echo "Source: $repo_path\n";
echo "Target: $public_html_path\n\n";

// Deploy each file
$deployed_count = 0;
foreach ($files_to_deploy as $filename) {
    $source_file = $repo_path . '/' . $filename;
    $target_file = $public_html_path . '/' . $filename;
    
    if (file_exists($source_file)) {
        if (copy($source_file, $target_file)) {
            echo "✅ Would deploy: $filename (" . round(filesize($source_file)/1024, 1) . " KB)\n";
            $deployed_count++;
        } else {
            echo "❌ Failed to copy: $filename\n";
        }
    } else {
        echo "⚠️  Source file not found: $filename\n";
    }
}

// Check for CSS/JS files
$css_files = glob($repo_path . '/*.css');
$js_files = glob($repo_path . '/*.js');

if (!empty($css_files)) {
    echo "\nCSS files found:\n";
    foreach ($css_files as $css_file) {
        echo "  - " . basename($css_file) . "\n";
    }
}

if (!empty($js_files)) {
    echo "\nJS files found:\n";
    foreach ($js_files as $js_file) {
        echo "  - " . basename($js_file) . "\n";
    }
}

echo "\n=== Test Results ===\n";
echo "Files that would be deployed: $deployed_count\n";
echo "Test deployment folder: $public_html_path\n";

// List what's in the test folder
echo "\nFiles in test public_html:\n";
$deployed_files = scandir($public_html_path);
foreach ($deployed_files as $file) {
    if ($file != '.' && $file != '..') {
        $size = round(filesize($public_html_path . '/' . $file)/1024, 1);
        echo "  - $file ($size KB)\n";
    }
}

echo "\n✅ Local test complete! The script should work on cPanel.\n";
?> 