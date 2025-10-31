

import asyncio
import importlib
from pyrogram import idle
from pyrogram.types import BotCommand
from pytgcalls.exceptions import NoActiveGroupCall
import config
from NapsterMusicBot import LOGGER, app, userbot
from NapsterMusicBot.core.call import Nand
from NapsterMusicBot.misc import sudo
from NapsterMusicBot.plugins import ALL_MODULES
from NapsterMusicBot.utils.database import get_banned_users, get_gbanned
from config import BANNED_USERS

# Bot Commands List
COMMANDS = [
    BotCommand("start", "🚀 Start bot"),
    BotCommand("help", "❓ Help menu and Many More Management Commands"),
    BotCommand("ping", "📡 Ping and system stats"),
    BotCommand("play", "🎵 Start streaming the requested track"),
    BotCommand("vplay", "📹 Start video streaming"),
    BotCommand("playrtmps", "📺 Play Live Video"),
    BotCommand("playforce", "⚠️ Force play audio track"),
    BotCommand("vplayforce", "⚠️ Force play video track"),
    BotCommand("pause", "⏸ Pause the stream"),
    BotCommand("resume", "▶️ Resume the stream"),
    BotCommand("skip", "⏭ Skip the current track"),
    BotCommand("end", "🛑 End the stream"),
    BotCommand("stop", "🛑 Stop the stream"),
    BotCommand("queue", "📄 Show track queue"),
    BotCommand("auth", "➕ Add a user to auth list"),
    BotCommand("unauth", "➖ Remove a user from auth list"),
    BotCommand("authusers", "👥 Show list of auth users"),
    BotCommand("cplay", "📻 Channel audio play"),
    BotCommand("cvplay", "📺 Channel video play"),
    BotCommand("cplayforce", "🚨 Channel force audio play"),
    BotCommand("cvplayforce", "🚨 Channel force video play"),
    BotCommand("channelplay", "🔗 Connect group to channel"),
    BotCommand("loop", "🔁 Enable/disable loop"),
    BotCommand("stats", "📊 Bot stats"),
    BotCommand("shuffle", "🔀 Shuffle the queue"),
    BotCommand("seek", "⏩ Seek forward"),
    BotCommand("seekback", "⏪ Seek backward"),
    BotCommand("song", "🎶 Download song (mp3/mp4)"),
    BotCommand("speed", "⏩ Adjust audio playback speed (group)"),
    BotCommand("cspeed", "⏩ Adjust audio speed (channel)"),
    BotCommand("tagall", "📢 Tag everyone"),
]

async def setup_bot_commands():
    """Setup bot commands during startup"""
    try:
        await app.set_bot_commands(COMMANDS)
        LOGGER("NapsterMusicBot").info("Bot commands set successfully!")
    except Exception as e:
        LOGGER("NapsterMusicBot").error(f"Failed to set bot commands: {str(e)}")

async def init():
    if (
        not config.STRING1
        and not config.STRING2
        and not config.STRING3
        and not config.STRING4
        and not config.STRING5
    ):
        LOGGER(__name__).error("Assistant client variables not defined, exiting...")
        exit()

    await sudo()

    try:
        users = await get_gbanned()
        for user_id in users:
            BANNED_USERS.add(user_id)
        users = await get_banned_users()
        for user_id in users:
            BANNED_USERS.add(user_id)
    except:
        pass

    await app.start()
    await setup_bot_commands()

    for all_module in ALL_MODULES:
        importlib.import_module("NapsterMusicBot.plugins" + all_module)

    LOGGER("NapsterMusicBot.plugins").info("Successfully Imported Modules...")

    await userbot.start()
    await Nand.start()

    try:
        await Nand.stream_call("https://te.legra.ph/file/29f784eb49d230ab62e9e.mp4")
    except NoActiveGroupCall:
        LOGGER("NapsterMusicBot").error(
            "Please turn on the videochat of your log group/channel.\n\nStopping Bot..."
        )
        exit()
    except:
        pass

    await Nand.decorators()

    LOGGER("NapsterMusicBot").info(
        "Napster Music Bot Started Successfully! 🎶\n\nDon’t forget to visit @NapsterMusic"
    )

    await idle()

    await app.stop()
    await userbot.stop()
    LOGGER("NapsterMusicBot").info("Stopping Napster Music Bot...🥺")

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(init())
