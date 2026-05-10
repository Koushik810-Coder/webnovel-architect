import argparse
import sys
import time
from playwright.sync_api import sync_playwright

def run_tests(url: str, take_screenshot: bool, check_a11y: bool):
    with sync_playwright() as p:
        print(f"Launching browser to test {url}...")
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        try:
            # Navigate to the app
            page.goto(url, wait_until="networkidle")
            print("Page loaded.")
            
            # Basic sanity check
            # Streamlit apps often have a title or specific elements. We just wait for the app container.
            page.wait_for_selector(".stApp", timeout=15000)
            print("Streamlit app container found.")
            
            # Simple interaction example: Click on a sidebar item if present, etc.
            # Give it a moment to render
            time.sleep(2)
            
            if take_screenshot:
                screenshot_path = "streamlit_app_screenshot.png"
                page.screenshot(path=screenshot_path)
                print(f"Screenshot saved to {screenshot_path}")
                
            if check_a11y:
                # Basic axe-core integration would go here
                print("Accessibility check not fully implemented in runner yet, but placeholder works.")
                
            print("Tests completed successfully.")
            
        except Exception as e:
            print(f"Test failed: {e}")
            page.screenshot(path="failure_screenshot.png")
            print("Saved failure screenshot to failure_screenshot.png")
            sys.exit(1)
        finally:
            browser.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Playwright tests against the Streamlit App.")
    parser.add_argument("url", type=str, help="The URL to test (e.g., http://localhost:8501)")
    parser.add_argument("--screenshot", action="store_true", help="Take a screenshot after load")
    parser.add_argument("--a11y", action="store_true", help="Run accessibility checks")
    
    args = parser.parse_args()
    run_tests(args.url, args.screenshot, args.a11y)
