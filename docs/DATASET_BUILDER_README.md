# YouTube Podcast Charts - Dataset Builder

## 🎯 Overview

The `build_top100_dataset.py` script is a comprehensive tool that transforms your podcast chart data into a rich, analytics-ready dataset by enriching it with YouTube video metadata. It takes the latest chart week from `complete_podcast_timeline.json` and fetches detailed information about each video in the top 100 podcast playlists.

## ✨ Features

- **📊 Chart Data Processing**: Automatically detects the latest chart week and selects top 100 podcasts
- **🔗 Playlist Extraction**: Extracts playlist IDs from YouTube channel URLs
- **📹 Video Metadata**: Fetches comprehensive video information (title, stats, duration, tags)
- **👥 Channel Analytics**: Retrieves channel information and subscriber counts
- **🧮 Derived Metrics**: Calculates 15+ derived metrics for analysis
- **📈 Batch Processing**: Efficiently processes videos in batches of 50
- **🔄 Rate Limiting**: Implements polite API usage with exponential backoff
- **💾 Multiple Formats**: Exports to CSV with optional Parquet support
- **📝 Comprehensive Logging**: Detailed progress tracking and API call monitoring

## 🚀 Quick Start

### 1. Prerequisites

```bash
# Python 3.11+ required
python --version

# Install dependencies
pip install -r scripts/requirements.txt

# Set YouTube API key
export YT_API_KEY="your_youtube_api_key_here"
```

### 2. Basic Usage

```bash
# Navigate to scripts directory
cd scripts

# Run with default settings
python build_top100_dataset.py

# Custom output location
python build_top100_dataset.py --out ../data/my_dataset.csv

# Limit videos per playlist
python build_top100_dataset.py --max-per-playlist 50
```

### 3. Verify Installation

```bash
# Run test suite (no API calls)
python test_dataset_builder.py
```

## 📋 Output Schema

The script generates a CSV with the following columns:

| Column | Description | Example |
|--------|-------------|---------|
| `rank` | Chart ranking (1-100) | `1` |
| `chart_week` | Chart date range | `"May 5 - May 11, 2025"` |
| `podcast_name` | Podcast name | `"The Joe Rogan Experience"` |
| `playlist_id` | YouTube playlist ID | `"PLk1Sqn_f33KuWf3tW9BBe_4TP7x8l0m3T"` |
| `channel_id` | YouTube channel ID | `"UCzQUP1qoWDoEbmsQxvdjxgQ"` |
| `channel_title` | Channel name | `"PowerfulJRE"` |
| `channel_subscribers` | Subscriber count | `15000000` |
| `video_id` | YouTube video ID | `"dQw4w9WgXcQ"` |
| `title` | Video title | `"Joe Rogan Experience #1234"` |
| `published_at` | Publication date | `"2025-01-15T10:30:00Z"` |
| `duration_iso8601` | Duration (ISO format) | `"PT2H15M30S"` |
| `duration_min` | Duration (minutes) | `135.5` |
| `view_count` | View count | `1500000` |
| `like_count` | Like count | `45000` |
| `comment_count` | Comment count | `3200` |
| `age_days` | Days since publication | `45` |
| `views_per_day` | Average daily views | `33333.33` |
| `views_per_sub` | Views per subscriber | `0.1` |
| `title_len_chars` | Title character count | `25` |
| `title_len_words` | Title word count | `4` |
| `has_question` | Contains question mark | `false` |
| `has_exclaim` | Contains exclamation | `false` |
| `has_vs` | Contains "vs" | `false` |
| `has_colon` | Contains colon | `true` |
| `has_brackets` | Contains brackets | `false` |
| `num_tokens_numeric` | Number of numeric tokens | `1` |
| `num_all_caps_words` | All-caps words count | `0` |
| `starts_with_quote` | Starts with quote | `false` |
| `ends_with_ellipsis` | Ends with ellipsis | `false` |
| `tags_json` | Video tags (JSON) | `["podcast","comedy","interview"]` |
| `category_id` | YouTube category ID | `"22"` |
| `category_name` | Category name | `"People & Blogs"` |

## 🔧 Configuration Options

### Command Line Arguments

```bash
python build_top100_dataset.py [OPTIONS]

Options:
  --max-per-playlist INT    Maximum videos per playlist (default: 100)
  --out PATH               Output CSV file path (default: data/top100_youtube_podcasts.csv)
  --region TEXT            Region code for categories (default: US)
  --json-path PATH         Path to timeline JSON (default: ../data/complete_podcast_timeline.json)
  -h, --help              Show help message
```

### Environment Variables

```bash
# Required
export YT_API_KEY="your_youtube_api_key_here"

# Optional
export PYTHONPATH="${PYTHONPATH}:/path/to/scripts"
```

## 🏗️ Architecture

### Data Flow

```
1. Load JSON Data → 2. Extract Latest Week → 3. Get Top 100 → 4. Extract Playlist IDs
                                                                    ↓
8. Export CSV ← 7. Calculate Metrics ← 6. Fetch Channel Info ← 5. Fetch Video Details
```

### API Endpoints Used

- **`playlistItems`**: Fetch video IDs from playlists
- **`videos`**: Get detailed video metadata
- **`channels`**: Retrieve channel information
- **`videoCategories`**: Map category IDs to names

