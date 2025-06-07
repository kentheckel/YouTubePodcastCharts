# YouTube Podcast Charts Tracker

A beautiful, interactive website that tracks YouTube podcast rankings over time with automatic weekly data collection.

## 🎯 Features

- **Interactive Timeline Chart**: Scroll through weeks of podcast ranking data
- **Individual Podcast Analytics**: Detailed performance metrics for each podcast
- **Automatic Data Collection**: Weekly updates via GitHub Actions
- **Dark/Light Theme**: User-friendly interface with theme switching
- **Responsive Design**: Works perfectly on desktop and mobile
- **AdSense Ready**: Pre-configured for monetization

## 🚀 Live Demo

Visit the live site at: `https://yourusername.github.io/youtube-podcast-charts/`

## 📊 Current Data

The site currently tracks:
- **400+ podcast entries** across multiple weeks
- **Individual podcast pages** with comprehensive analytics
- **Ranking history charts** showing performance over time
- **100+ off-chart tracking** for complete podcast journeys

## 🛠️ Setup & Deployment

### 1. Fork/Clone Repository

```bash
git clone https://github.com/yourusername/youtube-podcast-charts.git
cd youtube-podcast-charts
```

### 2. Enable GitHub Pages

1. Go to your repository **Settings**
2. Navigate to **Pages** section
3. Set source to **GitHub Actions**
4. Your site will be available at `https://yourusername.github.io/repository-name/`

### 3. Configure Automated Data Collection

The GitHub Action will automatically:
- Run every **Monday at 2 AM UTC**
- Scrape current YouTube podcast charts
- Update the JSON data file
- Redeploy the website

**Manual trigger**: Go to **Actions** tab → **Update Podcast Chart Data** → **Run workflow**

### 4. Set Up AdSense (Optional)

1. Apply for [Google AdSense](https://www.google.com/adsense)
2. Once approved, replace placeholder codes in both `index.html` and `podcast.html`:
   ```html
   data-ad-client="ca-pub-YOUR_PUBLISHER_ID"
   data-ad-slot="YOUR_AD_SLOT_ID"
   ```
3. Uncomment the initialization script:
   ```javascript
   (adsbygoogle = window.adsbygoogle || []).push({});
   ```

## 📁 Project Structure

```
youtube-podcast-charts/
├── index.html                          # Main chart page
├── podcast.html                        # Individual podcast analytics
├── complete_podcast_timeline.json      # Chart data (auto-updated)
├── collect_weekly_data.py              # Data collection script
├── .github/workflows/update-data.yml   # GitHub Action workflow
└── README.md                           # This file
```

## 🔄 How Automatic Updates Work

1. **GitHub Action triggers** every Monday
2. **Playwright scrapes** current YouTube podcast charts
3. **Script checks** if data for current week already exists
4. **New data added** to JSON file if it's a new week
5. **Website redeploys** automatically with updated data
6. **Users see** fresh data without any manual intervention

## 🎨 Customization

### Modify Chart Appearance
- Edit CSS variables in both HTML files
- Adjust `WEEKS_VISIBLE`, `RANK_HEIGHT`, etc. in JavaScript
- Change color schemes in the `:root` CSS section

### Change Update Frequency
- Modify the cron schedule in `.github/workflows/update-data.yml`
- Current: `'0 2 * * 1'` (Monday 2 AM UTC)
- Daily: `'0 2 * * *'`
- Weekly different day: `'0 2 * * 3'` (Wednesday)

### Add More Analytics
- Extend the `calculateAnalytics()` function in `podcast.html`
- Add new stat cards to the analytics grid
- Implement additional chart types using Chart.js

## 🛡️ Troubleshooting

### GitHub Action Fails
- Check if Playwright can access YouTube (they may block automated requests)
- Verify the DOM selectors still match YouTube's structure
- Check Action logs for specific error messages

### Website Not Updating
- Ensure GitHub Pages is set to use GitHub Actions
- Verify the JSON file is being updated in the repository
- Check if there are any deployment errors in Actions

### Charts Not Loading
- Verify `complete_podcast_timeline.json` is valid JSON
- Check browser console for JavaScript errors
- Ensure file paths are correct for your hosting setup

## 📈 Performance Optimization

- **Lazy loading**: Images load as needed
- **Efficient scrolling**: Only visible elements are rendered
- **Minimal dependencies**: Fast loading times
- **Responsive design**: Optimized for all devices

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit changes: `git commit -am 'Add feature'`
4. Push to branch: `git push origin feature-name`
5. Submit a pull request

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 👨‍💻 Made By

Created by **Kent** - [kentheckel.com](https://kentheckel.com) - 2025

---

**⭐ Star this repository if you find it useful!** 