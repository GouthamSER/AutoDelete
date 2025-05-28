from os import environ
from pyrogram import Client

API_ID = int(environ.get('API_ID', ''))
API_HASH = environ.get('API_HASH', '')
BOT_TOKEN = environ.get('BOT_TOKEN', '')

class Bot(Client):
    def __init__(self):
        super().__init__(
            name="deletebot",
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            workers=50,
            plugins={"root": "plugins"},
            sleep_threshold=5,
        )

bot = Bot()

if __name__ == "__main__":
    bot.run()