### Rate Limiting Strategy

- **Batch Size**: 50 videos per API call (YouTube limit)
- **Request Delay**: 200ms between requests
- **Exponential Backoff**: Automatic retry with increasing delays
- **Max Retries**: 3 attempts per request

## 📊 Derived Metrics

The script calculates 15+ derived metrics for each video:

### Time-based Metrics
- **`age_days`**: Days since video publication
- **`views_per_day`**: Average daily view count
- **`views_per_sub`**: Views relative to channel subscribers

### Title Analysis
- **`title_len_chars/words`**: Length metrics
- **`has_question/exclaim`**: Punctuation detection
- **`has_vs/colon/brackets`**: Pattern detection
- **`num_tokens_numeric`**: Number count
- **`num_all_caps_words`**: Capitalization analysis
- **`starts_with_quote/ends_with_ellipsis`**: Format detection

### Duration Processing
- **`duration_min`**: ISO 8601 duration converted to minutes

## 🧪 Testing

### Run Test Suite

```bash
cd scripts
python test_dataset_builder.py
```

### Test Coverage

- ✅ Chart data loading and parsing
- ✅ Playlist ID extraction
- ✅ Derived metrics calculation
- ✅ CSV export functionality
- ✅ Error handling and edge cases

### Manual Testing

```bash
# Test with small dataset
python build_top100_dataset.py --max-per-playlist 5 --out test_output.csv

# Verify output
head -5 test_output.csv
wc -l test_output.csv
```

## 🚨 Error Handling

### Common Issues

1. **Missing API Key**
   ```
   Error: YT_API_KEY environment variable is required
   Solution: export YT_API_KEY="your_key_here"
   ```

2. **Rate Limiting**
   ```
   Warning: Rate limited (HTTP 429), waiting 0.4s before retry 2
   Solution: Script automatically handles with exponential backoff
   ```

3. **Invalid Playlist URLs**
   ```
   Warning: Could not extract playlist ID from: https://...
   Solution: Check if channel URLs are valid YouTube playlist links
   ```

4. **File Path Issues**
   ```
   Error: Chart data file not found: ../data/complete_podcast_timeline.json
   Solution: Verify file exists and path is correct
   ```

### Debug Mode

```bash
# Enable debug logging
export PYTHONPATH="${PYTHONPATH}:/path/to/scripts"
python -c "
import logging
logging.basicConfig(level=logging.DEBUG)
from build_top100_dataset import YouTubeDatasetBuilder
"
```

## 📈 Performance Considerations

### API Quota Usage

- **Playlist Items**: ~1 call per playlist
- **Videos**: ~2 calls per 100 videos (batch size 50)
- **Channels**: ~1 call per unique channel
- **Categories**: ~1 call per unique category

### Estimated Processing Time

- **100 playlists × 100 videos**: ~15-30 minutes
- **API calls**: ~400-600 total
- **Data size**: ~10-50 MB CSV output

### Optimization Tips

1. **Reduce `max-per-playlist`** for faster processing
2. **Use regional API endpoints** if available
3. **Monitor API quotas** in Google Cloud Console
4. **Run during off-peak hours** for better API performance

## 🔒 Security & Privacy

### API Key Management

```bash
# Never commit API keys to version control
echo "export YT_API_KEY='your_key'" >> ~/.bashrc
source ~/.bashrc

# Or use environment file
echo "YT_API_KEY=your_key" > .env
source .env
```

### Data Privacy

- Only fetches publicly available YouTube data
- No user authentication required
- Respects YouTube's terms of service
- Implements polite API usage

## 🤝 Contributing

### Development Setup

```bash
# Clone repository
git clone <your-repo>
cd YouTubePodcastCharts/scripts

# Install development dependencies
pip install -r requirements.txt

# Run tests
python test_dataset_builder.py

# Make changes and test
python build_top100_dataset.py --max-per-playlist 5
```

### Code Style

- Follow PEP 8 guidelines
- Add comprehensive docstrings
- Include type hints
- Write unit tests for new features

## 📚 Related Documentation

- **[Main README](../README.md)**: Project overview and setup
- **[Folder Structure](FOLDER_STRUCTURE.md)**: Repository organization
- **[YouTube Data API](https://developers.google.com/youtube/v3)**: Official API documentation
- **[API Quotas](https://developers.google.com/youtube/v3/getting-started#quota)**: Usage limits and costs

## 🆘 Support

### Getting Help

1. **Check logs** for detailed error messages
2. **Run test suite** to verify installation
3. **Verify API key** and permissions
4. **Check file paths** and permissions
5. **Review API quotas** in Google Cloud Console

### Common Questions

**Q: How do I get a YouTube API key?**
A: Follow the [YouTube Data API setup guide](https://developers.google.com/youtube/v3/getting-started)

**Q: Why is the script slow?**
A: YouTube API has rate limits. The script processes ~2-3 videos per second to be polite.

**Q: Can I process historical data?**
A: Yes, modify the `load_chart_data` method to select different chart weeks.

**Q: What if a playlist is private/deleted?**
A: The script logs warnings and continues with other playlists.

---

**🎯 Ready to build your dataset?** Set your API key and run `python build_top100_dataset.py`!
