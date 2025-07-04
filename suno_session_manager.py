# suno_session_manager.py
import asyncio
import time
from playwright.async_api import async_playwright

async def generate_song_on_suno(lyrics: str):
    print(lyrics)
    print("🚀 Launching Suno automation...")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=50)
        context = await browser.new_context(storage_state="suno_session.json")

        page = await context.new_page()
        await page.goto("https://suno.com/create", timeout=60000)
        print("✅ Logged in and opened /create")

        # Step 1: Fill lyrics
        try:
            await page.wait_for_selector('textarea', timeout=15000)
            await page.fill('textarea', lyrics)
            print("🎤 Lyrics filled.")
        except Exception as e:
            print(f"❌ Could not fill lyrics: {e}")
            return


        # Step 2: Click "Create"
        try:
            await page.click('button:has-text("Create")')
            print("🎵 Create button clicked.")
        except Exception as e:
            print(f"❌ Failed to click Create: {e}")
            return

        # Step 3: Wait for song card to appear
        print("⏳ Waiting for track to render...")
        await page.wait_for_timeout(50000)  # Adjust if needed

        # Step 4: Click 3-dot menu
        try:
            print("🧑‍📏 Looking for 3-dots button...")
            await page.wait_for_selector('button[aria-label="More Options"]', timeout=10000)
            await page.click('button[aria-label="More Options"]')
            print("✅ 3-dots menu clicked.")
        except Exception as e:
            print(f"❌ Failed to click 3-dots menu: {e}")
            return None

        # Step 5: Click "Download" from dropdown
        try:
            await page.wait_for_selector("text=Download", timeout=15000)
            await page.hover("text=Download")
            await page.click("text=Download")
            print("📂 Clicked 'Download'")
        except Exception as e:
            print(f"❌ Could not click 'Download': {e}")
            return

        # Step 6: Click "MP3 Audio"
        try:
            await page.wait_for_selector("text=MP3 Audio", timeout=10000)
            await page.click("text=MP3 Audio")
            print("🎷 Clicked 'MP3 Audio'")
        except Exception as e:
            print(f"❌ Could not click 'MP3 Audio': {e}")
            return

        # Step 7: Handle "Download Anyway" confirmation
        try:
            await page.wait_for_selector("text=Download Anyway", timeout=10000)
            async with page.expect_download() as download_info:
                await page.click("text=Download Anyway")
                print("⬇️ Clicked 'Download Anyway'")
            download = await download_info.value
            filename = f"static/audio/suno_song_{int(time.time())}.mp3"
            await download.save_as(filename)
            print(f"✅ Downloaded as {filename}")
        except Exception as e:
            print(f"❌ Final download step failed: {e}")
            return

        await browser.close()
        print("🎉 Automation complete.")
        return f"/{filename}"
