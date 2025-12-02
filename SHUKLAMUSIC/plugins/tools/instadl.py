
import re

import httpx
from pyrogram import filters
from pyrogram.types import Message

from SHUKLAMUSIC import app

try:
    from config import LOGGER_ID
except ImportError:
    LOGGER_ID = None


DOWNLOADING_STICKER_ID = (
    "CAACAgEAAx0CfD7LAgACO7xmZzb83lrLUVhxtmUaanKe0_ionAAC-gADUSkNORIJSVEUKRrhHgQ"
)

# Regex to match Instagram URLs
INSTA_URL_REGEX = re.compile(r"^(https?://)?(www\.)?(instagram\.com|instagr\.am)/.*$")


async def _process_reel(message: Message, url: str):
    """
    Helper function to process the Instagram URL and send the video.
    """
    # Check if the URL is a valid Instagram URL
    if not re.match(INSTA_URL_REGEX, url):
        return await message.reply_text(
            "Tʜᴇ ᴘʀᴏᴠɪᴅᴇᴅ URL ɪs ɴᴏᴛ ᴀ ᴠᴀʟɪᴅ Iɴsᴛᴀɢʀᴀᴍ URL😅😅"
        )

    processing_msg = await message.reply_sticker(DOWNLOADING_STICKER_ID)
    await processing_msg.edit_text("ᴘʀᴏᴄᴇssɪɴɢ...")
    api_url = f"https://insta-dl.hazex.workers.dev/?url={url}"

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(api_url, timeout=30)
            response.raise_for_status()  # Raise an exception for bad status codes
            result = response.json()

        # Check for API-level errors
        if result.get("error"):
            raise Exception(result.get("message", "Unknown API error"))

        data = result.get("result")
        if not data:
            raise Exception("No result data found in API response.")

    except Exception as e:
        error_message = f"Eʀʀᴏʀ :\n{e}"
        try:
            await processing_msg.edit_text(error_message)
        except Exception:
            await message.reply_text(error_message)
        if LOGGER_ID:
            await app.send_message(LOGGER_ID, error_message)
        return

    # Process the successful response
    if data.get("url"):
        video_url = data["url"]
        duration = data.get("duration", "N/A")
        quality = data.get("quality", "N/A")
        type_ext = data.get("extension", "N/A")
        size = data.get("formattedSize", "N/A")

        caption = f"Dᴜʀᴀᴛɪᴏɴ : {duration}\nQᴜᴀʟɪᴛʏ : {quality}\nTʏᴘᴇ : {type_ext}\nSɪᴢᴇ : {size}"

        try:
            await message.reply_video(video_url, caption=caption)
            await processing_msg.delete()
        except Exception as e:
            error_message = f"Eʀʀᴏʀ ᴡʜɪʟᴇ sᴇɴᴅɪɴɢ ᴠɪᴅᴇᴏ:\n{e}"
            await processing_msg.edit_text(error_message)
            if LOGGER_ID:
                await app.send_message(LOGGER_ID, error_message)
    else:
        # Handle cases where the API call was 'successful' but didn't return a video URL
        try:
            return await processing_msg.edit_text(
                "Fᴀɪʟᴇᴅ ᴛᴏ ᴅᴏᴡɴʟᴏᴀᴅ ʀᴇᴇʟ. Nᴏ ᴠɪᴅᴇᴏ URL Fᴏᴜɴᴅ."
            )
        except Exception:
            return await message.reply_text(
                "Fᴀɪʟᴇᴅ ᴛᴏ ᴅᴏᴡɴʟᴏᴀᴅ ʀᴇᴇʟ. Nᴏ ᴠɪᴅᴇᴏ URL Fᴏᴜɴᴅ."
            )


@app.on_message(filters.command(["ig", "instagram", "reel"]))
async def download_instagram_command(client, message: Message):
    """
    Handles reel downloads via command.
    """
    if len(message.command) < 2:
        await message.reply_text(
            "Pʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ᴛʜᴇ Iɴsᴛᴀɢʀᴀᴍ ʀᴇᴇʟ URL ᴀғᴛᴇʀ ᴛʜᴇ ᴄᴏᴍᴍᴀɴᴅ"
        )
        return

    # Extract the URL from the message
    url = message.text.split(None, 1)[1].strip()
    if not url:
        await message.reply_text(
            "Pʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ᴛʜᴇ Iɴsᴛᴀɢʀᴀᴍ ʀᴇᴇʟ URL ᴀғᴛᴇʀ ᴛʜᴇ ᴄᴏᴍᴍᴀɴᴅ"
        )
        return

    await _process_reel(message, url)


@app.on_message(filters.text & (filters.private | filters.group) & ~filters.via_bot)
async def download_instagram_no_command(client, message: Message):
    """
    Handles reel downloads when a link is sent directly.
    """
    if not message.text or message.text.startswith(("/", "!", "?", ".")):
        return
