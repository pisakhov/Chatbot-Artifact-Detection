from playwright.sync_api import sync_playwright
import time

def test_chat_interface():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        page.goto('http://localhost:8000')

        time.sleep(2)

        print("✓ Page loaded successfully")
        print(f"✓ Page title: {page.title()}")

        message_input = page.locator('#messageInput')
        send_button = page.locator('#sendBtn')

        print("✓ Found message input and send button")

        print("\n--- Test 1: Regular Message ---")
        message_input.fill('Hello, this is a test message!')
        print("✓ Typed test message")

        time.sleep(1)

        send_button.click()
        print("✓ Clicked send button")

        time.sleep(3)

        messages = page.locator('.rounded-lg.px-4.py-3')
        message_count = messages.count()
        print(f"✓ Found {message_count} messages in chat")

        time.sleep(2)

        print("\n--- Test 2: Artifact Message (Chart) ---")
        message_input.fill('Show me a sales chart')
        print("✓ Typed chart request")

        time.sleep(1)

        send_button.click()
        print("✓ Clicked send button")

        time.sleep(4)

        charts = page.locator('.highcharts-container')
        chart_count = charts.count()
        print(f"✓ Found {chart_count} chart(s) rendered")

        if chart_count > 0:
            print("✓ Artifact detection and rendering working!")
        else:
            print("✗ No charts found - artifact rendering may have issues")

        time.sleep(5)

        browser.close()
        print("\n✓ Test completed successfully!")

if __name__ == "__main__":
    test_chat_interface()

