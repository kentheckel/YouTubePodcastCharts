<?php
/**
 * Quick Manual Deployment Test
 * 
 * Upload this file to your cPanel and run it to manually deploy your site
 * This bypasses the git pull and just copies files from repo to public_html
 */

echo "<h1>Quick Deployment Test</h1>";
echo "<pre>";

// Configuration - adjust if needed
$repo_path = '/home/youtufov/repositories/YouTubePodcastCharts';
$public_html_path = '/home/youtufov/public_html';

echo "Repo Path: $repo_path\n";
echo "Public HTML Path: $public_html_path\n\n";

// Check if paths exist
if (!is_dir($repo_path)) {
    echo "❌ ERROR: Repository not found at $repo_path\n";
    echo "Make sure you've set up Git Version Control in cPanel first!\n";
    exit;
}

if (!is_dir($public_html_path)) {
    echo "Creating public_html directory...\n";
    mkdir($public_html_path, 0755, true);
}

echo "✅ Both directories found!\n\n";

// Files to deploy
$files_to_deploy = [
    'index.html',
    'podcast.html', 
    'complete_podcast_timeline.json',
    'podcast_data.json'
];

echo "=== Starting Manual Deployment ===\n";

$deployed = 0;
$errors = 0;

foreach ($files_to_deploy as $filename) {
    $source = $repo_path . '/' . $filename;
    $target = $public_html_path . '/' . $filename;
    
    if (file_exists($source)) {
        if (copy($source, $target)) {
            chmod($target, 0644);
            $size = round(filesize($target) / 1024, 1);
            echo "✅ Deployed: $filename ($size KB)\n";
            $deployed++;
        } else {
            echo "❌ Failed to copy: $filename\n";
            $errors++;
        }
    } else {
        echo "⚠️  File not found in repo: $filename\n";
        $errors++;
    }
}

echo "\n=== Deployment Summary ===\n";
echo "Files deployed: $deployed\n";
echo "Errors: $errors\n";

if ($deployed > 0) {
    echo "\n🎉 SUCCESS! Your site should now be live!\n";
    echo "Visit your domain to check it out.\n";
    
    // List what's now in public_html
    echo "\nFiles now in public_html:\n";
    $files = scandir($public_html_path);
    foreach ($files as $file) {
        if ($file != '.' && $file != '..' && is_file($public_html_path . '/' . $file)) {
            $size = round(filesize($public_html_path . '/' . $file) / 1024, 1);
            echo "  - $file ($size KB)\n";
        }
    }
} else {
    echo "\n❌ No files were deployed. Check the errors above.\n";
}

echo "\n📝 Next Steps:\n";
echo "1. Visit your domain to see if the site loads\n";
echo "2. If it works, set up the cron job for automatic updates\n";
echo "3. Delete this test file for security\n";

echo "</pre>";
?> 