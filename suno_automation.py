# suno_login_save_session.py

import asyncio
from playwright.async_api import async_playwright

async def automate_login():
    print("🚀 Starting Suno.ai login automation...")

    async with async_playwright() as p:
        print("🔧 Launching Chromium...")
        browser = await p.chromium.launch(headless=False, slow_mo=100)

        context = await browser.new_context()
        page = await context.new_page()

        print("🌐 Navigating to https://app.suno.ai ...")
        await page.goto("https://app.suno.ai", timeout=60000)
        print("✅ Suno landing page loaded.")

        # STEP 1: Click "Sign In"
        try:
            print("🔍 Looking for 'Sign In' button...")
            await page.wait_for_selector("text=Sign In", timeout=10000)
            await page.click("text=Sign In")
            print("✅ 'Sign In' button clicked.")
        except:
            print("⚠️ Could not find or click 'Sign In'. You may already be logged in.")

        # STEP 2: Wait for user to manually log in
        print("🧠 Waiting for manual login... (Complete Google login if prompted)")
        try:
            await page.wait_for_url("**/create?**", timeout=180000)  # Waits until you land on /create
            print("✅ Login successful — reached /create page.")
        except Exception as e:
            print(f"❌ Login may have failed or took too long: {e}")
            await browser.close()
            return

        # STEP 3: Save session to file
        print("💾 Saving session to 'suno_session.json' ...")
        await context.storage_state(path="suno_session.json")
        print("🎉 Session saved successfully.")

        await browser.close()
        print("🧼 Browser closed.")
        print("🏁 Done.")

if __name__ == "__main__":
    asyncio.run(automate_login())
