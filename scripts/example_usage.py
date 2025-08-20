#!/usr/bin/env python3
"""
Example usage of the YouTube Dataset Builder.

This script demonstrates how to use the YouTubeDatasetBuilder class
programmatically instead of through the command line interface.
"""

import os
import sys
from pathlib import Path

# Add the current directory to Python path for imports
sys.path.insert(0, Path(__file__).parent)

from build_top100_dataset import YouTubeDatasetBuilder


def example_basic_usage():
    """Example of basic usage with custom parameters."""
    print("🚀 Example: Basic Dataset Builder Usage")
    print("=" * 50)
    
    # Check if API key is available
    api_key = os.environ.get('YT_API_KEY')
    if not api_key:
        print("❌ YT_API_KEY environment variable not set")
        print("   Please set it with: export YT_API_KEY='your_api_key_here'")
        return False
    
    try:
        # Initialize the builder with custom parameters
        builder = YouTubeDatasetBuilder(
            api_key=api_key,
            max_per_playlist=10,  # Only fetch 10 videos per playlist for testing
            region="US"
        )
        
        print("✅ Builder initialized successfully")
        print(f"   Max videos per playlist: {builder.max_per_playlist}")
        print(f"   Region: {builder.region}")
        
        # Load chart data (this will find the latest week)
        json_path = "../data/complete_podcast_timeline.json"
        chart_entries = builder.load_chart_data(json_path)
        
        print(f"✅ Loaded {len(chart_entries)} chart entries")
        print(f"   Latest chart week: {chart_entries[0]['Chart Date']}")
        print(f"   Top podcast: {chart_entries[0]['Name']} (Rank {chart_entries[0]['Rank']})")
        
        # Extract a few playlist IDs as examples
        print("\n📋 Sample Playlist IDs:")
        for i, entry in enumerate(chart_entries[:3]):
            playlist_id = builder.extract_playlist_id(entry['Channel URL'])
            print(f"   {entry['Name']}: {playlist_id}")
        
        return True
        
    except Exception as e:
        print(f"❌ Example failed: {e}")
        return False


def example_custom_processing():
    """Example of custom data processing workflow."""
    print("\n🔧 Example: Custom Processing Workflow")
    print("=" * 50)
    
    try:
        # Create a mock builder for demonstration
        builder = YouTubeDatasetBuilder("mock_key", max_per_playlist=5)
        
        # Example: Process only specific chart entries
        sample_entries = [
            {
                "Name": "Sample Podcast 1",
                "Chart Date": "May 5 - May 11, 2025",
                "Rank": "1",
                "Channel URL": "https://www.youtube.com/playlist?list=PLsample123"
            },
            {
                "Name": "Sample Podcast 2",
                "Chart Date": "May 5 - May 11, 2025", 
                "Rank": "2",
                "Channel URL": "https://www.youtube.com/playlist?list=PLsample456"
            }
        ]
        
        print("✅ Processing custom chart entries:")
        for entry in sample_entries:
            playlist_id = builder.extract_playlist_id(entry['Channel URL'])
            print(f"   {entry['Name']} → Playlist ID: {playlist_id}")
        
        # Example: Calculate metrics for sample video data
        sample_video = {
            'title': 'Sample Video: Episode 123 with Special Guest!',
            'publishedAt': '2025-01-01T12:00:00Z',
            'duration': 'PT1H30M45S',
            'viewCount': 50000,
            'channelId': 'sample_channel'
        }
        
        # Mock channel data
        builder.channel_data = {'sample_channel': {'subscriberCount': 100000}}
        
        # Calculate derived metrics
        enriched_video = builder.calculate_derived_metrics(sample_video)
        
        print("\n✅ Sample video metrics calculated:")
        print(f"   Title length: {enriched_video['title_len_chars']} chars, {enriched_video['title_len_words']} words")
        print(f"   Duration: {enriched_video['duration_min']:.1f} minutes")
        print(f"   Has exclamation: {enriched_video['has_exclaim']}")
        print(f"   Has colon: {enriched_video['has_colon']}")
        print(f"   Views per sub: {enriched_video['views_per_sub']:.3f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Example failed: {e}")
        return False


def example_batch_processing():
    """Example of batch processing multiple datasets."""
    print("\n📊 Example: Batch Processing Multiple Datasets")
    print("=" * 50)
    
    try:
        # Mock builder for demonstration
        builder = YouTubeDatasetBuilder("mock_key", max_per_playlist=20)
        
        # Example: Process different chart weeks
        chart_weeks = [
            "May 5 - May 11, 2025",
            "May 12 - May 18, 2025", 
            "May 19 - May 25, 2025"
        ]
        
        print("✅ Processing multiple chart weeks:")
        for week in chart_weeks:
            print(f"   Processing week: {week}")
            # In real usage, you would load data for each week
            # and process them separately
        
        # Example: Export to different formats
        output_formats = [
            "data/podcasts_week1.csv",
            "data/podcasts_week2.csv", 
            "data/podcasts_week3.csv"
        ]
        
        print("\n✅ Output files to be generated:")
        for output_file in output_formats:
            print(f"   {output_file}")
        
        return True
        
    except Exception as e:
        print(f"❌ Example failed: {e}")
        return False


def main():
    """Run all examples."""
    print("🎯 YouTube Dataset Builder - Usage Examples")
    print("=" * 60)
    
    examples = [
        example_basic_usage,
        example_custom_processing,
        example_batch_processing
    ]
    
    passed = 0
    total = len(examples)
    
    for example in examples:
        if example():
            passed += 1
        print()
    
    print("=" * 60)
    print(f"📊 Examples completed: {passed}/{total} successful")
    
    if passed == total:
        print("🎉 All examples completed successfully!")
        print("\n💡 Ready to use the dataset builder:")
        print("   1. Set your API key: export YT_API_KEY='your_key_here'")
        print("   2. Run the main script: python build_top100_dataset.py")
        print("   3. Or use the class programmatically as shown above")
    else:
        print("⚠️  Some examples had issues (likely due to missing API key)")
        print("   This is normal for demonstration purposes")
    
    return 0


if __name__ == "__main__":
    exit(main())
