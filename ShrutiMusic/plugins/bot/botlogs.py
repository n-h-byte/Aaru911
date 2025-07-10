import random
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from config import LOG_GROUP_ID
from ShrutiMusic import app
from ShrutiMusic.utils.database import add_served_chat, get_assistant

welcome_photo = "https://files.catbox.moe/3zqpqh.jpg"  # Bot added image

@app.on_message(filters.new_chat_members, group=-10)
async def join_watcher(_, message):
    try:
        userbot = await get_assistant(message.chat.id)
        chat = message.chat
        for members in message.new_chat_members:
            if members.id == app.id:
                count = await app.get_chat_members_count(chat.id)
                username = message.chat.username if message.chat.username else "Private Group"
                
                # Try to get invite link if bot has admin rights
                invite_link = ""
                try:
                    if not message.chat.username:  # Only for private groups
                        link = await app.export_chat_invite_link(message.chat.id)
                        invite_link = f"\nGroup Link: {link}" if link else ""
                except:
                    pass
                
                msg = (
                    f"Music Bot Added In A New Group\n\n"
                    f"Chat Name: {message.chat.title}\n"
                    f"Chat ID: {message.chat.id}\n"
                    f"Chat Username: @{username}\n"
                    f"Group Members: {count}\n"
                    f"Added By: {message.from_user.mention}"
                    f"{invite_link}"
                )
                
                buttons = []
                if message.from_user.id:
                    buttons.append([InlineKeyboardButton("Added By", 
                                    url=f"tg://openmessage?user_id={message.from_user.id}")])
                
                await app.send_photo(
                    LOG_GROUP_ID,
                    photo=welcome_photo,
                    caption=msg,
                    reply_markup=InlineKeyboardMarkup(buttons) if buttons else None
                )
                
                await add_served_chat(message.chat.id)
                if username:
                    await userbot.join_chat(f"@{username}")

    except Exception as e:
        print(f"Error: {e}")
