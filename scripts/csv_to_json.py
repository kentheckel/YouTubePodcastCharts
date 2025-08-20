import csv
import json

# Input CSV file name (update this if your CSV file name changes)
CSV_FILE = 'YouTube Podcast Charts 202051ef802980d4a63af327dff12c2b_all.csv'
# Output JSON file name
JSON_FILE = 'podcast_data.json'

# Read the CSV file and convert it to a list of dictionaries
podcast_list = []
with open(CSV_FILE, 'r', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        # Each row is a dictionary with keys from the CSV header
        podcast_list.append(row)

# Write the list of dictionaries to a JSON file
with open(JSON_FILE, 'w', encoding='utf-8') as jsonfile:
    # Use indent=2 for pretty printing
    json.dump(podcast_list, jsonfile, indent=2)

print(f"Converted {CSV_FILE} to {JSON_FILE} with {len(podcast_list)} records.") 