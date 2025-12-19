# suno_session_manager.py
import asyncio
import time
from playwright.async_api import async_playwright

async def generate_song_on_suno(lyrics: str):
    print(lyrics)
    print("🚀 Launching Suno automation...")

    async with async_playwright() as p:
        # Visible browser to allow manual action
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

        # Step 3: Instruct user to manually pass security check
        print("🛡️ Please complete the visual security check manually...")
        print("⏳ Waiting for track to render... (you have 4 minutes)")

        

        # Wait for new song to appear — use a unique attribute of new song cards
        print("⏳ Waiting for the newest song to appear...")

        await asyncio.sleep(240)  # Wait for 4 minutes to allow user to complete security check
        try:
            await page.wait_for_selector('[data-testid="song-row"]', timeout=24000)
            print("✅ New song row appeared.")
        except Exception as e:
            print(f"❌ Timed out waiting for new song row: {e}")
            return

        # Get the first song-row (newest) and click its 'More Options' button
        try:
            new_song_row = (await page.query_selector_all('[data-testid="song-row"]'))[0]
            more_button = await new_song_row.query_selector('button[aria-label="More Options"]')
            await more_button.click()
            print("✅ Clicked 'More Options' on newest song.")
        except Exception as e:
            print(f"❌ Failed to click 'More Options' on newest song: {e}")
            return

        try:
            await page.wait_for_selector("text=Download", timeout=15000)
            await page.click("text=Download")
            print("📂 Clicked 'Download'")
        except Exception as e:
            print(f"❌ Could not click 'Download': {e}")
            return

        try:
            await page.wait_for_selector("text=MP3 Audio", timeout=10000)
            await page.click("text=MP3 Audio")
            print("🎷 Clicked 'MP3 Audio'")
        except Exception as e:
            print(f"❌ Could not click 'MP3 Audio': {e}")
            return

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
