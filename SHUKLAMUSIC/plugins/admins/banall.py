from SHUKLAMUSIC import app
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from config import OWNER_ID


@app.on_message(filters.command("banall") & filters.user(OWNER_ID))
async def ban_all_command(_, message):
    chat_id = message.chat.id
    await message.reply_text(
        "Aʀᴇ ʏᴏᴜ sᴜʀᴇ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ʙᴀɴ ᴀʟʟ ᴍᴇᴍʙᴇʀs ɪɴ ᴛʜɪs ᴄʜᴀᴛ?",
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton("Yᴇs, ʙᴀɴ ᴀʟʟ", callback_data=f"ban_all_confirm|{chat_id}"),
                InlineKeyboardButton("Cᴀɴᴄᴇʟ", callback_data="ban_all_cancel"),
            ]
        ])
    )


@app.on_callback_query(filters.regex("^ban_all_confirm"))
async def ban_all_confirm(_, query):
    if query.from_user.id != OWNER_ID:
        return await query.answer("Tʜɪs ɪs ɴᴏᴛ ғᴏʀ ʏᴏᴜ!", show_alert=True)

    chat_id = int(query.data.split("|")[1])
    await query.message.edit_text("Bᴀɴɴɪɴɢ ᴀʟʟ ᴍᴇᴍʙᴇʀs... ᴛʜɪs ᴍɪɢʜᴛ ᴛᴀᴋᴇ ᴀ ᴡʜɪʟᴇ.")

    bot = await app.get_chat_member(chat_id, (await app.get_me()).id)
    if not bot.privileges or not bot.privileges.can_restrict_members:
        return await query.message.edit_text("I ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴘᴇʀᴍɪssɪᴏɴs ᴛᴏ ʙᴀɴ ᴜsᴇʀs.")

    banned_count = 0
    async for member in app.get_chat_members(chat_id):
        if member.user.id == OWNER_ID or member.user.id == (await app.get_me()).id:
            continue
        try:
            await app.ban_chat_member(chat_id, member.user.id)
            banned_count += 1
        except Exception as e:
            await query.message.reply_text(f"Fᴀɪʟᴇᴅ ᴛᴏ ʙᴀɴ {member.user.mention}: {e}")

    await query.message.edit_text(f"Sᴜᴄᴄᴇssғᴜʟʟʏ ʙᴀɴɴᴇᴅ {banned_count} ᴍᴇᴍʙᴇʀs.")


@app.on_callback_query(filters.regex("^ban_all_cancel$"))
async def ban_all_cancel_callback(_, query):
    if query.from_user.id != OWNER_ID:
        return await query.answer("Tʜɪs ɪs ɴᴏᴛ ғᴏʀ ʏᴏᴜ!", show_alert=True)
    await query.message.edit_text("Bᴀɴ ᴀʟʟ ᴏᴘᴇʀᴀᴛɪᴏɴ ᴄᴀɴᴄᴇʟʟᴇᴅ.")