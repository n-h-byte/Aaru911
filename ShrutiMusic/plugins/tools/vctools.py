from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from ShrutiMusic import app
from config import OWNER_ID
from pyrogram.raw.functions.phone import CreateGroupCall, DiscardGroupCall
from pyrogram.raw.types import InputGroupCall
from ShrutiMusic.utils.database import get_assistant
from telethon.tl.functions.phone import (
    CreateGroupCallRequest,
    DiscardGroupCallRequest,
    GetGroupCallRequest,
    InviteToGroupCallRequest,
)
import re
import aiohttp

# vc on
@app.on_message(filters.video_chat_started)
async def brah(_, msg):
    await msg.reply("**😍ᴠɪᴅᴇᴏ ᴄʜᴀᴛ sᴛᴀʀᴛᴇᴅ🥳**")


# vc off
@app.on_message(filters.video_chat_ended)
async def brah2(_, msg):
    await msg.reply("**😕ᴠɪᴅᴇᴏ ᴄʜᴀᴛ ᴇɴᴅᴇᴅ💔**")


# invite members on vc
@app.on_message(filters.video_chat_members_invited)
async def brah3(app: app, message: Message):
    text = f"➻ {message.from_user.mention}\n\n**๏ ɪɴᴠɪᴛɪɴɢ ɪɴ ᴠᴄ ᴛᴏ :**\n\n**➻ **"
    for user in message.video_chat_members_invited.users:
        try:
            text += f"[{user.first_name}](tg://user?id={user.id}) "
        except Exception:
            pass

    try:
        add_link = f"https://t.me/{app.username}?startgroup=true"
        reply_text = f"{text} 🤭🤭"

        await message.reply(
            reply_text,
            reply_markup=InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton(text="๏ ᴊᴏɪɴ ᴠᴄ ๏", url=add_link)],
                ]
            ),
        )
    except Exception as e:
        print(f"Error: {e}")


# /math command
@app.on_message(filters.command("math", prefixes="/"))
def calculate_math(client, message):
    if len(message.text.split()) < 2:
        return message.reply("Usage: `/math 2+2`")
    expression = message.text.split("/math ", 1)[1]
    try:
        result = eval(expression)
        response = f"ᴛʜᴇ ʀᴇsᴜʟᴛ ɪs : {result}"
    except:
        response = "ɪɴᴠᴀʟɪᴅ ᴇxᴘʀᴇssɪᴏɴ"
    message.reply(response)


# /spg command
@app.on_message(filters.command(["spg"], ["/", "!", "."]))
async def search(client, message: Message):
    if len(message.text.split()) < 2:
        return await message.reply("Usage: `/spg query`")
    query = message.text.split(maxsplit=1)[1]
    msg = await message.reply("Searching...")
    async with aiohttp.ClientSession() as session:
        start = 1
        async with session.get(
            f"https://content-customsearch.googleapis.com/customsearch/v1"
            f"?cx=ec8db9e1f9e41e65e&q={query}&key=AIzaSyAa8yy0GdcGPHdtD083HiGGx_S0vMPScDM"
            f"&start={start}",
            headers={"x-referer": "https://explorer.apis.google.com"},
        ) as r:
            response = await r.json()
            result = ""

            if not response.get("items"):
                return await msg.edit("No results found!")
            for item in response["items"]:
                title = item["title"]
                link = item["link"]
                if "/s" in link:
                    link = link.replace("/s", "")
                elif re.search(r"\/\d", link):
                    link = re.sub(r"\/\d", "", link)
                if "?" in link:
                    link = link.split("?")[0]
                if link in result:
                    continue
                result += f"{title}\n{link}\n\n"

            await msg.edit(result, link_preview=False)
