#!/usr/bin/env python3
import os
import datetime
import html
import json
from notion_client import Client
from playwright.sync_api import sync_playwright

# ─── CONFIG ────────────────────────────────────────────────────────────────────
YOUTUBE_CHARTS_URL = "https://charts.youtube.com/podcasts"
NOTION_TOKEN       = os.environ["NOTION_TOKEN"]
NOTION_DATABASE_ID = os.environ["NOTION_DATABASE_ID"]
# ────────────────────────────────────────────────────────────────────────────────

def scrape_podcasts():
    """Use Playwright to grab the weekly top podcast list, including artwork."""
    results = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(YOUTUBE_CHARTS_URL)
        page.wait_for_selector("ytmc-entry-row")

        items = page.query_selector_all("ytmc-entry-row")
        for item in items:
            # ─── Rank ───────────────────────────────────────────
            rank_el = item.query_selector("span#rank")
            if not rank_el:
                continue
            rank = int(rank_el.inner_text().strip())

            # ─── Title & URL ────────────────────────────────────
            title_el = item.query_selector("div#entity-title")
            if not title_el:
                continue
            title = title_el.inner_text().strip()

            endpoint_attr = title_el.get_attribute("endpoint")
            url = None
            if endpoint_attr:
                data = json.loads(html.unescape(endpoint_attr))
                url = data.get("urlEndpoint", {}).get("url")

            # ─── Thumbnail ─────────────────────────────────────
            thumb_el = item.query_selector("img.podcasts-thumbnail")
            thumb_url = thumb_el.get_attribute("src") if thumb_el else None

            results.append({
                "rank": rank,
                "title": title,
                "url": url,
                "thumbnail_url": thumb_url
            })

        browser.close()
    return results

def upsert_notion(podcasts):
    """Push or update each podcast entry in Notion with this week's date, rank, and artwork."""
    notion = Client(auth=NOTION_TOKEN)
    today = datetime.date.today().isoformat()

    for pod in podcasts:
        query = notion.databases.query(
            database_id=NOTION_DATABASE_ID,
            filter={
                "and": [
                    {"property": "Name",       "title": {"equals": pod["title"]}},
                    {"property": "Chart Date", "date":  {"equals": today}}
                ]
            }
        )

        props = {
            "Name": {
                "title": [{"text": {"content": pod["title"]}}]
            },
            "Chart Date": {
                "date": {"start": today}
            },
            "Rank": {
                "number": pod["rank"]
            },
            "Channel URL": {
                "url": pod["url"]
            },
            "Thumbnail URL": {
                "url": pod["thumbnail_url"]
            }
        }

        if query["results"]:
            page_id = query["results"][0]["id"]
            notion.pages.update(page_id=page_id, properties=props)
            print(f"Updated: {pod['title']} → rank {pod['rank']}")
        else:
            notion.pages.create(parent={"database_id": NOTION_DATABASE_ID}, properties=props)
            print(f"Inserted: {pod['title']} → rank {pod['rank']}")

if __name__ == "__main__":
    pods = scrape_podcasts()
    upsert_notion(pods)
