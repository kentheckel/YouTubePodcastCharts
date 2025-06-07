#!/usr/bin/env python3
"""
Debug script to inspect YouTube podcast charts page structure
"""

import time
from playwright.sync_api import sync_playwright

def debug_youtube_structure():
    print("🔍 Debugging YouTube Podcast Charts page structure...")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # Set to False to see the browser
        page = browser.new_page()
        
        try:
            # Navigate to YouTube Podcast Charts
            print("📱 Navigating to YouTube Podcast Charts...")
            page.goto("https://charts.youtube.com/podcasts", wait_until="networkidle")
            
            # Wait a bit for dynamic content
            time.sleep(10)
            
            # Take a screenshot for debugging
            page.screenshot(path="youtube_debug.png")
            print("📸 Screenshot saved as youtube_debug.png")
            
            # Try to find different possible selectors
            selectors_to_try = [
                "[data-test-id='entity-row']",
                ".entity-row", 
                "[data-testid='entity-row']",
                ".chart-entity",
                ".ytmc-entry-row",
                "ytmc-entry-row",
                ".podcast-entry",
                ".chart-row",
                "[role='listitem']",
                "li",
                ".entry",
                "[data-entity]"
            ]
            
            print("\n🔍 Testing different selectors:")
            for selector in selectors_to_try:
                try:
                    elements = page.locator(selector).all()
                    if elements:
                        print(f"✅ Found {len(elements)} elements with selector: {selector}")
                        
                        # Get some sample text from first few elements
                        for i, element in enumerate(elements[:3]):
                            try:
                                text = element.inner_text()[:100]
                                print(f"   Element {i+1}: {text}...")
                            except:
                                print(f"   Element {i+1}: Could not get text")
                    else:
                        print(f"❌ No elements found with selector: {selector}")
                except Exception as e:
                    print(f"❌ Error with selector {selector}: {e}")
            
            # Get page title and URL to confirm we're on the right page
            print(f"\n📄 Page title: {page.title()}")
            print(f"🔗 Current URL: {page.url()}")
            
            # Save the page HTML for manual inspection
            html_content = page.content()
            with open("youtube_debug.html", "w", encoding="utf-8") as f:
                f.write(html_content)
            print("💾 Full HTML saved as youtube_debug.html")
            
            # Wait for manual inspection
            print("\n⏳ Browser will stay open for 30 seconds for manual inspection...")
            time.sleep(30)
            
        except Exception as e:
            print(f"❌ Error during debugging: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    debug_youtube_structure() 