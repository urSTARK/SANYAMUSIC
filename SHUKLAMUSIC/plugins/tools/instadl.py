from telegram import Update, Bot
import httpx

from SHUKLAMUSIC import app
from pyrogram import filters


DOWNLOADING_STICKER_ID = (
    "CAACAgEAAx0CfD7LAgACO7xmZzb83lrLUVhxtmUaanKe0_ionAAC-gADUSkNORIJSVEUKRrhHgQ"
)
# The base API URL remains here
API_URL = "https://insta-dl.hazex.workers.dev/?url="  


@app.on_message(filters.command(["ig", "insta"]))
async def instadl_command_handler(client, message):
    if len(message.command) < 2:
        await message.reply_text("Usage: /insta [Instagram URL]")
        return

    link = message.command[1]
    # Construct the full URL for the API call
    # This variable holds the sensitive API endpoint + user input
    full_api_url = API_URL + link
    
    downloading_sticker = None 

    try:
        downloading_sticker = await message.reply_sticker(DOWNLOADING_STICKER_ID)

        # Make an asynchronous GET request to the API
        async with httpx.AsyncClient() as client:
            response = await client.get(full_api_url)
            response.raise_for_status()
            data = response.json()

        # Check for successful response format
        if not data.get("error") and "result" in data and "url" in data["result"]:
            content_url = data["result"]["url"]
            extension = data["result"].get("extension", "").lower()

            # Determine content type 
            if extension in ("mp4", "mov", "webm", "avi") or "video" in content_url:
                await message.reply_video(content_url, caption=f"Downloaded from: `{link}`")
            elif extension in ("jpg", "jpeg", "png", "webp") or "photo" in content_url or "image" in content_url:
                await message.reply_photo(content_url, caption=f"Downloaded from: `{link}`")
            else:
                await message.reply_document(content_url, caption=f"Downloaded from: `{link}` (Sent as Document)")
        else:
            # Handle API-specific errors (e.g., "error": true)
            error_message = data.get("message", "Unable to fetch content. Please check the Instagram URL or ensure the post is public.")
            await message.reply_text(error_message)

    except httpx.HTTPStatusError as e:
        # Handle 4xx or 5xx errors from the API endpoint
        # The specific API URL is NOT sent to the user, only a generic error
        print(f"HTTP Status Error: {e}") # Log error for your own debugging
        await message.reply_text(
            "An error occurred while connecting to the download service (HTTP Status Error)."
        )
    except httpx.RequestError as e:
        # Handle connection errors (e.g., DNS failure, timeout)
        # The specific API URL is NOT sent to the user, only a generic error
        print(f"Request Error: {e}") # Log error for your own debugging
        await message.reply_text(
            "A network error occurred while trying to reach the download service."
        )
    except Exception as e:
        # Catch all other unexpected errors
        # The exception 'e' is printed for your own logs, but the user gets a generic message
        print(f"Unexpected Error: {e}")
        await message.reply_text(
            "An unexpected error occurred while processing the request. Please try again later."
        )

    finally:
        if downloading_sticker:
            # Safely delete the sticker even if an error occurred after it was sent
            await downloading_sticker.delete()
